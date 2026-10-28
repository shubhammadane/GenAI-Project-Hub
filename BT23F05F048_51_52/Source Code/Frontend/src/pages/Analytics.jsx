import { useState, useEffect, useRef } from "react";
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';
import { Link } from "react-router-dom";
import axios from "axios";
import "./Analytics.css";
import api from "../api/axios";
import Sidebar from "../components/Sidebar";
import {useAuth} from '../context/AuthContext'
/* ── Material Symbol helper ── */
const Icon = ({ name, className = "" }) => (
  <span className={`ms-icon material-symbols-outlined ${className}`}>{name}</span>
);

/* ── Navigation Items ── */
const NAV_ITEMS = [
  { icon: "dashboard", label: "Dashboard", path: "/dashboard" },
  { icon: "assignment", label: "Tasks", path: "/tasks" },
  { icon: "event", label: "Events", path: "/events" },
  { icon: "monitoring", label: "Analytics", path: "/Analytics", active: true },
  { icon: "psychology", label: "AI Planner", path: "/ai-planner" },
  { icon: "account_circle", label: "Profile", path: "/profile" },
];

export default function Analytics({ tasks = [], setTasks }) {
  const [analyticsData, setAnalyticsData] = useState({
    overview: {},
    weeklyProductivity: [],
    categories: [],
    priority: [],
    monthResult: [],
  });
  // const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [animated, setAnimated] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const ringRef = useRef(null);
  
  const{user,token,logout} =useAuth();


  // Fetch Data on mount
  useEffect(() => {
    const fetchData = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const [analyticsRes] = await Promise.all([
          api.get("/analytics")
        ]);

        setAnalyticsData(analyticsRes.data);
      } catch (err) {
        console.error("Error fetching analytics data:", err);
        setError(err.response?.data?.message || err.message || "Failed to load analytics");
      } finally {
        setLoading(false);
      }
    };
    fetchData();

    // Trigger chart entrance animations
    const t = setTimeout(() => setAnimated(true), 300);
    return () => clearTimeout(t);
  }, [token]);

  const overview = analyticsData.overview || {};
  const hasAnalyticsOverview = overview && Object.keys(overview).length > 0;

  const totalTasks = hasAnalyticsOverview ? overview.totalTasks : tasks.length || 0;
  const completedTasks = hasAnalyticsOverview ? overview.completedTasks : tasks.filter((t) => t.completed || t.status === "Review").length || 0;
  const pendingTasks = hasAnalyticsOverview ? overview.pendingTasks : totalTasks - completedTasks || 0;
  const completionRate = hasAnalyticsOverview ? Math.round(overview.completionRate) : totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) :0;
  const upcomingEventsCount = hasAnalyticsOverview ? overview.upcomingEvents : 0;

  // Project Categories percentages calculation using analytics API first
  const analyticsCategories = analyticsData.categories || [];
  let categoryDistribution = [
    { name: "Engineering", percentage: 0, class: "blue" },
    { name: "Marketing", percentage: 0, class: "indigo" },
    { name: "HR & Admin", percentage: 0, class: "purple" },
  ];

  if (analyticsCategories.length > 0) {
    const totalCategoryCount = analyticsCategories.reduce((sum, item) => sum + (item.count || 0), 0) || 1;

    categoryDistribution = analyticsCategories.slice(0, 3).map((item, index) => {
      const classes = ["blue", "indigo", "purple"];
      return {
        name: item.category || "Other",
        percentage: Math.round(((item.count || 0) / totalCategoryCount) * 100),
        class: classes[index % 3],
      };
    });
  } else if (tasks.length > 0) {
    const counts = {};
    tasks.forEach((t) => {
      const cat = t.category || "Work";
      counts[cat] = (counts[cat] || 0) + 1;
    });
    const total = tasks.length || 1;
    const mapped = Object.entries(counts).map(([name, count], index) => {
      const classes = ["blue", "indigo", "purple"];
      return {
        name,
        percentage: Math.round((count / total) * 100),
        class: classes[index % 3],
      };
    });
    if (mapped.length > 0) {
      categoryDistribution = mapped.slice(0, 3);
    }
  }

  // Priority Breakdown counts using analytics API first
  let priorities = { high: 0, medium: 0, low: 0 };
  if (analyticsData.priority && analyticsData.priority.length > 0) {
    priorities = {
      high: analyticsData.priority.find((p) => p.priority?.toLowerCase() === "high")?.count || 0,
      medium: analyticsData.priority.find((p) => p.priority?.toLowerCase() === "medium")?.count || 0,
      low: analyticsData.priority.find((p) => p.priority?.toLowerCase() === "low")?.count || 0,
    };
  } else if (tasks.length > 0) {
    priorities = {
      high: tasks.filter((t) => t.priority?.toLowerCase() === "high").length,
      medium: tasks.filter((t) => t.priority?.toLowerCase() === "medium").length,
      low: tasks.filter((t) => t.priority?.toLowerCase() === "low").length,
    };
  }

  const weeklyProductivity = analyticsData.weeklyProductivity || [];
  const weeklyData = weeklyProductivity.length > 0
    ? weeklyProductivity.map((item) => {
        const completed = Number(item.completed) || 0;
        const remaining = Number(item.remaining) || 0;
        const total = completed + remaining || 1;
        return {
          day: item.day || "",
          done: `${Math.round((completed / total) * 100)}%`,
          remaining: `${Math.round((remaining / total) * 100)}%`,
        };
      })
    : [
        { day: "Mon", done: "0%", remaining: "0%" },
        { day: "Tue", done: "0%", remaining: "0%" },
        { day: "Wed", done: "0%", remaining: "0%" },
        { day: "Thu", done: "0%", remaining: "0%" },
        { day: "Fri", done: "0%", remaining: "0%" },
        { day: "Sat", done: "0%", remaining: "0%" },
        { day: "Sun", done: "0%", remaining: "0%" },
      ];

  // Progress ring variables (Radius = 46, Circumference = 289.03)
  const ringCircumference = 289.03;
  const strokeOffset = ringCircumference - (ringCircumference * completionRate) / 100;

  // Monthly chart: normalize monthResult and fill gaps for the last 12 months
  const monthlyRaw = analyticsData.monthResult || [];
  // Build last 12 months labels (from oldest to newest)
  const now = new Date();
  const last12 = Array.from({ length: 12 }).map((_, i) => {
    const d = new Date(now.getFullYear(), now.getMonth() - 11 + i, 1);
    return { monthNumber: d.getMonth() + 1, label: d.toLocaleString('default', { month: 'short' }) };
  });

  // Create a lookup from backend results by monthNumber
  const monthMap = {};
  monthlyRaw.forEach((m) => {
    const num = Number(m.monthNumber);
    monthMap[num] = Number(m.count) || 0;
  });

  const startD = new Date(now.getFullYear(), now.getMonth() - 11, 1);
  const chartRangePill = `${startD.toLocaleString('default', { month: 'short' })} ${startD.getFullYear()} - ${now.toLocaleString('default', { month: 'short' })} ${now.getFullYear()}`;

  const monthlyLabels = last12.map((m) => m.label);
  const monthlyDataPoints = last12.map((m) => monthMap[m.monthNumber] ?? 0);

  const monthlyChartData = {
    labels: monthlyLabels,
    datasets: [
      {
        label: 'Tasks created',
        data: monthlyDataPoints,
        fill: true,
        backgroundColor: 'rgba(37,99,235,0.08)',
        borderColor: '#2563EB',
        tension: 0.25,
        pointRadius: 3,
        pointBackgroundColor: '#2563EB',
      },
    ],
  };

  const monthlyChartOptions = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      x: { display: true },
      y: { display: true, beginAtZero: true, ticks: { precision: 0 } },
    },
  };

  // User metadata fallback
  const username = user?.username || user?.email?.split("@")[0] || "Alex Rivera";
  const userEmail = user?.email || "alex@taskpilot.ai";
  
  // High quality headshot matching the screenshot's circular avatar
  const avatarImage = "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=facearea&facepad=2&w=256&h=256&q=80";

  return (
    <div className="an-root">
      
      <Sidebar
              NAV_ITEMS={NAV_ITEMS}
              // avatarImage={avatarImage}
              user={user}
            />

      {/* ══ MAIN CONTENT ══ */}
      <main className="an-main">
        {/* Header Section */}
        <header className="an-header">
          <div>
            <h2>Analytics Overview</h2>
            <p className="an-subtitle">
              Visualizing your productivity and mission-critical milestones.
            </p>
          </div>
          <div className="an-header-actions">
            <div className="relative">
              {/* <button
                className="an-dropdown-btn"
                onClick={() => setDropdownOpen(!dropdownOpen)}
              >
                <Icon name="calendar_month" />
                <span>Last 30 Days</span>
                <Icon name="keyboard_arrow_down" />
              </button> */}
              {dropdownOpen && (
                <div
                  style={{
                    position: "absolute",
                    right: 0,
                    top: "45px",
                    background: "#fff",
                    borderRadius: "10px",
                    boxShadow: "0 10px 25px rgba(0,0,0,0.08)",
                    border: "1px solid rgba(114,119,133,0.15)",
                    zIndex: 100,
                    width: "150px",
                    overflow: "hidden",
                  }}
                >
                  {["Last 7 Days", "Last 30 Days", "Last 90 Days", "This Year"].map((opt) => (
                    <button
                      key={opt}
                      onClick={() => setDropdownOpen(false)}
                      style={{
                        width: "100%",
                        padding: "10px 16px",
                        textAlign: "left",
                        border: "none",
                        background: "none",
                        fontSize: "13px",
                        cursor: "pointer",
                        color: "var(--on-surface-variant)",
                      }}
                      onMouseEnter={(e) => (e.target.style.background = "var(--surface-low)")}
                      onMouseLeave={(e) => (e.target.style.background = "none")}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {/* <button className="an-export-btn" onClick={() => alert("Report exported successfully!")}>
              <Icon name="download" />
              <span>Export Report</span>
            </button> */}
          </div>
        </header>

        {/* ── Stats Cards Row ── */}
        <div className="an-stats-row">
          {/* Card 1: Total Tasks */}
          <div className="glass-card an-stat-card stat-total">
            <div className="an-stat-top">
              <div className="an-stat-icon">
                <Icon name="task_alt" style={{ fontVariationSettings: "'FILL' 1" }} />
              </div>
              <span className="an-stat-badge">+12%</span>
            </div>
            <div>
              <p className="an-stat-label">Total Tasks</p>
              <p className="an-stat-value">{totalTasks.toLocaleString()}</p>
            </div>
          </div>

          {/* Card 2: Completed */}
          <div className="glass-card an-stat-card stat-completed">
            <div className="an-stat-top">
              <div className="an-stat-icon">
                <Icon name="check_circle" style={{ fontVariationSettings: "'FILL' 1" }} />
              </div>
              <span className="an-stat-badge">+8%</span>
            </div>
            <div>
              <p className="an-stat-label">Completed</p>
              <p className="an-stat-value">{completedTasks.toLocaleString()}</p>
            </div>
          </div>

          {/* Card 3: Pending */}
          <div className="glass-card an-stat-card stat-pending">
            <div className="an-stat-top">
              <div className="an-stat-icon">
                <Icon name="pending" style={{ fontVariationSettings: "'FILL' 1" }} />
              </div>
            </div>
            <div>
              <p className="an-stat-label">Pending</p>
              <p className="an-stat-value">{pendingTasks.toLocaleString()}</p>
            </div>
          </div>

          {/* Card 4: Completion Rate */}
          <div className="glass-card an-stat-card stat-rate">
            <div>
              <p className="an-stat-label">Completion Rate</p>
              <p className="an-stat-value">{completionRate}%</p>
            </div>
            <div className="an-rate-container">
              <div className="an-rate-bar-track">
                <div
                  className="an-rate-bar-fill"
                  style={{ width: animated ? `${completionRate}%` : "0%" }}
                ></div>
              </div>
            </div>
          </div>

          {/* Card 5: Next 48H solid blue */}
          <div className="glass-card an-stat-card stat-next-48h">
            <div className="an-stat-top">
              <div className="an-stat-icon">
                <Icon name="notifications" style={{ fontVariationSettings: "'FILL' 1" }} />
              </div>
              <span className="an-stat-badge-text">Next 48H</span>
            </div>
            <div>
              <p className="an-stat-label">Upcoming Events</p>
              <p className="an-stat-value">{upcomingEventsCount}</p>
            </div>
          </div>
        </div>

        {/* ── Row 1 of Charts ── */}
        <div className="an-charts-row-1">
          {/* Weekly Productivity Bar Chart */}
          <div className="glass-card an-chart-card">
            <div className="an-chart-header-row">
              <div className="an-chart-title-wrap">
                <h3>Weekly Productivity</h3>
                <p>Daily task throughput across the current week.</p>
              </div>
              <div className="an-chart-legend">
                <div className="an-legend-item">
                  <span className="an-legend-dot blue"></span>
                  Done
                </div>
                <div className="an-legend-item">
                  <span className="an-legend-dot gray"></span>
                  Remaining
                </div>
              </div>
            </div>

            <div className="weekly-bar-chart-container">
              {weeklyData.map(({ day, done, remaining }) => (
                <div key={day} className="weekly-bar-col">
                  <div className="weekly-bar-track-wrap">
                    {/* Done Bar */}
                    <div className="weekly-bar-track">
                      <div
                        className="weekly-bar-fill done"
                        style={{ height: animated ? done : "0%" }}
                      ></div>
                    </div>
                    {/* Remaining Bar */}
                    <div className="weekly-bar-track">
                      <div
                        className="weekly-bar-fill remaining"
                        style={{ height: animated ? remaining : "0%" }}
                      ></div>
                    </div>
                  </div>
                  <span className="weekly-bar-day">{day}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Status Breakdown Circle Chart */}
          <div className="glass-card an-chart-card">
            <div className="an-chart-header-row">
              <div className="an-chart-title-wrap">
                <h3>Status Breakdown</h3>
              </div>
            </div>

            <div className="circular-chart-container">
              <div className="circular-ring-wrap">
                <svg viewBox="0 0 110 110">
                  <circle className="ring-track" cx="55" cy="55" r="46" strokeWidth="8" fill="none" />
                  <circle
                    ref={ringRef}
                    className="ring-fill"
                    cx="55"
                    cy="55"
                    r="46"
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={ringCircumference}
                    strokeDashoffset={animated ? strokeOffset : ringCircumference}
                  />
                </svg>
                <div className="ring-center-label">
                  <h4>{completionRate}%</h4>
                  <p>Completed</p>
                </div>
              </div>

              {/* Status details indicators */}
              <div className="status-breakdown-details">
                <div className="status-detail-row">
                  <div className="status-detail-left">
                    <span className="status-detail-dot blue"></span>
                    Done
                  </div>
                  <span className="status-detail-value">{completedTasks.toLocaleString()}</span>
                </div>
                <div className="status-detail-row">
                  <div className="status-detail-left">
                    <span className="status-detail-dot gray"></span>
                    Pending
                  </div>
                  <span className="status-detail-value">{pendingTasks.toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── Row 2 of Charts ── */}
        <div className="an-charts-row-2">
          {/* Monthly Task Volume Line Chart */}
          <div className="glass-card an-chart-card">
            <div className="an-chart-header-row">
              <div className="an-chart-title-wrap">
                <h3>Monthly Task Volume</h3>
                <p>Number of tasks created per month (last 12 months).</p>
              </div>
              <span className="monthly-chart-pill">{chartRangePill}</span>
            </div>
            <div style={{ paddingTop: 16 }}>
              <Line data={monthlyChartData} options={monthlyChartOptions} />
            </div>
          </div>

          {/* Distribution Categories & Priorities Breakdown */}
          <div className="glass-card an-chart-card">
            {/* Project Categories */}
            <div className="distribution-subheading-row">
              <h4>Task Categories</h4>
              <a href="#details" className="distribution-view-details" onClick={(e) => e.preventDefault()}>
                View Details
              </a>
            </div>

            <div className="category-distribution-list">
              {categoryDistribution.map(({ name, percentage, class: colorCls }) => (
                <div key={name} className="category-progress-item">
                  <div className="category-progress-info">
                    <span>{name}</span>
                    <span>{percentage}%</span>
                  </div>
                  <div className="category-progress-bar-track">
                    <div
                      className={`category-progress-bar-fill ${colorCls}`}
                      style={{ width: animated ? `${percentage}%` : "0%" }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>

            {/* Priority Breakdown */}
            <div className="distribution-subheading-row" style={{ marginTop: "8px" }}>
              <h4>Priority Breakdown</h4>
            </div>

            <div className="priority-breakdown-container">
              <div className="priority-box high">
                <span className="priority-box-label">High</span>
                <span className="priority-box-val">{priorities.high}</span>
              </div>
              <div className="priority-box medium">
                <span className="priority-box-label">Medium</span>
                <span className="priority-box-val">{priorities.medium}</span>
              </div>
              <div className="priority-box low">
                <span className="priority-box-label">Low</span>
                <span className="priority-box-val">{priorities.low}</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}