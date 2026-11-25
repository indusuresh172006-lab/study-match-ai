"""
Module 5: Mock Tests & Previous Question Papers Router (Extended)
Endpoints: question paper library, test CRUD, attempt flow,
result analysis with topic-wise breakdown, adaptive test generation.
After each attempt the SkillProfile is updated.
"""
import datetime
import logging
import os
import uuid
from typing import List, Optional, Literal
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from starlette.responses import FileResponse, RedirectResponse

from academic_scope import normalize_academic_year
from database import get_db
from auth import get_current_user, require_teacher
from models import (
    Student, StudentProfile, SkillProfile, QuestionPaper, Test, TestQuestion,
    TestAttempt, AttemptAnswer, TestResult
)
from paper_generator import generate_paper_pdfs, get_ai_paper_questions

router = APIRouter()
logger = logging.getLogger(__name__)
MAX_PDF_BYTES = 20 * 1024 * 1024
UPLOAD_ROOT = Path(
    os.getenv("STUDYMATCH_UPLOAD_DIR", str(Path(__file__).resolve().parents[1] / "uploads"))
).resolve()


class TestReviewRequest(BaseModel):
    decision: Literal["approve", "reject"]


# ─────────────────────────────────────────────
# QUESTION PAPER LIBRARY
# ─────────────────────────────────────────────

def _paper_matches_student_scope(paper: QuestionPaper, scope) -> bool:
    if scope is None:
        return True

    course, curriculum, academic_year = scope
    return bool(course and curriculum and academic_year) and (
        (paper.course or "").strip().casefold() == course
        and (paper.curriculum or "").strip().casefold() == curriculum
        and normalize_academic_year(paper.academic_year) == academic_year
    )


def _filter_papers_to_scope(query, scope):
    if scope is None:
        return query

    course, curriculum, _ = scope
    if not course or not curriculum:
        return query.filter(QuestionPaper.id == -1)

    return query.filter(
        func.lower(func.trim(QuestionPaper.course)) == course,
        func.lower(func.trim(QuestionPaper.curriculum)) == curriculum,
    )


def _paper_scope_values(course, curriculum, academic_year):
    values = [
        (value or "").strip()
        for value in (course, curriculum, academic_year)
    ]
    if any(values) and not all(values):
        raise HTTPException(
            status_code=422,
            detail="Course, institution, and semester must all be provided for a scoped paper.",
        )
    return values


class GenerateAIPaperRequest(BaseModel):
    subject: str
    exam_name: Optional[str] = "AI Adaptive Examination"
    year: Optional[int] = None


@router.get("/papers")
def list_papers(
    exam: Optional[str] = None,
    subject: Optional[str] = None,
    year: Optional[int] = None,
    topic: Optional[str] = None,
    source: Optional[str] = None,
    skip: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    q = db.query(QuestionPaper)
    if current_user.role not in {"teacher", "admin"}:
        q = q.filter(QuestionPaper.approval_status == "approved")
    if exam:
        q = q.filter(QuestionPaper.exam_name.ilike(f"%{exam}%"))
    if subject and subject != "All":
        q = q.filter(QuestionPaper.subject.ilike(f"%{subject}%"))
    if year and year != "All":
        try:
            q = q.filter(QuestionPaper.year == int(year))
        except (ValueError, TypeError):
            pass
    if topic:
        # topic_tags is a JSON list — do a text search
        q = q.filter(QuestionPaper.topic_tags.cast(db.bind.dialect.name == "postgresql" and
                     __import__("sqlalchemy").Text or __import__("sqlalchemy").Text).ilike(f"%{topic}%"))

    scope = _student_test_scope(db, current_user)
    if scope is not None:
        q = _filter_papers_to_scope(q, scope)
        candidates = q.order_by(QuestionPaper.year.desc()).all()
        papers = [
            paper for paper in candidates
            if _paper_matches_student_scope(paper, scope)
        ]
        if source and source != "All":
            papers = [
                p for p in papers
                if (getattr(p, "source", None) or ("ai" if "ai" in (p.title + " " + p.exam_name).lower() else "teacher")) == source.lower()
            ]
        total = len(papers)
        papers = papers[skip:skip + limit]
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": [_paper_dict(paper) for paper in papers],
        }

    candidates = q.order_by(QuestionPaper.year.desc()).all()
    if source and source != "All":
        candidates = [
            p for p in candidates
            if (getattr(p, "source", None) or ("ai" if "ai" in (p.title + " " + p.exam_name).lower() else "teacher")) == source.lower()
        ]
    total = len(candidates)
    papers = candidates[skip:skip + limit]
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [_paper_dict(p) for p in papers],
    }


