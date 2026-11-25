import TeacherManagement from "./TeacherManagement";

function TeacherQuizzesPage() {
  return (
    <div className="teacher-quizzes-page">
      <div className="card-head-row" style={{ marginBottom: "20px" }}>
        <div>
          <h2>🎯 Quiz & Question Bank Management</h2>
          <p className="subtext">
            Module 1.3: Create and manage topic-tagged multiple choice questions with 4 options, designated correct answers, explanations, and difficulty levels.
          </p>
        </div>
      </div>

      <TeacherManagement
        defaultTab="questions"
        allowedTabs={["questions"]}
        hideHeader={true}
        hideTabs={true}
      />
    </div>
  );
}

export default TeacherQuizzesPage;
