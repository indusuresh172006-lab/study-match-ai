# StudyMatch AI

> **"Learn Together. Teach Each Other. Improve Faster. Plan Your Future."**

StudyMatch AI is a modern web application designed for peer-learning study group matching and personalized higher-studies and career guidance. It dynamically tracks student topic proficiencies in real-time via an adaptive **Skill Profile Engine** (labeling topics as *weak*, *average*, or *strong*), connecting test performance directly to learning materials, career roadmaps, AI personal mentoring, and peer study groups.

---

## 🛠️ Technology Stack

- **Frontend**: React 19, React Router v7, Recharts, Axios, Modern Responsive CSS3 (Desktop Sidebar + Mobile Bottom Navigation)
- **Backend**: Python 3.12, FastAPI (REST APIs, JWT authentication with role-based checks, Pydantic v2 schemas)
- **Database & Migrations**: PostgreSQL, SQLAlchemy 2.0 ORM, psycopg2, Alembic
- **Machine Learning & Analytics**: scikit-learn, Pandas, NumPy, SciPy (Weighted multi-factor course recommendation engine)
- **AI Mentoring & Chatbot (RAG)**: Multi-turn academic mentor powered by Gemini 1.5 Flash via backend Google Generative AI API with TF-IDF vector embeddings over teacher-curated guidance documents

---

## 🚀 The Core Student Support Modules

### Module 1: Study Materials with Weak-Topic Prioritization
- Browse comprehensive study notes, formula sheets, important questions, and learning resources by Subject (`Biology`, `Mathematics`, `Computer Science`) and Topic.
- Students see syllabus subjects and diagnostic questions scoped to their registered course, board/institution, and year/semester. Teachers curate the matching subjects, topics, and question sets in Content Management.
- **Weak Topic Prioritization**: Automatically prioritizes materials for a student's identified weak topics to the top of the feed with a distinct visual badge.
- Search, filter by type, bookmark/save materials for fast review.
- Teacher role capability to publish, edit, and delete materials.

### Module 2: Course Summaries & Rapid Revision
- High-yield summaries, formulas, and key points for Biology, Mathematics, and Computer Science (extensible to any subject).
- Fast revision view with concise cheat sheets and an interactive 3-question rapid concept retention quiz with instant scoring.
- Teachers can edit summaries or generate new ones.

### Module 3: Personal Mentoring through AI Assistance
- 24/7 dedicated academic mentor that retrieves the student's real-time weak/strong topics, test scores, and learning goals.
- Provides concept breakdowns, study timetables, and targeted exam advice.
- Includes dynamic suggested-question chips, persistent chat history per student, and secure backend-only API key handling.

### Module 4: Higher Studies & Course Guidance
- **Academic Roadmaps**: Step-by-step career journeys (Science, Commerce, Humanities) from Plus Two / 12th Standard through Undergraduate and Postgraduate specializations with actionable next steps.
- **ML Course Recommender**: Combines the student's `SkillProfile` strengths (60%) and an 8-question Interest Questionnaire (40%) to calculate match percentages (0–100%) and plain-language reasoning (e.g., *"Strong in Mathematics and Computer Science"*).
- **Side-by-Side Course Comparison**: Compare up to 3 courses across duration, fees, eligibility, accepted entrance exams, target job roles, salary ranges, and top colleges.
- **Career Path Explorer**: Detailed 3-tier career progression (Entry → Mid → Senior), salary outlooks, higher-study options, and recommended professional certifications.
- **Entrance Exams & Colleges**: Directory of national entrance exams (JEE Main, JEE Adv, NEET-UG, CUET-UG, KEAM, CLAT, GATE, CAT, NATA) and NIRF-ranked institutions with dates, eligibility, and links to official portals.
- **Scholarships & Study Abroad**: Categorized financial aid opportunities (Merit, Need-based) and country dossiers (USA, UK, Germany, Canada, Australia) with visa work rights and tuition estimates.
- **Application Checklist & Deadlines**: Task manager with completion toggles and upcoming deadline reminders with countdown badges.
- **Academic Counselling Flow**: Students can request 1-on-1 career counselling (Online or In-person); teachers review, schedule, and provide feedback notes.

