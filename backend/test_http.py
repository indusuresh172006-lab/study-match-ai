"""
HTTP-level tests: real requests through FastAPI (routing, JWT dependency,
role guards, validation). Run from the backend folder:  pytest test_http.py -v
Needs:  python -m pip install pytest httpx
"""
import uuid
import pytest
from fastapi.testclient import TestClient

from main import app
from database import SessionLocal
from models import Student, StudentProfile, TeacherProfile
from auth import get_password_hash

API = "/api/v1"
PASSWORD = "TestPass123!"
client = TestClient(app)


def _email(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@httptest.com"


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _login(email, password=PASSWORD):
    return client.post(f"{API}/auth/login", json={"email": email, "password": password})


def _delete_user(email):
    db = SessionLocal()
    try:
        user = db.query(Student).filter(Student.email == email).first()
        if user:
            db.query(StudentProfile).filter(StudentProfile.student_id == user.id).delete()
            db.query(TeacherProfile).filter(TeacherProfile.teacher_id == user.id).delete()
            db.delete(user)
            db.commit()
    finally:
        db.close()


@pytest.fixture
def student():
    email = _email("student")
    res = client.post(f"{API}/auth/register", json={
        "name": "HTTP Student", "email": email, "password": PASSWORD,
        "department": "CSE", "semester": "5", "college": "Test College",
    })
    assert res.status_code == 201, res.text
    yield {"email": email, "token": res.json()["access_token"]}
    _delete_user(email)


@pytest.fixture
def teacher():
    """Teachers are created directly in the DB, as sign-up must not grant this role."""
    email = _email("teacher")
    db = SessionLocal()
    try:
        user = Student(name="HTTP Teacher", email=email,
                       password_hash=get_password_hash(PASSWORD), role="teacher")
        db.add(user)
        db.commit()
        db.refresh(user)
        db.add(TeacherProfile(teacher_id=user.id, department="CSE",
                              designation="Faculty Instructor", college="Test College"))
        db.commit()
    finally:
        db.close()
    token = _login(email).json()["access_token"]
    yield {"email": email, "token": token}
    _delete_user(email)


# ---------- Registration ----------

def test_register_returns_201_and_token(student):
    assert student["token"]


def test_register_duplicate_email_rejected(student):
    res = client.post(f"{API}/auth/register", json={
        "name": "Dup", "email": student["email"], "password": PASSWORD})
    assert res.status_code == 400


def test_register_invalid_email_returns_422():
    res = client.post(f"{API}/auth/register", json={
        "name": "Bad", "email": "not-an-email", "password": PASSWORD})
    assert res.status_code == 422


def test_register_missing_fields_returns_422():
    assert client.post(f"{API}/auth/register", json={"email": _email("x")}).status_code == 422


def test_legacy_register_saves_selected_course():
    email = _email("course")
    try:
        res = client.post("/register", json={
            "name": "Course Student", "email": email, "password": PASSWORD,
            "course": "B.Tech / B.E.", "college": "Test Institute",
            "semester": "Year 2",
        })
        assert res.status_code == 200, res.text

        db = SessionLocal()
        try:
            student = db.query(Student).filter(Student.email == email).first()
            profile = db.query(StudentProfile).filter(
                StudentProfile.student_id == student.id
            ).first()
            assert profile.course == "B.Tech / B.E."
            assert profile.college == "Test Institute"
            assert profile.semester == "Year 2"
        finally:
            db.close()
    finally:
        _delete_user(email)


def test_student_can_request_teacher_study_support(student):
    res = client.post(
        f"{API}/guidance/counselling",
        headers=_auth(student["token"]),
        json={
            "request_type": "study_support",
            "message": "Please help with weak topics.",
            "preferred_mode": "Online",
        },
    )
    assert res.status_code == 201
    requests = client.get(
        f"{API}/guidance/counselling", headers=_auth(student["token"])
    )
    assert requests.status_code == 200
    assert requests.json()[0]["request_type"] == "study_support"


def test_student_only_sees_study_materials_for_exact_course_scope(student, teacher):
    profile = client.put(
        f"{API}/auth/profile",
        headers=_auth(student["token"]),
        json={
            "course": "Diploma",
            "college": "Polytechnic College Kannur",
            "semester": "3rd Semester",
        },
    )
    assert profile.status_code == 200, profile.text

    created_ids = []
    try:
        for suffix, course, curriculum, academic_year in [
            ("matching", "Diploma", "Polytechnic College Kannur", "3rd Semester"),
            ("other-course", "B.Tech / B.E.", "Polytechnic College Kannur", "3rd Semester"),
            ("unscoped", None, None, None),
        ]:
            response = client.post(
                "/materials",
                headers=_auth(teacher["token"]),
                json={
                    "title": f"Scoped material {suffix} {uuid.uuid4().hex[:6]}",
                    "subject": "Materials Scope Test",
                    "topic": "Materials Scope",
                    "course": course,
                    "curriculum": curriculum,
                    "academic_year": academic_year,
                    "material_type": "notes",
                    "content": "Course-scoped test material.",
                },
            )
            assert response.status_code == 200, response.text
            created_ids.append(response.json()["id"])

        materials = client.get("/materials", headers=_auth(student["token"]))
        assert materials.status_code == 200, materials.text
        visible_ids = {item["id"] for item in materials.json()["items"]}
        assert created_ids[0] in visible_ids
        assert created_ids[1] not in visible_ids
        assert created_ids[2] not in visible_ids
        assert client.get(
            f"/materials/{created_ids[1]}", headers=_auth(student["token"])
        ).status_code == 404
        assert client.get(
            f"/materials/{created_ids[2]}", headers=_auth(student["token"])
        ).status_code == 404
    finally:
        for material_id in created_ids:
            client.delete(
                f"/materials/{material_id}", headers=_auth(teacher["token"])
            )


def test_register_cannot_create_teacher():
    """SECURITY: public sign-up must never grant the teacher role."""
    email = _email("sneaky")
    try:
        res = client.post(f"{API}/auth/register", json={
            "name": "Sneaky", "email": email, "password": PASSWORD, "role": "teacher"})
        assert res.status_code in (201, 400, 403)
        if res.status_code == 201:
            assert res.json()["user"]["role"] == "student"
    finally:
        _delete_user(email)


def test_password_is_not_returned_or_stored_plain(student):
    res = client.get(f"{API}/auth/me", headers=_auth(student["token"]))
    assert "password" not in res.text.lower()
    db = SessionLocal()
    try:
        user = db.query(Student).filter(Student.email == student["email"]).first()
        assert user.password_hash != PASSWORD
    finally:
        db.close()


# ---------- Login and JWT ----------

def test_login_success(student):
    res = _login(student["email"])
    assert res.status_code == 200
    assert res.json()["token_type"] == "bearer"


def test_login_wrong_password_returns_401(student):
    assert _login(student["email"], "WrongPass999").status_code == 401


def test_login_unknown_user_returns_401():
    assert _login(_email("ghost")).status_code == 401


def test_me_requires_token():
    assert client.get(f"{API}/auth/me").status_code == 401


def test_me_rejects_garbage_token():
    assert client.get(f"{API}/auth/me", headers=_auth("not.a.jwt")).status_code == 401


def test_me_returns_current_user(student):
    res = client.get(f"{API}/auth/me", headers=_auth(student["token"]))
    assert res.status_code == 200
    assert res.json()["email"] == student["email"]
    assert res.json()["role"] == "student"


def test_profile_update_persists(student):
    res = client.put(f"{API}/auth/profile", headers=_auth(student["token"]),
                     json={"department": "ECE", "learning_interests": ["AI", "Python"]})
    assert res.status_code == 200
    me = client.get(f"{API}/auth/me", headers=_auth(student["token"])).json()
    assert me["profile"]["department"] == "ECE"


def test_profile_update_requires_token():
    assert client.put(f"{API}/auth/profile", json={"department": "X"}).status_code == 401


# ---------- Role-based access: subjects and topics ----------

def test_create_subject_without_token_returns_401():
    assert client.post(f"{API}/subjects", json={"name": "NoAuth"}).status_code == 401


def test_student_cannot_create_subject(student):
    res = client.post(f"{API}/subjects", headers=_auth(student["token"]),
                      json={"name": f"Blocked {uuid.uuid4().hex[:6]}"})
    assert res.status_code == 403


def test_teacher_syllabus_subjects_are_filterable_by_course(teacher):
    subject_name = f"Scoped Subject {uuid.uuid4().hex[:6]}"
    payload = {
        "name": subject_name,
        "course": "Diploma in Civil Engineering",
        "curriculum": "Test Technical Board",
        "academic_year": "Semester 2",
    }
    created = client.post(f"{API}/subjects", headers=_auth(teacher["token"]), json=payload)
    assert created.status_code == 201, created.text
    subject_id = created.json()["id"]
    try:
        filters = {
            "course": payload["course"],
            "curriculum": payload["curriculum"],
            "academic_year": payload["academic_year"],
        }
        matched = client.get(f"{API}/subjects", params=filters)
        assert matched.status_code == 200
        assert subject_id in [item["id"] for item in matched.json()]

        unmatched = client.get(
            f"{API}/subjects",
            params={**filters, "curriculum": "Different Board"},
        )
        assert unmatched.status_code == 200
        assert subject_id not in [item["id"] for item in unmatched.json()]
    finally:
        assert client.delete(
            f"{API}/subjects/{subject_id}", headers=_auth(teacher["token"])
        ).status_code == 200


def test_teacher_subject_and_topic_lifecycle(teacher, student):
    th = _auth(teacher["token"])
    name = f"HTTP Subject {uuid.uuid4().hex[:6]}"

    created = client.post(f"{API}/subjects", headers=th, json={"name": name, "code": "HT101"})
    assert created.status_code == 201
    sid = created.json()["id"]
    try:
        # duplicate subject rejected
        assert client.post(f"{API}/subjects", headers=th, json={"name": name}).status_code == 400

        # topic creation: teacher ok, student blocked, bad parent -> 404
        topic = client.post(f"{API}/topics", headers=th,
                            json={"subject_id": sid, "name": "Variables", "order_index": 1})
        assert topic.status_code == 201
        assert client.post(f"{API}/topics", headers=_auth(student["token"]),
                           json={"subject_id": sid, "name": "Nope"}).status_code == 403
        assert client.post(f"{API}/topics", headers=th,
                           json={"subject_id": 999999, "name": "Orphan"}).status_code == 404

        # students can read the subject and its topics
        sh = _auth(student["token"])
        assert client.get(f"{API}/subjects/{sid}", headers=sh).status_code == 200
        topics = client.get(f"{API}/subjects/{sid}/topics", headers=sh)
        assert topics.status_code == 200
        assert [t["name"] for t in topics.json()] == ["Variables"]

        # student cannot delete
        assert client.delete(f"{API}/subjects/{sid}", headers=sh).status_code == 403
    finally:
        assert client.delete(f"{API}/subjects/{sid}", headers=th).status_code == 200
    assert client.get(f"{API}/subjects/{sid}").status_code == 404


def test_create_topic_invalid_body_returns_422(teacher):
    res = client.post(f"{API}/topics", headers=_auth(teacher["token"]), json={"name": "No subject"})
    assert res.status_code == 422


def test_legacy_register_cannot_create_teacher():
    """SECURITY: the /register route used by the React app must also force student."""
    email = _email("legacy")
    try:
        res = client.post("/register", json={
            "name": "Legacy Sneaky", "email": email,
            "password": PASSWORD, "role": "teacher"})
        assert res.status_code == 200, res.text
        assert res.json()["role"] == "student"
    finally:
        _delete_user(email)


# ---------- Quiz question management (teacher) ----------

def test_question_management_lifecycle(teacher, student):
    th, sh = _auth(teacher["token"]), _auth(student["token"])
    sid = client.post(f"{API}/subjects", headers=th,
                      json={"name": f"QM Subject {uuid.uuid4().hex[:6]}"}).json()["id"]
    try:
        tid = client.post(f"{API}/topics", headers=th,
                          json={"subject_id": sid, "name": "QM Topic"}).json()["id"]
        body = {"topic_id": tid, "question_text": "Which keyword filters rows in SQL?",
                "options": ["WHERE", "ORDER", "GROUP", "LIMIT"], "correct_answer": 0,
                "explanation": "WHERE filters rows.", "difficulty": "easy"}

        # students cannot add, list (answers visible) or delete
        assert client.post(f"{API}/quiz/questions", headers=sh, json=body).status_code == 403
        assert client.get(f"{API}/quiz/questions", headers=sh).status_code == 403

        # invalid payloads are rejected
        bad = dict(body, options=["only one"])
        assert client.post(f"{API}/quiz/questions", headers=th, json=bad).status_code == 422

        created = client.post(f"{API}/quiz/questions", headers=th, json=body)
        assert created.status_code == 201
        qid = created.json()["id"]

        listed = client.get(f"{API}/quiz/questions", headers=th, params={"topic_id": tid})
        assert [q["id"] for q in listed.json()] == [qid]

        # the student quiz must NOT leak the correct answer
        quiz = client.get(f"{API}/quiz/topic/{tid}", headers=sh)
        assert quiz.status_code == 200
        assert "correct_answer" not in quiz.text

        assert client.delete(f"{API}/quiz/questions/{qid}", headers=sh).status_code == 403
        assert client.delete(f"{API}/quiz/questions/{qid}", headers=th).status_code == 200
        assert client.delete(f"{API}/quiz/questions/{qid}", headers=th).status_code == 404
    finally:
        client.delete(f"{API}/subjects/{sid}", headers=th)