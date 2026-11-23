import { useCallback, useEffect, useState } from "react";
import api from "../api";

const EMPTY_TEACHER = { name: "", email: "", password: "", subject: "", college: "", semester: "" };
const EMPTY_CLASS = {
  name: "",
  course: "",
  curriculum: "",
  academic_year: "",
  teacher_id: "",
};

function AdminManagement() {
  const [overview, setOverview] = useState(null);
  const [users, setUsers] = useState([]);
  const [classes, setClasses] = useState([]);
  const [teacherRequests, setTeacherRequests] = useState([]);
  const [teacherForm, setTeacherForm] = useState(EMPTY_TEACHER);
  const [classForm, setClassForm] = useState(EMPTY_CLASS);
  const [classTeacherSelections, setClassTeacherSelections] = useState({});
  const [loading, setLoading] = useState(true);
  const [savingTeacher, setSavingTeacher] = useState(false);
  const [savingClass, setSavingClass] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadData = useCallback(async () => {
    setError("");
    try {
      const [overviewResponse, usersResponse, classesResponse, requestsResponse] = await Promise.all([
        api.get("/api/v1/admin/overview"),
        api.get("/api/v1/admin/users", { params: { limit: 200 } }),
        api.get("/api/v1/admin/classes", { params: { include_inactive: true } }),
        api.get("/api/v1/admin/teacher-requests"),
      ]);
      setError("");
      setOverview(overviewResponse.data);
      setUsers(usersResponse.data.items || []);
      setClasses(classesResponse.data || []);
      setTeacherRequests(requestsResponse.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load admin overview.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const teachers = users.filter((user) => user.role === "teacher");

  const createTeacher = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");
    setSavingTeacher(true);
    try {
      const response = await api.post("/api/v1/admin/teachers", teacherForm);
      setTeacherForm({ ...EMPTY_TEACHER });
      setNotice(`Teacher account created for ${response.data.email}.`);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not create teacher account.");
    } finally {
      setSavingTeacher(false);
    }
  };

  const reviewTeacherRequest = async (teacherId, decision) => {
    setError("");
    setNotice("");
    try {
      await api.patch(`/api/v1/admin/teacher-requests/${teacherId}`, { decision });
      setNotice(decision === "approve" ? "Teacher request approved." : "Teacher request rejected.");
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not review teacher request.");
    }
  };

  const createClass = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");
    setSavingClass(true);
    try {
      const response = await api.post("/api/v1/admin/classes", {
        ...classForm,
        teacher_id: Number(classForm.teacher_id),
      });
      setClassForm(EMPTY_CLASS);
      setNotice(`Class created. Join code: ${response.data.join_code}`);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not create class.");
    } finally {
      setSavingClass(false);
    }
  };

  const updateClass = async (studyClass, changes) => {
    setError("");
    setNotice("");
    try {
      await api.patch(`/api/v1/admin/classes/${studyClass.id}`, changes);
      setNotice(`Updated ${studyClass.name}.`);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not update class.");
    }
  };

  if (loading) {
    return <section className="teacher-section-card"><p>Loading admin controls...</p></section>;
  }

  return (
    <div className="admin-management">
      {error && <p className="auth-error-msg" role="alert">{error}</p>}
      {notice && <p className="scope-feedback" role="status">{notice}</p>}

      <section className="kpi-grid" aria-label="Platform overview">
        <div className="kpi-card info"><div className="kpi-icon">👥</div><div className="kpi-details"><span className="kpi-num">{overview?.total_users ?? 0}</span><span className="kpi-label">Total Accounts</span></div></div>
        <div className="kpi-card success"><div className="kpi-icon">👨‍🏫</div><div className="kpi-details"><span className="kpi-num">{overview?.teachers ?? 0}</span><span className="kpi-label">Teachers</span></div></div>
        <div className="kpi-card warning"><div className="kpi-icon">🎓</div><div className="kpi-details"><span className="kpi-num">{overview?.students ?? 0}</span><span className="kpi-label">Students</span></div></div>
        <div className="kpi-card info"><div className="kpi-icon">🏫</div><div className="kpi-details"><span className="kpi-num">{overview?.active_classes ?? 0} / {overview?.total_classes ?? 0}</span><span className="kpi-label">Active Classes</span></div></div>
      </section>

      <section className="teacher-section-card">
        <div className="card-head-row">
          <div>
            <h3>Teacher account requests</h3>
            <p className="subtext">Approve requests to enable teacher login and dashboard access.</p>
          </div>
          <span className="weak-count-badge">{teacherRequests.length} pending</span>
        </div>
        {teacherRequests.length === 0 ? (
          <p className="all-good-msg">No teacher requests are awaiting review.</p>
        ) : (
          <div className="class-topics-table-wrapper">
            <table className="teacher-table">
              <thead><tr><th>Name</th><th>Email</th><th>Subject</th><th>College</th><th>Semester</th><th>Review</th></tr></thead>
              <tbody>{teacherRequests.map((request) => (
                <tr key={request.id}>
                  <td>{request.name}</td>
                  <td>{request.email}</td>
                  <td>{request.subject || "—"}</td>
                  <td>{request.college || "—"}</td>
                  <td>{request.semester || "—"}</td>
                  <td>
                    <div className="teacher-review-actions">
                      <button className="action-btn-success btn-sm" type="button" onClick={() => reviewTeacherRequest(request.id, "approve")}>Approve</button>
                      <button className="action-btn-secondary btn-sm" type="button" onClick={() => reviewTeacherRequest(request.id, "reject")}>Reject</button>
                    </div>
                  </td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        )}
      </section>

      <div className="teacher-split-grid admin-forms-grid">
        <section className="teacher-section-card">
          <div className="card-head-row"><div><h3>Create a teacher account</h3><p className="subtext">Only administrators can provision teacher accounts.</p></div></div>
          <form className="teacher-class-form" onSubmit={createTeacher}>
            <label>Full name<input required minLength={2} maxLength={100} value={teacherForm.name} onChange={(event) => setTeacherForm({ ...teacherForm, name: event.target.value })} /></label>
            <label>Email<input required type="email" value={teacherForm.email} onChange={(event) => setTeacherForm({ ...teacherForm, email: event.target.value })} /></label>
            <label>Subject<input required maxLength={100} value={teacherForm.subject} onChange={(event) => setTeacherForm({ ...teacherForm, subject: event.target.value })} /></label>
            <label>College / institution<input required maxLength={150} value={teacherForm.college} onChange={(event) => setTeacherForm({ ...teacherForm, college: event.target.value })} /></label>
            <label>Semester taught<input required maxLength={20} value={teacherForm.semester} onChange={(event) => setTeacherForm({ ...teacherForm, semester: event.target.value })} /></label>
            <label>Initial password (12+ characters)<input required type="password" minLength={12} maxLength={128} autoComplete="new-password" value={teacherForm.password} onChange={(event) => setTeacherForm({ ...teacherForm, password: event.target.value })} /></label>
            <button className="action-btn-primary" type="submit" disabled={savingTeacher}>{savingTeacher ? "Creating..." : "Create teacher"}</button>
          </form>
        </section>

        <section className="teacher-section-card">
          <div className="card-head-row"><div><h3>Create a class</h3><p className="subtext">Assign the class to an existing teacher.</p></div></div>
          <form className="teacher-class-form" onSubmit={createClass}>
            <label>Class name<input required minLength={2} maxLength={100} value={classForm.name} onChange={(event) => setClassForm({ ...classForm, name: event.target.value })} /></label>
            <label>Course / program<input required maxLength={100} value={classForm.course} onChange={(event) => setClassForm({ ...classForm, course: event.target.value })} /></label>
            <label>Board / institution<input required maxLength={150} value={classForm.curriculum} onChange={(event) => setClassForm({ ...classForm, curriculum: event.target.value })} /></label>
            <label>Year / semester<input required maxLength={20} value={classForm.academic_year} onChange={(event) => setClassForm({ ...classForm, academic_year: event.target.value })} /></label>
            <label>Teacher<select required value={classForm.teacher_id} onChange={(event) => setClassForm({ ...classForm, teacher_id: event.target.value })}><option value="">Select a teacher</option>{teachers.map((teacher) => <option key={teacher.id} value={teacher.id}>{teacher.name} ({teacher.email})</option>)}</select></label>
            <button className="action-btn-primary" type="submit" disabled={savingClass || teachers.length === 0}>{savingClass ? "Creating..." : "Create class and join code"}</button>
            {teachers.length === 0 && <p className="subtext">Create a teacher account first.</p>}
          </form>
        </section>
      </div>

      <section className="teacher-section-card">
        <div className="card-head-row"><div><h3>Accounts</h3><p className="subtext">Showing {users.length} of {overview?.total_users ?? users.length} accounts.</p></div><button className="action-btn-secondary btn-sm" type="button" onClick={loadData}>Refresh</button></div>
        <div className="class-topics-table-wrapper">
          <table className="teacher-table">
            <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Approval</th></tr></thead>
            <tbody>{users.map((user) => <tr key={user.id}><td>{user.name}</td><td>{user.email}</td><td><span className="status-badge">{user.role.toUpperCase()}</span></td><td><span className="status-badge">{user.approval_status.toUpperCase()}</span></td></tr>)}</tbody>
          </table>
        </div>
      </section>

      <section className="teacher-section-card">
        <div className="card-head-row"><div><h3>Class administration</h3><p className="subtext">Reassign classes and deactivate or reactivate enrollment codes.</p></div></div>
        <div className="class-topics-table-wrapper">
          <table className="teacher-table">
            <thead><tr><th>Class</th><th>Course scope</th><th>Teacher</th><th>Join code</th><th>Roster</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>{classes.map((studyClass) => (
              <tr key={studyClass.id}>
                <td>{studyClass.name}</td>
                <td>{studyClass.course}<br /><small>{studyClass.curriculum} · {studyClass.academic_year}</small></td>
                <td>
                  <select
                    aria-label={`Teacher for ${studyClass.name}`}
                    value={classTeacherSelections[studyClass.id] ?? studyClass.teacher_id}
                    onChange={(event) => setClassTeacherSelections({ ...classTeacherSelections, [studyClass.id]: Number(event.target.value) })}
                  >
                    {teachers.map((teacher) => <option key={teacher.id} value={teacher.id}>{teacher.name}</option>)}
                  </select>
                </td>
                <td>{studyClass.join_code}</td>
                <td>{studyClass.roster_size}</td>
                <td>{studyClass.is_active ? "Active" : "Inactive"}</td>
                <td>
                  <div className="teacher-review-actions">
                    {Number(classTeacherSelections[studyClass.id] ?? studyClass.teacher_id) !== studyClass.teacher_id && (
                      <button className="action-btn-primary btn-sm" type="button" onClick={() => updateClass(studyClass, { teacher_id: Number(classTeacherSelections[studyClass.id]) })}>Reassign</button>
                    )}
                    <button className="action-btn-secondary btn-sm" type="button" onClick={() => updateClass(studyClass, { is_active: !studyClass.is_active })}>{studyClass.is_active ? "Deactivate" : "Reactivate"}</button>
                  </div>
                </td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default AdminManagement;
