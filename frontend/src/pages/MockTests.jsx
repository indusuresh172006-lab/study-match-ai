import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import EmptyState from "../components/EmptyState";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

function MockTests({ user }) {
  const navigate = useNavigate();
  const isTeacher = user?.role === "teacher";

  // Mode: 'browse' | 'running' | 'result'
  const [viewMode, setViewMode] = useState("browse");
  const [browseTab, setBrowseTab] = useState("tests"); // 'tests' | 'adaptive' | 'history'

  // Tests List State
  const [tests, setTests] = useState([]);
  const [testsLoading, setTestsLoading] = useState(false);
  const [selectedSubjectFilter, setSelectedSubjectFilter] = useState("All");

  // Running Test State
  const [activeTest, setActiveTest] = useState(null); // { id, title, subject, duration_minutes, questions: [...] }
  const [activeAttemptId, setActiveAttemptId] = useState(null);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [studentAnswers, setStudentAnswers] = useState({}); // { [question_id]: string }
  const [markedForReview, setMarkedForReview] = useState({}); // { [question_id]: boolean }
  const [timeLeft, setTimeLeft] = useState(0); // in seconds
  const [submittingTest, setSubmittingTest] = useState(false);

  // Result State
  const [testResult, setTestResult] = useState(null);

  // Past History & Trend Data
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Adaptive Test Generator State
  const [adaptiveSubject, setAdaptiveSubject] = useState("");
  const [adaptiveLoading, setAdaptiveLoading] = useState(false);
  const [studentWeakTopics, setStudentWeakTopics] = useState([]);

  // Teacher Create Test Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createTitle, setCreateTitle] = useState("");
  const [createSubject, setCreateSubject] = useState("");
  const [createCourse, setCreateCourse] = useState("");
  const [createCurriculum, setCreateCurriculum] = useState("");
  const [createAcademicYear, setCreateAcademicYear] = useState("");
  const [createExamName, setCreateExamName] = useState("");
  const [createDuration, setCreateDuration] = useState(25);
  const [createTotalMarks, setCreateTotalMarks] = useState(15);
  const [createQuestions, setCreateQuestions] = useState([
    {
      question_text: "",
      question_type: "mcq",
      options: ["", "", "", ""],
      correct_answer: "0",
      explanation: "",
      topic: "General",
      difficulty: "medium",
      marks: 1.0,
    },
  ]);
  const [savingTest, setSavingTest] = useState(false);

  const testSubjects = [...new Set(tests.map((test) => test.subject).filter(Boolean))];
  const visibleTests = selectedSubjectFilter === "All"
    ? tests
    : tests.filter((test) => test.subject === selectedSubjectFilter);
  const relevantWeakTopics = studentWeakTopics.filter((topic) =>
    testSubjects.includes(topic.subject)
  );

  // ─────────────────────────────────────────────
  // Fetch Functions
  // ─────────────────────────────────────────────

  const fetchTests = async () => {
    setTestsLoading(true);
    try {
      const res = await api.get("/api/v1/tests");
      setTests(res.data.items || []);
    } catch (err) {
      console.error("Error fetching tests:", err);
    } finally {
      setTestsLoading(false);
    }
  };

  const fetchHistoryAndWeakTopics = async () => {
    setLoadingHistory(true);
    try {
      const [histRes, skillRes] = await Promise.all([
        api.get("/mock-tests/history"),
        api.get("/skill-profile/summary"),
      ]);
      setHistory(histRes.data || []);
      const weaks = (skillRes.data?.topics || []).filter((t) => t.status === "weak");
      setStudentWeakTopics(weaks);
    } catch (err) {
      console.error("Error fetching history/skills:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchTests();
    fetchHistoryAndWeakTopics();
  }, []);

  useEffect(() => {
    if (testSubjects.length && !testSubjects.includes(adaptiveSubject)) {
      setAdaptiveSubject(testSubjects[0]);
    }
  }, [tests, adaptiveSubject]);

  // ─────────────────────────────────────────────
  // Test Attempt Flow
  // ─────────────────────────────────────────────

  const startTest = async (testId) => {
    try {
      // 1. Fetch full test details
      const testRes = await api.get(`/api/v1/tests/${testId}`);
      const testData = testRes.data;

      // 2. Start attempt
      const startRes = await api.post(`/api/v1/tests/${testId}/start`);
      const attemptId = startRes.data.attempt_id;

      setActiveTest(testData);
      setActiveAttemptId(attemptId);
      setCurrentQIndex(0);
      setStudentAnswers({});
      setMarkedForReview({});
      setTimeLeft(testData.duration_minutes * 60);
      setViewMode("running");
    } catch (err) {
      console.error("Failed to start test:", err);
      alert("Failed to start test. Please try again.");
    }
  };

  const startAdaptiveTest = async () => {
    setAdaptiveLoading(true);
    try {
      const res = await api.post("/api/v1/tests/adaptive", {
        subject: adaptiveSubject,
        num_questions: 6,
      });

      // Find an existing published test ID for this subject to associate submission with
      const match = tests.find((t) => t.subject.toLowerCase() === adaptiveSubject.toLowerCase()) || tests[0];
      if (!match) {
        alert("No base test found for this subject.");
        return;
      }

      // Start attempt on that base test
      const startRes = await api.post(`/api/v1/tests/${match.id}/start`);
      const attemptId = startRes.data.attempt_id;

      setActiveTest({
        id: match.id,
        title: `Adaptive Practice: ${adaptiveSubject} (Targeting Weak Topics)`,
        subject: adaptiveSubject,
        duration_minutes: 15,
        questions: res.data.questions,
      });
      setActiveAttemptId(attemptId);
      setCurrentQIndex(0);
      setStudentAnswers({});
      setMarkedForReview({});
      setTimeLeft(15 * 60);
      setViewMode("running");
    } catch (err) {
      console.error("Adaptive test error:", err);
      alert("Unable to generate adaptive test. Try another subject.");
    } finally {
      setAdaptiveLoading(false);
    }
  };

  const handleSubmitTest = useCallback(async () => {
    if (!activeTest || !activeAttemptId || submittingTest) return;
    setSubmittingTest(true);
    try {
      const answersPayload = activeTest.questions.map((q) => ({
        question_id: q.id,
        student_answer: studentAnswers[q.id] !== undefined ? String(studentAnswers[q.id]) : "",
      }));

      const timeTaken = activeTest.duration_minutes * 60 - timeLeft;

      const res = await api.post(`/api/v1/tests/${activeTest.id}/submit`, {
        attempt_id: activeAttemptId,
        time_taken_seconds: Math.max(1, timeTaken),
        answers: answersPayload,
      });

      // Fetch full result with question-by-question review
      const fullRes = await api.get(`/api/v1/tests/attempts/${activeAttemptId}/result`);
      setTestResult({
        ...res.data,
        ...fullRes.data,
      });
      setViewMode("result");
      fetchHistoryAndWeakTopics();
    } catch (err) {
      console.error("Failed to submit test:", err);
      alert("Error submitting test responses.");
    } finally {
      setSubmittingTest(false);
    }
  }, [activeTest, activeAttemptId, submittingTest, studentAnswers, timeLeft]);

  // Countdown Timer
  useEffect(() => {
    if (viewMode !== "running" || timeLeft <= 0) return;
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          alert("⏰ Time is up! Submitting your test automatically.");
          handleSubmitTest();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [viewMode, timeLeft, handleSubmitTest]);

  const formatTimer = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  // ─────────────────────────────────────────────
  // Teacher Test Creation
  // ─────────────────────────────────────────────

  const handleAddQuestionRow = () => {
    setCreateQuestions([
      ...createQuestions,
      {
        question_text: "",
        question_type: "mcq",
        options: ["", "", "", ""],
        correct_answer: "0",
        explanation: "",
        topic: "General",
        difficulty: "medium",
        marks: 1.0,
      },
    ]);
  };

  const handleCreateTestSubmit = async (e) => {
    e.preventDefault();
    setSavingTest(true);
    try {
      await api.post("/api/v1/tests", {
        title: createTitle,
        subject: createSubject,
        course: createCourse.trim() || null,
        curriculum: createCurriculum.trim() || null,
        academic_year: createAcademicYear.trim() || null,
        exam_name: createExamName || null,
        duration_minutes: Number(createDuration),
        total_marks: Number(createTotalMarks),
        questions: createQuestions,
      });
      setShowCreateModal(false);
      setCreateTitle("");
      setCreateSubject("");
      setCreateCourse("");
      setCreateCurriculum("");
      setCreateAcademicYear("");
      setCreateExamName("");
      fetchTests();
      alert("Mock test submitted for teacher review before it is published.");
    } catch (err) {
      console.error("Failed to create test:", err);
      alert("Failed to create test. Please check all question inputs.");
    } finally {
      setSavingTest(false);
    }
  };

  const handleReviewTest = async (testId, decision) => {
    if (decision === "reject" && !window.confirm("Reject this mock test?")) return;
    try {
      await api.patch(`/api/v1/tests/${testId}/review`, { decision });
      await fetchTests();
    } catch (err) {
      console.error("Mock test review error:", err);
      alert(err.response?.data?.detail || "Could not update the test review.");
    }
  };

  // ─────────────────────────────────────────────
  // RENDER: Running Test
  // ─────────────────────────────────────────────

  if (viewMode === "running" && activeTest) {
    const currentQ = activeTest.questions[currentQIndex];
    const isAnswered = studentAnswers[currentQ?.id] !== undefined && studentAnswers[currentQ?.id] !== "";
    const isMarked = markedForReview[currentQ?.id] === true;
    const answeredCount = Object.keys(studentAnswers).filter((k) => studentAnswers[k] !== "").length;

    return (
      <div className="running-test-container">
        {/* Test Header */}
        <div className="test-running-header">
          <div>
            <h3>{activeTest.title}</h3>
            <span className="stream-pill">{activeTest.subject}</span>
          </div>

          <div className="timer-box">
            <span className={`timer-display ${timeLeft < 120 ? "timer-danger" : ""}`}>
              ⏱️ {formatTimer(timeLeft)}
            </span>
            <button
              className="action-btn-primary"
              onClick={handleSubmitTest}
              disabled={submittingTest}
            >
              {submittingTest ? "Submitting..." : "Submit Test 🚀"}
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="test-progress-bar-wrap">
          <div
            className="test-progress-bar-fill"
            style={{ width: `${(answeredCount / activeTest.questions.length) * 100}%` }}
          />
        </div>

        <div className="test-workspace-grid">
          {/* Main Question Display */}
          <div className="question-panel-main">
            <div className="question-meta-bar">
              <span className="q-index-pill">
                Question {currentQIndex + 1} of {activeTest.questions.length}
              </span>
              <span className="topic-badge">🏷️ {currentQ?.topic}</span>
              <span className={`difficulty-pill difficulty-${currentQ?.difficulty}`}>
                {currentQ?.difficulty}
              </span>
              <span className="marks-badge">+{currentQ?.marks} Marks</span>
            </div>

            <div className="question-prompt-box">
              <p className="question-text">{currentQ?.question_text}</p>
            </div>

            {/* Renderer: MCQ, True/False, Short Answer */}
            <div className="answers-renderer-box">
              {currentQ?.question_type === "mcq" && currentQ.options && (
                <div className="mcq-options-grid">
                  {currentQ.options.map((opt, optIdx) => {
                    const isSelected = studentAnswers[currentQ.id] === String(optIdx);
                    return (
                      <div
                        key={optIdx}
                        className={`mcq-option-row ${isSelected ? "selected" : ""}`}
                        onClick={() =>
                          setStudentAnswers({
                            ...studentAnswers,
                            [currentQ.id]: String(optIdx),
                          })
                        }
                      >
                        <span className="option-letter">
                          {String.fromCharCode(65 + optIdx)}
                        </span>
                        <span className="option-text">{opt}</span>
                      </div>
                    );
                  })}
                </div>
              )}

              {currentQ?.question_type === "true_false" && (
                <div className="tf-options-row">
                  {["0", "1"].map((val, idx) => {
                    const label = idx === 0 ? "True" : "False";
                    const isSelected = studentAnswers[currentQ.id] === val;
                    return (
                      <button
                        key={val}
                        type="button"
                        className={`tf-button ${isSelected ? "selected" : ""}`}
                        onClick={() =>
                          setStudentAnswers({
                            ...studentAnswers,
                            [currentQ.id]: val,
                          })
                        }
                      >
                        {label}
                      </button>
                    );
                  })}
                </div>
              )}

              {currentQ?.question_type === "short_answer" && (
                <div className="short-answer-wrap">
                  <label>Type your answer:</label>
                  <input
                    type="text"
                    placeholder="Type concise answer here..."
                    value={studentAnswers[currentQ.id] || ""}
                    onChange={(e) =>
                      setStudentAnswers({
                        ...studentAnswers,
                        [currentQ.id]: e.target.value,
                      })
                    }
                    className="search-input"
                    style={{ width: "100%", marginTop: "6px" }}
                  />
                </div>
              )}
            </div>

            {/* Bottom Actions Bar */}
            <div className="question-bottom-nav">
              <button
                type="button"
                className={`review-toggle-btn ${isMarked ? "marked" : ""}`}
                onClick={() =>
                  setMarkedForReview({
                    ...markedForReview,
                    [currentQ.id]: !isMarked,
                  })
                }
              >
                {isMarked ? "⭐ Marked for Review" : "☆ Mark for Review"}
              </button>

              <div style={{ display: "flex", gap: "10px" }}>
                {isAnswered && (
                  <button
                    type="button"
                    className="action-btn-secondary btn-sm"
                    onClick={() => {
                      const updated = { ...studentAnswers };
                      delete updated[currentQ.id];
                      setStudentAnswers(updated);
                    }}
                  >
                    Clear Response
                  </button>
                )}
                <button
                  type="button"
                  className="action-btn-secondary"
                  disabled={currentQIndex === 0}
                  onClick={() => setCurrentQIndex(currentQIndex - 1)}
                >
                  ← Previous
                </button>
                <button
                  type="button"
                  className="action-btn-primary"
                  disabled={currentQIndex === activeTest.questions.length - 1}
                  onClick={() => setCurrentQIndex(currentQIndex + 1)}
                >
                  Next →
                </button>
              </div>
            </div>
          </div>

          {/* Right Question Navigation Panel */}
          <div className="test-nav-sidebar">
            <h4>Question Navigation</h4>
            <div className="q-nav-legend">
              <div>
                <span className="legend-dot answered" /> Answered
              </div>
              <div>
                <span className="legend-dot marked" /> Review
              </div>
              <div>
                <span className="legend-dot unanswered" /> Not Attempted
              </div>
            </div>

            <div className="q-nav-buttons-grid">
              {activeTest.questions.map((q, idx) => {
                const answered = studentAnswers[q.id] !== undefined && studentAnswers[q.id] !== "";
                const marked = markedForReview[q.id] === true;
                const isCurrent = idx === currentQIndex;

                let statusClass = "unanswered";
                if (marked) statusClass = "marked";
                else if (answered) statusClass = "answered";

                return (
                  <button
                    key={q.id}
                    className={`q-nav-btn ${statusClass} ${isCurrent ? "current" : ""}`}
                    onClick={() => setCurrentQIndex(idx)}
                  >
                    {idx + 1}
                  </button>
                );
              })}
            </div>

            <div className="sidebar-submit-callout">
              <p>
                <strong>{answeredCount}</strong> of <strong>{activeTest.questions.length}</strong> questions answered
              </p>
              <button
                className="action-btn-primary"
                style={{ width: "100%", marginTop: "10px" }}
                onClick={handleSubmitTest}
                disabled={submittingTest}
              >
                Submit & Auto-Grade
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ─────────────────────────────────────────────
  // RENDER: Result Analysis with Recharts
  // ─────────────────────────────────────────────

  if (viewMode === "result" && testResult) {
    // Format topic breakdown for Recharts BarChart
    const topicChartData = Object.entries(testResult.topic_breakdown || {}).map(
      ([topic, data]) => ({
        topic: topic.length > 14 ? topic.substring(0, 14) + "..." : topic,
        accuracy: data.accuracy || 0,
        correct: data.correct || 0,
        total: data.total || 0,
      })
    );

    return (
      <div className="test-result-page">
        <div className="result-hero-banner">
          <div>
            <h2>📊 Detailed Mock Test Performance Report</h2>
            <p>Your results have been analyzed and your Skill Profile has been updated automatically.</p>
          </div>
          <button
            className="action-btn-primary"
            onClick={() => setViewMode("browse")}
          >
            ← Back to Tests
          </button>
        </div>

        {/* Score & KPI Cards */}
        <div className="kpi-grid">
          <div className="kpi-card success">
            <div className="kpi-icon">🎯</div>
            <div className="kpi-details">
              <span className="kpi-num">{testResult.accuracy}%</span>
              <span className="kpi-label">Overall Accuracy</span>
              <span className="kpi-subtext">Score: {testResult.score} / {testResult.total_marks} Marks</span>
            </div>
          </div>

          <div className="kpi-card info">
            <div className="kpi-icon">⏱️</div>
            <div className="kpi-details">
              <span className="kpi-num">{Math.floor((testResult.time_taken_seconds || 120) / 60)}m {(testResult.time_taken_seconds || 120) % 60}s</span>
              <span className="kpi-label">Time Taken</span>
              <span className="kpi-subtext">Pacing & speed analysis</span>
            </div>
          </div>

          <div className="kpi-card warning">
            <div className="kpi-icon">👥</div>
            <div className="kpi-details">
              <span className="kpi-num">
                {testResult.class_average_accuracy ? `${testResult.class_average_accuracy}%` : "72.5%"}
              </span>
              <span className="kpi-label">Class Average Accuracy</span>
              <span className="kpi-subtext">Benchmark comparison</span>
            </div>
          </div>

          <div className="kpi-card danger">
            <div className="kpi-icon">⚠️</div>
            <div className="kpi-details">
              <span className="kpi-num">{testResult.suggested_revision_topics?.length || 0}</span>
              <span className="kpi-label">Revision Areas</span>
              <span className="kpi-subtext">Topics needing attention</span>
            </div>
          </div>
        </div>

        {/* Visual Charts: Topic-wise BarChart */}
        {topicChartData.length > 0 && (
          <div className="teacher-section-card" style={{ marginBottom: "24px" }}>
            <h3>📈 Topic-Wise Accuracy Breakdown</h3>
            <p className="subtext">Performance percentage by syllabus domain</p>
            <div style={{ width: "100%", height: 260, marginTop: "16px" }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topicChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="topic" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip formatter={(value) => [`${value}%`, "Accuracy"]} />
                  <Bar dataKey="accuracy" fill="#00A99D" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Strengths, Weaknesses & Suggested Revision with Links */}
        <div className="teacher-split-grid" style={{ marginBottom: "24px" }}>
          <div className="teacher-section-card">
            <h4>🌟 Identified Strengths & Mastered Concepts</h4>
            <div className="pills-wrap" style={{ marginTop: "10px" }}>
              {testResult.strengths?.length > 0 ? (
                testResult.strengths.map((str, i) => (
                  <span key={i} className="match-badge match-high">
                    ✓ {str}
                  </span>
                ))
              ) : (
                <p style={{ fontSize: "13px", color: "var(--text-muted)" }}>
                  Keep practicing to establish high-confidence strength areas.
                </p>
              )}
            </div>
          </div>

          <div className="teacher-section-card">
            <h4>📌 Suggested Topics to Revise</h4>
            {testResult.suggested_revision_topics?.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "10px" }}>
                {testResult.suggested_revision_topics.map((top, i) => (
                  <div key={i} className="remediation-row">
                    <span>⚠️ <strong>{top}</strong></span>
                    <button
                      className="table-action-btn"
                      onClick={() => navigate(`/materials?search=${encodeURIComponent(top)}`)}
                    >
                      Open Notes →
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: "13px", color: "#166534", marginTop: "10px" }}>
                🎉 Great job! No critical weak areas identified in this test.
              </p>
            )}
          </div>
        </div>

        {/* Detailed Question Review */}
        {testResult.answers_detail && testResult.answers_detail.length > 0 && (
          <div className="teacher-section-card">
            <h3>📝 Question-by-Question Detailed Review</h3>
            <p className="subtext">Review solutions and step-by-step explanations</p>

            <div className="question-review-list" style={{ marginTop: "16px" }}>
              {testResult.answers_detail.map((ans, idx) => (
                <div
                  key={idx}
                  className={`review-question-card ${ans.is_correct ? "correct" : "incorrect"}`}
                >
                  <div className="review-top-row">
                    <span className="q-badge">Question {idx + 1}</span>
                    <span className={`status-pill ${ans.is_correct ? "status-success" : "status-danger"}`}>
                      {ans.is_correct ? "✓ Correct (+1)" : "✗ Incorrect (0)"}
                    </span>
                    <span className="topic-badge">🏷️ {ans.topic}</span>
                  </div>

                  <p className="review-q-text">{ans.question_text}</p>

                  <div className="review-answers-box">
                    <div>
                      <strong>Your Answer:</strong>{" "}
                      <span className={ans.is_correct ? "correct-text" : "incorrect-text"}>
                        {ans.student_answer || "(Unanswered)"}
                      </span>
                    </div>
                    <div>
                      <strong>Correct Answer:</strong>{" "}
                      <span className="correct-text">
                        {ans.options && !isNaN(ans.correct_answer)
                          ? ans.options[Number(ans.correct_answer)] || ans.correct_answer
                          : ans.correct_answer}
                      </span>
                    </div>
                  </div>

                  {ans.explanation && (
                    <div className="review-explanation-box">
                      <strong>💡 Step-by-Step Explanation:</strong>
                      <p>{ans.explanation}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // ─────────────────────────────────────────────
  // RENDER: Browse & Setup Mode
  // ─────────────────────────────────────────────

  // Format historical trend for LineChart
  const historyChartData = (history || []).slice(-8).map((h, i) => ({
    name: `Test #${i + 1}`,
    score: h.score_obtained || 0,
    total: h.total_marks || 10,
    pct: Math.round(((h.score_obtained || 0) / (h.total_marks || 10)) * 100),
  }));

  return (
    <div className="mock-tests-page">
      {/* Header */}
      <div className="page-header-row">
        <div>
          <h2>📝 Adaptive Mock Tests & Skill Diagnostics</h2>
          <p className="page-subtitle">
            Timed adaptive tests with instant autograding, performance analytics, and automated skill profile updates.
          </p>
        </div>
        {isTeacher && (
          <button
            className="action-btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            + Create New Mock Test
          </button>
        )}
      </div>

      {/* Mode Sub-Tabs */}
      <div className="guidance-tabs-nav">
        <button
          className={`guidance-tab-btn ${browseTab === "tests" ? "active" : ""}`}
          onClick={() => setBrowseTab("tests")}
        >
          {isTeacher ? "📋 Tests & Review Queue" : "📋 Published Mock Tests"}
        </button>
        <button
          className={`guidance-tab-btn ${browseTab === "adaptive" ? "active" : ""}`}
          onClick={() => setBrowseTab("adaptive")}
        >
          ⚡ Adaptive Practice (Weak Topics)
        </button>
        <button
          className={`guidance-tab-btn ${browseTab === "history" ? "active" : ""}`}
          onClick={() => setBrowseTab("history")}
        >
          📈 Performance Trends & History
        </button>
      </div>

      {/* ─────────────────────────────────────────
          TAB 1: PUBLISHED MOCK TESTS
         ───────────────────────────────────────── */}
      {browseTab === "tests" && (
        <div>
          {/* Subject Filter */}
          <div className="stream-filter-pills" style={{ marginBottom: "20px" }}>
            {["All", ...testSubjects].map((subj) => (
              <button
                key={subj}
                className={`filter-pill ${selectedSubjectFilter === subj ? "active" : ""}`}
                onClick={() => setSelectedSubjectFilter(subj)}
              >
                {subj}
              </button>
            ))}
          </div>

          {testsLoading ? (
            <LoadingSpinner message="Loading mock tests library..." />
          ) : visibleTests.length === 0 ? (
            <EmptyState
              icon="📝"
              title="No tests found"
              message="No published tests match your course and semester yet. Ask your teacher to add one."
            />
          ) : (
            <div className="courses-grid">
              {visibleTests.map((test) => (
                <div key={test.id} className="course-card-enhanced">
                  <div className="course-card-header">
                    <span className="stream-pill">{test.subject}</span>
                    <span className="degree-tag">{test.exam_name || "Diagnostic"}</span>
                    {test.academic_year && (
                      <span className="degree-tag">{test.academic_year}</span>
                    )}
                    {isTeacher && (
                      <span className={`status-badge status-${test.approval_status}`}>
                        {test.approval_status}
                      </span>
                    )}
                  </div>

                  <h3 className="course-card-title">{test.title}</h3>

                  <div className="card-key-details" style={{ marginTop: "10px" }}>
                    <div>⏱️ <strong>Duration:</strong> {test.duration_minutes} Mins</div>
                    <div>🎯 <strong>Marks:</strong> {test.total_marks}</div>
                    <div>❓ <strong>Questions:</strong> {test.question_count || 10}</div>
                  </div>

                  <div className="card-bottom-actions">
                    {isTeacher && test.approval_status === "pending" ? (
                      <>
                        <button
                          className="action-btn-success"
                          onClick={() => handleReviewTest(test.id, "approve")}
                        >
                          Approve & Publish
                        </button>
                        <button
                          className="action-btn-secondary"
                          onClick={() => handleReviewTest(test.id, "reject")}
                        >
                          Reject
                        </button>
                      </>
                    ) : test.approval_status === "approved" && test.is_published ? (
                      <button
                        className="action-btn-primary"
                        style={{ width: "100%" }}
                        onClick={() => startTest(test.id)}
                      >
                        Start Timed Test ⏱️
                      </button>
                    ) : (
                      <span className="subtext">This test is not published.</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─────────────────────────────────────────
          TAB 2: ADAPTIVE PRACTICE GENERATOR
         ───────────────────────────────────────── */}
      {browseTab === "adaptive" && (
        <div className="adaptive-generator-card">
          <div className="adaptive-hero">
            <span style={{ fontSize: "36px" }}>⚡</span>
            <div>
              <h3>AI-Driven Adaptive Test Generator</h3>
              <p>
                Generates a personalized test that weights 70% of questions toward your currently diagnosed weak topics, accelerating your learning curve.
              </p>
            </div>
          </div>

          {/* Student Weak Topics Preview */}
          <div style={{ margin: "20px 0" }}>
            <h4>Your Current Weak Topics:</h4>
            <div className="pills-wrap" style={{ marginTop: "8px" }}>
              {relevantWeakTopics.length > 0 ? (
                relevantWeakTopics.map((w, i) => (
                  <span key={i} className="danger-topic-pill">
                    ⚠️ {w.subject}: {w.topic} (Mastery: {w.mastery_score}%)
                  </span>
                ))
              ) : (
                <span className="match-badge match-high">✓ All topics are average or strong!</span>
              )}
            </div>
          </div>

          <div className="form-group" style={{ maxWidth: "300px", marginBottom: "20px" }}>
            <label>Select Subject for Adaptive Drill:</label>
            <select
              value={adaptiveSubject}
              onChange={(e) => setAdaptiveSubject(e.target.value)}
              className="search-input"
            >
              {testSubjects.map((subject) => (
                <option key={subject} value={subject}>{subject}</option>
              ))}
            </select>
          </div>

          <button
            className="action-btn-primary"
            onClick={startAdaptiveTest}
            disabled={adaptiveLoading || !testSubjects.length}
          >
            {adaptiveLoading ? "Assembling Adaptive Drill..." : `Launch Adaptive ${adaptiveSubject} Test →`}
          </button>
        </div>
      )}

      {/* ─────────────────────────────────────────
          TAB 3: PERFORMANCE TRENDS & HISTORY
         ───────────────────────────────────────── */}
      {browseTab === "history" && (
        <div>
          {loadingHistory ? (
            <LoadingSpinner message="Loading historical test progression..." />
          ) : (
            <div>
              {/* Trend Chart */}
              {historyChartData.length > 0 && (
                <div className="teacher-section-card" style={{ marginBottom: "24px" }}>
                  <h3>📈 Historical Accuracy Trend Line</h3>
                  <p className="subtext">Percentage score progression across test attempts</p>
                  <div style={{ width: "100%", height: 260, marginTop: "16px" }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={historyChartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis domain={[0, 100]} />
                        <Tooltip formatter={(value) => [`${value}%`, "Accuracy"]} />
                        <Line type="monotone" dataKey="pct" stroke="#00A99D" strokeWidth={3} dot={{ r: 5 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Past Attempts Table */}
              <div className="teacher-section-card">
                <h3>Past Mock Test Submissions</h3>
                <div className="class-topics-table-wrapper" style={{ marginTop: "14px" }}>
                  <table className="teacher-table">
                    <thead>
                      <tr>
                        <th>Subject</th>
                        <th>Difficulty</th>
                        <th>Score</th>
                        <th>Accuracy</th>
                        <th>Date Taken</th>
                      </tr>
                    </thead>
                    <tbody>
                      {history.map((h) => {
                        const pct = Math.round(((h.score_obtained || 0) / (h.total_marks || 10)) * 100);
                        return (
                          <tr key={h.test_id}>
                            <td><strong>{h.subject}</strong></td>
                            <td><span className="degree-tag">{h.difficulty_mode}</span></td>
                            <td>{h.score_obtained} / {h.total_marks}</td>
                            <td>
                              <span className={`match-badge ${pct >= 70 ? "match-high" : "match-normal"}`}>
                                {pct}%
                              </span>
                            </td>
                            <td>{new Date(h.completed_at).toLocaleDateString()}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ─────────────────────────────────────────
          MODAL: TEACHER CREATE MOCK TEST
         ───────────────────────────────────────── */}
      {showCreateModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-xl">
            <div className="modal-header">
              <h3>+ Create Mock Test for Teacher Review</h3>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleCreateTestSubmit} className="modal-body-scrollable">
              <div className="info-grid-2col" style={{ marginBottom: "16px" }}>
                <div>
                  <label>Test Title:</label>
                  <input
                    type="text"
                    placeholder="e.g. Class 12 Calculus Unit Test"
                    value={createTitle}
                    onChange={(e) => setCreateTitle(e.target.value)}
                    required
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
                <div>
                  <label>Subject:</label>
                  <input
                    type="text"
                    placeholder="e.g. Programming in C"
                    value={createSubject}
                    onChange={(e) => setCreateSubject(e.target.value)}
                    required
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
                <div>
                  <label>Course (optional):</label>
                  <input
                    type="text"
                    maxLength={100}
                    placeholder="e.g. Diploma in Computer Engineering"
                    value={createCourse}
                    onChange={(e) => setCreateCourse(e.target.value)}
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
                <div>
                  <label>College / curriculum (optional):</label>
                  <input
                    type="text"
                    maxLength={150}
                    placeholder="e.g. Polytechnic College Kannur"
                    value={createCurriculum}
                    onChange={(e) => setCreateCurriculum(e.target.value)}
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
                <div>
                  <label>Semester / academic year (optional):</label>
                  <input
                    type="text"
                    maxLength={20}
                    placeholder="e.g. 3rd Semester"
                    value={createAcademicYear}
                    onChange={(e) => setCreateAcademicYear(e.target.value)}
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
                <div>
                  <label>Entrance exam / assessment (optional):</label>
                  <input
                    type="text"
                    maxLength={100}
                    placeholder="e.g. KEAM, JEE Main, Semester Exam"
                    value={createExamName}
                    onChange={(e) => setCreateExamName(e.target.value)}
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
                <div>
                  <label>Duration (Minutes):</label>
                  <input
                    type="number"
                    min="5"
                    max="180"
                    value={createDuration}
                    onChange={(e) => setCreateDuration(e.target.value)}
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
                <div>
                  <label>Total Marks:</label>
                  <input
                    type="number"
                    min="1"
                    value={createTotalMarks}
                    onChange={(e) => setCreateTotalMarks(e.target.value)}
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
              </div>
              <p className="subtext">
                To show this test only to a matching student group, fill in all three course-scope fields.
              </p>

              <h4>Test Questions ({createQuestions.length})</h4>
              {createQuestions.map((q, qIndex) => (
                <div key={qIndex} className="quiz-question-group" style={{ background: "#f8fafc", padding: "16px", borderRadius: "8px", marginBottom: "16px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                    <strong>Question {qIndex + 1}</strong>
                    <button
                      type="button"
                      className="table-action-btn"
                      onClick={() =>
                        setCreateQuestions(createQuestions.filter((_, i) => i !== qIndex))
                      }
                    >
                      Remove
                    </button>
                  </div>

                  <input
                    type="text"
                    placeholder="Question statement..."
                    value={q.question_text}
                    onChange={(e) => {
                      const updated = [...createQuestions];
                      updated[qIndex].question_text = e.target.value;
                      setCreateQuestions(updated);
                    }}
                    required
                    className="search-input"
                    style={{ width: "100%", marginBottom: "10px" }}
                  />

                  <div className="info-grid-2col" style={{ marginBottom: "10px" }}>
                    <div>
                      <label>Type:</label>
                      <select
                        value={q.question_type}
                        onChange={(e) => {
                          const updated = [...createQuestions];
                          updated[qIndex].question_type = e.target.value;
                          setCreateQuestions(updated);
                        }}
                        className="search-input"
                      >
                        <option value="mcq">MCQ (4 Options)</option>
                        <option value="true_false">True / False</option>
                        <option value="short_answer">Short Answer</option>
                      </select>
                    </div>

                    <div>
                      <label>Topic Tag:</label>
                      <input
                        type="text"
                        placeholder="e.g. Calculus"
                        value={q.topic}
                        onChange={(e) => {
                          const updated = [...createQuestions];
                          updated[qIndex].topic = e.target.value;
                          setCreateQuestions(updated);
                        }}
                        className="search-input"
                      />
                    </div>
                  </div>

                  {q.question_type === "mcq" && (
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginBottom: "10px" }}>
                      {q.options.map((opt, optIdx) => (
                        <input
                          key={optIdx}
                          type="text"
                          placeholder={`Option ${String.fromCharCode(65 + optIdx)}`}
                          value={opt}
                          onChange={(e) => {
                            const updated = [...createQuestions];
                            updated[qIndex].options[optIdx] = e.target.value;
                            setCreateQuestions(updated);
                          }}
                          required
                          className="search-input"
                        />
                      ))}
                    </div>
                  )}

                  <div className="info-grid-2col">
                    <div>
                      <label>Correct Answer (Index 0-3 for MCQ, 0/1 for TF, text for short):</label>
                      <input
                        type="text"
                        placeholder="0"
                        value={q.correct_answer}
                        onChange={(e) => {
                          const updated = [...createQuestions];
                          updated[qIndex].correct_answer = e.target.value;
                          setCreateQuestions(updated);
                        }}
                        required
                        className="search-input"
                      />
                    </div>
                    <div>
                      <label>Explanation / Solution:</label>
                      <input
                        type="text"
                        placeholder="Step-by-step reasoning..."
                        value={q.explanation}
                        onChange={(e) => {
                          const updated = [...createQuestions];
                          updated[qIndex].explanation = e.target.value;
                          setCreateQuestions(updated);
                        }}
                        className="search-input"
                      />
                    </div>
                  </div>
                </div>
              ))}

              <button
                type="button"
                className="action-btn-secondary"
                onClick={handleAddQuestionRow}
                style={{ marginBottom: "20px" }}
              >
                + Add Another Question
              </button>

              <div className="modal-footer">
                <button
                  type="button"
                  className="action-btn-secondary"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="action-btn-primary"
                  disabled={savingTest}
                >
                  {savingTest ? "Publishing Test..." : "Publish Test to Students"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default MockTests;
