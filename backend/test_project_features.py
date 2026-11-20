import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi import HTTPException

from academic_scope import normalize_academic_year
from main import _scope_materials_to_student
from routers.academic import list_subjects
from ml.group_matcher import form_balanced_study_groups, match_study_schedules
from routers.chatbot import _find_study_resources
from routers.classes import parse_mark_rows
from routers.guidance import _filter_courses_for_diploma, recommend_courses
from routers.mock_tests_v2 import _test_matches_student_scope, create_test


class ProjectFeatureTests(unittest.TestCase):
    def test_mark_import_normalizes_headers_and_scores(self):
        rows = parse_mark_rows(
            "marks.csv",
            (
                "Student Email,Subject,Topic,Score,Max Score\n"
                "ava@example.com,Mathematics,Algebra,8,10\n"
            ).encode("utf-8"),
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["student_email"], "ava@example.com")
        self.assertEqual(rows[0]["topic"], "Algebra")
        self.assertEqual(rows[0]["score"], 8)
        self.assertEqual(rows[0]["max_score"], 10)

    def test_mark_import_rejects_scores_above_maximum(self):
        with self.assertRaises(HTTPException) as raised:
            parse_mark_rows(
                "marks.csv",
                (
                    "student_email,subject,topic,score,max_score\n"
                    "ava@example.com,Mathematics,Algebra,11,10\n"
                ).encode("utf-8"),
            )

        self.assertEqual(raised.exception.status_code, 422)

    def test_group_matcher_does_not_create_undersized_groups(self):
        self.assertEqual(
            form_balanced_study_groups(
                [{"id": 1}, {"id": 2}],
                min_size=3,
                max_size=5,
            ),
            [],
        )

    def test_schedule_matching_separates_modes_and_counts_unscheduled_members(self):
        schedules = {
            1: [{"day_of_week": "Monday", "start_time": "17:00", "end_time": "18:00", "study_mode": "online"}],
            2: [{"day_of_week": "Monday", "start_time": "17:00", "end_time": "18:00", "study_mode": "offline"}],
            3: [{"day_of_week": "Monday", "start_time": "17:00", "end_time": "18:00", "study_mode": "either"}],
            4: [],
        }

        matches = match_study_schedules(schedules, {1: "A", 2: "B", 3: "C", 4: "D"})

        by_mode = {match["study_mode"]: match for match in matches}
        self.assertEqual(set(by_mode), {"online", "offline"})
        self.assertEqual(by_mode["online"]["available_count"], 2)
        self.assertEqual(by_mode["offline"]["available_count"], 2)
        self.assertEqual(by_mode["online"]["total_members"], 4)
        self.assertEqual(by_mode["offline"]["total_members"], 4)

    def test_chatbot_resource_search_filters_subject_and_requested_year_range(self):
        this_year = date.today().year
        matching_paper = SimpleNamespace(
            id=1,
            title="Physics Practice Paper",
            subject="Physics",
            exam_name="KEAM",
            year=this_year,
            topic_tags=["Mechanics"],
        )
        old_paper = SimpleNamespace(
            id=2,
            title="Physics Paper",
            subject="Physics",
            exam_name="KEAM",
            year=this_year - 5,
            topic_tags=[],
        )
        matching_test = SimpleNamespace(
            id=3,
            title="Physics Mock Test",
            subject="Physics",
            exam_name="KEAM",
            created_at=None,
        )
        unrelated_test = SimpleNamespace(
            id=4,
            title="Biology Mock Test",
            subject="Biology",
            exam_name="NEET",
            created_at=None,
        )
        paper_query = MagicMock()
        paper_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            matching_paper,
            old_paper,
        ]
        test_query = MagicMock()
        test_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            matching_test,
            unrelated_test,
        ]
        db = MagicMock()
        db.query.side_effect = [paper_query, test_query]

        results = _find_study_resources("Physics question papers from last 3 years", db)

        self.assertEqual([resource["title"] for resource in results], [
            "Physics Practice Paper",
            "Physics Mock Test",
        ])
        self.assertEqual(results[0]["link"], "/papers")
        self.assertEqual(results[1]["link"], "/mock-tests")

    def test_chatbot_skips_resource_queries_for_general_questions(self):
        db = MagicMock()

        self.assertEqual(_find_study_resources("How do I improve in physics?", db), [])
        db.query.assert_not_called()

    def test_chatbot_resource_search_respects_an_exact_paper_year(self):
        matching_paper = SimpleNamespace(
            id=5,
            title="Physics Practice Paper",
            subject="Physics",
            exam_name="KEAM",
            year=2024,
            topic_tags=[],
        )
        other_paper = SimpleNamespace(
            id=6,
            title="Physics Practice Paper",
            subject="Physics",
            exam_name="KEAM",
            year=2023,
            topic_tags=[],
        )
        paper_query = MagicMock()
        paper_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            matching_paper,
            other_paper,
        ]
        test_query = MagicMock()
        test_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        db = MagicMock()
        db.query.side_effect = [paper_query, test_query]

        results = _find_study_resources("2024 Physics question paper", db)

        self.assertEqual([resource["year"] for resource in results], [2024])

    def test_diploma_recommendations_only_include_matching_lateral_entry_paths(self):
        profile = SimpleNamespace(
            course="Diploma",
            department="Computer Engineering",
            stream="Engineering",
        )
        matching = SimpleNamespace(
            title="B.Tech Computer Science & Engineering (Lateral Entry)",
            eligibility="Diploma in a related engineering branch.",
        )
        unrelated_branch = SimpleNamespace(
            title="B.Tech Electronics & Communication Engineering (Lateral Entry)",
            eligibility="Diploma in a related engineering branch.",
        )
        regular_degree = SimpleNamespace(
            title="B.Tech Computer Science & Engineering",
            eligibility="10+2 with PCM.",
        )
        unrelated_degree = SimpleNamespace(title="MBBS", eligibility="10+2 with PCB.")

        self.assertEqual(
            _filter_courses_for_diploma(
                [matching, unrelated_branch, regular_degree, unrelated_degree],
                profile,
            ),
            [matching],
        )

    def test_diploma_with_unrecognized_branch_does_not_get_general_recommendations(self):
        profile = SimpleNamespace(
            course="Diploma",
            department="Polymer Technology",
            stream="Engineering",
        )
        course = SimpleNamespace(
            title="B.Tech Computer Science & Engineering (Lateral Entry)",
            eligibility="Diploma in a related engineering branch.",
        )

        self.assertEqual(_filter_courses_for_diploma([course], profile), [])

    def test_recommendation_endpoint_never_returns_unrelated_paths_for_diploma(self):
        profile = SimpleNamespace(
            course="Diploma in Computer Engineering",
            department=None,
            stream="Engineering",
        )
        matching = SimpleNamespace(
            id=1,
            title="B.Tech Computer Science & Engineering (Lateral Entry)",
            eligibility="Diploma in a related engineering branch.",
            stream="Engineering",
            degree_level="Undergraduate Lateral Entry",
            duration_years=3.0,
            exams=[],
            fee_range="Varies",
            skills_needed=[],
            job_roles=[],
            salary_range="Varies",
            scope="",
            top_colleges=[],
        )
        unrelated = SimpleNamespace(
            id=2,
            title="MBBS",
            eligibility="10+2 with PCB.",
            stream="Health Sciences",
            degree_level="Undergraduate",
            duration_years=5.5,
            exams=[],
            fee_range="Varies",
            skills_needed=[],
            job_roles=[],
            salary_range="Varies",
            scope="",
            top_colleges=[],
        )
        profile_query = MagicMock()
        profile_query.filter.return_value.first.return_value = profile
        skills_query = MagicMock()
        skills_query.filter.return_value.all.return_value = []
        answers_query = MagicMock()
        answers_query.filter.return_value.all.return_value = []
        courses_query = MagicMock()
        courses_query.all.return_value = [matching, unrelated]
        db = MagicMock()
        db.query.side_effect = [
            profile_query,
            skills_query,
            answers_query,
            courses_query,
        ]

        recommendations = recommend_courses(db, current_user=SimpleNamespace(id=7))

        self.assertEqual([item["title"] for item in recommendations], [matching.title])
        self.assertIn("lateral-entry", recommendations[0]["match_reason"])

    def test_subject_list_matches_ordinal_semester_variants(self):
        matching_subject = SimpleNamespace(
            id=1,
            name="Programming",
            code=None,
            description=None,
            course="Diploma in Computer Engineering",
            curriculum="Polytechnic College Kannur",
            academic_year="3rd Semester",
            topics=[],
        )
        other_semester = SimpleNamespace(
            id=2,
            name="Programming II",
            code=None,
            description=None,
            course="Diploma in Computer Engineering",
            curriculum="Polytechnic College Kannur",
            academic_year="4th Semester",
            topics=[],
        )
        subjects_query = MagicMock()
        subjects_query.filter.return_value = subjects_query
        subjects_query.order_by.return_value.all.return_value = [
            matching_subject,
            other_semester,
        ]
        db = MagicMock()
        db.query.return_value = subjects_query

        results = list_subjects(
            course="Diploma in Computer Engineering",
            curriculum="Polytechnic College Kannur",
            academic_year="3rs sem",
            db=db,
        )

        self.assertEqual([item.name for item in results], ["Programming"])

    def test_material_scope_matches_semester_variants_and_excludes_other_semesters(self):
        profile = SimpleNamespace(
            course="Diploma in Computer Engineering",
            college="Polytechnic College Kannur",
            semester="3rs sem",
        )
        matching_material = SimpleNamespace(id=1, academic_year="3rd Semester")
        other_semester = SimpleNamespace(id=2, academic_year="4th Semester")
        profile_query = MagicMock()
        profile_query.filter.return_value.first.return_value = profile
        db = MagicMock()
        db.query.return_value = profile_query

        materials_query = MagicMock()
        scoped_query = MagicMock()
        scoped_query.all.return_value = [matching_material, other_semester]
        materials_query.filter.side_effect = [scoped_query, materials_query]

        result = _scope_materials_to_student(
            materials_query,
            SimpleNamespace(id=7, role="student"),
            db,
        )

        self.assertIs(result, materials_query)
        matching_ids = materials_query.filter.call_args_list[1].args[0].right.value
        self.assertEqual(matching_ids, [1])

    def test_semester_scope_normalizes_ordinal_and_abbreviated_forms(self):
        self.assertEqual(normalize_academic_year("3rs sem"), "semester:3")
        self.assertEqual(normalize_academic_year("3rd Semester"), "semester:3")
        self.assertEqual(normalize_academic_year("Semester 3"), "semester:3")

    def test_mock_test_scope_matches_course_college_and_normalized_semester(self):
        scope = (
            "diploma in computer engineering",
            "polytechnic college kannur",
            "semester:3",
        )
        matching_test = SimpleNamespace(
            course="Diploma in Computer Engineering",
            curriculum="Polytechnic College Kannur",
            academic_year="3rd Semester",
        )
        other_course = SimpleNamespace(
            course="B.Tech",
            curriculum="Polytechnic College Kannur",
            academic_year="3rd Semester",
        )
        other_semester = SimpleNamespace(
            course="Diploma in Computer Engineering",
            curriculum="Polytechnic College Kannur",
            academic_year="4th Semester",
        )

        self.assertTrue(_test_matches_student_scope(matching_test, scope))
        self.assertFalse(_test_matches_student_scope(other_course, scope))
        self.assertFalse(_test_matches_student_scope(other_semester, scope))

    def test_mock_test_rejects_partial_course_scope(self):
        with self.assertRaises(HTTPException) as raised:
            create_test(
                {"title": "Scoped test", "subject": "Programming", "course": "Diploma"},
                db=MagicMock(),
                current_user=SimpleNamespace(id=1),
            )

        self.assertEqual(raised.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
