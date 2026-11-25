"""
Module 4: Higher Studies & Course Guidance Router
Endpoints for roadmap, exams, colleges, courses (ML recommender),
scholarships, study abroad, checklist, deadlines, questionnaire,
counselling requests.
"""
import os
import re
from typing import List, Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_
import datetime

from database import get_db
from auth import get_current_user, require_teacher
from medical_guidance import ensure_medical_pg_courses
from models import (
    Student, StudentProfile, SkillProfile, InterestProfile,
    RoadmapItem, EntranceExam, College, Course, Scholarship,
    StudyAbroadInfo, ApplicationChecklistItem, DeadlineReminder,
    QuestionnaireQuestion, StudentQuestionnaireAnswer, CounsellingRequest,
    GuidanceCourse, GuidanceActivity
)

router = APIRouter()

class CounsellingRequestCreate(BaseModel):
    request_type: Literal["higher_studies", "study_support"] = "higher_studies"
    message: str = Field(..., min_length=1)
    preferred_mode: str = "Online"


class GuidanceActivityCreate(BaseModel):
    activity_type: Literal["course", "exam"]
    entity_id: int = Field(..., ge=1)


# ─────────────────────────────────────────────
# ROADMAP
# ─────────────────────────────────────────────

@router.get("/roadmap")
def get_roadmap(
    stream: Optional[str] = Query(None, description="Filter by stream e.g. Science, Commerce"),
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Return roadmap stages, optionally filtered by stream."""
    q = db.query(RoadmapItem)
    if stream:
        q = q.filter(RoadmapItem.stream.ilike(f"%{stream}%"))
    items = q.order_by(RoadmapItem.order_index).all()
    return [
        {
            "id": r.id,
            "stage": r.stage,
            "stream": r.stream,
            "title": r.title,
            "description": r.description,
            "options": r.options,
            "next_steps": r.next_steps,
        }
        for r in items
    ]


# ─────────────────────────────────────────────
# ENTRANCE EXAMS
# ─────────────────────────────────────────────

@router.get("/exams")
def list_exams(
    stream: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    q = db.query(EntranceExam)
    if stream:
        q = q.filter(EntranceExam.stream.ilike(f"%{stream}%"))
    if search:
        q = q.filter(
            or_(
                EntranceExam.name.ilike(f"%{search}%"),
                EntranceExam.code.ilike(f"%{search}%"),
            )
        )
    total = q.count()
    exams = q.offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": e.id,
                "name": e.name,
                "code": e.code,
                "conducting_body": e.conducting_body,
                "stream": e.stream,
                "eligibility": e.eligibility,
                "exam_dates": e.exam_dates,
                "official_website_url": e.official_website_url,
            }
            for e in exams
        ],
    }


@router.get("/exams/{exam_id}")
def get_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    exam = db.query(EntranceExam).filter(EntranceExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return {
        "id": exam.id,
        "name": exam.name,
        "code": exam.code,
        "conducting_body": exam.conducting_body,
        "eligibility": exam.eligibility,
        "syllabus": exam.syllabus,
        "exam_dates": exam.exam_dates,
        "application_process": exam.application_process,
        "preparation_tips": exam.preparation_tips,
        "official_website_url": exam.official_website_url,
        "stream": exam.stream,
    }


# ─────────────────────────────────────────────
# COLLEGES
# ─────────────────────────────────────────────

@router.get("/colleges")
def list_colleges(
    state: Optional[str] = None,
    college_type: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    q = db.query(College)
    if state:
        q = q.filter(College.state.ilike(f"%{state}%"))
    if college_type:
        q = q.filter(College.college_type.ilike(f"%{college_type}%"))
    if search:
        q = q.filter(College.name.ilike(f"%{search}%"))
    total = q.count()
    colleges = q.order_by(College.nirf_ranking.nullslast()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": c.id,
                "name": c.name,
                "location": c.location,
                "state": c.state,
                "college_type": c.college_type,
                "nirf_ranking": c.nirf_ranking,
                "courses_offered": c.courses_offered,
                "admission_process": c.admission_process,
                "website_url": c.website_url,
                "average_annual_fee": c.average_annual_fee,
                "established_year": c.established_year,
            }
            for c in colleges
        ],
    }


# ─────────────────────────────────────────────
# COURSES — List, Recommend (ML), Compare, Career Path
# ─────────────────────────────────────────────

@router.get("/courses")
def list_courses(
    stream: Optional[str] = None,
    degree_level: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    q = db.query(Course)
    if stream:
        q = q.filter(Course.stream.ilike(f"%{stream}%"))
    if degree_level:
        q = q.filter(Course.degree_level.ilike(f"%{degree_level}%"))
    if search:
        q = q.filter(Course.title.ilike(f"%{search}%"))
    total = q.count()
    courses = q.offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [_course_dict(c) for c in courses],
    }


def _course_dict(c: Course, match_score: float = None, match_reason: str = None):
    d = {
        "id": c.id,
        "title": c.title,
        "stream": c.stream,
        "degree_level": c.degree_level,
        "duration_years": c.duration_years,
        "eligibility": c.eligibility,
        "exams": c.exams,
        "fee_range": c.fee_range,
        "skills_needed": c.skills_needed,
        "job_roles": c.job_roles,
        "salary_range": c.salary_range,
        "scope": c.scope,
        "top_colleges": c.top_colleges,
    }
    if match_score is not None:
        d["match_score"] = round(match_score, 1)
    if match_reason is not None:
        d["match_reason"] = match_reason
    return d


def _diploma_branch(profile: Optional[StudentProfile]) -> Optional[str]:
    if not profile:
        return None

    qualification = " ".join(
        value or ""
        for value in (profile.course, profile.department, profile.stream)
    ).casefold()
    if not re.search(r"\b(diploma|polytechnic)\b", qualification):
        return None

    if (
        any(term in qualification for term in ("computer", "information technology", "software"))
        or re.search(r"\bit\b", qualification)
    ):
        return "computer"
    if any(term in qualification for term in ("electronics", "communication", "telecommunication")):
        return "electronics"
    if "electrical" in qualification:
        return "electrical"
    if "civil" in qualification:
        return "civil"
    if "mechanical" in qualification:
        return "mechanical"
    return "unknown"


def _filter_courses_for_diploma(courses: List[Course], profile: Optional[StudentProfile]) -> List[Course]:
    branch = _diploma_branch(profile)
    if branch is None:
        return courses
    if branch == "unknown":
        return []

    branch_terms = {
        "computer": ("computer", "information technology", "software"),
        "electronics": ("electronics", "communication", "telecommunication"),
        "electrical": ("electrical",),
        "civil": ("civil",),
        "mechanical": ("mechanical",),
    }[branch]
    return [
        course for course in courses
        if "lateral entry" in (course.title or "").casefold()
        and "diploma" in (course.eligibility or "").casefold()
        and any(term in (course.title or "").casefold() for term in branch_terms)
    ]


def _current_bachelor_stream(profile: Optional[StudentProfile]) -> Optional[str]:
    if not profile:
        return None

    qualification = " ".join(
        value or ""
        for value in (profile.course, profile.department, profile.stream)
    ).casefold()
    qualification = re.sub(r"[^a-z0-9]+", " ", qualification).strip()

    degree_patterns = (
        (r"\b(?:b\s*a|ba|bachelor of arts)\b", "Humanities"),
        (r"\b(?:b\s*com|bcom|bachelor of commerce)\b", "Commerce"),
        (r"\b(?:b\s*sc|bsc|bachelor of science)\b", "Science"),
        (r"\b(?:b\s*tech|b\s*e|be|bachelor of engineering|bachelor of technology)\b", "Engineering"),
        (r"\b(?:bca|bachelor of computer applications)\b", "Computer Applications"),
        (r"\b(?:bba|bachelor of business administration)\b", "Management"),
        (
            r"\b(?:mbbs|bds|bams|bhms|b\s*pharm|bpharm|bachelor of medicine|bachelor of surgery|bachelor of dental|bachelor of pharmacy|bachelor of ayurveda|b\s*sc\s*nursing|nursing|allied health)\b",
            "Health Sciences",
        ),
        (r"\b(?:llb|bachelor of laws?)\b", "Law"),
        (r"\b(?:b\s*des|bdes|bachelor of design)\b", "Design"),
    )
    return next(
        (stream for pattern, stream in degree_patterns if re.search(pattern, qualification)),
        None,
    )


def _bachelor_eligibility_fit(course: Course, current_stream: str) -> float:
    eligibility = re.sub(r"[^a-z0-9]+", " ", (course.eligibility or "").casefold()).strip()
    if any(term in eligibility for term in ("any bachelor", "any discipline", "any stream")):
        return 0.5

    stream_terms = {
        "Humanities": ("humanities", "arts", "social science", "bachelor of arts", "b a"),
        "Commerce": ("commerce", "bachelor of commerce", "b com", "bcom"),
        "Science": ("science", "stem", "bachelor of science", "b sc", "bsc"),
        "Engineering": ("engineering", "bachelor of engineering", "b tech", "b e"),
        "Computer Applications": ("computer applications", "computer science", "bca"),
        "Management": ("management", "business administration", "bba"),
        "Health Sciences": (
            "health sciences", "health science", "mbbs", "bds", "bams", "bhms",
            "medicine", "medical", "neet pg", "ini cet", "neetpg", "inicet", "nbe", "nmc",
            "doctor of medicine", "master of surgery", "pharmacy", "nursing"
        ),
        "Law": ("law", "llb", "legal"),
        "Design": ("design", "b des", "bdes", "ceed"),
    }
    return 1.0 if any(term in eligibility for term in stream_terms.get(current_stream, ())) else 0.0


def _filter_courses_for_bachelor(
    courses: List[Course],
    current_stream: str,
) -> List[Course]:
    return [
        course for course in courses
        if (course.degree_level or "").casefold().startswith("postgraduate")
        and _bachelor_eligibility_fit(course, current_stream) > 0
    ]


@router.get("/courses/recommend")
def recommend_courses(
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """
    ML-based course recommender.
    Combines:
      1. Student's SkillProfile (strong subjects → stream weights)
      2. StudentQuestionnaireAnswer stream_weights
      3. InterestProfile tags (from original questionnaire)
    Returns top-10 courses with match_score and match_reason.
    """
    # Ensure health sciences & medical postgraduate courses exist in DB
    ensure_medical_pg_courses(db)

    profile = db.query(StudentProfile).filter(
        StudentProfile.student_id == current_user.id
    ).first()

    # Build skill-based stream weights
    skills = db.query(SkillProfile).filter(SkillProfile.student_id == current_user.id).all()
    skill_weights: dict[str, float] = {}
    subject_map = {
        "mathematics": ["Engineering", "Computer Applications", "Science"],
        "physics": ["Engineering", "Science"],
        "chemistry": ["Health Sciences", "Science"],
        "biology": ["Health Sciences", "Science"],
        "computer science": ["Computer Applications", "Engineering"],
        "commerce": ["Commerce"],
        "economics": ["Commerce", "Humanities"],
        "english": ["Humanities", "Law"],
        "history": ["Humanities", "Law"],
        "geography": ["Humanities", "Science"],
        "political science": ["Humanities", "Law"],
        "design": ["Design"],
    }
    for skill in skills:
        subj_lower = skill.subject.lower()
        multiplier = 1.5 if skill.status == "strong" else (1.0 if skill.status == "average" else 0.5)
        for subj_key, streams in subject_map.items():
            if subj_key in subj_lower:
                for s in streams:
                    skill_weights[s] = skill_weights.get(s, 0) + multiplier * (skill.mastery_score / 100.0)

    # Build questionnaire answer stream weights
    answers = (
        db.query(StudentQuestionnaireAnswer)
        .filter(StudentQuestionnaireAnswer.student_id == current_user.id)
        .all()
    )
    qa_weights: dict[str, float] = {}
    for ans in answers:
        q = db.query(QuestionnaireQuestion).filter(QuestionnaireQuestion.id == ans.question_id).first()
        if q and q.options and ans.selected_option_index < len(q.options):
            opt = q.options[ans.selected_option_index]
            if isinstance(opt, dict) and "stream_weights" in opt:
                for stream, w in opt["stream_weights"].items():
                    qa_weights[stream] = qa_weights.get(stream, 0) + float(w)

    # Combine weights (60% skill, 40% questionnaire)
    all_streams = set(list(skill_weights.keys()) + list(qa_weights.keys()))
    combined: dict[str, float] = {}
    for s in all_streams:
        combined[s] = 0.6 * skill_weights.get(s, 0) + 0.4 * qa_weights.get(s, 0)

    courses = _filter_courses_for_diploma(db.query(Course).all(), profile)
    diploma_branch = _diploma_branch(profile)
    current_bachelor_stream = _current_bachelor_stream(profile) if not diploma_branch else None
    if current_bachelor_stream:
        courses = _filter_courses_for_bachelor(courses, current_bachelor_stream)

    # Fallback: if no data, return eligible courses with equal weight.
    if not combined:
        reason = (
            "Possible lateral-entry pathway; verify the current admission rules and branch eligibility."
            if diploma_branch
            else (
                f"Primary postgraduate medical specialization after your {profile.course.strip()} degree (NEET-PG / INI-CET)."
                if current_bachelor_stream == "Health Sciences" and profile and profile.course
                else (
                    f"Postgraduate option after your current {profile.course.strip()} studies; "
                    "verify subject-specific admission eligibility."
                    if current_bachelor_stream and profile and profile.course
                    else "Explore all career options"
                )
            )
        )
        return [_course_dict(c, 50.0, reason) for c in courses]

    # Score every course
    scored = []
    max_score = max(combined.values()) if combined else 1
    for course in courses:
        raw = combined.get(course.stream, 0)
        if current_bachelor_stream:
            degree_fit = _bachelor_eligibility_fit(course, current_bachelor_stream)
            is_direct_stream = (course.stream.casefold() == current_bachelor_stream.casefold())
            stream_boost = 1.0 if is_direct_stream else 0.5
            raw += max(max_score, 1.0) * stream_boost * degree_fit
            score_ceiling = max(max_score, 1.0) * (1.0 + stream_boost)
        else:
            score_ceiling = max(max_score, 0.01)
        pct = min(100.0, round((raw / score_ceiling) * 100.0, 1))

        # Build reason string
        strong_subjects = [
            sk.subject for sk in skills
            if sk.status == "strong" and any(
                subj in sk.subject.lower()
                for subj in subject_map.get(course.stream.lower().replace(" ", "_"), [])
            )
        ]
        if current_bachelor_stream:
            current_course = profile.course.strip() if profile and profile.course else "bachelor's"
            is_direct_stream = (course.stream.casefold() == current_bachelor_stream.casefold())
            if current_bachelor_stream == "Health Sciences" and course.stream == "Health Sciences":
                reason = f"Primary postgraduate medical specialization after your {current_course} degree (NEET-PG / INI-CET)."
            elif is_direct_stream:
                reason = f"Direct postgraduate advancement in {course.stream} following your {current_course} studies."
            else:
                reason = f"Eligible postgraduate option after your current {current_course} studies; verify admission eligibility."
        elif strong_subjects:
            reason = f"Strong in {', '.join(strong_subjects[:2])}"
        elif pct > 60:
            reason = f"Matches your interests and skills in {course.stream}"
        elif pct > 30:
            reason = f"Good fit based on your questionnaire responses"
        else:
            reason = "Broad career option worth exploring"

        if diploma_branch:
            reason = "Possible lateral-entry pathway; verify the current admission rules and branch eligibility."
        scored.append((pct, course, reason))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [_course_dict(c, score, reason) for score, c, reason in scored[:10]]


@router.get("/courses/compare")
def compare_courses(
    ids: str = Query(..., description="Comma-separated course IDs, e.g. 1,2,3"),
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Side-by-side comparison of 2–3 courses."""
    try:
        id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="ids must be comma-separated integers")
    if not 2 <= len(id_list) <= 3:
        raise HTTPException(status_code=400, detail="Provide 2 or 3 course IDs for comparison")
    courses = db.query(Course).filter(Course.id.in_(id_list)).all()
    if len(courses) < 2:
        raise HTTPException(status_code=404, detail="One or more courses not found")
    return {"courses": [_course_dict(c) for c in courses]}


