import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import TeacherClassesPanel from "./TeacherClassesPanel";

function TeacherDashboard({ user, isAdmin = false }) {
  const navigate = useNavigate();

  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Counselling Requests State
  const [counsellingRequests, setCounsellingRequests] = useState([]);
  const [counsellingLoading, setCounsellingLoading] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [newStatus, setNewStatus] = useState("scheduled");
  const [teacherNotes, setTeacherNotes] = useState("");
  const [savingNotes, setSavingNotes] = useState(false);

  // Guidance Documents (RAG) State
  const [guidanceDocs, setGuidanceDocs] = useState([]);
  const [docsLoading, setDocsLoading] = useState(false);
  const [revisionQueue, setRevisionQueue] = useState([]);
  const [revisionQueueLoading, setRevisionQueueLoading] = useState(false);
  const [guidanceActivity, setGuidanceActivity] = useState([]);
  const [activityLoading, setActivityLoading] = useState(false);
  const [showUploadDocModal, setShowUploadDocModal] = useState(false);
  const [docTitle, setDocTitle] = useState("");
  const [docType, setDocType] = useState("exam");
  const [docContent, setDocContent] = useState("");
  const [savingDoc, setSavingDoc] = useState(false);

  // Intelligent Study Groups State (Module 7 & 8)
  const [studyGroups, setStudyGroups] = useState([]);
  const [groupsLoading, setGroupsLoading] = useState(false);
  const [generatingGroups, setGeneratingGroups] = useState(false);
  const [selectedClassId, setSelectedClassId] = useState(null);

  const handleSelectedClassChange = useCallback((classId) => {
    setSelectedClassId(classId);
  }, []);

  const fetchStats = async () => {
    setError(null);
    try {
      const res = await api.get("/teacher/dashboard", {
        params: selectedClassId ? { class_id: selectedClassId } : {},
      });
      setStats(res.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load teacher analytics. Are you logged in as a teacher?");
    } finally {
      setLoading(false);
    }
  };

  const fetchCounsellingRequests = async () => {
    setCounsellingLoading(true);
    try {
      const res = await api.get("/api/v1/guidance/counselling");
      setCounsellingRequests(res.data || []);
    } catch (err) {
      console.error("Counselling requests fetch error:", err);
    } finally {
      setCounsellingLoading(false);
    }
  };

  const fetchGuidanceDocs = async () => {
    setDocsLoading(true);
    try {
      const res = await api.get("/api/v1/chat/documents");
      setGuidanceDocs(res.data.items || []);
    } catch (err) {
      console.error("Guidance docs fetch error:", err);
    } finally {
      setDocsLoading(false);
    }
  };

  const fetchRevisionQueue = async () => {
    setRevisionQueueLoading(true);
    try {
      const res = await api.get("/api/v1/revision/review-queue");
      setRevisionQueue(res.data || []);
    } catch (err) {
      console.error("Revision notes review queue fetch error:", err);
      alert(err.response?.data?.detail || "Could not load revision notes awaiting review.");
    } finally {
      setRevisionQueueLoading(false);
    }
  };

  const fetchGuidanceActivity = async () => {
    setActivityLoading(true);
    try {
      const res = await api.get("/api/v1/guidance/activity");
      setGuidanceActivity(res.data || []);
    } catch (err) {
      console.error("Student guidance activity fetch error:", err);
      alert(err.response?.data?.detail || "Could not load student guidance activity.");
    } finally {
      setActivityLoading(false);
    }
  };

  const fetchStudyGroups = async () => {
    setGroupsLoading(true);
    try {
      const res = await api.get("/api/v1/groups");
      setStudyGroups(res.data || []);
    } catch (err) {
      console.error("Study groups fetch error:", err);
    } finally {
      setGroupsLoading(false);
    }
  };

  const handleRegenerateGroups = async () => {
    if (!selectedClassId) {
      alert("Create or select a class before generating groups.");
      return;
    }
    setGeneratingGroups(true);
    try {
      const res = await api.post("/api/v1/groups/generate", {
        class_id: selectedClassId,
        min_size: 3,
        max_size: 5,
        reset_existing: true,
      });
      setStudyGroups(res.data || []);
      alert("Groups generated for teacher review. Approve a group to make it visible to its students.");
    } catch (err) {
      console.error("Group generation error:", err);
      alert(err.response?.data?.detail || "Error generating study groups.");
    } finally {
      setGeneratingGroups(false);
    }
  };

  const handleReviewGroup = async (groupId, decision) => {
    if (decision === "reject" && !window.confirm("Reject this proposed study group?")) return;
    try {
      await api.patch(`/api/v1/groups/${groupId}/review`, { decision });
      await fetchStudyGroups();
    } catch (err) {
      console.error("Study group review error:", err);
      alert(err.response?.data?.detail || "Could not update the group review.");
    }
  };

  const handleReviewRevisionNote = async (noteId, decision) => {
    if (decision === "reject" && !window.confirm("Reject these AI-generated revision notes?")) return;
    try {
      await api.patch(`/api/v1/revision/${noteId}/review`, { decision });
      await fetchRevisionQueue();
    } catch (err) {
      console.error("Revision note review error:", err);
      alert(err.response?.data?.detail || "Could not update the revision note review.");
    }
  };

  useEffect(() => {
    fetchCounsellingRequests();
    fetchGuidanceDocs();
    fetchRevisionQueue();
    fetchGuidanceActivity();
    fetchStudyGroups();
  }, []);

  useEffect(() => {
    fetchStats();
  }, [selectedClassId]);

  const handleUpdateRequest = async (e) => {
    e.preventDefault();
    if (!selectedRequest) return;
    setSavingNotes(true);
    try {
      await api.patch(`/api/v1/guidance/counselling/${selectedRequest.id}`, {
        status: newStatus,
        teacher_notes: teacherNotes,
      });
      setSelectedRequest(null);
      setTeacherNotes("");
      fetchCounsellingRequests();
      alert("Counselling request updated successfully!");
    } catch (err) {
      console.error("Update request error:", err);
      alert("Failed to update counselling request.");
    } finally {
      setSavingNotes(false);
    }
  };

  const handleUploadDoc = async (e) => {
    e.preventDefault();
    if (!docTitle.trim() || !docContent.trim()) return;
    setSavingDoc(true);
    try {
      await api.post("/api/v1/chat/documents", {
        title: docTitle,
        doc_type: docType,
        content: docContent,
      });
      setShowUploadDocModal(false);
      setDocTitle("");
      setDocContent("");
      fetchGuidanceDocs();
      alert("Guidance document uploaded and queued for teacher approval before chatbot use.");
    } catch (err) {
      console.error("Upload doc error:", err);
      alert("Failed to upload guidance document.");
    } finally {
      setSavingDoc(false);
    }
  };

  const handleApproveDoc = async (docId) => {
    try {
      await api.patch(`/api/v1/chat/documents/${docId}/approve`);
      fetchGuidanceDocs();
      alert("Document approved for chatbot RAG indexing.");
    } catch (err) {
      console.error("Approve doc error:", err);
    }
  };

  if (loading) return <LoadingSpinner message="Aggregating class analytics & weak topics..." />;
  if (error) return <ErrorMessage error={error} onRetry={fetchStats} />;

  return (
    <div className="teacher-dashboard-page">
      {/* Header */}
      <div className="page-header-row">
        <div>
          <h2>{isAdmin ? "🌐 Platform Academic Command Center" : "👨‍🏫 Teacher Academic Command Center"} ({user?.name || (isAdmin ? "Admin" : "Teacher")})</h2>
          <p className="page-subtitle">
            Monitor class-wide weak topics, respond to career counselling requests, curate verified guidance documents, and publish instructional resources.
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

      <TeacherClassesPanel isAdmin={isAdmin} onSelectedClassChange={handleSelectedClassChange} />

      <section className="teacher-section-card" style={{ marginBottom: "28px" }}>
        <div className="card-head-row">
          <div>
            <h3>🧠 AI Revision Notes Awaiting Review</h3>
            <p className="subtext">
              Review generated notes and the student teaching outline before sharing them with learners.
            </p>
          </div>
          <button className="action-btn-secondary btn-sm" onClick={fetchRevisionQueue}>
            Refresh Queue
          </button>
        </div>
        {revisionQueueLoading ? (
          <p>Loading revision notes...</p>
        ) : revisionQueue.length === 0 ? (
          <p className="all-good-msg">No revision notes are waiting for review.</p>
        ) : (
          <div className="class-topics-table-wrapper">
            <table className="teacher-table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Subject / Topic</th>
                  <th>Teaching outline</th>
                  <th>Teacher review</th>
                </tr>
              </thead>
              <tbody>
                {revisionQueue.map((note) => (
                  <tr key={note.id}>
                    <td>{note.student_name}</td>
                    <td>{note.subject_name} / {note.topic_name}</td>
                    <td style={{ maxWidth: "380px" }}>
                      <strong>{note.content?.overview}</strong>
                      <p className="subtext">{note.content?.teaching_outline}</p>
                    </td>
                    <td>
                      <div className="teacher-review-actions">
                        <button
                          className="action-btn-success btn-sm"
                          onClick={() => handleReviewRevisionNote(note.id, "approve")}
                        >
                          Approve
                        </button>
                        <button
                          className="action-btn-secondary btn-sm"
                          onClick={() => handleReviewRevisionNote(note.id, "reject")}
                        >
                          Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="teacher-section-card" style={{ marginBottom: "28px" }}>
        <div className="card-head-row">
          <div>
            <h3>🧭 Student Course & Exam Exploration</h3>
            <p className="subtext">
              Recent course details and entrance-exam preparation pages opened by students.
            </p>
          </div>
          <button className="action-btn-secondary btn-sm" onClick={fetchGuidanceActivity}>
            Refresh Activity
          </button>
        </div>
        {activityLoading ? (
          <p>Loading student activity...</p>
        ) : guidanceActivity.length === 0 ? (
          <p className="subtext">No course or exam details have been explored yet.</p>
        ) : (
          <div className="class-topics-table-wrapper">
            <table className="teacher-table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Explored</th>
                  <th>Item</th>
                  <th>When</th>
                </tr>
              </thead>
              <tbody>
                {guidanceActivity.map((activity) => (
                  <tr key={activity.id}>
                    <td>{activity.student_name}</td>
                    <td>{activity.activity_type === "exam" ? "Entrance exam" : "Course"}</td>
                    <td>{activity.title}</td>
                    <td>{new Date(activity.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* KPI Stats */}
      <section className="kpi-grid">
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

        <div className="kpi-card success">
          <div className="kpi-icon">📚</div>
          <div className="kpi-details">
            <span className="kpi-num">{stats?.total_materials || 0}</span>
            <span className="kpi-label">Study Materials</span>
            <span className="kpi-subtext">Published across 3 subjects</span>
          </div>
        </div>

        <div className="kpi-card warning">
          <div className="kpi-icon">🤝</div>
          <div className="kpi-details">
            <span className="kpi-num">{counsellingRequests.length}</span>
            <span className="kpi-label">Counselling Requests</span>
            <span className="kpi-subtext">Career & course inquiries</span>
          </div>
        </div>
      </section>

      {/* Section: Student Career & Higher Studies Counselling Requests */}
      <section className="teacher-section-card" style={{ marginBottom: "28px" }}>
        <div className="card-head-row">
          <div>
            <h3>🤝 Student Study Support & Higher Studies Requests</h3>
            <p className="subtext">
              Review teacher-led study requests, peer-match needs, and questions about courses, exams, and career pathways.
            </p>
          </div>
          <button
            className="action-btn-secondary btn-sm"
            onClick={fetchCounsellingRequests}
          >
            🔄 Refresh Queue
          </button>
        </div>

        {counsellingLoading ? (
          <p>Loading requests...</p>
        ) : counsellingRequests.length === 0 ? (
          <p className="all-good-msg">🎉 No pending counselling requests at this time.</p>
        ) : (
          <div className="class-topics-table-wrapper">
            <table className="teacher-table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Request Type</th>
                  <th>Preferred Mode</th>
                  <th>Doubt / Question</th>
                  <th>Submitted</th>
                  <th>Status</th>
                  <th>Teacher Response</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {counsellingRequests.map((req) => (
                  <tr key={req.id}>
                    <td>
                      <strong>{req.student_name || `Student #${req.student_id}`}</strong>
                    </td>
                    <td>{req.request_type === "study_support" ? "Study support" : "Higher studies"}</td>
                    <td>
                      <span className="mode-badge">📍 {req.preferred_mode}</span>
                    </td>
                    <td style={{ maxWidth: "260px" }}>
                      <p style={{ margin: 0, fontSize: "13px" }}>{req.message}</p>
                    </td>
                    <td>{new Date(req.created_at).toLocaleDateString()}</td>
                    <td>
                      <span className={`status-badge status-${req.status}`}>
                        {req.status.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ maxWidth: "200px", fontSize: "12px", color: "var(--text-muted)" }}>
                      {req.teacher_notes || "No notes yet"}
                    </td>
                    <td>
                      <button
                        className="table-action-btn"
                        onClick={() => {
                          setSelectedRequest(req);
                          setNewStatus(req.status || "scheduled");
                          setTeacherNotes(req.teacher_notes || "");
                        }}
                      >
                        Respond & Schedule →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Section: Balanced Study Groups & Peer Matching (Module 7 & 8) */}
      <section className="teacher-section-card" style={{ marginBottom: "28px" }}>
        <div className="card-head-row">
          <div>
            <h3>👥 Balanced Study Groups & Peer-Teaching Coverage (Module 7 & 8)</h3>
            <p className="subtext">
              Matches students within the same course, board/institution, and year/semester so peers with strong mastery can help with weak topics.
            </p>
          </div>
          <button
            className="action-btn-primary btn-sm"
            onClick={handleRegenerateGroups}
            disabled={generatingGroups || !selectedClassId}
          >
            {generatingGroups ? "Optimizing Groups..." : "⚡ Generate Groups for Selected Class"}
          </button>
        </div>

        {groupsLoading ? (
          <p>Analyzing student skill profiles and matching groups...</p>
        ) : studyGroups.length === 0 ? (
          <p style={{ color: "var(--text-muted)", fontSize: "13px" }}>
            No peer groups are available yet. Generate groups to match students who share a course, board/institution, and year/semester.
          </p>
        ) : (
          <div className="class-topics-table-wrapper">
            <table className="teacher-table">
              <thead>
                <tr>
                  <th>Group Name</th>
                  <th>Review status</th>
                  <th>Members (3-5)</th>
                  <th>Weak-Topic Coverage</th>
                  <th>Teaching Pairs</th>
                  <th>Uncovered Topics</th>
                  <th>Schedule Matches</th>
                  <th>Follow-up progress</th>
                  <th>Teacher review</th>
                </tr>
              </thead>
              <tbody>
                {studyGroups.map((grp) => (
                  <tr key={grp.id}>
                    <td>
                      <strong>{grp.name}</strong>
                    </td>
                    <td>
                      <span className={`status-badge status-${grp.status}`}>
                        {grp.status.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <div className="pills-wrap">
                        {grp.members.map((m) => (
                          <span key={m.student_id} className="degree-tag">
                            {m.name}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <span className="match-badge match-high">
                        {grp.coverage_rate}% Covered
                      </span>
                    </td>
                    <td>
                      <span className="stream-badge">
                        🤝 {grp.teaching_pairs.length} Pairs
                      </span>
                    </td>
                    <td>
                      {grp.uncovered_topics.length > 0 ? (
                        <div className="pills-wrap">
                          {grp.uncovered_topics.map((t, idx) => (
                            <span key={idx} className="test-tag" style={{ background: "#fee2e2", color: "#b91c1c" }}>
                              {t}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span style={{ color: "#16a34a", fontSize: "12px", fontWeight: "600" }}>
                          ✓ 100% Fully Covered
                        </span>
                      )}
                    </td>
                    <td>
                      <span style={{ fontSize: "12px", color: "#475569" }}>
                        📅 {grp.common_schedules.length} overlap slots
                      </span>
                    </td>
                    <td>
                      {grp.progress_summary?.change_points === null ||
                      grp.progress_summary?.change_points === undefined ? (
                        <span className="subtext">No comparable follow-up quizzes</span>
                      ) : (
                        <span style={{ color: grp.progress_summary.change_points >= 0 ? "#15803d" : "#b91c1c" }}>
                          {grp.progress_summary.change_points > 0 ? "+" : ""}
                          {grp.progress_summary.change_points} pts
                          <small>
                            {" "}({grp.progress_summary.baseline_accuracy}% → {grp.progress_summary.follow_up_accuracy}%)
                          </small>
                        </span>
                      )}
                    </td>
                    <td>
                      {grp.status === "pending" ? (
                        <div className="teacher-review-actions">
                          <button
                            className="action-btn-success btn-sm"
                            onClick={() => handleReviewGroup(grp.id, "approve")}
                          >
                            Approve
                          </button>
                          <button
                            className="action-btn-secondary btn-sm"
                            onClick={() => handleReviewGroup(grp.id, "reject")}
                          >
                            Reject
                          </button>
                        </div>
                      ) : (
                        <span className="subtext">Reviewed</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Section: Verified Guidance Documents (RAG Knowledge Base) */}
      <section className="teacher-section-card" style={{ marginBottom: "28px" }}>
        <div className="card-head-row">
          <div>
            <h3>📖 Verified Guidance Documents (AI Chatbot Knowledge Base)</h3>
            <p className="subtext">
              Documents curated by faculty to ground AI responses with official facts and prevent hallucination
            </p>
          </div>
          <button
            className="action-btn-primary btn-sm"
            onClick={() => setShowUploadDocModal(true)}
          >
            + Upload Document
          </button>
        </div>

        {docsLoading ? (
          <p>Loading knowledge base...</p>
        ) : guidanceDocs.length === 0 ? (
          <p style={{ color: "var(--text-muted)", fontSize: "13px" }}>
            No documents uploaded yet. Upload official exam brochures or course guides.
          </p>
        ) : (
          <div className="class-topics-table-wrapper">
            <table className="teacher-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Type</th>
                  <th>RAG Indexing Status</th>
                  <th>Indexed Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {guidanceDocs.map((doc) => (
                  <tr key={doc.id}>
                    <td>
                      <strong>📄 {doc.title}</strong>
                    </td>
                    <td>
                      <span className="stream-pill">{doc.doc_type}</span>
                    </td>
                    <td>
                      <span className={`status-badge ${doc.is_approved ? "status-completed" : "status-pending"}`}>
                        {doc.is_approved ? "VERIFIED & INDEXED" : "PENDING REVIEW"}
                      </span>
                    </td>
                    <td>{new Date(doc.created_at).toLocaleDateString()}</td>
                    <td>
                      {!doc.is_approved && (
                        <button
                          className="table-action-btn"
                          onClick={() => handleApproveDoc(doc.id)}
                        >
                          Approve for RAG ✓
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Grid: Class Weak Topics & At-Risk Students */}
      <div className="teacher-split-grid">
        {/* Class Weak Topics Heatmap */}
        <section className="teacher-section-card">
          <div className="card-head-row">
            <div>
              <h3>⚠️ Class-Wide Topic Difficulty Heatmap</h3>
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
                {stats?.class_weak_topics?.map((item, idx) => (
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
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* At-Risk Students List */}
        <section className="teacher-section-card">
          <div className="card-head-row">
            <div>
              <h3>🚨 Students Requiring Personal Intervention</h3>
              <p className="subtext">Flags weak topics and repeated downward trends in recent topic quizzes.</p>
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
                      onClick={handleRegenerateGroups}
                      disabled={!selectedClassId || generatingGroups}
                    >
                      ⚡ Rebuild Class Groups
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      {/* Modal: Respond & Schedule Counselling */}
      {selectedRequest && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-md">
            <div className="modal-header">
              <h3>Respond to Counselling Request</h3>
              <button className="modal-close" onClick={() => setSelectedRequest(null)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleUpdateRequest} className="modal-body">
              <div style={{ marginBottom: "14px", background: "#f8fafc", padding: "12px 14px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                <strong>Student:</strong> {selectedRequest.student_name || `Student #${selectedRequest.student_id}`}
                <br />
                <strong>Preferred Mode:</strong> {selectedRequest.preferred_mode}
                <br />
                <strong>Question / Need:</strong>
                <p style={{ margin: "4px 0 0", color: "#334155" }}>{selectedRequest.message}</p>
              </div>

              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Update Status:</label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  className="search-input"
                >
                  <option value="scheduled">Scheduled (Date & Time Provided)</option>
                  <option value="completed">Completed / Answered</option>
                  <option value="pending">Pending</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>

              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Meeting Instructions / Feedback / Notes:</label>
                <textarea
                  rows="4"
                  placeholder="e.g. Scheduled for Friday at 4:00 PM via Google Meet link: meet.google.com/xyz or Meet in Room 204..."
                  value={teacherNotes}
                  onChange={(e) => setTeacherNotes(e.target.value)}
                  required
                  className="search-input"
                  style={{ width: "100%" }}
                />
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="action-btn-secondary"
                  onClick={() => setSelectedRequest(null)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="action-btn-primary"
                  disabled={savingNotes}
                >
                  {savingNotes ? "Saving..." : "Save & Notify Student"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

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
              <p className="modal-instructions">
                Upload verified brochures, syllabus notes, or entrance guidelines. This content will be chunked, indexed, and cited by the AI Assistant when responding to student inquiries.
              </p>

              <div className="info-grid-2col" style={{ marginBottom: "14px" }}>
                <div>
                  <label>Document Title:</label>
                  <input
                    type="text"
                    placeholder="e.g. KEAM 2025 Kerala Engineering Prospectus"
                    value={docTitle}
                    onChange={(e) => setDocTitle(e.target.value)}
                    required
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
                <div>
                  <label>Document Type:</label>
                  <select
                    value={docType}
                    onChange={(e) => setDocType(e.target.value)}
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  >
                    <option value="exam">Entrance Exam Guide</option>
                    <option value="course">Course Description / Roadmap</option>
                    <option value="scholarship">Scholarship Details</option>
                    <option value="study_abroad">Study Abroad Dossier</option>
                    <option value="syllabus">Syllabus Topic Breakdown</option>
                  </select>
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: "16px" }}>
                <label>Verified Guidance Text / Content:</label>
                <textarea
                  rows="8"
                  placeholder="Paste official prospectus text, eligibility criteria, exam patterns, deadlines, or fees here..."
                  value={docContent}
                  onChange={(e) => setDocContent(e.target.value)}
                  required
                  className="search-input"
                  style={{ width: "100%", marginTop: "4px" }}
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
                  {savingDoc ? "Chunking & Generating Embeddings..." : "Upload & Index in RAG Database"}
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
