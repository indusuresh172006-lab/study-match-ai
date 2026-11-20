import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";

const emptyProfile = {
  course: "",
  college: "",
  semester: "",
  phone: "",
  stream: "",
  academic_level: "",
  learning_goal: "",
};

function StudentProfile({ user }) {
  const [profile, setProfile] = useState(emptyProfile);
  const [learningInterests, setLearningInterests] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [loadError, setLoadError] = useState("");
  const [success, setSuccess] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;

    const loadProfile = async () => {
      try {
        const response = await api.get("/api/v1/auth/me");
        if (!active) return;

        const studentProfile = response.data?.profile || {};
        setProfile({
          course: studentProfile.course || "",
          college: studentProfile.college || "",
          semester: studentProfile.semester || "",
          phone: studentProfile.phone || "",
          stream: studentProfile.stream || "",
          academic_level: studentProfile.academic_level || "",
          learning_goal: studentProfile.learning_goal || "",
        });
        setLearningInterests(
          Array.isArray(studentProfile.learning_interests)
            ? studentProfile.learning_interests.join(", ")
            : ""
        );
      } catch (err) {
        console.error("Could not load student profile:", err);
        if (active) setLoadError("Could not load your profile. Check your connection and try again.");
      } finally {
        if (active) setLoading(false);
      }
    };

    loadProfile();
    return () => {
      active = false;
    };
  }, [reloadKey]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setProfile((current) => ({ ...current, [name]: value }));
    setSuccess("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const response = await api.put("/api/v1/auth/profile", {
        ...profile,
        learning_interests: learningInterests
          .split(",")
          .map((interest) => interest.trim())
          .filter(Boolean),
      });
      setProfile((current) => ({ ...current, ...response.data }));
      setSuccess("Profile saved. Your course-based syllabus and learning resources will use these details.");
    } catch (err) {
      console.error("Could not save student profile:", err);
      const detail = err.response?.data?.detail;
      const message = Array.isArray(detail)
        ? detail.map((item) => item.msg || "Invalid profile details").join("; ")
        : typeof detail === "string"
          ? detail
          : "Could not save your profile. Please try again.";
      setError(message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="student-profile-page">
      <div className="page-header-row">
        <div>
          <h2>My Profile</h2>
          <p className="page-subtitle">Keep your academic details up to date for course-matched study content.</p>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Loading your profile..." />
      ) : (
        <div className="student-profile-layout">
          <section className="student-profile-account">
            <div className="student-profile-avatar">
              {user?.name ? user.name.charAt(0).toUpperCase() : "S"}
            </div>
            <div>
              <span className="student-profile-eyebrow">STUDENT ACCOUNT</span>
              <h3>{user?.name || "Student"}</h3>
              <p>{user?.email || ""}</p>
            </div>
          </section>

          <section className="student-profile-card">
            <div className="student-profile-card-heading">
              <div>
                <h3>Academic profile</h3>
                <p>These details help FLINT match your syllabus, quizzes, and study materials.</p>
              </div>
            </div>

            {loadError ? (
              <div className="student-profile-load-error">
                <p className="student-profile-message error" role="alert">{loadError}</p>
                <button
                  className="action-btn-secondary"
                  type="button"
                  onClick={() => {
                    setLoadError("");
                    setLoading(true);
                    setReloadKey((current) => current + 1);
                  }}
                >
                  Try again
                </button>
              </div>
            ) : (
              <form className="student-profile-form" onSubmit={handleSubmit}>
                <label>
                  Course / program
                  <input
                    name="course"
                    type="text"
                    maxLength={100}
                    value={profile.course}
                    onChange={handleChange}
                    placeholder="e.g. Diploma in Computer Engineering"
                    required
                  />
                </label>
                <label>
                  College
                  <input
                    name="college"
                    type="text"
                    maxLength={150}
                    value={profile.college}
                    onChange={handleChange}
                    placeholder="e.g. Polytechnic College Kannur"
                    required
                  />
                </label>
                <label>
                  Semester
                  <input
                    name="semester"
                    type="text"
                    maxLength={20}
                    value={profile.semester}
                    onChange={handleChange}
                    placeholder="e.g. 3rd Semester"
                    required
                  />
                </label>
                <label>
                  Phone
                  <input
                    name="phone"
                    type="tel"
                    maxLength={30}
                    value={profile.phone}
                    onChange={handleChange}
                    placeholder="Optional"
                  />
                </label>
                <label>
                  Stream / specialization
                  <input
                    name="stream"
                    type="text"
                    maxLength={100}
                    value={profile.stream}
                    onChange={handleChange}
                    placeholder="e.g. Computer Engineering"
                  />
                </label>
                <label>
                  Academic level
                  <input
                    name="academic_level"
                    type="text"
                    maxLength={50}
                    value={profile.academic_level}
                    onChange={handleChange}
                    placeholder="e.g. Diploma"
                  />
                </label>
                <label className="student-profile-form-wide">
                  Learning goal
                  <textarea
                    name="learning_goal"
                    maxLength={255}
                    value={profile.learning_goal}
                    onChange={handleChange}
                    placeholder="What would you like to achieve?"
                    rows={3}
                  />
                </label>
                <label className="student-profile-form-wide">
                  Learning interests <span>(separate with commas)</span>
                  <input
                    type="text"
                    value={learningInterests}
                    onChange={(event) => {
                      setLearningInterests(event.target.value);
                      setSuccess("");
                    }}
                    placeholder="e.g. Web development, databases"
                  />
                </label>

                {error && <p className="student-profile-message error" role="alert">{error}</p>}
                {success && (
                  <div className="student-profile-message success" role="status">
                    <p>{success}</p>
                    <Link to="/quiz">Open your updated syllabus and quizzes</Link>
                  </div>
                )}
                <div className="student-profile-form-actions">
                  <button className="action-btn-primary" type="submit" disabled={saving}>
                    {saving ? "Saving..." : "Save profile"}
                  </button>
                </div>
              </form>
            )}
          </section>
        </div>
      )}
    </div>
  );
}

export default StudentProfile;
