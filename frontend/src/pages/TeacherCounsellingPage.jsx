import { useState, useEffect, useCallback } from "react";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";

function TeacherCounsellingPage() {
  const [requests, setRequests] = useState([]);
  const [filterStatus, setFilterStatus] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const [selectedRequest, setSelectedRequest] = useState(null);
  const [newStatus, setNewStatus] = useState("scheduled");
  const [teacherNotes, setTeacherNotes] = useState("");
  const [savingNotes, setSavingNotes] = useState(false);

  const fetchRequests = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get("/api/v1/guidance/counselling");
      setRequests(res.data || []);
      setError("");
    } catch (err) {
      console.error("Counselling requests fetch error:", err);
      setError("Failed to load counselling requests.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRequests();
  }, [fetchRequests]);

  const handleUpdateRequest = async (e) => {
    e.preventDefault();
    if (!selectedRequest) return;
    setSavingNotes(true);
    setError("");
    setNotice("");
    try {
      await api.patch(`/api/v1/guidance/counselling/${selectedRequest.id}`, {
        status: newStatus,
        teacher_notes: teacherNotes,
      });
      setNotice(`Successfully updated counselling request for ${selectedRequest.student_name || "student"}.`);
      setSelectedRequest(null);
      fetchRequests();
    } catch (err) {
      console.error("Counselling update error:", err);
      setError(err.response?.data?.detail || "Could not update counselling request.");
    } finally {
      setSavingNotes(false);
    }
  };

  const filteredRequests = requests.filter((r) => {
    if (filterStatus === "all") return true;
    return r.status === filterStatus;
  });

  return (
    <div className="teacher-counselling-page">
      <div className="card-head-row" style={{ marginBottom: "20px" }}>
        <div>
          <h2>🤝 Student Study Support & Higher Studies Guidance</h2>
          <p className="subtext">
            Module 4.D: Review student doubt inquiries, study session assistance requests, and higher studies / entrance exam questions.
          </p>
        </div>
        <button className="action-btn-secondary" onClick={fetchRequests}>
          🔄 Refresh Inquiries
        </button>
      </div>

      {error && <ErrorMessage message={error} />}
      {notice && (
        <div style={{ background: "#ecfdf5", border: "1px solid #a7f3d0", color: "#065f46", padding: "12px 16px", borderRadius: "8px", marginBottom: "20px" }}>
          {notice}
        </div>
      )}

      {/* Filter Tabs */}
      <div className="teacher-module-tabs" style={{ marginBottom: "20px" }}>
        <button
          className={`teacher-module-tab-btn ${filterStatus === "all" ? "active" : ""}`}
          onClick={() => setFilterStatus("all")}
        >
          All Requests ({requests.length})
        </button>
        <button
          className={`teacher-module-tab-btn ${filterStatus === "pending" ? "active" : ""}`}
          onClick={() => setFilterStatus("pending")}
        >
          Pending Review
          {requests.filter((r) => r.status === "pending").length > 0 && (
            <span className="tab-pill-badge">
              {requests.filter((r) => r.status === "pending").length}
            </span>
          )}
        </button>
        <button
          className={`teacher-module-tab-btn ${filterStatus === "scheduled" ? "active" : ""}`}
          onClick={() => setFilterStatus("scheduled")}
        >
          Scheduled Sessions ({requests.filter((r) => r.status === "scheduled").length})
        </button>
        <button
          className={`teacher-module-tab-btn ${filterStatus === "completed" ? "active" : ""}`}
          onClick={() => setFilterStatus("completed")}
        >
          Completed ({requests.filter((r) => r.status === "completed").length})
        </button>
      </div>

      <section className="teacher-section-card">
        {loading ? (
          <LoadingSpinner />
        ) : filteredRequests.length === 0 ? (
          <div style={{ padding: "40px 20px", textAlign: "center", color: "var(--text-muted)" }}>
            <div style={{ fontSize: "36px", marginBottom: "8px" }}>🎉</div>
            <strong>No {filterStatus !== "all" ? filterStatus : ""} counselling requests found.</strong>
            <p style={{ margin: "4px 0 0" }}>When students submit guidance or study support requests, they will appear here.</p>
          </div>
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
                {filteredRequests.map((req) => (
                  <tr key={req.id}>
                    <td>
                      <strong>{req.student_name || `Student #${req.student_id}`}</strong>
                    </td>
                    <td>
                      <span className="subject-pill">
                        {req.request_type === "study_support" ? "Study Support" : "Higher Studies"}
                      </span>
                    </td>
                    <td>
                      <span className="mode-badge">📍 {req.preferred_mode}</span>
                    </td>
                    <td style={{ maxWidth: "280px" }}>
                      <p style={{ margin: 0, fontSize: "13px" }}>{req.message}</p>
                    </td>
                    <td>{new Date(req.created_at).toLocaleDateString()}</td>
                    <td>
                      <span className={`status-badge status-${req.status}`}>
                        {req.status.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ maxWidth: "220px", fontSize: "12px", color: "var(--text-muted)" }}>
                      {req.teacher_notes || "No notes entered"}
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
                  placeholder="e.g. Scheduled for Friday at 4:00 PM via Google Meet link: meet.google.com/xyz or Meet in Staff Room 204..."
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
    </div>
  );
}

export default TeacherCounsellingPage;
