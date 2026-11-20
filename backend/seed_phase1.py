"""
Phase 1 Seed Script — Modules 4, 5, 6
Seeds:
  - 3 roadmap stages (Science / Commerce / Humanities)
  - 9 entrance exams
  - 10 colleges
  - 12 courses across all streams
  - 6 scholarships
  - 5 study-abroad profiles
  - 8 questionnaire questions
  - 3 published tests with MCQ/TF/short-answer questions
  - 5 guidance documents (pre-indexed for chatbot RAG)
  - Sample question papers metadata
"""
import sys
import os
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal, engine, Base
from models import (
    RoadmapItem, EntranceExam, College, Course, Scholarship,
    StudyAbroadInfo, QuestionnaireQuestion,
    Test, TestQuestion,
    GuidanceDocument, DocumentEmbedding,
    QuestionPaper,
)

Base.metadata.create_all(bind=engine)
db = SessionLocal()

print("🌱 Starting Phase 1 seed...")


# ─────────────────────────────────────────────
# Skip if already seeded (idempotent)
# ─────────────────────────────────────────────
if db.query(RoadmapItem).count() > 0:
    print("⏭  Seed data already present. Skipping roadmap/exam/college seed.")
else:
    # ─────────────────────────────────────────────
    # ROADMAP ITEMS
    # ─────────────────────────────────────────────
    roadmaps = [
        RoadmapItem(
            stage="Plus Two / 12th Standard",
            stream="Science",
            title="Class 12 Science Path",
            description="Foundation for Engineering, Medical, Computer Science and Pure Science degrees.",
            options=[
                {"type": "Stream", "name": "PCM (Physics, Chemistry, Maths)", "description": "Best for Engineering / CS careers"},
                {"type": "Stream", "name": "PCB (Physics, Chemistry, Biology)", "description": "Best for Medical / Allied Health careers"},
                {"type": "Stream", "name": "PCMB (All four)", "description": "Keeps both Engineering and Medical options open"},
            ],
            next_steps=["Focus on NCERT + reference books", "Register for JEE / NEET coaching", "Aim for 75%+ in boards"],
            order_index=1,
        ),
        RoadmapItem(
            stage="Plus Two / 12th Standard",
            stream="Commerce",
            title="Class 12 Commerce Path",
            description="Foundation for CA, MBA, BBA, Economics, Law and Finance careers.",
            options=[
                {"type": "Stream", "name": "Commerce with Maths", "description": "Opens B.Com Hons, CA, Actuarial Science"},
                {"type": "Stream", "name": "Commerce without Maths", "description": "BBA, BMS, BA Economics"},
            ],
            next_steps=["Appear for CUET", "Consider CA Foundation early", "Target DU, Christ, Symbiosis"],
            order_index=2,
        ),
        RoadmapItem(
            stage="Plus Two / 12th Standard",
            stream="Humanities",
            title="Class 12 Humanities / Arts Path",
            description="Foundation for Law, Civil Services, Journalism, Psychology and Social Sciences.",
            options=[
                {"type": "Stream", "name": "History / Political Science / Economics", "description": "UPSC Civil Services base"},
                {"type": "Stream", "name": "Psychology / Sociology", "description": "Human services, counselling, NGO sectors"},
                {"type": "Stream", "name": "Fine Arts / Design", "description": "NID, NIF, Creative careers"},
            ],
            next_steps=["Appear for CLAT (Law)", "Prepare for DU / JNU entrance", "Start UPSC awareness from Class 11"],
            order_index=3,
        ),
    ]
    db.add_all(roadmaps)
    db.flush()
    print(f"  ✔ {len(roadmaps)} roadmap items")

    # ─────────────────────────────────────────────
    # ENTRANCE EXAMS
    # ─────────────────────────────────────────────
    exams = [
        EntranceExam(
            name="JEE Main", code="JEE-MAIN",
            conducting_body="National Testing Agency (NTA)",
            eligibility="10+2 with PCM. Minimum 75% aggregate (65% for SC/ST). Max 3 attempts.",
            syllabus="Physics, Chemistry, Mathematics (NCERT Class 11 & 12). JEE Main Paper 2 for Architecture.",
            exam_dates={"notification": "October–November", "exam_date": "January & April sessions", "result": "Within 2 weeks of exam"},
            application_process="Register at jeemain.nta.nic.in. Upload documents, pay fee ₹650–₹1300 depending on category.",
            preparation_tips="Focus on NCERT, practice Previous Year Questions (PYQs), mock tests from NTA. Time management is key.",
            official_website_url="https://jeemain.nta.nic.in",
            stream="Engineering",
        ),
        EntranceExam(
            name="JEE Advanced", code="JEE-ADV",
            conducting_body="IIT (rotating basis)",
            eligibility="Top 2.5 lakh JEE Main qualifiers. 10+2 with PCM. Max 2 attempts. Must be born after October 1 of the year (age limit).",
            syllabus="Advanced Physics, Chemistry, Mathematics — deeper than JEE Main. Numerical, MCQ and matrix types.",
            exam_dates={"notification": "April (after JEE Main result)", "exam_date": "May (2 papers, same day)", "result": "June"},
            application_process="Register at jeeadv.ac.in using JEE Main roll number. Category certificates required.",
            preparation_tips="Solve HC Verma, DC Pandey, NCERT Exemplar. 20+ full-length mock tests. Focus on concept clarity.",
            official_website_url="https://jeeadv.ac.in",
            stream="Engineering",
        ),
        EntranceExam(
            name="NEET-UG", code="NEET",
            conducting_body="National Testing Agency (NTA)",
            eligibility="10+2 with PCB. Minimum 50% (40% for SC/ST/OBC). No age limit now.",
            syllabus="Physics, Chemistry, Biology (Botany + Zoology) — NCERT Class 11 & 12.",
            exam_dates={"notification": "December–January", "exam_date": "May (single session)", "result": "June"},
            application_process="Register at neet.nta.nic.in. Documents: 10th/12th certificates, Aadhaar, photographs.",
            preparation_tips="NCERT is the Bible. Use NCERT Fingertips, Disha, Allen modules. Take at least 15 full mocks.",
            official_website_url="https://neet.nta.nic.in",
            stream="Health Sciences",
        ),
        EntranceExam(
            name="CUET-UG", code="CUET-UG",
            conducting_body="National Testing Agency (NTA)",
            eligibility="10+2 from any recognised board. No minimum percentage (varies by university).",
            syllabus="Domain subjects (up to 6) + General Test. Subjects chosen by candidate and university requirements.",
            exam_dates={"notification": "February", "exam_date": "May–June (computer-based)", "result": "July"},
            application_process="Register at cuet.samarth.ac.in. Choose universities + subjects. Pay ₹650–₹750.",
            preparation_tips="Check specific university syllabus. Practice from NCERT. General Test: verbal, reasoning, GK.",
            official_website_url="https://cuet.samarth.ac.in",
            stream="General / All Streams",
        ),
        EntranceExam(
            name="KEAM", code="KEAM",
            conducting_body="Commissioner for Entrance Examinations (CEE Kerala)",
            eligibility="Kerala domicile or Category D. 10+2 with PCM (Engineering) or PCB (Pharmacy). Min 50% aggregate.",
            syllabus="Physics, Chemistry, Mathematics (Engineering). Biology instead of Maths for Pharmacy.",
            exam_dates={"notification": "January–February", "exam_date": "April", "result": "May–June"},
            application_process="cee.kerala.gov.in. Documents: bonafide, domicile, community certificate.",
            preparation_tips="Kerala State Board SCERT + NCERT. Solve past 10 years KEAM papers. Physics and Chemistry carry more weight.",
            official_website_url="https://cee.kerala.gov.in",
            stream="Engineering",
        ),
        EntranceExam(
            name="CLAT", code="CLAT",
            conducting_body="Consortium of National Law Universities",
            eligibility="10+2 from any stream. Minimum 45% (40% for SC/ST). Age limit 20 years (22 for SC/ST).",
            syllabus="English Language, Current Affairs & GK, Legal Reasoning, Logical Reasoning, Quantitative Techniques.",
            exam_dates={"notification": "September", "exam_date": "December", "result": "December–January"},
            application_process="consortiumofnlus.ac.in. Online application, documents upload, fee ₹4000.",
            preparation_tips="Read newspapers daily (The Hindu). Study Indian Constitution basics. Solve at least 30 mocks.",
            official_website_url="https://consortiumofnlus.ac.in",
            stream="Law",
        ),
        EntranceExam(
            name="GATE", code="GATE",
            conducting_body="IITs + IISc (rotating)",
            eligibility="B.E./B.Tech/B.Sc/M.Sc or final year students. No age limit.",
            syllabus="29 papers covering Engineering, Science and Humanities disciplines. Subject-specific + GA section.",
            exam_dates={"notification": "September", "exam_date": "February (3 weekends)", "result": "March"},
            application_process="gate.iitb.ac.in (or respective IIT). Online, documents, fee ₹1800–₹2400.",
            preparation_tips="Standard textbooks + NPTEL lectures. 6-month intensive preparation. Previous year GATE papers are essential.",
            official_website_url="https://gate2025.iitr.ac.in",
            stream="Engineering / Science",
        ),
        EntranceExam(
            name="CAT", code="CAT",
            conducting_body="IIMs (rotating)",
            eligibility="Bachelor's degree with min 50% (45% SC/ST). Final year students can apply.",
            syllabus="Verbal Ability & Reading Comprehension (VARC), Data Interpretation & Logical Reasoning (DILR), Quantitative Aptitude (QA).",
            exam_dates={"notification": "July–August", "exam_date": "November", "result": "January"},
            application_process="iimcat.ac.in. Online registration, fee ₹2300. Upload graduation certificates.",
            preparation_tips="Time management crucial — 2 hours for 3 sections. Enroll in coaching or use Arun Sharma books.",
            official_website_url="https://iimcat.ac.in",
            stream="Management / MBA",
        ),
        EntranceExam(
            name="NATA", code="NATA",
            conducting_body="Council of Architecture (CoA)",
            eligibility="10+2 with Maths. Minimum 50% aggregate. No upper age limit.",
            syllabus="Drawing, Aesthetic Sensitivity, Critical Thinking (mathematical reasoning, visual perception, general aptitude).",
            exam_dates={"notification": "December–January", "exam_date": "2 attempts: April and July", "result": "Within 2 weeks of exam"},
            application_process="nata.in. Online, fee ₹2000 per attempt. Documents: 10th certificate, photos.",
            preparation_tips="Practice freehand drawing, 3D visualisation. Study history of art and architecture. Take both attempts for better score.",
            official_website_url="https://nata.in",
            stream="Design / Architecture",
        ),
    ]
    db.add_all(exams)
    db.flush()
    print(f"  ✔ {len(exams)} entrance exams")

    # ─────────────────────────────────────────────
    # COLLEGES
    # ─────────────────────────────────────────────
    colleges = [
        College(name="IIT Bombay", location="Mumbai, Maharashtra", state="Maharashtra",
                college_type="Institute of National Importance", nirf_ranking=3,
                courses_offered=["B.Tech", "M.Tech", "M.Sc", "PhD", "MBA (SJMSOM)"],
                admission_process="JEE Advanced (B.Tech), GATE (M.Tech), JAM (M.Sc)", website_url="https://www.iitb.ac.in",
                average_annual_fee="₹2.5 Lakh", established_year=1958),
        College(name="IIT Delhi", location="New Delhi", state="Delhi",
                college_type="Institute of National Importance", nirf_ranking=2,
                courses_offered=["B.Tech", "M.Tech", "PhD", "M.Sc (5-yr Integrated)"],
                admission_process="JEE Advanced (B.Tech), GATE (M.Tech)", website_url="https://home.iitd.ac.in",
                average_annual_fee="₹2.3 Lakh", established_year=1961),
        College(name="AIIMS New Delhi", location="New Delhi", state="Delhi",
                college_type="Institute of National Importance", nirf_ranking=1,
                courses_offered=["MBBS", "MD", "MS", "PhD", "B.Sc Nursing"],
                admission_process="NEET-UG (MBBS), NEET-PG / AIIMS PG (Postgraduate)", website_url="https://www.aiims.edu",
                average_annual_fee="₹5,000 (Govt funded)", established_year=1956),
        College(name="NIT Trichy", location="Tiruchirappalli, Tamil Nadu", state="Tamil Nadu",
                college_type="Institute of National Importance", nirf_ranking=9,
                courses_offered=["B.Tech", "M.Tech", "M.Sc", "MBA", "PhD"],
                admission_process="JEE Main (B.Tech), GATE / CCMT (M.Tech)", website_url="https://www.nitt.edu",
                average_annual_fee="₹1.5 Lakh", established_year=1964),
        College(name="Delhi University (DU)", location="New Delhi", state="Delhi",
                college_type="Central University", nirf_ranking=11,
                courses_offered=["B.A.", "B.Sc", "B.Com", "LLB", "M.A.", "MBA", "PhD"],
                admission_process="CUET-UG (Undergraduate)", website_url="https://www.du.ac.in",
                average_annual_fee="₹25,000–₹1.5 Lakh", established_year=1922),
        College(name="Christ University", location="Bengaluru, Karnataka", state="Karnataka",
                college_type="Deemed University", nirf_ranking=48,
                courses_offered=["BBA", "B.Com", "BCA", "B.Sc", "MBA", "MCA", "Law"],
                admission_process="Entrance exam + Interview (Christ University Entrance Test)", website_url="https://christuniversity.in",
                average_annual_fee="₹1.5–₹3 Lakh", established_year=1969),
        College(name="IIM Ahmedabad", location="Ahmedabad, Gujarat", state="Gujarat",
                college_type="Institute of National Importance", nirf_ranking=1,
                courses_offered=["MBA (PGP)", "PGPX", "PhD", "Executive MBA"],
                admission_process="CAT + Personal Interview + Writing Ability Test", website_url="https://www.iima.ac.in",
                average_annual_fee="₹28 Lakh (Full PGP)", established_year=1961),
        College(name="National Law School of India University (NLSIU)", location="Bengaluru", state="Karnataka",
                college_type="Deemed University", nirf_ranking=1,
                courses_offered=["B.A. LLB (Hons)", "LLM", "PhD"],
                admission_process="CLAT (Undergraduate)", website_url="https://nls.ac.in",
                average_annual_fee="₹2.5 Lakh", established_year=1987),
        College(name="National Institute of Design (NID)", location="Ahmedabad, Gujarat", state="Gujarat",
                college_type="Institute of National Importance", nirf_ranking=1,
                courses_offered=["B.Des", "M.Des", "PhD"],
                admission_process="NID DAT (Design Aptitude Test)", website_url="https://www.nid.edu",
                average_annual_fee="₹2 Lakh", established_year=1961),
        College(name="University of Calicut", location="Malappuram, Kerala", state="Kerala",
                college_type="State University", nirf_ranking=None,
                courses_offered=["B.Sc", "B.A.", "B.Com", "B.Tech (affiliated colleges)", "M.Sc", "MA", "PhD"],
                admission_process="Kerala CEE / CUET / Direct merit-based for most UG programs", website_url="https://www.uoc.ac.in",
                average_annual_fee="₹10,000–₹50,000", established_year=1968),
    ]
    db.add_all(colleges)
    db.flush()
    print(f"  ✔ {len(colleges)} colleges")

    # ─────────────────────────────────────────────
    # COURSES
    # ─────────────────────────────────────────────
    courses = [
        Course(title="B.Tech Computer Science & Engineering", stream="Engineering", degree_level="Undergraduate",
               duration_years=4.0,
               eligibility="10+2 with PCM. Min 75% aggregate. JEE Main/Advanced or state CET.",
               exams=["JEE Main", "JEE Advanced", "KEAM", "KCET", "MHT-CET"],
               fee_range="₹1–₹10 Lakh/year",
               skills_needed=["Mathematics", "Logical Reasoning", "Problem Solving", "Programming Basics"],
               job_roles=["Software Engineer", "Data Scientist", "ML Engineer", "DevOps Engineer", "Product Manager"],
               salary_range="₹6–₹40 LPA (fresher–mid level)",
               scope="Highest growth sector. Cloud, AI, Cybersecurity dominate hiring.",
               top_colleges=["IIT Bombay", "IIT Delhi", "NIT Trichy", "BITS Pilani", "VIT Vellore"]),
        Course(title="B.Tech Electronics & Communication Engineering", stream="Engineering", degree_level="Undergraduate",
               duration_years=4.0,
               eligibility="10+2 with PCM. JEE Main or state CET.",
               exams=["JEE Main", "KEAM", "KCET", "AP EAMCET"],
               fee_range="₹80K–₹8 Lakh/year",
               skills_needed=["Physics", "Mathematics", "Signal Processing Concepts"],
               job_roles=["VLSI Engineer", "Embedded Systems Engineer", "Telecom Engineer", "ISRO/DRDO Scientist"],
               salary_range="₹5–₹25 LPA",
               scope="VLSI, 5G, IoT, Space tech growing rapidly.",
               top_colleges=["IIT Kharagpur", "NIT Calicut", "BITS Goa"]),
        Course(title="MBBS", stream="Health Sciences", degree_level="Undergraduate",
               duration_years=5.5,
               eligibility="10+2 with PCB. NEET-UG score. Min 50% in PCB.",
               exams=["NEET-UG"],
               fee_range="Govt: ₹50K/year | Private: ₹10–₹25 Lakh/year",
               skills_needed=["Biology", "Chemistry", "Empathy", "Dedication"],
               job_roles=["General Physician", "Specialist Doctor", "Surgeon", "Public Health Officer", "Medical Researcher"],
               salary_range="₹8–₹60 LPA (specialisation dependent)",
               scope="Always in demand. Specialisations (MD/MS) multiply earning potential.",
               top_colleges=["AIIMS New Delhi", "CMC Vellore", "JIPMER Puducherry"]),
        Course(title="B.Sc Computer Science", stream="Computer Applications", degree_level="Undergraduate",
               duration_years=3.0,
               eligibility="10+2 from any stream. Many colleges accept non-Science students.",
               exams=["CUET", "University entrance test", "Direct merit-based"],
               fee_range="₹30K–₹2 Lakh/year",
               skills_needed=["Mathematics", "Logical Thinking", "Interest in Technology"],
               job_roles=["Software Developer", "Web Developer", "Database Admin", "IT Analyst"],
               salary_range="₹3–₹12 LPA",
               scope="Good foundation for MCA or M.Sc CS with better career prospects.",
               top_colleges=["Delhi University", "Christ University", "Loyola College Chennai"]),
        Course(title="BCA (Bachelor of Computer Applications)", stream="Computer Applications", degree_level="Undergraduate",
               duration_years=3.0,
               eligibility="10+2 from any stream. Maths at 10+2 preferred but not always mandatory.",
               exams=["University entrance test", "Direct merit-based", "CUET"],
               fee_range="₹30K–₹1.5 Lakh/year",
               skills_needed=["Logical Thinking", "Basic Maths", "Interest in IT"],
               job_roles=["Software Developer", "Web Designer", "App Developer", "IT Support"],
               salary_range="₹3–₹10 LPA",
               scope="Gateway to MCA. Many lateral entry M.Tech programs also accept BCA.",
               top_colleges=["Symbiosis Pune", "Christ University", "Manipal University"]),
        Course(title="B.Sc Physics", stream="Science", degree_level="Undergraduate",
               duration_years=3.0,
               eligibility="10+2 with Physics and Maths. Min 50–60% depending on institution.",
               exams=["CUET", "JAM (for IITs)", "University entrance"],
               fee_range="₹10K–₹1.5 Lakh/year",
               skills_needed=["Physics", "Mathematics", "Analytical Thinking"],
               job_roles=["Physicist (R&D)", "ISRO Scientist", "Radiation Safety Officer", "Data Analyst", "Teaching"],
               salary_range="₹4–₹20 LPA (varies widely by role)",
               scope="ISRO, DAE, DRDO hiring. Physics + CS combination is powerful.",
               top_colleges=["IISc Bangalore", "St. Stephen's Delhi", "Presidency Kolkata"]),
        Course(title="B.Com (Bachelor of Commerce)", stream="Commerce", degree_level="Undergraduate",
               duration_years=3.0,
               eligibility="10+2 with Commerce. Min 45–60% aggregate.",
               exams=["CUET", "DU entrance", "University merit-based"],
               fee_range="₹10K–₹1 Lakh/year",
               skills_needed=["Accountancy", "Economics", "Mathematics (basic)"],
               job_roles=["Accountant", "CA (after ICAI exams)", "Financial Analyst", "Banking Officer", "Tax Consultant"],
               salary_range="₹3–₹20 LPA (CA can go much higher)",
               scope="Always in demand. CA + B.Com is a golden combination.",
               top_colleges=["Shri Ram College Delhi", "St. Xavier's Mumbai", "Christ University"]),
        Course(title="B.A. Economics", stream="Humanities", degree_level="Undergraduate",
               duration_years=3.0,
               eligibility="10+2 from any stream. Maths at 10+2 is an advantage.",
               exams=["CUET", "DU entrance", "University entrance"],
               fee_range="₹10K–₹80K/year",
               skills_needed=["Mathematics", "Analytical Thinking", "Statistics Basics"],
               job_roles=["Economist", "Policy Analyst", "Investment Banker", "Data Analyst", "UPSC/IES"],
               salary_range="₹4–₹25 LPA",
               scope="Economics + Data Science is a hot combination. Good for UPSC/IES preparation.",
               top_colleges=["Delhi School of Economics", "St. Stephen's", "Presidency College"]),
        Course(title="B.A. LLB (Integrated Law)", stream="Law", degree_level="Undergraduate",
               duration_years=5.0,
               eligibility="10+2 from any stream. Max 20 years of age for CLAT (22 for SC/ST).",
               exams=["CLAT", "AILET", "LSAT India", "MH-CET Law"],
               fee_range="₹1–₹5 Lakh/year",
               skills_needed=["Reading Comprehension", "Logical Reasoning", "GK & Current Affairs"],
               job_roles=["Advocate", "Corporate Lawyer", "Judicial Officer", "Legal Analyst", "Policy Researcher"],
               salary_range="₹5–₹50 LPA (highly variable)",
               scope="High demand in corporate, tech, and IP law. Judiciary is always a stable path.",
               top_colleges=["NLSIU Bangalore", "NALSAR Hyderabad", "NLU Delhi"]),
        Course(title="B.Des (Bachelor of Design)", stream="Design", degree_level="Undergraduate",
               duration_years=4.0,
               eligibility="10+2 from any stream. NATA or NID DAT score.",
               exams=["NATA", "NID DAT", "UCEED (IITs)", "CEED (IITs for M.Des)"],
               fee_range="₹1.5–₹5 Lakh/year",
               skills_needed=["Creative Thinking", "Drawing", "Aesthetic Sense", "3D Visualisation"],
               job_roles=["UI/UX Designer", "Product Designer", "Graphic Designer", "Film Art Director", "Architect"],
               salary_range="₹5–₹30 LPA",
               scope="UX/UI design is booming with startup culture. Film, Metaverse and game design growing fast.",
               top_colleges=["NID Ahmedabad", "NID Delhi", "IDC IIT Bombay", "Pearl Academy"]),
        Course(title="MBA (Master of Business Administration)", stream="Management", degree_level="Postgraduate",
               duration_years=2.0,
               eligibility="Any bachelor's degree with min 50%. Work experience preferred for top IIMs.",
               exams=["CAT", "XAT", "GMAT", "MAT", "SNAP"],
               fee_range="₹5–₹30 Lakh (total)",
               skills_needed=["Communication", "Leadership", "Quantitative Aptitude", "Data Interpretation"],
               job_roles=["Management Consultant", "Marketing Manager", "Financial Analyst", "Entrepreneur", "HR Manager"],
               salary_range="₹10–₹50 LPA",
               scope="Evergreen demand. Finance and Tech MBA (FinTech, Product) are highest paying.",
               top_colleges=["IIM Ahmedabad", "IIM Bangalore", "ISB Hyderabad", "XLRI Jamshedpur"]),
        Course(title="M.Sc Data Science", stream="Computer Applications", degree_level="Postgraduate",
               duration_years=2.0,
               eligibility="B.Sc / B.Tech in any STEM field. Some programs accept B.Com with Maths.",
               exams=["CUET-PG", "University entrance test", "GATE (CS/Statistics)"],
               fee_range="₹1–₹5 Lakh/year",
               skills_needed=["Statistics", "Python / R Programming", "Mathematics", "Machine Learning Basics"],
               job_roles=["Data Scientist", "ML Engineer", "AI Researcher", "Business Intelligence Analyst"],
               salary_range="₹8–₹35 LPA",
               scope="One of the fastest growing fields. AI/ML demand expected to triple by 2030.",
               top_colleges=["IIT Madras", "IIIT Hyderabad", "ISI Kolkata", "Manipal Academy"]),
    ]
    db.add_all(courses)
    db.flush()
    print(f"  ✔ {len(courses)} courses")

    # ─────────────────────────────────────────────
    # SCHOLARSHIPS
    # ─────────────────────────────────────────────
    scholarships = [
        Scholarship(name="National Merit Scholarship", provider="Ministry of Education, India",
                    eligibility="Top 1% students in Class 10 board exams. Family income < ₹1.5 Lakh/year.",
                    amount_and_benefits="₹12,000/year for Class 11–12; ₹24,000/year for UG/PG",
                    deadline_description="August–September each year",
                    application_process="Apply through National Scholarship Portal (scholarships.gov.in). Upload income certificate, marksheet.",
                    application_url="https://scholarships.gov.in", category="Merit"),
        Scholarship(name="INSPIRE Scholarship (DST)", provider="Department of Science & Technology",
                    eligibility="Top 1% in Class 12 Science stream. Enrolled in B.Sc / M.Sc in Natural Sciences.",
                    amount_and_benefits="₹80,000/year (₹60K scholarship + ₹20K summer attachment)",
                    deadline_description="September–October",
                    application_process="Online at online-inspire.gov.in. Submit marks, enrollment proof, bank details.",
                    application_url="https://online-inspire.gov.in", category="Merit"),
        Scholarship(name="Post-Matric Scholarship (SC/ST/OBC)", provider="Ministry of Social Justice",
                    eligibility="SC/ST/OBC students. Family income < ₹2.5 Lakh/year. Enrolled in Class 11+ or higher education.",
                    amount_and_benefits="Maintenance allowance + tuition fee reimbursement (varies by state)",
                    deadline_description="October–November",
                    application_process="State portal or scholarships.gov.in. Documents: caste certificate, income certificate, fee receipts.",
                    application_url="https://scholarships.gov.in", category="Need-based"),
        Scholarship(name="KVPY (Kishore Vaigyanik Protsahan Yojana)", provider="Indian Institute of Science (IISc)",
                    eligibility="Class 11 / 12 / 1st year UG Science students. Merit-based aptitude test + interview.",
                    amount_and_benefits="₹5,000–₹7,000/month fellowship + annual contingency grant",
                    deadline_description="August",
                    application_process="kvpy.iisc.ernet.in. National aptitude test + interview round.",
                    application_url="https://kvpy.iisc.ac.in", category="Merit"),
        Scholarship(name="Sitaram Jindal Foundation Scholarship", provider="Sitaram Jindal Foundation",
                    eligibility="Students from financially weak families. Studying in Class 10–PG in any stream.",
                    amount_and_benefits="₹500–₹2,000/month depending on level and merit",
                    deadline_description="May–June (varies by state)",
                    application_process="sitaramjindalfoundation.org. Send application with income proof and marksheets by post/online.",
                    application_url="https://sitaramjindalfoundation.org", category="Need-based"),
        Scholarship(name="Vidyadhan Scholarship (Sarojini Damodaran Foundation)", provider="Sarojini Damodaran Foundation",
                    eligibility="Class 12 to UG students in Kerala, Tamil Nadu and other states. Family income < ₹2 Lakh/year.",
                    amount_and_benefits="₹10,000–₹30,000/year",
                    deadline_description="June–July",
                    application_process="vidyadhan.org. Online application with income and academic documents.",
                    application_url="https://www.vidyadhan.org", category="Need-based"),
    ]
    db.add_all(scholarships)
    db.flush()
    print(f"  ✔ {len(scholarships)} scholarships")

    # ─────────────────────────────────────────────
    # STUDY ABROAD
    # ─────────────────────────────────────────────
    study_abroad = [
        StudyAbroadInfo(country="United States of America", flag_emoji="🇺🇸",
                        popular_courses=["Computer Science", "Data Science", "MBA", "Engineering", "Public Health"],
                        required_tests=["SAT / ACT (UG)", "GRE / GMAT (PG)", "IELTS / TOEFL (English)"],
                        avg_tuition_cost="$25,000–$60,000/year",
                        living_cost="$12,000–$20,000/year",
                        visa_work_rights="F-1 Student Visa. CPT during studies + 1-year OPT (3-year STEM OPT extension for STEM fields).",
                        intake_timelines={"Fall (Primary)": "August/September", "Spring": "January", "Application Deadline": "November–January for Fall"}),
        StudyAbroadInfo(country="United Kingdom", flag_emoji="🇬🇧",
                        popular_courses=["Finance", "Law", "Medicine", "Engineering", "Design", "MBA"],
                        required_tests=["IELTS (min 6.0–7.0)", "UKCAT/BMAT (Medicine)", "GRE (some PG programs)"],
                        avg_tuition_cost="£15,000–£35,000/year",
                        living_cost="£9,000–£15,000/year",
                        visa_work_rights="Student Visa (Tier 4). 20 hrs/week work during term. Graduate Route Visa: 2-year post-study work (3-year for PhD).",
                        intake_timelines={"September (Main)": "September/October", "January": "January intake (limited courses)", "UCAS Deadline": "January 25 for most courses"}),
        StudyAbroadInfo(country="Germany", flag_emoji="🇩🇪",
                        popular_courses=["Engineering", "Natural Sciences", "Computer Science", "Business", "Architecture"],
                        required_tests=["TestDaF / IELTS (Language)", "GRE (some programs)", "APS Certificate (Indian students)"],
                        avg_tuition_cost="€0–€3,000/semester (mostly public university tuition-free)",
                        living_cost="€700–€1,200/month",
                        visa_work_rights="Student Visa allows 120 full days / 240 half-days work per year. Post-study: 18-month job-search visa.",
                        intake_timelines={"Winter Semester": "October", "Summer Semester": "April", "Application Deadline": "June for Winter, December for Summer"}),
        StudyAbroadInfo(country="Canada", flag_emoji="🇨🇦",
                        popular_courses=["Computer Science", "Business", "Engineering", "Healthcare", "Data Science"],
                        required_tests=["IELTS (min 6.0)", "GMAT / GRE (PG management)", "SAT (some UG)"],
                        avg_tuition_cost="CAD 20,000–50,000/year",
                        living_cost="CAD 10,000–15,000/year",
                        visa_work_rights="Study Permit. 20 hrs/week off-campus work. 3-year PGWP for 3-year programs. Path to PR via Express Entry.",
                        intake_timelines={"September (Fall)": "September", "January (Winter)": "January", "May (Summer, limited)": "May"}),
        StudyAbroadInfo(country="Australia", flag_emoji="🇦🇺",
                        popular_courses=["Engineering", "Nursing", "Business", "Education", "Environmental Science"],
                        required_tests=["IELTS (min 6.0–6.5)", "PTE", "GRE (some programs)"],
                        avg_tuition_cost="AUD 25,000–45,000/year",
                        living_cost="AUD 15,000–22,000/year",
                        visa_work_rights="Student Visa (Subclass 500). Unlimited work hours for student visa holders (since 2023). 2–4 year Temporary Graduate Visa post-study.",
                        intake_timelines={"February (Semester 1)": "February", "July (Semester 2)": "July", "Application Deadline": "October for February; April for July"}),
    ]
    db.add_all(study_abroad)
    db.flush()
    print(f"  ✔ {len(study_abroad)} study abroad profiles")

    # ─────────────────────────────────────────────
    # QUESTIONNAIRE QUESTIONS
    # ─────────────────────────────────────────────
    questionnaire = [
        QuestionnaireQuestion(
            question_text="Which subjects do you enjoy studying the most?",
            category="Subject Preference", order_index=1,
            options=[
                {"text": "Mathematics and Physics", "stream_weights": {"Engineering": 2.0, "Computer Applications": 1.5, "Science": 1.0}},
                {"text": "Biology and Chemistry", "stream_weights": {"Health Sciences": 2.0, "Science": 1.5}},
                {"text": "History, Political Science and Literature", "stream_weights": {"Humanities": 2.0, "Law": 1.0}},
                {"text": "Accountancy, Economics and Business Studies", "stream_weights": {"Commerce": 2.0, "Management": 1.0}},
                {"text": "Computer Science and Programming", "stream_weights": {"Computer Applications": 2.5, "Engineering": 1.0}},
                {"text": "Drawing, Art and Design", "stream_weights": {"Design": 2.5}},
            ]
        ),
        QuestionnaireQuestion(
            question_text="What type of work environment excites you?",
            category="Work Style", order_index=2,
            options=[
                {"text": "Laboratory or research settings", "stream_weights": {"Science": 2.0, "Health Sciences": 1.0, "Engineering": 1.0}},
                {"text": "Office / corporate environment", "stream_weights": {"Management": 2.0, "Commerce": 1.5}},
                {"text": "Courtroom, advocacy or public service", "stream_weights": {"Law": 2.5, "Humanities": 1.0}},
                {"text": "Hospitals or clinical settings", "stream_weights": {"Health Sciences": 2.5}},
                {"text": "Creative studio or design firm", "stream_weights": {"Design": 2.5}},
                {"text": "Tech startup or software company", "stream_weights": {"Computer Applications": 2.5, "Engineering": 1.5}},
            ]
        ),
        QuestionnaireQuestion(
            question_text="How do you prefer to solve problems?",
            category="Aptitude", order_index=3,
            options=[
                {"text": "Using logic, formulas and calculations", "stream_weights": {"Engineering": 2.0, "Science": 1.5, "Computer Applications": 1.5}},
                {"text": "Understanding people and social situations", "stream_weights": {"Humanities": 2.0, "Management": 1.0, "Law": 1.0}},
                {"text": "Creative and visual thinking", "stream_weights": {"Design": 2.5}},
                {"text": "Analysing data and financial figures", "stream_weights": {"Commerce": 2.0, "Management": 1.5}},
                {"text": "Following scientific method and experimentation", "stream_weights": {"Science": 2.5, "Health Sciences": 1.5}},
            ]
        ),
        QuestionnaireQuestion(
            question_text="Which career outcome matters most to you?",
            category="Interest", order_index=4,
            options=[
                {"text": "High salary and financial growth", "stream_weights": {"Engineering": 1.5, "Management": 2.0, "Computer Applications": 1.5}},
                {"text": "Helping and healing people", "stream_weights": {"Health Sciences": 2.5, "Humanities": 1.0}},
                {"text": "Creating things — products, software, art", "stream_weights": {"Engineering": 1.5, "Computer Applications": 1.5, "Design": 2.0}},
                {"text": "Justice, rights and policy", "stream_weights": {"Law": 2.5, "Humanities": 1.5}},
                {"text": "Research and discovering new knowledge", "stream_weights": {"Science": 2.5, "Engineering": 1.0}},
                {"text": "Running my own business", "stream_weights": {"Management": 2.5, "Commerce": 1.5}},
            ]
        ),
        QuestionnaireQuestion(
            question_text="Are you comfortable with extended study duration (5+ years)?",
            category="Work Style", order_index=5,
            options=[
                {"text": "Yes, I am committed to any duration needed", "stream_weights": {"Health Sciences": 1.5, "Law": 1.5, "Engineering": 0.5}},
                {"text": "Prefer 3–4 year programs", "stream_weights": {"Science": 1.0, "Commerce": 1.0, "Computer Applications": 1.0}},
                {"text": "Prefer to start earning quickly (2–3 year diploma / degree)", "stream_weights": {"Commerce": 1.5, "Design": 1.0}},
            ]
        ),
        QuestionnaireQuestion(
            question_text="What is your proficiency in Mathematics?",
            category="Subject Preference", order_index=6,
            options=[
                {"text": "Excellent — I love solving complex problems", "stream_weights": {"Engineering": 2.0, "Computer Applications": 1.5, "Science": 1.5, "Management": 1.0}},
                {"text": "Good — I am comfortable with standard syllabus", "stream_weights": {"Commerce": 1.0, "Science": 1.0}},
                {"text": "Average — I manage but it's not my strength", "stream_weights": {"Humanities": 1.0, "Design": 1.0}},
                {"text": "Weak — I prefer subjects without heavy maths", "stream_weights": {"Law": 1.5, "Humanities": 1.5}},
            ]
        ),
        QuestionnaireQuestion(
            question_text="Are you interested in government sector jobs or civil services?",
            category="Interest", order_index=7,
            options=[
                {"text": "Yes, UPSC / State PSC is my goal", "stream_weights": {"Humanities": 2.5, "Law": 1.0}},
                {"text": "PSU (Public Sector Undertaking) through GATE", "stream_weights": {"Engineering": 2.0}},
                {"text": "Banking / SSC / Government Finance jobs", "stream_weights": {"Commerce": 2.0}},
                {"text": "No, I prefer private sector or entrepreneurship", "stream_weights": {"Computer Applications": 1.0, "Management": 1.0, "Design": 1.0}},
            ]
        ),
        QuestionnaireQuestion(
            question_text="How important is studying abroad for your career plans?",
            category="Interest", order_index=8,
            options=[
                {"text": "Very important — I plan to pursue higher studies abroad", "stream_weights": {"Engineering": 1.0, "Management": 1.0, "Science": 1.5, "Computer Applications": 1.0}},
                {"text": "Somewhat — if I get a scholarship", "stream_weights": {"Health Sciences": 0.5, "Law": 0.5}},
                {"text": "Not important — I want to stay in India", "stream_weights": {"Humanities": 0.5, "Commerce": 0.5}},
            ]
        ),
    ]
    db.add_all(questionnaire)
    db.flush()
    print(f"  ✔ {len(questionnaire)} questionnaire questions")

    db.commit()
    print("  ✔ Core guidance data committed.")


