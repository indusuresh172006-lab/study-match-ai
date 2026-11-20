"""
Module 6: AI Chatbot "StudyMatch Assistant" (RAG-based)
Endpoints: chat sessions, messages, guidance document upload + embedding.

RAG pipeline:
  1. Teacher uploads guidance docs → chunked, TF-IDF vectorized, stored in DocumentEmbedding.
  2. On student chat: retrieve top-5 chunks by cosine similarity → inject into Gemini prompt.
  3. Student skill profile + weak topics are always injected as context.
  4. API key read from environment (never hardcoded).
  5. Disclaimer appended to every bot message.

Fallback: if Gemini API call fails, a helpful static response is returned.
"""
import os
import math
import datetime
import re
import logging
import requests
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user, require_teacher
from models import (
    Student, SkillProfile, ChatSession, ChatMessage,
    GuidanceDocument, DocumentEmbedding, QuestionPaper, Test,
    StudyGroup, GroupMember
)

router = APIRouter()
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
DISCLAIMER = (
    "\n\n⚠️ *Important:* Always verify exact dates, fees and eligibility on the "
    "official website before applying."
)
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


# ─────────────────────────────────────────────
# UTILITY: Chunking & TF-IDF Embedding
# ─────────────────────────────────────────────

def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += size - overlap
    return chunks or [text]


