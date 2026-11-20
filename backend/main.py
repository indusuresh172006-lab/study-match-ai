import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc

from database import engine, Base, get_db
from models import (
    Student, StudentProfile, SkillProfile, StudyMaterial, MaterialBookmark,
    QuestionBank, MockTest, MockTestResponse, PreviousPaper, PaperQuestion,
    PaperAttempt, GuidanceCourse, InterestProfile, CourseSummary, MentorChatMessage,
    StudyClass, ClassEnrollment
)
from schemas import (
    StudentRegister, StudentLogin, StudentResponse, TokenResponse,
    ProfileCreate, ProfileResponse,
    SkillProfileItem, SkillSummaryResponse,
    StudyMaterialCreate, StudyMaterialUpdate, StudyMaterialResponse, StudyMaterialListResponse, BookmarkToggleResponse,
    QuestionnaireSubmit, QuestionnaireResponse, GuidanceCourseResponse,
    MentorChatRequest, MentorChatResponse, MentorHistoryResponse, MentorMessageItem,
    MockTestCreate, MockTestStartResponse, MockTestQuestionOut, MockTestSubmit, MockTestResultResponse,
    QuestionReviewItem, MockTestHistoryItem,
    CourseSummaryResponse, CourseSummaryUpdate, QuickQuizSubmit, QuickQuizResult, QuizQuestionItem,
    PaperListItem, PaperDetailResponse, PaperQuestionOut, PaperAttemptSubmit, PaperAttemptResult, RemediationItem,
    TeacherDashboardStats, ClassWeakTopicItem, AtRiskStudentItem
)
from auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, require_student, require_teacher
)
from ai_mentor import get_mentor_response

# Core & Module routers
from routers import auth, academic, quiz, groups, revision, guidance, mock_tests_v2, chatbot, classes

# Initialize database schema if not present
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyMatch AI API",
    description="Intelligent peer-learning, adaptive mock tests, course guidance and AI mentoring platform",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows Vite dev server & production client
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all modular routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Module 1 - Authentication"])
app.include_router(classes.router, prefix="/api/v1", tags=["Classes & Marks"])
app.include_router(academic.router, prefix="/api/v1", tags=["Module 3 - Subject & Topic Management"])
app.include_router(quiz.router, prefix="/api/v1", tags=["Module 4 & 5 - Diagnostic Quiz & ML Prediction"])
app.include_router(groups.router, prefix="/api/v1", tags=["Module 7, 8 & 9 - Intelligent Study Groups & Schedules"])
app.include_router(revision.router, prefix="/api/v1", tags=["Module 10 - AI Revision Notes"])
app.include_router(guidance.router, prefix="/api/v1/guidance", tags=["Module 4 - Higher Studies Guidance"])
app.include_router(mock_tests_v2.router, prefix="/api/v1", tags=["Module 5 - Tests & Papers"])
app.include_router(chatbot.router, prefix="/api/v1/chat", tags=["Module 6 - AI Chatbot"])


# =====================================================================
# 1. AUTHENTICATION & USER PROFILE
# =====================================================================

@app.get("/")
def home():
    return {
        "app": "StudyMatch AI",
        "status": "online",
        "version": "2.0.0",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }


@app.post("/register", response_model=StudentResponse)
def register_student(payload: StudentRegister, db: Session = Depends(get_db)):
    study_class = None
    if payload.class_code and payload.class_code.strip():
        study_class = db.query(StudyClass).filter(
            StudyClass.join_code == payload.class_code.strip().upper(),
            StudyClass.is_active.is_(True),
        ).first()
        if not study_class:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Class code is invalid or inactive.",
            )

    existing = db.query(Student).filter(Student.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    user_role = "student"
    new_user = Student(
        name=payload.name,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role=user_role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Initialize default skill profiles if role is student
    if user_role == "student":
        db.add(StudentProfile(
            student_id=new_user.id,
            course=study_class.course if study_class else (payload.course or "General"),
            college=study_class.curriculum if study_class else payload.college,
            semester=study_class.academic_year if study_class else payload.semester,
        ))
        if study_class:
            db.add(ClassEnrollment(class_id=study_class.id, student_id=new_user.id))
        default_topics = [
            ("Biology", "Genetics & DNA"),
            ("Biology", "Cell Biology"),
            ("Biology", "Ecology & Evolution"),
            ("Mathematics", "Calculus & Limits"),
            ("Mathematics", "Linear Algebra & Matrices"),
            ("Mathematics", "Probability & Statistics"),
            ("Computer Science", "Operating Systems"),
            ("Computer Science", "Database Management (SQL)"),
            ("Computer Science", "Data Structures & Algorithms"),
        ]
        for subj, top in default_topics:
            db.add(SkillProfile(
                student_id=new_user.id,
                subject=subj,
                topic=top,
                status="average",
                mastery_score=50.0,
                tests_taken=0
            ))
        db.commit()

    return new_user


@app.post("/login", response_model=TokenResponse)
def login_student(payload: StudentLogin, db: Session = Depends(get_db)):
    user = db.query(Student).filter(Student.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        student_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role
    )


@app.get("/auth/me", response_model=StudentResponse)
def get_me(current_user: Student = Depends(get_current_user)):
    return current_user


@app.post("/profile", response_model=ProfileResponse)
def create_or_update_profile(
    profile: ProfileCreate,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_profile = db.query(StudentProfile).filter(StudentProfile.student_id == current_user.id).first()
    if existing_profile:
        existing_profile.course = profile.course
        existing_profile.stream = profile.stream
        existing_profile.academic_level = profile.academic_level
        existing_profile.learning_goal = profile.learning_goal
        if profile.college is not None:
            existing_profile.college = profile.college
        if profile.semester is not None:
            existing_profile.semester = profile.semester
        db.commit()
        db.refresh(existing_profile)
        return existing_profile

    new_profile = StudentProfile(
        student_id=current_user.id,
        course=profile.course,
        stream=profile.stream,
        academic_level=profile.academic_level,
        learning_goal=profile.learning_goal,
        college=profile.college,
        semester=profile.semester,
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


@app.get("/profile/me", response_model=Optional[ProfileResponse])
def get_my_profile(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.student_id == current_user.id).first()
    return profile


# =====================================================================
# 2. SKILL PROFILE & STUDENT DASHBOARD
# =====================================================================

@app.get("/skill-profile", response_model=List[SkillProfileItem])
def get_student_skills(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    skills = db.query(SkillProfile).filter(SkillProfile.student_id == current_user.id).all()
    return skills


@app.get("/skill-profile/summary", response_model=SkillSummaryResponse)
def get_skill_summary(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    skills = db.query(SkillProfile).filter(SkillProfile.student_id == current_user.id).all()
    if not skills:
        return SkillSummaryResponse(
            total_topics=0,
            weak_count=0,
            average_count=0,
            strong_count=0,
            average_mastery=0.0,
            weak_topics=[],
            strong_topics=[],
            subject_breakdown={}
        )

    weak_topics = [s.topic for s in skills if s.status == "weak"]
    strong_topics = [s.topic for s in skills if s.status == "strong"]
    average_count = sum(1 for s in skills if s.status == "average")
    avg_mastery = sum(s.mastery_score for s in skills) / len(skills)

    # Subject breakdown
    subject_map: Dict[str, Dict[str, Any]] = {}
    for s in skills:
        if s.subject not in subject_map:
            subject_map[s.subject] = {"total": 0, "weak": 0, "average": 0, "strong": 0, "scores": []}
        subject_map[s.subject]["total"] += 1
        subject_map[s.subject][s.status] += 1
        subject_map[s.subject]["scores"].append(s.mastery_score)

    for subj, data in subject_map.items():
        data["average_score"] = round(sum(data["scores"]) / len(data["scores"]), 1)
        del data["scores"]

    return SkillSummaryResponse(
        total_topics=len(skills),
        weak_count=len(weak_topics),
        average_count=average_count,
        strong_count=len(strong_topics),
        average_mastery=round(avg_mastery, 1),
        weak_topics=weak_topics,
        strong_topics=strong_topics,
        subject_breakdown=subject_map
    )


# =====================================================================
# 3. FEATURE 1: STUDY MATERIALS
# =====================================================================

def _scope_materials_to_student(query, current_user: Student, db: Session):
    if current_user.role != "student":
        return query

    profile = db.query(StudentProfile).filter(
        StudentProfile.student_id == current_user.id
    ).first()
    if not profile:
        return query.filter(StudyMaterial.id == -1)

    course = (profile.course or "").strip().lower()
    curriculum = (profile.college or "").strip().lower()
    academic_year = (profile.semester or "").strip().lower()
    if not course or not curriculum or not academic_year:
        return query.filter(StudyMaterial.id == -1)

    return query.filter(
        func.lower(func.trim(StudyMaterial.course)) == course,
        func.lower(func.trim(StudyMaterial.curriculum)) == curriculum,
        func.lower(func.trim(StudyMaterial.academic_year)) == academic_year,
    )


@app.get("/materials", response_model=StudyMaterialListResponse)
def list_study_materials(
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    material_type: Optional[str] = None,
    search: Optional[str] = None,
    bookmarked_only: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(9, ge=1, le=50),
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = _scope_materials_to_student(db.query(StudyMaterial), current_user, db)

    if subject and subject != "All":
        query = query.filter(StudyMaterial.subject == subject)
    if topic and topic != "All":
        query = query.filter(StudyMaterial.topic == topic)
    if material_type and material_type != "All":
        query = query.filter(StudyMaterial.material_type == material_type)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                StudyMaterial.title.ilike(search_filter),
                StudyMaterial.summary.ilike(search_filter),
                StudyMaterial.topic.ilike(search_filter)
            )
        )

    # Get bookmarks for current user
    user_bookmarks = set(
        b.material_id for b in db.query(MaterialBookmark).filter(
            MaterialBookmark.student_id == current_user.id
        ).all()
    )

    if bookmarked_only:
        query = query.filter(StudyMaterial.id.in_(user_bookmarks))

    # Retrieve student's weak topics to prioritize them!
    student_weak_topics = set(
        s.topic for s in db.query(SkillProfile).filter(
            SkillProfile.student_id == current_user.id,
            SkillProfile.status == "weak"
        ).all()
    )

    all_materials = query.all()

    # Prioritize weak topic materials to top of the list
    sorted_materials = sorted(
        all_materials,
        key=lambda m: (
            0 if m.topic in student_weak_topics else 1, # 0 goes first
            0 if m.id in user_bookmarks else 1,
            -m.id
        )
    )

    total = len(sorted_materials)
    pages = max(1, (total + limit - 1) // limit)
    offset = (page - 1) * limit
    paginated_items = sorted_materials[offset:offset + limit]

    response_items = []
    for m in paginated_items:
        resp = StudyMaterialResponse.model_validate(m)
        resp.is_bookmarked = m.id in user_bookmarks
        resp.is_weak_topic = m.topic in student_weak_topics
        response_items.append(resp)

    return StudyMaterialListResponse(
        items=response_items,
        total=total,
        page=page,
        pages=pages
    )


@app.get("/materials/subjects", response_model=List[str])
def list_study_material_subjects(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = _scope_materials_to_student(db.query(StudyMaterial.subject), current_user, db)
    return [subject for (subject,) in query.distinct().order_by(StudyMaterial.subject).all()]


@app.get("/materials/{material_id}", response_model=StudyMaterialResponse)
def get_study_material(
    material_id: int,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    material = _scope_materials_to_student(
        db.query(StudyMaterial), current_user, db
    ).filter(StudyMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Study material not found")

    is_bookmarked = db.query(MaterialBookmark).filter(
        MaterialBookmark.student_id == current_user.id,
        MaterialBookmark.material_id == material.id
    ).first() is not None

    is_weak = db.query(SkillProfile).filter(
        SkillProfile.student_id == current_user.id,
        SkillProfile.topic == material.topic,
        SkillProfile.status == "weak"
    ).first() is not None

    resp = StudyMaterialResponse.model_validate(material)
    resp.is_bookmarked = is_bookmarked
    resp.is_weak_topic = is_weak
    return resp


@app.post("/materials", response_model=StudyMaterialResponse)
def create_study_material(
    payload: StudyMaterialCreate,
    current_teacher: Student = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    new_material = StudyMaterial(
        title=payload.title,
        subject=payload.subject,
        topic=payload.topic,
        course=payload.course.strip() if payload.course and payload.course.strip() else None,
        curriculum=payload.curriculum.strip() if payload.curriculum and payload.curriculum.strip() else None,
        academic_year=payload.academic_year.strip() if payload.academic_year and payload.academic_year.strip() else None,
        material_type=payload.material_type,
        content=payload.content,
        summary=payload.summary,
        difficulty_level=payload.difficulty_level or "medium",
        uploaded_by=current_teacher.id
    )
    db.add(new_material)
    db.commit()
    db.refresh(new_material)
    resp = StudyMaterialResponse.model_validate(new_material)
    resp.is_bookmarked = False
    resp.is_weak_topic = False
    return resp


@app.put("/materials/{material_id}", response_model=StudyMaterialResponse)
def update_study_material(
    material_id: int,
    payload: StudyMaterialUpdate,
    current_teacher: Student = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    material = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Study material not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(material, key, value)

    db.commit()
    db.refresh(material)
    resp = StudyMaterialResponse.model_validate(material)
    resp.is_bookmarked = False
    resp.is_weak_topic = False
    return resp


@app.delete("/materials/{material_id}")
def delete_study_material(
    material_id: int,
    current_teacher: Student = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    material = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Study material not found")

    db.delete(material)
    db.commit()
    return {"message": "Study material deleted successfully"}


@app.post("/materials/{material_id}/bookmark", response_model=BookmarkToggleResponse)
def toggle_bookmark(
    material_id: int,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    material = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Study material not found")

    existing_bm = db.query(MaterialBookmark).filter(
        MaterialBookmark.student_id == current_user.id,
        MaterialBookmark.material_id == material_id
    ).first()

    if existing_bm:
        db.delete(existing_bm)
        db.commit()
        return BookmarkToggleResponse(
            material_id=material_id,
            bookmarked=False,
            message="Bookmark removed"
        )
    else:
        new_bm = MaterialBookmark(student_id=current_user.id, material_id=material_id)
        db.add(new_bm)
        db.commit()
        return BookmarkToggleResponse(
            material_id=material_id,
            bookmarked=True,
            message="Material saved to bookmarks"
        )


# =====================================================================
# 4. FEATURE 2: FUTURE COURSE GUIDANCE
# =====================================================================

@app.post("/guidance/questionnaire", response_model=QuestionnaireResponse)
def submit_questionnaire(
    payload: QuestionnaireSubmit,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interest_tags = [
        payload.preferred_work_style.lower(),
        payload.favorite_subject.lower(),
        payload.career_interest.lower(),
        payload.higher_study_goal.lower()
    ]

    # Store or update in database
    existing_profile = db.query(InterestProfile).filter(InterestProfile.student_id == current_user.id).first()
    if existing_profile:
        existing_profile.answers = payload.model_dump()
        existing_profile.interest_tags = interest_tags
    else:
        new_ip = InterestProfile(
            student_id=current_user.id,
            answers=payload.model_dump(),
            interest_tags=interest_tags
        )
        db.add(new_ip)
    db.commit()

    # Calculate ranked course recommendations
    recommended_courses = compute_course_recommendations(current_user.id, interest_tags, db)

    return QuestionnaireResponse(
        message="Interest profile saved and career guidance computed!",
        interest_tags=interest_tags,
        recommended_courses=recommended_courses
    )


@app.get("/guidance/courses", response_model=List[GuidanceCourseResponse])
def get_guidance_courses(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip = db.query(InterestProfile).filter(InterestProfile.student_id == current_user.id).first()
    tags = ip.interest_tags if ip else []
    return compute_course_recommendations(current_user.id, tags, db)


@app.get("/guidance/courses/{course_id}", response_model=GuidanceCourseResponse)
def get_course_detail(
    course_id: int,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(GuidanceCourse).filter(GuidanceCourse.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course guidance record not found")

    ip = db.query(InterestProfile).filter(InterestProfile.student_id == current_user.id).first()
    tags = ip.interest_tags if ip else []
    recommendations = compute_course_recommendations(current_user.id, tags, db)
    for r in recommendations:
        if r.id == course_id:
            return r

    return GuidanceCourseResponse(
        id=course.id,
        title=course.title,
        stream=course.stream,
        degree_level=course.degree_level,
        description=course.description,
        eligibility=course.eligibility,
        fees_range=course.fees_range,
        scope_and_careers=course.scope_and_careers,
        entrance_exams=course.entrance_exams,
        roadmap_steps=course.roadmap_steps,
        match_percentage=75,
        recommended_reason="Aligned with standard STEM higher-study prerequisites."
    )


def compute_course_recommendations(
    student_id: int,
    interest_tags: List[str],
    db: Session
) -> List[GuidanceCourseResponse]:
    courses = db.query(GuidanceCourse).all()
    skills = db.query(SkillProfile).filter(SkillProfile.student_id == student_id).all()

    # Map student subjects/topics to strengths
    strong_topics = set(s.topic.lower() for s in skills if s.status == "strong")
    weak_topics = set(s.topic.lower() for s in skills if s.status == "weak")
    subject_avg = {}
    for s in skills:
        subject_avg.setdefault(s.subject.lower(), []).append(s.mastery_score)
    subject_scores = {k: sum(v)/len(v) for k, v in subject_avg.items()}

    results = []
    for c in courses:
        score = 60 # Base baseline match

        # 1. Questionnaire interest tag overlap
        c_tags = [t.lower() for t in c.matching_tags]
        matches = sum(1 for tag in interest_tags if any(tag in ct or ct in tag for ct in c_tags))
        score += matches * 10

        # 2. Subject strength alignment
        c_title_stream = (c.title + " " + c.stream).lower()
        if "computer" in c_title_stream or "ai" in c_title_stream:
            cs_score = subject_scores.get("computer science", 50)
            score += int((cs_score - 50) * 0.3)
        elif "bio" in c_title_stream or "medical" in c_title_stream or "mbbs" in c_title_stream:
            bio_score = subject_scores.get("biology", 50)
            score += int((bio_score - 50) * 0.3)
        elif "math" in c_title_stream or "data" in c_title_stream:
            math_score = subject_scores.get("mathematics", 50)
            score += int((math_score - 50) * 0.3)

        # Cap between 55% and 98%
        match_pct = max(55, min(98, score))

        reasons = []
        if matches > 0:
            reasons.append("Strongly aligns with your stated career interests")
        if any(st in " ".join(c_tags) for st in strong_topics):
            reasons.append("Leverages your proven strengths in your skill profile")
        if not reasons:
            reasons.append("High-demand STEM career path matching your academic background")

        results.append(
            GuidanceCourseResponse(
                id=c.id,
                title=c.title,
                stream=c.stream,
                degree_level=c.degree_level,
                description=c.description,
                eligibility=c.eligibility,
                fees_range=c.fees_range,
                scope_and_careers=c.scope_and_careers,
                entrance_exams=c.entrance_exams,
                roadmap_steps=c.roadmap_steps,
                match_percentage=match_pct,
                recommended_reason="; ".join(reasons) + "."
            )
        )

    # Sort descending by match percentage
    results.sort(key=lambda x: x.match_percentage, reverse=True)
    return results


# =====================================================================
# 5. FEATURE 3: PERSONAL MENTORING THROUGH AI ASSISTANCE
# =====================================================================

@app.post("/mentor/chat", response_model=MentorChatResponse)
def chat_with_mentor(
    payload: MentorChatRequest,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch student profile & skill analytics
    skills = db.query(SkillProfile).filter(SkillProfile.student_id == current_user.id).all()
    weak_topics = [s.topic for s in skills if s.status == "weak"]
    strong_topics = [s.topic for s in skills if s.status == "strong"]

    # Recent mock test scores
    recent_tests = db.query(MockTest).filter(
        MockTest.student_id == current_user.id,
        MockTest.status == "completed"
    ).order_by(desc(MockTest.created_at)).limit(3).all()
    scores = [{"subject": t.subject, "score": t.score, "total": t.total_marks} for t in recent_tests]

    # Save student message
    student_msg = MentorChatMessage(
        student_id=current_user.id,
        sender="student",
        message=payload.message
    )
    db.add(student_msg)
    db.commit()

    # Generate response
    response_text, referenced_topics, suggested_chips = get_mentor_response(
        user_message=payload.message,
        student_name=current_user.name,
        weak_topics=weak_topics,
        strong_topics=strong_topics,
        recent_scores=scores,
        chat_history=[]
    )

    # Save mentor message
    mentor_msg = MentorChatMessage(
        student_id=current_user.id,
        sender="mentor",
        message=response_text,
        referenced_topics=referenced_topics
    )
    db.add(mentor_msg)
    db.commit()

    return MentorChatResponse(
        response=response_text,
        referenced_topics=referenced_topics,
        suggested_chips=suggested_chips,
        timestamp=mentor_msg.created_at
    )


@app.get("/mentor/history", response_model=MentorHistoryResponse)
def get_mentor_history(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    messages = db.query(MentorChatMessage).filter(
        MentorChatMessage.student_id == current_user.id
    ).order_by(MentorChatMessage.created_at.asc()).all()

    skills = db.query(SkillProfile).filter(SkillProfile.student_id == current_user.id).all()
    weak_topics = [s.topic for s in skills if s.status == "weak"]

    chips = [
        "How can I improve my weak topics?",
        "Create a 7-day study timetable",
        "Which entrance exams should I prioritize?"
    ]
    if weak_topics:
        chips[0] = f"How can I improve in {weak_topics[0]}?"

    return MentorHistoryResponse(
        messages=[MentorMessageItem.model_validate(m) for m in messages],
        student_weak_topics=weak_topics,
        suggested_chips=chips
    )


@app.delete("/mentor/history")
def clear_mentor_history(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(MentorChatMessage).filter(MentorChatMessage.student_id == current_user.id).delete()
    db.commit()
    return {"message": "Chat history cleared successfully"}


# =====================================================================
# 6. FEATURE 4: MOCK TESTS BASED ON STUDENT LEVEL
# =====================================================================

@app.post("/mock-tests/generate", response_model=MockTestStartResponse)
def generate_mock_test(
    payload: MockTestCreate,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject = payload.subject
    total_q = payload.total_questions or 6

    # Determine difficulty selection
    if payload.difficulty_mode == "adaptive":
        # Check student skill profile for this subject
        weak_topics = [
            s.topic for s in db.query(SkillProfile).filter(
                SkillProfile.student_id == current_user.id,
                SkillProfile.subject == subject,
                SkillProfile.status == "weak"
            ).all()
        ]

        selected_questions = []
        # If student has weak topics, pull foundational (easy/medium) questions from weak topics
        if weak_topics:
            weak_q = db.query(QuestionBank).filter(
                QuestionBank.subject == subject,
                QuestionBank.topic.in_(weak_topics),
                QuestionBank.difficulty.in_(["easy", "medium"])
            ).limit(total_q // 2).all()
            selected_questions.extend(weak_q)

        remaining_needed = total_q - len(selected_questions)
        other_q = db.query(QuestionBank).filter(
            QuestionBank.subject == subject,
            ~QuestionBank.id.in_([q.id for q in selected_questions])
        ).limit(remaining_needed).all()
        selected_questions.extend(other_q)
    else:
        # Manual override (easy, medium, difficult)
        selected_questions = db.query(QuestionBank).filter(
            QuestionBank.subject == subject,
            QuestionBank.difficulty == payload.difficulty_mode
        ).limit(total_q).all()

        # If not enough at exact difficulty, backfill
        if len(selected_questions) < total_q:
            more_q = db.query(QuestionBank).filter(
                QuestionBank.subject == subject,
                ~QuestionBank.id.in_([q.id for q in selected_questions])
            ).limit(total_q - len(selected_questions)).all()
            selected_questions.extend(more_q)

    if not selected_questions:
        raise HTTPException(
            status_code=404,
            detail=f"No questions available in question bank for subject: {subject}"
        )

    # Create mock test record
    test = MockTest(
        student_id=current_user.id,
        subject=subject,
        difficulty_mode=payload.difficulty_mode,
        time_limit_minutes=max(5, len(selected_questions) * 2),
        total_questions=len(selected_questions),
        total_marks=len(selected_questions),
        status="in_progress"
    )
    db.add(test)
    db.commit()
    db.refresh(test)

    # Initialize responses table
    for q in selected_questions:
        db.add(MockTestResponse(
            mock_test_id=test.id,
            question_id=q.id,
            topic=q.topic
        ))
    db.commit()

    # Build question output (options without revealing correct_option!)
    questions_out = [
        MockTestQuestionOut(
            question_id=q.id,
            question_number=idx + 1,
            topic=q.topic,
            difficulty=q.difficulty,
            question_text=q.question_text,
            options=q.options
        )
        for idx, q in enumerate(selected_questions)
    ]

    return MockTestStartResponse(
        test_id=test.id,
        subject=subject,
        difficulty_mode=payload.difficulty_mode,
        time_limit_minutes=test.time_limit_minutes,
        total_questions=test.total_questions,
        questions=questions_out
    )


@app.post("/mock-tests/{test_id}/submit", response_model=MockTestResultResponse)
def submit_mock_test(
    test_id: int,
    payload: MockTestSubmit,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    test = db.query(MockTest).filter(
        MockTest.id == test_id,
        MockTest.student_id == current_user.id
    ).first()
    if not test:
        raise HTTPException(status_code=404, detail="Mock test not found")

    answers_dict = {a.question_id: a.selected_option for a in payload.answers}

    # Fetch stored responses
    responses = db.query(MockTestResponse).filter(MockTestResponse.mock_test_id == test.id).all()
    q_ids = [r.question_id for r in responses]
    questions = {q.id: q for q in db.query(QuestionBank).filter(QuestionBank.id.in_(q_ids)).all()}

    score = 0
    topic_stats: Dict[str, Dict[str, int]] = {}
    reviews: List[QuestionReviewItem] = []

    for resp in responses:
        q = questions.get(resp.question_id)
        if not q:
            continue

        selected = answers_dict.get(q.id)
        is_correct = (selected is not None and selected == q.correct_option)
        resp.selected_option = selected
        resp.is_correct = is_correct

        if is_correct:
            score += 1

        topic = q.topic
        if topic not in topic_stats:
            topic_stats[topic] = {"correct": 0, "total": 0}
        topic_stats[topic]["total"] += 1
        if is_correct:
            topic_stats[topic]["correct"] += 1

        reviews.append(
            QuestionReviewItem(
                question_id=q.id,
                question_text=q.question_text,
                topic=q.topic,
                difficulty=q.difficulty,
                options=q.options,
                selected_option=selected,
                correct_option=q.correct_option,
                is_correct=is_correct,
                explanation=q.explanation,
                related_material_id=q.related_material_id
            )
        )

    test.score = float(score)
    test.status = "completed"
    test.completed_at = datetime.datetime.utcnow()
    test.topic_breakdown = topic_stats
    db.commit()

    # ==========================================
    # UPDATE SKILL PROFILE AUTOMATICALLY!
    # ==========================================
    for topic, stats in topic_stats.items():
        accuracy = (stats["correct"] / stats["total"]) * 100.0

        skill = db.query(SkillProfile).filter(
            SkillProfile.student_id == current_user.id,
            SkillProfile.subject == test.subject,
            SkillProfile.topic == topic
        ).first()

        if not skill:
            skill = SkillProfile(
                student_id=current_user.id,
                subject=test.subject,
                topic=topic,
                mastery_score=accuracy,
                tests_taken=1
            )
            db.add(skill)
        else:
            # Exponential moving average to smoothly update mastery
            skill.tests_taken += 1
            skill.mastery_score = round(0.6 * skill.mastery_score + 0.4 * accuracy, 1)

        # Re-classify status
        if skill.mastery_score < 50.0:
            skill.status = "weak"
        elif skill.mastery_score <= 75.0:
            skill.status = "average"
        else:
            skill.status = "strong"

    db.commit()

    # Fetch updated skill profile
    updated_skills = db.query(SkillProfile).filter(
        SkillProfile.student_id == current_user.id,
        SkillProfile.subject == test.subject
    ).all()

    percentage = round((score / test.total_marks) * 100.0, 1) if test.total_marks > 0 else 0.0

    return MockTestResultResponse(
        test_id=test.id,
        subject=test.subject,
        difficulty_mode=test.difficulty_mode,
        score=float(score),
        total_marks=test.total_marks,
        percentage=percentage,
        topic_breakdown=topic_stats,
        questions_review=reviews,
        updated_skill_profile=[SkillProfileItem.model_validate(s) for s in updated_skills]
    )


@app.get("/mock-tests/history", response_model=List[MockTestHistoryItem])
def get_mock_test_history(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tests = db.query(MockTest).filter(
        MockTest.student_id == current_user.id,
        MockTest.status == "completed"
    ).order_by(desc(MockTest.created_at)).all()

    result = []
    for t in tests:
        pct = round((t.score / t.total_marks) * 100.0, 1) if t.total_marks > 0 else 0.0
        result.append(
            MockTestHistoryItem(
                id=t.id,
                subject=t.subject,
                difficulty_mode=t.difficulty_mode,
                score=t.score,
                total_marks=t.total_marks,
                percentage=pct,
                status=t.status,
                created_at=t.created_at
            )
        )
    return result


# =====================================================================
# 7. FEATURE 5: COURSE SUMMARIES & RAPID REVISION
# =====================================================================

@app.get("/summaries", response_model=List[CourseSummaryResponse])
def list_course_summaries(
    subject: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(CourseSummary)
    if subject and subject != "All":
        query = query.filter(CourseSummary.subject == subject)
    return [CourseSummaryResponse.model_validate(s) for s in query.all()]


@app.get("/summaries/{summary_id}", response_model=CourseSummaryResponse)
def get_course_summary(
    summary_id: int,
    db: Session = Depends(get_db)
):
    summary = db.query(CourseSummary).filter(CourseSummary.id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Course summary not found")
    return CourseSummaryResponse.model_validate(summary)


@app.put("/summaries/{summary_id}", response_model=CourseSummaryResponse)
def edit_course_summary(
    summary_id: int,
    payload: CourseSummaryUpdate,
    current_teacher: Student = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    summary = db.query(CourseSummary).filter(CourseSummary.id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Course summary not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "quiz_questions" in update_data and update_data["quiz_questions"]:
        update_data["quiz_questions"] = [q if isinstance(q, dict) else q.model_dump() for q in update_data["quiz_questions"]]

    for key, val in update_data.items():
        setattr(summary, key, val)

    summary.last_edited_by = current_teacher.id
    summary.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(summary)
    return CourseSummaryResponse.model_validate(summary)


@app.post("/summaries/{summary_id}/quiz-submit", response_model=QuickQuizResult)
def submit_summary_quiz(
    summary_id: int,
    payload: QuickQuizSubmit,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    summary = db.query(CourseSummary).filter(CourseSummary.id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Course summary not found")

    quiz_questions = summary.quiz_questions or []
    answers_map = {a.question_index: a.selected_option for a in payload.answers}

    score = 0
    total = len(quiz_questions)
    details = []

    for idx, q in enumerate(quiz_questions):
        selected = answers_map.get(idx)
        correct = q.get("correct_option")
        is_correct = (selected == correct)
        if is_correct:
            score += 1
        details.append({
            "question": q.get("question"),
            "selected_option": selected,
            "correct_option": correct,
            "is_correct": is_correct,
            "explanation": q.get("explanation")
        })

    pct = round((score / total) * 100.0, 1) if total > 0 else 0.0
    feedback = (
        "🌟 Excellent quick retention! You've nailed the core concepts." if pct >= 75
        else "👍 Good effort! Review the quick formula sheet above to solidify your memory." if pct >= 50
        else "⚠️ Consider re-reading the summary notes before attempting your next mock test."
    )

    return QuickQuizResult(
        summary_id=summary.id,
        score=score,
        total=total,
        percentage=pct,
        feedback=feedback,
        details=details
    )


# =====================================================================
# 8. FEATURE 6: PREVIOUS QUESTION PAPERS (SOLVED)
# =====================================================================

@app.get("/papers", response_model=List[PaperListItem])
def list_previous_papers(
    subject: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(PreviousPaper)
    if subject and subject != "All":
        query = query.filter(PreviousPaper.subject == subject)
    if year:
        query = query.filter(PreviousPaper.year == year)

    papers = query.order_by(desc(PreviousPaper.year)).all()
    results = []
    for p in papers:
        q_count = len(p.questions)
        results.append(
            PaperListItem(
                id=p.id,
                title=p.title,
                subject=p.subject,
                year=p.year,
                time_limit_minutes=p.time_limit_minutes,
                total_marks=p.total_marks,
                questions_count=q_count
            )
        )
    return results


@app.get("/papers/{paper_id}", response_model=PaperDetailResponse)
def get_paper_detail(
    paper_id: int,
    db: Session = Depends(get_db)
):
    paper = db.query(PreviousPaper).filter(PreviousPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Previous question paper not found")

    questions_out = []
    for q in sorted(paper.questions, key=lambda x: x.question_number):
        mat_title = q.related_material.title if q.related_material else None
        questions_out.append(
            PaperQuestionOut(
                id=q.id,
                question_number=q.question_number,
                topic=q.topic,
                question_text=q.question_text,
                options=q.options,
                correct_option=q.correct_option,
                step_by_step_solution=q.step_by_step_solution,
                related_material_id=q.related_material_id,
                related_material_title=mat_title
            )
        )

    return PaperDetailResponse(
        id=paper.id,
        title=paper.title,
        subject=paper.subject,
        year=paper.year,
        time_limit_minutes=paper.time_limit_minutes,
        total_marks=paper.total_marks,
        questions=questions_out
    )


@app.post("/papers/{paper_id}/attempt", response_model=PaperAttemptResult)
def submit_paper_attempt(
    paper_id: int,
    payload: PaperAttemptSubmit,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    paper = db.query(PreviousPaper).filter(PreviousPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    answers_map = {a.question_id: a.selected_option for a in payload.answers}
    questions = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper.id).all()

    score = 0
    remediations: List[RemediationItem] = []
    topic_results: Dict[str, Dict[str, int]] = {}

    for q in questions:
        selected = answers_map.get(q.id)
        is_correct = (selected is not None and selected == q.correct_option)
        if is_correct:
            score += 1

        topic_results.setdefault(q.topic, {"correct": 0, "total": 0})
        topic_results[q.topic]["total"] += 1
        if is_correct:
            topic_results[q.topic]["correct"] += 1

        mat_title = q.related_material.title if q.related_material else None

        remediations.append(
            RemediationItem(
                question_id=q.id,
                question_number=q.question_number,
                topic=q.topic,
                question_text=q.question_text,
                selected_option=selected,
                correct_option=q.correct_option,
                is_correct=is_correct,
                step_by_step_solution=q.step_by_step_solution,
                related_material_id=q.related_material_id,
                related_material_title=mat_title
            )
        )

    # Save attempt
    attempt = PaperAttempt(
        student_id=current_user.id,
        paper_id=paper.id,
        score=float(score),
        total_marks=len(questions),
        time_spent_seconds=payload.time_spent_seconds,
        answers={str(q.id): answers_map.get(q.id) for q in questions}
    )
    db.add(attempt)
    db.commit()

    # Update topic proficiency in skill profile
    weak_updated = []
    for top, data in topic_results.items():
        acc = (data["correct"] / data["total"]) * 100.0
        sk = db.query(SkillProfile).filter(
            SkillProfile.student_id == current_user.id,
            SkillProfile.subject == paper.subject,
            SkillProfile.topic == top
        ).first()
        if sk:
            sk.tests_taken += 1
            sk.mastery_score = round(0.7 * sk.mastery_score + 0.3 * acc, 1)
            if sk.mastery_score < 50:
                sk.status = "weak"
                weak_updated.append(top)
            elif sk.mastery_score <= 75:
                sk.status = "average"
            else:
                sk.status = "strong"
    db.commit()

    total_marks = len(questions)
    pct = round((score / total_marks) * 100.0, 1) if total_marks > 0 else 0.0

    return PaperAttemptResult(
        paper_id=paper.id,
        paper_title=paper.title,
        score=float(score),
        total_marks=total_marks,
        percentage=pct,
        time_spent_seconds=payload.time_spent_seconds,
        remediations=remediations,
        weak_topics_updated=weak_updated
    )


# =====================================================================
# 9. TEACHER DASHBOARD
# =====================================================================

@app.get("/teacher/dashboard", response_model=TeacherDashboardStats)
def get_teacher_dashboard(
    current_teacher: Student = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    total_students = db.query(Student).filter(Student.role == "student").count()
    total_materials = db.query(StudyMaterial).count()
    total_papers = db.query(PreviousPaper).count()
    total_summaries = db.query(CourseSummary).count()

    # Find class-wide weak topics
    all_skills = db.query(SkillProfile).all()
    topic_agg: Dict[tuple, Dict[str, Any]] = {}
    for s in all_skills:
        key = (s.subject, s.topic)
        if key not in topic_agg:
            topic_agg[key] = {"weak": 0, "scores": []}
        if s.status == "weak":
            topic_agg[key]["weak"] += 1
        topic_agg[key]["scores"].append(s.mastery_score)

    weak_topics_list = []
    for (subj, top), val in topic_agg.items():
        mat_count = db.query(StudyMaterial).filter(
            StudyMaterial.subject == subj,
            StudyMaterial.topic == top
        ).count()
        avg_score = round(sum(val["scores"]) / len(val["scores"]), 1) if val["scores"] else 0.0
        weak_topics_list.append(
            ClassWeakTopicItem(
                subject=subj,
                topic=top,
                weak_students_count=val["weak"],
                average_mastery=avg_score,
                linked_materials_count=mat_count
            )
        )

    # Sort topics by most weak students first
    weak_topics_list.sort(key=lambda x: (x.weak_students_count, -x.average_mastery), reverse=True)

    # Identify at-risk students (>= 2 weak topics)
    students = db.query(Student).filter(Student.role == "student").all()
    at_risk = []
    for st in students:
        st_skills = db.query(SkillProfile).filter(SkillProfile.student_id == st.id).all()
        st_weak = [s.topic for s in st_skills if s.status == "weak"]
        if len(st_weak) >= 1: # Flag students with weak areas
            avg_m = round(sum(s.mastery_score for s in st_skills) / len(st_skills), 1) if st_skills else 0.0
            at_risk.append(
                AtRiskStudentItem(
                    student_id=st.id,
                    name=st.name,
                    email=st.email,
                    weak_topics_count=len(st_weak),
                    weak_topics=st_weak,
                    average_mastery=avg_m
                )
            )

    at_risk.sort(key=lambda x: x.weak_topics_count, reverse=True)

    return TeacherDashboardStats(
        total_students=total_students,
        total_materials=total_materials,
        total_papers=total_papers,
        total_summaries=total_summaries,
        class_weak_topics=weak_topics_list[:8],
        at_risk_students=at_risk
    )