# ─────────────────────────────────────────────
# TESTS (Module 5) — seed if not present
# ─────────────────────────────────────────────
if db.query(Test).count() > 0:
    print("⏭  Tests already seeded. Skipping.")
else:
    # Biology Test
    bio_test = Test(title="Biology Chapter Test – Cell Biology & Genetics",
                    subject="Biology", exam_name="NEET-UG", duration_minutes=25, total_marks=15, is_published=True)
    db.add(bio_test)
    db.flush()
    bio_questions = [
        TestQuestion(test_id=bio_test.id, question_text="The powerhouse of the cell is:",
                     question_type="mcq", options=["Nucleus", "Ribosome", "Mitochondria", "Chloroplast"],
                     correct_answer="2", explanation="Mitochondria produce ATP via cellular respiration.",
                     topic="Cell Biology", difficulty="easy", marks=1.0),
        TestQuestion(test_id=bio_test.id, question_text="DNA stands for Deoxyribonucleic Acid.",
                     question_type="true_false", options=["True", "False"],
                     correct_answer="0", explanation="DNA = Deoxyribonucleic Acid — the genetic material.",
                     topic="Genetics", difficulty="easy", marks=1.0),
        TestQuestion(test_id=bio_test.id, question_text="Which law states that alleles segregate during gamete formation?",
                     question_type="mcq", options=["Law of Independent Assortment", "Law of Segregation", "Hardy-Weinberg Law", "Law of Dominance"],
                     correct_answer="1", explanation="Mendel's Law of Segregation.",
                     topic="Genetics", difficulty="medium", marks=2.0),
        TestQuestion(test_id=bio_test.id, question_text="Name the organelle responsible for protein synthesis.",
                     question_type="short_answer", options=None,
                     correct_answer="ribosome", explanation="Ribosomes translate mRNA into proteins.",
                     topic="Cell Biology", difficulty="easy", marks=1.0),
        TestQuestion(test_id=bio_test.id, question_text="The process of cell division that produces genetically identical daughter cells is:",
                     question_type="mcq", options=["Meiosis", "Mitosis", "Binary fission", "Budding"],
                     correct_answer="1", explanation="Mitosis produces 2 identical diploid daughter cells.",
                     topic="Cell Division", difficulty="medium", marks=2.0),
        TestQuestion(test_id=bio_test.id, question_text="In a monohybrid cross between Tt × Tt, what is the phenotypic ratio in F2?",
                     question_type="mcq", options=["1:2:1", "3:1", "1:1", "9:3:3:1"],
                     correct_answer="1", explanation="3 Tall : 1 dwarf (3:1 phenotypic ratio).",
                     topic="Genetics", difficulty="difficult", marks=3.0),
        TestQuestion(test_id=bio_test.id, question_text="Meiosis occurs in somatic cells.",
                     question_type="true_false", options=["True", "False"],
                     correct_answer="1", explanation="Meiosis occurs in reproductive cells (germline). Somatic cells undergo mitosis.",
                     topic="Cell Division", difficulty="medium", marks=2.0),
        TestQuestion(test_id=bio_test.id, question_text="Which base pairs with Adenine in DNA?",
                     question_type="short_answer", options=None,
                     correct_answer="thymine", explanation="A pairs with T (2 hydrogen bonds) in DNA.",
                     topic="Genetics", difficulty="easy", marks=1.0),
    ]
    db.add_all(bio_questions)

    # Mathematics Test
    math_test = Test(title="Mathematics Test – Calculus & Algebra",
                     subject="Mathematics", exam_name="JEE Main", duration_minutes=30, total_marks=20, is_published=True)
    db.add(math_test)
    db.flush()
    math_questions = [
        TestQuestion(test_id=math_test.id, question_text="What is the derivative of sin(x)?",
                     question_type="mcq", options=["-cos(x)", "cos(x)", "-sin(x)", "tan(x)"],
                     correct_answer="1", explanation="d/dx(sin x) = cos x",
                     topic="Calculus", difficulty="easy", marks=1.0),
        TestQuestion(test_id=math_test.id, question_text="The sum of an infinite geometric series with first term a and ratio r (|r|<1) is a/(1-r).",
                     question_type="true_false", options=["True", "False"],
                     correct_answer="0", explanation="S∞ = a / (1 - r) for |r| < 1.",
                     topic="Algebra", difficulty="medium", marks=2.0),
        TestQuestion(test_id=math_test.id, question_text="If f(x) = x³ - 3x, find f'(x).",
                     question_type="mcq", options=["3x² - 3", "x² - 3", "3x² + 3", "3x - 3"],
                     correct_answer="0", explanation="f'(x) = 3x² - 3 by power rule.",
                     topic="Calculus", difficulty="easy", marks=1.0),
        TestQuestion(test_id=math_test.id, question_text="What is the value of ∫₀¹ x² dx?",
                     question_type="mcq", options=["1/2", "1/3", "1/4", "2/3"],
                     correct_answer="1", explanation="∫₀¹ x² dx = [x³/3]₀¹ = 1/3.",
                     topic="Calculus", difficulty="medium", marks=2.0),
        TestQuestion(test_id=math_test.id, question_text="Solve: 2x² - 5x + 2 = 0. What are the roots?",
                     question_type="mcq", options=["x = 1/2, 2", "x = -1/2, -2", "x = 1, 2", "x = 2, 3"],
                     correct_answer="0", explanation="Factor: (2x-1)(x-2)=0 → x=1/2 or x=2.",
                     topic="Algebra", difficulty="medium", marks=2.0),
        TestQuestion(test_id=math_test.id, question_text="Name the rule used to differentiate a product of two functions.",
                     question_type="short_answer", options=None,
                     correct_answer="product rule", explanation="Product Rule: d/dx[u·v] = u'v + uv'",
                     topic="Calculus", difficulty="easy", marks=1.0),
        TestQuestion(test_id=math_test.id, question_text="A matrix A is invertible if and only if det(A) ≠ 0.",
                     question_type="true_false", options=["True", "False"],
                     correct_answer="0", explanation="det(A) ≠ 0 is the condition for invertibility.",
                     topic="Matrices", difficulty="medium", marks=2.0),
        TestQuestion(test_id=math_test.id, question_text="Find the number of ways to arrange 5 different books on a shelf.",
                     question_type="mcq", options=["25", "120", "60", "100"],
                     correct_answer="1", explanation="5! = 120 permutations.",
                     topic="Permutations & Combinations", difficulty="medium", marks=2.0),
        TestQuestion(test_id=math_test.id, question_text="What is the limit of (sin x)/x as x approaches 0?",
                     question_type="mcq", options=["0", "∞", "1", "-1"],
                     correct_answer="2", explanation="Standard limit: lim(x→0) sin(x)/x = 1.",
                     topic="Calculus", difficulty="difficult", marks=3.0),
        TestQuestion(test_id=math_test.id, question_text="The logarithm of 1 to any base is always 0.",
                     question_type="true_false", options=["True", "False"],
                     correct_answer="0", explanation="log_b(1) = 0 for any base b > 0, b ≠ 1.",
                     topic="Algebra", difficulty="easy", marks=1.0),
    ]
    db.add_all(math_questions)

    # Computer Science Test
    cs_test = Test(title="Computer Science Test – Programming & Data Structures",
                   subject="Computer Science", exam_name="GATE", duration_minutes=20, total_marks=15, is_published=True)
    db.add(cs_test)
    db.flush()
    cs_questions = [
        TestQuestion(test_id=cs_test.id, question_text="Which data structure follows LIFO (Last In First Out) principle?",
                     question_type="mcq", options=["Queue", "Stack", "Linked List", "Tree"],
                     correct_answer="1", explanation="Stack: push/pop from the same end (LIFO).",
                     topic="Data Structures", difficulty="easy", marks=1.0),
        TestQuestion(test_id=cs_test.id, question_text="A binary search tree can have duplicate keys.",
                     question_type="true_false", options=["True", "False"],
                     correct_answer="1", explanation="Classic BST property requires unique keys (strict inequalities).",
                     topic="Data Structures", difficulty="medium", marks=2.0),
        TestQuestion(test_id=cs_test.id, question_text="What is the time complexity of binary search on a sorted array of n elements?",
                     question_type="mcq", options=["O(n)", "O(n²)", "O(log n)", "O(1)"],
                     correct_answer="2", explanation="Binary search halves the search space each step → O(log n).",
                     topic="Algorithms", difficulty="easy", marks=1.0),
        TestQuestion(test_id=cs_test.id, question_text="Name the sorting algorithm with best-case O(n) time complexity that exploits partially sorted arrays.",
                     question_type="short_answer", options=None,
                     correct_answer="insertion sort", explanation="Insertion Sort is O(n) for already-sorted input.",
                     topic="Algorithms", difficulty="medium", marks=2.0),
        TestQuestion(test_id=cs_test.id, question_text="In Python, what keyword is used to define a function?",
                     question_type="mcq", options=["function", "def", "fun", "lambda"],
                     correct_answer="1", explanation="Python uses 'def' to define functions.",
                     topic="Programming", difficulty="easy", marks=1.0),
        TestQuestion(test_id=cs_test.id, question_text="What does SQL stand for?",
                     question_type="short_answer", options=None,
                     correct_answer="structured query language", explanation="SQL = Structured Query Language, used for relational databases.",
                     topic="Databases", difficulty="easy", marks=1.0),
        TestQuestion(test_id=cs_test.id, question_text="Quicksort is always faster than Merge Sort in all cases.",
                     question_type="true_false", options=["True", "False"],
                     correct_answer="1", explanation="Quicksort worst case O(n²); Merge Sort is always O(n log n).",
                     topic="Algorithms", difficulty="difficult", marks=3.0),
        TestQuestion(test_id=cs_test.id, question_text="Which of the following is NOT an OOP concept?",
                     question_type="mcq", options=["Encapsulation", "Polymorphism", "Compilation", "Inheritance"],
                     correct_answer="2", explanation="Core OOP concepts: Encapsulation, Polymorphism, Inheritance, Abstraction. Compilation is a language concept.",
                     topic="Programming", difficulty="medium", marks=2.0),
        TestQuestion(test_id=cs_test.id, question_text="What is the worst-case time complexity of bubble sort?",
                     question_type="mcq", options=["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
                     correct_answer="2", explanation="Bubble Sort compares n*(n-1)/2 pairs in worst case → O(n²).",
                     topic="Algorithms", difficulty="medium", marks=2.0),
    ]
    db.add_all(cs_questions)
    db.commit()
    print("  ✔ 3 tests with questions seeded (Biology, Mathematics, Computer Science)")


# ─────────────────────────────────────────────
# GUIDANCE DOCUMENTS (for RAG chatbot)
# ─────────────────────────────────────────────
if db.query(GuidanceDocument).count() > 0:
    print("⏭  Guidance documents already seeded. Skipping.")
else:
    docs = [
        GuidanceDocument(title="JEE Main 2025 – Complete Guide",
                         doc_type="exam", is_approved=True,
                         content="""JEE Main 2025 is conducted by NTA twice a year (January and April sessions).
Eligibility: Passed or appearing in Class 12 with PCM. 75% aggregate for general (65% for SC/ST).
Maximum 3 attempts allowed across consecutive years.
Syllabus covers Physics, Chemistry and Mathematics from NCERT Class 11 and 12.
Application fee is ₹650 for general category females and ₹1300 for general category males.
Top NIT, IIIT and GFTIs accept JEE Main scores. IITs require JEE Advanced after clearing JEE Main.
Paper 2A is for B.Arch (Maths + Aptitude + Drawing) and Paper 2B for B.Planning.
Score validity: JEE Main score is valid only for that academic year.
Preparation strategy: Complete NCERT first, then solve previous year papers, take NTA mock tests online.
Important: Register at jeemain.nta.nic.in. Verify dates on the official site as they change each year."""),
        GuidanceDocument(title="NEET-UG 2025 – Complete Guide",
                         doc_type="exam", is_approved=True,
                         content="""NEET-UG is the single national entrance exam for MBBS, BDS, AYUSH, Veterinary and Nursing programs.
Conducted by NTA once a year, usually in May.
Eligibility: 10+2 with Physics, Chemistry, Biology. Minimum 50% aggregate (40% for SC/ST/OBC).
No upper age limit as per recent Supreme Court ruling.
Syllabus: 180 questions (45 Physics, 45 Chemistry, 45 Botany, 45 Zoology) from NCERT Class 11 & 12.
Marking: +4 for correct, -1 for incorrect, 0 for unattempted.
Total marks: 720.
Top colleges: AIIMS New Delhi (separate exam — AIIMS MBBS discontinued; now through NEET), CMC Vellore, JIPMER Puducherry, MAMC Delhi.
15% All India Quota seats filled based on NEET score via MCC counselling. 85% state quota.
Preparation: NCERT is the primary source. Use NCERT Fingertips, Disha, Allen modules. Solve 10 years of papers.
Apply at neet.nta.nic.in. Verify exact dates and eligibility on official website."""),
        GuidanceDocument(title="B.Tech CSE Career Path Guide",
                         doc_type="course", is_approved=True,
                         content="""B.Tech Computer Science Engineering is a 4-year undergraduate program.
Top institutions: IIT Bombay, IIT Delhi, IIT Madras, NIT Trichy, BITS Pilani, VIT Vellore, Manipal.
Admission through JEE Main (for NITs/IIITs), JEE Advanced (IITs), or state entrance tests (KEAM, KCET, MHT-CET).
Key subjects: Data Structures, Algorithms, Operating Systems, DBMS, Computer Networks, Software Engineering, Machine Learning.
Career options: Software Engineer (₹6–40 LPA), Data Scientist (₹8–50 LPA), ML Engineer (₹10–60 LPA), Cybersecurity Analyst (₹5–30 LPA), Product Manager (₹12–60 LPA).
Top recruiters: Google, Microsoft, Amazon, Flipkart, Infosys, TCS, Wipro, Goldman Sachs, JP Morgan, startups.
Higher study options: M.Tech (IITs via GATE), MS/PhD abroad (GRE + TOEFL/IELTS), MBA at IIMs.
Certifications to boost profile: AWS Certified Developer, Google Cloud, Meta Front-End, TensorFlow Developer, Cisco CCNA.
Internship platforms: Internshala, LinkedIn, company career portals. First internship crucial for placement.
Skills students should build: Python/Java, DSA, System Design, SQL, Git, Cloud basics, Communication."""),
        GuidanceDocument(title="Scholarship Guide for Indian Students 2025",
                         doc_type="scholarship", is_approved=True,
                         content="""Multiple scholarships are available for Indian students at Class 11 to Postgraduate level.
National Merit Scholarship: Top 1% board students. ₹12,000–₹24,000/year. Apply at scholarships.gov.in by September.
INSPIRE (DST): B.Sc/M.Sc Natural Sciences students who topped Class 12 Science. ₹80,000/year. Apply at online-inspire.gov.in.
Post-Matric Scholarship: SC/ST/OBC students. Family income < ₹2.5 Lakh. Full/partial fee reimbursement. State government portals.
KVPY Fellowship: Class 11 to 1st year UG Science students. Aptitude test + interview. ₹5000–₹7000/month. kvpy.iisc.ac.in.
Sitaram Jindal Foundation: ₹500–₹2000/month for financially weak students. sitaramjindalfoundation.org.
Vidyadhan (SDF): Kerala, Tamil Nadu students. ₹10,000–₹30,000/year. vidyadhan.org.
Buddy4Study aggregates all scholarships: buddy4study.com
Tips: Apply to multiple scholarships simultaneously. Keep academic certificates, income certificate and Aadhaar ready.
Deadlines are strict — mark them in your calendar and apply at least 2 weeks before the last date."""),
        GuidanceDocument(title="Study Abroad Guide – USA, UK, Germany, Canada, Australia",
                         doc_type="study_abroad", is_approved=True,
                         content="""USA: Most popular for STEM and MBA. Tuition $25,000–$60,000/year. SAT/ACT for UG, GRE/GMAT for PG, IELTS/TOEFL for English.
F-1 Student Visa. STEM OPT extends post-study work to 3 years. Top universities: MIT, Stanford, CMU, UC Berkeley.
UK: 1-year faster PG programs. £15,000–£35,000/year. IELTS 6.0+ required. Graduate Route Visa: 2-year post-study work.
Top universities: Oxford, Cambridge, Imperial, UCL, Edinburgh. UCAS application by January 25.
Germany: Mostly tuition-free public universities. €0–€3,000/semester. TestDaF required for German-taught programs; IELTS for English programs.
18-month job-search visa after graduation. TU Munich, RWTH Aachen, Heidelberg top choices.
Canada: 3-year PGWP allows post-study work matching degree duration. IELTS 6.0+ required. CAD 20,000–50,000/year.
PR through Express Entry after PGWP. Top universities: UofT, UBC, McGill, Waterloo.
Australia: Student visa allows unlimited work hours (since 2023). AUD 25,000–45,000/year. 2–4 year Temporary Graduate Visa.
IELTS 6.0–6.5 required. Top: ANU, Melbourne, Sydney, Monash.
General tips: Apply 12–18 months before intake. Statement of Purpose (SOP) is critical. Research scholarships like Fulbright (USA), Chevening (UK), DAAD (Germany) for financial aid.
Verify visa requirements and fee structures on official university/embassy websites."""),
    ]
    db.add_all(docs)
    db.flush()
    db.commit()
    print(f"  ✔ {len(docs)} guidance documents seeded")

    # Build embeddings for all documents
    # Import here to avoid circular issues
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'routers'))
    try:
        from routers.chatbot import _embed_document
        for doc in docs:
            _embed_document(doc, db)
        print("  ✔ Document embeddings generated")
    except Exception as e:
        print(f"  ⚠ Embedding generation skipped: {e}")


