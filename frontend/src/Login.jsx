import { useState } from "react";
import api from "./api";

function Login({ onLogin, onSwitchToRegister }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setMessage("");
    setLoading(true);

    try {
      const response = await api.post("/login", {
        email: email.trim(),
        password: password,
      });

      const userData = response.data;
      localStorage.setItem("studymatch_token", userData.access_token);
      localStorage.setItem(
        "studymatch_user",
        JSON.stringify({
          id: userData.student_id,
          name: userData.name,
          email: userData.email,
          role: userData.role,
        })
      );

      onLogin(userData);
    } catch (error) {
      setMessage(
        error.response?.data?.detail || "Login failed. Check your email and password."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-split-card">
      {/* LEFT SECTION – 45% WIDTH */}
      <div className="login-left-section">
        <div className="login-brand-header">
          <img
            className="login-flint-logo"
            src="/flint-logo.jpeg"
            alt="FLINT logo"
          />
          <p className="login-brand-subtitle">
            Sign in to your learning dashboard
          </p>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          <div className="login-field-group">
            <label className="login-field-label">Email Address</label>
            <div className="login-input-wrapper">
              <span className="login-input-icon left">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <rect x="2" y="4" width="20" height="16" rx="2" />
                  <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                </svg>
              </span>
              <input
                type="email"
                className="login-text-input"
                placeholder="alan@gmail.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>
          </div>

          <div className="login-field-group">
            <label className="login-field-label">Password</label>
            <div className="login-input-wrapper">
              <span className="login-input-icon left">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
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
                autoComplete="current-password"
              />
              <button
                type="button"
                className="login-password-toggle-btn"
                onClick={() => setShowPassword(!showPassword)}
                title={showPassword ? "Hide password" : "Show password"}
                tabIndex="-1"
              >
                {showPassword ? (
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                    <line x1="1" y1="1" x2="23" y2="23" />
                  </svg>
                ) : (
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          {message && (
            <div className="login-error-alert" role="alert">
              <span>⚠️</span> {message}
            </div>
          )}

          <button
            type="submit"
            className="login-submit-button"
            disabled={loading}
          >
            {loading ? "Signing in..." : "Sign In →"}
          </button>

          <div className="login-divider-row">
            <span className="login-divider-line"></span>
            <span className="login-footer-text">
              Don't have an account?{" "}
              <button
                type="button"
                className="login-register-link-btn"
                onClick={onSwitchToRegister}
              >
                Register here
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

export default Login;
