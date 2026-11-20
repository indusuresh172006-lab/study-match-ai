import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";

function StudyMaterials({ user }) {
  const [searchParams] = useSearchParams();
  const initialSearch = searchParams.get("search") || "";

  const [materials, setMaterials] = useState([]);
  const [materialSubjects, setMaterialSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [subject, setSubject] = useState("All");
  const [materialType, setMaterialType] = useState("All");
  const [search, setSearch] = useState(initialSearch);
  const [bookmarkedOnly, setBookmarkedOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Reader Modal State
  const [activeMaterial, setActiveMaterial] = useState(null);

  // Teacher Upload Modal State
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFormData, setUploadFormData] = useState({
    title: "",
    subject: "",
    topic: "",
    course: "",
    curriculum: "",
    academic_year: "",
    material_type: "notes",
    difficulty_level: "medium",
    summary: "",
    content: "",
  });
  const [uploading, setUploading] = useState(false);

  const fetchMaterials = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        limit: 9,
        bookmarked_only: bookmarkedOnly,
      };
      if (subject !== "All") params.subject = subject;
      if (materialType !== "All") params.material_type = materialType;
      if (search.trim()) params.search = search.trim();

      const res = await api.get("/materials", { params });
      setMaterials(res.data.items);
      setTotalPages(res.data.pages);
    } catch (err) {
      console.error(err);
      setError("Failed to load study materials. Please check your connection.");
    } finally {
      setLoading(false);
    }
  };

  const fetchMaterialSubjects = async () => {
    try {
      const res = await api.get("/materials/subjects");
      setMaterialSubjects(res.data || []);
    } catch (err) {
      console.error("Could not load material subjects:", err);
    }
  };

  useEffect(() => {
    fetchMaterials();
  }, [subject, materialType, bookmarkedOnly, page]);

  useEffect(() => {
    fetchMaterialSubjects();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchMaterials();
  };

  const handleToggleBookmark = async (id, e) => {
    e.stopPropagation();
    try {
      const res = await api.post(`/materials/${id}/bookmark`);
      const isBookmarked = res.data.bookmarked;
      setMaterials((prev) =>
        prev.map((m) => (m.id === id ? { ...m, is_bookmarked: isBookmarked } : m))
      );
      if (activeMaterial && activeMaterial.id === id) {
        setActiveMaterial((prev) => ({ ...prev, is_bookmarked: isBookmarked }));
      }
    } catch (err) {
      console.error("Bookmark toggle failed", err);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);
    try {
      await api.post("/materials", uploadFormData);
      setShowUploadModal(false);
      setUploadFormData({
        title: "",
        subject: "",
        topic: "",
        course: "",
        curriculum: "",
        academic_year: "",
        material_type: "notes",
        difficulty_level: "medium",
        summary: "",
        content: "",
      });
      await Promise.all([fetchMaterials(), fetchMaterialSubjects()]);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to upload study material");
    } finally {
      setUploading(false);
    }
  };

  const isTeacher = user?.role === "teacher";

  return (
    <div className="study-materials-page">
      {/* Header and Teacher Actions */}
      <div className="page-header-row">
        <div>
          <h2>📚 Study Materials & Resources</h2>
          <p className="page-subtitle">
            Comprehensive notes, high-yield questions, and revision guides. Weak-topic resources are prioritized.
          </p>
        </div>
        {isTeacher && (
          <button
            className="action-btn-primary"
            onClick={() => setShowUploadModal(true)}
          >
            + Upload New Material
          </button>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div className="materials-filter-bar">
        {/* Subject Tabs */}
        <div className="subject-tabs">
          {["All", ...materialSubjects].map((subj) => (
            <button
              key={subj}
              className={`tab-btn ${subject === subj ? "active" : ""}`}
              onClick={() => {
                setSubject(subj);
                setPage(1);
              }}
            >
              {subj}
            </button>
          ))}
        </div>

        {/* Search & Secondary Filters */}
        <div className="filter-controls-row">
          <form onSubmit={handleSearchSubmit} className="search-form">
            <input
              type="text"
              placeholder="Search by title, topic or keyword..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="search-input"
            />
            <button type="submit" className="search-btn">
              🔍 Search
            </button>
          </form>

          <select
            value={materialType}
            onChange={(e) => {
              setMaterialType(e.target.value);
              setPage(1);
            }}
            className="filter-select"
          >
            <option value="All">All Material Types</option>
            <option value="notes">Notes</option>
            <option value="learning_material">Learning Materials</option>
            <option value="important_questions">Important Questions</option>
            <option value="topic_resource">Topic Resources</option>
          </select>

          <label className="bookmark-toggle-label">
            <input
              type="checkbox"
              checked={bookmarkedOnly}
              onChange={(e) => {
                setBookmarkedOnly(e.target.checked);
                setPage(1);
              }}
            />
            ⭐ Bookmarked Only
          </label>
        </div>
      </div>

      {/* Materials List / Grid */}
      {loading ? (
        <LoadingSpinner message="Retrieving study materials..." />
      ) : error ? (
        <ErrorMessage error={error} onRetry={fetchMaterials} />
      ) : materials.length === 0 ? (
        <EmptyState
          icon="📂"
          title={user?.role === "student" ? "No course-matched materials yet" : "No materials match your filters"}
          message={user?.role === "student"
            ? "Materials are filtered by your registered course, institution, and year/semester. Ask your teacher to publish resources for your syllabus."
            : "Try adjusting your subject selection or clearing search keywords."}
          actionText="Reset Filters"
          onAction={() => {
            setSubject("All");
            setMaterialType("All");
            setSearch("");
            setBookmarkedOnly(false);
            setPage(1);
          }}
        />
      ) : (
        <>
          <div className="materials-grid">
            {materials.map((mat) => (
              <div
                key={mat.id}
                className={`material-card ${mat.is_weak_topic ? "weak-highlight" : ""}`}
                onClick={() => setActiveMaterial(mat)}
              >
                <div className="mat-card-header">
                  <div className="header-tags">
                    <span className="subject-pill">{mat.subject}</span>
                    <span className="type-pill">{mat.material_type.replace("_", " ")}</span>
                    {mat.is_weak_topic && (
                      <span className="weak-topic-flag">⚠️ Weak Topic Priority</span>
                    )}
                  </div>
                  <button
                    className={`bookmark-icon-btn ${mat.is_bookmarked ? "bookmarked" : ""}`}
                    onClick={(e) => handleToggleBookmark(mat.id, e)}
                    title={mat.is_bookmarked ? "Remove bookmark" : "Save bookmark"}
                  >
                    {mat.is_bookmarked ? "★" : "☆"}
                  </button>
                </div>

                <h3 className="mat-title">{mat.title}</h3>
                <p className="mat-summary">{mat.summary || mat.content.substring(0, 140) + "..."}</p>

                <div className="mat-card-footer">
                  <span className="topic-indicator">📌 {mat.topic}</span>
                  <button className="read-material-btn">Read Notes →</button>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination-row">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="page-nav-btn"
              >
                ← Previous
              </button>
              <span className="page-indicator">
                Page {page} of {totalPages}
              </span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="page-nav-btn"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}

      {/* Reader Modal */}
      {activeMaterial && (
        <div className="modal-backdrop" onClick={() => setActiveMaterial(null)}>
          <div className="reader-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-topbar">
              <div className="topbar-info">
                <span className="subject-pill">{activeMaterial.subject}</span>
                <span className="topic-indicator">📌 {activeMaterial.topic}</span>
                {activeMaterial.is_weak_topic && (
                  <span className="weak-topic-flag">⚠️ Weak Topic Focus</span>
                )}
              </div>
              <div className="modal-top-actions">
                <button
                  className={`modal-bookmark-btn ${activeMaterial.is_bookmarked ? "bookmarked" : ""}`}
                  onClick={(e) => handleToggleBookmark(activeMaterial.id, e)}
                >
                  {activeMaterial.is_bookmarked ? "★ Bookmarked" : "☆ Save"}
                </button>
                <button
                  className="modal-close-btn"
                  onClick={() => setActiveMaterial(null)}
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="reader-body">
              <h1 className="reader-title">{activeMaterial.title}</h1>
              {activeMaterial.summary && (
                <div className="reader-summary-box">
                  <strong>Key Takeaway:</strong> {activeMaterial.summary}
                </div>
              )}
              <div className="reader-markdown">
                <pre className="content-pre">{activeMaterial.content}</pre>
              </div>
            </div>

            <div className="reader-footer">
              <button
                className="action-btn-secondary"
                onClick={() => setActiveMaterial(null)}
              >
                Close Reader
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Teacher Upload Material Modal */}
      {showUploadModal && (
        <div className="modal-backdrop" onClick={() => setShowUploadModal(false)}>
          <div className="form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-topbar">
              <h3>Upload Study Material</h3>
              <button
                className="modal-close-btn"
                onClick={() => setShowUploadModal(false)}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="upload-form">
              <label>Title *</label>
              <input
                type="text"
                required
                value={uploadFormData.title}
                onChange={(e) =>
                  setUploadFormData({ ...uploadFormData, title: e.target.value })
                }
                placeholder="e.g. Master Guide to Mendelian Genetics"
              />

              <div className="form-row">
                <div className="form-col">
                  <label>Subject *</label>
                  <input
                    list="study-material-subject-options"
                    value={uploadFormData.subject}
                    onChange={(e) =>
                      setUploadFormData({ ...uploadFormData, subject: e.target.value })
                    }
                    placeholder="e.g. Applied Mathematics"
                    required
                  />
                  <datalist id="study-material-subject-options">
                    {Array.from(new Set(["Biology", "Mathematics", "Computer Science", ...materialSubjects])).map((subj) => (
                      <option key={subj} value={subj} />
                    ))}
                  </datalist>
                </div>
                <div className="form-col">
                  <label>Topic *</label>
                  <input
                    type="text"
                    required
                    value={uploadFormData.topic}
                    onChange={(e) =>
                      setUploadFormData({ ...uploadFormData, topic: e.target.value })
                    }
                    placeholder="e.g. Genetics & DNA"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-col">
                  <label>Course / Program (exact registration value) *</label>
                  <input
                    type="text"
                    value={uploadFormData.course}
                    onChange={(e) => setUploadFormData({ ...uploadFormData, course: e.target.value })}
                    maxLength={100}
                    required
                  />
                </div>
                <div className="form-col">
                  <label>Board / Institution (exact) *</label>
                  <input
                    type="text"
                    value={uploadFormData.curriculum}
                    onChange={(e) => setUploadFormData({ ...uploadFormData, curriculum: e.target.value })}
                    maxLength={150}
                    required
                  />
                </div>
                <div className="form-col">
                  <label>Year / Semester (exact) *</label>
                  <input
                    type="text"
                    value={uploadFormData.academic_year}
                    onChange={(e) => setUploadFormData({ ...uploadFormData, academic_year: e.target.value })}
                    maxLength={20}
                    required
                  />
                </div>
              </div>
              <p className="upload-scope-help">
                Students see this resource only when all three course details match their registration.
              </p>

              <div className="form-row">
                <div className="form-col">
                  <label>Material Type *</label>
                  <select
                    value={uploadFormData.material_type}
                    onChange={(e) =>
                      setUploadFormData({
                        ...uploadFormData,
                        material_type: e.target.value,
                      })
                    }
                  >
                    <option value="notes">Notes</option>
                    <option value="learning_material">Learning Material</option>
                    <option value="important_questions">Important Questions</option>
                    <option value="topic_resource">Topic Resource</option>
                  </select>
                </div>
                <div className="form-col">
                  <label>Difficulty</label>
                  <select
                    value={uploadFormData.difficulty_level}
                    onChange={(e) =>
                      setUploadFormData({
                        ...uploadFormData,
                        difficulty_level: e.target.value,
                      })
                    }
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="difficult">Difficult</option>
                  </select>
                </div>
              </div>

              <label>Summary / Overview</label>
              <input
                type="text"
                value={uploadFormData.summary}
                onChange={(e) =>
                  setUploadFormData({ ...uploadFormData, summary: e.target.value })
                }
                placeholder="Brief high-level summary..."
              />

              <label>Full Content (Markdown supported) *</label>
              <textarea
                rows={8}
                required
                value={uploadFormData.content}
                onChange={(e) =>
                  setUploadFormData({ ...uploadFormData, content: e.target.value })
                }
                placeholder="Write full study notes, formulas, and examples..."
              />

              <div className="form-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => setShowUploadModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="submit-btn"
                  disabled={uploading}
                >
                  {uploading ? "Publishing..." : "Publish Material"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default StudyMaterials;