### Peer Learning & Teacher Support
- Teachers create course-scoped classes and share join codes; students can enroll during registration or later from Study Groups.
- Teachers can import CSV/XLSX marks (student_email, subject, topic, score, max_score) to update topic skill profiles.
- Teachers generate study groups only among students in the same course, board/institution, and year/semester; strong peers are paired with students who have matching weak topics.
- Proposed groups stay hidden from students until the class teacher approves them. Availability matching separates online and offline sessions and includes "either" preferences.
- Students can request a teacher-led study session when no peer match covers a weak topic. Requests appear in the Teacher Dashboard and students can track teacher responses in Guidance.
- Teachers can review generated revision notes and mock tests before students can access them. Class group progress and repeated quiz-score declines are available in teacher reporting; teachers can rebuild a selected class's peer groups from the at-risk list.
- Students with no published matching syllabus are told to ask a teacher to tag or add the appropriate course content rather than being shown unrelated material.

Teacher-uploaded guidance documents are pending by default and only become chatbot sources after explicit teacher approval.

### Module 5: Adaptive Mock Tests & Previous Papers
- **Adaptive Mock Test Engine**:
  - Live timer with visual countdown alerts and automatic submission.
  - Multi-format questions: Multiple Choice (MCQ), True/False, and Short Answer.
  - Question Navigation Grid: tracks questions as *Answered* (Green), *Marked for Review* (Purple), *Active*, or *Unanswered* (Gray).
  - **⚡ Adaptive Practice Generator**: One-click drill generator that allocates 70% of questions directly from the student's diagnosed weak topics.
  - **Skill Profile Auto-Update**: Every completed test recalculates topic mastery scores in the database.
- **Recharts Performance Analytics**:
  - Topic-wise accuracy Bar Chart (`BarChart`).
  - Historical score progression Line Chart (`LineChart`).
  - Class average accuracy comparison.
  - Strengths and weaknesses chips, with direct links to revise weak topic notes.
  - Full solution review with step-by-step official explanations.
- **Solved Previous Question Papers Library**:
  - Filter past board and entrance examinations by Exam, Subject, Year, and Topic tag.
  - PDF paper download and solution key preview.
  - Timed examination mode with automatic scoring and **remediation links** mapping wrong answers to study materials.
  - Teacher upload and approval flow.
  - Approved PDF files are stored by the backend and downloadable from the student paper library.
  - Teacher-authored mock tests are submitted for review, tagged to an entrance exam or assessment, and only published after approval.

### Module 6: AI Chatbot "StudyMatch Assistant" (RAG)
- **RAG Knowledge Base**: Uses teacher-verified guidance documents (exam brochures, syllabi, career guides) chunked and indexed into vector embeddings.
- **Context Injection**: Each query retrieves the top-5 most relevant document chunks and combines them with the student's active weak/strong topics and active peer-group matches. Paper and mock-test questions also search approved resources by subject, exam, and requested year range.
- **Verified Sources & Disclaimer**: Every response cites the source documents used and appends an official verification advisory.
- **Persistent Multi-Session Threads**: Students can create new discussion threads, switch between sessions, or delete threads.
- **Global Floating Chat Widget**: Accessible from the bottom right corner of every page (`🤖 StudyMatch AI`), providing instant academic assistance anywhere in the app.
- **Faculty Curation**: Teachers can upload and verify guidance documents directly from the Teacher Dashboard.

---

## 🔄 Connecting Everything: The Skill Profile Engine

```
       [ Mock Tests / Paper Attempts ]
                      │
                      ▼
            [ Topic Evaluation ]
     (Score <50%: Weak | 50-75%: Avg | >75%: Strong)
                      │
                      ▼
             [ Skill Profile ]
                      │
    ┌─────────────────┼─────────────────┐
    ▼                 ▼                 ▼
[ Study Materials ]  [ Course Guidance ]  [ AI Mentor ]
(Weak topics first)  (Strength alignment) (Focuses advice)
```

1. **Assessments** (adaptive mock tests and past paper attempts) evaluate topic accuracy.
2. The **Skill Profile** dynamically updates topic mastery scores.
3. **Study Materials** sort weak-topic notes to the top of the feed.
4. **Mock Tests** calibrate question difficulty based on weak vs strong ratings.
5. **Course Guidance** maps strong subjects to career roadmaps and flags prerequisites.
6. **AI Mentor & Assistant** proactively addresses weak topics in conversation.
7. **Student Dashboard** provides real-time progress charts and action recommendations.

