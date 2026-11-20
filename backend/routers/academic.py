import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Subject, Topic, Question, Student
from auth import get_current_user, require_teacher

router = APIRouter()


# ─────────────────────────────────────────────
# PYDANTIC SCHEMAS
# ─────────────────────────────────────────────

class TopicBase(BaseModel):
    name: str
    order_index: Optional[int] = 0
    description: Optional[str] = None


class TopicCreate(TopicBase):
    subject_id: int


class TopicUpdate(BaseModel):
    name: Optional[str] = None
    order_index: Optional[int] = None
    description: Optional[str] = None


class TopicOut(TopicBase):
    id: int
    subject_id: int
    question_count: Optional[int] = 0

    class Config:
        from_attributes = True


class SubjectBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    course: Optional[str] = Field(None, max_length=100)
    curriculum: Optional[str] = Field(None, max_length=150)
    academic_year: Optional[str] = Field(None, max_length=20)


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    course: Optional[str] = Field(None, max_length=100)
    curriculum: Optional[str] = Field(None, max_length=150)
    academic_year: Optional[str] = Field(None, max_length=20)


class SubjectOut(SubjectBase):
    id: int
    topic_count: Optional[int] = 0
    topics: List[TopicOut] = []

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# SUBJECT ENDPOINTS
# ─────────────────────────────────────────────

@router.get("/subjects", response_model=List[SubjectOut])
def list_subjects(
    course: Optional[str] = None,
    curriculum: Optional[str] = None,
    academic_year: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List all academic subjects along with their registered topics and question counts.
    """
    query = db.query(Subject)
    if course and course.strip():
        query = query.filter(func.lower(func.trim(Subject.course)) == course.strip().lower())
    if curriculum and curriculum.strip():
        query = query.filter(func.lower(func.trim(Subject.curriculum)) == curriculum.strip().lower())
    if academic_year and academic_year.strip():
        query = query.filter(
            func.lower(func.trim(Subject.academic_year)) == academic_year.strip().lower()
        )
    subjects = query.order_by(Subject.name).all()
    results = []

    for s in subjects:
        topics_out = []
        for t in s.topics:
            q_count = db.query(Question).filter(Question.topic_id == t.id).count()
            topics_out.append(TopicOut(
                id=t.id,
                subject_id=t.subject_id,
                name=t.name,
                order_index=t.order_index,
                description=t.description,
                question_count=q_count,
            ))
        results.append(SubjectOut(
            id=s.id,
            name=s.name,
            code=s.code,
            description=s.description,
            course=s.course,
            curriculum=s.curriculum,
            academic_year=s.academic_year,
            topic_count=len(topics_out),
            topics=topics_out,
        ))

    return results


@router.post("/subjects", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
def create_subject(
    req: SubjectCreate,
    current_user: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """
    Teacher Only: Create a new academic subject.
    """
    require_teacher(current_user)
    name_clean = req.name.strip()
    course = req.course.strip() if req.course and req.course.strip() else ""
    curriculum = req.curriculum.strip() if req.curriculum and req.curriculum.strip() else ""
    academic_year = req.academic_year.strip() if req.academic_year and req.academic_year.strip() else ""
    existing = db.query(Subject).filter(
        func.lower(Subject.name) == name_clean.lower(),
        func.lower(func.coalesce(Subject.course, "")) == course.lower(),
        func.lower(func.coalesce(Subject.curriculum, "")) == curriculum.lower(),
        func.lower(func.coalesce(Subject.academic_year, "")) == academic_year.lower(),
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A subject named '{name_clean}' already exists.",
        )

    new_sub = Subject(
        name=name_clean,
        code=req.code.strip() if req.code else None,
        description=req.description.strip() if req.description else None,
        course=course or None,
        curriculum=curriculum or None,
        academic_year=academic_year or None,
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)

    return SubjectOut(
        id=new_sub.id,
        name=new_sub.name,
        code=new_sub.code,
        description=new_sub.description,
        course=new_sub.course,
        curriculum=new_sub.curriculum,
        academic_year=new_sub.academic_year,
        topic_count=0,
        topics=[],
    )


@router.get("/subjects/{subject_id}", response_model=SubjectOut)
def get_subject_detail(subject_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information for a single subject with all child topics.
    """
    sub = db.query(Subject).filter(Subject.id == subject_id).first()
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {subject_id} not found.",
        )

    topics_out = []
    for t in sub.topics:
        q_count = db.query(Question).filter(Question.topic_id == t.id).count()
        topics_out.append(TopicOut(
            id=t.id,
            subject_id=t.subject_id,
            name=t.name,
            order_index=t.order_index,
            description=t.description,
            question_count=q_count,
        ))

    return SubjectOut(
        id=sub.id,
        name=sub.name,
        code=sub.code,
        description=sub.description,
        course=sub.course,
        curriculum=sub.curriculum,
        academic_year=sub.academic_year,
        topic_count=len(topics_out),
        topics=topics_out,
    )


