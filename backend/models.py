import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON,
    Index, UniqueConstraint, func,
)
from sqlalchemy.orm import relationship
from database import Base

# =====================================================================
# CORE USER & STUDENT MODELS
# =====================================================================

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="student", nullable=False) # 'student' or 'teacher' or 'admin'

    profile = relationship("StudentProfile", back_populates="student", uselist=False, cascade="all, delete-orphan")
    skills = relationship("SkillProfile", back_populates="student", cascade="all, delete-orphan")
    bookmarks = relationship("MaterialBookmark", back_populates="student", cascade="all, delete-orphan")
    mock_tests = relationship("MockTest", back_populates="student", cascade="all, delete-orphan")
    paper_attempts = relationship("PaperAttempt", back_populates="student", cascade="all, delete-orphan")
    mentor_messages = relationship("MentorChatMessage", back_populates="student", cascade="all, delete-orphan")
    interest_profile = relationship("InterestProfile", back_populates="student", uselist=False, cascade="all, delete-orphan")

    # New Module 4, 5, 6 relationships
    checklist_items = relationship("ApplicationChecklistItem", back_populates="student", cascade="all, delete-orphan")
    deadline_reminders = relationship("DeadlineReminder", back_populates="student", cascade="all, delete-orphan")
    counselling_requests = relationship("CounsellingRequest", foreign_keys="CounsellingRequest.student_id", back_populates="student", cascade="all, delete-orphan")
    test_attempts = relationship("TestAttempt", back_populates="student", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="student", cascade="all, delete-orphan")
    class_enrollments = relationship("ClassEnrollment", back_populates="student", cascade="all, delete-orphan")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False)
    course = Column(String(100))
    stream = Column(String(100))
    academic_level = Column(String(50))
    learning_goal = Column(String(255))
    phone = Column(String(30), nullable=True)
    department = Column(String(100), nullable=True)
    semester = Column(String(20), nullable=True)
    college = Column(String(150), nullable=True)
    academic_info = Column(Text, nullable=True)
    learning_interests = Column(JSON, nullable=True)

    student = relationship("Student", back_populates="profile")


class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False)
    department = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)
    college = Column(String(150), nullable=True)

    teacher = relationship("Student", foreign_keys=[teacher_id])


class StudyClass(Base):
    __tablename__ = "study_classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    join_code = Column(String(16), nullable=False)
    teacher_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    course = Column(String(100), nullable=False)
    curriculum = Column(String(150), nullable=False)
    academic_year = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("join_code", name="uq_study_class_join_code"),
    )

    teacher = relationship("Student")
    enrollments = relationship("ClassEnrollment", back_populates="study_class", cascade="all, delete-orphan")
    mark_imports = relationship("MarkImportBatch", back_populates="study_class", cascade="all, delete-orphan")
    groups = relationship("StudyGroup", back_populates="study_class")


class ClassEnrollment(Base):
    __tablename__ = "class_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("study_classes.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("class_id", "student_id", name="uq_class_enrollment"),
    )

    study_class = relationship("StudyClass", back_populates="enrollments")
    student = relationship("Student", back_populates="class_enrollments")


class MarkImportBatch(Base):
    __tablename__ = "mark_import_batches"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("study_classes.id", ondelete="CASCADE"), nullable=False)
    imported_by = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=False)
    row_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    study_class = relationship("StudyClass", back_populates="mark_imports")
    marks = relationship("ImportedMark", back_populates="batch", cascade="all, delete-orphan")


class ImportedMark(Base):
    __tablename__ = "imported_marks"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("mark_import_batches.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(100), nullable=False)
    topic = Column(String(100), nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    batch = relationship("MarkImportBatch", back_populates="marks")
    student = relationship("Student")


class SkillProfile(Base):
    __tablename__ = "skill_profiles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(100), nullable=False)
    topic = Column(String(100), nullable=False)
    status = Column(String(20), default="average", nullable=False) # 'weak', 'average', 'strong'
    mastery_score = Column(Float, default=50.0) # 0 to 100
    tests_taken = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("student_id", "subject", "topic", name="uq_student_subject_topic"),
    )

    student = relationship("Student", back_populates="skills")


# =====================================================================
# STUDY MATERIALS & REVISION NOTES
# =====================================================================

class StudyMaterial(Base):
    __tablename__ = "study_materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)
    course = Column(String(100), nullable=True, index=True)
    curriculum = Column(String(150), nullable=True)
    academic_year = Column(String(20), nullable=True)
    material_type = Column(String(50), nullable=False) # 'notes', 'learning_material', 'important_questions', 'topic_resource'
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    difficulty_level = Column(String(20), default="medium") # 'easy', 'medium', 'difficult'
    uploaded_by = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    uploader = relationship("Student", foreign_keys=[uploaded_by])
    bookmarks = relationship("MaterialBookmark", back_populates="material", cascade="all, delete-orphan")


class MaterialBookmark(Base):
    __tablename__ = "material_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(Integer, ForeignKey("study_materials.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("student_id", "material_id", name="uq_student_material_bookmark"),
    )

    student = relationship("Student", back_populates="bookmarks")
    material = relationship("StudyMaterial", back_populates="bookmarks")


