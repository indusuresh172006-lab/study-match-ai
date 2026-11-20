"""Seed course-scoped starter quizzes and study notes for Kerala Diploma Computer Engineering, Semester III."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import CourseSummary, Question, StudyMaterial, Subject, Test, TestQuestion, Topic


COURSE = "Diploma in Computer Engineering"
CURRICULUM = "Polytechnic College Kannur"
SEMESTER = "3rd Semester"
REVISION = "SITTTR Revision 2021"

COURSES = [
    {
        "code": "3131",
        "name": "Computer Organisation",
        "topic": "CPU organization and instruction cycle",
        "topic_description": "CPU components, registers, buses, and the instruction cycle.",
        "question": "Which CPU component directs the steps required to execute an instruction?",
        "options": ["Control unit", "ALU", "Cache memory", "Input unit"],
        "correct": 0,
        "explanation": "The control unit coordinates instruction fetch, decode, and execution.",
        "material_type": "notes",
        "material_summary": "Review the main CPU components and how instructions move through the processor.",
        "summary_key_points": [
            "The control unit coordinates instruction execution; the ALU handles arithmetic and logic.",
            "The instruction cycle commonly proceeds through fetch, decode, and execute.",
            "Registers and cache provide fast storage close to the CPU.",
        ],
        "material_content": """# Computer Organisation - Quick Notes

The CPU contains the arithmetic logic unit (ALU), control unit, and registers. The control unit directs operations, while the ALU performs arithmetic and logical operations. Registers hold small amounts of data close to the CPU.

An instruction cycle commonly includes fetch, decode, and execute. The memory hierarchy places registers and cache near the CPU, followed by main memory and secondary storage.

These are starter revision notes for the SITTTR Revision 2021 course. Confirm detailed unit coverage with the official syllabus and your teacher.""",
    },
    {
        "code": "3132",
        "name": "Programming in C",
        "topic": "C control flow and arrays",
        "topic_description": "Expressions, selection, iteration, and basic array processing in C.",
        "question": "Which loop is most suitable when the number of iterations is known before the loop starts?",
        "options": ["for", "switch", "goto", "typedef"],
        "correct": 0,
        "explanation": "A for loop groups initialization, condition, and update for a counted iteration.",
        "material_type": "notes",
        "material_summary": "A concise review of C statements, loops, and arrays.",
        "summary_key_points": [
            "Use if or switch for selection and loops for repeated operations.",
            "A for loop is convenient when the iteration count is known.",
            "C arrays use zero-based indexes; initialize values and check bounds.",
        ],
        "material_content": """# Programming in C - Quick Notes

A C program uses declarations, expressions, and statements. Selection statements such as if and switch choose a path. Loops repeat work: for is convenient for counted loops, while checks a condition before each iteration, and do-while checks after the loop body.

An array stores elements of one type in consecutive indexed positions. In C, the first array element has index 0. Check array bounds carefully and initialize variables before using them.

These are starter revision notes for the SITTTR Revision 2021 course. Confirm detailed unit coverage with the official syllabus and your teacher.""",
    },
    {
        "code": "3133",
        "name": "Database Management Systems",
        "topic": "Relational tables, keys, and SQL",
        "topic_description": "Relational data, key constraints, and foundational SQL queries.",
        "question": "What is the main purpose of a primary key in a relational table?",
        "options": [
            "Uniquely identify each row",
            "Sort all rows automatically",
            "Store multiple values in one cell",
            "Hide the table from users",
        ],
        "correct": 0,
        "explanation": "A primary key uniquely identifies each row and cannot contain duplicate key values.",
        "material_type": "notes",
        "material_summary": "Review relational tables, keys, and the structure of common SQL queries.",
        "summary_key_points": [
            "Relational data is organized in tables of rows and columns.",
            "Primary keys identify rows; foreign keys connect related tables.",
            "SELECT reads rows, while INSERT, UPDATE, and DELETE change data.",
        ],
        "material_content": """# Database Management Systems - Quick Notes

A relational database stores data in tables made of rows and columns. A primary key identifies a row; a foreign key connects a row to a key in another table. Constraints help protect data integrity.

