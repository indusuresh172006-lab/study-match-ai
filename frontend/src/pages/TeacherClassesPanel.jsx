import { useCallback, useEffect, useState } from "react";
import api from "../api";

const EMPTY_CLASS = {
  name: "",
  course: "",
  curriculum: "",
  academic_year: "",
};

function TeacherClassesPanel({ onSelectedClassChange, isAdmin = false, hideHeader = false }) {
  const [classes, setClasses] = useState([]);
  const [selectedClassId, setSelectedClassId] = useState("");
  const [form, setForm] = useState(EMPTY_CLASS);
  const [students, setStudents] = useState([]);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const fetchClasses = useCallback(async () => {
    try {
      const response = await api.get("/api/v1/classes");
      setClasses(response.data || []);
      setError("");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load your classes.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchClasses();
  }, [fetchClasses]);

  useEffect(() => {
    if (selectedClassId && !classes.some((item) => String(item.id) === selectedClassId)) {
      setSelectedClassId("");
    }
  }, [classes, selectedClassId]);

  useEffect(() => {
    if (typeof onSelectedClassChange === "function") {
      onSelectedClassChange(selectedClassId ? Number(selectedClassId) : null);
    }
  }, [onSelectedClassChange, selectedClassId]);

  const createClass = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const response = await api.post("/api/v1/classes", form);
      setForm(EMPTY_CLASS);
      const createdClassId = String(response.data.id);
      setClasses((current) => [...current, response.data]);
      setSelectedClassId(createdClassId);
      setNotice(`Class created. Share join code ${response.data.join_code} with students.`);
      await fetchClasses();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not create the class.");
    } finally {
      setSaving(false);
    }
  };

  const loadRoster = async () => {
    if (!selectedClassId) return;
    setError("");
    try {
      const response = await api.get(`/api/v1/classes/${selectedClassId}/students`);
      setStudents(response.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load the class roster.");
    }
  };

  const importMarks = async (event) => {
    event.preventDefault();
    if (!selectedClassId || !file) return;
    setUploading(true);
    setError("");
    setNotice("");
    try {
      const payload = new FormData();
      payload.append("file", file);
      const response = await api.post(
        `/api/v1/classes/${selectedClassId}/marks/import`,
        payload,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setNotice(`${response.data.imported_rows} marks imported; ${response.data.students_updated} student profiles updated.`);
      setFile(null);
      event.target.reset();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.join(" ") : detail || "Could not import marks.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <section className="teacher-section-card teacher-class-panel">
      {!hideHeader && (
        <div className="card-head-row">
          <div>
            <h3>🏫 Classes, Enrollment & Marks</h3>
            <p className="subtext">
              {isAdmin
                ? "Review class rosters and import topic-tagged CSV/XLSX marks across the platform."
                : "Create a scoped class, share its join code, and import topic-tagged CSV/XLSX marks."}
            </p>
          </div>
        </div>
      )}

      {error && <p className="auth-error-msg" role="alert">{error}</p>}
      {notice && <p className="scope-feedback" role="status">{notice}</p>}

      <div className={`teacher-classes-grid ${isAdmin ? "admin-classes-grid" : ""}`}>
        {!isAdmin && <form className="teacher-class-form" onSubmit={createClass}>
          <h4>Create a class</h4>
          <label>
            Class name
            <input
              value={form.name}
              maxLength={100}
              required
              onChange={(event) => setForm({ ...form, name: event.target.value })}
              placeholder="e.g. Polytechnic Civil - Semester 3"
            />
          </label>
          <label>
            Course / program
            <input
              value={form.course}
              maxLength={100}
              required
              onChange={(event) => setForm({ ...form, course: event.target.value })}
              placeholder="e.g. Diploma in Civil Engineering"
            />
          </label>
          <label>
            Board / institution
            <input
              value={form.curriculum}
              maxLength={150}
              required
              onChange={(event) => setForm({ ...form, curriculum: event.target.value })}
              placeholder="e.g. Polytechnic College Kannur"
            />
          </label>
          <label>
            Year / semester
            <input
              value={form.academic_year}
              maxLength={20}
              required
              onChange={(event) => setForm({ ...form, academic_year: event.target.value })}
              placeholder="e.g. 3rd Semester"
            />
          </label>
          <button className="action-btn-primary" type="submit" disabled={saving}>
            {saving ? "Creating..." : "Create class and join code"}
          </button>
        </form>}

        <div className="teacher-class-roster">
          <h4>{isAdmin ? "Platform classes" : "Your classes"}</h4>
          {loading ? (
            <p className="subtext">Loading classes...</p>
          ) : classes.length === 0 ? (
            <p className="subtext">{isAdmin ? "Create a class above to get a student join code." : "Create a class to get a student join code."}</p>
          ) : (
            <>
              <label>
                Select a class for group matching and marks import
                <select
                  value={selectedClassId}
                  onChange={(event) => {
                    setSelectedClassId(event.target.value);
                    setStudents([]);
                  }}
                >
                  <option value="">Select a class</option>
                  {classes.map((studyClass) => (
                    <option key={studyClass.id} value={studyClass.id}>
                      {studyClass.name} ({studyClass.roster_size} students)
                    </option>
                  ))}
                </select>
              </label>
              {classes.filter((studyClass) => String(studyClass.id) === selectedClassId).map((studyClass) => (
                <div className="class-join-code" key={studyClass.id}>
                  <span>Student join code</span>
                  <strong>{studyClass.join_code}</strong>
                  <small>
                    {studyClass.course} · {studyClass.curriculum} · {studyClass.academic_year}
                  </small>
                </div>
              ))}
              <button
                className="action-btn-secondary btn-sm"
                type="button"
                onClick={loadRoster}
                disabled={!selectedClassId}
              >
                View enrolled students
              </button>
              {students.length > 0 && (
                <ul className="class-roster-list">
                  {students.map((student) => (
                    <li key={student.student_id}>
                      <span>{student.name}</span>
                      <small>{student.email}</small>
                    </li>
                  ))}
                </ul>
              )}
              <form className="class-mark-import" onSubmit={importMarks}>
                <label>
                  Import topic marks (.csv, .xlsx)
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xlsm"
                    onChange={(event) => setFile(event.target.files?.[0] || null)}
                    required
                  />
                </label>
                <p className="subtext">
                  Required columns: student_email, subject, topic, score, max_score.
                </p>
                <button
                  className="action-btn-primary btn-sm"
                  type="submit"
                  disabled={!selectedClassId || !file || uploading}
                >
                  {uploading ? "Importing marks..." : "Import and update skills"}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </section>
  );
}

export default TeacherClassesPanel;