class QuestionBank(Base):
    __tablename__ = "question_bank"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(100), nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)
    difficulty = Column(String(20), nullable=False, index=True) # 'easy', 'medium', 'difficult'
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_option = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)
    related_material_id = Column(Integer, ForeignKey("study_materials.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    related_material = relationship("StudyMaterial")


class MockTest(Base):
    __tablename__ = "mock_tests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(100), nullable=False)
    difficulty_mode = Column(String(20), nullable=False)
    time_limit_minutes = Column(Integer, default=15)
    total_questions = Column(Integer, default=10)
    score = Column(Float, default=0.0)
    total_marks = Column(Integer, default=10)
    status = Column(String(20), default="in_progress")
    topic_breakdown = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="mock_tests")
    responses = relationship("MockTestResponse", back_populates="mock_test", cascade="all, delete-orphan")


class MockTestResponse(Base):
    __tablename__ = "mock_test_responses"

    id = Column(Integer, primary_key=True, index=True)
    mock_test_id = Column(Integer, ForeignKey("mock_tests.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("question_bank.id", ondelete="CASCADE"), nullable=False)
    selected_option = Column(Integer, nullable=True)
    is_correct = Column(Boolean, default=False)
    topic = Column(String(100), nullable=False)

    mock_test = relationship("MockTest", back_populates="responses")
    question = relationship("QuestionBank")


class PreviousPaper(Base):
    __tablename__ = "previous_papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    time_limit_minutes = Column(Integer, default=60)
    total_marks = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    questions = relationship("PaperQuestion", back_populates="paper", cascade="all, delete-orphan")
    attempts = relationship("PaperAttempt", back_populates="paper", cascade="all, delete-orphan")


class PaperQuestion(Base):
    __tablename__ = "paper_questions"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("previous_papers.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(Integer, nullable=False)
    topic = Column(String(100), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_option = Column(Integer, nullable=False)
    step_by_step_solution = Column(Text, nullable=False)
    related_material_id = Column(Integer, ForeignKey("study_materials.id", ondelete="SET NULL"), nullable=True)

    paper = relationship("PreviousPaper", back_populates="questions")
    related_material = relationship("StudyMaterial")


class PaperAttempt(Base):
    __tablename__ = "paper_attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    paper_id = Column(Integer, ForeignKey("previous_papers.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    total_marks = Column(Integer, nullable=False)
    time_spent_seconds = Column(Integer, default=0)
    answers = Column(JSON, nullable=False)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="paper_attempts")
    paper = relationship("PreviousPaper", back_populates="attempts")


class GuidanceCourse(Base):
    __tablename__ = "guidance_courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    stream = Column(String(100), nullable=False)
    degree_level = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    eligibility = Column(Text, nullable=False)
    fees_range = Column(String(100), nullable=False)
    scope_and_careers = Column(JSON, nullable=False)
    entrance_exams = Column(JSON, nullable=False)
    roadmap_steps = Column(JSON, nullable=False)
    matching_tags = Column(JSON, nullable=False)


class InterestProfile(Base):
    __tablename__ = "interest_profiles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False)
    answers = Column(JSON, nullable=False)
    interest_tags = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="interest_profile")


class CourseSummary(Base):
    __tablename__ = "course_summaries"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(100), nullable=False, index=True)
    course = Column(String(100), nullable=True, index=True)
    curriculum = Column(String(150), nullable=True)
    academic_year = Column(String(20), nullable=True)
    topic = Column(String(100), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    overview = Column(Text, nullable=False)
    key_points = Column(JSON, nullable=False)
    quick_revision_notes = Column(Text, nullable=False)
    quiz_questions = Column(JSON, nullable=False)
    is_ai_generated = Column(Boolean, default=False)
    last_edited_by = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    editor = relationship("Student")


class MentorChatMessage(Base):
    __tablename__ = "mentor_chat_history"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    referenced_topics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="mentor_messages")


# =====================================================================
# MODULE 4: HIGHER STUDIES & COURSE GUIDANCE EXTENDED MODELS
# =====================================================================

class RoadmapItem(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    stage = Column(String(100), nullable=False) # e.g. "Plus Two / 12th", "Degree / Undergraduate", "Postgraduate"
    stream = Column(String(100), nullable=False) # Science, Commerce, Humanities, Engineering, Medical, Law
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    options = Column(JSON, nullable=False) # list of {type, name, duration, description}
    next_steps = Column(JSON, nullable=False) # list of string suggestions
    order_index = Column(Integer, default=0)


class EntranceExam(Base):
    __tablename__ = "entrance_exams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    conducting_body = Column(String(150), nullable=False)
    eligibility = Column(Text, nullable=False)
    syllabus = Column(Text, nullable=False)
    exam_dates = Column(JSON, nullable=False) # {"notification": "...", "exam_date": "...", "admit_card": "..."}
    application_process = Column(Text, nullable=False)
    preparation_tips = Column(Text, nullable=False)
    official_website_url = Column(String(255), nullable=True)
    stream = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250), nullable=False, index=True)
    location = Column(String(150), nullable=False)
    state = Column(String(100), nullable=False)
    college_type = Column(String(100), nullable=False) # Central, State, Institute of National Importance, Private
    nirf_ranking = Column(Integer, nullable=True)
    courses_offered = Column(JSON, nullable=False) # list of course names or degrees
    admission_process = Column(Text, nullable=False)
    website_url = Column(String(255), nullable=True)
    average_annual_fee = Column(String(100), nullable=True)
    established_year = Column(Integer, nullable=True)


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    stream = Column(String(100), nullable=False, index=True) # Engineering, Computer Applications, Science, Commerce, Humanities, Health Sciences, Law, Design
    degree_level = Column(String(50), nullable=False) # Undergraduate, Postgraduate, Integrated, Diploma
    duration_years = Column(Float, nullable=False) # e.g. 4.0, 3.0, 5.0
    eligibility = Column(Text, nullable=False)
    exams = Column(JSON, nullable=False) # list of accepted entrance exam names
    fee_range = Column(String(100), nullable=False)
    skills_needed = Column(JSON, nullable=False) # list of skills / subject prerequisites
    job_roles = Column(JSON, nullable=False) # list of target job titles
    salary_range = Column(String(100), nullable=False)
    scope = Column(Text, nullable=False) # future growth and market trends
    top_colleges = Column(JSON, nullable=True) # list of top institutions


class Scholarship(Base):
    __tablename__ = "scholarships"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    provider = Column(String(150), nullable=False)
    eligibility = Column(Text, nullable=False)
    amount_and_benefits = Column(String(200), nullable=False)
    deadline_description = Column(String(100), nullable=False)
    application_process = Column(Text, nullable=False)
    application_url = Column(String(255), nullable=True)
    category = Column(String(100), default="Merit") # Merit, Need-based, Minority, Girl Child, Technical


class StudyAbroadInfo(Base):
    __tablename__ = "study_abroad_info"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String(100), nullable=False, unique=True, index=True)
    flag_emoji = Column(String(10), default="🌍")
    popular_courses = Column(JSON, nullable=False) # list of top study tracks
    required_tests = Column(JSON, nullable=False) # e.g. ["IELTS / TOEFL", "GRE", "SAT"]
    avg_tuition_cost = Column(String(100), nullable=False)
    living_cost = Column(String(100), nullable=False)
    visa_work_rights = Column(Text, nullable=False)
    intake_timelines = Column(JSON, nullable=False) # e.g. {"Fall": "August/September", "Spring": "January"}


