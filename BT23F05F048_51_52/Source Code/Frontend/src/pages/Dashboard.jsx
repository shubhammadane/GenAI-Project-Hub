import { useState, useEffect, useRef } from 'react';
import { useNavigate,Link, useFetcher } from 'react-router-dom';
import axios from 'axios';
import './Dashboard.css';
import api from "../api/axios"
import {getRelativeTime} from "../utils/timeFormatter.js"
import Sidebar from '../components/Sidebar.jsx';
import {useAuth} from '../context/AuthContext.jsx'

/* ── Material Symbol helper ── */
const Icon = ({ name, className = '' }) => (
  <span className={`ms-icon material-symbols-outlined ${className}`}>{name}</span>
);

/* ── Weekly chart data ── */
const CHART_BARS = [
  { day: 'M', height: '40%', opacity: 0.38 },
  { day: 'T', height: '65%', opacity: 0.55 },
  { day: 'W', height: '90%', opacity: 0.78 },
  { day: 'T', height: '55%', opacity: 0.48 },
  { day: 'F', height: '100%', opacity: 1 },
  { day: 'S', height: '75%', opacity: 0.65 },
  { day: 'S', height: '28%', opacity: 0.28 },
];

/* ── Nav items ── */
const NAV_ITEMS = [
  { icon: 'dashboard',      label: 'Dashboard',   path: '/dashboard' ,active: true },
  { icon: 'assignment',     label: 'Tasks',       path: '/tasks' },
  { icon: 'event',          label: 'Events',      path: '/events' },
  { icon: 'monitoring',     label: 'Analytics',   path: '/Analytics' },
  { icon: 'psychology',     label: 'AI Planner',  path: '/ai-planner' },
  { icon: 'account_circle', label: 'Profile',     path: '/profile' },
];



