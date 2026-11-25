import { useState, useEffect, useCallback } from "react";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";

function TeacherRevisionNotesPage() {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const fetchQueue = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get("/api/v1/revision/review-queue");
      setQueue(res.data || []);
      setError("");
    } catch (err) {
      console.error("Revision queue error:", err);
      setError("Failed to load revision notes review queue.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchQueue();
  }, [fetchQueue]);

  const handleReview = async (noteId, action) => {
    try {
      await api.post(`/api/v1/revision/${noteId}/review`, { action });
      setNotice(`Revision note ${action === "approve" ? "approved" : "rejected"} successfully.`);
      setQueue((prev) => prev.filter((item) => item.id !== noteId));
    } catch (err) {
      console.error("Revision note review error:", err);
      setError(err.response?.data?.detail || "Could not review revision note.");
    }
  };

  return (
    <div className="teacher-revision-notes-page">
      <div className="card-head-row" style={{ marginBottom: "20px" }}>
        <div>
          <h2>🧠 AI Revision Notes Awaiting Review</h2>
          <p className="subtext">
            Module 10: Review AI-generated revision notes and peer-teaching outlines before publishing them to learners for group study.
          </p>
        </div>
        <button className="action-btn-secondary" onClick={fetchQueue}>
          🔄 Refresh Queue
        </button>
      </div>

      {error && <ErrorMessage message={error} />}
      {notice && (
        <div style={{ background: "#ecfdf5", border: "1px solid #a7f3d0", color: "#065f46", padding: "12px 16px", borderRadius: "8px", marginBottom: "20px" }}>
          {notice}
        </div>
      )}

      <section className="teacher-section-card">
        {loading ? (
          <LoadingSpinner />
        ) : queue.length === 0 ? (
          <div style={{ padding: "40px 20px", textAlign: "center", color: "var(--text-muted)" }}>
            <div style={{ fontSize: "36px", marginBottom: "8px" }}>🎉</div>
            <strong>No revision notes waiting for review!</strong>
            <p style={{ margin: "4px 0 0" }}>When AI generates custom revision notes for struggling students, they will queue here for your sign-off.</p>
          </div>
        ) : (
          <div className="class-topics-table-wrapper">
            <table className="teacher-table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Subject / Topic</th>
                  <th>Content Overview & Outline</th>
                  <th>Teacher Review</th>
                </tr>
              </thead>
              <tbody>
                {queue.map((note) => (
                  <tr key={note.id}>
                    <td>
                      <strong>{note.student_name}</strong>
                    </td>
                    <td>
                      <span className="subject-pill">{note.subject_name}</span>
                      <div style={{ fontWeight: "600", marginTop: "4px" }}>{note.topic_name}</div>
                    </td>
                    <td style={{ maxWidth: "420px" }}>
                      <strong>{note.content?.overview}</strong>
                      <p className="subtext" style={{ marginTop: "4px" }}>{note.content?.teaching_outline}</p>
                    </td>
                    <td>
                      <div className="teacher-review-actions">
                        <button
                          className="action-btn-success btn-sm"
                          onClick={() => handleReview(note.id, "approve")}
                        >
                          Approve ✓
                        </button>
                        <button
                          className="action-btn-secondary btn-sm"
                          onClick={() => handleReview(note.id, "reject")}
                        >
                          Reject ✕
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
    </div>
  );
}

export default TeacherRevisionNotesPage;
