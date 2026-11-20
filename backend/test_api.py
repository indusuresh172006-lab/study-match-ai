import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Student, StudyMaterial, SkillProfile, QuestionBank, PreviousPaper, CourseSummary, GuidanceCourse
from schemas import (
    StudentLogin, QuestionnaireSubmit, MentorChatRequest,
    MockTestCreate, MockTestSubmit, MockAnswerSubmit,
    QuickQuizSubmit, QuickQuizAnswer, PaperAttemptSubmit, PaperAttemptAnswer
)
from main import (
    login_student, get_skill_summary, list_study_materials, toggle_bookmark,
    submit_questionnaire, get_guidance_courses, chat_with_mentor, get_mentor_history,
    generate_mock_test, submit_mock_test, list_course_summaries, submit_summary_quiz,
    list_previous_papers, get_paper_detail, submit_paper_attempt, get_teacher_dashboard
)

def run_tests():
    print("\n--- Starting Comprehensive Backend Feature Tests ---")
    db = SessionLocal()
    try:
        # 1. Student Login
        login_res = login_student(
            StudentLogin(email="student@studymatch.ai", password="password123"),
            db=db
        )
        assert login_res.access_token is not None
        assert login_res.student_id is not None
        student_user = db.query(Student).filter(Student.id == login_res.student_id).first()
        print(f"✓ Test 1: Student Login & JWT Token Passed (User: {student_user.name}, Token: {login_res.access_token[:15]}...)")

        # 2. Teacher Login
        teacher_login_res = login_student(
            StudentLogin(email="teacher@studymatch.ai", password="password123"),
            db=db
        )
        teacher_user = db.query(Student).filter(Student.id == teacher_login_res.student_id).first()
        assert teacher_user.role == "teacher"
        print(f"✓ Test 2: Teacher Login & Role Passed (User: {teacher_user.name}, Role: {teacher_user.role})")

        # 3. Skill Profile Summary
        summary = get_skill_summary(current_user=student_user, db=db)
        assert summary.total_topics > 0
        assert summary.weak_count >= 1
        print(f"✓ Test 3: Skill Profile Summary Passed (Total: {summary.total_topics}, Weak: {summary.weak_count}, Strong: {summary.strong_count})")

        # 4. Feature 1: Study Materials & Weak-Topic Prioritization
        mat_res = list_study_materials(
            subject=None, topic=None, material_type=None, search=None,
            bookmarked_only=False, page=1, limit=9,
            current_user=student_user, db=db
        )
        assert len(mat_res.items) > 0
        first_mat = mat_res.items[0]
        assert first_mat.is_weak_topic is True
        print(f"✓ Test 4: Study Materials Passed (Top material '{first_mat.title}' marked is_weak_topic={first_mat.is_weak_topic})")

        # Bookmark toggle
        bm_res = toggle_bookmark(material_id=first_mat.id, current_user=student_user, db=db)
        print(f"✓ Test 4b: Bookmark Toggle Passed: {bm_res.message}")

        # 5. Feature 2: Future Course Guidance Questionnaire & Matching
        q_payload = QuestionnaireSubmit(
            preferred_work_style="Practical / Hands-on",
            favorite_subject="Computer Science",
            career_interest="Software & AI",
            higher_study_goal="Immediate Jobs",
            study_budget="Medium"
        )
        g_res = submit_questionnaire(payload=q_payload, current_user=student_user, db=db)
        assert len(g_res.recommended_courses) > 0
        top_rec = g_res.recommended_courses[0]
        assert top_rec.match_percentage >= 70
        print(f"✓ Test 5: Course Guidance Engine Passed (Top: '{top_rec.title}', Match: {top_rec.match_percentage}%)")

        # 6. Feature 3: Personal Mentoring through AI Assistance
        chat_res = chat_with_mentor(
            payload=MentorChatRequest(message="Can you help me understand Calculus limits and my weak areas?"),
            current_user=student_user,
            db=db
        )
        assert len(chat_res.response) > 50
        assert len(chat_res.suggested_chips) > 0
        print(f"✓ Test 6: AI Personal Mentor Chat Passed (Response: {chat_res.response[:60]}...)")

        history_res = get_mentor_history(current_user=student_user, db=db)
        assert len(history_res.messages) >= 2 # student msg + mentor response
        print(f"✓ Test 6b: Mentor Chat History Persisted ({len(history_res.messages)} messages in thread)")

        # 7. Feature 4: Mock Tests Based on Student Level (Adaptive & Auto-scoring)
        test_session = generate_mock_test(
            payload=MockTestCreate(subject="Biology", difficulty_mode="adaptive", total_questions=4),
            current_user=student_user,
            db=db
        )
        assert test_session.test_id is not None
        assert len(test_session.questions) == 4
        print(f"✓ Test 7: Adaptive Mock Test Generated (Test ID: {test_session.test_id}, Questions: {len(test_session.questions)})")

        # Submit answers
        q_submits = [MockAnswerSubmit(question_id=q.question_id, selected_option=1) for q in test_session.questions]
        sub_res = submit_mock_test(
            test_id=test_session.test_id,
            payload=MockTestSubmit(test_id=test_session.test_id, answers=q_submits),
            current_user=student_user,
            db=db
        )
        assert sub_res.score is not None
        assert len(sub_res.updated_skill_profile) > 0
        print(f"✓ Test 7b: Mock Test Scored & Skill Profile Auto-Updated (Score: {sub_res.score}/{sub_res.total_marks})")

        # 8. Feature 5: Course Summaries & Rapid Revision
        summaries = list_course_summaries(subject=None, current_user=teacher_user, db=db)
        assert len(summaries) >= 3
        first_sum = summaries[0]
        quiz_res = submit_summary_quiz(
            summary_id=first_sum.id,
            payload=QuickQuizSubmit(
                summary_id=first_sum.id,
                answers=[QuickQuizAnswer(question_index=0, selected_option=1), QuickQuizAnswer(question_index=1, selected_option=2)]
            ),
            current_user=teacher_user,
            db=db
        )
        assert quiz_res.total > 0
        print(f"✓ Test 8: Course Summaries & Rapid Quiz Passed (Summary: '{first_sum.title}', Quiz Score: {quiz_res.score}/{quiz_res.total})")

        # 9. Feature 6: Solved Previous Papers & Wrong-Answer Remediation
        papers = list_previous_papers(subject=None, year=None, db=db)
        assert len(papers) >= 3
        p1 = papers[0]
        p_detail = get_paper_detail(paper_id=p1.id, db=db)
        assert len(p_detail.questions) > 0

        # Submit paper attempt with deliberately wrong option 99 to check remediation links
        wrong_attempt = submit_paper_attempt(
            paper_id=p1.id,
            payload=PaperAttemptSubmit(
                paper_id=p1.id,
                time_spent_seconds=60,
                answers=[PaperAttemptAnswer(question_id=p_detail.questions[0].id, selected_option=99)]
            ),
            current_user=student_user,
            db=db
        )
        assert wrong_attempt.remediations[0].is_correct is False
        assert wrong_attempt.remediations[0].related_material_id is not None
        print(f"✓ Test 9: Previous Papers Solved & Remediation Link Passed (Wrong Answer linked to Material: '{wrong_attempt.remediations[0].related_material_title}')")

        # 10. Teacher Dashboard
        teacher_dash = get_teacher_dashboard(current_teacher=teacher_user, db=db)
        assert teacher_dash.total_students >= 1
        assert len(teacher_dash.class_weak_topics) >= 1
        print(f"✓ Test 10: Teacher Dashboard Analytics Passed (Total Students: {teacher_dash.total_students}, Top Weak Topic: {teacher_dash.class_weak_topics[0].topic})")

        print("\n=======================================================")
        print("🎉 ALL 10 COMPREHENSIVE BACKEND UNIT TESTS PASSED! 🎉")
        print("=======================================================\n")

    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