@router.put("/subjects/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: int,
    req: SubjectUpdate,
    current_user: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """
    Teacher Only: Update subject details.
    """
    require_teacher(current_user)
    sub = db.query(Subject).filter(Subject.id == subject_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found.")

    name = req.name.strip() if req.name is not None else sub.name
    course = req.course.strip() if req.course is not None else (sub.course or "")
    curriculum = req.curriculum.strip() if req.curriculum is not None else (sub.curriculum or "")
    academic_year = req.academic_year.strip() if req.academic_year is not None else (sub.academic_year or "")
    duplicate = db.query(Subject).filter(
        Subject.id != subject_id,
        func.lower(Subject.name) == name.lower(),
        func.lower(func.coalesce(Subject.course, "")) == course.lower(),
        func.lower(func.coalesce(Subject.curriculum, "")) == curriculum.lower(),
        func.lower(func.coalesce(Subject.academic_year, "")) == academic_year.lower(),
    ).first()
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A subject named '{name}' already exists for this course scope.",
        )

    if req.name is not None:
        sub.name = name
    if req.code is not None:
        sub.code = req.code.strip()
    if req.description is not None:
        sub.description = req.description.strip()
    if req.course is not None:
        sub.course = req.course.strip() or None
    if req.curriculum is not None:
        sub.curriculum = req.curriculum.strip() or None
    if req.academic_year is not None:
        sub.academic_year = req.academic_year.strip() or None

    db.commit()
    db.refresh(sub)
    return get_subject_detail(subject_id=sub.id, db=db)


@router.delete("/subjects/{subject_id}")
def delete_subject(
    subject_id: int,
    current_user: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """
    Teacher Only: Delete an academic subject and its cascading topics.
    """
    require_teacher(current_user)
    sub = db.query(Subject).filter(Subject.id == subject_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found.")

    db.delete(sub)
    db.commit()
    return {"message": f"Subject '{sub.name}' and all associated topics deleted successfully."}


# ─────────────────────────────────────────────
# TOPIC ENDPOINTS
# ─────────────────────────────────────────────

@router.get("/subjects/{subject_id}/topics", response_model=List[TopicOut])
def list_topics_for_subject(subject_id: int, db: Session = Depends(get_db)):
    """
    List all topics for a given subject.
    """
    topics = (
        db.query(Topic)
        .filter(Topic.subject_id == subject_id)
        .order_by(Topic.order_index, Topic.id)
        .all()
    )
    results = []
    for t in topics:
        q_count = db.query(Question).filter(Question.topic_id == t.id).count()
        results.append(TopicOut(
            id=t.id,
            subject_id=t.subject_id,
            name=t.name,
            order_index=t.order_index,
            description=t.description,
            question_count=q_count,
        ))
    return results


@router.post("/topics", response_model=TopicOut, status_code=status.HTTP_201_CREATED)
def create_topic(
    req: TopicCreate,
    current_user: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """
    Teacher Only: Create a new topic under a subject.
    """
    require_teacher(current_user)
    sub = db.query(Subject).filter(Subject.id == req.subject_id).first()
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent Subject with ID {req.subject_id} not found.",
        )

    topic = Topic(
        subject_id=req.subject_id,
        name=req.name.strip(),
        order_index=req.order_index or 0,
        description=req.description.strip() if req.description else None,
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)

    return TopicOut(
        id=topic.id,
        subject_id=topic.subject_id,
        name=topic.name,
        order_index=topic.order_index,
        description=topic.description,
        question_count=0,
    )


@router.get("/topics/{topic_id}", response_model=TopicOut)
def get_topic_detail(topic_id: int, db: Session = Depends(get_db)):
    """
    Fetch topic details.
    """
    t = db.query(Topic).filter(Topic.id == topic_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Topic not found.")
    q_count = db.query(Question).filter(Question.topic_id == t.id).count()
    return TopicOut(
        id=t.id,
        subject_id=t.subject_id,
        name=t.name,
        order_index=t.order_index,
        description=t.description,
        question_count=q_count,
    )


@router.put("/topics/{topic_id}", response_model=TopicOut)
def update_topic(
    topic_id: int,
    req: TopicUpdate,
    current_user: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """
    Teacher Only: Update topic name, order index, or description.
    """
    require_teacher(current_user)
    t = db.query(Topic).filter(Topic.id == topic_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Topic not found.")

    if req.name is not None:
        t.name = req.name.strip()
    if req.order_index is not None:
        t.order_index = req.order_index
    if req.description is not None:
        t.description = req.description.strip()

    db.commit()
    db.refresh(t)
    return get_topic_detail(topic_id=t.id, db=db)


@router.delete("/topics/{topic_id}")
def delete_topic(
    topic_id: int,
    current_user: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """
    Teacher Only: Delete a topic and its associated questions.
    """
    require_teacher(current_user)
    t = db.query(Topic).filter(Topic.id == topic_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Topic not found.")

    db.delete(t)
    db.commit()
    return {"message": f"Topic '{t.name}' deleted successfully."}