def _tfidf_vector(text: str, vocab: dict) -> List[float]:
    """Very simple bag-of-words TF vector using provided vocabulary."""
    words = text.lower().split()
    vec = [0.0] * len(vocab)
    for w in words:
        if w in vocab:
            vec[vocab[w]] += 1.0
    # L2 norm
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _cosine(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _get_vocab(db: Session) -> dict:
    """Build vocab from all stored chunk texts."""
    rows = db.query(DocumentEmbedding.chunk_text).all()
    vocab: dict = {}
    for (text,) in rows:
        for w in text.lower().split():
            if w not in vocab:
                vocab[w] = len(vocab)
    return vocab


def _embed_document(doc: GuidanceDocument, db: Session):
    """Chunk document and store TF-IDF embeddings."""
    # Delete old embeddings
    db.query(DocumentEmbedding).filter(DocumentEmbedding.document_id == doc.id).delete()

    chunks = _chunk_text(doc.content)
    vocab = _get_vocab(db)

    # Add new words to vocab
    for chunk in chunks:
        for w in chunk.lower().split():
            if w not in vocab:
                vocab[w] = len(vocab)

    for idx, chunk in enumerate(chunks):
        vec = _tfidf_vector(chunk, vocab)
        emb = DocumentEmbedding(
            document_id=doc.id,
            chunk_index=idx,
            chunk_text=chunk,
            embedding=vec,
            metadata_json={"doc_title": doc.title, "doc_type": doc.doc_type},
        )
        db.add(emb)
    db.commit()


def _retrieve_chunks(query: str, db: Session, top_k: int = 5) -> List[dict]:
    """Retrieve top-k most relevant chunks for a query."""
    vocab = _get_vocab(db)
    if not vocab:
        return []

    q_vec = _tfidf_vector(query, vocab)
    all_embeddings = db.query(DocumentEmbedding).join(GuidanceDocument).filter(
        GuidanceDocument.is_approved == True
    ).all()

    scored = []
    for emb in all_embeddings:
        stored_vec = emb.embedding
        # Pad/trim if vocab size changed
        if len(stored_vec) < len(q_vec):
            stored_vec = stored_vec + [0.0] * (len(q_vec) - len(stored_vec))
        elif len(stored_vec) > len(q_vec):
            stored_vec = stored_vec[:len(q_vec)]
        sim = _cosine(q_vec, stored_vec)
        scored.append((sim, emb))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for sim, emb in scored[:top_k]:
        if sim > 0.01:  # Relevance threshold
            results.append({
                "doc_id": emb.document_id,
                "title": (emb.metadata_json or {}).get("doc_title", "Guidance Document"),
                "snippet": emb.chunk_text[:300],
                "similarity": round(sim, 4),
            })
    return results


def _call_gemini(prompt: str, fallback_response: Optional[str] = None) -> str:
    """Call Google Gemini API using current models with intelligent fallback."""
    api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
    if not api_key:
        return fallback_response or (
            "Hello! I am your StudyMatch Assistant. AI live generation is currently "
            "running in offline guidance mode because an API key is not configured. "
            "Please explore the verified course roadmaps, exams, and scholarship modules above!"
        )

    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 1024, "temperature": 0.4},
    }

    # Sequence of models to attempt (prioritize fast, current Gemini 3.5 flash models)
    models_to_try = [
        os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        "gemini-3.8-flash",
        "gemini-3.5-flash",
    ]

    for model in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            resp = requests.post(url, json=body, headers=headers, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    return "".join(p.get("text", "") for p in parts)
            else:
                logger.warning("Chatbot request to %s returned status %s", model, resp.status_code)
        except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
            logger.warning("Chatbot request failed with %s: %s", model, exc)
            continue

    # Clean, helpful user-facing response if all live model requests encounter issues
    return fallback_response or (
        "Hello! I am here to help you navigate courses, entrance exams, and your personalized study plan. "
        "I was unable to establish a live connection to the AI generation service right now. "
        "You can check our verified guidance documents, exam guides, and mock tests in the meantime, or try asking again in a moment!"
    )


def _build_prompt(
    user_message: str,
    context_chunks: List[dict],
    skill_profile: List,
    student_name: str,
    history: List,
    resources: List[Dict[str, Any]],
    group_context: Optional[str],
) -> str:
    """Build the full RAG prompt for Gemini."""
    # Recent history (last 6 messages)
    history_text = ""
    for msg in history[-6:]:
        role = "Student" if msg.sender == "student" else "Assistant"
        history_text += f"{role}: {msg.message}\n"

    # Skill context
    weak_topics = [s.subject + "/" + s.topic for s in skill_profile if s.status == "weak"]
    strong_topics = [s.subject + "/" + s.topic for s in skill_profile if s.status == "strong"]

    skill_summary = ""
    if weak_topics:
        skill_summary += f"Weak topics: {', '.join(weak_topics[:8])}\n"
    if strong_topics:
        skill_summary += f"Strong topics: {', '.join(strong_topics[:5])}\n"

    # Retrieved content
    retrieved_text = ""
    if context_chunks:
        retrieved_text = "\n\n---RETRIEVED GUIDANCE CONTENT---\n"
        for chunk in context_chunks:
            retrieved_text += f"[{chunk['title']}]: {chunk['snippet']}\n\n"
    else:
        retrieved_text = "\n(No specific guidance documents found for this query — answer from general knowledge.)\n"

    resources_text = "\n".join(
        f"- {item['kind']}: {item['title']} ({item['subject']}, {item.get('year') or item.get('exam_name') or 'available'}); "
        f"topics: {', '.join(item.get('topic_tags', [])) or 'not tagged'}; link: {item['link']}"
        for item in resources
    ) or "No matching approved tests or papers were found."

    prompt = f"""You are StudyMatch Assistant, a friendly and knowledgeable academic mentor for Indian students.
You help students with higher education guidance, course/exam queries, study tips, and understanding their own skill profile.

STUDENT: {student_name}
SKILL PROFILE:
{skill_summary or 'No skill data yet.'}

{retrieved_text}

ACTIVE STUDY GROUP:
{group_context or 'No active study group assigned.'}

APPROVED STUDY RESOURCES:
{resources_text}

CONVERSATION HISTORY:
{history_text}

Student's question: {user_message}

Instructions:
- Answer helpfully and concisely (3-6 sentences usually).
- If the retrieved content is relevant, use it and cite the document title.
- If nothing relevant was found, say so and answer from general knowledge.
- If asked about weak topics, give specific, actionable study advice.
- If asked to find question papers or mock tests, recommend only matching resources from the approved list above.
- Never fabricate specific dates, fees or college rankings — advise verification.
- Respond in the same language as the student's question.
"""
    return prompt


def _find_study_resources(user_message: str, db: Session) -> List[Dict[str, Any]]:
    query = user_message.casefold()
    if not any(term in query for term in ("paper", "question", "mock test", "practice test", "test")):
        return []

    terms = {
        term for term in re.findall(r"[a-z0-9]+", query)
        if len(term) > 2 and not term.isdigit() and term not in {
            "paper", "papers", "question", "questions", "mock", "test", "tests",
            "last", "year", "years", "give", "find", "show", "for", "the",
            "one", "two", "three", "four", "five", "exam", "exams", "previous",
            "past", "practice", "from", "available", "are", "can", "me",
        }
    }
    year_span_match = re.search(r"last\s+(\d+|one|two|three|four|five)\s+years?", query)
    year_words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    year_span = (
        int(year_span_match.group(1))
        if year_span_match and year_span_match.group(1).isdigit()
        else year_words.get(year_span_match.group(1), 0) if year_span_match else 0
    )
    requested_years = {
        int(year) for year in re.findall(r"\b(?:19|20)\d{2}\b", query)
    }
    min_year = datetime.date.today().year - year_span + 1 if year_span else None
    resources = []

    papers = db.query(QuestionPaper).filter(
        QuestionPaper.approval_status == "approved",
    ).order_by(QuestionPaper.year.desc()).limit(50).all()
    for paper in papers:
        topic_tags = paper.topic_tags if isinstance(paper.topic_tags, list) else []
        haystack = " ".join([paper.title, paper.subject, paper.exam_name, *topic_tags]).casefold()
        matches = sum(term in haystack for term in terms)
        if (terms and not matches) or (min_year and paper.year < min_year):
            continue
        if requested_years and paper.year not in requested_years:
            continue
        resources.append({
            "kind": "Question paper",
            "title": paper.title,
            "subject": paper.subject,
            "exam_name": paper.exam_name,
            "year": paper.year,
            "topic_tags": topic_tags,
            "link": "/papers",
            "match_score": matches,
        })

    tests = db.query(Test).filter(
        Test.is_published.is_(True),
        Test.approval_status == "approved",
    ).order_by(Test.created_at.desc()).limit(50).all()
    for test in tests:
        if requested_years:
            continue
        haystack = " ".join((test.title, test.subject, test.exam_name or "")).casefold()
        matches = sum(term in haystack for term in terms)
        if terms and not matches:
            continue
        resources.append({
            "kind": "Mock test",
            "title": test.title,
            "subject": test.subject,
            "exam_name": test.exam_name,
            "topic_tags": [],
            "link": "/mock-tests",
            "match_score": matches,
        })

    resources.sort(
        key=lambda item: (item["match_score"], item.get("year") or 0),
        reverse=True,
    )
    return resources[:8]


def _get_active_group_context(student_id: int, db: Session) -> Optional[str]:
    membership = db.query(GroupMember).join(StudyGroup).filter(
        GroupMember.student_id == student_id,
        StudyGroup.status == "active",
    ).first()
    if not membership:
        return None

    group = membership.group
    classmates = sum(
        1 for member in group.members
        if member.student_id != student_id
    )
    pairs = [
        f"you are {'tutoring' if pair.tutor_id == student_id else 'learning'} "
        f"{pair.topic.name if pair.topic else 'a topic'}"
        for pair in group.teaching_pairs
        if student_id in (pair.tutor_id, pair.learner_id)
    ]
    return (
        f"Active study group; {classmates} other group member(s); "
        f"your peer-teaching matches: {', '.join(pairs) or 'none'}"
    )


def _offline_chat_response(resources: List[Dict[str, Any]], group_context: Optional[str]) -> str:
    if resources:
        lines = [
            f"- {item['kind']}: {item['title']} — {item['subject']}"
            + (f", {item['year']}" if item.get("year") else "")
            + f" ({item['link']})"
            for item in resources
        ]
        return "Here are approved study resources matching your request:\n" + "\n".join(lines)
    if group_context:
        return f"Your active study group details: {group_context}. You can ask me to explain one of your weak topics or prepare for a group session."
    return (
        "Hello! I am here to help you navigate courses, entrance exams, and your personalized study plan. "
        "Live AI generation is unavailable right now; please use the verified guidance and study resources in the app."
    )


# ─────────────────────────────────────────────
# GUIDANCE DOCUMENT MANAGEMENT (Teacher)
# ─────────────────────────────────────────────

@router.post("/documents", status_code=status.HTTP_201_CREATED)
def upload_document(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_teacher)
):
    """
    Teacher uploads a guidance document for RAG.
    payload: { title, doc_type, content }
    """
    doc = GuidanceDocument(
        title=payload.get("title", "Guidance Document"),
        doc_type=payload.get("doc_type", "general"),
        content=payload.get("content", ""),
        file_path=payload.get("file_path"),
        uploaded_by=current_user.id,
        is_approved=False,
    )
    db.add(doc)
    db.flush()
    # Build embeddings immediately
    _embed_document(doc, db)
    db.refresh(doc)
    return {
        "id": doc.id,
        "message": "Document uploaded and indexed for chatbot retrieval",
        "chunks_created": db.query(DocumentEmbedding)
            .filter(DocumentEmbedding.document_id == doc.id).count(),
    }


