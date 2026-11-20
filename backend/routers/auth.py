import datetime
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import get_db
from models import Student, StudentProfile, TeacherProfile, StudyClass, ClassEnrollment
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    require_student,
    require_teacher,
)

router = APIRouter()


# ─────────────────────────────────────────────
# PYDANTIC SCHEMAS
# ─────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "student" # "student" or "teacher"
    # Extended profile attributes
    department: Optional[str] = None
    semester: Optional[str] = None
    college: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    learning_interests: Optional[List[str]] = None
    class_code: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class StudentProfileOut(BaseModel):
    id: Optional[int] = None
    department: Optional[str] = None
    semester: Optional[str] = None
    college: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    stream: Optional[str] = None
    academic_level: Optional[str] = None
    learning_goal: Optional[str] = None
    learning_interests: Optional[Any] = None

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    profile: Optional[StudentProfileOut] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProfileUpdateRequest(BaseModel):
    department: Optional[str] = None
    semester: Optional[str] = None
    college: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    stream: Optional[str] = None
    academic_level: Optional[str] = None
    learning_goal: Optional[str] = None
    learning_interests: Optional[List[str]] = None


# ─────────────────────────────────────────────
# AUTHENTICATION ENDPOINTS
# ─────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new Student or Teacher with profile fields and return JWT token.
    """
    email_clean = req.email.strip().lower()
    existing = db.query(Student).filter(Student.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    study_class = None
    if req.class_code and req.class_code.strip():
        study_class = db.query(StudyClass).filter(
            StudyClass.join_code == req.class_code.strip().upper(),
            StudyClass.is_active.is_(True),
        ).first()
        if not study_class:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Class code is invalid or inactive.",
            )

    role_clean = "student"

    new_user = Student(
        name=req.name.strip(),
        email=email_clean,
        password_hash=get_password_hash(req.password),
        role=role_clean,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create associated profile
    if role_clean == "student":
        profile = StudentProfile(
            student_id=new_user.id,
            department=req.department,
            semester=study_class.academic_year if study_class else req.semester,
            college=study_class.curriculum if study_class else req.college,
            phone=req.phone,
            course=study_class.course if study_class else (req.course or "General"),
            stream=req.department or "Science/Technology",
            learning_interests=req.learning_interests or [],
        )
        db.add(profile)
        if study_class:
            db.add(ClassEnrollment(class_id=study_class.id, student_id=new_user.id))
        db.commit()
        db.refresh(new_user)
    else:
        teacher_prof = TeacherProfile(
            teacher_id=new_user.id,
            department=req.department,
            designation="Faculty Instructor",
            college=req.college,
        )
        db.add(teacher_prof)
        db.commit()
        db.refresh(new_user)

    # Issue JWT token
    token = create_access_token(data={
        "sub": str(new_user.id),
        "email": new_user.email,
        "name": new_user.name,
        "role": new_user.role,
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": new_user,
    }


@router.post("/login", response_model=TokenResponse)
def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with email & password and issue JWT token.
    """
    email_clean = req.email.strip().lower()
    user = db.query(Student).filter(Student.email == email_clean).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
    }


@router.get("/me", response_model=UserOut)
def get_current_authenticated_user(current_user: Student = Depends(get_current_user)):
    """
    Fetch current user identity and profile from JWT token.
    """
    return current_user


@router.put("/profile", response_model=StudentProfileOut)
def update_student_profile(
    req: ProfileUpdateRequest,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update or initialize the student's profile information.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.student_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(student_id=current_user.id)
        db.add(profile)

    if req.department is not None:
        profile.department = req.department
    if req.semester is not None:
        profile.semester = req.semester
    if req.college is not None:
        profile.college = req.college
    if req.phone is not None:
        profile.phone = req.phone
    if req.course is not None:
        profile.course = req.course
    if req.stream is not None:
        profile.stream = req.stream
    if req.academic_level is not None:
        profile.academic_level = req.academic_level
    if req.learning_goal is not None:
        profile.learning_goal = req.learning_goal
    if req.learning_interests is not None:
        profile.learning_interests = req.learning_interests

    db.commit()
    db.refresh(profile)
    return profile
