import { useEffect, useMemo, useState } from "react";
import api from "../api";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import LoadingSpinner from "../components/LoadingSpinner";

function buildYouTubeSearchUrl(course, semester, topic) {
  const query = [course, semester, topic].filter(Boolean).join(" ");
  return `https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`;
}

function CourseVideos() {
  const [profile, setProfile] = useState(null);
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    let active = true;

    const loadProfile = async () => {
      try {
        const response = await api.get("/profile/me");
        if (active) setProfile(response.data || null);
      } catch (err) {
        console.error("Could not load course profile for videos:", err);
        if (active) setError("Could not load your course details. Check your connection and try again.");
      } finally {
        if (active) setLoading(false);
      }
    };

    loadProfile();
    return () => {
      active = false;
    };
  }, [retryCount]);

  const suggestedTopics = useMemo(() => {
    const course = profile?.course?.trim();
    if (!course) return [];

    if (/computer|software|web|information technology|\bit\b|bca/i.test(course)) {
      return ["Web Development", "HTML & CSS", "JavaScript", "Database Management"];
    }

    return [
      `${course} syllabus`,
      `${course} practical lessons`,
      `${course} exam preparation`,
    ];
  }, [profile?.course]);

  const handleSearch = (event) => {
    event.preventDefault();
    const course = profile?.course?.trim();
    const searchTopic = topic.trim();
    if (!course || !searchTopic) return;

    window.open(
      buildYouTubeSearchUrl(course, profile.semester, searchTopic),
      "_blank",
      "noopener,noreferrer"
    );
  };

  const handleRetry = () => {
    setError(null);
    setLoading(true);
    setRetryCount((count) => count + 1);
  };

  const course = profile?.course?.trim();

  return (
    <div className="course-videos-page">
      <div className="page-header-row">
        <div>
          <h2>Course Videos</h2>
          <p className="page-subtitle">
            Find YouTube lessons related to your current course and topics.
          </p>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Loading your course details..." />
      ) : error ? (
        <ErrorMessage error={error} onRetry={handleRetry} />
      ) : !course ? (
        <EmptyState
          icon="📺"
          title="Add your current course"
          message="Course videos are matched to your registered course. Complete your course details to see relevant YouTube searches."
        />
      ) : (
        <>
          <section className="course-video-context">
            <div>
              <span className="course-video-eyebrow">VIDEOS FOR YOUR COURSE</span>
              <h3>{course}</h3>
              {profile.semester && <p>{profile.semester}</p>}
            </div>
            <span className="course-video-live-badge">YouTube search</span>
          </section>

          <section className="course-video-search-panel">
            <h3>Search a course topic</h3>
            <p>Results open on YouTube and update with its latest available videos.</p>
            <form className="course-video-search-form" onSubmit={handleSearch}>
              <label htmlFor="course-video-topic">Topic</label>
              <input
                id="course-video-topic"
                type="search"
                value={topic}
                onChange={(event) => setTopic(event.target.value)}
                placeholder="For example, Web Development"
                required
              />
              <button className="action-btn-primary" type="submit">
                Search YouTube
              </button>
            </form>
          </section>

          <section className="course-video-suggestions">
            <div className="course-video-section-heading">
              <h3>Suggested topics</h3>
              <p>Search suggestions based on {course}.</p>
            </div>
            <div className="course-video-topics-grid">
              {suggestedTopics.map((suggestedTopic) => (
                <a
                  className="course-video-topic-card"
                  href={buildYouTubeSearchUrl(course, profile.semester, suggestedTopic)}
                  key={suggestedTopic}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <span className="course-video-topic-icon" aria-hidden="true">▶</span>
                  <strong>{suggestedTopic}</strong>
                  <span className="course-video-topic-link">View videos on YouTube ↗</span>
                </a>
              ))}
            </div>
            <p className="course-video-disclaimer">
              YouTube search results are external. Review each video’s content and source before studying.
            </p>
          </section>
        </>
      )}
    </div>
  );
}

export default CourseVideos;
