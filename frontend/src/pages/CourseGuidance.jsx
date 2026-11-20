import { useState, useEffect } from "react";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import EmptyState from "../components/EmptyState";

function CourseGuidance() {
  const [activeTab, setActiveTab] = useState("recommended");

  // Recommended Courses State
  const [courses, setCourses] = useState([]);
  const [coursesLoading, setCoursesLoading] = useState(false);
  const [coursesError, setCoursesError] = useState(null);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [streamFilter, setStreamFilter] = useState("All");

  // Comparison State (up to 3 courses)
  const [compareIds, setCompareIds] = useState([]);
  const [compareData, setCompareData] = useState(null);
  const [comparingLoading, setComparingLoading] = useState(false);
  const [showCompareModal, setShowCompareModal] = useState(false);

  // Career Path State
  const [careerPathData, setCareerPathData] = useState(null);
  const [careerPathLoading, setCareerPathLoading] = useState(false);
  const [showCareerModal, setShowCareerModal] = useState(false);

  // Questionnaire Modal State
  const [showQuizModal, setShowQuizModal] = useState(false);
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [quizLoading, setQuizLoading] = useState(false);
  const [submittingQuiz, setSubmittingQuiz] = useState(false);

  // Roadmap State
  const [roadmapItems, setRoadmapItems] = useState([]);
  const [roadmapLoading, setRoadmapLoading] = useState(false);
  const [roadmapStream, setRoadmapStream] = useState("All");

  // Exams State
  const [exams, setExams] = useState([]);
  const [examsLoading, setExamsLoading] = useState(false);
  const [examSearch, setExamSearch] = useState("");
  const [selectedExam, setSelectedExam] = useState(null);

  // Colleges State
  const [colleges, setColleges] = useState([]);
  const [collegesLoading, setCollegesLoading] = useState(false);
  const [collegeSearch, setCollegeSearch] = useState("");

  // Scholarships State
  const [scholarships, setScholarships] = useState([]);
  const [scholarshipsLoading, setScholarshipsLoading] = useState(false);
  const [scholarshipCategory, setScholarshipCategory] = useState("All");

  // Study Abroad State
  const [studyAbroad, setStudyAbroad] = useState([]);
  const [studyAbroadLoading, setStudyAbroadLoading] = useState(false);

  // Checklist & Reminders State
  const [checklist, setChecklist] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [checklistLoading, setChecklistLoading] = useState(false);
  const [showAddChecklistModal, setShowAddChecklistModal] = useState(false);
  const [newChecklistTitle, setNewChecklistTitle] = useState("");
  const [newChecklistCategory, setNewChecklistCategory] = useState("Exam");
  const [newChecklistDeadline, setNewChecklistDeadline] = useState("");

  // Counselling Requests State
  const [counsellingList, setCounsellingList] = useState([]);
  const [counsellingLoading, setCounsellingLoading] = useState(false);
  const [showCounsellingModal, setShowCounsellingModal] = useState(false);
  const [counsellingMessage, setCounsellingMessage] = useState("");
  const [counsellingMode, setCounsellingMode] = useState("Online");
  const [submittingCounselling, setSubmittingCounselling] = useState(false);

  // ─────────────────────────────────────────────
  // Fetch Functions
  // ─────────────────────────────────────────────

  const fetchRecommendations = async () => {
    setCoursesLoading(true);
    setCoursesError(null);
    try {
      const res = await api.get("/api/v1/guidance/courses/recommend");
      setCourses(res.data);
    } catch (err) {
      console.error(err);
      try {
        const fallback = await api.get("/api/v1/guidance/courses");
        setCourses(fallback.data.items || []);
      } catch (e2) {
        setCoursesError("Failed to load course recommendations.");
      }
    } finally {
      setCoursesLoading(false);
    }
  };

  const fetchRoadmap = async () => {
    setRoadmapLoading(true);
    try {
      const streamParam = roadmapStream !== "All" ? `?stream=${roadmapStream}` : "";
      const res = await api.get(`/api/v1/guidance/roadmap${streamParam}`);
      setRoadmapItems(res.data);
    } catch (err) {
      console.error("Roadmap fetch error:", err);
    } finally {
      setRoadmapLoading(false);
    }
  };

  const fetchExams = async () => {
    setExamsLoading(true);
    try {
      const searchParam = examSearch ? `?search=${encodeURIComponent(examSearch)}` : "";
      const res = await api.get(`/api/v1/guidance/exams${searchParam}`);
      setExams(res.data.items || []);
    } catch (err) {
      console.error("Exams fetch error:", err);
    } finally {
      setExamsLoading(false);
    }
  };

  const fetchColleges = async () => {
    setCollegesLoading(true);
    try {
      const searchParam = collegeSearch ? `?search=${encodeURIComponent(collegeSearch)}` : "";
      const res = await api.get(`/api/v1/guidance/colleges${searchParam}`);
      setColleges(res.data.items || []);
    } catch (err) {
      console.error("Colleges fetch error:", err);
    } finally {
      setCollegesLoading(false);
    }
  };

  const fetchScholarships = async () => {
    setScholarshipsLoading(true);
    try {
      const catParam = scholarshipCategory !== "All" ? `?category=${scholarshipCategory}` : "";
      const res = await api.get(`/api/v1/guidance/scholarships${catParam}`);
      setScholarships(res.data.items || []);
    } catch (err) {
      console.error("Scholarships fetch error:", err);
    } finally {
      setScholarshipsLoading(false);
    }
  };

  const fetchStudyAbroad = async () => {
    setStudyAbroadLoading(true);
    try {
      const res = await api.get("/api/v1/guidance/study-abroad");
      setStudyAbroad(res.data || []);
    } catch (err) {
      console.error("Study abroad fetch error:", err);
    } finally {
      setStudyAbroadLoading(false);
    }
  };

  const fetchChecklistAndReminders = async () => {
    setChecklistLoading(true);
    try {
      const [clRes, remRes] = await Promise.all([
        api.get("/api/v1/guidance/checklist"),
        api.get("/api/v1/guidance/reminders"),
      ]);
      setChecklist(clRes.data || []);
      setReminders(remRes.data || []);
    } catch (err) {
      console.error("Checklist fetch error:", err);
    } finally {
      setChecklistLoading(false);
    }
  };

  const fetchCounsellingRequests = async () => {
    setCounsellingLoading(true);
    try {
      const res = await api.get("/api/v1/guidance/counselling");
      setCounsellingList(res.data || []);
    } catch (err) {
      console.error("Counselling fetch error:", err);
    } finally {
      setCounsellingLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  useEffect(() => {
    if (activeTab === "roadmap") fetchRoadmap();
    if (activeTab === "exams") fetchExams();
    if (activeTab === "colleges") fetchColleges();
    if (activeTab === "scholarships") fetchScholarships();
    if (activeTab === "study_abroad") fetchStudyAbroad();
    if (activeTab === "checklist") fetchChecklistAndReminders();
    if (activeTab === "counselling") fetchCounsellingRequests();
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === "roadmap") fetchRoadmap();
  }, [roadmapStream]);

  // ─────────────────────────────────────────────
  // Questionnaire Handlers
  // ─────────────────────────────────────────────
  const openQuestionnaire = async () => {
    setShowQuizModal(true);
    setQuizLoading(true);
    try {
      const res = await api.get("/api/v1/guidance/questionnaire/questions");
      setQuizQuestions(res.data || []);
      const initAnswers = {};
      (res.data || []).forEach((q) => {
        initAnswers[q.id] = 0;
      });
      setQuizAnswers(initAnswers);
    } catch (err) {
      console.error("Questionnaire questions fetch error:", err);
    } finally {
      setQuizLoading(false);
    }
  };

  const handleQuizSubmit = async (e) => {
    e.preventDefault();
    setSubmittingQuiz(true);
    try {
      const answersPayload = Object.entries(quizAnswers).map(([qId, optIdx]) => ({
        question_id: Number(qId),
        selected_option_index: Number(optIdx),
      }));
      await api.post("/api/v1/guidance/questionnaire/submit", { answers: answersPayload });
      setShowQuizModal(false);
      await fetchRecommendations();
    } catch (err) {
      console.error(err);
      alert("Failed to submit questionnaire. Please try again.");
    } finally {
      setSubmittingQuiz(false);
    }
  };

  // ─────────────────────────────────────────────
  // Compare Handlers
  // ─────────────────────────────────────────────
  const toggleCompareId = (id) => {
    if (compareIds.includes(id)) {
      setCompareIds(compareIds.filter((x) => x !== id));
    } else {
      if (compareIds.length >= 3) {
        alert("You can compare at most 3 courses side-by-side.");
        return;
      }
      setCompareIds([...compareIds, id]);
    }
  };

  const handleCompareClick = async () => {
    if (compareIds.length < 2) {
      alert("Please select at least 2 courses to compare.");
      return;
    }
    setComparingLoading(true);
    setShowCompareModal(true);
    try {
      const res = await api.get(`/api/v1/guidance/courses/compare?ids=${compareIds.join(",")}`);
      setCompareData(res.data.courses || []);
    } catch (err) {
      console.error("Comparison error:", err);
      alert("Failed to load course comparison.");
      setShowCompareModal(false);
    } finally {
      setComparingLoading(false);
    }
  };

  // ─────────────────────────────────────────────
  // Career Path Handlers
  // ─────────────────────────────────────────────
  const handleOpenCareerPath = async (courseId) => {
    setCareerPathLoading(true);
    setShowCareerModal(true);
    try {
      const res = await api.get(`/api/v1/guidance/courses/${courseId}/career-path`);
      setCareerPathData(res.data);
    } catch (err) {
      console.error("Career path error:", err);
      alert("Failed to load career path details.");
      setShowCareerModal(false);
    } finally {
      setCareerPathLoading(false);
    }
  };

  // ─────────────────────────────────────────────
  // Checklist Actions
  // ─────────────────────────────────────────────
  const toggleChecklistItem = async (item) => {
    try {
      await api.patch(`/api/v1/guidance/checklist/${item.id}`, {
        is_completed: !item.is_completed,
      });
      setChecklist(
        checklist.map((c) => (c.id === item.id ? { ...c, is_completed: !c.is_completed } : c))
      );
    } catch (err) {
      console.error("Error toggling checklist item:", err);
    }
  };

  const handleAddChecklist = async (e) => {
    e.preventDefault();
    if (!newChecklistTitle.trim()) return;
    try {
      await api.post("/api/v1/guidance/checklist", {
        title: newChecklistTitle,
        category: newChecklistCategory,
        deadline: newChecklistDeadline || null,
      });
      setNewChecklistTitle("");
      setNewChecklistDeadline("");
      setShowAddChecklistModal(false);
      fetchChecklistAndReminders();
    } catch (err) {
      console.error("Error adding checklist item:", err);
    }
  };

  // ─────────────────────────────────────────────
  // Counselling Submission
  // ─────────────────────────────────────────────
  const handleCounsellingSubmit = async (e) => {
    e.preventDefault();
    if (!counsellingMessage.trim()) return;
    setSubmittingCounselling(true);
    try {
      await api.post("/api/v1/guidance/counselling", {
        message: counsellingMessage,
        preferred_mode: counsellingMode,
      });
      setCounsellingMessage("");
      setShowCounsellingModal(false);
      alert("Counselling request submitted! Your teacher will review and schedule a session.");
      if (activeTab === "counselling") fetchCounsellingRequests();
    } catch (err) {
      console.error("Error submitting counselling request:", err);
      alert("Failed to submit request.");
    } finally {
      setSubmittingCounselling(false);
    }
  };

  // Filtered courses
  const displayedCourses =
    streamFilter === "All"
      ? courses
      : courses.filter((c) => c.stream?.toLowerCase().includes(streamFilter.toLowerCase()));

  return (
    <div className="course-guidance-page compact-layout">
      {/* Sleek Compact Header */}
      <div className="page-header-row compact-header">
        <div>
          <h2>🎓 Higher Studies & Career Guidance</h2>
          <p className="page-subtitle">
            Personalized academic roadmaps, entrance exams, premier colleges, scholarships, and ML-backed recommendations.
          </p>
        </div>
        <div className="header-action-group">
          <button
            className="action-btn-secondary btn-sm"
            onClick={() => setShowCounsellingModal(true)}
          >
            💬 Request Counselling
          </button>
          <button
            className="action-btn-primary btn-sm"
            onClick={openQuestionnaire}
          >
            ✍️ Retake Questionnaire
          </button>
        </div>
      </div>

      {/* Navigation Tabs — High Density, Wrap-Friendly Pills */}
      <div className="guidance-tabs-nav compact-tabs">
        {[
          { key: "recommended", label: "🌟 Recommended" },
          { key: "roadmap", label: "🗺️ Roadmap" },
          { key: "exams", label: "📝 Exams" },
          { key: "colleges", label: "🏛️ Colleges" },
          { key: "scholarships", label: "💰 Scholarships" },
          { key: "study_abroad", label: "🌍 Study Abroad" },
          { key: "checklist", label: "✅ Checklist" },
          { key: "counselling", label: "🤝 Counselling" },
        ].map((tab) => (
          <button
            key={tab.key}
            className={`guidance-tab-btn compact-pill ${activeTab === tab.key ? "active" : ""}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ─────────────────────────────────────────────
          TAB 1: RECOMMENDED COURSES
         ───────────────────────────────────────────── */}
      {activeTab === "recommended" && (
        <div className="tab-pane-content">
          <div className="filter-actions-bar compact-bar">
            <div className="stream-filter-pills">
              {["All", "Engineering", "Computer Applications", "Science", "Health Sciences", "Commerce", "Humanities", "Law", "Design"].map(
                (stream) => (
                  <button
                    key={stream}
                    className={`filter-pill ${streamFilter === stream ? "active" : ""}`}
                    onClick={() => setStreamFilter(stream)}
                  >
                    {stream}
                  </button>
                )
              )}
            </div>

            {compareIds.length >= 2 && (
              <button
                className="action-btn-primary btn-sm"
                onClick={handleCompareClick}
              >
                ⚖️ Compare ({compareIds.length})
              </button>
            )}
          </div>

          {coursesLoading ? (
            <LoadingSpinner message="Calculating ML profile fit based on your skills and questionnaire..." />
          ) : coursesError ? (
            <ErrorMessage error={coursesError} onRetry={fetchRecommendations} />
          ) : displayedCourses.length === 0 ? (
            <EmptyState
              icon="🎓"
              title="No courses found"
              message="Take the questionnaire to get tailored course recommendations."
              actionText="Take Questionnaire"
              onAction={openQuestionnaire}
            />
          ) : (
            <div className="courses-grid compact-grid">
              {displayedCourses.map((course) => {
                const matchScore = course.match_score ?? course.match_percentage ?? 75;
                const matchClass =
                  matchScore >= 85 ? "match-high" : matchScore >= 60 ? "match-mid" : "match-normal";
                const isCheckedForCompare = compareIds.includes(course.id);

                return (
                  <div key={course.id} className="course-card-enhanced compact-card">
                    <div className="course-card-header">
                      <span className={`match-badge ${matchClass}`}>{matchScore}% Match</span>
                      <span className="degree-tag">{course.degree_level}</span>
                    </div>

                    <h3 className="course-card-title">{course.title}</h3>
                    <div className="course-card-meta">
                      <span>🏷️ {course.stream}</span>
                      <span>⏱️ {course.duration_years} Yrs</span>
                    </div>

                    <div className="match-reason-box compact-reason">
                      💡 <strong>Why:</strong> {course.match_reason || course.recommended_reason || "Aligned with your learning goals"}
                    </div>

                    <div className="card-key-details compact-details">
                      <div><strong>Fees:</strong> {course.fee_range || course.fees_range || "N/A"}</div>
                      <div><strong>Salary:</strong> {course.salary_range || "Competitive"}</div>
                    </div>

                    <div className="card-bottom-actions compact-actions">
                      <button
                        className="action-btn-secondary btn-xs"
                        onClick={() => setSelectedCourse(course)}
                      >
                        Details
                      </button>
                      <button
                        className="action-btn-secondary btn-xs"
                        onClick={() => handleOpenCareerPath(course.id)}
                      >
                        🚀 Career Path
                      </button>
                      <label className="compare-checkbox-label">
                        <input
                          type="checkbox"
                          checked={isCheckedForCompare}
                          onChange={() => toggleCompareId(course.id)}
                        />
                        Compare
                      </label>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ─────────────────────────────────────────────
          TAB 2: ROADMAP
         ───────────────────────────────────────────── */}
      {activeTab === "roadmap" && (
        <div className="tab-pane-content">
          <div className="stream-filter-pills" style={{ marginBottom: "14px" }}>
            {["All", "Science", "Commerce", "Humanities"].map((s) => (
              <button
                key={s}
                className={`filter-pill ${roadmapStream === s ? "active" : ""}`}
                onClick={() => setRoadmapStream(s)}
              >
                {s} Stream
              </button>
            ))}
          </div>

          {roadmapLoading ? (
            <LoadingSpinner message="Loading academic roadmaps..." />
          ) : roadmapItems.length === 0 ? (
            <EmptyState icon="🗺️" title="No roadmap items found" message="Try switching stream filters." />
          ) : (
            <div className="roadmap-timeline compact-timeline">
              {roadmapItems.map((item, index) => (
                <div key={item.id} className="roadmap-stage-card compact-stage">
                  <div className="stage-marker compact-marker">
                    <span className="stage-number">{index + 1}</span>
                    <span className="stage-name">{item.stage}</span>
                  </div>

                  <div className="stage-content">
                    <div className="stage-header">
                      <h3>{item.title}</h3>
                      <span className="stream-pill">{item.stream}</span>
                    </div>
                    <p className="stage-desc">{item.description}</p>

                    {item.options && (
                      <div className="roadmap-options-grid compact-options">
                        {item.options.map((opt, i) => (
                          <div key={i} className="option-tile compact-tile">
                            <strong>{opt.name}</strong>
                            <p>{opt.description}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {item.next_steps && item.next_steps.length > 0 && (
                      <div className="next-steps-box compact-steps">
                        <strong>📌 Next Steps:</strong>
                        <ul>
                          {item.next_steps.map((step, i) => (
                            <li key={i}>{step}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─────────────────────────────────────────────
          TAB 3: ENTRANCE EXAMS
         ───────────────────────────────────────────── */}
      {activeTab === "exams" && (
        <div className="tab-pane-content">
          <div className="search-bar-row compact-search">
            <input
              type="text"
              placeholder="🔍 Search exams (e.g. JEE, NEET, CLAT)..."
              value={examSearch}
              onChange={(e) => setExamSearch(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && fetchExams()}
              className="search-input"
            />
            <button className="action-btn-primary btn-sm" onClick={fetchExams}>
              Search
            </button>
          </div>

          {examsLoading ? (
            <LoadingSpinner message="Loading entrance exams database..." />
          ) : (
            <div className="exams-grid compact-grid">
              {exams.map((exam) => (
                <div key={exam.id} className="exam-card compact-card">
                  <div className="exam-card-header">
                    <span className="exam-code-badge">{exam.code}</span>
                    <span className="stream-pill">{exam.stream}</span>
                  </div>
                  <h3 className="exam-name">{exam.name}</h3>
                  <p className="exam-body-agency">🏛️ {exam.conducting_body}</p>

                  <div className="exam-dates-box compact-dates">
                    {typeof exam.exam_dates === "object" && exam.exam_dates !== null ? (
                      <div className="dates-chips-grid">
                        {Object.entries(exam.exam_dates).map(([k, v]) => (
                          <span key={k} className="date-chip">
                            <strong>{k}:</strong> {v}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p>{JSON.stringify(exam.exam_dates)}</p>
                    )}
                  </div>

                  <div className="exam-card-actions compact-actions">
                    <button
                      className="action-btn-secondary btn-xs"
                      onClick={() => setSelectedExam(exam)}
                    >
                      Syllabus & Tips
                    </button>
                    {exam.official_website_url && (
                      <a
                        href={exam.official_website_url}
                        target="_blank"
                        rel="noreferrer"
                        className="action-btn-primary btn-xs"
                        style={{ textDecoration: "none" }}
                      >
                        Official Site ↗
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─────────────────────────────────────────────
          TAB 4: COLLEGES & RANKINGS
         ───────────────────────────────────────────── */}
      {activeTab === "colleges" && (
        <div className="tab-pane-content">
          <div className="search-bar-row compact-search">
            <input
              type="text"
              placeholder="🔍 Search colleges by name or city..."
              value={collegeSearch}
              onChange={(e) => setCollegeSearch(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && fetchColleges()}
              className="search-input"
            />
            <button className="action-btn-primary btn-sm" onClick={fetchColleges}>
              Search
            </button>
          </div>

          {collegesLoading ? (
            <LoadingSpinner message="Fetching colleges & NIRF ranking information..." />
          ) : (
            <div className="colleges-grid compact-grid">
              {colleges.map((col) => (
                <div key={col.id} className="college-card compact-card">
                  <div className="college-card-top">
                    <div>
                      <h3 className="college-name">{col.name}</h3>
                      <span className="college-location">📍 {col.location}</span>
                    </div>
                    {col.nirf_ranking && (
                      <div className="nirf-rank-badge compact-nirf">
                        <span className="rank-num">#{col.nirf_ranking}</span>
                        <span className="rank-label">NIRF</span>
                      </div>
                    )}
                  </div>

                  <div className="college-details-list compact-details">
                    <div><strong>Type:</strong> {col.college_type}</div>
                    <div><strong>Fees:</strong> {col.average_annual_fee || "Varies"}</div>
                    <div><strong>Admission:</strong> {col.admission_process}</div>
                  </div>

                  {col.courses_offered && (
                    <div className="college-courses-pills">
                      {col.courses_offered.slice(0, 4).map((crs, i) => (
                        <span key={i} className="course-pill">
                          {crs}
                        </span>
                      ))}
                    </div>
                  )}

                  {col.website_url && (
                    <a
                      href={col.website_url}
                      target="_blank"
                      rel="noreferrer"
                      className="college-web-link"
                    >
                      Visit Website →
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─────────────────────────────────────────────
          TAB 5: SCHOLARSHIPS & LOANS
         ───────────────────────────────────────────── */}
      {activeTab === "scholarships" && (
        <div className="tab-pane-content">
          <div className="stream-filter-pills" style={{ marginBottom: "14px" }}>
            {["All", "Merit", "Need-based"].map((cat) => (
              <button
                key={cat}
                className={`filter-pill ${scholarshipCategory === cat ? "active" : ""}`}
                onClick={() => setScholarshipCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>

          {scholarshipsLoading ? (
            <LoadingSpinner message="Loading scholarships & financial aid..." />
          ) : (
            <div className="scholarships-grid compact-grid">
              {scholarships.map((sch) => (
                <div key={sch.id} className="scholarship-card compact-card">
                  <div className="scholarship-header">
                    <span className="category-tag">{sch.category}</span>
                    <span className="deadline-badge">⏰ {sch.deadline_description}</span>
                  </div>

                  <h3 className="scholarship-title">{sch.name}</h3>
                  <p className="scholarship-provider">🏛️ {sch.provider}</p>

                  <div className="amount-banner compact-banner">
                    💰 {sch.amount_and_benefits}
                  </div>

                  <div className="eligibility-box compact-eligibility">
                    <strong>Eligibility:</strong> {sch.eligibility}
                  </div>

                  {sch.application_url && (
                    <a
                      href={sch.application_url}
                      target="_blank"
                      rel="noreferrer"
                      className="action-btn-primary btn-xs"
                      style={{ textDecoration: "none", alignSelf: "flex-start", marginTop: "auto" }}
                    >
                      Apply on Portal ↗
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─────────────────────────────────────────────
          TAB 6: STUDY ABROAD (HIGH INFORMATION DENSITY)
         ───────────────────────────────────────────── */}
      {activeTab === "study_abroad" && (
        <div className="tab-pane-content">
          {studyAbroadLoading ? (
            <LoadingSpinner message="Loading study abroad guide..." />
          ) : (
            <div className="study-abroad-grid compact-grid">
              {studyAbroad.map((country) => (
                <div key={country.id} className="study-abroad-card compact-country-card">
                  {/* Country Header with unified Flag & Title Row */}
                  <div className="country-card-header compact-country-header">
                    <div className="country-title-row">
                      <span className="country-code-pill">🌐 {country.country}</span>
                    </div>
                  </div>

                  {/* Sleek 2-Stat Cost Bar */}
                  <div className="country-costs-box compact-costs">
                    <div className="cost-item">
                      <span className="cost-label">Tuition:</span>
                      <span className="cost-val">{country.avg_tuition_cost}</span>
                    </div>
                    <div className="cost-item">
                      <span className="cost-label">Living:</span>
                      <span className="cost-val">{country.living_cost}</span>
                    </div>
                  </div>

                  {/* Required Exams Tags */}
                  <div className="country-info-row compact-row">
                    <span className="row-label">📝 Required Exams:</span>
                    <div className="pills-wrap compact-pills">
                      {country.required_tests?.map((t, i) => (
                        <span key={i} className="test-tag compact-tag">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Popular Tracks */}
                  <div className="country-info-row compact-row">
                    <span className="row-label">🌟 Popular Tracks:</span>
                    <span className="row-value">{country.popular_courses?.join(", ")}</span>
                  </div>

                  {/* Visa & Work Rights */}
                  <div className="country-info-row compact-row">
                    <span className="row-label">🛂 Visa & Work Rights:</span>
                    <p className="visa-text-compact">{country.visa_work_rights}</p>
                  </div>

                  {/* Primary Intakes as Compact Chip Row */}
                  {country.intake_timelines && (
                    <div className="intakes-box compact-intakes">
                      <span className="intakes-heading">📅 Key Intakes:</span>
                      <div className="intakes-chips-list">
                        {Object.entries(country.intake_timelines).map(([k, v]) => (
                          <span key={k} className="intake-chip">
                            <strong>{k}:</strong> {v}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─────────────────────────────────────────────
          TAB 7: APPLICATION CHECKLIST & DEADLINES
         ───────────────────────────────────────────── */}
      {activeTab === "checklist" && (
        <div className="tab-pane-content">
          <div className="page-header-row compact-header" style={{ marginBottom: "12px" }}>
            <div>
              <h3>Application Tracker & Deadlines</h3>
              <p className="page-subtitle">Track important dates and personal submission checklists.</p>
            </div>
            <button
              className="action-btn-primary btn-sm"
              onClick={() => setShowAddChecklistModal(true)}
            >
              + Add Item
            </button>
          </div>

          {/* Upcoming Reminders Alert Banner */}
          {reminders.length > 0 && (
            <div className="reminders-alert-box compact-reminders">
              <h4>⏰ Upcoming Priority Deadlines</h4>
              <div className="reminders-list">
                {reminders.map((rem) => (
                  <div key={rem.id} className="reminder-item-row">
                    <span className="reminder-title">{rem.title}</span>
                    <span className="days-left-badge">
                      {rem.days_left <= 0 ? "Due Today" : `${rem.days_left}d left`}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {checklistLoading ? (
            <LoadingSpinner message="Loading your checklist..." />
          ) : checklist.length === 0 ? (
            <EmptyState
              icon="✅"
              title="No checklist items yet"
              message="Add upcoming exams, scholarship deadlines, or college applications to stay organized."
              actionText="+ Add First Item"
              onAction={() => setShowAddChecklistModal(true)}
            />
          ) : (
            <div className="checklist-items-table compact-table">
              {checklist.map((item) => (
                <div
                  key={item.id}
                  className={`checklist-item-card compact-card ${item.is_completed ? "completed" : ""}`}
                >
                  <label className="checkbox-wrap">
                    <input
                      type="checkbox"
                      checked={item.is_completed}
                      onChange={() => toggleChecklistItem(item)}
                    />
                    <span className="checkmark" />
                  </label>

                  <div className="checklist-details">
                    <h4 className={item.is_completed ? "text-strikethrough" : ""}>
                      {item.title}
                    </h4>
                    <div className="checklist-meta">
                      <span className="category-pill">{item.category}</span>
                      {item.deadline && (
                        <span className="deadline-date">
                          📅 {new Date(item.deadline).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─────────────────────────────────────────────
          TAB 8: COUNSELLING STATUS
         ───────────────────────────────────────────── */}
      {activeTab === "counselling" && (
        <div className="tab-pane-content">
          <div className="page-header-row compact-header">
            <div>
              <h3>Personal Academic Counselling</h3>
              <p className="page-subtitle">Track your requests and scheduled sessions with teachers.</p>
            </div>
            <button
              className="action-btn-primary btn-sm"
              onClick={() => setShowCounsellingModal(true)}
            >
              + New Request
            </button>
          </div>

          {counsellingLoading ? (
            <LoadingSpinner message="Loading counselling requests..." />
          ) : counsellingList.length === 0 ? (
            <EmptyState
              icon="🤝"
              title="No counselling requests sent"
              message="Have doubts regarding course selection or entrance exams? Request a session with your teacher."
              actionText="Request Counselling"
              onAction={() => setShowCounsellingModal(true)}
            />
          ) : (
            <div className="counselling-list">
              {counsellingList.map((req) => (
                <div key={req.id} className="counselling-card compact-card">
                  <div className="counselling-header">
                    <span className={`status-badge status-${req.status}`}>
                      {req.status.toUpperCase()}
                    </span>
                    <span className="mode-badge">
                      {req.request_type === "study_support" ? "📚 Study support" : "🎓 Higher studies"}
                    </span>
                    <span className="mode-badge">📍 {req.preferred_mode}</span>
                    <span className="date-sub">
                      {new Date(req.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  <div className="counselling-msg">
                    <strong>My Inquiry:</strong>
                    <p>{req.message}</p>
                  </div>

                  {req.teacher_notes && (
                    <div className="teacher-notes-box compact-notes">
                      <strong>👨‍🏫 Teacher Instructions / Schedule:</strong>
                      <p>{req.teacher_notes}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─────────────────────────────────────────────
          MODALS
         ───────────────────────────────────────────── */}

      {/* Questionnaire Modal */}
      {showQuizModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-lg">
            <div className="modal-header">
              <h3>✍️ Academic & Career Interest Questionnaire</h3>
              <button className="modal-close" onClick={() => setShowQuizModal(false)}>
                &times;
              </button>
            </div>

            {quizLoading ? (
              <LoadingSpinner message="Loading questionnaire questions..." />
            ) : (
              <form onSubmit={handleQuizSubmit} className="modal-body-scrollable">
                <p className="modal-instructions">
                  Answer these short questions to help our ML recommender align course options with your aptitude, learning style, and career goals.
                </p>

                {quizQuestions.map((q, qIndex) => (
                  <div key={q.id} className="quiz-question-group">
                    <label className="question-title">
                      {qIndex + 1}. {q.question_text}
                    </label>
                    <div className="options-radio-grid">
                      {q.options.map((opt, optIndex) => (
                        <label
                          key={optIndex}
                          className={`radio-option-card ${
                            quizAnswers[q.id] === optIndex ? "selected" : ""
                          }`}
                        >
                          <input
                            type="radio"
                            name={`q_${q.id}`}
                            checked={quizAnswers[q.id] === optIndex}
                            onChange={() => setQuizAnswers({ ...quizAnswers, [q.id]: optIndex })}
                          />
                          <span>{opt}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}

                <div className="modal-footer">
                  <button
                    type="button"
                    className="action-btn-secondary"
                    onClick={() => setShowQuizModal(false)}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="action-btn-primary"
                    disabled={submittingQuiz}
                  >
                    {submittingQuiz ? "Computing Recommendations..." : "Submit & Get Matches"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Course Details Modal */}
      {selectedCourse && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-md">
            <div className="modal-header">
              <h3>{selectedCourse.title}</h3>
              <button className="modal-close" onClick={() => setSelectedCourse(null)}>
                &times;
              </button>
            </div>
            <div className="modal-body">
              <div className="detail-tags-row">
                <span className="stream-badge">{selectedCourse.stream}</span>
                <span className="degree-tag">{selectedCourse.degree_level}</span>
                <span className="match-badge match-high">
                  {selectedCourse.match_score ?? selectedCourse.match_percentage ?? 80}% Fit
                </span>
              </div>

              <div className="info-section">
                <h4>Why this fits you:</h4>
                <p>{selectedCourse.match_reason || selectedCourse.recommended_reason || "Based on your subject skills"}</p>
              </div>

              <div className="info-grid-2col">
                <div><strong>Duration:</strong> {selectedCourse.duration_years} Years</div>
                <div><strong>Estimated Fees:</strong> {selectedCourse.fee_range || selectedCourse.fees_range}</div>
                <div><strong>Salary Range:</strong> {selectedCourse.salary_range || "Competitive"}</div>
                <div><strong>Eligibility:</strong> {selectedCourse.eligibility}</div>
              </div>

              {selectedCourse.skills_needed && (
                <div className="info-section">
                  <h4>Skills & Prerequisites:</h4>
                  <div className="pills-wrap">
                    {selectedCourse.skills_needed.map((sk, i) => (
                      <span key={i} className="test-tag">
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedCourse.top_colleges && (
                <div className="info-section">
                  <h4>Top Premier Institutions:</h4>
                  <p>{selectedCourse.top_colleges.join(", ")}</p>
                </div>
              )}

              <div className="modal-footer" style={{ marginTop: "16px" }}>
                <button
                  className="action-btn-secondary"
                  onClick={() => handleOpenCareerPath(selectedCourse.id)}
                >
                  🚀 Career Roadmap
                </button>
                <button
                  className="action-btn-primary"
                  onClick={() => setSelectedCourse(null)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Compare Modal */}
      {showCompareModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-xl">
            <div className="modal-header">
              <h3>⚖️ Side-by-Side Course Comparison</h3>
              <button className="modal-close" onClick={() => setShowCompareModal(false)}>
                &times;
              </button>
            </div>
            <div className="modal-body-scrollable">
              {comparingLoading ? (
                <LoadingSpinner message="Generating comparative analysis..." />
              ) : compareData && compareData.length >= 2 ? (
                <div className="compare-table-wrapper">
                  <table className="compare-table">
                    <thead>
                      <tr>
                        <th>Metric / Feature</th>
                        {compareData.map((c) => (
                          <th key={c.id}>{c.title}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><strong>Stream</strong></td>
                        {compareData.map((c) => (
                          <td key={c.id}><span className="stream-pill">{c.stream}</span></td>
                        ))}
                      </tr>
                      <tr>
                        <td><strong>Duration</strong></td>
                        {compareData.map((c) => (
                          <td key={c.id}>{c.duration_years} Years</td>
                        ))}
                      </tr>
                      <tr>
                        <td><strong>Fee Range</strong></td>
                        {compareData.map((c) => (
                          <td key={c.id}>{c.fee_range || "N/A"}</td>
                        ))}
                      </tr>
                      <tr>
                        <td><strong>Salary Range</strong></td>
                        {compareData.map((c) => (
                          <td key={c.id}><strong>{c.salary_range || "N/A"}</strong></td>
                        ))}
                      </tr>
                      <tr>
                        <td><strong>Target Job Roles</strong></td>
                        {compareData.map((c) => (
                          <td key={c.id}>{c.job_roles?.join(", ") || "N/A"}</td>
                        ))}
                      </tr>
                      <tr>
                        <td><strong>Accepted Exams</strong></td>
                        {compareData.map((c) => (
                          <td key={c.id}>{c.exams?.join(", ") || "N/A"}</td>
                        ))}
                      </tr>
                      <tr>
                        <td><strong>Eligibility</strong></td>
                        {compareData.map((c) => (
                          <td key={c.id} style={{ fontSize: "12px" }}>{c.eligibility}</td>
                        ))}
                      </tr>
                    </tbody>
                  </table>
                </div>
              ) : (
                <p>Unable to compare selected courses.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Career Path Modal */}
      {showCareerModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-lg">
            <div className="modal-header">
              <h3>🚀 Career Path & Growth Progression</h3>
              <button className="modal-close" onClick={() => setShowCareerModal(false)}>
                &times;
              </button>
            </div>
            <div className="modal-body-scrollable">
              {careerPathLoading ? (
                <LoadingSpinner message="Mapping career roadmap..." />
              ) : careerPathData ? (
                <div>
                  <div className="career-path-hero compact-hero">
                    <h2>{careerPathData.course_title}</h2>
                    <span className="stream-badge">{careerPathData.stream}</span>
                    <p style={{ marginTop: "6px" }}>
                      <strong>Salary Outlook:</strong> {careerPathData.salary_range}
                    </p>
                  </div>

                  <div className="career-section">
                    <h4>🎯 Target Job Roles:</h4>
                    <div className="pills-wrap">
                      {careerPathData.job_roles?.map((r, i) => (
                        <span key={i} className="job-role-pill">
                          💼 {r}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="career-section">
                    <h4>📈 Growth & Seniority Progression:</h4>
                    <div className="growth-steps-list">
                      {careerPathData.growth_path?.map((step, i) => (
                        <div key={i} className="growth-step-card">
                          <span className="step-num">{i + 1}</span>
                          <span>{step}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="career-section">
                    <h4>🎓 Higher Study & Certifications:</h4>
                    <ul>
                      {careerPathData.higher_study_options?.map((hs, i) => (
                        <li key={i}>{hs}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <p>Career path details unavailable.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Exam Details Modal */}
      {selectedExam && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-md">
            <div className="modal-header">
              <h3>{selectedExam.name} ({selectedExam.code})</h3>
              <button className="modal-close" onClick={() => setSelectedExam(null)}>
                &times;
              </button>
            </div>
            <div className="modal-body">
              <div className="detail-tags-row">
                <span className="stream-badge">{selectedExam.stream}</span>
                <span className="degree-tag">{selectedExam.conducting_body}</span>
              </div>

              <div className="info-section">
                <h4>Eligibility:</h4>
                <p>{selectedExam.eligibility}</p>
              </div>

              <div className="info-section">
                <h4>Syllabus Overview:</h4>
                <p>{selectedExam.syllabus}</p>
              </div>

              <div className="info-section">
                <h4>💡 Preparation Tips:</h4>
                <p>{selectedExam.preparation_tips}</p>
              </div>

              <div className="modal-footer" style={{ marginTop: "16px" }}>
                {selectedExam.official_website_url && (
                  <a
                    href={selectedExam.official_website_url}
                    target="_blank"
                    rel="noreferrer"
                    className="action-btn-primary btn-sm"
                    style={{ textDecoration: "none" }}
                  >
                    Official Portal ↗
                  </a>
                )}
                <button
                  className="action-btn-secondary btn-sm"
                  onClick={() => setSelectedExam(null)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Checklist Modal */}
      {showAddChecklistModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-sm">
            <div className="modal-header">
              <h3>+ Track Application</h3>
              <button className="modal-close" onClick={() => setShowAddChecklistModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleAddChecklist} className="modal-body">
              <div className="form-group" style={{ marginBottom: "12px" }}>
                <label>Task / Application Name:</label>
                <input
                  type="text"
                  placeholder="e.g. JEE Main Application"
                  value={newChecklistTitle}
                  onChange={(e) => setNewChecklistTitle(e.target.value)}
                  required
                  className="search-input"
                />
              </div>

              <div className="form-group" style={{ marginBottom: "12px" }}>
                <label>Category:</label>
                <select
                  value={newChecklistCategory}
                  onChange={(e) => setNewChecklistCategory(e.target.value)}
                  className="search-input"
                >
                  <option value="Exam">Entrance Exam</option>
                  <option value="College">College Application</option>
                  <option value="Scholarship">Scholarship</option>
                  <option value="Document">Documentation</option>
                </select>
              </div>

              <div className="form-group" style={{ marginBottom: "12px" }}>
                <label>Target Deadline (Optional):</label>
                <input
                  type="date"
                  value={newChecklistDeadline}
                  onChange={(e) => setNewChecklistDeadline(e.target.value)}
                  className="search-input"
                />
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="action-btn-secondary"
                  onClick={() => setShowAddChecklistModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="action-btn-primary">
                  Save Item
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Request Counselling Modal */}
      {showCounsellingModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-md">
            <div className="modal-header">
              <h3>💬 Request Academic Counselling</h3>
              <button className="modal-close" onClick={() => setShowCounsellingModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleCounsellingSubmit} className="modal-body">
              <div className="form-group" style={{ marginBottom: "12px" }}>
                <label>Preferred Mode:</label>
                <select
                  value={counsellingMode}
                  onChange={(e) => setCounsellingMode(e.target.value)}
                  className="search-input"
                >
                  <option value="Online">Online Video / Chat</option>
                  <option value="In-person">In-Person at Campus</option>
                </select>
              </div>

              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Question or Doubt:</label>
                <textarea
                  rows="3"
                  placeholder="Describe your questions regarding career paths, streams, or college choices..."
                  value={counsellingMessage}
                  onChange={(e) => setCounsellingMessage(e.target.value)}
                  required
                  className="search-input"
                  style={{ width: "100%" }}
                />
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="action-btn-secondary"
                  onClick={() => setShowCounsellingModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="action-btn-primary"
                  disabled={submittingCounselling}
                >
                  {submittingCounselling ? "Submitting..." : "Send Request"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default CourseGuidance;