---

## ⚙️ Setup & Installation Instructions

### 1. Prerequisites
- **Python**: 3.12+
- **Node.js**: 18+ (with `npm`)
- **PostgreSQL**: 14+ running on `localhost:5432`

---

### 2. Database Configuration
Create a PostgreSQL database named `studymatch_db`:
```sql
CREATE DATABASE studymatch_db;
```

---

### 3. Backend Setup

1. **Navigate to the backend directory**:
   ```powershell
   cd backend
   ```

2. **Configure Environment Variables**:
   Ensure `.env` exists in `backend/` with the following configuration:
   ```env
   DB_USER=postgres
   DB_PASSWORD=admin123
   DB_HOST=127.0.0.1
   DB_PORT=5432
   DB_NAME=studymatch_db

   JWT_SECRET=studymatch_jwt_secret_key_change_in_production_2026

   GEMINI_API_KEY=YOUR_GEMINI_API_KEY
   LLM_API_KEY=YOUR_GEMINI_API_KEY
   STUDYMATCH_UPLOAD_DIR="C:\studymatch-uploads"
   ```
   Configure `STUDYMATCH_UPLOAD_DIR` as persistent storage in deployments; otherwise uploaded PDFs are stored under `backend/uploads/`.

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run Database Migrations (Alembic)**:
   ```powershell
   python -m alembic upgrade head
   ```
   Existing databases stamped at revision `6f2c1a8d4e90` are recognized and their partially applied course-syllabus schema is reconciled by the latest migration.

5. **Seed Sample Data**:
   ```powershell
   python seed_data.py
   python seed_phase1.py
   python seed_diploma_computer_sem3.py
   ```
   `seed_phase1.py` also upserts diploma lateral-entry guidance when rerun, even if the general guidance catalogue was already seeded. `seed_diploma_computer_sem3.py` adds the SITTTR Revision 2021 Computer Engineering Semester III course list, plus starter practice topics, quizzes, and study notes scoped to Polytechnic College Kannur. The course list is from the official SITTTR catalog; teachers should verify the starter topics and questions against the detailed syllabus.

6. **Start the FastAPI Server**:
   ```powershell
   uvicorn main:app --reload --port 8000
   ```
   Interactive Swagger documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

### 4. Frontend Setup

1. **Navigate to the frontend directory**:
   ```powershell
   cd frontend
   ```

2. **Install Dependencies**:
   ```powershell
   npm install
   ```

3. **Start the Development Server**:
   ```powershell
   npm run dev
   ```
   Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🔑 Demo Account Credentials

| Role | Email | Password | Features Accessible |
|---|---|---|---|
| **Student** | `student@studymatch.ai` | `password123` | Dashboard, Study Materials, Course Guidance, AI Mentor, Mock Tests, Summaries, Solved Papers, Global Floating Chatbot |
| **Teacher** | `teacher@studymatch.ai` | `password123` | All student features + Teacher Dashboard, Class Weak Topics Heatmap, At-Risk Student Interventions, Counselling Queue, Guidance Doc Curation, Test Authoring |

---

## 🧪 Running Tests

### Focused Class, Group, and Chatbot Regression Tests
```powershell
cd backend
python -m pytest test_project_features.py -q
```

### 1. Core Feature Unit Tests (10 Tests)
```powershell
python backend/test_api.py
```
*Tests authentication, skill profile aggregation, weak-topic material sorting, bookmarking, course guidance, AI mentoring, adaptive mock tests, rapid quizzes, and paper remediation links.*

### 2. Extended Modules 4, 5, 6 Integration Tests
```powershell
python backend/test_phase1.py
```
*Tests roadmaps, exams, colleges, ML course recommendations, side-by-side comparison, career paths, scholarships, study abroad, application checklist, counselling workflow, question papers library, mock test attempts with skill updates, and RAG chatbot generation with source citations.*

### 3. Frontend Production Build Verification
```powershell
cd frontend
npm run build
```

---

## 📡 REST API Endpoints Overview