def _paper_dict(p: QuestionPaper):
    source_val = getattr(p, "source", None)
    if not source_val:
        source_val = "ai" if "ai" in (p.title + " " + p.exam_name).lower() else "teacher"

    uploader_label = "AI Academic Engine" if source_val == "ai" else (
        p.uploader.name if getattr(p, "uploader", None) else "Faculty / Department"
    )

    return {
        "id": p.id,
        "exam_name": p.exam_name,
        "subject": p.subject,
        "course": p.course,
        "curriculum": p.curriculum,
        "academic_year": p.academic_year,
        "year": p.year,
        "title": p.title,
        "topic_tags": p.topic_tags,
        "file_path": p.file_path,
        "answer_key_file": p.answer_key_file,
        "approval_status": p.approval_status,
        "source": source_val,
        "uploader_name": uploader_label,
        "has_solutions": bool(getattr(p, "solutions", None) or p.answer_key_file),
        "solutions": getattr(p, "solutions", None),
    }


@router.get("/papers/{paper_id}")
def get_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    paper = db.query(QuestionPaper).filter(QuestionPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    if current_user.role not in {"teacher", "admin"} and (
        paper.approval_status != "approved"
        or not _paper_matches_student_scope(
            paper, _student_test_scope(db, current_user)
        )
    ):
        raise HTTPException(status_code=404, detail="Paper not found")
    return _paper_dict(paper)


@router.get("/papers/{paper_id}/solutions")
def get_paper_solutions(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    paper = db.query(QuestionPaper).filter(QuestionPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    if current_user.role not in {"teacher", "admin"} and (
        paper.approval_status != "approved"
        or not _paper_matches_student_scope(
            paper, _student_test_scope(db, current_user)
        )
    ):
        raise HTTPException(status_code=404, detail="Paper not found")

    solutions = getattr(paper, "solutions", None) or []
    return {
        "id": paper.id,
        "title": paper.title,
        "subject": paper.subject,
        "year": paper.year,
        "exam_name": paper.exam_name,
        "course": paper.course,
        "academic_year": paper.academic_year,
        "curriculum": paper.curriculum,
        "source": getattr(paper, "source", "teacher"),
        "uploader_name": paper.uploader.name if getattr(paper, "uploader", None) else ("AI Academic Engine" if getattr(paper, "source", "") == "ai" else "Faculty / Department"),
        "solutions": solutions,
    }


@router.post("/papers/generate-ai", status_code=status.HTTP_201_CREATED)
def generate_ai_question_paper(
    payload: GenerateAIPaperRequest,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    # Determine student or teacher academic scope
    scope = _student_test_scope(db, current_user)
    course = None
    curriculum = None
    academic_year = None
    if scope:
        course, curriculum, academic_year = scope
    elif current_user.profile:
        course = current_user.profile.course
        curriculum = current_user.profile.college
        academic_year = current_user.profile.semester

    course = course or "General"
    curriculum = curriculum or "Autonomous University"
    academic_year = academic_year or "Year 1"

    exam_year = payload.year or datetime.datetime.utcnow().year
    subject_name = payload.subject.strip()
    exam_title = f"AI Adaptive Solved Paper {exam_year}: {subject_name} Comprehensive"

    # Generate questions & solutions
    questions = get_ai_paper_questions(subject_name)
    tags = ["AI Generated", subject_name, "Comprehensive Practice", "Detailed Solutions"]

    # Generate PDFs
    file_code = f"ai_gen_{uuid.uuid4().hex[:10]}"
    meta_info = {
        "subject": subject_name,
        "course": course.upper(),
        "academic_year": academic_year,
        "curriculum": curriculum,
        "year": exam_year,
        "total_marks": 50,
        "time_limit": "2 Hours"
    }

    try:
        rel_qp, rel_key = generate_paper_pdfs(file_code, exam_title, payload.exam_name, meta_info, questions)
    except Exception as exc:
        logger.exception("Failed to generate PDFs for AI question paper.")
        rel_qp, rel_key = "", ""

    paper = QuestionPaper(
        exam_name=payload.exam_name,
        subject=subject_name,
        course=course.upper(),
        curriculum=curriculum,
        academic_year=academic_year,
        year=exam_year,
        title=exam_title,
        topic_tags=tags,
        file_path=rel_qp,
        answer_key_file=rel_key,
        approval_status="approved",
        source="ai",
        solutions=questions,
        uploaded_by=None
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)

    return _paper_dict(paper)


@router.post("/papers", status_code=status.HTTP_201_CREATED)
def upload_paper(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_teacher)
):
    """Teacher uploads question paper metadata."""
    scope_values = _paper_scope_values(
        payload.get("course"),
        payload.get("curriculum"),
        payload.get("academic_year"),
    )

    paper = QuestionPaper(
        exam_name=payload.get("exam_name", ""),
        subject=payload.get("subject", ""),
        course=scope_values[0] or None,
        curriculum=scope_values[1] or None,
        academic_year=scope_values[2] or None,
        year=payload.get("year", datetime.datetime.utcnow().year),
        title=payload.get("title", ""),
        topic_tags=payload.get("topic_tags", []),
        file_path=payload.get("file_path", ""),
        answer_key_file=payload.get("answer_key_file"),
        approval_status="pending",
        uploaded_by=current_user.id,
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return {"id": paper.id, "message": "Paper submitted for approval"}


async def _store_pdf(upload: UploadFile, stored_name: str) -> str:
    if Path(upload.filename or "").suffix.lower() != ".pdf":
        raise HTTPException(status_code=415, detail="Upload a PDF file.")
    content = await upload.read(MAX_PDF_BYTES + 1)
    if len(content) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="Each PDF must be 20 MB or smaller.")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=422, detail="The uploaded file is not a valid PDF.")

    relative_path = Path("question_papers") / stored_name
    target_path = UPLOAD_ROOT / relative_path
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(content)
    except OSError as exc:
        logger.exception("Could not save an uploaded question paper.")
        raise HTTPException(status_code=500, detail="Could not save the uploaded PDF.") from exc
    return relative_path.as_posix()


def _remove_stored_files(stored_paths: List[str]) -> None:
    for stored_path in stored_paths:
        try:
            (UPLOAD_ROOT / stored_path).unlink(missing_ok=True)
        except OSError:
            logger.exception("Could not remove a question-paper file after upload failure.")


@router.post("/papers/upload", status_code=status.HTTP_201_CREATED)
async def upload_paper_files(
    exam_name: str = Form(..., min_length=1, max_length=100),
    subject: str = Form(..., min_length=1, max_length=100),
    year: int = Form(..., ge=1900, le=2200),
    title: str = Form(..., min_length=1, max_length=200),
    topic_tags: str = Form(""),
    course: Optional[str] = Form(None, max_length=100),
    curriculum: Optional[str] = Form(None, max_length=150),
    academic_year: Optional[str] = Form(None, max_length=20),
    paper_file: UploadFile = File(...),
    answer_key_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_teacher: Student = Depends(require_teacher),
):
    stored_paths = []
    try:
        scope_values = _paper_scope_values(course, curriculum, academic_year)

        paper_path = await _store_pdf(paper_file, f"{uuid.uuid4().hex}.pdf")
        stored_paths.append(paper_path)
        answer_key_path = None
        if answer_key_file and answer_key_file.filename:
            answer_key_path = await _store_pdf(answer_key_file, f"{uuid.uuid4().hex}-key.pdf")
            stored_paths.append(answer_key_path)

        tags = [tag.strip() for tag in topic_tags.split(",") if tag.strip()]
        paper = QuestionPaper(
            exam_name=exam_name.strip(),
            subject=subject.strip(),
            course=scope_values[0] or None,
            curriculum=scope_values[1] or None,
            academic_year=scope_values[2] or None,
            year=year,
            title=title.strip(),
            topic_tags=tags,
            file_path=paper_path,
            answer_key_file=answer_key_path,
            approval_status="pending",
            uploaded_by=current_teacher.id,
        )
        db.add(paper)
        db.commit()
        db.refresh(paper)
    except HTTPException:
        _remove_stored_files(stored_paths)
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        _remove_stored_files(stored_paths)
        logger.exception("Could not create the uploaded question-paper record.")
        raise HTTPException(status_code=500, detail="Could not save the question paper.") from exc
    finally:
        await paper_file.close()
        if answer_key_file:
            await answer_key_file.close()

    return {"id": paper.id, "message": "Paper uploaded and submitted for approval"}


@router.get("/papers/{paper_id}/file")
def download_paper_file(
    paper_id: int,
    kind: Literal["paper", "answer_key"] = "paper",
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    paper = db.query(QuestionPaper).filter(QuestionPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    if current_user.role not in {"teacher", "admin"} and (
        paper.approval_status != "approved"
        or not _paper_matches_student_scope(
            paper, _student_test_scope(db, current_user)
        )
    ):
        raise HTTPException(status_code=404, detail="Paper not found.")

    stored_value = paper.file_path if kind == "paper" else paper.answer_key_file
    if not stored_value:
        raise HTTPException(status_code=404, detail="The requested PDF is not available.")
    if stored_value.startswith(("https://", "http://")):
        return RedirectResponse(stored_value)

    relative_path = Path(stored_value)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise HTTPException(status_code=404, detail="Paper file not found.")
    resolved_path = (UPLOAD_ROOT / relative_path).resolve()
    if os.path.commonpath([str(UPLOAD_ROOT), str(resolved_path)]) != str(UPLOAD_ROOT):
        raise HTTPException(status_code=404, detail="Paper file not found.")
    if not resolved_path.is_file():
        raise HTTPException(status_code=404, detail="Paper file not found.")
    return FileResponse(
        resolved_path,
        media_type="application/pdf",
        filename=resolved_path.name,
    )


@router.patch("/papers/{paper_id}/approve")
def approve_paper(
    paper_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_teacher)
):
    paper = db.query(QuestionPaper).filter(QuestionPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    paper.approval_status = payload.get("approval_status", "approved")
    db.commit()
    return {"message": f"Paper status set to {paper.approval_status}"}


# ─────────────────────────────────────────────
# TESTS (Teacher CRUD)
# ─────────────────────────────────────────────

def _student_test_scope(db: Session, current_user: Student):
    if current_user.role != "student":
        return None

    profile = db.query(StudentProfile).filter(
        StudentProfile.student_id == current_user.id
    ).first()
    if not profile:
        return None

    return (
        (profile.course or "").strip().casefold(),
        (profile.college or "").strip().casefold(),
        normalize_academic_year(profile.semester),
    )


def _test_matches_student_scope(test: Test, scope) -> bool:
    if scope is None:
        return True

    course, curriculum, academic_year = scope
    return bool(course and curriculum and academic_year) and (
        (test.course or "").strip().casefold() == course
        and (test.curriculum or "").strip().casefold() == curriculum
        and normalize_academic_year(test.academic_year) == academic_year
    )


def _filter_tests_to_scope(query, scope):
    if scope is None:
        return query

    course, curriculum, _ = scope
    if not course or not curriculum:
        return query.filter(Test.id == -1)

    return query.filter(
        func.lower(func.trim(Test.course)) == course,
        func.lower(func.trim(Test.curriculum)) == curriculum,
    )


@router.get("/tests")
def list_tests(
    subject: Optional[str] = None,
    skip: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    q = db.query(Test)
    if current_user.role not in {"teacher", "admin"}:
        q = q.filter(Test.is_published.is_(True), Test.approval_status == "approved")
    if subject:
        q = q.filter(Test.subject.ilike(f"%{subject}%"))

    scope = _student_test_scope(db, current_user)
    if scope is not None:
        q = _filter_tests_to_scope(q, scope)
        candidates = q.order_by(Test.created_at.desc()).all()
        tests = [test for test in candidates if _test_matches_student_scope(test, scope)]
        total = len(tests)
        tests = tests[skip:skip + limit]
        return {
            "total": total,
            "items": [_test_dict(test) for test in tests],
        }

    total = q.count()
    tests = q.order_by(Test.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [_test_dict(t) for t in tests],
    }


def _test_dict(t: Test):
    return {
        "id": t.id,
        "title": t.title,
        "subject": t.subject,
        "course": t.course,
        "curriculum": t.curriculum,
        "academic_year": t.academic_year,
        "exam_name": t.exam_name,
        "duration_minutes": t.duration_minutes,
        "total_marks": t.total_marks,
        "is_adaptive": t.is_adaptive,
        "is_published": t.is_published,
        "approval_status": t.approval_status,
        "question_count": len(t.questions),
    }


@router.post("/tests", status_code=status.HTTP_201_CREATED)
def create_test(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_teacher)
):
    """
    payload: {
      title, subject, course, curriculum, academic_year, exam_name,
      duration_minutes, total_marks, is_adaptive,
      questions: [ {question_text, question_type, options, correct_answer, explanation, topic, difficulty, marks} ]
    }
    """
    scope_values = [
        (payload.get(field) or "").strip()
        for field in ("course", "curriculum", "academic_year")
    ]
    if any(scope_values) and not all(scope_values):
        raise HTTPException(
            status_code=422,
            detail="Course, institution, and semester must all be provided for a scoped test.",
        )

    test = Test(
        title=payload.get("title", "New Test"),
        subject=payload.get("subject", ""),
        course=scope_values[0] or None,
        curriculum=scope_values[1] or None,
        academic_year=scope_values[2] or None,
        exam_name=payload.get("exam_name"),
        duration_minutes=payload.get("duration_minutes", 30),
        total_marks=payload.get("total_marks", 20),
        is_adaptive=payload.get("is_adaptive", False),
        is_published=False,
        approval_status="pending",
        created_by=current_user.id,
    )
    db.add(test)
    db.flush()

    for idx, q in enumerate(payload.get("questions", [])):
        tq = TestQuestion(
            test_id=test.id,
            question_text=q.get("question_text", ""),
            question_type=q.get("question_type", "mcq"),
            options=q.get("options"),
            correct_answer=str(q.get("correct_answer", "")),
            explanation=q.get("explanation"),
            topic=q.get("topic", "General"),
            difficulty=q.get("difficulty", "medium"),
            marks=float(q.get("marks", 1.0)),
        )
        db.add(tq)

    db.commit()
    db.refresh(test)
    return {"id": test.id, "message": "Test created"}


@router.patch("/tests/{test_id}/review")
def review_test(
    test_id: int,
    payload: TestReviewRequest,
    db: Session = Depends(get_db),
    current_teacher: Student = Depends(require_teacher),
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found.")
    if test.approval_status != "pending":
        raise HTTPException(status_code=409, detail="Only pending tests can be reviewed.")

    test.approval_status = "approved" if payload.decision == "approve" else "rejected"
    test.is_published = payload.decision == "approve"
    db.commit()
    return {"id": test.id, "approval_status": test.approval_status}


@router.get("/tests/{test_id}")
def get_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    if not _test_matches_student_scope(
        test, _student_test_scope(db, current_user)
    ):
        raise HTTPException(status_code=404, detail="Test not found")
    if current_user.role not in {"teacher", "admin"} and (
        not test.is_published or test.approval_status != "approved"
    ):
        raise HTTPException(status_code=404, detail="Test not found")
    questions = []
    for q in test.questions:
        questions.append({
            "id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": q.options,
            "topic": q.topic,
            "difficulty": q.difficulty,
            "marks": q.marks,
            # Do NOT send correct_answer or explanation to student at this stage
        })
    return {
        **_test_dict(test),
        "questions": questions,
    }


# ─────────────────────────────────────────────
# ATTEMPT FLOW: start → submit
# ─────────────────────────────────────────────

@router.post("/tests/{test_id}/start", status_code=status.HTTP_201_CREATED)
def start_test_attempt(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    test = db.query(Test).filter(
        Test.id == test_id,
        Test.is_published.is_(True),
        Test.approval_status == "approved",
    ).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    if not _test_matches_student_scope(
        test, _student_test_scope(db, current_user)
    ):
        raise HTTPException(status_code=404, detail="Test not found")

    attempt = TestAttempt(
        test_id=test_id,
        student_id=current_user.id,
        status="in_progress",
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return {
        "attempt_id": attempt.id,
        "test_id": test_id,
        "duration_minutes": test.duration_minutes,
        "started_at": attempt.created_at.isoformat(),
        "total_marks": test.total_marks,
    }


@router.post("/tests/{test_id}/submit")
def submit_test_attempt(
    test_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """
    payload: {
      attempt_id: int,
      time_taken_seconds: int,
      answers: [ {question_id: int, student_answer: str} ]
    }
    Returns scored result with topic breakdown. Also updates SkillProfile.
    """
    attempt_id = payload.get("attempt_id")
    attempt = db.query(TestAttempt).filter(
        TestAttempt.id == attempt_id,
        TestAttempt.student_id == current_user.id,
        TestAttempt.test_id == test_id,
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.status == "completed":
        raise HTTPException(status_code=400, detail="Attempt already submitted")

    test = db.query(Test).filter(Test.id == test_id).first()
    questions = {q.id: q for q in test.questions}

    # Grade answers
    total_score = 0.0
    topic_stats: dict = {}  # topic -> {correct, total, marks_earned, total_marks}
    answer_records = []

    for ans in payload.get("answers", []):
        q_id = ans.get("question_id")
        student_ans = str(ans.get("student_answer", "")).strip()
        q = questions.get(q_id)
        if not q:
            continue

        # Evaluate correctness
        is_correct = False
        if q.question_type in ("mcq", "true_false"):
            is_correct = student_ans == str(q.correct_answer).strip()
        else:
            # Short answer: case-insensitive substring match
            is_correct = q.correct_answer.lower() in student_ans.lower() if student_ans else False

        marks_awarded = q.marks if is_correct else 0.0
        total_score += marks_awarded

        # Track per-topic
        t = q.topic
        if t not in topic_stats:
            topic_stats[t] = {"correct": 0, "total": 0, "marks_earned": 0.0, "total_marks": 0.0}
        topic_stats[t]["total"] += 1
        topic_stats[t]["total_marks"] += q.marks
        if is_correct:
            topic_stats[t]["correct"] += 1
            topic_stats[t]["marks_earned"] += q.marks

        aa = AttemptAnswer(
            attempt_id=attempt_id,
            question_id=q_id,
            student_answer=student_ans,
            is_correct=is_correct,
            marks_awarded=marks_awarded,
        )
        db.add(aa)
        answer_records.append((q, is_correct))

    # Finalise attempt
    total_possible = test.total_marks or sum(q.marks for q in questions.values())
    accuracy = (total_score / max(total_possible, 1)) * 100.0
    attempt.score = total_score
    attempt.total_marks = int(total_possible)
    attempt.accuracy = accuracy
    attempt.time_taken_seconds = payload.get("time_taken_seconds", 0)
    attempt.status = "completed"
    attempt.completed_at = datetime.datetime.utcnow()

    # Build topic breakdown
    breakdown = {}
    strengths, weaknesses, suggestions = [], [], []
    for topic, stats in topic_stats.items():
        pct = (stats["correct"] / max(stats["total"], 1)) * 100.0
        breakdown[topic] = {
            "correct": stats["correct"],
            "total": stats["total"],
            "accuracy": round(pct, 1),
            "marks_earned": stats["marks_earned"],
            "total_marks": stats["total_marks"],
        }
        if pct >= 70:
            strengths.append(topic)
        else:
            weaknesses.append(topic)
            if pct < 50:
                suggestions.append(topic)

    # Save TestResult
    result = TestResult(
        attempt_id=attempt_id,
        topic_wise_breakdown=breakdown,
        strengths=strengths,
        weaknesses=weaknesses,
        suggested_revision_topics=suggestions,
    )
    db.add(result)

    # ───────────────────────────────────────────
    # Update SkillProfile from this test result
    # ───────────────────────────────────────────
    for topic, stats in topic_stats.items():
        pct = (stats["correct"] / max(stats["total"], 1)) * 100.0
        new_status = "strong" if pct >= 70 else ("average" if pct >= 40 else "weak")

        existing = db.query(SkillProfile).filter(
            SkillProfile.student_id == current_user.id,
            SkillProfile.subject == test.subject,
            SkillProfile.topic == topic,
        ).first()
        if existing:
            # Exponential moving average (EMA) so single test doesn't dominate
            existing.mastery_score = round(0.7 * existing.mastery_score + 0.3 * pct, 2)
            existing.status = new_status
            existing.tests_taken = (existing.tests_taken or 0) + 1
        else:
            db.add(SkillProfile(
                student_id=current_user.id,
                subject=test.subject,
                topic=topic,
                status=new_status,
                mastery_score=round(pct, 2),
                tests_taken=1,
            ))

    db.commit()

    # Class average for this test (excluding this attempt for fairness)
    class_attempts = db.query(TestAttempt).filter(
        TestAttempt.test_id == test_id,
        TestAttempt.status == "completed",
        TestAttempt.id != attempt_id,
    ).all()
    class_avg = (
        sum(a.accuracy for a in class_attempts) / len(class_attempts)
        if class_attempts else None
    )

    return {
        "attempt_id": attempt_id,
        "score": total_score,
        "total_marks": total_possible,
        "accuracy": round(accuracy, 1),
        "time_taken_seconds": attempt.time_taken_seconds,
        "topic_breakdown": breakdown,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggested_revision_topics": suggestions,
        "class_average_accuracy": round(class_avg, 1) if class_avg else None,
        "skill_profile_updated": True,
    }


@router.get("/tests/attempts/{attempt_id}/result")
def get_attempt_result(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    attempt = db.query(TestAttempt).filter(
        TestAttempt.id == attempt_id,
        TestAttempt.student_id == current_user.id,
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    result = attempt.result
    test = attempt.test

    # Answers with correct answer revealed
    answers_detail = []
    for aa in attempt.answers:
        q = aa.question
        answers_detail.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": q.options,
            "student_answer": aa.student_answer,
            "correct_answer": q.correct_answer,
            "is_correct": aa.is_correct,
            "marks_awarded": aa.marks_awarded,
            "explanation": q.explanation,
            "topic": q.topic,
        })

    # Previous attempts for trend
    previous = db.query(TestAttempt).filter(
        TestAttempt.test_id == test.id,
        TestAttempt.student_id == current_user.id,
        TestAttempt.id != attempt_id,
        TestAttempt.status == "completed",
    ).order_by(TestAttempt.created_at).all()

    return {
        "attempt_id": attempt_id,
        "test_title": test.title,
        "test_subject": test.subject,
        "score": attempt.score,
        "total_marks": attempt.total_marks,
        "accuracy": attempt.accuracy,
        "time_taken_seconds": attempt.time_taken_seconds,
        "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        "topic_breakdown": result.topic_wise_breakdown if result else {},
        "strengths": result.strengths if result else [],
        "weaknesses": result.weaknesses if result else [],
        "suggested_revision_topics": result.suggested_revision_topics if result else [],
        "answers_detail": answers_detail,
        "previous_attempts": [
            {
                "attempt_id": a.id,
                "score": a.score,
                "accuracy": a.accuracy,
                "completed_at": a.completed_at.isoformat() if a.completed_at else None,
            }
            for a in previous
        ],
    }


# ─────────────────────────────────────────────
# ADAPTIVE TEST GENERATION
# ─────────────────────────────────────────────

@router.post("/tests/adaptive")
def generate_adaptive_test(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """
    Generates an adaptive test from the student's weak topics.
    payload: { subject: str, num_questions: int (default 10) }
    Returns a one-time test with more questions from weak topics.
    """
    subject = payload.get("subject", "")
    num_questions = int(payload.get("num_questions", 10))

    # Find weak topics for this student in this subject
    weak_skills = db.query(SkillProfile).filter(
        SkillProfile.student_id == current_user.id,
        SkillProfile.subject.ilike(f"%{subject}%"),
        SkillProfile.status.in_(["weak", "average"]),
    ).order_by(SkillProfile.mastery_score).all()

    weak_topics = [s.topic for s in weak_skills]

    # Find published tests that match subject
    test_query = db.query(Test).filter(
        Test.subject.ilike(f"%{subject}%"),
        Test.is_published.is_(True),
        Test.approval_status == "approved",
    )
    scope = _student_test_scope(db, current_user)
    test_query = _filter_tests_to_scope(test_query, scope)
    matching_tests = [
        test for test in test_query.all()
        if _test_matches_student_scope(test, scope)
    ]

    if not matching_tests:
        raise HTTPException(
            status_code=404,
            detail=f"No published tests found for subject '{subject}'. Ask your teacher to create one."
        )

    # Pull questions, prioritising weak topic questions
    all_questions = []
    for t in matching_tests:
        all_questions.extend(t.questions)

    weak_qs = [q for q in all_questions if q.topic in weak_topics]
    other_qs = [q for q in all_questions if q.topic not in weak_topics]

    # 70% from weak topics, 30% from rest
    n_weak = min(int(num_questions * 0.7), len(weak_qs))
    n_other = min(num_questions - n_weak, len(other_qs))

    import random
    selected = random.sample(weak_qs, n_weak) + random.sample(other_qs, n_other)
    random.shuffle(selected)

    return {
        "adaptive": True,
        "subject": subject,
        "weak_topics_targeted": weak_topics[:5],
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "options": q.options,
                "topic": q.topic,
                "difficulty": q.difficulty,
                "marks": q.marks,
            }
            for q in selected
        ],
        "note": "Submit answers via POST /tests/{original_test_id}/submit with the attempt_id",
    }


# ─────────────────────────────────────────────
# TEACHER DASHBOARD: Class Performance
# ─────────────────────────────────────────────

@router.get("/tests/{test_id}/class-results")
def get_class_results(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_teacher)
):
    """Teacher: see all student results for a specific test."""
    attempts = db.query(TestAttempt).filter(
        TestAttempt.test_id == test_id,
        TestAttempt.status == "completed",
    ).all()
    if not attempts:
        return {"test_id": test_id, "attempts": [], "class_average": None}

    avg_accuracy = sum(a.accuracy for a in attempts) / len(attempts)
    return {
        "test_id": test_id,
        "class_average_accuracy": round(avg_accuracy, 1),
        "attempts": [
            {
                "attempt_id": a.id,
                "student_id": a.student_id,
                "student_name": a.student.name if a.student else None,
                "score": a.score,
                "total_marks": a.total_marks,
                "accuracy": a.accuracy,
                "completed_at": a.completed_at.isoformat() if a.completed_at else None,
            }
            for a in attempts
        ],
    }