@router.get("/documents")
def list_documents(
    doc_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    q = db.query(GuidanceDocument)
    if current_user.role == "student":
        q = q.filter(GuidanceDocument.is_approved == True)
    if doc_type:
        q = q.filter(GuidanceDocument.doc_type == doc_type)
    total = q.count()
    docs = q.order_by(GuidanceDocument.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [
            {
                "id": d.id,
                "title": d.title,
                "doc_type": d.doc_type,
                "is_approved": d.is_approved,
                "created_at": d.created_at.isoformat(),
            }
            for d in docs
        ],
    }


@router.patch("/documents/{doc_id}/approve")
def approve_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_teacher)
):
    doc = db.query(GuidanceDocument).filter(GuidanceDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.is_approved = True
    db.commit()
    return {"message": "Document approved for chatbot use"}


# ─────────────────────────────────────────────
# CHAT SESSIONS
# ─────────────────────────────────────────────

@router.post("/sessions", status_code=status.HTTP_201_CREATED)
def create_session(
    payload: dict = None,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    if payload is None:
        payload = {}
    session = ChatSession(
        student_id=current_user.id,
        title=payload.get("title", "Study Discussion"),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "session_id": session.id,
        "title": session.title,
        "created_at": session.created_at.isoformat(),
    }


@router.get("/sessions")
def list_sessions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.student_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "session_id": s.id,
            "title": s.title,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
            "message_count": len(s.messages),
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}/messages")
def get_messages(
    session_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.student_id == current_user.id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": m.id,
            "sender": m.sender,
            "message": m.message,
            "sources": m.sources,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]


@router.post("/sessions/{session_id}/message")
def send_message(
    session_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """
    Send a student message and get an AI response.
    payload: { message: str }
    """
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.student_id == current_user.id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    user_text = payload.get("message", "").strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Save student message
    student_msg = ChatMessage(
        session_id=session_id,
        sender="student",
        message=user_text,
    )
    db.add(student_msg)
    db.flush()

    # Get student's skill profile
    skills = db.query(SkillProfile).filter(
        SkillProfile.student_id == current_user.id
    ).all()

    # Get session history
    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )

    # RAG: retrieve relevant chunks
    context_chunks = _retrieve_chunks(user_text, db, top_k=5)
    resources = _find_study_resources(user_text, db)
    group_context = _get_active_group_context(current_user.id, db)

    # Build prompt and call Gemini
    prompt = _build_prompt(
        user_message=user_text,
        context_chunks=context_chunks,
        skill_profile=skills,
        student_name=current_user.name,
        history=history[:-1],  # Exclude the message we just added
        resources=resources,
        group_context=group_context,
    )
    ai_response = _call_gemini(
        prompt,
        fallback_response=_offline_chat_response(resources, group_context),
    )
    full_response = ai_response + DISCLAIMER

    source_entries = (context_chunks[:3] if context_chunks else []) + [
        {
            "title": f"{resource['kind']}: {resource['title']}",
            "link": resource["link"],
        }
        for resource in resources
    ]
    # Save bot message
    bot_msg = ChatMessage(
        session_id=session_id,
        sender="bot",
        message=full_response,
        context_data={
            "weak_topics": [s.topic for s in skills if s.status == "weak"][:5],
            "group_context": group_context,
        },
        sources=source_entries or None,
    )
    db.add(bot_msg)

    # Update session title if it's the first message
    if len(history) <= 1:
        session.title = user_text[:60] + ("..." if len(user_text) > 60 else "")
    session.updated_at = datetime.datetime.utcnow()
    db.commit()

    return {
        "session_id": session_id,
        "student_message_id": student_msg.id,
        "bot_response": full_response,
        "sources": source_entries,
        "recommended_resources": resources,
        "suggested_questions": _suggest_questions(skills, user_text),
    }


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.student_id == current_user.id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()


def _suggest_questions(skills: List, last_message: str) -> List[str]:
    """Return context-aware suggested follow-up questions."""
    weak = [s.subject + " - " + s.topic for s in skills if s.status == "weak"]
    suggestions = []
    if weak:
        suggestions.append(f"How can I improve my weak topic: {weak[0]}?")
        if len(weak) > 1:
            suggestions.append(f"What resources are available for {weak[1]}?")
    suggestions += [
        "What entrance exams should I prepare for?",
        "Which courses match my skill profile?",
        "How do I apply for scholarships?",
        "Show me my study plan for this week.",
    ]
    return suggestions[:4]