@router.get("/courses/{course_id}")
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return _course_dict(course)


@router.get("/courses/{course_id}/career-path")
def career_path(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Return detailed career path for a course."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return {
        "course_title": course.title,
        "stream": course.stream,
        "job_roles": course.job_roles,
        "salary_range": course.salary_range,
        "scope": course.scope,
        "skills_needed": course.skills_needed,
        "higher_study_options": [
            f"M.Tech / M.E. in {course.stream}" if "Engineering" in course.stream else f"M.Sc / MBA in {course.stream}",
            "PhD / Research",
            "MBA (Management specialisation)",
        ],
        "recommended_certifications": [
            "Google / AWS / Microsoft Cloud Certifications",
            "NPTEL Online Courses",
            "Coursera / edX Professional Certificates",
        ],
        "growth_path": [
            f"Entry Level: {course.job_roles[0] if course.job_roles else 'Graduate Trainee'}",
            "Mid Level (3-5 yrs): Senior Specialist / Team Lead",
            "Senior Level (8+ yrs): Manager / Architect / Consultant",
        ],
    }


# ─────────────────────────────────────────────
# SCHOLARSHIPS
# ─────────────────────────────────────────────

@router.get("/scholarships")
def list_scholarships(
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    q = db.query(Scholarship)
    if category:
        q = q.filter(Scholarship.category.ilike(f"%{category}%"))
    if search:
        q = q.filter(Scholarship.name.ilike(f"%{search}%"))
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [
            {
                "id": s.id,
                "name": s.name,
                "provider": s.provider,
                "eligibility": s.eligibility,
                "amount_and_benefits": s.amount_and_benefits,
                "deadline_description": s.deadline_description,
                "application_process": s.application_process,
                "application_url": s.application_url,
                "category": s.category,
            }
            for s in items
        ],
    }