SQL statements include SELECT for reading data, INSERT for adding rows, UPDATE for changing rows, and DELETE for removing rows. WHERE filters rows, while JOIN combines related tables.

These are starter revision notes for the SITTTR Revision 2021 course. Confirm detailed unit coverage with the official syllabus and your teacher.""",
    },
    {
        "code": "3134",
        "name": "Digital Computer Fundamentals",
        "topic": "Number systems and Boolean logic",
        "topic_description": "Binary representation, logic operations, and truth tables.",
        "question": "What is the decimal value of the binary number 1011?",
        "options": ["9", "10", "11", "13"],
        "correct": 2,
        "explanation": "1011₂ = 8 + 0 + 2 + 1 = 11₁₀.",
        "material_type": "learning_material",
        "material_summary": "Practice binary place values and the basic operations of Boolean logic.",
        "summary_key_points": [
            "Each binary digit represents a power of two; 1011₂ equals 11₁₀.",
            "Boolean values are 0 and 1.",
            "AND, OR, and NOT operations can be checked with truth tables.",
        ],
        "material_content": """# Digital Computer Fundamentals - Quick Notes

Binary numbers use the digits 0 and 1. Each position represents a power of two; for example, 1011₂ equals 1×8 + 0×4 + 1×2 + 1×1 = 11₁₀.

Boolean variables take the values 0 or 1. AND is 1 only when both inputs are 1, OR is 1 when at least one input is 1, and NOT reverses its input. Truth tables list the output for every possible input combination.

These are starter revision notes for the SITTTR Revision 2021 course. Confirm detailed unit coverage with the official syllabus and your teacher.""",
    },
    {
        "code": "3135",
        "name": "Programming in C Lab",
        "topic": "Writing and testing C programs",
        "topic_description": "Program structure, input/output, functions, and systematic testing.",
        "question": "Which function is the usual entry point of a hosted C program?",
        "options": ["main", "start", "printf", "include"],
        "correct": 0,
        "explanation": "Execution of a standard hosted C program begins in main.",
        "material_type": "topic_resource",
        "material_summary": "A simple checklist for building, running, and checking C lab programs.",
        "summary_key_points": [
            "Identify the inputs, outputs, and algorithm before writing code.",
            "Compile and resolve warnings before evaluating program output.",
            "Test normal and boundary inputs and record observed results.",
        ],
        "material_content": """# Programming in C Lab - Practice Guide

1. Read the problem and identify inputs, outputs, and required calculations.
2. Write the algorithm before coding.
3. Implement the program with a clear main function and suitable variables.
4. Compile, fix warnings, and test normal and boundary inputs.
5. Record the expected result and the result observed during the lab.

These are starter revision notes for the SITTTR Revision 2021 course. Confirm lab experiments with your teacher.""",
    },
    {
        "code": "3136",
        "name": "Database Management System lab",
        "topic": "Creating tables and querying data",
        "topic_description": "Table definitions, constraints, data changes, and filtered queries.",
        "question": "Which SQL clause filters rows before they are returned by a SELECT query?",
        "options": ["WHERE", "ORDER BY", "VALUES", "CREATE"],
        "correct": 0,
        "explanation": "WHERE applies a condition to rows selected by a query.",
        "material_type": "topic_resource",
        "material_summary": "Practice defining tables and using basic SQL data and query statements.",
        "summary_key_points": [
            "CREATE TABLE defines columns and constraints; INSERT adds records.",
            "Use SELECT and WHERE to query the intended rows.",
            "Check WHERE conditions carefully before UPDATE or DELETE.",
        ],
        "material_content": """# Database Management System Lab - Practice Guide

Use CREATE TABLE to define columns and constraints. Add records with INSERT, read them with SELECT, and use WHERE to filter results. UPDATE changes selected rows and DELETE removes selected rows, so check the WHERE condition before running either statement.

Use primary and foreign keys to represent relationships. Test queries with several records, including cases where a search returns no rows.

