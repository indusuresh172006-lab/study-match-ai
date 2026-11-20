import { useState, useEffect, useCallback } from "react";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";

function TopicQuiz() {
  const [subjects, setSubjects] = useState([]);
  const [profile, setProfile] = useState(null);
  const [scopeForm, setScopeForm] = useState({ course: "", college: "", semester: "" });
  const [savingScope, setSavingScope] = useState(false);
  const [scopeMessage, setScopeMessage] = useState("");
  const [scopeError, setScopeError] = useState("");
  const [loadingSubjects, setLoadingSubjects] = useState(true);
  const [error, setError] = useState(null);

  // Active quiz session state
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [quizData, setQuizData] = useState(null);
  const [quizLoading, setQuizLoading] = useState(false);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [timeSpent, setTimeSpent] = useState(0);
  const [timerInterval, setTimerInterval] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Results state
  const [resultData, setResultData] = useState(null);

  // AI Revision Modal state
  const [showRevisionModal, setShowRevisionModal] = useState(false);
  const [revisionNotes, setRevisionNotes] = useState(null);
  const [loadingRevision, setLoadingRevision] = useState(false);
  const hasCourseScope = Boolean(
    profile?.course?.trim() && profile?.college?.trim() && profile?.semester?.trim()
  );

  const fetchSubjects = useCallback(async () => {
    try {
      const profileRes = await api.get("/profile/me");
      setError(null);
      const studentProfile = profileRes.data;
      setProfile(studentProfile);
      setScopeForm({
        course: studentProfile.course || "",
        college: studentProfile.college || "",
        semester: studentProfile.semester || "",
      });

      if (
        !studentProfile?.course?.trim() ||
        !studentProfile?.college?.trim() ||
        !studentProfile?.semester?.trim()
      ) {
        setSubjects([]);
        return;
      }

      const res = await api.get("/api/v1/subjects", {
        params: {
          course: studentProfile.course,
          curriculum: studentProfile.college,
          academic_year: studentProfile.semester,
        },
      });
      setSubjects(res.data || []);
    } catch (err) {
      console.error("Error fetching subjects:", err);
      setError("Failed to load subjects and topics.");
    } finally {
      setLoadingSubjects(false);
    }
  }, []);

  useEffect(() => {
    fetchSubjects();
  }, [fetchSubjects]);

  const handleUpdateCourseScope = async (e) => {
    e.preventDefault();
    setSavingScope(true);
    setScopeMessage("");
    setScopeError("");
    try {
      await api.put("/api/v1/auth/profile", {
        course: scopeForm.course.trim(),
        college: scopeForm.college.trim(),
        semester: scopeForm.semester.trim(),
      });
      setScopeMessage("Course details saved. Reloading your matching syllabus...");
      await fetchSubjects();
    } catch (err) {
      const detail = err.response?.data?.detail;
      const message = Array.isArray(detail)
        ? detail.map((item) => item.msg || "Invalid course details").join("; ")
        : typeof detail === "string"
          ? detail
          : "Could not update your course details. Please try again.";
      setScopeError(message);
    } finally {
      setSavingScope(false);
    }
  };

  const handleStartQuiz = async (topic) => {
    setSelectedTopic(topic);
    setQuizLoading(true);
    setError(null);
    setResultData(null);
    setSelectedAnswers({});
    setCurrentQIndex(0);
    setTimeSpent(0);

    try {
      const res = await api.get(`/api/v1/quiz/topic/${topic.id}`);
      setQuizData(res.data);

      // Start timer
      const interval = setInterval(() => {
        setTimeSpent((prev) => prev + 1);
      }, 1000);
      setTimerInterval(interval);
    } catch (err) {
      console.error("Error loading quiz:", err);
      setError(err.response?.data?.detail || "Could not load quiz for this topic.");
    } finally {
      setQuizLoading(false);
    }
  };

  const handleSelectOption = (questionId, optionIndex) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: optionIndex,
    }));
  };

  const handleSubmitQuiz = async () => {
    if (timerInterval) clearInterval(timerInterval);
    setSubmitting(true);
    try {
      const res = await api.post(`/api/v1/quiz/topic/${selectedTopic.id}/submit`, {
        answers: selectedAnswers,
        time_taken_sec: timeSpent,
      });
      setResultData(res.data);
    } catch (err) {
      console.error("Error submitting quiz:", err);
      setError("Error evaluating your quiz answers.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleGenerateRevisionNotes = async (topicName, subjectName) => {
    setShowRevisionModal(true);
    setLoadingRevision(true);
    setRevisionNotes(null);
    try {
      const res = await api.post("/api/v1/revision/generate", {
        topic_name: topicName,
        subject_name: subjectName || "General",
      });
      setRevisionNotes(res.data);
    } catch (err) {
      console.error("Error generating revision notes:", err);
    } finally {
      setLoadingRevision(false);
    }
  };

  if (loadingSubjects) {
    return <LoadingSpinner message="Loading academic curriculum..." />;
  }
  if (quizLoading) {
    return <LoadingSpinner message="Loading your topic quiz..." />;
  }

  // ─────────────────────────────────────────────
  // 1. ACTIVE QUIZ TAKING VIEW
  // ─────────────────────────────────────────────
  if (quizData && !resultData) {
    const currentQ = quizData.questions[currentQIndex];
    const totalQ = quizData.total_questions;
    const answeredCount = Object.keys(selectedAnswers).length;

    return (
      <div className="page-container compact-layout">
        <div className="page-header compact-header">
          <div>
            <button
              className="action-btn-secondary btn-sm"
              onClick={() => {
                if (timerInterval) clearInterval(timerInterval);
                setQuizData(null);
              }}
              style={{ marginBottom: "8px" }}
            >
              &larr; Exit Diagnostic Quiz
            </button>
            <h2>📝 {quizData.topic_name} — Diagnostic Quiz</h2>
            <p>Subject: {quizData.subject_name}</p>
          </div>
          <div className="quiz-timer-pill">
            ⏱️ Time: {Math.floor(timeSpent / 60)}:
            {(timeSpent % 60).toString().padStart(2, "0")}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="quiz-progress-bar-wrap">
          <div
            className="quiz-progress-bar-fill"
            style={{ width: `${((currentQIndex + 1) / totalQ) * 100}%` }}
          />
        </div>

        <div className="quiz-card-box">
          <div className="quiz-question-header">
            <span className="q-badge">
              Question {currentQIndex + 1} of {totalQ}
            </span>
            <span className="diff-badge">{currentQ.difficulty || "medium"}</span>
          </div>

          <h3 className="quiz-question-title">{currentQ.question_text}</h3>

          <div className="quiz-options-vertical">
            {currentQ.options.map((opt, optIdx) => {
              const isSelected = selectedAnswers[currentQ.id] === optIdx;
              return (
                <label
                  key={optIdx}
                  className={`quiz-option-choice ${isSelected ? "selected" : ""}`}
                  onClick={() => handleSelectOption(currentQ.id, optIdx)}
                >
                  <span className="option-letter">
                    {String.fromCharCode(65 + optIdx)}
                  </span>
                  <span className="option-text">{opt}</span>
                </label>
              );
            })}
          </div>

          <div className="quiz-nav-row">
            <button
              className="action-btn-secondary"
              disabled={currentQIndex === 0}
              onClick={() => setCurrentQIndex((prev) => prev - 1)}
            >
              &larr; Previous
            </button>

            {currentQIndex < totalQ - 1 ? (
              <button
                className="action-btn-primary"
                onClick={() => setCurrentQIndex((prev) => prev + 1)}
              >
                Next &rarr;
              </button>
            ) : (
              <button
                className="action-btn-success"
                onClick={handleSubmitQuiz}
                disabled={submitting}
              >
                {submitting
                  ? "Evaluating with Random Forest..."
                  : `Submit Quiz (${answeredCount}/${totalQ} Answered)`}
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // ─────────────────────────────────────────────
  // 2. QUIZ RESULTS & ML CLASSIFICATION VIEW
  // ─────────────────────────────────────────────
  if (resultData) {
    const isWeak = resultData.predicted_status === "weak";
    const isStrong = resultData.predicted_status === "strong";

    return (
      <div className="page-container compact-layout">
        <div className="page-header compact-header">
          <div>
            <h2>📊 Diagnostic Quiz Evaluation & ML Skill Classification</h2>
            <p>
              Topic: <strong>{resultData.topic_name}</strong> &bull; Subject:{" "}
              {resultData.subject_name}
            </p>
          </div>
          <button
            className="action-btn-secondary btn-sm"
            onClick={() => {
              setResultData(null);
              setQuizData(null);
            }}
          >
            &larr; Back to Curriculum
          </button>
        </div>

        {/* Hero Result Banner */}
        <div
          className={`quiz-result-hero ${
            isStrong ? "hero-strong" : isWeak ? "hero-weak" : "hero-average"
          }`}
        >
          <div className="result-hero-left">
            <span className="result-score-callout">
              {resultData.score} / {resultData.total_marks}
            </span>
            <div>
              <h3>Accuracy: {resultData.accuracy}%</h3>
              <p>Time Taken: {resultData.time_taken_sec} seconds</p>
            </div>
          </div>

          <div className="result-hero-right">
            <span className="ml-status-pill">
              {isStrong ? "🌟 Strong" : isWeak ? "🌱 Weak" : "⚡ Average"}
            </span>
            <span className="ml-confidence-sub">
              Random Forest Confidence: {resultData.ml_confidence}%
            </span>
          </div>
        </div>

        {/* Skill Profile Auto-Update Notice */}
        <div className="skill-update-notice">
          <span>
            🔄 <strong>Skill Profile Auto-Updated:</strong> Your topic mastery
            for <em>{resultData.topic_name}</em> has been set to{" "}
            <strong>{resultData.predicted_status.toUpperCase()}</strong> in the
            database. Your Study Group matching and peer-teaching recommendations
            now reflect this result!
          </span>
          {isWeak && (
            <button
              className="action-btn-primary btn-sm"
              onClick={() =>
                handleGenerateRevisionNotes(
                  resultData.topic_name,
                  resultData.subject_name
                )
              }
            >
              🚀 Generate AI Revision Notes
            </button>
          )}
        </div>

        {/* Question-by-Question Breakdown */}
        <div className="breakdown-section">
          <h3>Detailed Answers & Pedagogical Explanations</h3>
          <div className="breakdown-list">
            {resultData.questions_breakdown.map((item, idx) => (
              <div
                key={item.question_id}
                className={`breakdown-card ${item.is_correct ? "correct" : "incorrect"}`}
              >
                <div className="breakdown-header">
                  <strong>
                    Q{idx + 1}: {item.question_text}
                  </strong>
                  <span
                    className={`badge-result ${
                      item.is_correct ? "badge-correct" : "badge-incorrect"
                    }`}
                  >
                    {item.is_correct ? "✓ Correct (+1)" : "✗ Incorrect (0)"}
                  </span>
                </div>

                <div className="breakdown-options">
                  {item.options.map((opt, optI) => {
                    const isUserChoice = item.selected_option === optI;
                    const isRightAnswer = item.correct_answer === optI;

                    let choiceClass = "choice-neutral";
                    if (isRightAnswer) choiceClass = "choice-right";
                    if (isUserChoice && !isRightAnswer)
                      choiceClass = "choice-wrong";

                    return (
                      <div key={optI} className={`choice-line ${choiceClass}`}>
                        <span>
                          {String.fromCharCode(65 + optI)}. {opt}
                        </span>
                        {isUserChoice && (
                          <span className="user-choice-tag">(Your choice)</span>
                        )}
                        {isRightAnswer && (
                          <span className="correct-tag">(Correct answer)</span>
                        )}
                      </div>
                    );
                  })}
                </div>

                {item.explanation && (
                  <div className="explanation-box">
                    💡 <strong>Explanation:</strong> {item.explanation}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Modal: AI Revision Notes */}
        {showRevisionModal && (
          <div className="modal-backdrop">
            <div className="modal-dialog modal-lg">
              <div className="modal-header">
                <h3>🚀 AI Revision Notes: {resultData.topic_name}</h3>
                <button
                  className="modal-close"
                  onClick={() => setShowRevisionModal(false)}
                >
                  &times;
                </button>
              </div>

              <div className="modal-body-scrollable">
                {loadingRevision ? (
                  <LoadingSpinner message="Generating pedagogical revision notes with Gemini..." />
                ) : revisionNotes ? (
                  <div>
                    <div className="revision-overview-box">
                      <h4>📖 Overview</h4>
                      <p>{revisionNotes.overview}</p>
                    </div>

                    <div className="revision-block">
                      <h4>🔑 Essential Concepts & Formulas:</h4>
                      <ul>
                        {revisionNotes.key_concepts.map((kc, i) => (
                          <li key={i}>{kc}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="revision-block">
                      <h4>🧪 Practical Example:</h4>
                      <div className="example-box">
                        <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>
                          {revisionNotes.practical_example}
                        </pre>
                      </div>
                    </div>

                    <div className="revision-block">
                      <h4>⚠️ Common Pitfalls to Avoid:</h4>
                      <ul>
                        {revisionNotes.common_pitfalls.map((cp, i) => (
                          <li key={i} style={{ color: "#dc2626" }}>
                            {cp}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="revision-block">
                      <h4>🎯 Quick Practice Questions:</h4>
                      {revisionNotes.practice_questions.map((pq, i) => (
                        <div key={i} className="practice-q-card">
                          <strong>
                            Q{i + 1}: {pq.question}
                          </strong>
                          <div style={{ margin: "6px 0" }}>
                            {pq.options.map((opt, oI) => (
                              <div key={oI} style={{ fontSize: "12.5px" }}>
                                {opt}
                              </div>
                            ))}
                          </div>
                          <p style={{ margin: "4px 0", color: "#16a34a" }}>
                            ✓ <strong>Answer:</strong> {pq.correct_answer} &bull;{" "}
                            {pq.explanation}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p>Unable to generate revision notes at this time.</p>
                )}
              </div>

              <div className="modal-footer">
                <button
                  className="action-btn-primary"
                  onClick={() => setShowRevisionModal(false)}
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // ─────────────────────────────────────────────
  // 3. CURRICULUM BROWSER (DEFAULT VIEW)
  // ─────────────────────────────────────────────
  return (
    <div className="page-container compact-layout">
      <div className="page-header compact-header">
        <div>
          <h2>🎯 Topic-Wise Diagnostic Quizzes</h2>
          <p>
            {hasCourseScope
              ? `Teacher-approved syllabus for ${profile.course} - ${profile.college} - ${profile.semester}. `
              : "Course, board/institution, and year/semester are needed to load the right syllabus. "}
            Your answers update your skill profile and peer-study matches.
          </p>
        </div>
      </div>

      {error && <ErrorMessage error={error} onRetry={fetchSubjects} />}

      {subjects.length === 0 ? (
          <div className="syllabus-empty-card" role="status">
            <div className="syllabus-empty-icon">📘</div>
            <h3>{hasCourseScope ? "No matching syllabus published yet" : "Complete your course details first"}</h3>
            <p>
              {hasCourseScope
                ? `No syllabus currently matches ${profile.course}, ${profile.college}, ${profile.semester}. Your teacher must tag the syllabus with these exact course details.`
                : "A course, board/institution, and year/semester are required to prevent unrelated course content from appearing."}
            </p>
            <form className="course-scope-form" onSubmit={handleUpdateCourseScope}>
              <label>
                Course / program
                <input
                  type="text"
                  maxLength={100}
                  value={scopeForm.course}
                  onChange={(e) => setScopeForm({ ...scopeForm, course: e.target.value })}
                  placeholder="e.g. Diploma in Civil Engineering"
                  required
                />
              </label>
              <label>
                Board / institution
                <input
                  type="text"
                  maxLength={150}
                  value={scopeForm.college}
                  onChange={(e) => setScopeForm({ ...scopeForm, college: e.target.value })}
                  placeholder="e.g. Polytechnic College Kannur"
                  required
                />
              </label>
              <label>
                Year / semester
                <input
                  type="text"
                  maxLength={20}
                  value={scopeForm.semester}
                  onChange={(e) => setScopeForm({ ...scopeForm, semester: e.target.value })}
                  placeholder="e.g. 3rd Semester"
                  required
                />
              </label>
              <button className="action-btn-primary" type="submit" disabled={savingScope}>
                {savingScope ? "Saving..." : "Save details and reload"}
              </button>
            </form>
            {scopeMessage && <p className="scope-feedback" role="status">{scopeMessage}</p>}
            {scopeError && <p className="auth-error-msg" role="alert">{scopeError}</p>}
          </div>
      ) : (
      <div className="curriculum-subjects-list">
        {subjects.map((sub) => (
          <div key={sub.id} className="subject-curriculum-card">
            <div className="subject-card-top">
              <div>
                <span className="subject-code-tag">{sub.code || "CURR"}</span>
                <h3 className="subject-title">{sub.name}</h3>
                <p className="subject-desc">{sub.description}</p>
                <p className="subject-desc">
                  {[sub.course, sub.curriculum, sub.academic_year].filter(Boolean).join(" · ")}
                </p>
              </div>
              <span className="topic-count-pill">
                {sub.topic_count} Topics
              </span>
            </div>

            <div className="topics-selection-grid">
              {sub.topics && sub.topics.length > 0 ? (
                sub.topics.map((t) => (
                  <div key={t.id} className="topic-choice-card">
                    <div>
                      <strong className="topic-name">{t.name}</strong>
                      <p className="topic-sub-desc">
                        {t.description || "Core syllabus module"}
                      </p>
                    </div>

                    <div className="topic-action-row">
                      <span className="q-count-text">
                        📝 {t.question_count ?? 0} Questions
                      </span>
                      {t.question_count > 0 ? (
                        <button
                          className="action-btn-primary btn-sm"
                          onClick={() => handleStartQuiz(t)}
                        >
                          Start Quiz &rarr;
                        </button>
                      ) : (
                        <span className="empty-subtext">Questions not published yet</span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <p className="empty-subtext">No topics added for this subject.</p>
              )}
            </div>
          </div>
        ))}
      </div>
      )}
    </div>
  );
}

export default TopicQuiz;
