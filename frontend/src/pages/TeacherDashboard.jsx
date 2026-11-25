import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";

function TeacherDashboard({ user, isAdmin = false }) {
  const navigate = useNavigate();

  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Guidance Documents (RAG) State
  const [showUploadDocModal, setShowUploadDocModal] = useState(false);
  const [docTitle, setDocTitle] = useState("");
  const [docType, setDocType] = useState("exam");
  const [docContent, setDocContent] = useState("");
  const [savingDoc, setSavingDoc] = useState(false);

  // Student Exploration Telemetry
  const [guidanceActivity, setGuidanceActivity] = useState([]);
  const [activityLoading, setActivityLoading] = useState(false);

  // Counselling count for KPI
  const [counsellingCount, setCounsellingCount] = useState(0);

  const fetchStats = async () => {
    setError(null);
    try {
      const res = await api.get("/teacher/dashboard");
      setStats(res.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load teacher analytics. Are you logged in as a teacher?");
    } finally {
      setLoading(false);
    }
  };

  const fetchGuidanceActivity = async () => {
    setActivityLoading(true);
    try {
      const res = await api.get("/api/v1/guidance/activity");
      setGuidanceActivity(res.data || []);
    } catch (err) {
      console.error("Student guidance activity fetch error:", err);
    } finally {
      setActivityLoading(false);
    }
  };

  const fetchCounsellingCount = async () => {
    try {
      const res = await api.get("/api/v1/guidance/counselling");
      setCounsellingCount((res.data || []).length);
    } catch (err) {
      console.error("Counselling count error:", err);
    }
  };

  useEffect(() => {
    fetchStats();
    fetchGuidanceActivity();
    fetchCounsellingCount();
  }, []);

  const handleUploadDoc = async (e) => {
    e.preventDefault();
    if (!docTitle.trim() || !docContent.trim()) return;
    setSavingDoc(true);
    try {
      await api.post("/api/v1/chat/documents", {
        title: docTitle.trim(),
        doc_type: docType,
        content: docContent.trim(),
        source_url: "",
      });
      setShowUploadDocModal(false);
      setDocTitle("");
      setDocContent("");
      alert("Guidance document uploaded and queued for verified RAG indexing.");
    } catch (err) {
      console.error("Upload doc error:", err);
      alert(err.response?.data?.detail || "Could not upload guidance document.");
    } finally {
      setSavingDoc(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="teacher-dashboard">
      {error && <ErrorMessage message={error} />}

      {/* Header Row */}
      <div className="card-head-row" style={{ marginBottom: "20px" }}>
        <div>
          <h2>👨‍🏫 Teacher Dashboard ({user?.name || "misna"})</h2>
          <p className="subtext">
            Module 1 Executive Overview: Track class health, analyze topic difficulty heatmaps, and intervene for at-risk students.
          </p>
        </div>
        <div className="teacher-top-actions">
          <button
            className="action-btn-secondary"
            onClick={() => setShowUploadDocModal(true)}
          >
            + Add Guidance Doc (RAG)
          </button>
          <button
            className="action-btn-primary"
            onClick={() => navigate("/materials")}
          >
            + Upload Study Material
          </button>
        </div>
      </div>

      {/* Executive KPI Stats */}
      <section className="kpi-grid" style={{ marginBottom: "24px" }}>
        <div className="kpi-card info">
          <div className="kpi-icon">👥</div>
          <div className="kpi-details">
            <span className="kpi-num">{stats?.total_students || 0}</span>
            <span className="kpi-label">Enrolled Students</span>
            <span className="kpi-subtext">Active skill profiles</span>
          </div>
        </div>

        <div className="kpi-card danger">
          <div className="kpi-icon">🚨</div>
          <div className="kpi-details">
            <span className="kpi-num">{stats?.at_risk_students?.length || 0}</span>
            <span className="kpi-label">Students Needing Support</span>
            <span className="kpi-subtext">Weak areas or declining quiz scores</span>
          </div>
        </div>

        <div className="kpi-card warning">
          <div className="kpi-icon">⚠️</div>
          <div className="kpi-details">
            <span className="kpi-num">{stats?.class_weak_topics?.length || 0}</span>
            <span className="kpi-label">Class Weak Topics</span>
            <span className="kpi-subtext">Topics requiring focused review</span>
          </div>
        </div>

        <div className="kpi-card success">
          <div className="kpi-icon">📚</div>
          <div className="kpi-details">
            <span className="kpi-num">{stats?.total_materials || 0}</span>
            <span className="kpi-label">Study Materials</span>
            <span className="kpi-subtext">Published teaching resources</span>
          </div>
        </div>

        <div className="kpi-card info">
          <div className="kpi-icon">🤝</div>
          <div className="kpi-details">
            <span className="kpi-num">{counsellingCount}</span>
            <span className="kpi-label">Counselling Requests</span>
            <span className="kpi-subtext">Career & course inquiries</span>
          </div>
        </div>
      </section>

      {/* Module 1 Quick Access Shortcuts */}
      <section className="teacher-module-shortcuts" style={{ marginBottom: "28px" }}>
        <div className="teacher-shortcut-card" onClick={() => navigate("/teacher/classes")}>
          <div>
            <div className="teacher-shortcut-title">🏫 Classes, Rosters & Marks</div>
            <p className="teacher-shortcut-desc">Create classes, share student join codes, inspect enrolled rosters, and import CSV marks.</p>
          </div>
          <span className="teacher-shortcut-link">Open Classes Page →</span>
        </div>

        <div className="teacher-shortcut-card" onClick={() => navigate("/teacher/curriculum")}>
          <div>
            <div className="teacher-shortcut-title">📚 Subjects & Syllabus</div>
            <p className="teacher-shortcut-desc">Define courses, curriculum subjects, and topic hierarchies with ordering index.</p>
          </div>
          <span className="teacher-shortcut-link">Manage Syllabus →</span>
        </div>

        <div className="teacher-shortcut-card" onClick={() => navigate("/teacher/quizzes")}>
          <div>
            <div className="teacher-shortcut-title">🎯 Topic-Tagged Quizzes</div>
            <p className="teacher-shortcut-desc">Create multiple choice questions with 4 options, explanations, and difficulty levels.</p>
          </div>
          <span className="teacher-shortcut-link">Manage Questions →</span>
        </div>

        <div className="teacher-shortcut-card" onClick={() => navigate("/teacher/groups")}>
          <div>
            <div className="teacher-shortcut-title">👥 Study Groups (ML)</div>
            <p className="teacher-shortcut-desc">Generate balanced peer-teaching groups and review coverage rates before approval.</p>
          </div>
          <span className="teacher-shortcut-link">Review Groups →</span>
        </div>

        <div className="teacher-shortcut-card" onClick={() => navigate("/teacher/counselling")}>
          <div>
            <div className="teacher-shortcut-title">🤝 Student Counselling</div>
            <p className="teacher-shortcut-desc">Review study-support inquiries, doubt submissions, and schedule guidance sessions.</p>
          </div>
          <span className="teacher-shortcut-link">View Counselling →</span>
        </div>

        <div className="teacher-shortcut-card" onClick={() => navigate("/teacher/revision-notes")}>
          <div>
            <div className="teacher-shortcut-title">🧠 AI Revision Notes</div>
            <p className="teacher-shortcut-desc">Review and approve AI-generated revision notes and peer teaching outlines.</p>
          </div>
          <span className="teacher-shortcut-link">Review Queue →</span>
        </div>
      </section>

      {/* Grid: Class Weak Topics Heatmap & At-Risk Students List */}
      <div className="teacher-split-grid" style={{ marginBottom: "28px" }}>
        {/* Class Weak Topics Heatmap */}
        <section className="teacher-section-card">
          <div className="card-head-row">
            <div>
              <h3>⚠️ Class-Wide Topic Difficulty Heatmap (Module 1.5)</h3>
              <p className="subtext">Topics where the highest number of students are struggling</p>
            </div>
          </div>

          <div className="class-topics-table-wrapper">
            <table className="teacher-table">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Topic</th>
                  <th>Struggling Students</th>
                  <th>Class Avg</th>
                  <th>Linked Materials</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {stats?.class_weak_topics?.length === 0 ? (
                  <tr>
                    <td colSpan="6" style={{ textAlign: "center", padding: "20px", color: "var(--text-muted)" }}>
                      🎉 No class-wide weak topics detected. All students are progressing well!
                    </td>
                  </tr>
                ) : (
                  stats?.class_weak_topics?.map((item, idx) => (
                    <tr key={idx}>
                      <td>
                        <span className="subject-pill">{item.subject}</span>
                      </td>
                      <td>
                        <strong>{item.topic}</strong>
                      </td>
                      <td>
                        <span className="weak-count-badge">
                          {item.weak_students_count} Students
                        </span>
                      </td>
                      <td>{item.average_mastery}%</td>
                      <td>
                        <span className="materials-count-pill">
                          {item.linked_materials_count} Resources
                        </span>
                      </td>
                      <td>
                        <button
                          className="table-action-btn"
                          onClick={() =>
                            navigate(`/materials?search=${encodeURIComponent(item.topic)}`)
                          }
                        >
                          View Notes →
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        {/* At-Risk Students List */}
        <section className="teacher-section-card">
          <div className="card-head-row">
            <div>
              <h3>🚨 Students Requiring Personal Intervention (Module 1.7)</h3>
              <p className="subtext">Flags weak topics and repeated downward trends in recent quizzes.</p>
            </div>
          </div>

          <div className="at-risk-list">
            {stats?.at_risk_students?.length === 0 ? (
              <p className="all-good-msg">🎉 All students are performing above average!</p>
            ) : (
              stats?.at_risk_students?.map((st) => (
                <div key={st.student_id} className="at-risk-card">
                  <div className="at-risk-top">
                    <div className="at-risk-user">
                      <span className="user-icon-circle">
                        {st.name.charAt(0).toUpperCase()}
                      </span>
                      <div>
                        <strong>{st.name}</strong>
                        <span className="user-email-text">{st.email}</span>
                      </div>
                    </div>
                    <span className="weak-flag">
                      {st.weak_topics_count > 0
                        ? `${st.weak_topics_count} Weak Topics`
                        : "Progress alert"}
                    </span>
                  </div>

                  {st.risk_reasons?.length > 0 && (
                    <p className="subtext" style={{ margin: "8px 0" }}>
                      {st.risk_reasons.join(" · ")}
                    </p>
                  )}

                  <div className="student-weak-pills">
                    {st.weak_topics.map((t, i) => (
                      <span key={i} className="danger-topic-pill">
                        ⚠️ {t}
                      </span>
                    ))}
                  </div>

                  <div className="at-risk-footer">
                    <span>Overall Mastery: <strong>{st.average_mastery}%</strong></span>
                    <button
                      className="contact-btn"
                      onClick={() => navigate("/teacher/groups")}
                    >
                      ⚡ Review Groups
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      {/* Student Course & Exam Exploration Telemetry */}
      <section className="teacher-section-card" style={{ marginBottom: "28px" }}>
        <div className="card-head-row">
          <div>
            <h3>🧭 Student Course & Exam Exploration Telemetry</h3>
            <p className="subtext">
              Recent course details and entrance-exam preparation pathways opened by students.
            </p>
          </div>
          <button className="action-btn-secondary btn-sm" onClick={fetchGuidanceActivity}>
            Refresh Activity
          </button>
        </div>
        {activityLoading ? (
          <p>Loading student activity...</p>
        ) : guidanceActivity.length === 0 ? (
          <p className="subtext">No course or entrance exam exploration recorded yet.</p>
        ) : (
          <div className="class-topics-table-wrapper">
            <table className="teacher-table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Explored Category</th>
                  <th>Item Title</th>
                  <th>When</th>
                </tr>
              </thead>
              <tbody>
                {guidanceActivity.map((activity) => (
                  <tr key={activity.id}>
                    <td><strong>{activity.student_name}</strong></td>
                    <td>
                      <span className="subject-pill">
                        {activity.activity_type === "exam" ? "Entrance Exam" : "Higher Studies Course"}
                      </span>
                    </td>
                    <td>{activity.title}</td>
                    <td>{new Date(activity.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Modal: Upload Guidance Document for RAG */}
      {showUploadDocModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-lg">
            <div className="modal-header">
              <h3>+ Upload Verified Guidance Document (RAG)</h3>
              <button className="modal-close" onClick={() => setShowUploadDocModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleUploadDoc} className="modal-body">
              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Document Title:</label>
                <input
                  type="text"
                  placeholder="e.g. KEAM 2025 Prospectus or Polytechnic Lateral Entry Rules"
                  value={docTitle}
                  onChange={(e) => setDocTitle(e.target.value)}
                  required
                  className="search-input"
                  style={{ width: "100%" }}
                />
              </div>

              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Document Category:</label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="search-input"
                >
                  <option value="exam">Entrance Exam Prospectus</option>
                  <option value="course">Degree / Diploma Course Guide</option>
                  <option value="scholarship">Scholarship & Financial Aid Guideline</option>
                  <option value="admission">College Admission Criteria</option>
                </select>
              </div>

              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Official Content / Text Excerpts:</label>
                <textarea
                  rows="7"
                  placeholder="Paste official brochure text, eligibility guidelines, cutoffs, or key rules for the AI chatbot to use as ground truth..."
                  value={docContent}
                  onChange={(e) => setDocContent(e.target.value)}
                  required
                  className="search-input"
                  style={{ width: "100%" }}
                />
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="action-btn-secondary"
                  onClick={() => setShowUploadDocModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="action-btn-primary"
                  disabled={savingDoc}
                >
                  {savingDoc ? "Indexing Document..." : "Save & Index for RAG"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default TeacherDashboard;
