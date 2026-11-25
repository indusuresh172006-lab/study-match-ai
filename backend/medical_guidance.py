"""
Medical and Health Sciences Postgraduate pathways and entrance exams.
Automatically seeds or upserts postgraduate medical courses into StudyMatch AI.
"""
from typing import List
from sqlalchemy.orm import Session
from models import Course, EntranceExam


def get_medical_pg_courses() -> List[Course]:
    return [
        Course(
            title="MD (Doctor of Medicine)",
            stream="Health Sciences",
            degree_level="Postgraduate",
            duration_years=3.0,
            eligibility="MBBS degree recognized by National Medical Commission (NMC/MCI) with completion of compulsory 1-year rotating internship. Valid NEET-PG or INI-CET score.",
            exams=["NEET-PG", "INI-CET"],
            fee_range="Govt: ₹30K–₹1 Lakh/year | Private: ₹15–₹35 Lakh/year",
            skills_needed=["Clinical Diagnostics", "Patient Care", "Internal Medicine", "Medical Research", "Pathology"],
            job_roles=["Consultant Physician", "Specialist Doctor (MD)", "Clinical Researcher", "Assistant Professor (Medical College)"],
            salary_range="₹12–₹35 LPA (post-residency)",
            scope="Primary postgraduate clinical medical degree in India leading to senior consultant roles and super-specialty DM fellowships (Cardiology, Neurology, Nephrology, Gastroenterology, Medical Oncology).",
            top_colleges=["AIIMS New Delhi", "PGIMER Chandigarh", "CMC Vellore", "JIPMER Puducherry", "Madras Medical College"]
        ),
        Course(
            title="MS (Master of Surgery)",
            stream="Health Sciences",
            degree_level="Postgraduate",
            duration_years=3.0,
            eligibility="MBBS degree recognized by National Medical Commission (NMC/MCI) with completion of compulsory 1-year rotating internship. Valid NEET-PG or INI-CET score.",
            exams=["NEET-PG", "INI-CET"],
            fee_range="Govt: ₹30K–₹1 Lakh/year | Private: ₹18–₹40 Lakh/year",
            skills_needed=["Surgical Technique", "Anatomy & Operative Skills", "Emergency Trauma Care", "Patient Care", "Manual Dexterity"],
            job_roles=["General Surgeon", "Orthopaedic Surgeon", "ENT Specialist", "Ophthalmologist", "Obstetrician & Gynaecologist"],
            salary_range="₹15–₹45 LPA (post-residency)",
            scope="Advanced surgical postgraduate qualification leading to surgical super-specialty M.Ch pathways (Neurosurgery, Cardiothoracic Surgery, Surgical Oncology, Urology, Plastic Surgery).",
            top_colleges=["AIIMS New Delhi", "JIPMER Puducherry", "PGIMER Chandigarh", "King George's Medical University", "Grant Medical College Mumbai"]
        ),
        Course(
            title="DNB (Diplomate of National Board - Broad Specialties)",
            stream="Health Sciences",
            degree_level="Postgraduate",
            duration_years=3.0,
            eligibility="MBBS degree with rotating internship completion and valid NEET-PG score. Awarded by the National Board of Examinations in Medical Sciences (NBEMS).",
            exams=["NEET-PG"],
            fee_range="₹1.25 Lakh/year (Standardized NBEMS fee)",
            skills_needed=["Clinical Specialty Practice", "Hospital Inpatient Care", "Diagnostic Reasoning", "Procedural Skills"],
            job_roles=["DNB Specialist", "Consultant Doctor", "Intensivist", "Clinical Fellow"],
            salary_range="₹12–₹30 LPA",
            scope="Nationally recognized post-MBBS specialist degree equivalent to MD/MS, offered in premier corporate and multi-specialty hospital chains across India with high clinical patient volume.",
            top_colleges=["Sir Ganga Ram Hospital Delhi", "Apollo Hospitals Chennai/Hyderabad", "Fortis Healthcare", "Medanta The Medicity Gurugram"]
        ),
        Course(
            title="Master of Public Health (MPH)",
            stream="Health Sciences",
            degree_level="Postgraduate",
            duration_years=2.0,
            eligibility="MBBS, BDS, BAMS, BHMS, or any recognized Health Sciences / Allied Medical bachelor's degree with minimum 50% aggregate.",
            exams=["CUET-PG", "AIIMS PG Entrance", "JIPMER PG", "TISS-NET"],
            fee_range="₹50K–₹3 Lakh/year",
            skills_needed=["Epidemiology", "Biostatistics", "Health Systems Management", "Public Health Research", "Disease Control"],
            job_roles=["Epidemiologist", "Public Health Specialist", "WHO / UNICEF Health Officer", "Health Policy Analyst", "Clinical Trial Coordinator"],
            salary_range="₹8–₹24 LPA",
            scope="Leadership pathway in public health, epidemiology, global health organizations (WHO, UN), government health missions, and pharmaceutical research.",
            top_colleges=["AIIMS New Delhi", "JIPMER Puducherry", "SCTIMST Thiruvananthapuram", "TISS Mumbai", "NIMHANS Bengaluru"]
        ),
        Course(
            title="MBA in Hospital & Healthcare Management",
            stream="Management",
            degree_level="Postgraduate",
            duration_years=2.0,
            eligibility="MBBS, BDS, B.Pharm, B.Sc Nursing, or any recognized Bachelor's degree. Clinical/medical background preferred.",
            exams=["CAT", "MAT", "CMAT", "XAT"],
            fee_range="₹3–₹15 Lakh (total)",
            skills_needed=["Hospital Operations", "Healthcare Finance", "NABH/JCI Quality Accreditation", "Health Informatics", "Strategic Leadership"],
            job_roles=["Hospital Administrator", "Healthcare Operations Manager", "Medical Superintendent Executive", "Health Insurance Lead", "Healthcare Consultant"],
            salary_range="₹10–₹28 LPA",
            scope="Bridges clinical medical training with administrative and corporate leadership of hospitals, health-tech startups, and health insurance conglomerates.",
            top_colleges=["IIHMR University Jaipur", "TISS Mumbai", "Symbiosis Institute of Health Sciences Pune", "FMS Delhi", "Manipal University"]
        ),
    ]