# ─────────────────────────────────────────────
# QUESTION PAPERS (Module 5)
# ─────────────────────────────────────────────
if db.query(QuestionPaper).count() > 0:
    print("⏭  Question papers already seeded.")
else:
    papers = [
        QuestionPaper(exam_name="NEET-UG", subject="Biology", year=2023,
                      title="NEET 2023 Biology Section",
                      topic_tags=["Cell Biology", "Genetics", "Plant Physiology", "Human Physiology"],
                      file_path="/papers/neet_2023_biology.pdf",
                      answer_key_file="/papers/neet_2023_biology_ans.pdf",
                      approval_status="approved"),
        QuestionPaper(exam_name="JEE Main", subject="Mathematics", year=2024,
                      title="JEE Main Jan 2024 – Mathematics",
                      topic_tags=["Calculus", "Algebra", "Trigonometry", "Coordinate Geometry", "Matrices"],
                      file_path="/papers/jee_main_2024_maths.pdf",
                      answer_key_file="/papers/jee_main_2024_maths_ans.pdf",
                      approval_status="approved"),
        QuestionPaper(exam_name="GATE", subject="Computer Science", year=2023,
                      title="GATE CS 2023 – Data Structures & Algorithms",
                      topic_tags=["Data Structures", "Algorithms", "Databases", "Operating Systems", "Networks"],
                      file_path="/papers/gate_2023_cs.pdf",
                      answer_key_file="/papers/gate_2023_cs_ans.pdf",
                      approval_status="approved"),
        QuestionPaper(exam_name="KEAM", subject="Physics", year=2023,
                      title="KEAM 2023 Physics Paper",
                      topic_tags=["Mechanics", "Electromagnetism", "Optics", "Modern Physics"],
                      file_path="/papers/keam_2023_physics.pdf",
                      answer_key_file=None,
                      approval_status="approved"),
        QuestionPaper(exam_name="Board", subject="Mathematics", year=2024,
                      title="Kerala HSE Plus Two Maths 2024",
                      topic_tags=["Calculus", "Matrices", "Probability", "Vectors"],
                      file_path="/papers/kerala_hse_maths_2024.pdf",
                      answer_key_file="/papers/kerala_hse_maths_2024_ans.pdf",
                      approval_status="approved"),
    ]
    db.add_all(papers)
    db.commit()
    print(f"  ✔ {len(papers)} question papers seeded")