class ApplicationChecklistItem(Base):
    __tablename__ = "application_checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    category = Column(String(50), default="General") # Exam, College, Scholarship, Document, Visa
    deadline = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="checklist_items")


class DeadlineReminder(Base):
    __tablename__ = "deadline_reminders"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    target_date = Column(DateTime, nullable=False)
    related_type = Column(String(50), nullable=True) # Exam, College, Scholarship
    related_id = Column(Integer, nullable=True)
    reminder_type = Column(String(50), default="Deadline") # Application Deadline, Exam Date, Admit Card
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="deadline_reminders")


class QuestionnaireQuestion(Base):
    __tablename__ = "questionnaire_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    category = Column(String(50), nullable=False) # Aptitude, Interest, Work Style, Subject Preference
    options = Column(JSON, nullable=False) # list of {text, stream_weights: {Engineering: 1.0, ...}}
    order_index = Column(Integer, default=0)


class StudentQuestionnaireAnswer(Base):
    __tablename__ = "questionnaire_student_answers"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questionnaire_questions.id", ondelete="CASCADE"), nullable=False)
    selected_option_index = Column(Integer, nullable=False)
    answer_text = Column(String(255), nullable=True)
    answered_at = Column(DateTime, default=datetime.datetime.utcnow)


class CounsellingRequest(Base):
    __tablename__ = "counselling_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    request_type = Column(String(50), default="higher_studies", nullable=False)
    message = Column(Text, nullable=False)
    preferred_mode = Column(String(50), default="Online") # Online, In-person
    status = Column(String(50), default="pending") # pending, scheduled, completed, cancelled
    teacher_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    student = relationship("Student", foreign_keys=[student_id], back_populates="counselling_requests")
    teacher = relationship("Student", foreign_keys=[teacher_id])


