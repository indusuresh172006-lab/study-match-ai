import { NavLink } from "react-router-dom";

const iconShapes = {
  dashboard: (
    <>
      <rect x="3" y="3" width="8" height="8" rx="1.5" />
      <rect x="13" y="3" width="8" height="5" rx="1.5" />
      <rect x="13" y="10" width="8" height="11" rx="1.5" />
      <rect x="3" y="13" width="8" height="8" rx="1.5" />
    </>
  ),
  quiz: (
    <>
      <rect x="5" y="4" width="14" height="17" rx="2" />
      <path d="M9 4V3h6v1M8.5 13l2.5 2.5 5-5" />
    </>
  ),
  mentor: (
    <>
      <path d="M20 11.5a7.5 7.5 0 0 1-7.5 7.5H6l-3 2v-5.5a7.5 7.5 0 1 1 17-4Z" />
      <path d="M8 11h.01M12 11h.01M16 11h.01" />
    </>
  ),
  groups: (
    <>
      <circle cx="9" cy="8" r="3" />
      <path d="M3.5 20v-1.5A5.5 5.5 0 0 1 9 13h1a5.5 5.5 0 0 1 5.5 5.5V20Z" />
      <path d="M16 4.5a3 3 0 0 1 0 6M17 13a5 5 0 0 1 3.5 4.8V20h-3" />
    </>
  ),
  profile: (
    <>
      <circle cx="12" cy="8" r="3.5" />
      <path d="M4.5 21a7.5 7.5 0 0 1 15 0" />
    </>
  ),
  notes: (
    <>
      <path d="M4 5.5c3-.6 5.7-.2 8 1.5 2.3-1.7 5-2.1 8-1.5v13c-3-.6-5.7-.2-8 1.5-2.3-1.7-5-2.1-8-1.5Z" />
      <path d="M12 7v13" />
    </>
  ),
  videos: (
    <>
      <rect x="3" y="5" width="13" height="14" rx="2" />
      <path d="m16 10 5-3v10l-5-3Z" />
      <path d="m8 9 4 3-4 3Z" />
    </>
  ),
  manage: (
    <>
      <path d="M14.5 6.5a5 5 0 0 0-6.7 6.7L3 18l3 3 4.8-4.8a5 5 0 0 0 6.7-6.7L14 13l-3-3Z" />
    </>
  ),
  teacher: (
    <>
      <path d="m2 9 10-5 10 5-10 5Z" />
      <path d="M6 11v5c3.5 2.7 8.5 2.7 12 0v-5M22 9v6" />
    </>
  ),
};

function BottomNavIcon({ name }) {
  return (
    <svg
      className="bottom-nav-svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {iconShapes[name]}
    </svg>
  );
}

function BottomNav({ user }) {
  const isTeacher = user?.role === "teacher";
  const isAdmin = user?.role === "admin";

  const navItems = isAdmin
    ? [
        { to: "/admin", label: "Reports", icon: "dashboard" },
        { to: "/admin/manage/teacher-requests", label: "Requests", icon: "teacher" },
        { to: "/admin/manage/accounts", label: "Accounts", icon: "profile" },
        { to: "/admin/manage/classes", label: "Classes", icon: "groups" },
        { to: "/admin/manage/content", label: "Content", icon: "manage" },
      ]
    : isTeacher
    ? [
        { to: "/dashboard", label: "Dashboard", icon: "dashboard" },
        { to: "/materials", label: "Notes", icon: "notes" },
        { to: "/videos", label: "Videos", icon: "videos" },
        { to: "/mock-tests", label: "Tests", icon: "quiz" },
        { to: "/teacher/manage", label: "Manage", icon: "manage" },
        { to: "/teacher", label: "Teacher", icon: "teacher" },
      ]
    : [
        { to: "/dashboard", label: "Dashboard", icon: "dashboard" },
        { to: "/quiz", label: "Quizzes", icon: "quiz" },
        { to: "/mentor", label: "AI Mentor", icon: "mentor" },
        { to: "/groups", label: "Groups", icon: "groups" },
        { to: "/profile", label: "Profile", icon: "profile" },
      ];

  return (
    <nav className="mobile-bottom-nav">
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === "/admin"}
          className={({ isActive }) =>
            `bottom-nav-item ${isActive ? "active" : ""}`
          }
        >
          <span className="bottom-nav-icon">
            <BottomNavIcon name={item.icon} />
          </span>
          <span className="bottom-nav-label">{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}

export default BottomNav;