# Diploma-to-degree pathway data is maintained outside the main seed guard so
# existing installations receive it when this script is rerun.
diploma_pathways = [
    Course(
        title="B.Tech Computer Science & Engineering (Lateral Entry)",
        stream="Engineering",
        degree_level="Undergraduate Lateral Entry",
        duration_years=3.0,
        eligibility=(
            "Diploma in a related engineering branch. Branch compatibility, "
            "entrance requirements, and admission rules vary by institution "
            "and current state notification; verify before applying."
        ),
        exams=["State lateral-entry admission process (verify current notification)"],
        fee_range="Varies by institution",
        skills_needed=["Mathematics", "Programming", "Problem Solving"],
        job_roles=["Software Engineer", "Application Developer", "Systems Analyst"],
        salary_range="Varies by role and location",
        scope="A possible degree pathway for eligible diploma holders through lateral entry.",
        top_colleges=[],
    ),
]
for pathway in diploma_pathways:
    existing = db.query(Course).filter(Course.title == pathway.title).first()
    if not existing:
        db.add(pathway)
        print(f"  ✔ Added pathway: {pathway.title}")
db.commit()


db.close()
print("\n✅ Phase 1 seed complete!")
print("\nTest accounts:")
print("  Student: student@studymatch.ai / password123")
print("  Teacher: teacher@studymatch.ai / password123")
print("\nNew endpoints available at http://localhost:8000/docs")