These are starter revision notes for the SITTTR Revision 2021 course. Confirm lab exercises with your teacher.""",
    },
    {
        "code": "3137",
        "name": "Digital Computer Fundamentals Lab",
        "topic": "Logic gates and truth tables",
        "topic_description": "Constructing truth tables and checking logic-gate outputs.",
        "question": "For an XOR gate, what is the output when both inputs are 1?",
        "options": ["0", "1", "Undefined", "Depends on the clock"],
        "correct": 0,
        "explanation": "XOR is 1 when its inputs differ; equal inputs produce 0.",
        "material_type": "topic_resource",
        "material_summary": "Use truth tables to verify basic logic-gate behavior.",
        "summary_key_points": [
            "List every input combination when constructing a truth table.",
            "XOR outputs 1 only when its two inputs differ.",
            "Compare calculated outputs with the lab circuit or simulator.",
        ],
        "material_content": """# Digital Computer Fundamentals Lab - Practice Guide

For each gate, list every possible input combination and calculate the output. AND requires both inputs to be 1; OR requires at least one input to be 1; NOT inverts a single input. XOR is 1 only when its two inputs differ.

Compare the truth table with the output from the lab circuit or simulator. Check power, wiring, and pin orientation before concluding that a component is faulty.

These are starter revision notes for the SITTTR Revision 2021 course. Confirm lab experiments with your teacher.""",
    },
    {
        "code": "3138",
        "name": "Web Technology lab",
        "topic": "HTML document structure and forms",
        "topic_description": "Semantic HTML structure, form controls, and basic page styling.",
        "question": "Which HTML element groups controls that submit user-entered data?",
        "options": ["<form>", "<table>", "<title>", "<footer>"],
        "correct": 0,
        "explanation": "The form element groups controls for submitting user data.",
        "material_type": "topic_resource",
        "material_summary": "Review the structure of an HTML page and the purpose of common form elements.",
        "summary_key_points": [
            "A basic HTML document contains doctype, html, head, and body sections.",
            "Forms group labeled controls such as input, select, and button.",
            "Use CSS for presentation and check pages at different viewport sizes.",
        ],
        "material_content": """# Web Technology Lab - Practice Guide

An HTML document has a doctype, html root, head metadata, and body content. Use headings and semantic elements to structure a page. A form groups controls such as input, label, select, and button.

CSS controls presentation. Keep content in HTML and visual rules in CSS; test the page at different viewport sizes and check that form controls have clear labels.

These are starter revision notes for the SITTTR Revision 2021 course. Confirm lab exercises with your teacher.""",
    },
    {
        "code": "3139",
        "name": "Computer System Hardware Lab",
        "topic": "Computer components and basic diagnostics",
        "topic_description": "Identifying hardware components and following a safe diagnostic process.",
        "question": "Which component temporarily stores data used by running programs?",
        "options": ["RAM", "SSD", "Power supply", "Keyboard"],
        "correct": 0,
        "explanation": "RAM is volatile working memory used by running programs.",
        "material_type": "topic_resource",
        "material_summary": "Identify common PC components and follow basic safety checks.",
        "summary_key_points": [
            "The motherboard connects the CPU, RAM, storage, and peripherals.",
            "RAM is temporary working memory; SSDs retain data without power.",
            "Disconnect power and use electrostatic precautions before handling parts.",
        ],
        "material_content": """# Computer System Hardware Lab - Practice Guide

The motherboard connects the CPU, memory, storage, and peripheral interfaces. RAM temporarily holds data used by active programs; SSDs and hard drives retain data when power is off. The power supply provides regulated power to system components.

Before handling internal parts, shut down and disconnect power, use appropriate electrostatic precautions, and follow the lab's safety instructions. Diagnose faults by checking one component or connection at a time.

