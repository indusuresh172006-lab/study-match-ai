import csv
import io
import math
import re
import secrets
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth import get_current_user, require_student, require_teacher
from database import get_db
from models import (
    ClassEnrollment,
    ImportedMark,
    MarkImportBatch,
    SkillProfile,
    Student,
    StudyClass,
)

router = APIRouter()

MAX_MARK_FILE_BYTES = 5 * 1024 * 1024
MAX_MARK_ROWS = 5000
REQUIRED_MARK_COLUMNS = {"student_email", "subject", "topic", "score", "max_score"}


class StudyClassCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    course: str = Field(..., min_length=1, max_length=100)
    curriculum: str = Field(..., min_length=1, max_length=150)
    academic_year: str = Field(..., min_length=1, max_length=20)


class ClassJoinRequest(BaseModel):
    join_code: str = Field(..., min_length=4, max_length=16)


def _normalize_header(value: Any) -> str:
    return re.sub(r"\s+", "_", str(value).strip().lower().lstrip("\ufeff"))


def parse_mark_rows(filename: str, content: bytes) -> List[Dict[str, Any]]:
    extension = Path(filename).suffix.lower()
    if extension == ".csv":
        try:
            reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
            headers = reader.fieldnames or []
            rows = list(reader)
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=422, detail="CSV must be encoded as UTF-8.") from exc
    elif extension in {".xlsx", ".xlsm"}:
        import pandas as pd

        try:
            frame = pd.read_excel(io.BytesIO(content), engine="openpyxl")
        except (ValueError, OSError) as exc:
            raise HTTPException(status_code=422, detail="Could not read the Excel workbook.") from exc
        headers = list(frame.columns)
        rows = frame.to_dict(orient="records")
    else:
        raise HTTPException(status_code=415, detail="Upload a .csv, .xlsx, or .xlsm marks file.")

    column_map = {_normalize_header(header): header for header in headers}
    aliases = {
        "email": "student_email",
        "student": "student_email",
        "student_email_address": "student_email",
        "maximum_score": "max_score",
        "max_marks": "max_score",
        "total_marks": "max_score",
    }
    for alias, canonical in aliases.items():
        if alias in column_map and canonical not in column_map:
            column_map[canonical] = column_map[alias]

    missing_columns = sorted(REQUIRED_MARK_COLUMNS - column_map.keys())
    if missing_columns:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required columns: {', '.join(missing_columns)}.",
        )
    if not rows:
        raise HTTPException(status_code=422, detail="The marks file contains no data rows.")
    if len(rows) > MAX_MARK_ROWS:
        raise HTTPException(
            status_code=413,
            detail=f"A single import may contain at most {MAX_MARK_ROWS} rows.",
        )

    normalized_rows = []
    row_errors = []
    for row_number, row in enumerate(rows, start=2):
        values = {
            canonical: row.get(original)
            for canonical, original in column_map.items()
            if canonical in REQUIRED_MARK_COLUMNS
        }
        email = str(values.get("student_email") or "").strip().lower()
        subject = str(values.get("subject") or "").strip()
        topic = str(values.get("topic") or "").strip()
        try:
            score = float(values.get("score"))
            max_score = float(values.get("max_score"))
        except (TypeError, ValueError):
            row_errors.append(f"Row {row_number}: score and max_score must be numbers.")
            continue

        if not email or not subject or not topic:
            row_errors.append(f"Row {row_number}: student_email, subject, and topic are required.")
        elif len(subject) > 100 or len(topic) > 100:
            row_errors.append(f"Row {row_number}: subject and topic must be at most 100 characters.")
        elif not math.isfinite(score) or not math.isfinite(max_score) or max_score <= 0:
            row_errors.append(f"Row {row_number}: score and max_score must be finite; max_score must be positive.")
        elif score < 0 or score > max_score:
            row_errors.append(f"Row {row_number}: score must be between zero and max_score.")
        else:
            normalized_rows.append({
                "row_number": row_number,
                "student_email": email,
                "subject": subject,
                "topic": topic,
                "score": score,
                "max_score": max_score,
            })

    if row_errors:
        raise HTTPException(status_code=422, detail=row_errors[:20])
    return normalized_rows


