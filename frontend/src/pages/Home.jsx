import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Home.css";

function Home({ user, onLogout }) {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleNavClick = (e, targetId) => {
    e.preventDefault();
    setMobileMenuOpen(false);
    const element = document.getElementById(targetId);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleSignIn = () => {
    if (user) {
      if (user.role === "admin") navigate("/admin");
      else if (user.role === "teacher") navigate("/teacher");
      else navigate("/dashboard");
    } else {
      navigate("/login");
    }
  };

  const handleGetStarted = () => {
    if (user) {
      if (user.role === "admin") navigate("/admin");
      else if (user.role === "teacher") navigate("/teacher");
      else navigate("/dashboard");
    } else {
      navigate("/register");
    }
  };

  return (
    <div className="flint-home-wrapper" id="home">
      {/* =========================================================================
          NAVIGATION HEADER
          ========================================================================= */}
      <header className={`flint-header ${scrolled ? "is-scrolled" : ""}`}>
        <div className="flint-header-container">
          {/* Brand Logo */}
          <a href="#home" className="flint-logo-link" onClick={(e) => handleNavClick(e, "home")}>
            <img className="flint-nav-logo-img" src="/flint-logo.jpeg" alt="FLINT Logo" />
            <span className="flint-brand-text">FLINT</span>
          </a>

          {/* Desktop Nav Links */}
          <nav className="flint-desktop-nav">
            <a href="#home" onClick={(e) => handleNavClick(e, "home")} className="flint-nav-link active">
              Home
            </a>
            <a href="#about" onClick={(e) => handleNavClick(e, "about")} className="flint-nav-link">
              About Us
            </a>
            <a href="#courses" onClick={(e) => handleNavClick(e, "courses")} className="flint-nav-link">
              Courses
            </a>
            <a href="#features" onClick={(e) => handleNavClick(e, "features")} className="flint-nav-link">
              Features
            </a>
            <a href="#how-it-works" onClick={(e) => handleNavClick(e, "how-it-works")} className="flint-nav-link">
              How It Works
            </a>
            <a href="#contact" onClick={(e) => handleNavClick(e, "contact")} className="flint-nav-link">
              Contact
            </a>
          </nav>

          {/* Header Action Buttons */}
          <div className="flint-header-actions">
            <button type="button" className="flint-btn-signin" onClick={handleSignIn}>
              {user ? "Dashboard" : "Sign In"}
            </button>
            <button type="button" className="flint-btn-getstarted" onClick={handleGetStarted}>
              Get Started
            </button>
            <button
              type="button"
              className="flint-user-icon-btn"
              onClick={handleSignIn}
              title={user ? `Signed in as ${user.name}` : "User Profile / Login"}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </button>
            {/* Mobile Hamburger Toggle */}
            <button
              type="button"
              className="flint-hamburger-btn"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle menu"
            >
              <span className={`bar ${mobileMenuOpen ? "open" : ""}`}></span>
              <span className={`bar ${mobileMenuOpen ? "open" : ""}`}></span>
              <span className={`bar ${mobileMenuOpen ? "open" : ""}`}></span>
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="flint-mobile-dropdown">
            <a href="#home" onClick={(e) => handleNavClick(e, "home")}>Home</a>
            <a href="#about" onClick={(e) => handleNavClick(e, "about")}>About Us</a>
            <a href="#courses" onClick={(e) => handleNavClick(e, "courses")}>Courses</a>
            <a href="#features" onClick={(e) => handleNavClick(e, "features")}>Features</a>
            <a href="#how-it-works" onClick={(e) => handleNavClick(e, "how-it-works")}>How It Works</a>
            <a href="#contact" onClick={(e) => handleNavClick(e, "contact")}>Contact</a>
            <div className="flint-mobile-actions">
              <button type="button" className="flint-btn-signin" onClick={handleSignIn}>
                {user ? "Dashboard" : "Sign In"}
              </button>
              <button type="button" className="flint-btn-getstarted" onClick={handleGetStarted}>
                Get Started
              </button>
            </div>
          </div>
        )}
      </header>

      {/* =========================================================================
          1. HERO SECTION
          ========================================================================= */}
      <section className="flint-hero-section">
        <div className="flint-hero-container">
          {/* Left Column: Headline and CTAs */}
          <div className="flint-hero-left">
            <div className="flint-pill-badge">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" />
              </svg>
              <span>WELCOME TO FLINT</span>
            </div>

            <h1 className="flint-hero-headline">
              <span className="dark-text">Learn Today.</span>
              <span className="teal-text">Lead Tomorrow.</span>
            </h1>

            <p className="flint-hero-subtext">
              Discover a smarter way to learn, practice, and grow. FLINT brings your
              learning journey together in one simple platform with structured pathways
              and intuitive scholarly clarity.
            </p>

            <div className="flint-hero-cta-group">
              <button
                type="button"
                className="flint-hero-btn-primary"
                onClick={(e) => handleNavClick(e, "courses")}
              >
                <span>Explore Courses</span>
              </button>
              <button
                type="button"
                className="flint-hero-btn-secondary"
                onClick={handleGetStarted}
              >
                <span>Get Started</span>
              </button>
            </div>

            <div className="flint-hero-guarantee">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <circle cx="12" cy="12" r="10" />
                <path d="m9 12 2 2 4-4" />
              </svg>
              <span>Your learning journey starts here. Free instant access.</span>
            </div>
          </div>

          {/* Right Column: Floating Scholar Card */}
          <div className="flint-hero-right">
            <div className="flint-scholar-card">
              {/* Card Header: Avatars + Rating */}
              <div className="flint-card-top-bar">
                <div className="flint-avatars-group">
                  <div className="flint-avatar-pill-stack">
                    <span className="flint-avatar-bubble dark">AK</span>
                    <span className="flint-avatar-bubble teal">MS</span>
                    <span className="flint-avatar-bubble deep">RL</span>
                  </div>
                  <span className="flint-scholar-count">14,200+ Active Scholars</span>
                </div>
                <div className="flint-rating-badge">
                  <span className="star-icon">★</span>
                  <span>4.9+ Rating</span>
                </div>
              </div>

              {/* Photo Area with Bottom Overlay */}
              <div className="flint-hero-photo-wrap">
                <img
                  src="/hero-students.png"
                  alt="Scholars collaborating with laptops and tablets"
                  className="flint-hero-photo"
                />
              </div>

              {/* Bottom Dual Stats */}
              <div className="flint-dual-stats-grid">
                <div className="flint-stat-box">
                  <div className="flint-stat-header">
                    <span className="stat-label">CURRICULUM</span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                      <path d="m9 12 2 2 4-4" />
                    </svg>
                  </div>
                  <div className="flint-stat-number">98%</div>
                  <div className="flint-stat-desc">Completion Rate</div>
                </div>

                <div className="flint-stat-box">
                  <div className="flint-stat-header">
                    <span className="stat-label">STATUS</span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                      <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
                      <polyline points="16 7 22 7 22 13" />
                    </svg>
                  </div>
                  <div className="flint-stat-number">18 Tracks</div>
                  <div className="flint-stat-desc">Structured Pathways</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          2. ABOUT FLINT SECTION
          ========================================================================= */}
      <section className="flint-section flint-about-section" id="about">
        <div className="flint-container">
          <div className="flint-section-header-center">
            <div className="flint-pill-badge">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                <path d="M6 12v5c3 3 9 3 12 0v-5" />
              </svg>
              <span>ABOUT FLINT</span>
            </div>
            <h2 className="flint-section-heading">
              Learning Made Simple, Learning Made Smarter
            </h2>
            <p className="flint-section-subhead">
              FLINT is designed to make learning more organized, accessible, and effective.
              Explore learning materials, practice your knowledge, and track your educational
              journey in one place.
            </p>
          </div>

          <div className="flint-about-grid">
            {/* Card 1 */}
            <div className="flint-about-card">
              <div className="flint-card-icon-box">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
                  <path d="M6 6h10" />
                  <path d="M6 10h10" />
                </svg>
              </div>
              <h3 className="flint-card-title">Structured Learning</h3>
              <p className="flint-card-desc">
                Step-by-step modular curriculum structured for crystal-clear conceptual
                comprehension without the overwhelm. Follow linear progressions built by
                veteran educators.
              </p>

            </div>

            {/* Card 2 */}
            <div className="flint-about-card">
              <div className="flint-card-icon-box">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <rect x="3" y="3" width="18" height="18" rx="2" />
                  <circle cx="12" cy="10" r="3" />
                  <path d="M12 17v.01" />
                </svg>
              </div>
              <h3 className="flint-card-title">Interactive Practice</h3>
              <p className="flint-card-desc">
                Hands-on contextual quizzes, interactive mini-challenges, and real-time
                guided feedback to solidify retention as you complete every chapter.
              </p>

            </div>

            {/* Card 3 */}
            <div className="flint-about-card">
              <div className="flint-card-icon-box">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
                  <polyline points="16 7 22 7 22 13" />
                </svg>
              </div>
              <h3 className="flint-card-title">Continuous Improvement</h3>
              <p className="flint-card-desc">
                Personalized progress curves, milestone celebration badges, and adaptive
                skill reinforcement schedules that keep scholarly motivation high.
              </p>


            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          3. OUR LEARNING FEATURES SECTION
          ========================================================================= */}
      <section className="flint-section flint-features-section" id="features">
        <div className="flint-container">
          <div className="flint-features-header-split">
            <div className="flint-features-header-left">
              <div className="flint-pill-badge">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <circle cx="12" cy="12" r="10" />
                  <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
                </svg>
                <span>CORE CAPABILITIES</span>
              </div>
              <h2 className="flint-section-heading">Our Learning Features</h2>
            </div>
            <div className="flint-features-header-right">
              <p>
                Everything thoughtfully tailored to accelerate your learning speed,
                confidence, and long-term retention.
              </p>
            </div>
          </div>

          <div className="flint-features-grid">
            {/* Feature 1 */}
            <div className="flint-feature-card">
              <div className="flint-card-icon-box">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <rect x="3" y="3" width="7" height="7" />
                  <rect x="14" y="3" width="7" height="7" />
                  <rect x="14" y="14" width="7" height="7" />
                  <rect x="3" y="14" width="7" height="7" />
                </svg>
              </div>
              <h3 className="flint-card-title">Structured Modules</h3>
              <p className="flint-card-desc">
                Learn through organized topics and lessons with progressive depth that
                eliminates ambiguity.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="flint-feature-card">
              <div className="flint-card-icon-box">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <circle cx="12" cy="12" r="10" />
                  <polyline points="12 6 12 12 16 14" />
                </svg>
              </div>
              <h3 className="flint-card-title">Daily Learning</h3>
              <p className="flint-card-desc">
                Bite-sized daily cadences designed for sustainable momentum and zero
                cognitive exhaustion.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="flint-feature-card">
              <div className="flint-card-icon-box">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
                  <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
                  <path d="m9 14 2 2 4-4" />
                </svg>
              </div>
              <h3 className="flint-card-title">Practice & Quizzes</h3>
              <p className="flint-card-desc">
                Test your knowledge with interactive assessments and actionable cues that
                reinforce memory.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="flint-feature-card">
              <div className="flint-card-icon-box">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                  <path d="M3 3v5h5" />
                  <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
                  <path d="M16 21h5v-5" />
                </svg>
              </div>
              <h3 className="flint-card-title">Smart Revision</h3>
              <p className="flint-card-desc">
                Spaced repetition triggers to refresh memory before milestone assessments
                or industry reviews.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="flint-feature-card">
              <div className="flint-card-icon-box">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <line x1="18" x2="18" y1="20" y2="10" />
                  <line x1="12" x2="12" y1="20" y2="4" />
                  <line x1="6" x2="6" y1="20" y2="14" />
                </svg>
              </div>
              <h3 className="flint-card-title">Progress Tracking</h3>
              <p className="flint-card-desc">
                Visual retention curves and telemetry highlighting personal velocity and
                subject readiness.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="flint-feature-card">
              <div className="flint-card-icon-box">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <circle cx="12" cy="8" r="6" />
                  <path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11" />
                </svg>
              </div>
              <h3 className="flint-card-title">Achievements & Badges</h3>
              <p className="flint-card-desc">
                Micro-credentials, skill endorsements, and verified completion badges for
                public portfolios.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          4. EXPLORE WHAT YOU CAN LEARN (PROGRAM CATALOGUE)
          ========================================================================= */}
      <section className="flint-section flint-courses-section" id="courses">
        <div className="flint-container">
          <div className="flint-section-header-center">
            <div className="flint-pill-badge">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
              </svg>
              <span>PROGRAM CATALOGUE</span>
            </div>
            <h2 className="flint-section-heading">Explore What You Can Learn</h2>
            <p className="flint-section-subhead">
              Find the right curriculum pathway and start cultivating industry-standard
              capabilities today.
            </p>
          </div>

          <div className="flint-courses-grid">
            {/* Course Card 1 */}
            <div className="flint-course-card">
              <div className="flint-course-image-wrap">
                <img
                  src="/course-web.png"
                  alt="Full-Stack Web Engineering setup"
                  className="flint-course-img"
                />
                <span className="flint-course-category-tag">DEVELOPMENT</span>
              </div>
              <div className="flint-course-body">
                <div className="flint-course-meta">
                  <span className="meta-duration">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10" />
                      <polyline points="12 6 12 12 16 14" />
                    </svg>
                    <span>12 Weeks</span>
                  </span>
                  <span className="meta-level-pill">Beginner to Advanced</span>
                </div>
                <h3 className="flint-course-title">Full-Stack Web Engineering</h3>
                <p className="flint-course-desc">
                  Master modern responsive web architectures, API integration, and full
                  lifecycle production deployment on cloud foundations.
                </p>
                <button
                  type="button"
                  className="flint-course-btn"
                  onClick={handleGetStarted}
                >
                  <span>Explore Course</span>
                  <span>→</span>
                </button>
              </div>
            </div>

            {/* Course Card 2 */}
            <div className="flint-course-card">
              <div className="flint-course-image-wrap">
                <img
                  src="/course-data.png"
                  alt="Data Science & Applied Analytics visualization"
                  className="flint-course-img"
                />
                <span className="flint-course-category-tag">ANALYTICS</span>
              </div>
              <div className="flint-course-body">
                <div className="flint-course-meta">
                  <span className="meta-duration">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10" />
                      <polyline points="12 6 12 12 16 14" />
                    </svg>
                    <span>10 Weeks</span>
                  </span>
                  <span className="meta-level-pill">Intermediate</span>
                </div>
                <h3 className="flint-course-title">Data Science & Applied Analytics</h3>
                <p className="flint-course-desc">
                  Explore statistical workflows, predictive modeling, high-throughput
                  data manipulation pipelines, and automated reporting frameworks.
                </p>
                <button
                  type="button"
                  className="flint-course-btn"
                  onClick={handleGetStarted}
                >
                  <span>Explore Course</span>
                  <span>→</span>
                </button>
              </div>
            </div>

            {/* Course Card 3 */}
            <div className="flint-course-card">
              <div className="flint-course-image-wrap">
                <img
                  src="/course-ai.png"
                  alt="AI & Machine Learning neural visual"
                  className="flint-course-img"
                />
                <span className="flint-course-category-tag">ARTIFICIAL INTELLIGENCE</span>
              </div>
              <div className="flint-course-body">
                <div className="flint-course-meta">
                  <span className="meta-duration">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10" />
                      <polyline points="12 6 12 12 16 14" />
                    </svg>
                    <span>8 Weeks</span>
                  </span>
                  <span className="meta-level-pill">All Levels</span>
                </div>
                <h3 className="flint-course-title">AI & Machine Learning Foundations</h3>
                <p className="flint-course-desc">
                  Understand core machine learning algorithms, deep neural
                  representations, and practical generative prompt engineering workflows.
                </p>
                <button
                  type="button"
                  className="flint-course-btn"
                  onClick={handleGetStarted}
                >
                  <span>Explore Course</span>
                  <span>→</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          5. HOW FLINT WORKS SECTION
          ========================================================================= */}
      <section className="flint-section flint-how-it-works-section" id="how-it-works">
        <div className="flint-container">
          <div className="flint-section-header-center">
            <div className="flint-pill-badge">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
              </svg>
              <span>STEP-BY-STEP PROCESS</span>
            </div>
            <h2 className="flint-section-heading">How FLINT Works</h2>
            <p className="flint-section-subhead">
              A seamless 4-step path crafted to guide you from foundational curiosity to
              demonstrable skill mastery.
            </p>
          </div>

          <div className="flint-steps-grid">
            {/* Step 1 */}
            <div className="flint-step-card">
              <div className="flint-step-header">
                <span className="flint-step-number">01</span>
                <div className="flint-step-icon-bubble">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                    <circle cx="8.5" cy="7" r="4" />
                    <line x1="20" x2="20" y1="8" y2="14" />
                    <line x1="23" x2="17" y1="11" y2="11" />
                  </svg>
                </div>
              </div>
              <h3 className="flint-card-title">Create Your Account</h3>
              <p className="flint-card-desc">
                Quick frictionless setup to activate your personal learning dashboard
                and sync academic preferences.
              </p>
            </div>

            {/* Step 2 */}
            <div className="flint-step-card">
              <div className="flint-step-header">
                <span className="flint-step-number">02</span>
                <div className="flint-step-icon-bubble">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" x2="16.65" y1="21" y2="16.65" />
                  </svg>
                </div>
              </div>
              <h3 className="flint-card-title">Choose Your Course</h3>
              <p className="flint-card-desc">
                Browse comprehensive tracks or start with an adaptive diagnostic module
                to assess your exact level.
              </p>
            </div>

            {/* Step 3 */}
            <div className="flint-step-card">
              <div className="flint-step-header">
                <span className="flint-step-number">03</span>
                <div className="flint-step-icon-bubble">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                    <polyline points="16 18 22 12 16 6" />
                    <polyline points="8 6 2 12 8 18" />
                  </svg>
                </div>
              </div>
              <h3 className="flint-card-title">Learn & Practice</h3>
              <p className="flint-card-desc">
                Engage with multimedia lecture summaries, interactive test drills, and
                prompt real-world exercises.
              </p>
            </div>

            {/* Step 4 */}
            <div className="flint-step-card">
              <div className="flint-step-header">
                <span className="flint-step-number">04</span>
                <div className="flint-step-icon-bubble">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                    <circle cx="12" cy="8" r="6" />
                    <path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11" />
                  </svg>
                </div>
              </div>
              <h3 className="flint-card-title">Track Your Growth</h3>
              <p className="flint-card-desc">
                Inspect velocity analytics, earn digital credentials, and export
                verified accomplishment portfolios.
              </p>
            </div>
          </div>
        </div>
      </section>



      {/* =========================================================================
          8. CALL TO ACTION BANNER
          ========================================================================= */}
      <section className="flint-cta-section">
        <div className="flint-container">
          <div className="flint-cta-banner">
            <div className="flint-cta-decor-waves">
              <svg viewBox="0 0 1000 300" preserveAspectRatio="none">
                <path
                  d="M0,100 C150,200 350,0 500,100 C650,200 850,50 1000,120 L1000,300 L0,300 Z"
                  fill="rgba(255, 255, 255, 0.05)"
                />
                <path
                  d="M0,180 C200,80 400,240 600,160 C800,80 900,200 1000,170 L1000,300 L0,300 Z"
                  fill="rgba(255, 255, 255, 0.04)"
                />
              </svg>
            </div>

            <div className="flint-cta-content">
              <h2 className="flint-cta-title">Ready to Start Your Learning Journey?</h2>
              <p className="flint-cta-subtext">
                Take the next step towards mastering modern competencies and advancing
                your goals with FLINT today.
              </p>
              <button
                type="button"
                className="flint-cta-button"
                onClick={handleGetStarted}
              >
                <span>Get Started Today</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          9. FOOTER
          ========================================================================= */}
      <footer className="flint-footer" id="contact">
        <div className="flint-container">
          <div className="flint-footer-top-grid">
            {/* Column 1: Brand & Mission */}
            <div className="flint-footer-col brand-col">
              <a href="#home" className="flint-logo-link" onClick={(e) => handleNavClick(e, "home")}>
                <img className="flint-nav-logo-img" src="/flint-logo.jpeg" alt="FLINT Logo" />
                <span className="flint-brand-text">FLINT</span>
              </a>
              <p className="flint-footer-mission">
                Empowering curious minds through an academic yet luminous learning
                ecosystem designed for modern mastery and intuitive scholarly exploration.
              </p>
              <div className="flint-social-links-row">
                <button type="button" className="flint-social-btn" title="Global Network">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="2" x2="22" y1="12" y2="12" />
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                  </svg>
                </button>
                <button type="button" className="flint-social-btn" title="Contact Us">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="4" />
                    <path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-4 8" />
                  </svg>
                </button>
                <button type="button" className="flint-social-btn" title="Share FLINT">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="18" cy="5" r="3" />
                    <circle cx="6" cy="12" r="3" />
                    <circle cx="18" cy="19" r="3" />
                    <line x1="8.59" x2="15.42" y1="13.51" y2="17.49" />
                    <line x1="15.41" x2="8.59" y1="6.51" y2="10.49" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Column 2: Quick Navigation */}
            <div className="flint-footer-col nav-col">
              <h4 className="flint-footer-heading">Quick Navigation</h4>
              <ul className="flint-footer-nav-list">
                <li>
                  <a href="#courses" onClick={(e) => handleNavClick(e, "courses")}>Courses</a>
                </li>
                <li>
                  <a href="#about" onClick={(e) => handleNavClick(e, "about")}>About Us</a>
                </li>
                <li>
                  <a href="#contact" onClick={(e) => handleNavClick(e, "contact")}>Contact</a>
                </li>
                <li>
                  <a href="/login" onClick={(e) => { e.preventDefault(); handleSignIn(); }}>Sign In</a>
                </li>
              </ul>
            </div>

            {/* Column 3: Learning Redefined */}
            <div className="flint-footer-col info-col">
              <h4 className="flint-footer-heading">Learning Redefined</h4>
              <p className="flint-footer-redefined">
                Experience tailored syllabi, peer collaboration, and pedagogical clarity
                across all devices. Step into scholarly focus without clutter.
              </p>
              <div className="flint-accredited-badge">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <path d="m9 12 2 2 4-4" />
                </svg>
                <span>Accredited & Peer-Reviewed Curriculum</span>
              </div>
            </div>
          </div>

          {/* Bottom Copyright & Legal Links */}
          <div className="flint-footer-bottom-bar">
            <div className="flint-copyright">
              © 2025 FLINT Technologies, Inc. All rights reserved.
            </div>
            <div className="flint-legal-links">
              <a href="#privacy" onClick={(e) => e.preventDefault()}>Privacy Policy</a>
              <a href="#terms" onClick={(e) => e.preventDefault()}>Terms of Service</a>
              <a href="#cookies" onClick={(e) => e.preventDefault()}>Cookie Preferences</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Home;