These are starter revision notes for the SITTTR Revision 2021 course. Confirm lab procedures with your teacher.""",
    },
]


def seed_diploma_computer_sem3():
    db = SessionLocal()
    try:
        for item in COURSES:
            subject = db.query(Subject).filter(
                Subject.name == item["name"],
                Subject.course == COURSE,
                Subject.curriculum == CURRICULUM,
                Subject.academic_year == SEMESTER,
            ).first()
            if not subject:
                subject = Subject(
                    name=item["name"],
                    code=item["code"],
                    description=(
                        f"{REVISION} Computer Engineering course for Semester III. "
                        "Practice topic outlines and questions are starter content for teacher review."
                    ),
                    course=COURSE,
                    curriculum=CURRICULUM,
                    academic_year=SEMESTER,
                )
                db.add(subject)
                db.flush()

            topic = db.query(Topic).filter(
                Topic.subject_id == subject.id,
                Topic.name == item["topic"],
            ).first()
            if not topic:
                topic = Topic(
                    subject_id=subject.id,
                    name=item["topic"],
                    order_index=1,
                    description=item["topic_description"],
                )
                db.add(topic)
                db.flush()

            question = db.query(Question).filter(
                Question.topic_id == topic.id,
                Question.question_text == item["question"],
            ).first()
            if not question:
                db.add(Question(
                    topic_id=topic.id,
                    question_text=item["question"],
                    options=item["options"],
                    correct_answer=item["correct"],
                    explanation=item["explanation"],
                    difficulty="easy",
                ))

            material_title = f"{item['name']} - Quick Study Notes"
            material = db.query(StudyMaterial).filter(
                StudyMaterial.title == material_title,
                StudyMaterial.course == COURSE,
                StudyMaterial.curriculum == CURRICULUM,
                StudyMaterial.academic_year == SEMESTER,
            ).first()
            if not material:
                db.add(StudyMaterial(
                    title=material_title,
                    subject=item["name"],
                    topic=item["topic"],
                    course=COURSE,
                    curriculum=CURRICULUM,
                    academic_year=SEMESTER,
                    material_type=item["material_type"],
                    content=item["material_content"],
                    summary=item["material_summary"],
                    difficulty_level="easy",
                ))

            course_summary = db.query(CourseSummary).filter(
                CourseSummary.subject == item["name"],
                CourseSummary.topic == item["topic"],
                CourseSummary.course == COURSE,
                CourseSummary.curriculum == CURRICULUM,
                CourseSummary.academic_year == SEMESTER,
            ).first()
            if not course_summary:
                db.add(CourseSummary(
                    subject=item["name"],
                    course=COURSE,
                    curriculum=CURRICULUM,
                    academic_year=SEMESTER,
                    topic=item["topic"],
                    title=f"{item['name']} - Semester III Quick Summary",
                    overview=item["material_summary"],
                    key_points=item["summary_key_points"],
                    quick_revision_notes=item["material_content"],
                    quiz_questions=[{
                        "question": item["question"],
                        "options": item["options"],
                        "correct_option": item["correct"],
                        "explanation": item["explanation"],
                    }],
                    is_ai_generated=False,
                ))

        mock_test_title = "Diploma Computer Engineering Semester III Mock Test"
        mock_test = db.query(Test).filter(
            Test.title == mock_test_title,
            Test.course == COURSE,
            Test.curriculum == CURRICULUM,
            Test.academic_year == SEMESTER,
        ).first()
        if not mock_test:
            mock_test = Test(
                title=mock_test_title,
                subject=COURSE,
                course=COURSE,
                curriculum=CURRICULUM,
                academic_year=SEMESTER,
                exam_name=f"{REVISION} Semester III",
                duration_minutes=30,
                total_marks=len(COURSES),
                is_adaptive=False,
                is_published=True,
                approval_status="approved",
            )
            db.add(mock_test)
            db.flush()

        for item in COURSES:
            question = db.query(TestQuestion).filter(
                TestQuestion.test_id == mock_test.id,
                TestQuestion.question_text == item["question"],
            ).first()
            if not question:
                db.add(TestQuestion(
                    test_id=mock_test.id,
                    question_text=item["question"],
                    question_type="mcq",
                    options=item["options"],
                    correct_answer=str(item["correct"]),
                    explanation=item["explanation"],
                    topic=item["topic"],
                    difficulty="easy",
                    marks=1.0,
                ))

        db.commit()
        print(
            f"Seeded {len(COURSES)} {REVISION} Computer Engineering Semester III "
            "subjects, practice quizzes, study resources, course summaries, and one mock test."
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed_diploma_computer_sem3()
