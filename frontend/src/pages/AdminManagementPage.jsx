import AdminManagement from "./AdminManagement";
import TeacherManagement from "./TeacherManagement";

const PAGE_TITLES = {
  "teacher-requests": "Teacher Requests",
  accounts: "Accounts",
  classes: "Classes",
};

function AdminManagementPage({ view }) {
  if (view === "content") {
    return <TeacherManagement />;
  }

  return (
    <div className="admin-management-page">
      <section className="teacher-section-card admin-page-heading">
        <h2>{PAGE_TITLES[view]}</h2>
        <p className="page-subtitle">
          {view === "teacher-requests" && "Review pending teacher account applications."}
          {view === "accounts" && "View accounts and create teacher accounts."}
          {view === "classes" && "Create classes, reassign teachers, and manage enrollment."}
        </p>
      </section>
      <AdminManagement view={view} />
    </div>
  );
}

export default AdminManagementPage;
