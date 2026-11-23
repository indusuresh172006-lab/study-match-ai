import { useState, useEffect } from "react";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import EmptyState from "../components/EmptyState";

function CourseSummaries({ user }) {
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSubject, setSelectedSubject] = useState("All");

  // Revise Quickly Modal State
  const [activeSummary, setActiveSummary] = useState(null);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [quizResult, setQuizResult] = useState(null);
  const [submittingQuiz, setSubmittingQuiz] = useState(false);

  // Teacher Edit Modal State
  const [editingSummary, setEditingSummary] = useState(null);
  const [editFormData, setEditFormData] = useState({
    title: "",
    overview: "",
    quick_revision_notes: "",
  });
  const [savingEdit, setSavingEdit] = useState(false);

  const summarySubjects = [...new Set(summaries.map((summary) => summary.subject).filter(Boolean))];
  const visibleSummaries = selectedSubject === "All"
    ? summaries
    : summaries.filter((summary) => summary.subject === selectedSubject);

  const fetchSummaries = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get("/summaries");
      setSummaries(res.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load course summaries.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummaries();
  }, []);

  const handleOpenReviseModal = (sum) => {
    setActiveSummary(sum);
    setQuizAnswers({});
    setQuizResult(null);
  };

  const handleSelectQuizOption = (qIdx, optIdx) => {
    setQuizAnswers((prev) => ({
      ...prev,
      [qIdx]: optIdx,
    }));
  };

  const handleSubmitQuiz = async () => {
    if (!activeSummary) return;
    setSubmittingQuiz(true);
    try {
      const answersPayload = Object.keys(quizAnswers).map((k) => ({
        question_index: Number(k),
        selected_option: quizAnswers[k],
      }));
      const res = await api.post(`/summaries/${activeSummary.id}/quiz-submit`, {
        summary_id: activeSummary.id,
        answers: answersPayload,
      });
      setQuizResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Failed to score rapid quiz.");
    } finally {
      setSubmittingQuiz(false);
    }
  };

  const handleOpenEditModal = (sum) => {
    setEditingSummary(sum);
    setEditFormData({
      title: sum.title,
      overview: sum.overview,
      quick_revision_notes: sum.quick_revision_notes,
    });
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    if (!editingSummary) return;
    setSavingEdit(true);
    try {
      await api.put(`/summaries/${editingSummary.id}`, editFormData);
      setEditingSummary(null);
      fetchSummaries();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to save summary updates");
    } finally {
      setSavingEdit(false);
    }
  };

  const isTeacher = ["teacher", "admin"].includes(user?.role);

  return (
    <div className="course-summaries-page">
      {/* Header */}
      <div className="page-header-row">
        <div>
          <h2>📖 Course Summaries & High-Yield Quick Revision</h2>
          <p className="page-subtitle">
            Revision summaries and quick quizzes matched to your current course and semester.
          </p>
        </div>
      </div>

      {/* Subject Tabs */}
      <div className="subject-tabs-bar">
        {["All", ...summarySubjects].map((subj) => (
          <button
            key={subj}
            className={`subj-tab ${selectedSubject === subj ? "active" : ""}`}
            onClick={() => setSelectedSubject(subj)}
          >
            {subj}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingSpinner message="Loading course summaries..." />
      ) : error ? (
        <ErrorMessage error={error} onRetry={fetchSummaries} />
      ) : visibleSummaries.length === 0 ? (
        <EmptyState
          icon="📚"
          title="No course summaries found"
          message="Summaries for your course and semester will appear here when available."
        />
      ) : (
        <div className="summaries-grid">
          {visibleSummaries.map((sum) => (
            <div key={sum.id} className="summary-card">
              <div className="summary-card-top">
                <span className="summary-subj-badge">{sum.subject}</span>
                <span className="summary-topic-badge">📌 {sum.topic}</span>
                {sum.academic_year && (
                  <span className="summary-topic-badge">{sum.academic_year}</span>
                )}
              </div>

              <h3 className="summary-title">{sum.title}</h3>
              <p className="summary-overview">{sum.overview}</p>

              <div className="key-points-preview">
                <strong>Key Takeaway Points:</strong>
                <ul>
                  {sum.key_points.slice(0, 3).map((pt, idx) => (
                    <li key={idx}>• {pt}</li>
                  ))}
                </ul>
              </div>

              <div className="summary-card-footer">
                <button
                  className="revise-btn"
                  onClick={() => handleOpenReviseModal(sum)}
                >
                  ⚡ Revise Quickly & Quiz
                </button>
                {isTeacher && (
                  <button
                    className="edit-summary-btn"
                    onClick={() => handleOpenEditModal(sum)}
                  >
                    ✏️ Edit
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Revise Quickly Modal */}
      {activeSummary && (
        <div className="modal-backdrop" onClick={() => setActiveSummary(null)}>
          <div className="revise-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-topbar">
              <div>
                <span className="summary-subj-badge">{activeSummary.subject}</span>
                <h3>{activeSummary.title}</h3>
              </div>
              <button
                className="modal-close-btn"
                onClick={() => setActiveSummary(null)}
              >
                ✕
              </button>
            </div>

            <div className="revise-modal-body">
              {/* High Yield Key Points */}
              <div className="revise-section">
                <h4>📌 High-Yield Key Points</h4>
                <div className="key-points-box">
                  {activeSummary.key_points.map((pt, idx) => (
                    <div key={idx} className="key-point-row">
                      <span className="check-bullet">✓</span>
                      <span>{pt}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Fast Revision Notes */}
              <div className="revise-section">
                <h4>⚡ Fast Revision Notes & Formulas</h4>
                <div className="quick-notes-pre">
                  <pre>{activeSummary.quick_revision_notes}</pre>
                </div>
              </div>

              {/* End-of-Summary Rapid Retention Quiz */}
              <div className="revise-section retention-quiz-box">
                <h4>🎯 Rapid Concept Retention Quiz</h4>
                <p className="quiz-desc">
                  Test your understanding immediately before leaving this topic!
                </p>

                {activeSummary.quiz_questions && activeSummary.quiz_questions.length > 0 ? (
                  <div className="quiz-questions-list">
                    {activeSummary.quiz_questions.map((q, qIdx) => {
                      const selectedOpt = quizAnswers[qIdx];
                      const qDetail = quizResult?.details?.[qIdx];

                      return (
                        <div key={qIdx} className="quick-quiz-card">
                          <p className="quick-quiz-qtext">
                            <strong>Q{qIdx + 1}.</strong> {q.question}
                          </p>

                          <div className="quick-quiz-options">
                            {q.options.map((opt, optIdx) => {
                              const isSelected = selectedOpt === optIdx;
                              let statusClass = "";
                              if (qDetail) {
                                if (qDetail.correct_option === optIdx) statusClass = "correct";
                                else if (isSelected && !qDetail.is_correct) statusClass = "wrong";
                              } else if (isSelected) {
                                statusClass = "selected";
                              }

                              return (
                                <button
                                  key={optIdx}
                                  type="button"
                                  disabled={!!quizResult}
                                  className={`quick-opt-btn ${statusClass}`}
                                  onClick={() => handleSelectQuizOption(qIdx, optIdx)}
                                >
                                  <span className="opt-idx-char">
                                    {String.fromCharCode(65 + optIdx)}
                                  </span>
                                  <span>{opt}</span>
                                </button>
                              );
                            })}
                          </div>

                          {qDetail && (
                            <div className="quick-explanation">
                              💡 <strong>Explanation:</strong> {qDetail.explanation}
                            </div>
                          )}
                        </div>
                      );
                    })}

                    {!quizResult ? (
                      <button
                        className="submit-quick-quiz-btn"
                        onClick={handleSubmitQuiz}
                        disabled={
                          submittingQuiz ||
                          Object.keys(quizAnswers).length < activeSummary.quiz_questions.length
                        }
                      >
                        {submittingQuiz ? "Checking..." : "Submit Rapid Quiz ✓"}
                      </button>
                    ) : (
                      <div className="quick-quiz-result-banner">
                        <span className="res-score">
                          Score: {quizResult.score} / {quizResult.total} ({quizResult.percentage}%)
                        </span>
                        <p className="res-feedback">{quizResult.feedback}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <p>No quiz questions attached to this summary.</p>
                )}
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="action-btn-secondary"
                onClick={() => setActiveSummary(null)}
              >
                Done Revise
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Teacher Edit Modal */}
      {editingSummary && (
        <div className="modal-backdrop" onClick={() => setEditingSummary(null)}>
          <div className="form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-topbar">
              <h3>Edit Course Summary</h3>
              <button
                className="modal-close-btn"
                onClick={() => setEditingSummary(null)}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveEdit} className="edit-summary-form">
              <label>Title</label>
              <input
                type="text"
                required
                value={editFormData.title}
                onChange={(e) =>
                  setEditFormData({ ...editFormData, title: e.target.value })
                }
              />

              <label>Overview</label>
              <textarea
                rows={3}
                required
                value={editFormData.overview}
                onChange={(e) =>
                  setEditFormData({ ...editFormData, overview: e.target.value })
                }
              />

              <label>Quick Revision Notes</label>
              <textarea
                rows={6}
                required
                value={editFormData.quick_revision_notes}
                onChange={(e) =>
                  setEditFormData({
                    ...editFormData,
                    quick_revision_notes: e.target.value,
                  })
                }
              />

              <div className="form-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => setEditingSummary(null)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="submit-btn"
                  disabled={savingEdit}
                >
                  {savingEdit ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default CourseSummaries;