export default function Dashboard() {
  const [activeNav, setActiveNav]   = useState('Dashboard');
  const [dashboardStats, setDashboardStats] = useState({
    totalTasks: 0,
    completedTasks: 0,
    pendingTasks: 0,
    totalEvents: 0,
    upcomingEvents: 0,    
    todaysEvents:[],
    todaysTasks:[],
    recentActivity:[]
  });

  const findIcon = (action) => {
  // Always good to have a safety check in case 'action' is undefined
  if (!action) return { name: "info", color: "gray" };

  if (action.includes("Deleted") || action.includes("Archived")) {
    return { name: "delete", color: "red" };
  }  
  if (action.includes("Generated") || action.includes("Accepted")) {
    return { name: "auto_awesome", color: "purple" };
  }
  // If it's not deleted or AI-related, it defaults to the edit/create icon
  return { name: "edit_note", color: "blue" };
};

  

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [animated, setAnimated]     = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const ringRef = useRef(null);

  const {user,token,logout} =useAuth();
  
  const fetchDashboard = async () => {

    if (!token) {
        setLoading(false);
        return;
    }

    try {
        const res = await api.get(
            "/dashboard"
        );

        setDashboardStats(res.data);

    } catch (err) {
        console.error(err);

        setError(
            err.response?.data?.message ||
            err.message ||
            "Unable to load dashboard metrics"
        );
    } finally {
        setLoading(false);
    }
};

useEffect(() => {
    fetchDashboard();
}, [token]);


  /* animate bars + ring on mount */
  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 300);
    return () => clearTimeout(t);
  }, []);

  /* ring animation */
  const completionRate = dashboardStats.totalTasks
    ? Math.round((dashboardStats.completedTasks / dashboardStats.totalTasks) * 100)
    : 0;
  const ringStrokeOffset = 289.03 - (289.03 * completionRate) / 100;

  useEffect(() => {
    if (animated && ringRef.current) {
      ringRef.current.style.strokeDashoffset = '289.03';
      requestAnimationFrame(() => {
        ringRef.current.style.transition = 'stroke-dashoffset 1.3s ease-out';
        ringRef.current.style.strokeDashoffset = `${ringStrokeOffset}`;
      });
    }
  }, [animated, ringStrokeOffset]);

  const toggleTask = async(task) => {
        await api.patch(`/tasks/${task.id}/completed` ,
          { completed :!task.completed}
        );
        await fetchDashboard();
  };
  const navigate=useNavigate();
  const handleLogout=()=>{
    logout();
    navigate("/login");
  }

  return (
    <div className="db-root">

      <Sidebar
       NAV_ITEMS={NAV_ITEMS}
       // avatarImage={avatarImage}
       user={user}
      />

      {/* ══ MAIN ══ */}
      <main className="db-main">

        {/* Header */}
        <header className="db-header">
          <div>
            <h2>Welcome back, {user?.username}!</h2>
            <p className="db-subtitle">Here's your productivity overview for today.</p>
          </div>
          {/* <div className="db-header-actions">
            <div className="db-search glass-card">
              <Icon name="search" />
              Quick search (⌘K)
            </div>
            <button className="db-notif-btn glass-card" aria-label="Notifications">
              <Icon name="notifications" />
            </button>
          </div> */}
        </header>

        {/* ── Stats Row ── */}
        <div className="db-stats-row">
          {[
            { cls: 'stat-primary',   icon: 'task_alt',      badge: '+12%',  label: 'Total Tasks',      val: dashboardStats.totalTasks },
            { cls: 'stat-secondary', icon: 'check_circle',  badge: 'Done',  label: 'Completed Tasks',  val: dashboardStats.completedTasks },
            { cls: 'stat-tertiary',  icon: 'pending',       badge: `${dashboardStats.pendingTasks} left`, label: 'Pending Tasks',  val: dashboardStats.pendingTasks },
            { cls: 'stat-event',     icon: 'calendar_month',badge: 'next 7 days', label: 'Upcoming Events',  val: dashboardStats.upcomingEvents  },
          ].map(({ cls, icon, badge, label, val }) => (
            <div key={label} className={`glass-card db-stat-card ${cls}`}>
              <div className="db-stat-top">
                <div className="db-stat-icon"><Icon name={icon} /></div>
                <span className="db-stat-badge">{badge}</span>
              </div>
              <p className="db-stat-label">{label}</p>
              <p className="db-stat-value">{val}</p>
            </div>
          ))}
        </div>

        {/* ── AI Insight + Progress Ring ── */}
        {/* <div className="db-mid-row">
          <div className="glass-card db-ai-card">
            <div className="db-ai-badge"><Icon name="bolt" /> AI INSIGHT</div>
            <h3>Smart Productivity Suggestion</h3>
            <p>"You're most productive at 10 AM. We've scheduled your deep work session then to optimize your cognitive peak."</p>
            <div className="db-ai-actions">
              <button className="btn-primary">Accept Schedule</button>
              <button className="btn-secondary">See Details</button>
            </div>
          </div>

          <div className="glass-card db-progress-card">
            <div className="db-ring-wrap">
              <svg viewBox="0 0 110 110">
                <circle className="ring-track" cx="55" cy="55" r="46" strokeWidth="8" fill="none" />
                <circle
                  ref={ringRef}
                  className="ring-fill"
                  cx="55" cy="55" r="46"
                  strokeWidth="8" fill="none"
                  strokeDasharray="289.03"
                  strokeDashoffset="289.03"
                />
              </svg>
              <div className="db-ring-label"><span>{Math.round(dashboardStats.completedTasks * 100/dashboardStats.totalTasks)}</span></div>
            </div>
            <h4>Goal Completion</h4>
            <p>You're 15% ahead of your<br />weekly target!</p>
          </div>
        </div> */}

        {/* ── Today's Tasks + Right Column ── */}
        <div className="db-bottom-row">

          {/* Tasks */}
          <div className="glass-card db-tasks-card">
            <div className="db-card-header">
              <h3>Today's Tasks</h3>
              <button className="db-view-all">View All <Icon name="chevron_right" /></button>
            </div>
            <div className="db-tasks-list">
              {dashboardStats.todaysTasks.map(task => (
                <div
                  key={task.id}
                  className="db-task-item"
                  onClick={() => toggleTask(task)}
                >
                  <div className="db-task-left">
                    <div className={`db-checkbox ${task.completed ? 'done' : ''}`}>
                      {task.completed && <Icon name="done" />}
                    </div>
                    <div className="db-task-info">
                      <p className={task.completed ? 'done-text' : ''}>{task.title}</p>
                      <p>{task.description}</p>
                    </div>
                  </div>
                  <span className={`db-badge badge-${task.priority.toLowerCase()}`}>{task.priority}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Right column */}
          <div className="db-right-col">

            {/* Weekly Activity Chart */}
            <div className="glass-card db-chart-card">
              <div className="db-chart-header">
                <h3>Weekly Activity</h3>
                <span>Past 7 Days</span>
              </div>
              <div className="db-bar-chart">
                {CHART_BARS.map(({ day, height, opacity }, i) => (
                  <div key={i} className="db-bar-col">
                    <div className="db-bar-track">
                      <div
                        className="db-bar-fill"
                        style={{
                          height: animated ? height : '0%',
                          background: `rgba(0,88,190,${opacity})`,
                        }}
                      />
                    </div>
                    <span className="db-bar-day">{day}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Upcoming Events */}
            <div className="glass-card db-events-card">
              <h3>Upcoming Events</h3>
              <div className="db-timeline">
                {dashboardStats.todaysEvents.map(({ priority, title, event_time }) => (
                  <div key={title} className="db-event-item">
                    <div className={`db-event-dot dot-${priority}`} />
                    <p>{title}</p>
                    <p>{event_time}</p>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>{/* /bottom-row */}

        {/* ── Recent Activity Table ── */}
        <div className="glass-card db-activity-section">
          <div className="db-card-header">
            <h3>Recent Activity</h3>
            <button className="db-filter-btn">
              <Icon name="filter_list" /> Filter
            </button>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="db-table">
              <thead>
                <tr>
                  <th>Action</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {dashboardStats.recentActivity.map(({ id,action,Time }) => (
                  <tr key={id}>
                    <td>
                      <div className="db-action-cell">
                        <div className={`db-action-icon ${findIcon(action).color}`}><Icon name={findIcon(action).name} /></div>
                        <span style={{ fontWeight: 600 }}>{action}</span>
                      </div>
                    </td>
                  
                    <td className="db-time-cell">{getRelativeTime(Time)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </main>

      {/* ── FAB ── */}
      <div
        className="db-fab-wrap"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <button className="db-fab" aria-label="Create New Task">
          <Icon name="add" />
        </button>
        {showTooltip && <div className="db-fab-tooltip">Create New Task</div>}
      </div>

    </div>
  );
}