# =====================================================================
# MODULE 5: MOCK TESTS & PREVIOUS PAPERS EXTENDED MODELS
# =====================================================================

class QuestionPaper(Base):
    __tablename__ = "question_papers"

    id = Column(Integer, primary_key=True, index=True)
    exam_name = Column(String(100), nullable=False, index=True) # e.g. JEE Main, NEET, KEAM, Board
    subject = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    topic_tags = Column(JSON, nullable=False) # list of topics covered
    file_path = Column(String(255), nullable=False) # Path to PDF file or secure download URL
    answer_key_file = Column(String(255), nullable=True) # Solution or answer key PDF
    approval_status = Column(String(20), default="approved", nullable=False) # pending, approved, rejected
    uploaded_by = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    uploader = relationship("Student")


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=False, index=True)
    course = Column(String(100), nullable=True, index=True)
    curriculum = Column(String(150), nullable=True)
    academic_year = Column(String(20), nullable=True)
    exam_name = Column(String(100), nullable=True) # e.g. JEE Main, Class 12 Mid-Term
    duration_minutes = Column(Integer, default=30)
    total_marks = Column(Integer, default=20)
    is_adaptive = Column(Boolean, default=False)
    is_published = Column(Boolean, default=True)
    approval_status = Column(String(20), default="pending", nullable=False)
    created_by = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    questions = relationship("TestQuestion", back_populates="test", cascade="all, delete-orphan")
    attempts = relationship("TestAttempt", back_populates="test", cascade="all, delete-orphan")


class TestQuestion(Base):
    __tablename__ = "test_questions"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), default="mcq", nullable=False) # 'mcq', 'true_false', 'short_answer'
    options = Column(JSON, nullable=True) # JSON list for MCQ / TF
    correct_answer = Column(Text, nullable=False) # option index or text answer
    explanation = Column(Text, nullable=True)
    topic = Column(String(100), nullable=False, index=True)
    difficulty = Column(String(20), default="medium") # easy, medium, difficult
    marks = Column(Float, default=1.0)

    test = relationship("Test", back_populates="questions")


class TestAttempt(Base):
    __tablename__ = "test_attempts"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, default=0.0)
    total_marks = Column(Integer, default=0)
    time_taken_seconds = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0) # Percentage 0 to 100
    status = Column(String(20), default="completed") # in_progress, completed, autosubmitted
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="test_attempts")
    test = relationship("Test", back_populates="attempts")
    answers = relationship("AttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")
    result = relationship("TestResult", back_populates="attempt", uselist=False, cascade="all, delete-orphan")


class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("test_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("test_questions.id", ondelete="CASCADE"), nullable=False)
    student_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, default=False)
    marks_awarded = Column(Float, default=0.0)

    attempt = relationship("TestAttempt", back_populates="answers")
    question = relationship("TestQuestion")


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("test_attempts.id", ondelete="CASCADE"), unique=True, nullable=False)
    topic_wise_breakdown = Column(JSON, nullable=False) # {topic: {correct, total, accuracy}}
    strengths = Column(JSON, nullable=True) # list of mastered topics
    weaknesses = Column(JSON, nullable=True) # list of under-performing topics
    suggested_revision_topics = Column(JSON, nullable=True) # list of topics needing attention

    attempt = relationship("TestAttempt", back_populates="result")