def get_medical_pg_exams() -> List[EntranceExam]:
    return [
        EntranceExam(
            name="NEET-PG",
            code="NEET-PG",
            conducting_body="National Board of Examinations in Medical Sciences (NBEMS)",
            eligibility="MBBS degree or provisional MBBS pass certificate recognized by NMC. Completion of 1-year compulsory rotating internship.",
            syllabus="Clinical, Pre-Clinical, and Para-Clinical subjects taught across MBBS (Medicine, Surgery, OBGY, Pathology, Pharmacology, Paediatrics, etc.).",
            exam_dates={"notification": "January–February", "exam_date": "June–July", "result": "August"},
            application_process="Online application via nbe.edu.in / natboard.edu.in. Document verification and online MCC counselling.",
            preparation_tips="Focus on high-yield clinical vignettes, previous years question papers, Grand Tests, and marrow/prepladder revision notes.",
            official_website_url="https://natboard.edu.in",
            stream="Health Sciences",
        ),
        EntranceExam(
            name="INI-CET",
            code="INI-CET",
            conducting_body="All India Institute of Medical Sciences (AIIMS New Delhi)",
            eligibility="MBBS degree with completion of rotating internship. Minimum 55% aggregate marks for General/OBC, 50% for SC/ST.",
            syllabus="Comprehensive MBBS curriculum across 19 subjects with emphasis on applied clinical reasoning and research methodologies.",
            exam_dates={"notification": "September (Jan session) / March (July session)", "exam_date": "November / May (Bi-annual)", "result": "1 week post-exam"},
            application_process="Two-step PAAR registration on aiimsexams.ac.in. Basic Registration followed by Final Registration and code generation.",
            preparation_tips="Practice concept-based multiple-choice questions with multiple-correct and assertion-reason formats. Review AIIMS previous papers.",
            official_website_url="https://www.aiimsexams.ac.in",
            stream="Health Sciences",
        ),
    ]


def ensure_medical_pg_courses(db: Session) -> None:
    """Idempotently ensure medical postgraduate courses and entrance exams exist in the database."""
    try:
        for course in get_medical_pg_courses():
            existing = db.query(Course).filter(Course.title == course.title).first()
            if not existing:
                db.add(course)

        for exam in get_medical_pg_exams():
            existing_exam = db.query(EntranceExam).filter(EntranceExam.name == exam.name).first()
            if not existing_exam:
                db.add(exam)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Warning in ensure_medical_pg_courses: {e}")
