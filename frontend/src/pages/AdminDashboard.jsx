import AdminManagement from "./AdminManagement";
import TeacherDashboard from "./TeacherDashboard";

function AdminDashboard({ user }) {
  return (
    <>
      <section className="teacher-section-card admin-page-heading">
        <h2>Administrator Dashboard</h2>
        <p className="page-subtitle">
          Manage accounts and classes, then review platform-wide academic activity.
        </p>
      </section>
      <AdminManagement />
      <TeacherDashboard user={user} isAdmin />
    </>
  );
}

export default AdminDashboard;
