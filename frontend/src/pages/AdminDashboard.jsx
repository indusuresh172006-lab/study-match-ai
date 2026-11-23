import { useCallback, useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import api from "../api";

function AdminDashboard() {
  const [overview, setOverview] = useState(null);
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchReportData = useCallback(() => Promise.all([
    api.get("/api/v1/admin/overview"),
    api.get("/api/v1/admin/classes", { params: { include_inactive: true } }),
  ]), []);

  useEffect(() => {
    let active = true;
    fetchReportData()
      .then(([overviewResponse, classesResponse]) => {
        if (!active) return;
        setOverview(overviewResponse.data);
        setClasses(classesResponse.data || []);
      })
      .catch((err) => {
        if (active) setError(err.response?.data?.detail || "Could not load admin reports.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [fetchReportData]);

  const refreshReports = async () => {
    setLoading(true);
    setError("");
    try {
      const [overviewResponse, classesResponse] = await fetchReportData();
      setOverview(overviewResponse.data);
      setClasses(classesResponse.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load admin reports.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <section className="teacher-section-card"><p>Loading admin reports...</p></section>;
  }

  if (error) {
    return (
      <section className="teacher-section-card">
        <p className="auth-error-msg" role="alert">{error}</p>
        <button className="action-btn-secondary" type="button" onClick={refreshReports}>Retry</button>
      </section>
    );
  }

  const accountData = [
    { role: "Students", total: overview?.students ?? 0 },
    { role: "Teachers", total: overview?.teachers ?? 0 },
    { role: "Admins", total: overview?.admins ?? 0 },
  ];
  const activeClasses = overview?.active_classes ?? 0;
  const classStatusData = [
    { status: "Active", total: activeClasses },
    { status: "Inactive", total: Math.max(0, (overview?.total_classes ?? 0) - activeClasses) },
  ];
  const enrollmentData = classes
    .filter((studyClass) => studyClass.is_active)
    .map((studyClass) => ({
      name: studyClass.name,
      students: studyClass.roster_size,
    }))
    .sort((a, b) => b.students - a.students);

  return (
    <div className="admin-reports-page">
      <section className="teacher-section-card admin-page-heading">
        <div className="card-head-row">
          <div>
            <h2>Admin Reports</h2>
            <p className="page-subtitle">Platform-wide account, class, and enrollment summaries.</p>
          </div>
          <button className="action-btn-secondary btn-sm" type="button" onClick={refreshReports}>
            Refresh reports
          </button>
        </div>
      </section>

      <section className="kpi-grid" aria-label="Platform report summary">
        <div className="kpi-card info"><div className="kpi-icon">👥</div><div className="kpi-details"><span className="kpi-num">{overview?.total_users ?? 0}</span><span className="kpi-label">Total Accounts</span></div></div>
        <div className="kpi-card success"><div className="kpi-icon">🏫</div><div className="kpi-details"><span className="kpi-num">{activeClasses}</span><span className="kpi-label">Active Classes</span></div></div>
        <div className="kpi-card warning"><div className="kpi-icon">⏳</div><div className="kpi-details"><span className="kpi-num">{overview?.pending_teacher_requests ?? 0}</span><span className="kpi-label">Pending Teacher Requests</span></div></div>
      </section>

      <div className="admin-reports-grid">
        <section className="dashboard-chart-card admin-report-chart">
          <h3>Accounts by role</h3>
          <span className="card-subtext">Number of registered accounts in each role.</span>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={accountData} margin={{ top: 8, right: 12, left: -12, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="role" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="total" name="Accounts" fill="#087e8b" radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="dashboard-chart-card admin-report-chart">
          <h3>Class status</h3>
          <span className="card-subtext">Active and inactive classes across the platform.</span>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={classStatusData} margin={{ top: 8, right: 12, left: -12, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="status" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="total" name="Classes" fill="#55a630" radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="dashboard-chart-card admin-report-chart admin-enrollment-chart">
          <h3>Students enrolled by active class</h3>
          <span className="card-subtext">Enrollment totals for active classes, highest first.</span>
          {enrollmentData.length ? (
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={Math.max(260, enrollmentData.length * 42)}>
                <BarChart
                  data={enrollmentData}
                  layout="vertical"
                  margin={{ top: 8, right: 24, left: 12, bottom: 4 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" allowDecimals={false} />
                  <YAxis type="category" dataKey="name" width={130} />
                  <Tooltip />
                  <Bar dataKey="students" name="Students" fill="#f4a261" radius={[0, 5, 5, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="no-data-msg">No active classes are available to report yet.</p>
          )}
        </section>
      </div>
    </div>
  );
}

export default AdminDashboard;
