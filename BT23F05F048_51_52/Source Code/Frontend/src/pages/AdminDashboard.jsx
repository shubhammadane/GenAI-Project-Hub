import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";
import "./AdminDashboard.css";
import {getRelativeTime} from "../utils/timeFormatter.js"
import Sidebar from "../components/Sidebar.jsx";
import {useAuth} from "../context/AuthContext.jsx"

/* ── Material Symbol helper ── */
const Icon = ({ name, className = "" }) => (
  <span className={`ms-icon material-symbols-outlined ${className}`}>{name}</span>
);

/* ── Admin Navigation Items ── */
const NAV_ITEMS = [
  { icon: "dashboard", label: "Dashboard", path: "/admin", active: true },
  { icon: "assignment", label: "Tasks", path: "/tasks" },
  { icon: "event", label: "Events", path: "/events" },
  { icon: "monitoring", label: "Analytics", path: "/Analytics" },
  { icon: "psychology", label: "AI Planner", path: "/ai-planner" },
  { icon: "account_circle", label: "Profile", path: "/profile" },
];

export default function AdminDashboard() {

  const [summary, setSummary] = useState({
    totalUsers: 0,
    activeUsers: 0,
    totalTasks: 0,
    completionRate: 0,
  });
  const [recentUsers, setRecentUsers] = useState([]);
  const [aiPlans,setAiplans]=useState([]);
  const [charts,setCharts]=useState({
    userGrowth: [], 
    dailyActivity: [],
    peakHour: "N/A"
  }
  )
  const [animated, setAnimated] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [dateRange, setDateRange] = useState("Last 30 Days");
  const [adminError, setAdminError] = useState("");
  const navigate = useNavigate();

  const {user,token,logout}=useAuth();


  // Trigger progress line animations on mount
  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 150);
    return () => clearTimeout(t);
  }, []);

  const fetchAdminSummary = async () => {
      if (!token) return;
      try {
        const res = await api.get("/admin");
        const data=res.data;
        setSummary(data.metrics);
        setCharts(data.charts)
        setRecentUsers(data.recentUsers || []);
        setAiplans(data.aiPlans);
      } catch (err) {
        setAdminError("Unable to load admin dashboard data.");
        console.error("Error fetching admin summary:", err);
      }
    };

  // Fetch User profile details on mount
  useEffect(() => {    
    fetchAdminSummary();
  }, []);

  // Logout handler
  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const username = user?.username || "Alex Rivera";
  const userRole = user?.role || "Admin Account";
  
  // High quality Unsplash face matching the admin look from the screenshot
  const avatarImage = "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=facearea&facepad=2&w=256&h=256&q=80";

  return (
    <div className="ad-root">
      <Sidebar
      NAV_ITEMS={NAV_ITEMS}
      // avatarImage={avatarImage}
      user={user}
      />

      {/* ══ MAIN CANVAS ══ */}
      <main className="ad-main">
        {/* Header section */}
        <header className="ad-header">
          <div className="ad-header-titles">
            <h2>Executive Dashboard</h2>
            <p>Real-time platform performance and task orchestration.</p>
          </div>
          <div className="ad-header-actions">
            <div className="ad-search-wrap">
              <Icon name="search" />
              <input
                type="text"
                className="ad-search-input"
                placeholder="Search insights..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <button className="ad-notification-btn" onClick={() => alert("No new notifications")}>
              <Icon name="notifications" />
              <span className="ad-notification-dot"></span>
            </button>
          </div>
        </header>

        {/* Bento Stats Grid */}
        <section className="ad-stats-grid">
          {/* Card 1: Total Users */}
          <div className="ad-stat-card">
            <div className="ad-stat-top">
              <div className="ad-stat-icon-wrap">
                <Icon name="group" />
              </div>
              {/* <span className="ad-stat-growth">+12% ↑</span> */}
            </div>
            <div>
              <p className="ad-stat-label">Total Users</p>
              <h3 className="ad-stat-value">{summary.totalUsers}</h3>
            </div>
            <div className="ad-progress-track">
              <div className="ad-progress-fill" style={{ width: animated ? "75%" : "0%" }}></div>
            </div>
          </div>

          {/* Card 2: Active Users */}
          <div className="ad-stat-card">
            <div className="ad-stat-top">
              <div className="ad-stat-icon-wrap">
                <Icon name="bolt" />
              </div>
              {/* <span className="ad-stat-growth">+8% ↑</span> */}
            </div>
            <div>
              <p className="ad-stat-label">Active Users</p>
              <h3 className="ad-stat-value">{summary.activeUser}</h3>
            </div>
            <div className="ad-progress-track">
              <div className="ad-progress-fill" style={{ width: animated ? "65%" : "0%" }}></div>
            </div>
          </div>

          {/* Card 3: Total Tasks */}
          <div className="ad-stat-card">
            <div className="ad-stat-top">
              <div className="ad-stat-icon-wrap">
                <Icon name="task_alt" />
              </div>
              {/* <span className="ad-stat-growth">+24% ↑</span> */}
            </div>
            <div>
              <p className="ad-stat-label">Total Tasks</p>
              <h3 className="ad-stat-value">{summary.totalTasks}</h3>
            </div>
            <div className="ad-progress-track">
              <div className="ad-progress-fill" style={{ width: animated ? "88%" : "0%" }}></div>
            </div>
          </div>

          {/* Card 4: Completion Rate */}
          <div className="ad-stat-card">
            <div className="ad-stat-top">
              <div className="ad-stat-icon-wrap">
                <Icon name="analytics" />
              </div>
              {/* <span className="ad-stat-growth">+2% ↑</span> */}
            </div>
            <div>
              <p className="ad-stat-label">Completion Rate</p>
              <h3 className="ad-stat-value">{summary.completionRate}%</h3>
            </div>
            <div className="ad-progress-track">
              <div className="ad-progress-fill" style={{ width: animated ? `${summary.completionRate}%` : "0%" }}></div>
            </div>
          </div>
        </section>

        {/* Charts Section */}
        <section className="ad-charts-grid">
          {/* User Growth Column Graph */}
          <div className="ad-chart-card">
            <div className="ad-chart-header">
              <h4>User Growth</h4>
              <select
                className="ad-filter-select"
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
              >
                <option>Last 7 Days</option>
                <option>Last 90 Days</option>
              </select>
            </div>
            
            <div className="ad-bars-container">
              {charts.userGrowth.map((d, i) => (
                <div key={d.day} className={`ad-bar-col ${i === 6 ? "active" : ""}`}>
                  <span className="ad-bar-tooltip">{d.count} Users</span>
                  <div
                    className="ad-bar-fill"
                    style={{ height: animated ? d.height : "0%" }}
                  ></div>
                </div>
              ))}
            </div>
            <div className="ad-labels-row">
              {charts.userGrowth.map((d) => (
                <span key={d.day}>{d.day}</span>
              ))}
            </div>
          </div>

          {/* Daily Active Server Traffic */}
          <div className="ad-chart-card ad-activity-card">
            <div>
              <h4 style={{ fontSize: "16px", fontWeight: 700, color: "var(--on-surface)", margin: "0 0 4px" }}>
                Daily Activity
              </h4>
              <p style={{ fontSize: "11px", color: "var(--on-surface-variant)", margin: 0 }}>
                Hourly server traffic distribution.
              </p>
            </div>

            <div className="ad-traffic-list">
              {charts.dailyActivity.map((d) => (
                <div key={d.time} className="ad-traffic-row">
                  <span className="ad-traffic-time">{d.time}</span>
                  <div className="ad-traffic-track">
                    <div
                      className="ad-traffic-fill"
                      style={{ width: animated ? d.percent : "0%" }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>

            <div className="ad-peak-footer">
              <span className="ad-peak-label">Peak Hour</span>
              <span className="ad-peak-value">{charts.peakHour}</span>
            </div>
          </div>
        </section>

        {/* Dynamic Tables Grid */}
        <section className="ad-tables-grid">
          {/* Recent Users list table */}
          <div className="ad-table-card">
            <div className="ad-table-header">
              <h4>Recent Users</h4>
              <button className="ad-view-all-btn" onClick={() => alert("Showing all users...")}>
                View All
              </button>
            </div>
            <div className="ad-table-wrap">
              <table className="ad-table">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Role</th>
                    <th>Joined</th>
                  </tr>
                </thead>
                <tbody>
                  {(recentUsers.length > 0 ? recentUsers : []).map((u, i) => (
                    <tr key={i} className="ad-table-tr">
                      <td>
                        <div className="ad-user-cell">
                          <div className="ad-avatar-initial">{(u.username?.[0] || "U")}</div>
                          <div>
                            <p className="ad-user-name">{u.username}</p>
                            <p className="ad-user-email">{u.email}</p>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className={`ad-badge ${u.role ? u.role.toLowerCase() : u.status?.toLowerCase()}`}>
                          {u.role ? u.role : u.status}
                        </span>
                      </td>
                      <td style={{ fontSize: "13px", color: "var(--on-surface-variant)" }}>
                        {getRelativeTime(u.joinedAt)|| "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Task Orchestration Status Table */}
          <div className="ad-table-card">
            <div className="ad-table-header">
              <h4>Task Orchestration</h4>
              <button className="ad-more-btn" onClick={() => alert("Showing options...")}>
                <Icon name="more_horiz" />
              </button>
            </div>
            <div className="ad-table-wrap">
              <table className="ad-table">
                <thead>
                  <tr>
                    <th>Plan</th>
                    <th>User</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {aiPlans.map((task) => (
                    <tr key={task.id} className="ad-table-tr">
                      <td>
                        <span className="ad-task-title">{task.plan}</span>
                        
                      </td>
                      <td className="ad-task-owner">{task.username}</td>
                      <td>
                        <div className={`ad-status-indicator ${task.status}`}>
                          <span className="ad-status-dot"></span>
                          {task.status}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
