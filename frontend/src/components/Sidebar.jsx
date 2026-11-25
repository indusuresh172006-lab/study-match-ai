import { NavLink, useLocation } from "react-router-dom";

function Sidebar({ user, mobileOpen, onClose }) {
  const location = useLocation();
  const isTeacher = user?.role === "teacher";
  const isAdmin = user?.role === "admin";
  const isStaff = isTeacher || isAdmin;

  const studentNavItems = [
    { to: "/dashboard", label: "Dashboard", icon: "📊" },
    { to: "/quiz", label: "Topic Quiz", icon: "🎯" },
    { to: "/groups", label: "Study Groups", icon: "👥" },
    { to: "/materials", label: "Study Materials", icon: "📚" },
    { to: "/videos", label: "Course Videos", icon: "▶️" },
    { to: "/guidance", label: "Course Guidance", icon: "🎓" },
    { to: "/mentor", label: "AI Mentor", icon: "🤖" },
    { to: "/mock-tests", label: "Mock Tests", icon: "📝" },
    { to: "/summaries", label: "Course Summaries", icon: "📖" },
    { to: "/papers", label: "Previous Papers", icon: "📄" },
  ];

  const teacherNavItems = [
    { to: "/teacher", label: "Dashboard", icon: "📊", end: true },
    { to: "/teacher/classes", label: "Classes & Marks", icon: "🏫" },
    { to: "/teacher/curriculum", label: "Subjects & Topics", icon: "📚" },
    { to: "/teacher/quizzes", label: "Quiz Questions", icon: "🎯" },
    { to: "/teacher/groups", label: "Study Groups", icon: "👥" },
    { to: "/teacher/counselling", label: "Counselling Requests", icon: "🤝" },
    { to: "/teacher/revision-notes", label: "AI Revision Review", icon: "🧠" },
    { to: "/papers", label: "Question Papers", icon: "📄" },
    { to: "/materials", label: "Study Materials", icon: "📖" },
    { to: "/mentor", label: "AI Mentor", icon: "🤖" },
  ];

  const adminNavItems = [
    { to: "/admin", label: "Dashboard", icon: "📊" },
    { to: "/admin/manage/teacher-requests", label: "Teacher Requests", icon: "👨‍🏫" },
    { to: "/admin/manage/accounts", label: "Accounts", icon: "👥" },
    { to: "/admin/manage/classes", label: "Classes", icon: "🏫" },
    { to: "/admin/manage/content", label: "Content Management", icon: "🛠️" },
  ];

  const navItems = isAdmin
    ? adminNavItems
    : isTeacher
    ? teacherNavItems
    : (() => {
        const items = [...studentNavItems];
        items.splice(1, 0, { to: "/profile", label: "My Profile", icon: "👤" });
        return items;
      })();

  return (
    <>
      {!isStaff && mobileOpen && (
        <button
          className="mobile-sidebar-backdrop"
          type="button"
          aria-label="Close navigation menu"
          onClick={onClose}
        />
      )}
      <aside
        id={!isStaff ? "student-mobile-sidebar" : undefined}
        className={`app-sidebar ${!isStaff ? "student-mobile-sidebar" : ""} ${mobileOpen && !isStaff ? "mobile-open" : ""}`}
      >
        <div className="sidebar-top">
          <div className="sidebar-menu-heading">NAVIGATION</div>
          <nav className="sidebar-nav">
            {navItems.map((item) => {
              const isItemActive = item.end || item.to === "/teacher" || item.to === "/admin" || item.to === "/dashboard"
                ? location.pathname === item.to
                : location.pathname.startsWith(item.to);

              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={onClose}
                  className={`sidebar-link ${isItemActive ? "active" : ""}`}
                >
                  <span className="sidebar-icon">{item.icon}</span>
                  <span className="sidebar-label">{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        <div className="sidebar-footer">
          {isTeacher ? (
            <div className="sidebar-tip">
              <span className="tip-title">👨‍🏫 Module 1 Tip</span>
              <p>Manage scoped classes, topic-tagged CSV marks, syllabus topics, and quiz questions.</p>
            </div>
          ) : isAdmin ? (
            <div className="sidebar-tip">
              <span className="tip-title">🛡️ Admin Tip</span>
              <p>Approve pending teacher requests and oversee platform institutions.</p>
            </div>
          ) : (
            <div className="sidebar-tip">
              <span className="tip-title">💡 Study Tip</span>
              <p>Mock tests update your Skill Profile and recommend targeted materials.</p>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
