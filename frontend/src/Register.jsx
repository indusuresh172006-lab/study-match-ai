import { useState } from "react";
import api from "./api";

function Register({ onSwitchToLogin }) {
  const [role, setRole] = useState("student");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
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
    <div className="login-split-card register-split-card">
      {/* LEFT SECTION – 45% WIDTH */}
      <div className="login-left-section register-left-section">
        <div className="login-brand-header">
          <img
            className="login-flint-logo"
            src="/flint-logo.jpeg"
            alt="FLINT logo"
          />
          <p className="login-brand-subtitle">
            {role === "teacher" ? "Request a teacher account" : "Create your student account"}
          </p>
        </div>

        <form onSubmit={handleRegister} className="login-form">
          {/* Account Type Toggle */}
          <div className="login-field-group">
            <label className="login-field-label">Account Type</label>
            <div className="register-role-toggle">
              <button
                type="button"
                className={`register-role-btn ${role === "student" ? "active" : ""}`}
                onClick={() => setRole("student")}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                  <path d="M6 12v5c3 3 9 3 12 0v-5" />
                </svg>
                <span>Student</span>
              </button>
              <button
                type="button"
                className={`register-role-btn ${role === "teacher" ? "active" : ""}`}
                onClick={() => setRole("teacher")}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                  <circle cx="8.5" cy="7" r="4" />
                  <line x1="20" x2="20" y1="8" y2="14" />
                </svg>
                <span>Teacher</span>
              </button>
            </div>
          </div>

          {/* Full Name */}
          <div className="login-field-group">
            <label className="login-field-label">Full Name</label>
            <div className="login-input-wrapper">
              <span className="login-input-icon left">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </span>
              <input
                type="text"
                className="login-text-input"
                maxLength={100}
                placeholder="e.g. Alex Morgan"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                autoComplete="name"
              />
            </div>
          </div>

          {/* Email Address */}
          <div className="login-field-group">
            <label className="login-field-label">Email Address</label>
            <div className="login-input-wrapper">
              <span className="login-input-icon left">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="4" width="20" height="16" rx="2" />
                  <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                </svg>
              </span>
              <input
                type="email"
                className="login-text-input"
                placeholder="alex@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>
          </div>

          {/* Student Fields */}
          {role === "student" ? (
            <>
              <div className="login-field-group">
                <label className="login-field-label" htmlFor="current-course">Current Course</label>
                <div className="login-input-wrapper">
                  <span className="login-input-icon left">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                      <path d="M6 12v5c3 3 9 3 12 0v-5" />
                    </svg>
                  </span>
                  <select
                    id="current-course"
                    className="login-text-select"
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
              </div>

              {["Diploma", "Other / Not listed"].includes(course) && (
                <div className="login-field-group">
                  <label className="login-field-label" htmlFor="course-name">
                    {course === "Diploma" ? "Diploma program" : "Course name"}
                  </label>
                  <div className="login-input-wrapper">
                    <span className="login-input-icon left">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                      </svg>
                    </span>
                    <input
                      id="course-name"
                      type="text"
                      className="login-text-input"
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
                </div>
              )}

              <div className="register-row-2col">
                <div className="login-field-group">
                  <label className="login-field-label" htmlFor="curriculum">Board / Institution</label>
                  <div className="login-input-wrapper">
                    <span className="login-input-icon left">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M3 21h18" />
                        <path d="M5 21V7l7-4 7 4v14" />
                      </svg>
                    </span>
                    <input
                      id="curriculum"
                      type="text"
                      className="login-text-input"
                      maxLength={150}
                      placeholder="e.g. State Board / Uni"
                      value={curriculum}
                      onChange={(e) => setCurriculum(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="login-field-group">
                  <label className="login-field-label" htmlFor="academic-year">Year / Semester</label>
                  <div className="login-input-wrapper">
                    <span className="login-input-icon left">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                        <line x1="16" y1="2" x2="16" y2="6" />
                        <line x1="8" y1="2" x2="8" y2="6" />
                      </svg>
                    </span>
                    <input
                      id="academic-year"
                      type="text"
                      className="login-text-input"
                      maxLength={20}
                      placeholder="e.g. Year 2 / Sem 3"
                      value={academicYear}
                      onChange={(e) => setAcademicYear(e.target.value)}
                      required
                    />
                  </div>
                </div>
              </div>
            </>
          ) : (
            <>
              {/* Teacher Fields */}
              <div className="login-field-group">
                <label className="login-field-label" htmlFor="teacher-subject">Subject taught</label>
                <div className="login-input-wrapper">
                  <span className="login-input-icon left">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                      <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                    </svg>
                  </span>
                  <input
                    id="teacher-subject"
                    type="text"
                    className="login-text-input"
                    maxLength={100}
                    placeholder="e.g. Mathematics"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="register-row-2col">
                <div className="login-field-group">
                  <label className="login-field-label" htmlFor="teacher-college">College / Institution</label>
                  <div className="login-input-wrapper">
                    <span className="login-input-icon left">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M3 21h18" />
                        <path d="M5 21V7l7-4 7 4v14" />
                      </svg>
                    </span>
                    <input
                      id="teacher-college"
                      type="text"
                      className="login-text-input"
                      maxLength={150}
                      placeholder="Your college or institution"
                      value={curriculum}
                      onChange={(e) => setCurriculum(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="login-field-group">
                  <label className="login-field-label" htmlFor="teacher-semester">Semester taught</label>
                  <div className="login-input-wrapper">
                    <span className="login-input-icon left">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                        <line x1="16" y1="2" x2="16" y2="6" />
                        <line x1="8" y1="2" x2="8" y2="6" />
                      </svg>
                    </span>
                    <input
                      id="teacher-semester"
                      type="text"
                      className="login-text-input"
                      maxLength={20}
                      placeholder="e.g. Semester 3"
                      value={academicYear}
                      onChange={(e) => setAcademicYear(e.target.value)}
                      required
                    />
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Password */}
          <div className="login-field-group">
            <label className="login-field-label">Password (min 6 chars)</label>
            <div className="login-input-wrapper">
              <span className="login-input-icon left">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
              </span>
              <input
                type={showPassword ? "text" : "password"}
                className="login-text-input has-right-icon"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                autoComplete="new-password"
              />
              <button
                type="button"
                className="login-password-toggle-btn"
                onClick={() => setShowPassword(!showPassword)}
                title={showPassword ? "Hide password" : "Show password"}
                tabIndex="-1"
              >
                {showPassword ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                    <line x1="1" y1="1" x2="23" y2="23" />
                  </svg>
                ) : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          {/* Feedback Message */}
          {message && (
            <div className={success ? "register-success-alert" : "login-error-alert"} role="alert">
              <div>
                <span>{success ? "🎉 " : "⚠️ "}</span>
                <span>{message}</span>
              </div>
              {success && (
                <button
                  type="button"
                  className="register-goto-login-btn"
                  onClick={onSwitchToLogin}
                >
                  Go to Login →
                </button>
              )}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className="login-submit-button"
            disabled={loading}
          >
            {loading
              ? "Submitting..."
              : role === "teacher"
              ? "Request Teacher Account →"
              : "Create Account →"}
          </button>

          {/* Divider & Login Link */}
          <div className="login-divider-row">
            <span className="login-divider-line"></span>
            <span className="login-footer-text">
              Already have an account?{" "}
              <button
                type="button"
                className="login-register-link-btn"
                onClick={onSwitchToLogin}
              >
                Login here
              </button>
            </span>
            <span className="login-divider-line"></span>
          </div>
        </form>
      </div>

      {/* RIGHT SECTION – 55% WIDTH */}
      <div className="login-right-section">
        <div className="login-illustration-container">
          <img
            src="/education-illustration.png"
            alt="Education themed illustration with books, laptop, and learning elements"
            className="login-illustration-img"
          />
        </div>
      </div>
    </div>
  );
}

export default Register;
