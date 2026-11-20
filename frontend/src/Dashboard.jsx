
function Dashboard({ student, onLogout }) {
  const features = [
    {
      title: "Study Materials",
      description: "Access notes and learning resources",
      icon: "📚"
    },
    {
      title: "Future Course Guidance",
      description: "Explore your higher-study options",
      icon: "🎓"
    },
    {
      title: "AI Personal Mentor",
      description: "Get personalized study assistance",
      icon: "🤖"
    },
    {
      title: "Mock Tests",
      description: "Practice tests based on your level",
      icon: "📝"
    },
    {
      title: "Course Summaries",
      description: "Learn Biology, Maths, CS and more",
      icon: "📖"
    },
    {
      title: "Previous Question Papers",
      description: "Practice with solved question papers",
      icon: "📄"
    }
  ];

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>FLINT</h1>
        <button onClick={onLogout}>Logout</button>
      </header>

      <section className="welcome">
        <h2>Welcome, {student.name}!</h2>
        <p>Your personalized learning journey starts here.</p>
      </section>

      <h2 className="section-title">Learning Dashboard</h2>

      <div className="feature-grid">
        {features.map((feature, index) => (
          <div className="feature-card" key={index}>
            <span className="feature-icon">{feature.icon}</span>
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
            <button>Explore</button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
