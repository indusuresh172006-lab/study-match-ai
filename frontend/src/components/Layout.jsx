import { useState } from "react";
import { useLocation } from "react-router-dom";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import BottomNav from "./BottomNav";
import ChatWidget from "./ChatWidget";

function Layout({ user, onLogout, children }) {
  const location = useLocation();
  const isMentorPage = location.pathname === "/mentor";
  const isStaff = ["teacher", "admin"].includes(user?.role);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className={`app-layout ${isStaff ? "teacher-layout" : "student-layout"}`}>
      <Navbar
        user={user}
        onLogout={onLogout}
        mobileMenuOpen={mobileMenuOpen}
        onMenuToggle={() => setMobileMenuOpen((open) => !open)}
      />
      <div className="layout-body">
        <Sidebar
          user={user}
          mobileOpen={mobileMenuOpen}
          onClose={() => setMobileMenuOpen(false)}
        />
        <main className="layout-main-content">
          {children}
        </main>
      </div>
      <BottomNav user={user} />
      {/* Floating AI Mentor Chatbot accessible everywhere for students except full mentor page */}
      {!isMentorPage && !isStaff && <ChatWidget user={user} />}
    </div>
  );
}

export default Layout;
