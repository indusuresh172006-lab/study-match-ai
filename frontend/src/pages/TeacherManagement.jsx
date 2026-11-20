import { useState, useEffect, useCallback } from "react";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";

// Turns FastAPI error payloads (string or validation list) into readable text
function errorText(err, fallback) {
  const detail = err?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length) {
    return detail.map((d) => d.msg || "Invalid input").join("; ");
  }
  return fallback;
}

const EMPTY_SUBJECT = {
  name: "",
  code: "",
  description: "",
  course: "",
  curriculum: "",
  academic_year: "",
};
const EMPTY_TOPIC = { name: "", order_index: 0, description: "" };
const EMPTY_QUESTION = {
  question_text: "",
  options: ["", "", "", ""],
  correct_answer: 0,
  explanation: "",
  difficulty: "medium",
};

function TeacherManagement() {
  const [tab, setTab] = useState("subjects");
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null); // { type: "success" | "error", text }

  const [subjectId, setSubjectId] = useState(null);
  const [topicId, setTopicId] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [questionsLoading, setQuestionsLoading] = useState(false);

  // Modal state: null = closed, otherwise { id?: number, form: {...} }
  const [subjectModal, setSubjectModal] = useState(null);
  const [topicModal, setTopicModal] = useState(null);
  const [questionModal, setQuestionModal] = useState(null);
  const [saving, setSaving] = useState(false);

  const showNotice = (type, text) => {
    setNotice({ type, text });
    setTimeout(() => setNotice(null), 4000);
  };

  const fetchSubjects = useCallback(async () => {
    try {
      const res = await api.get("/api/v1/subjects");
      setSubjects(res.data || []);
      setError(null);
    } catch (err) {
      setError(errorText(err, "Could not load subjects."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSubjects();
  }, [fetchSubjects]);

  const currentSubject = subjects.find((s) => s.id === subjectId) || null;
  const topics = currentSubject?.topics || [];
  const currentTopic = topics.find((t) => t.id === topicId) || null;

  // Keep the selected subject/topic valid after data loads or changes
  useEffect(() => {
    if (subjects.length === 0) {
      setSubjectId(null);
      return;
    }
    if (!subjects.some((s) => s.id === subjectId)) {
      setSubjectId(subjects[0].id);
    }
  }, [subjects, subjectId]);

  useEffect(() => {
    if (topics.length === 0) {
      setTopicId(null);
      return;
    }
    if (!topics.some((t) => t.id === topicId)) {
      setTopicId(topics[0].id);
    }
  }, [topics, topicId]);

  const fetchQuestions = useCallback(async () => {
    if (!topicId) {
      setQuestions([]);
      return;
    }
    setQuestionsLoading(true);
    try {
      const res = await api.get("/api/v1/quiz/questions", { params: { topic_id: topicId } });
      setQuestions(res.data || []);
    } catch (err) {
      showNotice("error", errorText(err, "Could not load questions."));
    } finally {
      setQuestionsLoading(false);
    }
  }, [topicId]);

  useEffect(() => {
    if (tab === "questions") fetchQuestions();
  }, [tab, fetchQuestions]);

  // ---------- Subjects ----------
  const saveSubject = async (e) => {
    e.preventDefault();
    const { id, form } = subjectModal;
    if (!form.name.trim()) {
      showNotice("error", "Subject name is required.");
      return;
    }
    setSaving(true);
    try {
      const body = {
        name: form.name.trim(),
        code: form.code?.trim() || null,
        description: form.description?.trim() || null,
        course: form.course?.trim() || "",
        curriculum: form.curriculum?.trim() || "",
        academic_year: form.academic_year?.trim() || "",
      };
      if (id) await api.put(`/api/v1/subjects/${id}`, body);
      else await api.post("/api/v1/subjects", body);
      setSubjectModal(null);
      await fetchSubjects();
      showNotice("success", id ? "Subject updated." : "Subject created.");
    } catch (err) {
      showNotice("error", errorText(err, "Could not save subject."));
    } finally {
      setSaving(false);
    }
  };

  const deleteSubject = async (s) => {
    if (!window.confirm(`Delete "${s.name}" and all of its ${s.topic_count} topic(s), questions and quiz data? This cannot be undone.`)) return;
    try {
      await api.delete(`/api/v1/subjects/${s.id}`);
      await fetchSubjects();
      showNotice("success", "Subject deleted.");
    } catch (err) {
      showNotice("error", errorText(err, "Could not delete subject."));
    }
  };

  // ---------- Topics ----------
  const saveTopic = async (e) => {
    e.preventDefault();
    const { id, form } = topicModal;
    if (!form.name.trim()) {
      showNotice("error", "Topic name is required.");
      return;
    }
    setSaving(true);
    try {
      const body = {
        name: form.name.trim(),
        order_index: Number(form.order_index) || 0,
        description: form.description?.trim() || null,
      };
      if (id) await api.put(`/api/v1/topics/${id}`, body);
      else await api.post("/api/v1/topics", { ...body, subject_id: subjectId });
      setTopicModal(null);
      await fetchSubjects();
      showNotice("success", id ? "Topic updated." : "Topic created.");
    } catch (err) {
      showNotice("error", errorText(err, "Could not save topic."));
    } finally {
      setSaving(false);
    }
  };

  const deleteTopic = async (t) => {
    if (!window.confirm(`Delete topic "${t.name}" and its ${t.question_count} question(s)? This cannot be undone.`)) return;
    try {
      await api.delete(`/api/v1/topics/${t.id}`);
      await fetchSubjects();
      showNotice("success", "Topic deleted.");
    } catch (err) {
      showNotice("error", errorText(err, "Could not delete topic."));
    }
  };

  // ---------- Questions ----------
  const setOption = (i, value) => {
    const options = [...questionModal.form.options];
    options[i] = value;
    setQuestionModal({ ...questionModal, form: { ...questionModal.form, options } });
  };

  const addOption = () => {
    const { form } = questionModal;
    if (form.options.length >= 6) return;
    setQuestionModal({ ...questionModal, form: { ...form, options: [...form.options, ""] } });
  };

  const removeOption = (i) => {
    const { form } = questionModal;
    if (form.options.length <= 2) return;
    const options = form.options.filter((_, idx) => idx !== i);
    let correct = form.correct_answer;
    if (i === correct) correct = 0;
    else if (i < correct) correct -= 1;
    setQuestionModal({ ...questionModal, form: { ...form, options, correct_answer: correct } });
  };

  const saveQuestion = async (e) => {
    e.preventDefault();
    const { form } = questionModal;
    const options = form.options.map((o) => o.trim());
    if (!form.question_text.trim()) {
      showNotice("error", "Question text is required.");
      return;
    }
    if (options.some((o) => !o)) {
      showNotice("error", "Fill in every option, or remove the empty ones.");
      return;
    }
    if (new Set(options.map((o) => o.toLowerCase())).size !== options.length) {
      showNotice("error", "Options must be different from each other.");
      return;
    }
    setSaving(true);
    try {
      await api.post("/api/v1/quiz/questions", {
        topic_id: topicId,
        question_text: form.question_text.trim(),
        options,
        correct_answer: form.correct_answer,
        explanation: form.explanation?.trim() || null,
        difficulty: form.difficulty,
      });
      setQuestionModal(null);
      await Promise.all([fetchQuestions(), fetchSubjects()]);
      showNotice("success", "Question added.");
    } catch (err) {
      showNotice("error", errorText(err, "Could not save question."));
    } finally {
      setSaving(false);
    }
  };

  const deleteQuestion = async (q) => {
    if (!window.confirm("Delete this question? Students' past answers to it will also be removed.")) return;
    try {
      await api.delete(`/api/v1/quiz/questions/${q.id}`);
      await Promise.all([fetchQuestions(), fetchSubjects()]);
      showNotice("success", "Question deleted.");
    } catch (err) {
      showNotice("error", errorText(err, "Could not delete question."));
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} onRetry={fetchSubjects} />;

  const subjectPicker = (
    <select
      className="search-input"
      value={subjectId ?? ""}
      onChange={(e) => setSubjectId(Number(e.target.value))}
      aria-label="Subject"
    >
      {subjects.map((s) => (
        <option key={s.id} value={s.id}>{s.name}</option>
      ))}
    </select>
  );

  return (
    <div className="teacher-dashboard-page">
      <div className="page-header-row">
        <div>
          <h2>🛠️ Content Management</h2>
          <p className="page-subtitle">
            Manage teacher-curated syllabi and quiz questions. Match the course,
            board/institution, and year/semester to students' registration details.
          </p>
        </div>
      </div>

      {notice && (
        <div className={`auth-msg-banner ${notice.type === "success" ? "success" : "error"}`}>
          {notice.text}
        </div>
      )}

      <div style={{ display: "flex", gap: "8px", margin: "16px 0" }}>
        {[
          ["subjects", "Subjects"],
          ["topics", "Topics"],
          ["questions", "Quiz Questions"],
        ].map(([key, label]) => (
          <button key={key} className={`tab-btn ${tab === key ? "active" : ""}`} onClick={() => setTab(key)}>
            {label}
          </button>
        ))}
      </div>

      {/* ---------------- SUBJECTS ---------------- */}
      {tab === "subjects" && (
        <section className="teacher-section-card">
          <div className="section-head-row">
            <h3>Subjects ({subjects.length})</h3>
            <button className="action-btn-primary" onClick={() => setSubjectModal({ form: { ...EMPTY_SUBJECT } })}>
              + Add Subject
            </button>
          </div>
          {subjects.length === 0 ? (
            <div className="empty-state"><p>No subjects yet. Add your first one.</p></div>
          ) : (
            <div className="class-topics-table-wrapper">
              <table className="teacher-table">
                <thead>
                  <tr><th>Subject</th><th>Course</th><th>Board / Institution</th><th>Year / Semester</th><th>Topics</th><th>Description</th><th>Actions</th></tr>
                </thead>
                <tbody>
                  {subjects.map((s) => (
                    <tr key={s.id}>
                      <td><strong>{s.name}</strong></td>
                      <td>{s.course || "Not scoped"}{s.code ? ` (${s.code})` : ""}</td>
                      <td>{s.curriculum || "Not scoped"}</td>
                      <td>{s.academic_year || "Not scoped"}</td>
                      <td>{s.topic_count}</td>
                      <td>{s.description || "—"}</td>
                      <td style={{ whiteSpace: "nowrap" }}>
                        <button
                          className="action-btn-secondary btn-sm"
                          onClick={() => setSubjectModal({ id: s.id, form: {
                            name: s.name,
                            code: s.code || "",
                            description: s.description || "",
                            course: s.course || "",
                            curriculum: s.curriculum || "",
                            academic_year: s.academic_year || "",
                          } })}
                        >Edit</button>{" "}
                        <button className="action-btn-danger btn-sm" onClick={() => deleteSubject(s)}>Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {/* ---------------- TOPICS ---------------- */}
      {tab === "topics" && (
        <section className="teacher-section-card">
          <div className="section-head-row">
            <h3>Topics</h3>
            <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
              {subjects.length > 0 && subjectPicker}
              <button
                className="action-btn-primary"
                disabled={!subjectId}
                onClick={() => setTopicModal({ form: { ...EMPTY_TOPIC, order_index: topics.length + 1 } })}
              >+ Add Topic</button>
            </div>
          </div>
          {subjects.length === 0 ? (
            <div className="empty-state"><p>Create a subject first.</p></div>
          ) : topics.length === 0 ? (
            <div className="empty-state"><p>No topics in this subject yet.</p></div>
          ) : (
            <div className="class-topics-table-wrapper">
              <table className="teacher-table">
                <thead>
                  <tr><th>Order</th><th>Topic</th><th>Questions</th><th>Description</th><th>Actions</th></tr>
                </thead>
                <tbody>
                  {topics.map((t) => (
                    <tr key={t.id}>
                      <td>{t.order_index}</td>
                      <td><strong>{t.name}</strong></td>
                      <td>{t.question_count}</td>
                      <td>{t.description || "—"}</td>
                      <td style={{ whiteSpace: "nowrap" }}>
                        <button
                          className="action-btn-secondary btn-sm"
                          onClick={() => setTopicModal({ id: t.id, form: { name: t.name, order_index: t.order_index, description: t.description || "" } })}
                        >Edit</button>{" "}
                        <button className="action-btn-danger btn-sm" onClick={() => deleteTopic(t)}>Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {/* ---------------- QUESTIONS ---------------- */}
      {tab === "questions" && (
        <section className="teacher-section-card">
          <div className="section-head-row">
            <h3>Quiz Questions</h3>
            <div style={{ display: "flex", gap: "8px", alignItems: "center", flexWrap: "wrap" }}>
              {subjects.length > 0 && subjectPicker}
              {topics.length > 0 && (
                <select
                  className="search-input"
                  value={topicId ?? ""}
                  onChange={(e) => setTopicId(Number(e.target.value))}
                  aria-label="Topic"
                >
                  {topics.map((t) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              )}
              <button
                className="action-btn-primary"
                disabled={!topicId}
                onClick={() => setQuestionModal({ form: { ...EMPTY_QUESTION, options: [...EMPTY_QUESTION.options] } })}
              >+ Add Question</button>
            </div>
          </div>

          {!currentTopic ? (
            <div className="empty-state"><p>Select a subject that has at least one topic.</p></div>
          ) : questionsLoading ? (
            <LoadingSpinner />
          ) : questions.length === 0 ? (
            <div className="empty-state"><p>No questions for "{currentTopic.name}" yet.</p></div>
          ) : (
            <div className="class-topics-table-wrapper">
              <table className="teacher-table">
                <thead>
                  <tr><th>#</th><th>Question</th><th>Options</th><th>Level</th><th>Actions</th></tr>
                </thead>
                <tbody>
                  {questions.map((q, idx) => (
                    <tr key={q.id}>
                      <td>{idx + 1}</td>
                      <td>
                        {q.question_text}
                        {q.explanation && (
                          <div style={{ fontSize: "12px", color: "#64748b", marginTop: "4px" }}>💡 {q.explanation}</div>
                        )}
                      </td>
                      <td>
                        <ol type="A" style={{ margin: 0, paddingLeft: "18px" }}>
                          {q.options.map((o, i) => (
                            <li key={i} style={i === q.correct_answer ? { fontWeight: 700, color: "#15803d" } : undefined}>
                              {o}{i === q.correct_answer ? " ✓" : ""}
                            </li>
                          ))}
                        </ol>
                      </td>
                      <td>{q.difficulty}</td>
                      <td>
                        <button className="action-btn-danger btn-sm" onClick={() => deleteQuestion(q)}>Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {/* ---------------- MODALS ---------------- */}
      {subjectModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-md">
            <div className="modal-header">
              <h3>{subjectModal.id ? "Edit Subject" : "Add Subject"}</h3>
              <button className="modal-close" onClick={() => setSubjectModal(null)}>&times;</button>
            </div>
            <form onSubmit={saveSubject} className="modal-body">
              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Name *</label>
                <input className="search-input" style={{ width: "100%" }} value={subjectModal.form.name}
                  onChange={(e) => setSubjectModal({ ...subjectModal, form: { ...subjectModal.form, name: e.target.value } })} required />
              </div>
              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Code</label>
                <input className="search-input" style={{ width: "100%" }} value={subjectModal.form.code}
                  onChange={(e) => setSubjectModal({ ...subjectModal, form: { ...subjectModal.form, code: e.target.value } })} />
              </div>
              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Course / program (exact registration value) *</label>
                <input className="search-input" style={{ width: "100%" }} value={subjectModal.form.course}
                  maxLength={100} required
                  onChange={(e) => setSubjectModal({ ...subjectModal, form: { ...subjectModal.form, course: e.target.value } })} />
              </div>
              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Board / Institution (exact) *</label>
                <input className="search-input" style={{ width: "100%" }} value={subjectModal.form.curriculum}
                  maxLength={150} required
                  onChange={(e) => setSubjectModal({ ...subjectModal, form: { ...subjectModal.form, curriculum: e.target.value } })} />
              </div>
              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Year / Semester (exact) *</label>
                <input className="search-input" style={{ width: "100%" }} value={subjectModal.form.academic_year}
                  maxLength={20} required
                  onChange={(e) => setSubjectModal({ ...subjectModal, form: { ...subjectModal.form, academic_year: e.target.value } })} />
              </div>
              <p className="subtext" style={{ marginBottom: "14px" }}>
                Students see these syllabus topics and questions only when all
                three fields match their registration.
              </p>
              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Description</label>
                <textarea rows="3" className="search-input" style={{ width: "100%" }} value={subjectModal.form.description}
                  onChange={(e) => setSubjectModal({ ...subjectModal, form: { ...subjectModal.form, description: e.target.value } })} />
              </div>
              <div className="modal-footer">
                <button type="button" className="action-btn-secondary" onClick={() => setSubjectModal(null)}>Cancel</button>
                <button type="submit" className="action-btn-primary" disabled={saving}>{saving ? "Saving..." : "Save"}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {topicModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-md">
            <div className="modal-header">
              <h3>{topicModal.id ? "Edit Topic" : `Add Topic to ${currentSubject?.name || ""}`}</h3>
              <button className="modal-close" onClick={() => setTopicModal(null)}>&times;</button>
            </div>
            <form onSubmit={saveTopic} className="modal-body">
              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Name *</label>
                <input className="search-input" style={{ width: "100%" }} value={topicModal.form.name}
                  onChange={(e) => setTopicModal({ ...topicModal, form: { ...topicModal.form, name: e.target.value } })} required />
              </div>
              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Order</label>
                <input type="number" min="0" className="search-input" style={{ width: "100%" }} value={topicModal.form.order_index}
                  onChange={(e) => setTopicModal({ ...topicModal, form: { ...topicModal.form, order_index: e.target.value } })} />
              </div>
              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Description</label>
                <textarea rows="3" className="search-input" style={{ width: "100%" }} value={topicModal.form.description}
                  onChange={(e) => setTopicModal({ ...topicModal, form: { ...topicModal.form, description: e.target.value } })} />
              </div>
              <div className="modal-footer">
                <button type="button" className="action-btn-secondary" onClick={() => setTopicModal(null)}>Cancel</button>
                <button type="submit" className="action-btn-primary" disabled={saving}>{saving ? "Saving..." : "Save"}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {questionModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-lg">
            <div className="modal-header">
              <h3>Add Question to "{currentTopic?.name}"</h3>
              <button className="modal-close" onClick={() => setQuestionModal(null)}>&times;</button>
            </div>
            <form onSubmit={saveQuestion} className="modal-body">
              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Question *</label>
                <textarea rows="3" className="search-input" style={{ width: "100%" }} value={questionModal.form.question_text}
                  onChange={(e) => setQuestionModal({ ...questionModal, form: { ...questionModal.form, question_text: e.target.value } })} required />
              </div>

              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Options (select the correct one)</label>
                {questionModal.form.options.map((opt, i) => (
                  <div key={i} style={{ display: "flex", gap: "8px", alignItems: "center", marginTop: "6px" }}>
                    <input
                      type="radio"
                      name="correct"
                      checked={questionModal.form.correct_answer === i}
                      onChange={() => setQuestionModal({ ...questionModal, form: { ...questionModal.form, correct_answer: i } })}
                      aria-label={`Option ${String.fromCharCode(65 + i)} is correct`}
                    />
                    <span style={{ width: "18px" }}>{String.fromCharCode(65 + i)}.</span>
                    <input className="search-input" style={{ flex: 1 }} value={opt} onChange={(e) => setOption(i, e.target.value)} />
                    <button type="button" className="action-btn-secondary btn-sm" disabled={questionModal.form.options.length <= 2} onClick={() => removeOption(i)}>✕</button>
                  </div>
                ))}
                {questionModal.form.options.length < 6 && (
                  <button type="button" className="action-btn-secondary btn-sm" style={{ marginTop: "8px" }} onClick={addOption}>+ Add option</button>
                )}
              </div>

              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Explanation (shown after the quiz)</label>
                <textarea rows="2" className="search-input" style={{ width: "100%" }} value={questionModal.form.explanation}
                  onChange={(e) => setQuestionModal({ ...questionModal, form: { ...questionModal.form, explanation: e.target.value } })} />
              </div>

              <div className="form-group" style={{ marginBottom: "14px" }}>
                <label>Difficulty</label>
                <select className="search-input" value={questionModal.form.difficulty}
                  onChange={(e) => setQuestionModal({ ...questionModal, form: { ...questionModal.form, difficulty: e.target.value } })}>
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>

              <div className="modal-footer">
                <button type="button" className="action-btn-secondary" onClick={() => setQuestionModal(null)}>Cancel</button>
                <button type="submit" className="action-btn-primary" disabled={saving}>{saving ? "Saving..." : "Add Question"}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default TeacherManagement;