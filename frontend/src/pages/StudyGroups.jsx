import { useState, useEffect } from "react";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import EmptyState from "../components/EmptyState";

function StudyGroups({ user }) {
  const [group, setGroup] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Schedules state
  const [mySchedules, setMySchedules] = useState([]);
  const [newDay, setNewDay] = useState("Monday");
  const [newStart, setNewStart] = useState("17:00");
  const [newEnd, setNewEnd] = useState("19:00");
  const [savingSchedule, setSavingSchedule] = useState(false);
  const [requestingTeacher, setRequestingTeacher] = useState(false);
  const [teacherRequestMessage, setTeacherRequestMessage] = useState("");
  const [teacherRequestError, setTeacherRequestError] = useState("");

  // Peer-teaching view filter: 'all' | 'tutors_for_me' | 'i_can_teach'
  const [teachingFilter, setTeachingFilter] = useState("all");

  useEffect(() => {
    fetchGroupData();
    fetchMySchedules();
  }, []);

  const fetchGroupData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get("/api/v1/groups/my");
      setGroup(res.data);
    } catch (err) {
      console.error("Error fetching group:", err);
      setError("Unable to load your assigned study group.");
    } finally {
      setLoading(false);
    }
  };

  const fetchMySchedules = async () => {
    try {
      const res = await api.get("/api/v1/schedules/my");
      setMySchedules(res.data || []);
    } catch (err) {
      console.error("Error fetching schedules:", err);
    }
  };

  const handleAddSchedule = async (e) => {
    e.preventDefault();
    setSavingSchedule(true);
    try {
      await api.post("/api/v1/schedules", {
        day_of_week: newDay,
        start_time: newStart,
        end_time: newEnd,
      });
      await fetchMySchedules();
      await fetchGroupData(); // refresh common slots
    } catch (err) {
      console.error("Error saving schedule:", err);
    } finally {
      setSavingSchedule(false);
    }
  };

  const handleDeleteSchedule = async (slotId) => {
    try {
      await api.delete(`/api/v1/schedules/${slotId}`);
      setMySchedules(mySchedules.filter((s) => s.id !== slotId));
      await fetchGroupData();
    } catch (err) {
      console.error("Error deleting schedule:", err);
    }
  };

  const requestTeacherSupport = async (topics = []) => {
    setRequestingTeacher(true);
    setTeacherRequestMessage("");
    setTeacherRequestError("");
    try {
      const topicSummary = topics.length ? topics.join(", ") : "course and syllabus support";
      await api.post("/api/v1/guidance/counselling", {
        request_type: "study_support",
        preferred_mode: "Online",
        message: `Please help me study ${topicSummary}. I need a teacher-led study session or peer-group match if a suitable peer is available.`,
      });
      setTeacherRequestMessage("Your study-support request was sent to the teacher dashboard.");
    } catch (err) {
      const detail = err.response?.data?.detail;
      const message = Array.isArray(detail)
        ? detail.map((item) => item.msg || "Invalid request").join("; ")
        : typeof detail === "string"
          ? detail
          : "Could not send your study-support request. Please try again.";
      setTeacherRequestError(message);
    } finally {
      setRequestingTeacher(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading your intelligent study group..." />;
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={fetchGroupData} />;
  }

  if (!group) {
    return (
      <div className="page-container compact-layout">
        <div className="page-header compact-header">
          <div>
            <h2>👥 Intelligent Study Groups</h2>
            <p>Peer-teaching matches and synchronized study sessions</p>
          </div>
        </div>
        <EmptyState
          title="No Active Study Group Assigned Yet"
          description="Your teacher hasn't generated study groups yet, or you haven't completed enough topic diagnostic quizzes. Complete your topic quizzes to help the matching algorithm place you in an optimal group!"
          actionText="Take a Topic Quiz"
          onAction={() => (window.location.href = "/quiz")}
        />
        {teacherRequestMessage && <p className="all-good-msg" role="status">{teacherRequestMessage}</p>}
        {teacherRequestError && <p className="auth-error-msg" role="alert">{teacherRequestError}</p>}
        <button
          className="action-btn-secondary"
          onClick={() => requestTeacherSupport()}
          disabled={requestingTeacher}
        >
          {requestingTeacher ? "Sending request..." : "Request teacher support or peer matching"}
        </button>
      </div>
    );
  }

  // Filter teaching pairs
  const tutorsForMe = group.teaching_pairs.filter(
    (p) => p.learner_id === user?.id
  );
  const iCanTeach = group.teaching_pairs.filter(
    (p) => p.tutor_id === user?.id
  );

  let displayedPairs = group.teaching_pairs;
  if (teachingFilter === "tutors_for_me") displayedPairs = tutorsForMe;
  if (teachingFilter === "i_can_teach") displayedPairs = iCanTeach;

  const myMember = group.members.find((member) => member.student_id === user?.id);
  const myWeakTopics = myMember?.weak_topics || [];
  const topicsWithTutor = new Set(tutorsForMe.map((pair) => pair.topic_name));
  const topicsNeedingTeacher = myWeakTopics.filter((topic) => !topicsWithTutor.has(topic));

  return (
    <div className="page-container compact-layout">
      {/* Page Header */}
      <div className="page-header compact-header">
        <div>
          <h2>👥 Intelligent Study Group Matcher</h2>
          <p>
            Balanced study group formed via ML complementary matching. Learn
            together, teach each other, and coordinate common study sessions.
          </p>
        </div>
        <div className="header-badges-row">
          <span className="badge-pill-primary">
            🛡️ {group.name}
          </span>
          <span className="badge-pill-success">
            🎯 {group.coverage_rate}% Weak-Topic Coverage
          </span>
        </div>
      </div>

      {/* Group Overview Banner */}
      <div className="group-hero-card">
        <div className="group-hero-left">
          <div className="group-avatar-stack">
            {group.members.slice(0, 4).map((m, idx) => (
              <div key={m.student_id} className="stacked-avatar" title={m.name}>
                {m.name.charAt(0).toUpperCase()}
              </div>
            ))}
          </div>
          <div>
            <h3>{group.name}</h3>
            <p className="hero-subtext">
              {group.member_count} Members &bull; Formed using Maximum-Synergy
              Weak-to-Strong Topic Matching
            </p>
          </div>
        </div>

        <div className="group-hero-metrics">
          <div className="metric-box">
            <span className="metric-val">{group.covered_topics.length}</span>
            <span className="metric-lbl">Topics Covered</span>
          </div>
          <div className="metric-box">
            <span className="metric-val">{group.teaching_pairs.length}</span>
            <span className="metric-lbl">Teaching Pairs</span>
          </div>
          <div className="metric-box">
            <span className="metric-val">{group.common_schedules.length}</span>
            <span className="metric-lbl">Common Sessions</span>
          </div>
        </div>
      </div>

      {topicsNeedingTeacher.length > 0 && (
        <section className="teacher-section-card" style={{ marginBottom: "20px" }}>
          <h3>Need help with topics not covered by a peer?</h3>
          <p>
            No strong peer match is available for: {topicsNeedingTeacher.join(", ")}.
            You can ask a teacher to lead a study session.
          </p>
          {teacherRequestMessage && <p className="all-good-msg" role="status">{teacherRequestMessage}</p>}
          {teacherRequestError && <p className="auth-error-msg" role="alert">{teacherRequestError}</p>}
          <button
            className="action-btn-secondary"
            onClick={() => requestTeacherSupport(topicsNeedingTeacher)}
            disabled={requestingTeacher}
          >
            {requestingTeacher ? "Sending request..." : "Request teacher-led study support"}
          </button>
        </section>
      )}

      {/* Grid: Group Members Roster */}
      <section className="section-block">
        <h3 className="section-title">👥 Group Members Roster</h3>
        <div className="members-grid">
          {group.members.map((member) => {
            const isMe = member.student_id === user?.id;
            return (
              <div
                key={member.student_id}
                className={`member-roster-card ${isMe ? "is-current-user" : ""}`}
              >
                <div className="member-card-header">
                  <div className="user-avatar-small">
                    {member.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <strong className="member-name">
                      {member.name} {isMe && "(You)"}
                    </strong>
                    <span className="role-chip">{member.role}</span>
                  </div>
                </div>

                <div className="member-topics-section">
                  <div className="topic-subgroup">
                    <span className="topic-subgroup-label text-success">
                      ⭐ Strong In:
                    </span>
                    <div className="pills-wrap">
                      {member.strong_topics.length > 0 ? (
                        member.strong_topics.map((t, i) => (
                          <span key={i} className="skill-pill-strong">
                            {t}
                          </span>
                        ))
                      ) : (
                        <span className="empty-subtext">None recorded</span>
                      )}
                    </div>
                  </div>

                  <div className="topic-subgroup" style={{ marginTop: "6px" }}>
                    <span className="topic-subgroup-label text-warning">
                      🌱 Working On:
                    </span>
                    <div className="pills-wrap">
                      {member.weak_topics.length > 0 ? (
                        member.weak_topics.map((t, i) => (
                          <span key={i} className="skill-pill-weak">
                            {t}
                          </span>
                        ))
                      ) : (
                        <span className="empty-subtext">All topics strong</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Section 2: Peer-Teaching Recommendations */}
      <section className="section-block">
        <div className="section-header-flex">
          <h3 className="section-title">
            🤝 Peer-Teaching Recommendations ({group.teaching_pairs.length})
          </h3>
          <div className="filter-pills-row">
            <button
              className={`filter-btn ${teachingFilter === "all" ? "active" : ""}`}
              onClick={() => setTeachingFilter("all")}
            >
              All Pairs ({group.teaching_pairs.length})
            </button>
            <button
              className={`filter-btn ${teachingFilter === "tutors_for_me" ? "active" : ""}`}
              onClick={() => setTeachingFilter("tutors_for_me")}
            >
              🎓 Who Can Tutor Me ({tutorsForMe.length})
            </button>
            <button
              className={`filter-btn ${teachingFilter === "i_can_teach" ? "active" : ""}`}
              onClick={() => setTeachingFilter("i_can_teach")}
            >
              ⭐ Whom I Can Tutor ({iCanTeach.length})
            </button>
          </div>
        </div>

        {displayedPairs.length === 0 ? (
          <div className="empty-notice-box">
            No peer-teaching pairings matching this filter.
          </div>
        ) : (
          <div className="teaching-pairs-grid">
            {displayedPairs.map((pair, idx) => {
              const isTutorMe = pair.tutor_id === user?.id;
              const isLearnerMe = pair.learner_id === user?.id;

              return (
                <div
                  key={idx}
                  className={`teaching-pair-card ${
                    isTutorMe ? "border-tutor" : isLearnerMe ? "border-learner" : ""
                  }`}
                >
                  <div className="pair-header-row">
                    <span className="pair-topic-badge">
                      📖 {pair.topic_name}
                    </span>
                    <span className="pair-status-tag">Recommended</span>
                  </div>

                  <div className="pair-flow-row">
                    <div className="pair-person">
                      <span className="person-label">Tutor (Strong)</span>
                      <strong className="person-name">
                        {pair.tutor_name} {isTutorMe && "(You)"}
                      </strong>
                    </div>

                    <div className="pair-arrow">➔</div>

                    <div className="pair-person">
                      <span className="person-label">Learner (Target)</span>
                      <strong className="person-name">
                        {pair.learner_name} {isLearnerMe && "(You)"}
                      </strong>
                    </div>
                  </div>

                  <p className="pair-reason-text">
                    💡 <strong>Pedagogical Reason:</strong> {pair.reason}
                  </p>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Section 3: Study Schedule Synchronizer */}
      <section className="section-block">
        <h3 className="section-title">
          ⏰ Group Schedule Synchronizer & Common Study Sessions
        </h3>

        <div className="schedule-two-col">
          {/* Left: Recommended Common Sessions */}
          <div className="common-sessions-panel">
            <h4>📅 Top Overlapping Study Windows</h4>
            <p className="panel-subtext">
              Times when majority of group members are free:
            </p>

            {group.common_schedules && group.common_schedules.length > 0 ? (
              <div className="sessions-list">
                {group.common_schedules.map((slot, i) => (
                  <div key={i} className="session-card">
                    <div className="session-time-block">
                      <span className="session-day">{slot.day_of_week}</span>
                      <span className="session-hours">
                        {slot.start_time} - {slot.end_time}
                      </span>
                    </div>

                    <div className="session-attendance">
                      <span className="attendance-pill">
                        👥 {slot.available_count}/{slot.total_members} Members Free
                      </span>
                      <span className="attendance-pct">
                        {slot.match_percentage}% Attendance Match
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-notice-box">
                No common time slots found yet. Add your weekly study hours on
                the right to synchronize!
              </div>
            )}
          </div>

          {/* Right: My Study Availability */}
          <div className="my-availability-panel">
            <h4>🗓️ My Weekly Availability</h4>
            <form onSubmit={handleAddSchedule} className="add-schedule-form">
              <div className="schedule-form-row">
                <select
                  value={newDay}
                  onChange={(e) => setNewDay(e.target.value)}
                  className="search-input"
                >
                  <option value="Monday">Monday</option>
                  <option value="Tuesday">Tuesday</option>
                  <option value="Wednesday">Wednesday</option>
                  <option value="Thursday">Thursday</option>
                  <option value="Friday">Friday</option>
                  <option value="Saturday">Saturday</option>
                  <option value="Sunday">Sunday</option>
                </select>

                <input
                  type="time"
                  value={newStart}
                  onChange={(e) => setNewStart(e.target.value)}
                  className="search-input"
                  required
                />

                <input
                  type="time"
                  value={newEnd}
                  onChange={(e) => setNewEnd(e.target.value)}
                  className="search-input"
                  required
                />

                <button
                  type="submit"
                  className="action-btn-primary btn-sm"
                  disabled={savingSchedule}
                >
                  {savingSchedule ? "+" : "+ Add Slot"}
                </button>
              </div>
            </form>

            <div className="slots-chips-wrap">
              {mySchedules.length > 0 ? (
                mySchedules.map((s) => (
                  <div key={s.id} className="schedule-slot-chip">
                    <span>
                      {s.day_of_week} ({s.start_time} - {s.end_time})
                    </span>
                    <button
                      className="delete-slot-btn"
                      onClick={() => handleDeleteSchedule(s.id)}
                      title="Remove slot"
                    >
                      &times;
                    </button>
                  </div>
                ))
              ) : (
                <p className="empty-subtext">No study slots added yet.</p>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default StudyGroups;
