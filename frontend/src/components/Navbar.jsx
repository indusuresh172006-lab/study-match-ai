function Navbar({ user, onLogout }) {
  return (
    <header className="app-navbar">
      <div className="navbar-brand">
        <img className="brand-logo" src="/flint-logo.jpeg" alt="FLINT education logo" />
        <div className="brand-titles">
          <h1>StudyMatch AI</h1>
          <span className="brand-tagline">Peer-Learning & Academic Guidance</span>
        </div>
      </div>

      <div className="navbar-actions">
        {user && (
          <div className="user-profile-badge">
            <span className="user-avatar">{user.name ? user.name.charAt(0).toUpperCase() : "U"}</span>
            <div className="user-info-text">
              <span className="user-name">{user.name}</span>
              <span className={`role-pill ${user.role}`}>{user.role.toUpperCase()}</span>
            </div>
            <button className="logout-btn" onClick={onLogout} title="Sign out">
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
}

export default Navbar;
