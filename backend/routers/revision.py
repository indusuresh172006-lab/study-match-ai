import os
import json
import datetime
import logging
import requests
from typing import List, Optional, Dict, Any, Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Student, RevisionNote
from auth import get_current_user, require_teacher

router = APIRouter()
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


class RevisionNotesRequest(BaseModel):
    topic_name: str = Field(..., min_length=1, max_length=100)
    subject_name: str = Field(default="General", min_length=1, max_length=100)


class RevisionReviewRequest(BaseModel):
    decision: Literal["approve", "reject"]


class PracticeQuestionItem(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str


class RevisionNotesResponse(BaseModel):
    id: int
    topic_name: str
    subject_name: str
    status: str
    overview: Optional[str] = None
    key_concepts: List[str] = []
    practical_example: Optional[str] = None
    teaching_outline: Optional[str] = None
    common_pitfalls: List[str] = []
    practice_questions: List[Dict[str, Any]] = []
    message: Optional[str] = None
    created_at: str


def _generate_ai_revision_content(topic_name: str, subject_name: str) -> Dict[str, Any]:
    """Call Gemini to generate structured revision notes for a weak topic."""
    prompt = f"""You are an expert tutor creating targeted revision notes for a student who is struggling with:
Subject: {subject_name}
Topic: {topic_name}

Generate a concise, pedagogical revision note in valid JSON format with these exact keys:
{{
  "overview": "A clear, simple 2-3 sentence explanation of the topic without confusing jargon.",
  "key_concepts": [
    "Core concept 1 with key formula or principle",
    "Core concept 2",
    "Core concept 3"
  ],
  "practical_example": "A clear step-by-step example with code or calculation showing how to solve a problem in this topic.",
  "teaching_outline": "A short, simple explanation outline for a student teaching this topic to a classmate.",
  "common_pitfalls": [
    "Common mistake students make and how to avoid it",
    "Second common misconception"
  ],
  "practice_questions": [
    {{
      "question": "Practice question 1?",
      "options": ["A) option 1", "B) option 2", "C) option 3", "D) option 4"],
      "correct_answer": "B",
      "explanation": "Why B is correct."
    }},
    {{
      "question": "Practice question 2?",
      "options": ["A) opt 1", "B) opt 2", "C) opt 3", "D) opt 4"],
      "correct_answer": "A",
      "explanation": "Explanation here."
    }}
  ]
}}

Return ONLY valid JSON. Do not wrap in markdown quotes if possible."""

    api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
    if not api_key:
        return _fallback_revision(topic_name, subject_name)

    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1500,
            "responseMimeType": "application/json"
        }
    }

    models_to_try = [
        DEFAULT_GEMINI_MODEL,
        "gemini-3.8-flash",
        "gemini-3.5-flash",
    ]

    for model in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            res = requests.post(url, json=body, headers=headers, timeout=12)
            if res.status_code == 200:
                raw_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                # Parse JSON
                clean_json = raw_text.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.startswith("```"):
                    clean_json = clean_json[3:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                parsed = json.loads(clean_json.strip())
                return parsed
        except (
            requests.RequestException,
            KeyError,
            IndexError,
            TypeError,
            json.JSONDecodeError,
        ) as exc:
            logger.warning("Revision note generation failed with %s: %s", model, exc)
            continue

    return _fallback_revision(topic_name, subject_name)


def _fallback_revision(topic_name: str, subject_name: str) -> Dict[str, Any]:
    return {
        "overview": f"{topic_name} is a fundamental concept in {subject_name}. Mastering it enables a solid foundation for advanced problem solving.",
        "key_concepts": [
            f"Understand the core definitions and axioms governing {topic_name}.",
            "Break down multi-step problems into modular components.",
            "Verify edge cases and constraints before arriving at final answers."
        ],
        "practical_example": f"Review standard textbook exercises for {topic_name}. Practice step-by-step substitution and verify with known solutions.",
        "teaching_outline": (
            f"Start by defining {topic_name}, explain one core rule, work through a simple example, "
            "then ask your classmate to solve a similar question aloud."
        ),
        "common_pitfalls": [
            "Skipping foundational prerequisite concepts before tackling advanced formulas.",
            "Rushing through boundary condition checks."
        ],
        "practice_questions": [
            {
                "question": f"Which approach best characterizes problem-solving in {topic_name}?",
                "options": ["A) Guess and check", "B) Systematic step-by-step derivation", "C) Ignoring edge cases", "D) Memorizing answers without proofs"],
                "correct_answer": "B",
                "explanation": "Systematic step-by-step derivation ensures correctness across all test cases."
            }
        ]
    }


@router.post("/revision/generate", response_model=RevisionNotesResponse)
def generate_revision_notes(
    req: RevisionNotesRequest,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Module 10: AI Revision Notes Generator.
    Produces simple explanations, important concepts, examples, and practice questions for a weak topic.
    """
    topic_name = req.topic_name.strip()
    subject_name = req.subject_name.strip()
    existing = db.query(RevisionNote).filter(
        RevisionNote.student_id == current_user.id,
        func.lower(RevisionNote.topic_name) == topic_name.lower(),
        func.lower(RevisionNote.subject_name) == subject_name.lower(),
        RevisionNote.status.in_(["pending", "approved"]),
    ).order_by(RevisionNote.created_at.desc()).first()
    if existing:
        return _revision_response(existing)

    content = _generate_ai_revision_content(topic_name, subject_name)
    note = RevisionNote(
        student_id=current_user.id,
        subject_name=subject_name,
        topic_name=topic_name,
        content=content,
        status="pending",
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return _revision_response(note)


def _revision_response(note: RevisionNote) -> RevisionNotesResponse:
    content = note.content if note.status == "approved" else {}
    return RevisionNotesResponse(
        id=note.id,
        topic_name=note.topic_name,
        subject_name=note.subject_name,
        status=note.status,
        overview=content.get("overview"),
        key_concepts=content.get("key_concepts", []),
        practical_example=content.get("practical_example"),
        teaching_outline=content.get("teaching_outline"),
        common_pitfalls=content.get("common_pitfalls", []),
        practice_questions=content.get("practice_questions", []),
        message=(
            "Your revision notes are awaiting teacher review."
            if note.status == "pending"
            else None
        ),
        created_at=note.created_at.isoformat(),
    )


@router.get("/revision/mine", response_model=List[RevisionNotesResponse])
def list_my_revision_notes(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notes = db.query(RevisionNote).filter(
        RevisionNote.student_id == current_user.id,
    ).order_by(RevisionNote.created_at.desc()).limit(50).all()
    return [_revision_response(note) for note in notes]


@router.get("/revision/review-queue")
def list_revision_review_queue(
    current_teacher: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    notes = db.query(RevisionNote).filter(
        RevisionNote.status == "pending",
    ).order_by(RevisionNote.created_at.asc()).limit(100).all()
    return [
        {
            "id": note.id,
            "student_id": note.student_id,
            "student_name": note.student.name if note.student else "Student",
            "topic_name": note.topic_name,
            "subject_name": note.subject_name,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
        }
        for note in notes
    ]


@router.patch("/revision/{note_id}/review")
def review_revision_note(
    note_id: int,
    payload: RevisionReviewRequest,
    current_teacher: Student = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    note = db.query(RevisionNote).filter(RevisionNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Revision note not found.")
    if note.status != "pending":
        raise HTTPException(status_code=409, detail="Only pending revision notes can be reviewed.")

    note.status = "approved" if payload.decision == "approve" else "rejected"
    note.reviewed_by = current_teacher.id
    note.reviewed_at = datetime.datetime.utcnow()
    db.commit()
    return {"id": note.id, "status": note.status}
