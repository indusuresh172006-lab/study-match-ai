import TeacherManagement from "./TeacherManagement";

function TeacherCurriculumPage() {
  return (
    <div className="teacher-curriculum-page">
      <div className="card-head-row" style={{ marginBottom: "20px" }}>
        <div>
          <h2>📚 Subjects & Syllabus Topic Management</h2>
          <p className="subtext">
            Module 1.2: Define courses, curriculum subjects, and hierarchical syllabus topics with order index and topic learning descriptions.
          </p>
        </div>
      </div>

      <TeacherManagement
        defaultTab="subjects"
        allowedTabs={["subjects", "topics"]}
        hideHeader={true}
        hideTabs={false}
      />
    </div>
  );
}

export default TeacherCurriculumPage;