def _owned_class(db: Session, class_id: int, current_user: Student) -> StudyClass:
    query = db.query(StudyClass).filter(
        StudyClass.id == class_id,
        StudyClass.is_active.is_(True),
    )
    if current_user.role != "admin":
        query = query.filter(StudyClass.teacher_id == current_user.id)
    study_class = query.first()
    if not study_class:
        raise HTTPException(status_code=404, detail="Class not found.")
    return study_class


def _class_summary(study_class: StudyClass, roster_size: int, include_code: bool) -> Dict[str, Any]:
    return {
        "id": study_class.id,
        "name": study_class.name,
        "course": study_class.course,
        "curriculum": study_class.curriculum,
        "academic_year": study_class.academic_year,
        "join_code": study_class.join_code if include_code else None,
        "teacher_name": study_class.teacher.name if study_class.teacher else None,
        "roster_size": roster_size,
        "created_at": study_class.created_at,
    }


@router.post("/classes", status_code=status.HTTP_201_CREATED)
def create_study_class(
    payload: StudyClassCreate,
    current_teacher: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    code = secrets.token_hex(4).upper()
    while db.query(StudyClass.id).filter(StudyClass.join_code == code).first():
        code = secrets.token_hex(4).upper()

    study_class = StudyClass(
        name=payload.name.strip(),
        join_code=code,
        teacher_id=current_teacher.id,
        course=payload.course.strip(),
        curriculum=payload.curriculum.strip(),
        academic_year=payload.academic_year.strip(),
    )
    db.add(study_class)
    db.commit()
    db.refresh(study_class)
    return _class_summary(study_class, roster_size=0, include_code=True)


@router.get("/classes")
def list_my_classes(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(StudyClass)
    if current_user.role == "teacher":
        query = query.filter(StudyClass.teacher_id == current_user.id)
    elif current_user.role == "student":
        query = query.join(ClassEnrollment).filter(
            ClassEnrollment.student_id == current_user.id
        )

    classes = query.filter(StudyClass.is_active.is_(True)).order_by(StudyClass.name).all()
    return [
        _class_summary(
            study_class,
            roster_size=db.query(ClassEnrollment.id).filter(
                ClassEnrollment.class_id == study_class.id
            ).count(),
            include_code=current_user.role in {"teacher", "admin"},
        )
        for study_class in classes
    ]


@router.post("/classes/join")
def join_study_class(
    payload: ClassJoinRequest,
    current_student: Student = Depends(require_student),
    db: Session = Depends(get_db),
):
    study_class = db.query(StudyClass).filter(
        StudyClass.join_code == payload.join_code.strip().upper(),
        StudyClass.is_active.is_(True),
    ).first()
    if not study_class:
        raise HTTPException(status_code=404, detail="Class code is invalid or inactive.")

    enrollment = db.query(ClassEnrollment).filter(
        ClassEnrollment.class_id == study_class.id,
        ClassEnrollment.student_id == current_student.id,
    ).first()
    if not enrollment:
        enrollment = ClassEnrollment(class_id=study_class.id, student_id=current_student.id)
        db.add(enrollment)

    profile = current_student.profile
    if profile:
        profile.course = study_class.course
        profile.college = study_class.curriculum
        profile.semester = study_class.academic_year
    db.commit()
    return {
        "message": f"Joined {study_class.name}.",
        "class": _class_summary(study_class, roster_size=0, include_code=False),
    }


@router.get("/classes/{class_id}/students")
def list_class_students(
    class_id: int,
    current_teacher: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    _owned_class(db, class_id, current_teacher)
    enrollments = db.query(ClassEnrollment).filter(
        ClassEnrollment.class_id == class_id
    ).order_by(ClassEnrollment.joined_at).all()
    return [
        {
            "student_id": enrollment.student.id,
            "name": enrollment.student.name,
            "email": enrollment.student.email,
            "joined_at": enrollment.joined_at,
        }
        for enrollment in enrollments
    ]


@router.get("/classes/{class_id}/marks/imports")
def list_mark_imports(
    class_id: int,
    current_teacher: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    _owned_class(db, class_id, current_teacher)
    batches = db.query(MarkImportBatch).filter(
        MarkImportBatch.class_id == class_id
    ).order_by(MarkImportBatch.created_at.desc()).all()
    return [
        {
            "id": batch.id,
            "filename": batch.filename,
            "row_count": batch.row_count,
            "created_at": batch.created_at,
        }
        for batch in batches
    ]


@router.post("/classes/{class_id}/marks/import")
async def import_class_marks(
    class_id: int,
    file: UploadFile = File(...),
    current_teacher: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    study_class = _owned_class(db, class_id, current_teacher)
    content = await file.read(MAX_MARK_FILE_BYTES + 1)
    if len(content) > MAX_MARK_FILE_BYTES:
        raise HTTPException(status_code=413, detail="Marks file must be 5 MB or smaller.")

    rows = parse_mark_rows(file.filename or "", content)
    roster = {
        student.email.strip().lower(): student
        for (student,) in db.query(Student).join(ClassEnrollment).filter(
            ClassEnrollment.class_id == study_class.id
        ).all()
    }
    invalid_members = sorted({
        row["student_email"] for row in rows
        if row["student_email"] not in roster
    })
    if invalid_members:
        raise HTTPException(
            status_code=422,
            detail=(
                "Every student_email must belong to this class. Not enrolled: "
                + ", ".join(invalid_members[:20])
            ),
        )

    batch = MarkImportBatch(
        class_id=study_class.id,
        imported_by=current_teacher.id,
        filename=Path(file.filename or "marks.csv").name[:255],
        row_count=len(rows),
    )
    db.add(batch)
    db.flush()

    scores_by_student_topic: Dict[tuple, List[float]] = {}
    for row in rows:
        student = roster[row["student_email"]]
        percentage = row["score"] / row["max_score"] * 100.0
        key = (student.id, row["subject"], row["topic"])
        scores_by_student_topic.setdefault(key, []).append(percentage)
        db.add(ImportedMark(
            batch_id=batch.id,
            student_id=student.id,
            subject=row["subject"],
            topic=row["topic"],
            score=row["score"],
            max_score=row["max_score"],
        ))

    for (student_id, subject, topic), percentages in scores_by_student_topic.items():
        skill = db.query(SkillProfile).filter(
            SkillProfile.student_id == student_id,
            SkillProfile.subject == subject,
            SkillProfile.topic == topic,
        ).first()
        if skill:
            old_count = max(skill.tests_taken or 0, 0)
            total_count = old_count + len(percentages)
            skill.mastery_score = round(
                ((skill.mastery_score or 0.0) * old_count + sum(percentages)) / max(total_count, 1),
                1,
            )
            skill.tests_taken = total_count
        else:
            skill = SkillProfile(
                student_id=student_id,
                subject=subject,
                topic=topic,
                mastery_score=round(sum(percentages) / len(percentages), 1),
                tests_taken=len(percentages),
            )
            db.add(skill)

        if skill.mastery_score < 50:
            skill.status = "weak"
        elif skill.mastery_score <= 75:
            skill.status = "average"
        else:
            skill.status = "strong"

    db.commit()
    return {
        "batch_id": batch.id,
        "imported_rows": len(rows),
        "students_updated": len({row["student_email"] for row in rows}),
        "message": "Marks imported and student skill profiles updated.",
    }
