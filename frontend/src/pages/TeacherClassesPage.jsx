import TeacherClassesPanel from "./TeacherClassesPanel";

function TeacherClassesPage({ user }) {
  return (
    <div className="teacher-classes-page">
      <div className="card-head-row" style={{ marginBottom: "20px" }}>
        <div>
          <h2>🏫 Classes, Enrollment & Marks Import</h2>
          <p className="subtext">
            Module 1.2 & 1.4: Create scoped classes, share join codes with students, inspect class rosters, and import topic-tagged marks via CSV / XLSX.
          </p>
        </div>
      </div>

      <TeacherClassesPanel isAdmin={user?.role === "admin"} hideHeader={true} />
    </div>
  );
}

export default TeacherClassesPage;
