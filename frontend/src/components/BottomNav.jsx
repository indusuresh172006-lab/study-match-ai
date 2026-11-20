import { NavLink } from "react-router-dom";

function BottomNav({ user }) {
  const isTeacher = user?.role === "teacher";

  const navItems = isTeacher
    ? [
        { to: "/dashboard", label: "Dashboard", icon: "📊" },
        { to: "/materials", label: "Notes", icon: "📚" },
        { to: "/videos", label: "Videos", icon: "▶️" },
        { to: "/mock-tests", label: "Tests", icon: "📝" },
        { to: "/teacher/manage", label: "Manage", icon: "🛠️" },
        { to: "/teacher", label: "Teacher", icon: "👨‍🏫" },
      ]
    : [
        { to: "/dashboard", label: "Dashboard", icon: "📊" },
        { to: "/quiz", label: "Quizzes", icon: "🎯" },
        { to: "/mentor", label: "AI Mentor", icon: "🤖" },
        { to: "/groups", label: "Groups", icon: "👥" },
        { to: "/profile", label: "Profile", icon: "👤" },
      ];

  return (
    <nav className="mobile-bottom-nav">
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `bottom-nav-item ${isActive ? "active" : ""}`
          }
        >
          <span className="bottom-nav-icon">{item.icon}</span>
          <span className="bottom-nav-label">{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}

export default BottomNav;
