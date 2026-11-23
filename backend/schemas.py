from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, ConfigDict, Field


# ---------------- Auth & User Schemas ---------------- #
class StudentRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[str] = "student" # 'student' or 'teacher'
    course: Optional[str] = Field(None, max_length=100)
    subject: Optional[str] = Field(None, max_length=100)
    college: Optional[str] = Field(None, max_length=150)
    semester: Optional[str] = Field(None, max_length=20)
    class_code: Optional[str] = Field(None, max_length=16)


class StudentLogin(BaseModel):
    email: EmailStr
    password: str


class StudentResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


class TeacherRegistrationPendingResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    approval_status: str
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    student_id: int
    name: str
    email: str
    role: str


class ProfileCreate(BaseModel):
    student_id: int
    course: str
    stream: str
    academic_level: str
    learning_goal: str
    college: Optional[str] = None
    semester: Optional[str] = None


class ProfileResponse(BaseModel):
    id: int
    student_id: int
    course: Optional[str] = None
    stream: Optional[str] = None
    academic_level: Optional[str] = None
    learning_goal: Optional[str] = None
    college: Optional[str] = None
    semester: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------- Skill Profile Schemas ---------------- #
class SkillProfileItem(BaseModel):
    id: int
    subject: str
    topic: str
    status: str # 'weak', 'average', 'strong'
    mastery_score: float
    tests_taken: int
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SkillSummaryResponse(BaseModel):
    total_topics: int
    weak_count: int
    average_count: int
    strong_count: int
    average_mastery: float
    weak_topics: List[str]
    strong_topics: List[str]
    subject_breakdown: Dict[str, Dict[str, Any]]


# ---------------- Study Materials Schemas ---------------- #
class StudyMaterialBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    subject: str
    topic: str
    course: Optional[str] = Field(None, max_length=100)
    curriculum: Optional[str] = Field(None, max_length=150)
    academic_year: Optional[str] = Field(None, max_length=20)
    material_type: str # 'notes', 'learning_material', 'important_questions', 'topic_resource'
    content: str
    summary: Optional[str] = None
    difficulty_level: Optional[str] = "medium"


class StudyMaterialCreate(StudyMaterialBase):
    pass


class StudyMaterialUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    course: Optional[str] = Field(None, max_length=100)
    curriculum: Optional[str] = Field(None, max_length=150)
    academic_year: Optional[str] = Field(None, max_length=20)
    material_type: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    difficulty_level: Optional[str] = None


class StudyMaterialResponse(StudyMaterialBase):
    id: int
    uploaded_by: Optional[int] = None
    created_at: datetime
    is_bookmarked: Optional[bool] = False
    is_weak_topic: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class StudyMaterialListResponse(BaseModel):
    items: List[StudyMaterialResponse]
    total: int
    page: int
    pages: int


class BookmarkToggleResponse(BaseModel):
    material_id: int
    bookmarked: bool
    message: str


# ---------------- Course Guidance Schemas ---------------- #
class QuestionnaireSubmit(BaseModel):
    preferred_work_style: str # e.g. "Practical / Hands-on", "Theoretical / Research", "Creative / Tech"
    favorite_subject: str # e.g. "Biology", "Mathematics", "Computer Science"
    career_interest: str # e.g. "Medicine & Healthcare", "Software & AI", "Engineering", "Data & Finance"
    higher_study_goal: str # e.g. "Immediate Jobs", "Master's Degree", "Research / PhD"
    study_budget: str # e.g. "Low / Public University", "Medium", "High / Private"


class GuidanceCourseResponse(BaseModel):
    id: int
    title: str
    stream: str
    degree_level: str
    description: str
    eligibility: str
    fees_range: str
    scope_and_careers: List[str]
    entrance_exams: List[Dict[str, Any]]
    roadmap_steps: List[Dict[str, Any]]
    match_percentage: int
    recommended_reason: str

    model_config = ConfigDict(from_attributes=True)


class QuestionnaireResponse(BaseModel):
    message: str
    interest_tags: List[str]
    recommended_courses: List[GuidanceCourseResponse]


# ---------------- AI Personal Mentor Schemas ---------------- #
class MentorChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class MentorChatResponse(BaseModel):
    response: str
    referenced_topics: List[str]
    suggested_chips: List[str]
    timestamp: datetime