# ─────────────────────────────────────────────
# STUDY ABROAD
# ─────────────────────────────────────────────

@router.get("/study-abroad")
def list_study_abroad(
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    items = db.query(StudyAbroadInfo).all()
    return [
        {
            "id": s.id,
            "country": s.country,
            "flag_emoji": s.flag_emoji,
            "popular_courses": s.popular_courses,
            "required_tests": s.required_tests,
            "avg_tuition_cost": s.avg_tuition_cost,
            "living_cost": s.living_cost,
            "visa_work_rights": s.visa_work_rights,
            "intake_timelines": s.intake_timelines,
        }
        for s in items
    ]


# ─────────────────────────────────────────────
# APPLICATION CHECKLIST
# ─────────────────────────────────────────────

@router.get("/checklist")
def get_checklist(
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    items = (
        db.query(ApplicationChecklistItem)
        .filter(ApplicationChecklistItem.student_id == current_user.id)
        .order_by(ApplicationChecklistItem.created_at)
        .all()
    )
    return [
        {
            "id": i.id,
            "title": i.title,
            "category": i.category,
            "deadline": i.deadline.isoformat() if i.deadline else None,
            "is_completed": i.is_completed,
            "notes": i.notes,
        }
        for i in items
    ]


@router.post("/checklist", status_code=status.HTTP_201_CREATED)
def add_checklist_item(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    deadline = None
    if payload.get("deadline"):
        try:
            deadline = datetime.datetime.fromisoformat(payload["deadline"])
        except Exception:
            pass
    item = ApplicationChecklistItem(
        student_id=current_user.id,
        title=payload.get("title", ""),
        category=payload.get("category", "General"),
        deadline=deadline,
        notes=payload.get("notes"),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "message": "Checklist item added"}


@router.patch("/checklist/{item_id}")
def update_checklist_item(
    item_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    item = (
        db.query(ApplicationChecklistItem)
        .filter(
            ApplicationChecklistItem.id == item_id,
            ApplicationChecklistItem.student_id == current_user.id,
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if "is_completed" in payload:
        item.is_completed = bool(payload["is_completed"])
    if "notes" in payload:
        item.notes = payload["notes"]
    db.commit()
    return {"message": "Updated"}


@router.delete("/checklist/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checklist_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    item = (
        db.query(ApplicationChecklistItem)
        .filter(
            ApplicationChecklistItem.id == item_id,
            ApplicationChecklistItem.student_id == current_user.id,
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()


# ─────────────────────────────────────────────
# DEADLINE REMINDERS
# ─────────────────────────────────────────────

@router.get("/reminders")
def get_reminders(
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    now = datetime.datetime.utcnow()
    items = (
        db.query(DeadlineReminder)
        .filter(
            DeadlineReminder.student_id == current_user.id,
            DeadlineReminder.is_dismissed == False,
            DeadlineReminder.target_date >= now,
        )
        .order_by(DeadlineReminder.target_date)
        .all()
    )
    return [
        {
            "id": r.id,
            "title": r.title,
            "target_date": r.target_date.isoformat(),
            "related_type": r.related_type,
            "reminder_type": r.reminder_type,
            "days_left": (r.target_date - now).days,
        }
        for r in items
    ]


@router.post("/reminders", status_code=status.HTTP_201_CREATED)
def add_reminder(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    target_date = datetime.datetime.fromisoformat(payload["target_date"])
    reminder = DeadlineReminder(
        student_id=current_user.id,
        title=payload.get("title", "Reminder"),
        target_date=target_date,
        related_type=payload.get("related_type"),
        reminder_type=payload.get("reminder_type", "Deadline"),
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return {"id": reminder.id, "message": "Reminder created"}


@router.patch("/reminders/{reminder_id}/dismiss")
def dismiss_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    r = (
        db.query(DeadlineReminder)
        .filter(
            DeadlineReminder.id == reminder_id,
            DeadlineReminder.student_id == current_user.id,
        )
        .first()
    )
    if not r:
        raise HTTPException(status_code=404, detail="Reminder not found")
    r.is_dismissed = True
    db.commit()
    return {"message": "Dismissed"}


@router.post("/activity", status_code=status.HTTP_201_CREATED)
def track_guidance_activity(
    payload: GuidanceActivityCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    if payload.activity_type == "course":
        item = db.query(Course).filter(Course.id == payload.entity_id).first()
        title = item.title if item else None
    else:
        item = db.query(EntranceExam).filter(EntranceExam.id == payload.entity_id).first()
        title = item.name if item else None
    if not item:
        raise HTTPException(status_code=404, detail="Guidance item not found.")

    activity = GuidanceActivity(
        student_id=current_user.id,
        activity_type=payload.activity_type,
        entity_id=item.id,
        title=title,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return {"id": activity.id, "message": "Guidance activity recorded."}


@router.get("/activity")
def list_guidance_activity(
    db: Session = Depends(get_db),
    current_teacher: Student = Depends(require_teacher),
):
    rows = db.query(GuidanceActivity, Student).join(
        Student, Student.id == GuidanceActivity.student_id
    ).order_by(GuidanceActivity.created_at.desc()).limit(100).all()
    return [
        {
            "id": activity.id,
            "student_id": student.id,
            "student_name": student.name,
            "activity_type": activity.activity_type,
            "title": activity.title,
            "created_at": activity.created_at.isoformat(),
        }
        for activity, student in rows
    ]


# ─────────────────────────────────────────────
# INTEREST QUESTIONNAIRE
# ─────────────────────────────────────────────

@router.get("/questionnaire/questions")
def get_questionnaire_questions(
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    questions = db.query(QuestionnaireQuestion).order_by(QuestionnaireQuestion.order_index).all()
    return [
        {
            "id": q.id,
            "question_text": q.question_text,
            "category": q.category,
            "options": [opt.get("text", opt) if isinstance(opt, dict) else opt for opt in q.options],
            "order_index": q.order_index,
        }
        for q in questions
    ]


@router.post("/questionnaire/submit")
def submit_questionnaire(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """
    payload: { answers: [ {question_id: int, selected_option_index: int}, ... ] }
    Saves answers and returns course recommendations.
    """
    answers_data = payload.get("answers", [])
    # Delete old answers
    db.query(StudentQuestionnaireAnswer).filter(
        StudentQuestionnaireAnswer.student_id == current_user.id
    ).delete()

    for ans in answers_data:
        q_id = ans.get("question_id")
        idx = ans.get("selected_option_index", 0)
        qa = StudentQuestionnaireAnswer(
            student_id=current_user.id,
            question_id=q_id,
            selected_option_index=idx,
        )
        db.add(qa)
    db.commit()

    return {"message": "Answers saved. Call /courses/recommend for recommendations."}


# ─────────────────────────────────────────────
# COUNSELLING REQUESTS
# ─────────────────────────────────────────────

@router.post("/counselling", status_code=status.HTTP_201_CREATED)
def create_counselling_request(
    payload: CounsellingRequestCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit counselling requests")
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="A request message is required.")
    if payload.request_type == "study_support":
        profile = db.query(StudentProfile).filter(
            StudentProfile.student_id == current_user.id
        ).first()
        if profile:
            course_details = " / ".join(
                value for value in (profile.course, profile.college, profile.semester) if value
            )
            if course_details:
                message = f"{message}\n\nStudent course details: {course_details}"
    req = CounsellingRequest(
        student_id=current_user.id,
        request_type=payload.request_type,
        message=message,
        preferred_mode=payload.preferred_mode,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return {"id": req.id, "message": "Counselling request submitted"}


@router.get("/counselling")
def get_counselling_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """
    - Teachers/admins: see all requests.
    - Students: see only their own.
    """
    q = db.query(CounsellingRequest)
    if current_user.role == "student":
        q = q.filter(CounsellingRequest.student_id == current_user.id)
    if status_filter:
        q = q.filter(CounsellingRequest.status == status_filter)

    items = q.order_by(CounsellingRequest.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "student_id": r.student_id,
            "student_name": r.student.name if r.student else None,
            "request_type": r.request_type,
            "message": r.message,
            "preferred_mode": r.preferred_mode,
            "status": r.status,
            "teacher_notes": r.teacher_notes,
            "created_at": r.created_at.isoformat(),
        }
        for r in items
    ]


@router.patch("/counselling/{req_id}")
def update_counselling_request(
    req_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_teacher)
):
    """Teacher updates status and/or adds notes."""
    req = db.query(CounsellingRequest).filter(CounsellingRequest.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if "status" in payload:
        req.status = payload["status"]
    if "teacher_notes" in payload:
        req.teacher_notes = payload["teacher_notes"]
        req.teacher_id = current_user.id
    db.commit()
    return {"message": "Updated"}
