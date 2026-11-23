import secrets
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth import get_password_hash, require_admin
from database import get_db
from models import ClassEnrollment, Student, StudyClass, TeacherProfile

router = APIRouter(prefix="/admin")


class TeacherAccountCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    subject: str = Field(..., min_length=1, max_length=100)
    college: str = Field(..., min_length=1, max_length=150)
    semester: str = Field(..., min_length=1, max_length=20)

    @field_validator("name", "subject", "college", "semester")
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field must not be blank.")
        return value


class TeacherRequestReview(BaseModel):
    decision: Literal["approve", "reject"]


class AdminClassCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    course: str = Field(..., min_length=1, max_length=100)
    curriculum: str = Field(..., min_length=1, max_length=150)
    academic_year: str = Field(..., min_length=1, max_length=20)
    teacher_id: int

    @field_validator("name", "course", "curriculum", "academic_year")
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field must not be blank.")
        return value


class AdminClassUpdate(BaseModel):
    teacher_id: Optional[int] = None
    is_active: Optional[bool] = None


def _class_summary(db: Session, study_class: StudyClass) -> dict:
    return {
        "id": study_class.id,
        "name": study_class.name,
        "course": study_class.course,
        "curriculum": study_class.curriculum,
        "academic_year": study_class.academic_year,
        "join_code": study_class.join_code,
        "teacher_id": study_class.teacher_id,
        "teacher_name": study_class.teacher.name if study_class.teacher else None,
        "roster_size": db.query(ClassEnrollment.id).filter(
            ClassEnrollment.class_id == study_class.id
        ).count(),
        "is_active": study_class.is_active,
        "created_at": study_class.created_at,
    }


@router.get("/overview")
def get_admin_overview(
    current_admin: Student = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return {
        "total_users": db.query(Student).count(),
        "students": db.query(Student).filter(Student.role == "student").count(),
        "teachers": db.query(Student).filter(Student.role == "teacher").count(),
        "admins": db.query(Student).filter(Student.role == "admin").count(),
        "pending_teacher_requests": db.query(Student).filter(
            Student.role == "teacher",
            Student.approval_status == "pending",
        ).count(),
        "total_classes": db.query(StudyClass).count(),
        "active_classes": db.query(StudyClass).filter(StudyClass.is_active.is_(True)).count(),
    }


@router.get("/users")
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_admin: Student = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Student)
    total = query.count()
    users = query.order_by(Student.role, Student.name).offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "approval_status": user.approval_status,
            }
            for user in users
        ],
    }


@router.get("/teacher-requests")
def list_teacher_requests(
    current_admin: Student = Depends(require_admin),
    db: Session = Depends(get_db),
):
    requests = db.query(Student, TeacherProfile).outerjoin(
        TeacherProfile,
        TeacherProfile.teacher_id == Student.id,
    ).filter(
        Student.role == "teacher",
        Student.approval_status == "pending",
    ).order_by(Student.id).all()
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "subject": profile.subject or profile.department if profile else None,
            "college": profile.college if profile else None,
            "semester": profile.semester if profile else None,
            "approval_status": user.approval_status,
        }
        for user, profile in requests
    ]


@router.patch("/teacher-requests/{teacher_id}")
def review_teacher_request(
    teacher_id: int,
    payload: TeacherRequestReview,
    current_admin: Student = Depends(require_admin),
    db: Session = Depends(get_db),
):
    teacher = db.query(Student).filter(
        Student.id == teacher_id,
        Student.role == "teacher",
    ).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher request not found.")
    if teacher.approval_status != "pending":
        raise HTTPException(status_code=409, detail="Only pending teacher requests can be reviewed.")

    teacher.approval_status = "approved" if payload.decision == "approve" else "rejected"
    db.commit()
    return {"id": teacher.id, "approval_status": teacher.approval_status}


@router.post("/teachers", status_code=status.HTTP_201_CREATED)
def create_teacher(
    payload: TeacherAccountCreate,
    current_admin: Student = Depends(require_admin),
    db: Session = Depends(get_db),
):
    email = str(payload.email).strip().lower()
    existing = db.query(Student.id).filter(
        func.lower(Student.email) == email
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email is already registered.")

    teacher = Student(
        name=payload.name,
        email=email,
        password_hash=get_password_hash(payload.password),
        role="teacher",
        approval_status="approved",
    )
    db.add(teacher)
    db.flush()
    db.add(TeacherProfile(
        teacher_id=teacher.id,
        department=payload.subject,
        designation="Faculty Instructor",
        college=payload.college,
        subject=payload.subject,
        semester=payload.semester,
    ))
    db.commit()
    db.refresh(teacher)
    return {"id": teacher.id, "name": teacher.name, "email": teacher.email, "role": teacher.role}


@router.post("/classes", status_code=status.HTTP_201_CREATED)
def create_class(
    payload: AdminClassCreate,
    current_admin: Student = Depends(require_admin),
    db: Session = Depends(get_db),
):
    teacher = db.query(Student).filter(
        Student.id == payload.teacher_id,
        Student.role == "teacher",
    ).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher account not found.")

    join_code = secrets.token_hex(4).upper()
    while db.query(StudyClass.id).filter(StudyClass.join_code == join_code).first():
        join_code = secrets.token_hex(4).upper()

    study_class = StudyClass(
        name=payload.name,
        course=payload.course,
        curriculum=payload.curriculum,
        academic_year=payload.academic_year,
        teacher_id=teacher.id,
        join_code=join_code,
    )
    db.add(study_class)
    db.commit()
    db.refresh(study_class)
    return _class_summary(db, study_class)


@router.get("/classes")
def list_classes(
    include_inactive: bool = False,
    current_admin: Student = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(StudyClass)
    if not include_inactive:
        query = query.filter(StudyClass.is_active.is_(True))
    classes = query.order_by(StudyClass.name).all()
    return [_class_summary(db, study_class) for study_class in classes]


@router.patch("/classes/{class_id}")
def update_class(
    class_id: int,
    payload: AdminClassUpdate,
    current_admin: Student = Depends(require_admin),
    db: Session = Depends(get_db),
):
    study_class = db.query(StudyClass).filter(StudyClass.id == class_id).first()
    if not study_class:
        raise HTTPException(status_code=404, detail="Class not found.")
    if payload.teacher_id is None and payload.is_active is None:
        raise HTTPException(status_code=422, detail="Provide a new teacher or active status.")
    if payload.teacher_id is not None:
        teacher = db.query(Student).filter(
            Student.id == payload.teacher_id,
            Student.role == "teacher",
        ).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher account not found.")
        study_class.teacher_id = teacher.id
    if payload.is_active is not None:
        study_class.is_active = payload.is_active
    db.commit()
    db.refresh(study_class)
    return _class_summary(db, study_class)