class MentorMessageItem(BaseModel):
    id: int
    sender: str
    message: str
    referenced_topics: Optional[List[str]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MentorHistoryResponse(BaseModel):
    messages: List[MentorMessageItem]
    student_weak_topics: List[str]
    suggested_chips: List[str]


# ---------------- Mock Tests Schemas ---------------- #
class MockTestCreate(BaseModel):
    subject: str
    difficulty_mode: str = "adaptive" # 'adaptive', 'easy', 'medium', 'difficult'
    total_questions: Optional[int] = 6


class MockTestQuestionOut(BaseModel):
    question_id: int
    question_number: int
    topic: str
    difficulty: str
    question_text: str
    options: List[str]


class MockTestStartResponse(BaseModel):
    test_id: int
    subject: str
    difficulty_mode: str
    time_limit_minutes: int
    total_questions: int
    questions: List[MockTestQuestionOut]


class MockAnswerSubmit(BaseModel):
    question_id: int
    selected_option: Optional[int] # None if unanswered


class MockTestSubmit(BaseModel):
    test_id: int
    answers: List[MockAnswerSubmit]


class QuestionReviewItem(BaseModel):
    question_id: int
    question_text: str
    topic: str
    difficulty: str
    options: List[str]
    selected_option: Optional[int]
    correct_option: int
    is_correct: bool
    explanation: Optional[str] = None
    related_material_id: Optional[int] = None


class MockTestResultResponse(BaseModel):
    test_id: int
    subject: str
    difficulty_mode: str
    score: float
    total_marks: int
    percentage: float
    topic_breakdown: Dict[str, Dict[str, Any]]
    questions_review: List[QuestionReviewItem]
    updated_skill_profile: List[SkillProfileItem]


class MockTestHistoryItem(BaseModel):
    id: int
    subject: str
    difficulty_mode: str
    score: float
    total_marks: int
    percentage: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------- Course Summaries Schemas ---------------- #
class QuizQuestionItem(BaseModel):
    question: str
    options: List[str]
    correct_option: int
    explanation: str


class CourseSummaryResponse(BaseModel):
    id: int
    subject: str
    course: Optional[str] = None
    curriculum: Optional[str] = None
    academic_year: Optional[str] = None
    topic: str
    title: str
    overview: str
    key_points: List[str]
    quick_revision_notes: str
    quiz_questions: List[QuizQuestionItem]
    is_ai_generated: bool
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseSummaryUpdate(BaseModel):
    title: Optional[str] = None
    overview: Optional[str] = None
    key_points: Optional[List[str]] = None
    quick_revision_notes: Optional[str] = None
    quiz_questions: Optional[List[QuizQuestionItem]] = None


class QuickQuizAnswer(BaseModel):
    question_index: int
    selected_option: int


class QuickQuizSubmit(BaseModel):
    summary_id: int
    answers: List[QuickQuizAnswer]


class QuickQuizResult(BaseModel):
    summary_id: int
    score: int
    total: int
    percentage: float
    feedback: str
    details: List[Dict[str, Any]]


# ---------------- Previous Papers Schemas ---------------- #
class PaperQuestionOut(BaseModel):
    id: int
    question_number: int
    topic: str
    question_text: str
    options: List[str]
    correct_option: int
    step_by_step_solution: str
    related_material_id: Optional[int] = None
    related_material_title: Optional[str] = None


class PaperListItem(BaseModel):
    id: int
    title: str
    subject: str
    year: int
    time_limit_minutes: int
    total_marks: int
    questions_count: int

    model_config = ConfigDict(from_attributes=True)


class PaperDetailResponse(BaseModel):
    id: int
    title: str
    subject: str
    year: int
    time_limit_minutes: int
    total_marks: int
    questions: List[PaperQuestionOut]

    model_config = ConfigDict(from_attributes=True)


class PaperAttemptAnswer(BaseModel):
    question_id: int
    selected_option: Optional[int]


class PaperAttemptSubmit(BaseModel):
    paper_id: int
    time_spent_seconds: int
    answers: List[PaperAttemptAnswer]


class RemediationItem(BaseModel):
    question_id: int
    question_number: int
    topic: str
    question_text: str
    selected_option: Optional[int]
    correct_option: int
    is_correct: bool
    step_by_step_solution: str
    related_material_id: Optional[int] = None
    related_material_title: Optional[str] = None


class PaperAttemptResult(BaseModel):
    paper_id: int
    paper_title: str
    score: float
    total_marks: int
    percentage: float
    time_spent_seconds: int
    remediations: List[RemediationItem]
    weak_topics_updated: List[str]


# ---------------- Teacher Dashboard Schemas ---------------- #
class ClassWeakTopicItem(BaseModel):
    subject: str
    topic: str
    weak_students_count: int
    average_mastery: float
    linked_materials_count: int


class AtRiskStudentItem(BaseModel):
    student_id: int
    name: str
    email: str
    weak_topics_count: int
    weak_topics: List[str]
    average_mastery: float
    risk_reasons: List[str] = Field(default_factory=list)


class TeacherDashboardStats(BaseModel):
    total_students: int
    total_materials: int
    total_papers: int
    total_summaries: int
    class_weak_topics: List[ClassWeakTopicItem]
    at_risk_students: List[AtRiskStudentItem]