# =====================================================================
# MODULE 6: AI CHATBOT (STUDYMATCH ASSISTANT) MODELS
# =====================================================================

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), default="Study Discussion")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(20), nullable=False) # 'student' or 'bot'
    message = Column(Text, nullable=False)
    context_data = Column(JSON, nullable=True) # student profile / weak topics at query time
    sources = Column(JSON, nullable=True) # list of {title, doc_id, snippet}
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class GuidanceDocument(Base):
    __tablename__ = "guidance_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250), nullable=False, index=True)
    doc_type = Column(String(50), nullable=False) # 'exam', 'course', 'college', 'scholarship', 'study_abroad', 'syllabus'
    content = Column(Text, nullable=False)
    file_path = Column(String(255), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    uploader = relationship("Student")
    embeddings = relationship("DocumentEmbedding", back_populates="document", cascade="all, delete-orphan")


class RevisionNote(Base):
    __tablename__ = "revision_notes"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_name = Column(String(100), nullable=False)
    topic_name = Column(String(100), nullable=False)
    content = Column(JSON, nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    reviewed_by = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    student = relationship("Student", foreign_keys=[student_id])
    reviewer = relationship("Student", foreign_keys=[reviewed_by])


class GuidanceActivity(Base):
    __tablename__ = "guidance_activities"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    activity_type = Column(String(20), nullable=False)
    entity_id = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student")

    __table_args__ = (
        Index("ix_guidance_activities_created_at", "created_at"),
        Index("ix_guidance_activities_student_id", "student_id"),
    )


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("guidance_documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=False) # Float vector stored as JSON
    metadata_json = Column(JSON, nullable=True)

    document = relationship("GuidanceDocument", back_populates="embeddings")


# =====================================================================
# SUBJECT, TOPIC & DIAGNOSTIC QUIZ MODELS (DAY 1 - 3 FOUNDATION)
# =====================================================================

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    code = Column(String(30), nullable=True)
    description = Column(Text, nullable=True)
    course = Column(String(100), nullable=True, index=True)
    curriculum = Column(String(150), nullable=True)
    academic_year = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index(
            "uq_subject_course_scope",
            func.lower(name),
            func.lower(func.coalesce(course, "")),
            func.lower(func.coalesce(curriculum, "")),
            func.lower(func.coalesce(academic_year, "")),
            unique=True,
        ),
    )

    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    order_index = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    subject = relationship("Subject", back_populates="topics")
    questions = relationship("Question", back_populates="topic", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="topic", cascade="all, delete-orphan")
    performances = relationship("TopicPerformance", back_populates="topic", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False) # list of string options
    correct_answer = Column(Integer, nullable=False) # 0-indexed choice
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(20), default="medium") # 'easy', 'medium', 'hard'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    topic = relationship("Topic", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    total_marks = Column(Float, nullable=False)
    accuracy = Column(Float, default=0.0)
    time_taken_sec = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student")
    topic = relationship("Topic", back_populates="attempts")
    answers = relationship("QuizAnswer", back_populates="attempt", cascade="all, delete-orphan")


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    selected_option = Column(Integer, nullable=False)
    is_correct = Column(Boolean, default=False)

    attempt = relationship("QuizAttempt", back_populates="answers")
    question = relationship("Question")


class TopicPerformance(Base):
    __tablename__ = "topic_performances"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    accuracy = Column(Float, default=0.0) # 0 to 100
    attempt_count = Column(Integer, default=0)
    status = Column(String(20), default="average") # 'weak', 'average', 'strong'
    last_attempt_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    student = relationship("Student")
    topic = relationship("Topic", back_populates="performances")


# =====================================================================
# STUDY GROUP & PEER TEACHING MODELS (DAY 3 FOUNDATION)
# =====================================================================

class StudyGroup(Base):
    __tablename__ = "study_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    class_id = Column(Integer, ForeignKey("study_classes.id", ondelete="SET NULL"), nullable=True)
    created_by = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), default="pending") # 'pending', 'active', 'completed', 'archived'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    study_class = relationship("StudyClass", back_populates="groups")
    creator = relationship("Student")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    teaching_pairs = relationship("TeachingPair", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("study_groups.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), default="member") # 'lead', 'member'
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)

    group = relationship("StudyGroup", back_populates="members")
    student = relationship("Student")


class TeachingPair(Base):
    __tablename__ = "teaching_pairs"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("study_groups.id", ondelete="CASCADE"), nullable=False)
    tutor_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    learner_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="recommended") # 'recommended', 'accepted', 'completed'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    group = relationship("StudyGroup", back_populates="teaching_pairs")
    tutor = relationship("Student", foreign_keys=[tutor_id])
    learner = relationship("Student", foreign_keys=[learner_id])
    topic = relationship("Topic")


class StudySchedule(Base):
    __tablename__ = "study_schedules"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(String(20), nullable=False) # 'Monday', 'Tuesday', etc.
    start_time = Column(String(10), nullable=False) # '17:00'
    end_time = Column(String(10), nullable=False)   # '19:00'
    study_mode = Column(String(20), default="online", nullable=False)  # online, offline, either
    is_available = Column(Boolean, default=True)

    student = relationship("Student")
