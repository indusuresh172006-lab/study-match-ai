import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from database import engine, SessionLocal, Base
from models import (
    Student, StudentProfile, SkillProfile, StudyMaterial, QuestionBank,
    PreviousPaper, PaperQuestion, GuidanceCourse, CourseSummary, MaterialBookmark
)
from auth import get_password_hash

def seed():
    print("Starting database schema update and data seeding...")
    
    Base.metadata.create_all(bind=engine)
    print("Tables created / verified successfully.")

    # 1. Update schema
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'student';"))
        conn.commit()

    db = SessionLocal()
    try:
        # 2. Seed Users
        student_user = db.query(Student).filter(Student.email == "student@studymatch.ai").first()
        if not student_user:
            student_user = Student(
                name="Alex Morgan",
                email="student@studymatch.ai",
                password_hash=get_password_hash("password123"),
                role="student",
                approval_status="approved",
            )
            db.add(student_user)
            db.commit()
            db.refresh(student_user)
            print("Created student: student@studymatch.ai / password123")
        else:
            student_user.role = "student"
            student_user.approval_status = "approved"
            db.commit()

        teacher_user = db.query(Student).filter(Student.email == "teacher@studymatch.ai").first()
        if not teacher_user:
            teacher_user = Student(
                name="Dr. Sarah Jenkins",
                email="teacher@studymatch.ai",
                password_hash=get_password_hash("password123"),
                role="teacher",
                approval_status="approved",
            )
            db.add(teacher_user)
            db.commit()
            db.refresh(teacher_user)
            print("Created teacher: teacher@studymatch.ai / password123")
        else:
            teacher_user.role = "teacher"
            teacher_user.approval_status = "approved"
            db.commit()

        # Seed Administrator Users
        for adm_email in ["admin@studymatch.ai", "admin@gmail.com"]:
            admin_user = db.query(Student).filter(Student.email == adm_email).first()
            if not admin_user:
                admin_user = Student(
                    name="System Administrator",
                    email=adm_email,
                    password_hash=get_password_hash("admin123"),
                    role="admin",
                    approval_status="approved",
                )
                db.add(admin_user)
                db.commit()
                db.refresh(admin_user)
                print(f"Created admin: {adm_email} / admin123")
            else:
                admin_user.role = "admin"
                admin_user.approval_status = "approved"
                admin_user.password_hash = get_password_hash("admin123")
                db.commit()

        # Seed profile
        prof = db.query(StudentProfile).filter(StudentProfile.student_id == student_user.id).first()
        if not prof:
            prof = StudentProfile(
                student_id=student_user.id,
                course="Higher Secondary Science / Pre-University",
                stream="Science (PCM/B)",
                academic_level="Grade 12 / High School Senior",
                learning_goal="Excel in entrance exams and gain admission to top STEM university programs"
            )
            db.add(prof)
            db.commit()

        # 3. Seed Skill Profiles for Alex Morgan
        initial_skills = [
            # Biology
            ("Biology", "Genetics & DNA", "weak", 35.0),
            ("Biology", "Cell Biology", "average", 65.0),
            ("Biology", "Ecology & Evolution", "strong", 85.0),
            # Mathematics
            ("Mathematics", "Calculus & Limits", "weak", 38.0),
            ("Mathematics", "Linear Algebra & Matrices", "average", 68.0),
            ("Mathematics", "Probability & Statistics", "strong", 88.0),
            # Computer Science
            ("Computer Science", "Operating Systems", "weak", 42.0),
            ("Computer Science", "Database Management (SQL)", "average", 70.0),
            ("Computer Science", "Data Structures & Algorithms", "strong", 92.0),
        ]

        for subj, top, stat, score in initial_skills:
            sk = db.query(SkillProfile).filter(
                SkillProfile.student_id == student_user.id,
                SkillProfile.subject == subj,
                SkillProfile.topic == top
            ).first()
            if not sk:
                sk = SkillProfile(
                    student_id=student_user.id,
                    subject=subj,
                    topic=top,
                    status=stat,
                    mastery_score=score,
                    tests_taken=3
                )
                db.add(sk)
        db.commit()
        print("Skill profiles verified.")

        # 4. Seed Study Materials
        materials_data = [
            # Biology Materials
            {
                "title": "Mastering Mendelian Genetics and DNA Replication",
                "subject": "Biology",
                "topic": "Genetics & DNA",
                "material_type": "notes",
                "difficulty_level": "medium",
                "summary": "Core principles of segregation, independent assortment, DNA double helix structure, Okazaki fragments, and polymerase enzymes.",
                "content": """# Mendelian Genetics and Molecular Biology

## 1. Mendel's Fundamental Laws
1. **Law of Segregation**: Each individual possesses two alleles for each gene. During gamete formation, these alleles segregate equally.
2. **Law of Independent Assortment**: Genes for different traits assort independently of one another during gamete formation (valid for non-linked genes).

## 2. DNA Replication Mechanism
- **Helicase**: Unwinds the double-stranded DNA helix at the replication fork.
- **Single-Stranded Binding Proteins (SSBPs)**: Stabilize unwound DNA strands.
- **Primase**: Synthesizes an RNA primer required for DNA Polymerase to initiate synthesis.
- **DNA Polymerase III**: Adds complementary deoxyribonucleotides in the 5' to 3' direction.
- **Leading vs Lagging Strand**: The leading strand is synthesized continuously; the lagging strand is synthesized discontinuously as Okazaki fragments.
- **DNA Ligase**: Joins phosphodiester backbones between Okazaki fragments.

## 3. Key Differences: DNA vs RNA
- **Sugars**: Deoxyribose (lacks 2'-OH) vs Ribose.
- **Bases**: Thymine in DNA, Uracil in RNA.
- **Structure**: Typically double-stranded duplex vs single-stranded secondary structures."""
            },
            {
                "title": "Cell Biology: Organelles and Cellular Respiration",
                "subject": "Biology",
                "topic": "Cell Biology",
                "material_type": "learning_material",
                "difficulty_level": "easy",
                "summary": "Comprehensive overview of mitochondria, ATP generation, glycolysis, Krebs cycle, and chloroplast light reactions.",
                "content": """# Cell Structure and Cellular Respiration

## 1. Mitochondria and ATP Generation
- Mitochondria contain an inner folded membrane called cristae that accommodates the electron transport chain (ETC).
- **Proton Gradient**: Chemiosmosis couples proton movement through ATP Synthase to synthesize ~30-32 ATP molecules per glucose molecule.

## 2. Stages of Respiration
1. **Glycolysis** (Cytoplasm): 1 Glucose -> 2 Pyruvate + 2 Net ATP + 2 NADH (Anaerobic).
2. **Pyruvate Decarboxylation** (Mitochondrial Matrix): Pyruvate -> Acetyl-CoA + CO2 + NADH.
3. **Citric Acid (Krebs) Cycle**: Matrix; oxidizes Acetyl-CoA generating NADH, FADH2, and GTP/ATP.
4. **Oxidative Phosphorylation**: Inner membrane; oxygen serves as the terminal electron acceptor yielding H2O."""
            },
            {
                "title": "Ecological Pyramids and Ecosystem Dynamics",
                "subject": "Biology",
                "topic": "Ecology & Evolution",
                "material_type": "important_questions",
                "difficulty_level": "medium",
                "summary": "Important exam questions on trophic levels, 10 percent energy rule, natural selection mechanisms, and Hardy-Weinberg equilibrium.",
                "content": """# Ecology and Evolutionary Principles

## 1. Lindeman's 10% Energy Transfer Law
Only approximately 10% of energy transferred between trophic levels is assimilated into biomass; 90% is dissipated as metabolic heat and respiration.

## 2. Hardy-Weinberg Principle
In an idealized non-evolving population:
$$p + q = 1$$
$$p^2 + 2pq + q^2 = 1$$
Conditions required:
1. No mutations
2. Random mating
3. No gene flow (migration)
4. Extremely large population size (no genetic drift)
5. No natural selection"""
            },
            # Mathematics Materials
            {
                "title": "Calculus: Complete Guide to Limits and Continuity",
                "subject": "Mathematics",
                "topic": "Calculus & Limits",
                "material_type": "notes",
                "difficulty_level": "medium",
                "summary": "Step-by-step techniques for evaluating indeterminate limits (0/0, inf/inf), L'Hôpital's Rule, and epsilon-delta continuity proofs.",
                "content": """# Differential Calculus: Limits and Continuity

## 1. Standard Indeterminate Forms
When evaluating $\\lim_{x \\to a} \\frac{f(x)}{g(x)} = \\frac{0}{0}$ or $\\frac{\\infty}{\\infty}$:
- **Factorization**: Cancel common roots $(x - a)$.
- **Rationalization**: Multiply numerator and denominator by conjugate expressions.
- **Trigonometric Limits**:
  $$\\lim_{x \\to 0} \\frac{\\sin x}{x} = 1$$
  $$\\lim_{x \\to 0} \\frac{1 - \\cos x}{x} = 0$$
  $$\\lim_{x \\to 0} \\frac{\\tan x}{x} = 1$$

## 2. L'Hôpital's Rule
If $\\lim_{x \\to a} f(x) = 0$ and $\\lim_{x \\to a} g(x) = 0$, and both functions are differentiable near $a$:
$$\\lim_{x \\to a} \\frac{f(x)}{g(x)} = \\lim_{x \\to a} \\frac{f'(x)}{g'(x)}$$

## 3. Definition of Continuity
A function $f(x)$ is continuous at $x = c$ if and only if:
1. $f(c)$ is defined.
2. $\\lim_{x \\to c} f(x)$ exists ($LHL = RHL$).
3. $\\lim_{x \\to c} f(x) = f(c)$."""
            },
            {
                "title": "Linear Algebra: Matrices, Determinants and Eigenvalues",
                "subject": "Mathematics",
                "topic": "Linear Algebra & Matrices",
                "material_type": "learning_material",
                "difficulty_level": "medium",
                "summary": "Matrix operations, Gaussian elimination, inverse by adjugate method, and characteristic equation for eigenvalues.",
                "content": """# Linear Algebra and Matrix Operations

## 1. Determinants and Inverses
For a 2x2 matrix $A = \\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}$:
$$\\det(A) = ad - bc$$
$$A^{-1} = \\frac{1}{\\det(A)} \\begin{pmatrix} d & -b \\\\ -c & a \\end{pmatrix}$$
A matrix is invertible if and only if $\\det(A) \\neq 0$ (non-singular).

## 2. Eigenvalues and Eigenvectors
Given square matrix $A$, a scalar $\\lambda$ is an eigenvalue if:
$$Av = \\lambda v \\iff (A - \\lambda I)v = 0$$
Solve the characteristic equation:
$$\\det(A - \\lambda I) = 0$$"""
            },
            {
                "title": "Probability Distributions and Bayes' Theorem",
                "subject": "Mathematics",
                "topic": "Probability & Statistics",
                "material_type": "important_questions",
                "difficulty_level": "difficult",
                "summary": "Conditional probability, Bayes' formula with multiple partitions, Binomial and Normal distributions.",
                "content": """# Probability and Applied Statistics

## 1. Bayes' Theorem
$$P(A|B) = \\frac{P(B|A) \\cdot P(A)}{P(B)}$$
Total probability across mutually exclusive partitions $A_1, A_2, \\dots, A_n$:
$$P(B) = \\sum_{i=1}^n P(B|A_i)P(A_i)$$

## 2. Binomial Distribution
For $n$ independent Bernoulli trials with success probability $p$:
$$P(X = k) = \\binom{n}{k} p^k (1 - p)^{n-k}$$
- Mean $\\mu = np$
- Variance $\\sigma^2 = np(1 - p)$"""
            },
            # Computer Science Materials
            {
                "title": "Operating Systems: Concurrency, Deadlocks and Memory Management",
                "subject": "Computer Science",
                "topic": "Operating Systems",
                "material_type": "notes",
                "difficulty_level": "difficult",
                "summary": "Process scheduling, thread synchronization, semaphores, Coffman's 4 conditions for deadlock, and virtual memory paging.",
                "content": """# Operating Systems Architecture

## 1. The 4 Coffman Deadlock Conditions
Deadlock can occur if and only if all four conditions hold simultaneously:
1. **Mutual Exclusion**: At least one resource must be held in a non-shareable mode.
2. **Hold and Wait**: A process holds at least one resource and requests additional ones.
3. **No Preemption**: Resources cannot be preempted forcibly from a process.
4. **Circular Wait**: A closed chain of processes exists such that each process holds a resource needed by the next.

## 2. Banker's Algorithm for Deadlock Avoidance
Processes claim their maximum resource requirements. The OS grants requests only if the resulting state is guaranteed to be **safe** (a safe sequence exists where every process can terminate).

## 3. Virtual Memory and Paging
- Logical addresses are translated to physical frames via the **Page Table**.
- **Page Fault**: Occurs when a referenced page is not resident in physical RAM.
- **Thrashing**: Occurs when the OS spends more time swapping pages in/out than executing user instructions."""
            },
            {
                "title": "Relational Databases and SQL Mastery",
                "subject": "Computer Science",
                "topic": "Database Management (SQL)",
                "material_type": "learning_material",
                "difficulty_level": "medium",
                "summary": "ACID properties, indexing (B-Trees), normalization up to BCNF, and complex JOIN queries.",
                "content": """# Relational Database Management Systems

## 1. ACID Properties
- **Atomicity**: Entire transaction completes or completely rolls back.
- **Consistency**: Database transitions only from one valid state to another.
- **Isolation**: Intermediate states are invisible to concurrent transactions.
- **Durability**: Committed data survives power loss or crashes.

## 2. Normal Forms
- **1NF**: Atomic values; no repeating groups.
- **2NF**: In 1NF and no partial dependencies on candidate keys.
- **3NF**: In 2NF and no transitive dependencies ($A \\to B \\to C$).
- **BCNF**: For every functional dependency $X \\to Y$, $X$ must be a superkey."""
            },
            {
                "title": "Data Structures: Trees, Heaps and Graph Algorithms",
                "subject": "Computer Science",
                "topic": "Data Structures & Algorithms",
                "material_type": "important_questions",
                "difficulty_level": "medium",
                "summary": "Binary Search Trees, Dijkstra's shortest path, topological sorting, dynamic programming patterns.",
                "content": """# Data Structures and Algorithmic Analysis

## 1. Time Complexities Overview
- Array lookup: $O(1)$
- Binary Search: $O(\\log n)$
- Balanced BST (AVL/Red-Black) Search/Insert/Delete: $O(\\log n)$
- Heap push/pop: $O(\\log n)$
- Hash Map average: $O(1)$, worst case: $O(n)$

## 2. Dijkstra's Algorithm
Finds shortest paths from single source in non-negative weighted graphs:
- Uses min-priority queue (min-heap).
- Time Complexity: $O((V + E) \\log V)$ using adjacency lists and binary heap."""
            }
        ]

        material_map = {}
        for m_data in materials_data:
            mat = db.query(StudyMaterial).filter(
                StudyMaterial.title == m_data["title"]
            ).first()
            if not mat:
                mat = StudyMaterial(
                    title=m_data["title"],
                    subject=m_data["subject"],
                    topic=m_data["topic"],
                    material_type=m_data["material_type"],
                    difficulty_level=m_data["difficulty_level"],
                    summary=m_data["summary"],
                    content=m_data["content"],
                    uploaded_by=teacher_user.id
                )
                db.add(mat)
                db.commit()
                db.refresh(mat)
            material_map[(m_data["subject"], m_data["topic"])] = mat.id

        # Bookmark one material for Alex Morgan
        first_mat = db.query(StudyMaterial).filter(StudyMaterial.subject == "Biology").first()
        if first_mat:
            bm = db.query(MaterialBookmark).filter(
                MaterialBookmark.student_id == student_user.id,
                MaterialBookmark.material_id == first_mat.id
            ).first()
            if not bm:
                db.add(MaterialBookmark(student_id=student_user.id, material_id=first_mat.id))
                db.commit()

        print(f"Study materials seeded ({len(materials_data)} items).")

        # 5. Seed Question Bank (Easy, Medium, Difficult for each subject)
        questions_data = [
            # Biology Questions
            {
                "subject": "Biology", "topic": "Genetics & DNA", "difficulty": "easy",
                "question_text": "Which nitrogenous base is found in RNA but NOT in DNA?",
                "options": ["Thymine", "Uracil", "Cytosine", "Guanine"],
                "correct_option": 1,
                "explanation": "Uracil replaces Thymine in RNA and pairs with Adenine.",
                "mat_key": ("Biology", "Genetics & DNA")
            },
            {
                "subject": "Biology", "topic": "Genetics & DNA", "difficulty": "medium",
                "question_text": "During DNA replication, which enzyme synthesizes the short RNA primer required for DNA polymerase III initiation?",
                "options": ["DNA Ligase", "Topoisomerase", "RNA Primase", "Reverse Transcriptase"],
                "correct_option": 2,
                "explanation": "Primase synthesizes short RNA primers providing the 3'-OH end for DNA Polymerase III.",
                "mat_key": ("Biology", "Genetics & DNA")
            },
            {
                "subject": "Biology", "topic": "Genetics & DNA", "difficulty": "difficult",
                "question_text": "In a dihybrid cross between two heterozygous individuals (AaBb x AaBb) with independent assortment, what is the probability of an offspring having the genotype AaBB?",
                "options": ["1/16", "2/16 (1/8)", "4/16 (1/4)", "3/16"],
                "correct_option": 1,
                "explanation": "P(Aa) = 2/4 = 1/2. P(BB) = 1/4. P(Aa and BB) = 1/2 * 1/4 = 1/8 (2/16).",
                "mat_key": ("Biology", "Genetics & DNA")
            },
            {
                "subject": "Biology", "topic": "Cell Biology", "difficulty": "easy",
                "question_text": "Which organelle is considered the powerhouse of the cell due to ATP generation?",
                "options": ["Golgi apparatus", "Ribosome", "Mitochondria", "Lysosome"],
                "correct_option": 2,
                "explanation": "Mitochondria produce the majority of cellular ATP via oxidative phosphorylation.",
                "mat_key": ("Biology", "Cell Biology")
            },
            {
                "subject": "Biology", "topic": "Cell Biology", "difficulty": "medium",
                "question_text": "In glycolysis, how many net ATP molecules and NADH molecules are generated per single molecule of glucose?",
                "options": ["4 net ATP, 2 NADH", "2 net ATP, 2 NADH", "2 net ATP, 4 NADH", "32 net ATP, 10 NADH"],
                "correct_option": 1,
                "explanation": "Glycolysis consumes 2 ATP and produces 4 ATP (net 2 ATP) and 2 NADH molecules.",
                "mat_key": ("Biology", "Cell Biology")
            },
            {
                "subject": "Biology", "topic": "Ecology & Evolution", "difficulty": "difficult",
                "question_text": "If a recessive allele frequency q in a Hardy-Weinberg population is 0.3, what is the expected frequency of heterozygous carriers (2pq)?",
                "options": ["0.09", "0.42", "0.49", "0.21"],
                "correct_option": 1,
                "explanation": "p = 1 - q = 1 - 0.3 = 0.7. 2pq = 2 * (0.7) * (0.3) = 0.42 (42%).",
                "mat_key": ("Biology", "Ecology & Evolution")
            },

            # Mathematics Questions
            {
                "subject": "Mathematics", "topic": "Calculus & Limits", "difficulty": "easy",
                "question_text": "What is the limit of (sin x) / x as x approaches 0?",
                "options": ["0", "Infinity", "1", "Does not exist"],
                "correct_option": 2,
                "explanation": "lim (x->0) sin(x)/x = 1 is a fundamental trigonometric limit.",
                "mat_key": ("Mathematics", "Calculus & Limits")
            },
            {
                "subject": "Mathematics", "topic": "Calculus & Limits", "difficulty": "medium",
                "question_text": "Evaluate the limit: lim (x -> 2) of (x^2 - 4) / (x - 2).",
                "options": ["0", "2", "4", "Undefined"],
                "correct_option": 2,
                "explanation": "(x^2 - 4)/(x - 2) = (x - 2)(x + 2)/(x - 2) = x + 2. Substituting x=2 gives 4.",
                "mat_key": ("Mathematics", "Calculus & Limits")
            },
            {
                "subject": "Mathematics", "topic": "Calculus & Limits", "difficulty": "difficult",
                "question_text": "Evaluate lim (x -> 0) of (e^(3x) - 1 - 3x) / x^2.",
                "options": ["3", "9/2", "0", "9"],
                "correct_option": 1,
                "explanation": "Using L'Hopital twice: 1st derivative: (3e^(3x) - 3)/(2x). 2nd derivative: 9e^(3x)/2. As x->0, limit is 9/2.",
                "mat_key": ("Mathematics", "Calculus & Limits")
            },
            {
                "subject": "Mathematics", "topic": "Linear Algebra & Matrices", "difficulty": "easy",
                "question_text": "What is the determinant of the 2x2 matrix [[3, 2], [1, 4]]?",
                "options": ["10", "14", "12", "7"],
                "correct_option": 0,
                "explanation": "det = (3 * 4) - (2 * 1) = 12 - 2 = 10.",
                "mat_key": ("Mathematics", "Linear Algebra & Matrices")
            },
            {
                "subject": "Mathematics", "topic": "Linear Algebra & Matrices", "difficulty": "medium",
                "question_text": "What are the eigenvalues of the diagonal matrix [[4, 0], [0, -2]]?",
                "options": ["4 and -2", "2 and -2", "0 and 4", "16 and 4"],
                "correct_option": 0,
                "explanation": "For any diagonal or triangular matrix, eigenvalues are precisely the diagonal entries.",
                "mat_key": ("Mathematics", "Linear Algebra & Matrices")
            },
            {
                "subject": "Mathematics", "topic": "Probability & Statistics", "difficulty": "difficult",
                "question_text": "A diagnostic test for a disease has 95% sensitivity and 90% specificity. If disease prevalence is 1%, what is the approximate probability a test-positive person actually has the disease (P(D|+))?",
                "options": ["95%", "8.75%", "50%", "2.5%"],
                "correct_option": 1,
                "explanation": "Bayes: P(+|D)P(D) / [P(+|D)P(D) + P(+|no D)P(no D)] = (0.95*0.01) / (0.95*0.01 + 0.10*0.99) = 0.0095 / 0.1085 ~= 8.75%.",
                "mat_key": ("Mathematics", "Probability & Statistics")
            },

            # Computer Science Questions
            {
                "subject": "Computer Science", "topic": "Operating Systems", "difficulty": "easy",
                "question_text": "Which condition is NOT one of the 4 Coffman conditions required for deadlock?",
                "options": ["Mutual Exclusion", "Circular Wait", "Preemption Allowed", "Hold and Wait"],
                "correct_option": 2,
                "explanation": "The deadlock condition is NO preemption. If preemption is allowed, deadlocks cannot persist.",
                "mat_key": ("Computer Science", "Operating Systems")
            },
            {
                "subject": "Computer Science", "topic": "Operating Systems", "difficulty": "medium",
                "question_text": "What is 'thrashing' in virtual memory systems?",
                "options": [
                    "A virus destroying disk sectors",
                    "CPU spends excessive time swapping pages in and out of disk rather than executing processes",
                    "Overclocking the system bus to maximum speed",
                    "Fragmentation caused by dynamic memory allocation"
                ],
                "correct_option": 1,
                "explanation": "Thrashing occurs when total memory demand exceeds physical RAM, causing constant page faults and disk I/O.",
                "mat_key": ("Computer Science", "Operating Systems")
            },
            {
                "subject": "Computer Science", "topic": "Operating Systems", "difficulty": "difficult",
                "question_text": "In Banker's Algorithm, a system is in a 'Safe State' if and only if:",
                "options": [
                    "There are no active processes running",
                    "There exists at least one allocation sequence that allows every process to complete without deadlock",
                    "Available resources exceed maximum demand of all processes combined",
                    "All process requests are granted instantaneously"
                ],
                "correct_option": 1,
                "explanation": "A safe state guarantees a sequence <P1, P2, ... Pn> where each process can finish with available + freed resources.",
                "mat_key": ("Computer Science", "Operating Systems")
            },
            {
                "subject": "Computer Science", "topic": "Database Management (SQL)", "difficulty": "medium",
                "question_text": "Which normal form prohibits transitive dependencies (where a non-key attribute depends on another non-key attribute)?",
                "options": ["1NF", "2NF", "3NF", "4NF"],
                "correct_option": 2,
                "explanation": "3NF removes transitive dependencies (X -> Y -> Z).",
                "mat_key": ("Computer Science", "Database Management (SQL)")
            },
            {
                "subject": "Computer Science", "topic": "Data Structures & Algorithms", "difficulty": "easy",
                "question_text": "What is the average time complexity of searching for an element in a balanced Binary Search Tree (AVL / Red-Black)?",
                "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                "correct_option": 1,
                "explanation": "A balanced BST guarantees tree height is O(log n), making search, insert, and delete O(log n).",
                "mat_key": ("Computer Science", "Data Structures & Algorithms")
            },
            {
                "subject": "Computer Science", "topic": "Data Structures & Algorithms", "difficulty": "difficult",
                "question_text": "What is the optimal time complexity of Dijkstra's algorithm implemented with an adjacency list and a binary min-heap for a graph with V vertices and E edges?",
                "options": ["O(V^2)", "O((V + E) log V)", "O(E * V)", "O(V log E)"],
                "correct_option": 1,
                "explanation": "Each vertex is extracted from the min-heap in O(log V) and edges are relaxed in O(log V), yielding O((V + E) log V).",
                "mat_key": ("Computer Science", "Data Structures & Algorithms")
            }
        ]

        for q in questions_data:
            existing_q = db.query(QuestionBank).filter(
                QuestionBank.subject == q["subject"],
                QuestionBank.question_text == q["question_text"]
            ).first()
            if not existing_q:
                related_id = material_map.get(q["mat_key"])
                qb = QuestionBank(
                    subject=q["subject"],
                    topic=q["topic"],
                    difficulty=q["difficulty"],
                    question_text=q["question_text"],
                    options=q["options"],
                    correct_option=q["correct_option"],
                    explanation=q["explanation"],
                    related_material_id=related_id
                )
                db.add(qb)
        db.commit()
        print(f"Question bank seeded ({len(questions_data)} questions).")

        # 6. Seed Solved Previous Question Papers
        papers_info = [
            {
                "title": "2024 Pre-University Board Examination: Advanced Biology",
                "subject": "Biology",
                "year": 2024,
                "time_limit_minutes": 25,
                "total_marks": 25,
                "questions": [
                    {
                        "qnum": 1, "topic": "Genetics & DNA",
                        "text": "Explain why Okazaki fragments are formed on the lagging strand during DNA replication.",
                        "options": [
                            "Because DNA polymerase III can only synthesize in the 5' to 3' direction, while the fork opens antiparallel",
                            "Because RNA primers are unstable at physiological temperatures",
                            "Because helicase moves backward intermittently",
                            "Because topoisomerase cuts only one strand at a time"
                        ],
                        "correct": 0,
                        "mat_key": ("Biology", "Genetics & DNA"),
                        "solution": """**Step-by-Step Solution:**
1. **DNA Polymerase Directionality:** DNA Polymerase III strictly requires a free 3'-OH group to add incoming deoxynucleoside triphosphates (dNTPs). Consequently, synthesis exclusively proceeds in the 5' -> 3' direction.
2. **Antiparallel Architecture:** The two parental strands are antiparallel (one is 3'->5', the other is 5'->3').
3. **Leading vs Lagging Strand:** As the replication fork unzips in one direction, the leading strand template (3'->5') allows continuous synthesis. The lagging strand template (5'->3') exposes DNA in the opposite direction of polymerase activity.
4. **Conclusion:** Synthesis on the lagging strand must occur discontinuously in short segments known as Okazaki fragments, each preceded by an RNA primer and subsequently joined by DNA Ligase."""
                    },
                    {
                        "qnum": 2, "topic": "Cell Biology",
                        "text": "What is the ultimate electron acceptor in the mitochondrial electron transport chain during aerobic respiration?",
                        "options": ["NAD+", "FAD", "Molecular Oxygen (O2)", "Cytochrome c"],
                        "correct": 2,
                        "mat_key": ("Biology", "Cell Biology"),
                        "solution": """**Step-by-Step Solution:**
1. **Electrons Pathway:** High-energy electrons donated by NADH and FADH2 traverse Complex I, II, III, and IV (Cytochrome c oxidase).
2. **Terminal Reduction:** At Complex IV, four electrons and four protons are combined with molecular oxygen (O2).
3. **Formation of Water:** $O_2 + 4H^+ + 4e^- \\to 2H_2O$.
4. **Vital Role:** Without oxygen to accept electrons, the chain stalls, proton pumping ceases, and ATP synthesis via chemiosmosis stops."""
                    }
                ]
            },
            {
                "title": "2023 National STEM Entrance Exam: Higher Mathematics",
                "subject": "Mathematics",
                "year": 2023,
                "time_limit_minutes": 30,
                "total_marks": 30,
                "questions": [
                    {
                        "qnum": 1, "topic": "Calculus & Limits",
                        "text": "Evaluate the limit as x approaches 0 of (tan 2x) / (sin 5x).",
                        "options": ["2/5", "5/2", "0", "1"],
                        "correct": 0,
                        "mat_key": ("Mathematics", "Calculus & Limits"),
                        "solution": """**Step-by-Step Solution:**
1. Express in standard limits form:
   $$\\lim_{x \\to 0} \\frac{\\tan 2x}{\\sin 5x} = \\lim_{x \\to 0} \\left( \\frac{\\tan 2x}{2x} \\cdot \\frac{5x}{\\sin 5x} \\cdot \\frac{2x}{5x} \\right)$$
2. Apply fundamental limits:
   $$\\lim_{x \\to 0} \\frac{\\tan 2x}{2x} = 1$$
   $$\\lim_{x \\to 0} \\frac{5x}{\\sin 5x} = 1$$
3. Multiply the coefficients:
   $$1 \\cdot 1 \\cdot \\frac{2}{5} = \\frac{2}{5}$$
4. Alternatively, using L'Hopital's rule on 0/0: $\\lim_{x \\to 0} \\frac{2\\sec^2(2x)}{5\\cos(5x)} = \\frac{2(1)}{5(1)} = \\frac{2}{5}$."""
                    },
                    {
                        "qnum": 2, "topic": "Linear Algebra & Matrices",
                        "text": "If A is a 3x3 invertible matrix with det(A) = 4, what is det(2A)?",
                        "options": ["8", "16", "32", "64"],
                        "correct": 2,
                        "mat_key": ("Mathematics", "Linear Algebra & Matrices"),
                        "solution": """**Step-by-Step Solution:**
1. **Determinant Property for Scalar Multiplication:** For an $n \\times n$ matrix $A$ and scalar $k$:
   $$\\det(kA) = k^n \\det(A)$$
2. Here, matrix dimension $n = 3$, scalar $k = 2$, and $\\det(A) = 4$.
3. Compute:
   $$\\det(2A) = 2^3 \\cdot \\det(A) = 8 \\cdot 4 = 32$$."""
                    }
                ]
            },
            {
                "title": "2024 Technical University Assessment: Computer Science Core",
                "subject": "Computer Science",
                "year": 2024,
                "time_limit_minutes": 30,
                "total_marks": 30,
                "questions": [
                    {
                        "qnum": 1, "topic": "Operating Systems",
                        "text": "In a system with 3 processes sharing 4 units of the same resource, where each process requires at most 2 units, can a deadlock occur?",
                        "options": [
                            "Yes, always",
                            "No, deadlock is impossible in this configuration",
                            "Yes, if processes run concurrently",
                            "Depends on CPU clock speed"
                        ],
                        "correct": 1,
                        "mat_key": ("Computer Science", "Operating Systems"),
                        "solution": """**Step-by-Step Solution:**
1. Let $P = 3$ (number of processes) and $R = 4$ (total resource units).
2. Worst-case allocation before any process can claim its final unit:
   Each process requests 1 unit ($3 \\times 1 = 3$ units allocated).
3. Remaining resources available: $4 - 3 = 1$ resource unit left.
4. Any of the 3 processes can be granted this 1 remaining unit, reaching its maximum requirement of 2 units.
5. That process completes, releases both units, and allows the remaining processes to complete sequentially.
6. Hence, deadlock is mathematically impossible."""
                    },
                    {
                        "qnum": 2, "topic": "Data Structures & Algorithms",
                        "text": "What is the worst-case time complexity of QuickSort and how can it be avoided in practice?",
                        "options": [
                            "O(n^2), avoided by choosing median-of-three or randomized pivot selection",
                            "O(n log n), already optimal",
                            "O(2^n), avoided by memoization",
                            "O(n), avoided by double hashing"
                        ],
                        "correct": 0,
                        "mat_key": ("Computer Science", "Data Structures & Algorithms"),
                        "solution": """**Step-by-Step Solution:**
1. **Worst Case:** QuickSort degrades to $O(n^2)$ when the chosen pivot is consistently the minimum or maximum element (e.g., partitioning an already-sorted array with fixed first or last element as pivot).
2. **Recurrence Relation:** $T(n) = T(n-1) + O(n) \\implies O(n^2)$.
3. **Mitigation:**
   - **Randomized Pivot Selection:** Randomly pick pivot index.
   - **Median-of-Three:** Choose the median of the first, middle, and last elements.
   - **Introsort:** Fall back to HeapSort ($O(n \\log n)$) if recursive depth exceeds $2 \\log n$."""
                    }
                ]
            }
        ]

        for p_data in papers_info:
            paper = db.query(PreviousPaper).filter(
                PreviousPaper.title == p_data["title"]
            ).first()
            if not paper:
                paper = PreviousPaper(
                    title=p_data["title"],
                    subject=p_data["subject"],
                    year=p_data["year"],
                    time_limit_minutes=p_data["time_limit_minutes"],
                    total_marks=p_data["total_marks"]
                )
                db.add(paper)
                db.commit()
                db.refresh(paper)

                for q in p_data["questions"]:
                    rel_id = material_map.get(q["mat_key"])
                    pq = PaperQuestion(
                        paper_id=paper.id,
                        question_number=q["qnum"],
                        topic=q["topic"],
                        question_text=q["text"],
                        options=q["options"],
                        correct_option=q["correct"],
                        step_by_step_solution=q["solution"],
                        related_material_id=rel_id
                    )
                    db.add(pq)
                db.commit()

        print("Solved previous papers seeded.")

        # 7. Seed Course Summaries
        summaries_data = [
            {
                "subject": "Biology",
                "topic": "Genetics & Molecular Biology",
                "title": "Comprehensive Genetics & Cellular Biology Summary",
                "overview": "Essential principles of inheritance, molecular biology, gene expression, and bioenergetics for quick pre-exam consolidation.",
                "key_points": [
                    "DNA replicates semi-conservatively in the 5' to 3' direction with leading and lagging strands.",
                    "Transcription converts DNA to mRNA via RNA Polymerase; Translation occurs at ribosomes using tRNA anticodons.",
                    "Mendel's laws of segregation and independent assortment explain monohybrid (3:1) and dihybrid (9:3:3:1) phenotypic ratios.",
                    "Cellular respiration generates ~32 ATP per glucose via Glycolysis, Krebs cycle, and Chemiosmosis.",
                    "Hardy-Weinberg equilibrium: p^2 + 2pq + q^2 = 1 under conditions of no mutation, random mating, and no selection."
                ],
                "quick_revision_notes": """# Rapid Revision: Biology Essentials
- **Central Dogma**: DNA --(Transcription)--> RNA --(Translation)--> Protein.
- **Stop Codons**: UAA, UAG, UGA. Start Codon: AUG (Methionine).
- **Mitochondrial Respiration**: Glycolysis (Cytosol, 2 ATP) -> Krebs Cycle (Matrix, 2 ATP) -> ETC (Inner Membrane, 28 ATP).
- **Photosynthesis**: Light reactions in Thylakoids generate NADPH & ATP; Calvin Cycle in Stroma fixes CO2 into G3P.""",
                "quiz_questions": [
                    {
                        "question": "Which enzyme unzips double-stranded DNA during replication?",
                        "options": ["DNA Polymerase", "DNA Helicase", "DNA Ligase", "Topoisomerase"],
                        "correct_option": 1,
                        "explanation": "Helicase disrupts hydrogen bonds between nucleotide base pairs to unwind the helix."
                    },
                    {
                        "question": "What is the expected phenotypic ratio in a standard Mendelian dihybrid F2 generation?",
                        "options": ["3:1", "1:2:1", "9:3:3:1", "1:1:1:1"],
                        "correct_option": 2,
                        "explanation": "Independent assortment of two heterozygous traits produces a 9:3:3:1 phenotypic ratio."
                    },
                    {
                        "question": "In which cellular compartment does the Citric Acid (Krebs) cycle take place?",
                        "options": ["Cytoplasm", "Mitochondrial Matrix", "Thylakoid Lumen", "Endoplasmic Reticulum"],
                        "correct_option": 1,
                        "explanation": "Krebs cycle enzymes reside within the mitochondrial matrix."
                    }
                ]
            },
            {
                "subject": "Mathematics",
                "topic": "Calculus & Linear Algebra",
                "title": "Calculus, Matrices & Probability High-Yield Summary",
                "overview": "Condensed summary of core differentiation rules, limit evaluation, matrix operations, and probabilistic theorems.",
                "key_points": [
                    "Limits: 0/0 and inf/inf require factorization, rationalization, or L'Hopital's derivative rule.",
                    "Derivative Power Rule: d/dx(x^n) = n*x^(n-1); Product Rule: (uv)' = u'v + uv'; Chain Rule: d/dx[f(g(x))] = f'(g(x)) * g'(x).",
                    "A square matrix is invertible if and only if its determinant is non-zero.",
                    "Eigenvalues satisfy the characteristic equation det(A - lambda * I) = 0.",
                    "Bayes' Theorem updates prior probabilities P(A) with evidence B to produce posterior P(A|B)."
                ],
                "quick_revision_notes": """# Rapid Revision: Mathematics Formula Sheet
- **Key Limit**: $\\lim_{x \\to 0} \\frac{\\sin x}{x} = 1$, $\\lim_{x \\to 0} \\frac{e^x - 1}{x} = 1$.
- **Integration by Parts**: $\\int u \\, dv = uv - \\int v \\, du$.
- **2x2 Inverse**: $A^{-1} = \\frac{1}{ad-bc} \\begin{pmatrix} d & -b \\\\ -c & a \\end{pmatrix}$.
- **Conditional Probability**: $P(A|B) = \\frac{P(A \\cap B)}{P(B)}$.""",
                "quiz_questions": [
                    {
                        "question": "What is the derivative of f(x) = ln(3x^2)?",
                        "options": ["2/x", "6x", "1/(3x^2)", "3/x"],
                        "correct_option": 0,
                        "explanation": "ln(3x^2) = ln(3) + 2 ln(x). The derivative is 0 + 2/x = 2/x."
                    },
                    {
                        "question": "If det(A) = 0 for a square matrix A, which statement is true?",
                        "options": ["A has full rank", "A is invertible", "A is singular and has no inverse", "All eigenvalues are 1"],
                        "correct_option": 2,
                        "explanation": "A determinant of zero indicates a singular matrix with non-trivial null space, hence no inverse exists."
                    },
                    {
                        "question": "What is the sum of probabilities of all elementary outcomes in a sample space?",
                        "options": ["0", "Infinity", "1", "Depends on sample size"],
                        "correct_option": 2,
                        "explanation": "By the axioms of probability, the total probability of the entire sample space equals 1."
                    }
                ]
            },
            {
                "subject": "Computer Science",
                "topic": "Systems, Databases & Algorithms",
                "title": "Computer Science Core: OS, SQL & DSA Summary",
                "overview": "Synthesized reference covering process concurrency, ACID transactions, relational schema design, and algorithm complexities.",
                "key_points": [
                    "Deadlock requires 4 simultaneous conditions: Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait.",
                    "Virtual Memory isolates processes through paging; thrashing occurs when page faults dominate CPU execution.",
                    "ACID transactions guarantee Atomicity, Consistency, Isolation, and Durability.",
                    "Indexes (B-Trees) speed up range and lookup queries from O(n) table scans to O(log n).",
                    "Dijkstra's Algorithm finds single-source shortest paths in O((V + E) log V) using min-heaps."
                ],
                "quick_revision_notes": """# Rapid Revision: Computer Science Core
- **Process States**: New -> Ready -> Running -> Waiting -> Terminated.
- **SQL Execution Order**: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT.
- **Hashing**: O(1) average lookup; Collision resolution: Chaining vs Open Addressing.
- **Tree Traversals**: In-order of BST yields elements in strictly sorted ascending order.""",
                "quiz_questions": [
                    {
                        "question": "Which SQL clause is evaluated BEFORE the SELECT clause?",
                        "options": ["ORDER BY", "LIMIT", "WHERE", "DISTINCT"],
                        "correct_option": 2,
                        "explanation": "WHERE filters source rows before column projections in SELECT are evaluated."
                    },
                    {
                        "question": "In-order traversal of a valid Binary Search Tree produces elements in:",
                        "options": ["Descending order", "Strictly ascending sorted order", "Breadth-first order", "Random order"],
                        "correct_option": 1,
                        "explanation": "Left -> Root -> Right traversal recursively outputs nodes in ascending sorted order."
                    },
                    {
                        "question": "Which process scheduling algorithm guarantees prevention of starvation?",
                        "options": ["Shortest Job First (SJF)", "Round Robin with Aging", "Priority Scheduling without Aging", "First-Come First-Served"],
                        "correct_option": 1,
                        "explanation": "Round Robin guarantees equal time slices, and aging dynamically elevates waiting processes."
                    }
                ]
            }
        ]

        for s_data in summaries_data:
            summary = db.query(CourseSummary).filter(
                CourseSummary.subject == s_data["subject"],
                CourseSummary.topic == s_data["topic"]
            ).first()
            if not summary:
                summary = CourseSummary(
                    subject=s_data["subject"],
                    topic=s_data["topic"],
                    title=s_data["title"],
                    overview=s_data["overview"],
                    key_points=s_data["key_points"],
                    quick_revision_notes=s_data["quick_revision_notes"],
                    quiz_questions=s_data["quiz_questions"],
                    is_ai_generated=False,
                    last_edited_by=teacher_user.id
                )
                db.add(summary)
        db.commit()
        print("Course summaries seeded.")

        # 8. Seed Guidance Courses & Roadmaps
        guidance_data = [
            {
                "title": "B.Tech Computer Science & Artificial Intelligence",
                "stream": "Engineering & Technology",
                "degree_level": "Undergraduate (4 Years)",
                "description": "Premier engineering degree covering machine learning algorithms, distributed computing, neural networks, software architecture, and high-performance computing.",
                "eligibility": "10+2 / Grade 12 with Physics, Mathematics, and Chemistry/CS with minimum 75% aggregate.",
                "fees_range": "$4,000 - $18,000 per academic year (varies by public vs private institution)",
                "scope_and_careers": [
                    "AI/Machine Learning Engineer ($95,000 - $160,000)",
                    "Software Systems Architect",
                    "Data Scientist & Analytics Consultant",
                    "Cloud Platform Engineer"
                ],
                "entrance_exams": [
                    {"name": "JEE Main & Advanced", "date": "January / April & May", "importance": "National Primary"},
                    {"name": "BITSAT / State CETs", "date": "May - June", "importance": "State / Premier University"}
                ],
                "roadmap_steps": [
                    {"stage": "Year 1", "title": "Core Foundations", "description": "Discrete Mathematics, Linear Algebra, C/C++ programming, and Computer Architecture."},
                    {"stage": "Year 2", "title": "Data Structures & Systems", "description": "Data Structures, Algorithms, Operating Systems, Database Management, and Python for Data Science."},
                    {"stage": "Year 3", "title": "Specialization & Machine Learning", "description": "Machine Learning, Deep Learning, Cloud Computing, Open-Source Contributions, and Summer Internship."},
                    {"stage": "Year 4", "title": "Capstone & Industry Transition", "description": "Major AI thesis project, research publications, campus recruitment, and technical interviews."}
                ],
                "matching_tags": ["computer science", "mathematics", "software & ai", "programming", "algorithms", "engineering"]
            },
            {
                "title": "B.S. Bioinformatics & Computational Biology",
                "stream": "Life Sciences & Computing",
                "degree_level": "Undergraduate / Integrated (4 Years)",
                "description": "Interdisciplinary field leveraging computational power and statistical modeling to decipher biological genomes, drug discovery, and molecular dynamics.",
                "eligibility": "10+2 with Biology and Mathematics or Computer Science, minimum 60% aggregate.",
                "fees_range": "$3,500 - $14,000 per academic year",
                "scope_and_careers": [
                    "Bioinformatics Research Scientist ($80,000 - $135,000)",
                    "Genomic Data Analyst in Pharma",
                    "Computational Drug Designer",
                    "Biotech Software Specialist"
                ],
                "entrance_exams": [
                    {"name": "NEET / CUET-UG (Biology + Math)", "date": "May - June", "importance": "Central Universities"},
                    {"name": "Institute-specific Biotech Entrances", "date": "June", "importance": "Specialized"}
                ],
                "roadmap_steps": [
                    {"stage": "Year 1", "title": "Dual Foundations", "description": "Cell Biology, Genetics, Calculus, and Introductory Python programming."},
                    {"stage": "Year 2", "title": "Molecular Biology & Data Tools", "description": "Molecular Genetics, Biochemistry, Algorithms, and Biostatistics with R."},
                    {"stage": "Year 3", "title": "Genomics & Machine Learning", "description": "Sequence Analysis, Structural Bioinformatics, Molecular Modeling, and Machine Learning on Omics data."},
                    {"stage": "Year 4", "title": "Research Thesis & Industry Lab", "description": "Drug discovery capstone, genomic pipeline development, and research lab placement."}
                ],
                "matching_tags": ["biology", "computer science", "research / phd", "genetics", "biotechnology", "data & finance"]
            },
            {
                "title": "B.S. / B.Math Data Science & Applied Statistics",
                "stream": "Mathematical & Statistical Sciences",
                "degree_level": "Undergraduate (3-4 Years)",
                "description": "Rigorous quantitative program combining statistical inference, probabilistic modeling, predictive analytics, and big data engineering.",
                "eligibility": "10+2 with strong Mathematics background (minimum 70% in Mathematics).",
                "fees_range": "$3,000 - $12,000 per academic year",
                "scope_and_careers": [
                    "Quantitative Financial Analyst (Quant)",
                    "Risk & Actuarial Scientist ($85,000 - $150,000)",
                    "Data Analytics Director",
                    "Statistical Modeler"
                ],
                "entrance_exams": [
                    {"name": "ISI / CMI Entrance Exams", "date": "May", "importance": "Premier Math Institutes"},
                    {"name": "CUET-UG Mathematics", "date": "May - June", "importance": "Central Universities"}
                ],
                "roadmap_steps": [
                    {"stage": "Year 1", "title": "Mathematical Core", "description": "Real Analysis, Multivariable Calculus, Linear Algebra, and Probability Theory."},
                    {"stage": "Year 2", "title": "Inference & Computing", "description": "Statistical Inference, Regression Analysis, Time Series, and SQL/Python data handling."},
                    {"stage": "Year 3", "title": "Advanced Analytics & ML", "description": "Bayesian Methods, Stochastic Processes, Machine Learning, and Econometric Modeling."},
                    {"stage": "Year 4", "title": "Industry Capstone", "description": "Financial modeling, quantitative portfolio optimization project, and industry placement."}
                ],
                "matching_tags": ["mathematics", "data & finance", "statistics", "calculus", "theoretical / research"]
            },
            {
                "title": "MBBS / Biomedical Sciences",
                "stream": "Medical & Clinical Sciences",
                "degree_level": "Professional Undergraduate (5.5 Years)",
                "description": "Comprehensive clinical and surgical medical education leading to licensed medical doctor practice and medical research.",
                "eligibility": "10+2 with Physics, Chemistry, Biology with minimum 50-60% aggregate.",
                "fees_range": "$1,500 (Govt College) to $25,000 (Private College) per year",
                "scope_and_careers": [
                    "Physician / Medical Doctor ($120,000 - $250,000+)",
                    "Clinical Specialist (Surgeon, Cardiologist, Neurologist)",
                    "Medical Research Director",
                    "Public Health Officer (WHO / CDC)"
                ],
                "entrance_exams": [
                    {"name": "NEET-UG", "date": "First Sunday of May", "importance": "Mandatory National Exam"}
                ],
                "roadmap_steps": [
                    {"stage": "Pre-Clinical (1.5 Yrs)", "title": "Anatomy, Physiology, Biochemistry", "description": "Human body systems, histological structure, and biochemical pathways."},
                    {"stage": "Para-Clinical (1.5 Yrs)", "title": "Pathology, Pharmacology, Microbiology", "description": "Disease etiology, microbial defense, mechanisms of pharmacological action."},
                    {"stage": "Clinical (2 Yrs)", "title": "Medicine, Surgery, Pediatrics, OBGYN", "description": "Hospital bedside rounds, patient clinical examination, diagnostic procedures."},
                    {"stage": "Internship (1 Yr)", "title": "Compulsory Rotatory Residency", "description": "Hands-on emergency and clinical duty across rural and tertiary hospitals."}
                ],
                "matching_tags": ["biology", "medicine & healthcare", "practical / hands-on", "genetics", "physiology"]
            }
        ]

        for g_data in guidance_data:
            course = db.query(GuidanceCourse).filter(
                GuidanceCourse.title == g_data["title"]
            ).first()
            if not course:
                course = GuidanceCourse(
                    title=g_data["title"],
                    stream=g_data["stream"],
                    degree_level=g_data["degree_level"],
                    description=g_data["description"],
                    eligibility=g_data["eligibility"],
                    fees_range=g_data["fees_range"],
                    scope_and_careers=g_data["scope_and_careers"],
                    entrance_exams=g_data["entrance_exams"],
                    roadmap_steps=g_data["roadmap_steps"],
                    matching_tags=g_data["matching_tags"]
                )
                db.add(course)
        db.commit()
        print("Guidance courses seeded.")

        print("=== Database seeding completed successfully! ===")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