| Tag | Method | Endpoint | Description | Auth |
|---|---|---|---|---|
| **Auth** | `POST` | `/register` | Register student or teacher | Public |
| **Auth** | `POST` | `/token` | OAuth2 login returning JWT token | Public |
| **Profile** | `GET` | `/profile/me` | Fetch active student profile | Student/Teacher |
| **Classes** | `POST/GET` | `/api/v1/classes` | Create or list teacher classes / student enrollments | Teacher/Student |
| **Classes** | `POST` | `/api/v1/classes/join` | Enroll in a class with a join code | Student |
| **Classes** | `GET` | `/api/v1/classes/{id}/students` | View the class roster | Teacher |
| **Classes** | `POST` | `/api/v1/classes/{id}/marks/import` | Import CSV/XLSX marks and update skills | Teacher |
| **Groups** | `POST` | `/api/v1/groups/generate` | Generate proposed groups for a class | Teacher |
| **Groups** | `PATCH` | `/api/v1/groups/{id}/review` | Approve or reject a proposed group | Teacher |
| **Schedules** | `POST/GET` | `/api/v1/schedules` | Add or list weekly availability and study mode | Student |
| **Skills** | `GET` | `/skill-profile/summary` | Skill profile with weak/strong topics | Student |
| **Materials** | `GET` | `/materials` | Paginated study materials (weak topics first) | Student/Teacher |
| **Materials** | `POST` | `/materials` | Publish new study material | Teacher |
| **Materials** | `POST` | `/materials/{id}/bookmark` | Toggle saved bookmark | Student |
| **Guidance** | `GET` | `/api/v1/guidance/roadmap` | Academic roadmap stages by stream | Student/Teacher |
| **Guidance** | `GET` | `/api/v1/guidance/exams` | Entrance exams with filters & syllabus | Student/Teacher |
| **Guidance** | `GET` | `/api/v1/guidance/colleges` | Colleges with NIRF rankings & fees | Student/Teacher |
| **Guidance** | `GET` | `/api/v1/guidance/courses` | Complete course directory | Student/Teacher |
| **Guidance** | `GET` | `/api/v1/guidance/courses/recommend` | ML course recommendation engine | Student |
| **Guidance** | `GET` | `/api/v1/guidance/courses/compare` | Compare 2–3 courses side-by-side | Student |
| **Guidance** | `GET` | `/api/v1/guidance/courses/{id}/career-path` | 3-tier career progression roadmap | Student |
| **Guidance** | `GET` | `/api/v1/guidance/scholarships` | Scholarships directory (Merit/Need) | Student |
| **Guidance** | `GET` | `/api/v1/guidance/study-abroad` | Country dossiers & visa work rights | Student |
| **Guidance** | `GET/POST` | `/api/v1/guidance/checklist` | Student application task tracker | Student |
| **Guidance** | `POST` | `/api/v1/guidance/counselling` | Request career counselling session | Student |
| **Guidance** | `GET/PATCH` | `/api/v1/guidance/counselling` | View & schedule counselling inquiries | Teacher/Student |
| **Tests** | `GET/POST` | `/api/v1/tests` | List & create mock tests | Student/Teacher |
| **Tests** | `POST` | `/api/v1/tests/{id}/start` | Begin timed test attempt | Student |
| **Tests** | `POST` | `/api/v1/tests/{id}/submit` | Auto-grade attempt & update SkillProfile | Student |
| **Tests** | `GET` | `/api/v1/tests/attempts/{id}/result` | Result breakdown with class average | Student |
| **Tests** | `POST` | `/api/v1/tests/adaptive` | Generate test targeting weak topics | Student |
| **Papers** | `GET/POST` | `/api/v1/papers` | Browse & upload solved question papers | Student/Teacher |
| **Papers** | `PATCH` | `/api/v1/papers/{id}/approve` | Approve submitted question paper | Teacher |
| **Chatbot** | `POST` | `/api/v1/chat/sessions` | Create persistent discussion session | Student |
| **Chatbot** | `GET` | `/api/v1/chat/sessions` | List student's discussion sessions | Student |
| **Chatbot** | `POST` | `/api/v1/chat/sessions/{id}/message` | Send message (RAG + Skill context) | Student |
| **Chatbot** | `GET/POST`| `/api/v1/chat/documents` | Browse & upload verified RAG documents | Teacher/Student |
| **Teacher** | `GET` | `/teacher/dashboard` | Class weak topic heatmap & at-risk alerts | Teacher |
