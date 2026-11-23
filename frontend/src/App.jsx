import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "./App.css";
import TeacherManagement from "./pages/TeacherManagement";
import Login from "./Login";
import Register from "./Register";
import Layout from "./components/Layout";

import StudentDashboard from "./pages/StudentDashboard";
import TopicQuiz from "./pages/TopicQuiz";
import StudyGroups from "./pages/StudyGroups";
import StudyMaterials from "./pages/StudyMaterials";
import CourseVideos from "./pages/CourseVideos";
import CourseGuidance from "./pages/CourseGuidance";
import AIMentor from "./pages/AIMentor";
import MockTests from "./pages/MockTests";
import CourseSummaries from "./pages/CourseSummaries";
import PreviousPapers from "./pages/PreviousPapers";
import StudentProfile from "./pages/StudentProfile";
import TeacherDashboard from "./pages/TeacherDashboard";
import AdminDashboard from "./pages/AdminDashboard";

function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("studymatch_user");
    return saved ? JSON.parse(saved) : null;
  });

  const handleLogin = (userData) => {
    const userObj = {
      id: userData.student_id,
      name: userData.name,
      email: userData.email,
      role: userData.role,
    };
    setUser(userObj);
  };

  const handleLogout = () => {
    localStorage.removeItem("studymatch_token");
    localStorage.removeItem("studymatch_user");
    setUser(null);
  };

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Auth Routes */}
        <Route
          path="/login"
          element={
            !user ? (
              <div className="auth-wrapper">
                <Login
                  onLogin={handleLogin}
                  onSwitchToRegister={() => (window.location.href = "/register")}
                />
              </div>
            ) : (
              <Navigate to="/dashboard" replace />
            )
          }
        />

        <Route
          path="/register"
          element={
            !user ? (
              <div className="auth-wrapper">
                <Register onSwitchToLogin={() => (window.location.href = "/login")} />
              </div>
            ) : (
              <Navigate to="/dashboard" replace />
            )
          }
        />

        {/* Protected App Routes */}
        <Route
          path="/dashboard"
          element={
            user ? (
              user.role === "admin" ? (
                <Navigate to="/admin" replace />
              ) : (
                <Layout user={user} onLogout={handleLogout}>
                  <StudentDashboard user={user} />
                </Layout>
              )
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/profile"
          element={
            user && user.role === "student" ? (
              <Layout user={user} onLogout={handleLogout}>
                <StudentProfile user={user} />
              </Layout>
            ) : (
              <Navigate to={user ? "/dashboard" : "/login"} replace />
            )
          }
        />

        <Route
          path="/quiz"
          element={
            user ? (
              <Layout user={user} onLogout={handleLogout}>
                <TopicQuiz user={user} />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/groups"
          element={
            user ? (
              <Layout user={user} onLogout={handleLogout}>
                <StudyGroups user={user} />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/materials"
          element={
            user ? (
              <Layout user={user} onLogout={handleLogout}>
                <StudyMaterials user={user} />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/videos"
          element={
            user ? (
              <Layout user={user} onLogout={handleLogout}>
                <CourseVideos />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/guidance"
          element={
            user ? (
              <Layout user={user} onLogout={handleLogout}>
                <CourseGuidance user={user} />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/mentor"
          element={
            user ? (
              <Layout user={user} onLogout={handleLogout}>
                <AIMentor user={user} />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/mock-tests"
          element={
            user ? (
              <Layout user={user} onLogout={handleLogout}>
                <MockTests user={user} />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/summaries"
          element={
            user ? (
              <Layout user={user} onLogout={handleLogout}>
                <CourseSummaries user={user} />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/papers"
          element={
            user ? (
              <Layout user={user} onLogout={handleLogout}>
                <PreviousPapers user={user} />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/teacher"
          element={
            user && user.role === "teacher" ? (
              <Layout user={user} onLogout={handleLogout}>
                <TeacherDashboard user={user} />
              </Layout>
            ) : (
              <Navigate to={user?.role === "admin" ? "/admin" : user ? "/dashboard" : "/login"} replace />
            )
          }
        />

        <Route
          path="/admin"
          element={
            user && user.role === "admin" ? (
              <Layout user={user} onLogout={handleLogout}>
                <AdminDashboard user={user} />
              </Layout>
            ) : (
              <Navigate to={user ? "/dashboard" : "/login"} replace />
            )
          }
        />

        <Route
          path="/teacher/manage"
          element={
            user && ["teacher", "admin"].includes(user.role) ? (
              <Layout user={user} onLogout={handleLogout}>
                <TeacherManagement />
              </Layout>
            ) : (
              <Navigate to={user ? "/dashboard" : "/login"} replace />
            )
          }
        />
        <Route
          path="*"
          element={<Navigate to={user ? "/dashboard" : "/login"} replace />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
