import { useState, useEffect, useCallback } from "react";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";

function TeacherGroupsPage() {
  const [classes, setClasses] = useState([]);
  const [selectedClassId, setSelectedClassId] = useState("");
  const [studyGroups, setStudyGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [groupsLoading, setGroupsLoading] = useState(false);
  const [generatingGroups, setGeneratingGroups] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const fetchClasses = useCallback(async () => {
    try {
      const res = await api.get("/api/v1/classes");
      const classList = res.data || [];
      setClasses(classList);
      if (classList.length > 0 && !selectedClassId) {
        setSelectedClassId(String(classList[0].id));
      }
    } catch (err) {
      console.error("Classes fetch error:", err);
      setError("Failed to load classes for group formation.");
    } finally {
      setLoading(false);
    }
  }, [selectedClassId]);

  const fetchStudyGroups = useCallback(async (classId) => {
    setGroupsLoading(true);
    try {
      const res = await api.get("/api/v1/groups");
      let allGroups = res.data || [];
      if (classId) {
        allGroups = allGroups.filter((g) => !g.class_id || String(g.class_id) === String(classId));
      }
      setStudyGroups(allGroups);
    } catch (err) {
      console.error("Study groups fetch error:", err);
      setError("Failed to load study groups.");
    } finally {
      setGroupsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchClasses();
  }, [fetchClasses]);

  useEffect(() => {
    fetchStudyGroups(selectedClassId);
  }, [fetchStudyGroups, selectedClassId]);

  const handleRegenerateGroups = async () => {
    if (!selectedClassId) {
      alert("Please select a class before generating groups.");
      return;
    }
    setGeneratingGroups(true);
    setError("");
    setNotice("");
    try {
      const res = await api.post("/api/v1/groups/generate", {
        class_id: selectedClassId,
        min_size: 3,
        max_size: 5,
        reset_existing: true,
      });
      setStudyGroups(res.data || []);
      setNotice("Study groups generated successfully. Review and approve each group below.");
    } catch (err) {
      console.error("Group generation error:", err);
      setError(err.response?.data?.detail || "Could not generate groups for this class. Ensure students are enrolled and have taken topic quizzes.");
    } finally {
      setGeneratingGroups(false);
    }
  };

  const handleReviewGroup = async (groupId, action) => {
    try {
      const nextStatus = action === "approve" ? "approved" : "rejected";
      await api.patch(`/api/v1/groups/${groupId}/status`, { status: nextStatus });
      setStudyGroups((prev) =>
        prev.map((g) => (g.id === groupId ? { ...g, status: nextStatus } : g))
      );
      setNotice(`Group successfully ${nextStatus}.`);
    } catch (err) {
      console.error("Group status update error:", err);
      setError(err.response?.data?.detail || "Could not update group status.");
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="teacher-groups-page">
      <div className="card-head-row" style={{ marginBottom: "20px" }}>
        <div>
          <h2>👥 Study Group Review & Peer-Teaching Matching</h2>
          <p className="subtext">
            Module 1.6 & Modules 7-8: Algorithmic peer-teaching matches where students with high mastery cover classmates' weak topics within the same cohort.
          </p>
        </div>
      </div>

      {error && <ErrorMessage message={error} />}
      {notice && (
        <div style={{ background: "#ecfdf5", border: "1px solid #a7f3d0", color: "#065f46", padding: "12px 16px", borderRadius: "8px", marginBottom: "20px" }}>
          {notice}
        </div>
      )}

      {/* Class Selector Bar & Generator */}
      <section className="teacher-section-card" style={{ marginBottom: "24px" }}>
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <label style={{ fontWeight: "600", fontSize: "14px" }}>Select Class:</label>
            <select
              value={selectedClassId}
              onChange={(e) => setSelectedClassId(e.target.value)}
              className="search-input"
              style={{ minWidth: "260px" }}
            >
              {classes.length === 0 ? (
                <option value="">No classes available</option>
              ) : (
                classes.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.course || "General"} · Code: {c.join_code})
                  </option>
                ))
              )}
            </select>
          </div>

          <button
            className="action-btn-primary"
            onClick={handleRegenerateGroups}
            disabled={generatingGroups || !selectedClassId}
          >
            {generatingGroups ? "⚡ Optimizing Peer Groups..." : "⚡ Generate Balanced Groups for Class"}
          </button>
        </div>
      </section>

      {/* Groups Table */}
      <section className="teacher-section-card">
        <div className="card-head-row">
          <div>
            <h3>Generated Study Groups ({studyGroups.length})</h3>
            <p className="subtext">
              Review weak-topic coverage and peer-teaching pairs. Approved groups are instantly visible to their students.
            </p>
          </div>
          <button
            className="action-btn-secondary btn-sm"
            onClick={() => fetchStudyGroups(selectedClassId)}
          >
            🔄 Refresh
          </button>
        </div>

        {groupsLoading ? (
          <p>Analyzing student skill profiles and matching groups...</p>
        ) : studyGroups.length === 0 ? (
          <div style={{ padding: "40px 20px", textAlign: "center", color: "var(--text-muted)" }}>
            <div style={{ fontSize: "36px", marginBottom: "8px" }}>👥</div>
            <strong>No study groups generated yet for this class.</strong>
            <p style={{ margin: "4px 0 0" }}>
              Click <strong>&quot;Generate Balanced Groups for Class&quot;</strong> above to match students using their skill profile strengths and weak areas.
            </p>
          </div>
        ) : (
          <div className="class-topics-table-wrapper">
            <table className="teacher-table">
              <thead>
                <tr>
                  <th>Group Name</th>
                  <th>Status</th>
                  <th>Members (3-5)</th>
                  <th>Weak-Topic Coverage</th>
                  <th>Teaching Pairs</th>
                  <th>Uncovered Topics</th>
                  <th>Schedule Slots</th>
                  <th>Follow-up Progress</th>
                  <th>Teacher Review</th>
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
                        <span className="subtext">No follow-up test yet</span>
                      ) : (
                        <span style={{ color: grp.progress_summary.change_points >= 0 ? "#15803d" : "#b91c1c", fontWeight: "600" }}>
                          {grp.progress_summary.change_points > 0 ? "+" : ""}
                          {grp.progress_summary.change_points} pts
                          <small style={{ color: "#64748b", fontWeight: "400" }}>
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
                            Approve ✓
                          </button>
                          <button
                            className="action-btn-secondary btn-sm"
                            onClick={() => handleReviewGroup(grp.id, "reject")}
                          >
                            Reject ✕
                          </button>
                        </div>
                      ) : (
                        <button
                          className="table-action-btn"
                          onClick={() => handleReviewGroup(grp.id, grp.status === "approved" ? "reject" : "approve")}
                        >
                          {grp.status === "approved" ? "Revoke Approval" : "Re-approve"}
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
    </div>
  );
}

export default TeacherGroupsPage;
