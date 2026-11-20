import { NavLink } from "react-router-dom";

function BottomNav({ user }) {
  const isTeacher = user?.role === "teacher";

  const navItems = [
    { to: "/dashboard", label: "Dashboard", icon: "📊" },
    { to: "/materials", label: "Notes", icon: "📚" },
    { to: "/videos", label: "Videos", icon: "▶️" },
    { to: "/mock-tests", label: "Tests", icon: "📝" },
    { to: "/mentor", label: "AI Mentor", icon: "🤖" },
    { to: "/papers", label: "Papers", icon: "📄" },
  ];

  if (!isTeacher) {
    navItems.push({ to: "/profile", label: "Profile", icon: "👤" });
  }

  if (isTeacher) {
    navItems[4] = { to: "/teacher/manage", label: "Manage", icon: "🛠️" };
    navItems[5] = { to: "/teacher", label: "Teacher", icon: "👨‍🏫" };
  }

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
