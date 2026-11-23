"""
Unit & Integration Test Suite for Day 1: Backend Foundation
Tests registration, JWT authentication, RBAC role guards, and Subject/Topic Management.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import Response
from database import SessionLocal
from models import Student, Subject, Topic
from auth import create_access_token
from routers import auth as auth_router, academic as academic_router


def run_day1_tests():
    db = SessionLocal()
    print("--- Starting Day 1 Backend Foundation Tests ---")

    try:
        # 1. Test Student Registration with Extended Profile
        test_email = "day1_student@test.com"
        existing = db.query(Student).filter(Student.email == test_email).first()
        if existing:
            db.delete(existing)
            db.commit()

        reg_req = auth_router.RegisterRequest(
            name="Rohit Sharma",
            email=test_email,
            password="password123",
            role="student",
            department="Computer Science",
            semester="S5",
            college="National Institute of Technology",
            phone="9876543210",
            learning_interests=["Machine Learning", "System Design"],
        )
        reg_res = auth_router.register_user(reg_req, response=Response(), db=db)
        assert reg_res["access_token"] is not None
        assert reg_res["user"].role == "student"
        assert reg_res["user"].profile.department == "Computer Science"
        assert reg_res["user"].profile.semester == "S5"
        print("✓ Test 1: Student Registration with extended profile passed.")

        # 2. Test Student Login & Token Verification
        login_req = auth_router.LoginRequest(email=test_email, password="password123")
        login_res = auth_router.login_user(login_req, db=db)
        assert login_res["access_token"] is not None
        assert login_res["user"].email == test_email
        print("✓ Test 2: Student Login & JWT Token issuance passed.")

        # 3. Test Teacher Identity & Role
        teacher = db.query(Student).filter(Student.role == "teacher").first()
        assert teacher is not None, "A teacher user must exist in the database."
        teacher_token = create_access_token(data={"sub": str(teacher.id), "role": "teacher"})
        print(f"✓ Test 3: Teacher identified ('{teacher.name}', Role: {teacher.role}).")

        # 4. Test Role-Based Access Control (RBAC) Guard
        # Student attempting to create a subject must be rejected with 403 Forbidden
        student_user = db.query(Student).filter(Student.email == test_email).first()
        try:
            academic_router.create_subject(
                req=academic_router.SubjectCreate(name="Unauthorized Subject"),
                current_user=student_user, # is a student
                db=db
            )
            assert False, "Student should have been blocked with 403 Forbidden!"
        except Exception as exc:
            assert getattr(exc, "status_code", None) == 403 or "Teacher role required" in str(exc)
            print("✓ Test 4: RBAC successfully blocked unauthorized student subject creation (403 Forbidden).")

        # 5. Teacher Successfully Creates Subject and Topic
        test_sub_name = "Cloud Computing & DevOps"
        existing_sub = db.query(Subject).filter(Subject.name == test_sub_name).first()
        if existing_sub:
            db.delete(existing_sub)
            db.commit()

        created_sub = academic_router.create_subject(
            req=academic_router.SubjectCreate(
                name=test_sub_name,
                code="CS-405",
                description="Modern cloud infrastructure, containers, and CI/CD pipelines."
            ),
            current_user=teacher, # is teacher
            db=db
        )
        assert created_sub.id is not None
        assert created_sub.name == test_sub_name
        print(f"✓ Test 5a: Teacher successfully created subject '{created_sub.name}'.")

        # Teacher adds a topic to this subject
        created_topic = academic_router.create_topic(
            req=academic_router.TopicCreate(
                subject_id=created_sub.id,
                name="Docker & Containerization",
                order_index=1,
                description="Container images, Dockerfiles, and container lifecycles."
            ),
            current_user=teacher,
            db=db
        )
        assert created_topic.id is not None
        assert created_topic.subject_id == created_sub.id
        print(f"✓ Test 5b: Teacher successfully added topic '{created_topic.name}' under subject.")

        # 6. Fetch Subjects List
        subjects = academic_router.list_subjects(db=db)
        assert len(subjects) >= 5
        print(f"✓ Test 6: Retrieved {len(subjects)} subjects with nested topic structures.")

        # 7. Fetch Topics for Subject
        topics = academic_router.list_topics_for_subject(subject_id=created_sub.id, db=db)
        assert len(topics) >= 1
        assert topics[0].name == "Docker & Containerization"
        print(f"✓ Test 7: Retrieved topics for subject '{created_sub.name}'.")

        # 8. Profile Update Test
        upd_req = auth_router.ProfileUpdateRequest(
            phone="9998887776",
            learning_goal="Master full-stack engineering and machine learning"
        )
        upd_res = auth_router.update_student_profile(upd_req, current_user=student_user, db=db)
        assert upd_res.phone == "9998887776"
        assert upd_res.learning_goal == "Master full-stack engineering and machine learning"
        print("✓ Test 8: Student profile update verified.")

        print("\n=======================================================")
        print("🎉 ALL DAY 1 BACKEND FOUNDATION TESTS PASSED! 🎉")
        print("=======================================================\n")

    finally:
        # Remove test data so it never pollutes the real database
        db.rollback()
        test_user = db.query(Student).filter(Student.email == "day1_student@test.com").first()
        if test_user:
            db.delete(test_user)
        test_sub = db.query(Subject).filter(Subject.name == "Cloud Computing & DevOps").first()
        if test_sub:
            db.delete(test_sub)
        db.commit()
        db.close()


if __name__ == "__main__":
    run_day1_tests()
