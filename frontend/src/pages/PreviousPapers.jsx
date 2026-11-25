import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import EmptyState from "../components/EmptyState";

function PreviousPapers({ user }) {
  const navigate = useNavigate();
  const isTeacher = ["teacher", "admin"].includes(user?.role);

  // Views: 'list' | 'study' | 'timed_exam' | 'exam_result'
  const [viewMode, setViewMode] = useState("list");

  // Filters
  const [selectedSubject, setSelectedSubject] = useState("All");
  const [selectedExam, setSelectedExam] = useState("All");
  const [selectedYear, setSelectedYear] = useState("All");
  const [selectedSource, setSelectedSource] = useState("All"); // 'All' | 'teacher' | 'ai'
  const [topicSearch, setTopicSearch] = useState("");

  // Papers Data
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Active Paper for Study or Timed Exam
  const [activePaper, setActivePaper] = useState(null);
  const [loadingPaper, setLoadingPaper] = useState(false);

  // Solved Solutions Viewer Modal
  const [solutionsModalPaper, setSolutionsModalPaper] = useState(null);
  const [solutionsData, setSolutionsData] = useState([]);
  const [loadingSolutions, setLoadingSolutions] = useState(false);

  // AI Paper Generation Modal
  const [showAiModal, setShowAiModal] = useState(false);
  const [aiSubject, setAiSubject] = useState("");
  const [aiGenerating, setAiGenerating] = useState(false);
  const [aiError, setAiError] = useState("");

  // Timed exam attempt state
  const [examAnswers, setExamAnswers] = useState({});
  const [examTimeLeft, setExamTimeLeft] = useState(0);
  const [submittingExam, setSubmittingExam] = useState(false);
  const [attemptResult, setAttemptResult] = useState(null);

  // Teacher Upload Modal
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadExamName, setUploadExamName] = useState("");
  const [uploadSubject, setUploadSubject] = useState("");
  const [uploadCourse, setUploadCourse] = useState("");
  const [uploadCurriculum, setUploadCurriculum] = useState("");
  const [uploadAcademicYear, setUploadAcademicYear] = useState("");
  const [uploadYear, setUploadYear] = useState(2024);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadTopicTags, setUploadTopicTags] = useState("");
  const [uploadPaperFile, setUploadPaperFile] = useState(null);
  const [uploadAnswerKeyFile, setUploadAnswerKeyFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  // PDF Preview Modal
  const [previewPaper, setPreviewPaper] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");

  const paperSubjects = [...new Set(papers.map((paper) => paper.subject).filter(Boolean))];
  const paperExams = [...new Set(papers.map((paper) => paper.exam_name).filter(Boolean))];
  const paperYears = [...new Set(papers.map((paper) => paper.year).filter(Boolean))]
    .sort((a, b) => b - a);
  const visiblePapers = papers.filter((paper) =>
    (selectedSubject === "All" || paper.subject === selectedSubject)
    && (selectedExam === "All" || paper.exam_name === selectedExam)
    && (selectedYear === "All" || String(paper.year) === selectedYear)
    && (selectedSource === "All" || (paper.source || "teacher").toLowerCase() === selectedSource.toLowerCase())
    && (!topicSearch.trim() || (paper.topic_tags || []).some((tag) =>
      tag.toLowerCase().includes(topicSearch.trim().toLowerCase())
    ))
  );

  useEffect(() => {
    return () => {
      if (previewUrl.startsWith("blob:")) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const fetchPapers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get("/api/v1/papers", { params: { skip: 0, limit: 100 } });
      setPapers(res.data.items || []);
    } catch (err) {
      console.error("Question papers request failed:", err);
      setError(err.response?.data?.detail || "Failed to load question papers library.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, []);

  const handleSubmitExam = useCallback(async () => {
    if (!activePaper || submittingExam) return;
    setSubmittingExam(true);
    try {
      const answersPayload = activePaper.questions.map((q) => ({
        question_id: q.id,
        selected_option: examAnswers[q.id] !== undefined ? examAnswers[q.id] : null,
      }));

      const timeSpent = (activePaper.time_limit_minutes || 60) * 60 - examTimeLeft;

      const res = await api.post(`/papers/${activePaper.id}/attempt`, {
        paper_id: activePaper.id,
        time_spent_seconds: Math.max(1, timeSpent),
        answers: answersPayload,
      });

      setAttemptResult(res.data);
      setViewMode("exam_result");
    } catch (err) {
      console.error(err);
      alert("Failed to submit exam attempt.");
    } finally {
      setSubmittingExam(false);
    }
  }, [activePaper, submittingExam, examAnswers, examTimeLeft]);

  // Exam Countdown Timer
  useEffect(() => {
    if (viewMode !== "timed_exam" || examTimeLeft <= 0) return;

    const timer = setInterval(() => {
      setExamTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          alert("⏰ Time is up! Submitting your examination answers.");
          handleSubmitExam();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [viewMode, examTimeLeft, handleSubmitExam]);

  const handleOpenStudyMode = async (paperId) => {
    setLoadingPaper(true);
    try {
      const res = await api.get(`/papers/${paperId}`);
      setActivePaper(res.data);
      setViewMode("study");
    } catch (err) {
      console.error(err);
      alert("Failed to load solved question paper.");
    } finally {
      setLoadingPaper(false);
    }
  };

  const handleStartTimedExam = async (paperId) => {
    setLoadingPaper(true);
    try {
      const res = await api.get(`/papers/${paperId}`);
      setActivePaper(res.data);
      setExamAnswers({});
      setExamTimeLeft((res.data.time_limit_minutes || 60) * 60);
      setViewMode("timed_exam");
    } catch (err) {
      console.error(err);
      alert("Failed to start timed paper attempt.");
    } finally {
      setLoadingPaper(false);
    }
  };

  const formatTimer = (secs) => {
    const mins = Math.floor(secs / 60);
    const rem = secs % 60;
    return `${mins.toString().padStart(2, "0")}:${rem.toString().padStart(2, "0")}`;
  };

  // Teacher: Upload Paper
  const handleUploadPaper = async (e) => {
    e.preventDefault();
    if (!uploadPaperFile) {
      setUploadError("Choose the question paper PDF to upload.");
      return;
    }
    setUploading(true);
    setUploadError("");
    try {
      const payload = new FormData();
      payload.append("exam_name", uploadExamName);
      payload.append("subject", uploadSubject);
      payload.append("year", String(uploadYear));
      payload.append("title", uploadTitle);
      payload.append("topic_tags", uploadTopicTags);
      payload.append("course", uploadCourse.trim());
      payload.append("curriculum", uploadCurriculum.trim());
      payload.append("academic_year", uploadAcademicYear.trim());
      payload.append("paper_file", uploadPaperFile);
      if (uploadAnswerKeyFile) payload.append("answer_key_file", uploadAnswerKeyFile);

      await api.post("/api/v1/papers/upload", payload, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setShowUploadModal(false);
      setUploadTitle("");
      setUploadTopicTags("");
      setUploadExamName("");
      setUploadSubject("");
      setUploadCourse("");
      setUploadCurriculum("");
      setUploadAcademicYear("");
      setUploadPaperFile(null);
      setUploadAnswerKeyFile(null);
      fetchPapers();
      alert("Paper uploaded and submitted for teacher approval.");
    } catch (err) {
      console.error("Upload paper error:", err);
      const detail = err.response?.data?.detail;
      setUploadError(typeof detail === "string" ? detail : "Failed to upload the paper PDF.");
    } finally {
      setUploading(false);
    }
  };

  const handleOpenPreview = async (paper) => {
    setPreviewPaper(paper);
    setPreviewUrl("");
    if (/^https?:\/\//i.test(paper.file_path || "")) {
      setPreviewUrl(paper.file_path);
      return;
    }
    try {
      const response = await api.get(`/api/v1/papers/${paper.id}/file`, {
        responseType: "blob",
      });
      setPreviewUrl(URL.createObjectURL(response.data));
    } catch (err) {
      console.error("Paper preview error:", err);
      setPreviewPaper(null);
      alert(err.response?.data?.detail || "Could not load this paper PDF.");
    }
  };

  const handleDownloadPaper = async (paper, kind = "paper") => {
    const storedPath = kind === "paper" ? paper.file_path : paper.answer_key_file;
    if (!storedPath) return;
    if (/^https?:\/\//i.test(storedPath)) {
      window.open(storedPath, "_blank", "noopener,noreferrer");
      return;
    }
    try {
      const response = await api.get(`/api/v1/papers/${paper.id}/file`, {
        params: { kind },
        responseType: "blob",
      });
      const url = URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${paper.title}${kind === "answer_key" ? "-answer-key" : ""}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Paper download error:", err);
      alert(err.response?.data?.detail || "Could not download this PDF.");
    }
  };

  // Teacher: Approve Paper
  const handleApprovePaper = async (paperId) => {
    try {
      await api.patch(`/api/v1/papers/${paperId}/approve`, { approval_status: "approved" });
      fetchPapers();
      alert("Paper approved and published.");
    } catch (err) {
      console.error("Approve paper error:", err);
      alert("Failed to approve paper.");
    }
  };

  // Open Solved Solutions Viewer
  const handleOpenSolutions = async (paper) => {
    setSolutionsModalPaper(paper);
    if (paper.solutions && Array.isArray(paper.solutions) && paper.solutions.length > 0) {
      setSolutionsData(paper.solutions);
      return;
    }
    setLoadingSolutions(true);
    try {
      const res = await api.get(`/api/v1/papers/${paper.id}/solutions`);
      setSolutionsData(res.data.solutions || []);
    } catch (err) {
      console.error("Failed to load paper solutions:", err);
      setSolutionsData([]);
    } finally {
      setLoadingSolutions(false);
    }
  };

  // Generate AI Question Paper
  const handleGenerateAIPaper = async (e) => {
    e.preventDefault();
    if (!aiSubject) {
      setAiError("Please select a subject for the AI paper.");
      return;
    }
    setAiGenerating(true);
    setAiError("");
    try {
      await api.post("/api/v1/papers/generate-ai", {
        subject: aiSubject,
        exam_name: "AI Adaptive Examination"
      });
      setShowAiModal(false);
      setAiSubject("");
      await fetchPapers();
      alert("✨ AI Solved Question Paper successfully generated and added to your library!");
    } catch (err) {
      console.error("AI Paper Generation error:", err);
      setAiError(err.response?.data?.detail || "Failed to generate AI Question Paper.");
    } finally {
      setAiGenerating(false);
    }
  };

  return (
    <div className="previous-papers-page">
      {/* ================= VIEW 1: PAPERS LIST ================= */}
      {viewMode === "list" && (
        <>
          <div className="page-header-row">
            <div>
              <h2>📄 Solved Previous-Year Question Papers</h2>
              <p className="page-subtitle">
                Official teacher-uploaded papers and AI-generated practice papers with verified answer keys & solutions for your course.
              </p>
            </div>
            <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
              <button
                className="action-btn-primary"
                style={{ background: "#4f46e5", display: "inline-flex", alignItems: "center", gap: "6px" }}
                onClick={() => {
                  setAiSubject(paperSubjects[0] || "Marketing Management");
                  setShowAiModal(true);
                }}
              >
                <span>🤖</span> Generate AI Question Paper
              </button>
              {isTeacher && (
                <button
                  className="action-btn-primary"
                  onClick={() => setShowUploadModal(true)}
                >
                  + Upload Question Paper
                </button>
              )}
            </div>
          </div>

          {/* Filters Bar */}
          <div className="papers-filters-bar">
            {/* Paper Source Filter Tabs: All | Teacher Uploaded | AI Generated */}
            <div style={{ display: "flex", gap: "8px", alignItems: "center", flexWrap: "wrap", marginBottom: "4px" }}>
              <span style={{ fontSize: "13px", fontWeight: "600", color: "#475569" }}>Source:</span>
              {[
                { id: "All", label: "All Papers" },
                { id: "teacher", label: "👨‍🏫 Teacher Uploaded (Official)" },
                { id: "ai", label: "🤖 AI Generated (Adaptive QP)" }
              ].map((src) => (
                <button
                  key={src.id}
                  className={`filter-pill ${selectedSource === src.id ? "active" : ""}`}
                  style={selectedSource === src.id && src.id === "ai" ? { background: "#4f46e5", color: "white" } : {}}
                  onClick={() => setSelectedSource(src.id)}
                >
                  {src.label}
                </button>
              ))}
            </div>

            {/* Subject Tabs */}
            <div className="stream-filter-pills">
              {["All", ...paperSubjects].map((subj) => (
                <button
                  key={subj}
                  className={`filter-pill ${selectedSubject === subj ? "active" : ""}`}
                  onClick={() => setSelectedSubject(subj)}
                >
                  {subj}
                </button>
              ))}
            </div>

            {/* Exam Filter Dropdown */}
            <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
              <select
                value={selectedExam}
                onChange={(e) => setSelectedExam(e.target.value)}
                className="search-input"
                style={{ padding: "6px 12px", fontSize: "13px" }}
              >
                <option value="All">All Exams</option>
                {paperExams.map((exam) => (
                  <option key={exam} value={exam}>{exam}</option>
                ))}
              </select>

              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(e.target.value)}
                className="search-input"
                style={{ padding: "6px 12px", fontSize: "13px" }}
              >
                <option value="All">All Years</option>
                {paperYears.map((year) => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>

              <input
                type="text"
                placeholder="🔍 Search topic..."
                value={topicSearch}
                onChange={(e) => setTopicSearch(e.target.value)}
                className="search-input"
                style={{ padding: "6px 12px", fontSize: "13px", width: "160px" }}
              />
            </div>
          </div>

          {loading ? (
            <LoadingSpinner message="Loading previous year question papers..." />
          ) : error ? (
            <ErrorMessage error={error} onRetry={fetchPapers} />
          ) : visiblePapers.length === 0 ? (
            <EmptyState
              icon="📄"
              title={papers.length === 0 ? "No course papers available yet" : "No papers match these filters"}
              message={papers.length === 0
                ? (isTeacher
                  ? "Upload an official paper and answer key, or generate an AI question paper for your course."
                  : "A teacher must upload and approve a question paper, or you can generate an AI practice paper above.")
                : "Try clearing the filters or topic search."}
              actionText="Reset Filters"
              onAction={() => {
                setSelectedSubject("All");
                setSelectedExam("All");
                setSelectedYear("All");
                setSelectedSource("All");
                setTopicSearch("");
              }}
            />
          ) : (
            <div className="courses-grid">
              {visiblePapers.map((paper) => (
                <div key={paper.id} className="course-card-enhanced">
                  <div className="course-card-header">
                    <span className="exam-code-badge">{paper.exam_name || "Official"}</span>
                    <span className="degree-tag">{paper.year}</span>
                    <span className="stream-pill">{paper.subject}</span>
                    {paper.academic_year && (
                      <span className="degree-tag">{paper.academic_year}</span>
                    )}
                    {paper.source === "ai" ? (
                      <span className="status-badge" style={{ background: "#ede9fe", color: "#6d28d9", fontWeight: 700, marginLeft: "auto" }}>
                        🤖 AI Generated
                      </span>
                    ) : (
                      <span className="status-badge" style={{ background: "#ecfdf5", color: "#047857", fontWeight: 700, marginLeft: "auto" }}>
                        👨‍🏫 Teacher Uploaded
                      </span>
                    )}
                  </div>

                  <h3 className="course-card-title">{paper.title}</h3>

                  <div style={{ fontSize: "12px", color: "#64748b", margin: "4px 0" }}>
                    👤 <strong>Source:</strong> {paper.uploader_name || (paper.source === "ai" ? "AI Academic Engine" : "Faculty Department")}
                  </div>

                  {paper.topic_tags && (
                    <div className="card-exams-tags" style={{ marginTop: "8px" }}>
                      {paper.topic_tags.map((tag, i) => (
                        <span key={i} className="exam-tag-mini">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="card-key-details" style={{ marginTop: "12px" }}>
                    <div>📄 <strong>Question Paper:</strong> PDF Document</div>
                    <div>🔑 <strong>Answer Key & Solutions:</strong> {paper.has_solutions ? "✅ Complete Solved Solutions" : (paper.answer_key_file ? "Available" : "Not uploaded")}</div>
                  </div>

                  <div className="card-bottom-actions" style={{ flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
                    <button
                      className="action-btn-secondary btn-sm"
                      onClick={() => handleOpenPreview(paper)}
                    >
                      📄 View PDF
                    </button>
                    <button
                      className="action-btn-secondary btn-sm"
                      onClick={() => handleDownloadPaper(paper)}
                    >
                      ⬇️ Download QP
                    </button>
                    {paper.answer_key_file && (
                      <button
                        className="action-btn-secondary btn-sm"
                        onClick={() => handleDownloadPaper(paper, "answer_key")}
                      >
                        🔑 Answer Key
                      </button>
                    )}
                    <button
                      className="action-btn-primary btn-sm"
                      style={{ background: "#059669" }}
                      onClick={() => handleOpenSolutions(paper)}
                    >
                      💡 View Solved Answers
                    </button>
                  </div>

                  {isTeacher && paper.approval_status === "pending" && (
                    <div style={{ marginTop: "10px", borderTop: "1px dashed #cbd5e1", paddingTop: "8px" }}>
                      <span className="status-badge status-pending" style={{ marginRight: "8px" }}>
                        PENDING APPROVAL
                      </span>
                      <button
                        className="table-action-btn"
                        onClick={() => handleApprovePaper(paper.id)}
                      >
                        Approve Paper ✓
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ================= VIEW 2: TIMED EXAM MODE ================= */}
      {viewMode === "timed_exam" && activePaper && (
        <div className="running-test-container">
          <div className="test-running-header">
            <div>
              <h3>⏱️ Timed Paper Simulation: {activePaper.title}</h3>
              <span className="stream-pill">{activePaper.subject}</span>
              <span className="degree-tag" style={{ marginLeft: "8px" }}>Year {activePaper.year}</span>
            </div>

            <div className="timer-box">
              <span className={`timer-display ${examTimeLeft < 300 ? "timer-danger" : ""}`}>
                ⏳ {formatTimer(examTimeLeft)}
              </span>
              <button
                className="action-btn-primary"
                onClick={handleSubmitExam}
                disabled={submittingExam}
              >
                {submittingExam ? "Submitting..." : "Submit Examination 🚀"}
              </button>
            </div>
          </div>

          <div style={{ maxWidth: "800px", margin: "0 auto", padding: "20px 0" }}>
            {activePaper.questions && activePaper.questions.map((q, idx) => (
              <div
                key={q.id}
                className="quiz-question-group"
                style={{ background: "white", padding: "20px", borderRadius: "10px", marginBottom: "20px", border: "1px solid var(--border-color)" }}
              >
                <div className="review-top-row">
                  <span className="q-badge">Question {idx + 1}</span>
                  <span className="topic-badge">🏷️ {q.topic}</span>
                </div>

                <p className="question-text" style={{ fontSize: "16px", margin: "14px 0" }}>
                  {q.question_text}
                </p>

                <div className="mcq-options-grid">
                  {q.options && q.options.map((opt, optIdx) => {
                    const isSelected = examAnswers[q.id] === optIdx;
                    return (
                      <div
                        key={optIdx}
                        className={`mcq-option-row ${isSelected ? "selected" : ""}`}
                        onClick={() => setExamAnswers({ ...examAnswers, [q.id]: optIdx })}
                      >
                        <span className="option-letter">{String.fromCharCode(65 + optIdx)}</span>
                        <span className="option-text">{opt}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}

            <div style={{ textAlign: "center", marginTop: "20px" }}>
              <button
                className="action-btn-primary"
                style={{ padding: "12px 32px", fontSize: "16px" }}
                onClick={handleSubmitExam}
                disabled={submittingExam}
              >
                {submittingExam ? "Grading..." : "Submit Answers & View Detailed Solutions"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= VIEW 3: EXAM RESULTS & REMEDIATION ================= */}
      {viewMode === "exam_result" && attemptResult && (
        <div className="test-result-page">
          <div className="result-hero-banner">
            <div>
              <h2>📊 Previous Paper Performance Report</h2>
              <p>Step-by-step solutions revealed. Wrong answers are mapped directly to study materials.</p>
            </div>
            <button
              className="action-btn-primary"
              onClick={() => {
                setViewMode("list");
                fetchPapers();
              }}
            >
              ← Back to Papers Library
            </button>
          </div>

          <div className="kpi-grid">
            <div className="kpi-card success">
              <div className="kpi-icon">🎯</div>
              <div className="kpi-details">
                <span className="kpi-num">{attemptResult.percentage}%</span>
                <span className="kpi-label">Accuracy Score</span>
                <span className="kpi-subtext">{attemptResult.score} / {attemptResult.total_marks} Marks</span>
              </div>
            </div>

            <div className="kpi-card info">
              <div className="kpi-icon">⏱️</div>
              <div className="kpi-details">
                <span className="kpi-num">
                  {Math.floor(attemptResult.time_spent_seconds / 60)}m {attemptResult.time_spent_seconds % 60}s
                </span>
                <span className="kpi-label">Time Spent</span>
                <span className="kpi-subtext">Exam pace analysis</span>
              </div>
            </div>

            <div className="kpi-card danger">
              <div className="kpi-icon">⚠️</div>
              <div className="kpi-details">
                <span className="kpi-num">{attemptResult.remediation_materials?.length || 0}</span>
                <span className="kpi-label">Remediation Topics</span>
                <span className="kpi-subtext">Linked study materials</span>
              </div>
            </div>
          </div>

          {/* Remediation Study Materials Box */}
          {attemptResult.remediation_materials && attemptResult.remediation_materials.length > 0 && (
            <div className="teacher-section-card" style={{ marginBottom: "24px" }}>
              <h3>📚 Targeted Remediation Study Materials</h3>
              <p className="subtext">
                Directly study the notes and theory for the questions you got wrong on this paper.
              </p>

              <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "14px" }}>
                {attemptResult.remediation_materials.map((item, idx) => (
                  <div key={idx} className="remediation-row">
                    <div>
                      <span className="danger-topic-pill" style={{ marginRight: "8px" }}>
                        ⚠️ Q{item.question_number}: {item.topic}
                      </span>
                      <strong>{item.material_title}</strong>
                    </div>
                    <button
                      className="table-action-btn"
                      onClick={() => navigate(`/materials?search=${encodeURIComponent(item.topic)}`)}
                    >
                      Study Notes →
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Step-by-Step Question Review */}
          <div className="teacher-section-card">
            <h3>📝 Step-by-Step Solved Question Review</h3>
            <div className="question-review-list" style={{ marginTop: "16px" }}>
              {attemptResult.question_breakdown && attemptResult.question_breakdown.map((q, idx) => (
                <div
                  key={idx}
                  className={`review-question-card ${q.is_correct ? "correct" : "incorrect"}`}
                >
                  <div className="review-top-row">
                    <span className="q-badge">Question {q.question_number}</span>
                    <span className={`status-pill ${q.is_correct ? "status-success" : "status-danger"}`}>
                      {q.is_correct ? "✓ Correct" : "✗ Incorrect"}
                    </span>
                    <span className="topic-badge">🏷️ {q.topic}</span>
                  </div>

                  <p className="review-q-text">{q.question_text}</p>

                  <div className="review-answers-box">
                    <div>
                      <strong>Your Answer:</strong>{" "}
                      <span className={q.is_correct ? "correct-text" : "incorrect-text"}>
                        {q.options && q.selected_option !== null && q.selected_option !== undefined
                          ? q.options[q.selected_option]
                          : "(Unanswered)"}
                      </span>
                    </div>
                    <div>
                      <strong>Correct Solved Answer:</strong>{" "}
                      <span className="correct-text">
                        {q.options ? q.options[q.correct_option] : q.correct_option}
                      </span>
                    </div>
                  </div>

                  {q.step_by_step_solution && (
                    <div className="review-explanation-box">
                      <strong>💡 Step-by-Step Official Solution:</strong>
                      <p>{q.step_by_step_solution}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ================= MODAL: TEACHER UPLOAD QUESTION PAPER ================= */}
      {showUploadModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-md">
            <div className="modal-header">
              <h3>+ Upload & Tag Question Paper</h3>
              <button className="modal-close" onClick={() => setShowUploadModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleUploadPaper} className="modal-body">
              <div className="info-grid-2col" style={{ marginBottom: "12px" }}>
                <div>
                  <label>Exam Name:</label>
                  <input
                    type="text"
                    maxLength={100}
                    placeholder="e.g. SITTTR Diploma Semester Exam"
                    value={uploadExamName}
                    onChange={(e) => setUploadExamName(e.target.value)}
                    required
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>

                <div>
                  <label>Subject:</label>
                  <input
                    type="text"
                    maxLength={100}
                    placeholder="e.g. Programming in C"
                    value={uploadSubject}
                    onChange={(e) => setUploadSubject(e.target.value)}
                    required
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
              </div>

              <div className="info-grid-2col" style={{ marginBottom: "12px" }}>
                <div>
                  <label>Year:</label>
                  <input
                    type="number"
                    min="2000"
                    max="2030"
                    value={uploadYear}
                    onChange={(e) => setUploadYear(e.target.value)}
                    required
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>

                <div>
                  <label>Paper Title:</label>
                  <input
                    type="text"
                    placeholder="e.g. JEE Main 2024 Shift 1 Mathematics"
                    value={uploadTitle}
                    onChange={(e) => setUploadTitle(e.target.value)}
                    required
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
              </div>

              <div className="info-grid-2col" style={{ marginBottom: "8px" }}>
                <div>
                  <label>Course (for student matching):</label>
                  <input
                    type="text"
                    maxLength={100}
                    placeholder="e.g. Diploma in Computer Engineering"
                    value={uploadCourse}
                    onChange={(e) => setUploadCourse(e.target.value)}
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
                <div>
                  <label>College / curriculum:</label>
                  <input
                    type="text"
                    maxLength={150}
                    placeholder="e.g. Polytechnic College Kannur"
                    value={uploadCurriculum}
                    onChange={(e) => setUploadCurriculum(e.target.value)}
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
                <div>
                  <label>Semester / academic year:</label>
                  <input
                    type="text"
                    maxLength={20}
                    placeholder="e.g. 3rd Semester"
                    value={uploadAcademicYear}
                    onChange={(e) => setUploadAcademicYear(e.target.value)}
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
              </div>
              <p className="subtext">
                Fill in all three course fields so only matching students can see this paper and its answer key.
              </p>

              <div className="form-group" style={{ marginBottom: "12px" }}>
                <label>Topic Tags (comma-separated):</label>
                <input
                  type="text"
                  placeholder="e.g. Calculus, Algebra, Matrices, Coordinate Geometry"
                  value={uploadTopicTags}
                  onChange={(e) => setUploadTopicTags(e.target.value)}
                  className="search-input"
                  style={{ width: "100%", marginTop: "4px" }}
                />
              </div>

              <div className="form-group" style={{ marginBottom: "12px" }}>
                <label>Question Paper PDF (max 20 MB):</label>
                <input
                  type="file"
                  accept="application/pdf,.pdf"
                  onChange={(e) => setUploadPaperFile(e.target.files?.[0] || null)}
                  required
                />
              </div>

              <div className="form-group" style={{ marginBottom: "16px" }}>
                <label>Answer Key / Solution PDF (Optional, max 20 MB):</label>
                <input
                  type="file"
                  accept="application/pdf,.pdf"
                  onChange={(e) => setUploadAnswerKeyFile(e.target.files?.[0] || null)}
                />
              </div>
              {uploadError && <p className="auth-error-msg" role="alert">{uploadError}</p>}

              <div className="modal-footer">
                <button
                  type="button"
                  className="action-btn-secondary"
                  onClick={() => setShowUploadModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="action-btn-primary"
                  disabled={uploading}
                >
                  {uploading ? "Uploading..." : "Save to Library"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ================= MODAL: PDF PREVIEW ================= */}
      {previewPaper && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-md">
            <div className="modal-header">
              <h3>📄 {previewPaper.title}</h3>
              <button className="modal-close" onClick={() => {
                setPreviewPaper(null);
                setPreviewUrl("");
              }}>
                &times;
              </button>
            </div>
            <div className="modal-body" style={{ textAlign: "center", padding: "30px 20px" }}>
              <h4>{previewPaper.exam_name} {previewPaper.year} — {previewPaper.subject}</h4>
              {previewUrl ? (
                <iframe
                  title={`${previewPaper.title} PDF preview`}
                  src={previewUrl}
                  style={{ width: "100%", height: "60vh", border: "1px solid var(--border-color)" }}
                />
              ) : (
                <p>Loading PDF preview...</p>
              )}

              {previewPaper.topic_tags && (
                <div className="pills-wrap" style={{ justifyContent: "center", margin: "16px 0" }}>
                  {previewPaper.topic_tags.map((t, i) => (
                    <span key={i} className="exam-tag-mini">
                      {t}
                    </span>
                  ))}
                </div>
              )}

              <div style={{ display: "flex", gap: "12px", justifyContent: "center", marginTop: "20px" }}>
                <button
                  className="action-btn-primary"
                  onClick={() => handleDownloadPaper(previewPaper)}
                >
                  ⬇️ Download PDF Paper
                </button>
                {previewPaper.answer_key_file && (
                  <button
                    className="action-btn-secondary"
                    onClick={() => handleDownloadPaper(previewPaper, "answer_key")}
                  >
                    🔑 Download Answer Key
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ================= MODAL: SOLVED ANSWERS & STEP-BY-STEP SOLUTIONS ================= */}
      {solutionsModalPaper && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-lg" style={{ maxWidth: "860px", maxHeight: "90vh", display: "flex", flexDirection: "column" }}>
            <div className="modal-header">
              <div>
                <h3 style={{ margin: 0, display: "flex", alignItems: "center", gap: "8px" }}>
                  💡 Solved Questions & Answer Key
                </h3>
                <p style={{ margin: "4px 0 0 0", fontSize: "13px", color: "#64748b" }}>
                  {solutionsModalPaper.title}
                </p>
              </div>
              <button className="modal-close" onClick={() => setSolutionsModalPaper(null)}>
                &times;
              </button>
            </div>

            <div style={{ padding: "12px 24px", background: "#f8fafc", borderBottom: "1px solid #e2e8f0", display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
              <span className="exam-code-badge">{solutionsModalPaper.exam_name}</span>
              <span className="stream-pill">{solutionsModalPaper.subject}</span>
              <span className="degree-tag">Year {solutionsModalPaper.year}</span>
              {solutionsModalPaper.source === "ai" ? (
                <span className="status-badge" style={{ background: "#ede9fe", color: "#6d28d9", fontWeight: 700 }}>
                  🤖 AI Generated Practice Paper
                </span>
              ) : (
                <span className="status-badge" style={{ background: "#ecfdf5", color: "#047857", fontWeight: 700 }}>
                  👨‍🏫 Teacher Uploaded & Approved
                </span>
              )}
            </div>

            <div className="modal-body" style={{ overflowY: "auto", padding: "20px 24px" }}>
              {loadingSolutions ? (
                <LoadingSpinner message="Loading solved questions and answer key..." />
              ) : solutionsData && solutionsData.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                  {solutionsData.map((q, qIdx) => (
                    <div
                      key={qIdx}
                      style={{
                        background: "white",
                        border: "1px solid #e2e8f0",
                        borderRadius: "10px",
                        padding: "18px",
                        boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                        <span style={{ fontWeight: "700", color: "#1e293b", fontSize: "14px" }}>
                          Question {q.question_number || (qIdx + 1)}
                        </span>
                        {q.topic && (
                          <span className="topic-badge" style={{ fontSize: "11px" }}>
                            🏷️ {q.topic}
                          </span>
                        )}
                      </div>

                      <p style={{ fontSize: "15px", fontWeight: "600", color: "#0f172a", marginBottom: "14px", lineHeight: "1.4" }}>
                        {q.question_text}
                      </p>

                      {q.options && Array.isArray(q.options) && (
                        <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginBottom: "14px" }}>
                          {q.options.map((opt, optIdx) => {
                            const isCorrect = optIdx === q.correct_option;
                            return (
                              <div
                                key={optIdx}
                                style={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: "10px",
                                  padding: "9px 14px",
                                  borderRadius: "8px",
                                  background: isCorrect ? "#ecfdf5" : "#f8fafc",
                                  border: isCorrect ? "2px solid #10b981" : "1px solid #e2e8f0",
                                  color: isCorrect ? "#065f46" : "#334155",
                                  fontWeight: isCorrect ? "600" : "normal"
                                }}
                              >
                                <span
                                  style={{
                                    display: "inline-flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    width: "24px",
                                    height: "24px",
                                    borderRadius: "50%",
                                    background: isCorrect ? "#10b981" : "#e2e8f0",
                                    color: isCorrect ? "white" : "#475569",
                                    fontSize: "12px",
                                    fontWeight: "bold"
                                  }}
                                >
                                  {String.fromCharCode(65 + optIdx)}
                                </span>
                                <span style={{ flex: 1, fontSize: "14px" }}>{opt}</span>
                                {isCorrect && (
                                  <span style={{ fontSize: "12px", color: "#059669", fontWeight: "bold" }}>
                                    ✓ Correct Answer
                                  </span>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      )}

                      {q.step_by_step_solution && (
                        <div
                          style={{
                            background: "#f0fdf4",
                            border: "1px solid #bbf7d0",
                            borderRadius: "8px",
                            padding: "12px 16px",
                            marginTop: "10px"
                          }}
                        >
                          <strong style={{ color: "#166534", fontSize: "13px", display: "flex", alignItems: "center", gap: "4px" }}>
                            💡 Step-by-Step Conceptual Solution:
                          </strong>
                          <p style={{ margin: "6px 0 0 0", color: "#1e293b", fontSize: "13.5px", lineHeight: "1.5" }}>
                            {q.step_by_step_solution}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ textAlign: "center", padding: "40px 20px" }}>
                  <p style={{ fontSize: "16px", color: "#64748b" }}>
                    The complete official answer key is available as a downloadable PDF document.
                  </p>
                  <button
                    className="action-btn-primary"
                    style={{ marginTop: "12px" }}
                    onClick={() => handleDownloadPaper(solutionsModalPaper, "answer_key")}
                  >
                    🔑 Download Official Answer Key PDF
                  </button>
                </div>
              )}
            </div>

            <div className="modal-footer" style={{ borderTop: "1px solid #e2e8f0", padding: "14px 24px", display: "flex", justifyContent: "space-between" }}>
              <div style={{ display: "flex", gap: "10px" }}>
                <button
                  className="action-btn-secondary btn-sm"
                  onClick={() => handleDownloadPaper(solutionsModalPaper)}
                >
                  ⬇️ Download QP PDF
                </button>
                {solutionsModalPaper.answer_key_file && (
                  <button
                    className="action-btn-secondary btn-sm"
                    onClick={() => handleDownloadPaper(solutionsModalPaper, "answer_key")}
                  >
                    🔑 Download Answer Key PDF
                  </button>
                )}
              </div>
              <button
                type="button"
                className="action-btn-primary btn-sm"
                onClick={() => setSolutionsModalPaper(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= MODAL: GENERATE AI QUESTION PAPER ================= */}
      {showAiModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-md">
            <div className="modal-header">
              <h3 style={{ margin: 0, display: "flex", alignItems: "center", gap: "8px" }}>
                🤖 Generate AI Question Paper with Solutions
              </h3>
              <button className="modal-close" onClick={() => setShowAiModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleGenerateAIPaper} className="modal-body">
              <p style={{ fontSize: "13.5px", color: "#475569", marginBottom: "16px" }}>
                FLINT AI will generate a tailored examination paper for your course with syllabus questions, official answer keys, step-by-step solutions, and downloadable PDF documents.
              </p>

              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label style={{ fontWeight: 600, fontSize: "13px" }}>Select Course Subject:</label>
                <select
                  className="search-input"
                  style={{ width: "100%", marginTop: "6px", padding: "8px 12px" }}
                  value={aiSubject}
                  onChange={(e) => setAiSubject(e.target.value)}
                  required
                >
                  <option value="">-- Choose Subject --</option>
                  <option value="Marketing Management">Marketing Management</option>
                  <option value="Financial Management">Financial Management</option>
                  <option value="Human Resource Management & OB">Human Resource Management & OB</option>
                  {paperSubjects
                    .filter((s) => !["Marketing Management", "Financial Management", "Human Resource Management & OB"].includes(s))
                    .map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                </select>
              </div>

              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label style={{ fontWeight: 600, fontSize: "13px" }}>Examination Pattern:</label>
                <input
                  type="text"
                  readOnly
                  value="BBA Year 2 • Comprehensive Diagnostic & Analytical Pattern"
                  className="search-input"
                  style={{ width: "100%", marginTop: "6px", background: "#f8fafc", color: "#64748b" }}
                />
              </div>

              {aiError && <p className="auth-error-msg" role="alert">{aiError}</p>}

              <div className="modal-footer" style={{ marginTop: "20px" }}>
                <button
                  type="button"
                  className="action-btn-secondary"
                  onClick={() => setShowAiModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="action-btn-primary"
                  style={{ background: "#4f46e5" }}
                  disabled={aiGenerating}
                >
                  {aiGenerating ? "Generating Paper & PDFs..." : "✨ Generate Solved Paper"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default PreviousPapers;
