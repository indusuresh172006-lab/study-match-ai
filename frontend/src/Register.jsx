import { useState } from "react";
import api from "./api";

function Register({ onSwitchToLogin }) {
  const [role, setRole] = useState("student");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [subject, setSubject] = useState("");
  const [course, setCourse] = useState("");
  const [courseName, setCourseName] = useState("");
  const [curriculum, setCurriculum] = useState("");
  const [academicYear, setAcademicYear] = useState("");
  const [classCode, setClassCode] = useState("");
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setMessage("");
    setLoading(true);

    try {
      const registration = {
        name: name.trim(),
        email: email.trim(),
        password: password,
        role,
      };
      if (role === "teacher") {
        Object.assign(registration, {
          subject: subject.trim(),
          college: curriculum.trim(),
          semester: academicYear.trim(),
        });
      } else {
        Object.assign(registration, {
          course: ["Diploma", "Other / Not listed"].includes(course)
            ? courseName.trim()
            : course,
          college: curriculum.trim(),
          semester: academicYear.trim(),
          class_code: classCode.trim() || null,
        });
      }
      await api.post("/register", registration);

      setSuccess(true);
      setMessage(
        role === "teacher"
          ? "Teacher request submitted. You can sign in to the dashboard after an administrator approves your account."
          : "Registration successful! You can now log in."
      );
    } catch (error) {
      setSuccess(false);
      setMessage(error.response?.data?.detail || "Registration failed. Try a different email.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-card">
      <div className="auth-brand-head">
        <img className="auth-logo" src="/flint-logo.jpeg" alt="FLINT education logo" />
        <h1>FLINT</h1>
        <p className="auth-subtitle">
          {role === "teacher" ? "Request a teacher account" : "Create your student account"}
        </p>
      </div>

      <form onSubmit={handleRegister} className="auth-form">
        <div className="form-field">
          <label htmlFor="account-role">Account type</label>
          <select id="account-role" value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="student">Student</option>
            <option value="teacher">Teacher (requires admin approval)</option>
          </select>
        </div>

        <div className="form-field">
          <label>Full Name</label>
          <input
            type="text"
            maxLength={100}
            placeholder="e.g. Alex Morgan"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>

        <div className="form-field">
          <label>Email Address</label>
          <input
            type="email"
            placeholder="alex@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        {role === "student" ? (
          <>
            <div className="form-field">
              <label htmlFor="current-course">Current Course</label>
              <select
                id="current-course"
                value={course}
                onChange={(e) => setCourse(e.target.value)}
                required
              >
                <option value="" disabled>Select your current course</option>
                <option value="Higher Secondary">Higher Secondary</option>
                <option value="B.A.">B.A.</option>
                <option value="B.Sc.">B.Sc.</option>
                <option value="B.Com.">B.Com.</option>
                <option value="B.Tech / B.E.">B.Tech / B.E.</option>
                <option value="BCA">BCA</option>
                <option value="BBA">BBA</option>
                <option value="MBBS">MBBS</option>
                <option value="Diploma">Diploma</option>
                <option value="Other / Not listed">Other / Not listed</option>
              </select>
            </div>

            {["Diploma", "Other / Not listed"].includes(course) && (
              <div className="form-field">
                <label htmlFor="course-name">
                  {course === "Diploma" ? "Diploma program" : "Course name"}
                </label>
                <input
                  id="course-name"
                  type="text"
                  maxLength={100}
                  placeholder={
                    course === "Diploma"
                      ? "e.g. Diploma in Civil Engineering"
                      : "Enter your course or program name"
                  }
                  value={courseName}
                  onChange={(e) => setCourseName(e.target.value)}
                  required
                />
              </div>
            )}

            <div className="form-field">
              <label htmlFor="curriculum">Board / Institution</label>
              <input
                id="curriculum"
                type="text"
                maxLength={150}
                placeholder="e.g. State Board or university name"
                value={curriculum}
                onChange={(e) => setCurriculum(e.target.value)}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="academic-year">Current Year / Semester</label>
              <input
                id="academic-year"
                type="text"
                maxLength={20}
                placeholder="e.g. Year 2 or Semester 3"
                value={academicYear}
                onChange={(e) => setAcademicYear(e.target.value)}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="class-code">Teacher's class code (optional)</label>
              <input
                id="class-code"
                type="text"
                maxLength={16}
                autoCapitalize="characters"
                placeholder="Enter the code shared by your teacher"
                value={classCode}
                onChange={(e) => setClassCode(e.target.value.toUpperCase())}
              />
            </div>
          </>
        ) : (
          <>
            <div className="form-field">
              <label htmlFor="teacher-subject">Subject taught</label>
              <input
                id="teacher-subject"
                type="text"
                maxLength={100}
                placeholder="e.g. Mathematics"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="teacher-college">College / Institution</label>
              <input
                id="teacher-college"
                type="text"
                maxLength={150}
                placeholder="Your college or institution"
                value={curriculum}
                onChange={(e) => setCurriculum(e.target.value)}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="teacher-semester">Semester taught</label>
              <input
                id="teacher-semester"
                type="text"
                maxLength={20}
                placeholder="e.g. Semester 3"
                value={academicYear}
                onChange={(e) => setAcademicYear(e.target.value)}
                required
              />
            </div>
          </>
        )}

        <div className="form-field">
          <label>Password (min 6 chars)</label>
          <input
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
        </div>

        <button type="submit" className="auth-submit-btn" disabled={loading}>
          {loading
            ? "Submitting..."
            : role === "teacher"
              ? "Request Teacher Account →"
              : "Create Account →"}
        </button>
      </form>

      {message && (
        <div className={`auth-msg-banner ${success ? "success" : "error"}`}>
          {message}
          {success && (
            <button className="link-button block-btn" onClick={onSwitchToLogin}>
              Go to Login →
            </button>
          )}
        </div>
      )}

      <div className="auth-switch-footer">
        Already have an account?{" "}
        <button type="button" className="link-button" onClick={onSwitchToLogin}>
          Login here
        </button>
      </div>
    </div>
  );
}

export default Register;