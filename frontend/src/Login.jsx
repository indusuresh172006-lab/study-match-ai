import { useState } from "react";
import api from "./api";

function Login({ onLogin, onSwitchToRegister }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
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
      setMessage(error.response?.data?.detail || "Login failed. Check your email and password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-card">
      <div className="auth-brand-head">
        <img className="auth-logo" src="/flint-logo.jpeg" alt="FLINT education logo" />
        <h1>FLINT</h1>
        <p className="auth-subtitle">Sign in to your learning dashboard</p>
      </div>

      <form onSubmit={handleLogin} className="auth-form">
        <div className="form-field">
          <label>Email Address</label>
          <input
            type="email"
            placeholder="student@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className="form-field">
          <label>Password</label>
          <input
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button type="submit" className="auth-submit-btn" disabled={loading}>
          {loading ? "Signing in..." : "Sign In →"}
        </button>
      </form>

      {message && <div className="auth-error-msg">{message}</div>}

      <div className="auth-switch-footer">
        Don't have an account?{" "}
        <button type="button" className="link-button" onClick={onSwitchToRegister}>
          Register here
        </button>
      </div>
    </div>
  );
}

export default Login;
