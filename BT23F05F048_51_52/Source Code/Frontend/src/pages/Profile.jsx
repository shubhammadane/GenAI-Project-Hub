import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import "./Profile.css";
import api from "../api/axios";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";
/* ── Material Symbol helper ── */
const Icon = ({ name, className = "" }) => (
  <span className={`ms-icon material-symbols-outlined ${className}`}>{name}</span>
);

/* ── Navigation Items ── */
const NAV_ITEMS = [
  { icon: "dashboard", label: "Dashboard", path: "/dashboard" },
  { icon: "assignment", label: "Tasks", path: "/tasks" },
  { icon: "event", label: "Events", path: "/events" },
  { icon: "monitoring", label: "Analytics", path: "/Analytics" },
  { icon: "psychology", label: "AI Planner", path: "/ai-planner" },
  { icon: "account_circle", label: "Profile", path: "/profile", active: true },
];

export default function Profile() {
  // const [user, setUser] = useState(null);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [pushNotifications, setPushNotifications] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const navigate = useNavigate();

  const {user,token,logout}=useAuth();

  // const authHeaders = {
  //   headers: {
  //     Authorization: `Bearer ${token}`,
  //   },
  // };

  // Fetch User profile on mount
  useEffect(() => {
    const fetchProfile = async () => {
      if (!token) return;
      try {
        const res = await api.get("/auth/profile");
        setUser(res.data.user);
      } catch (err) {
        console.error("Error fetching user profile:", err);
      }
    };
    // fetchProfile();

    // Check if dark mode is active on html
    const isDark = document.documentElement.classList.contains("dark");
    setDarkMode(isDark);
  }, []);

  // Logout operations
  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  // Toggle theme class on html
  const handleThemeToggle = () => {
    const nextDark = !darkMode;
    setDarkMode(nextDark);
    if (nextDark) {
      document.documentElement.classList.add("dark");
      document.documentElement.classList.remove("light");
    } else {
      document.documentElement.classList.remove("dark");
      document.documentElement.classList.add("light");
    }
  };

  // Computed fields
  const username = user?.username || user?.email?.split("@")[0] || "Alex Rivers";
  const userEmail = user?.email || "alex.rivers@taskpilot.ai";
  
  // Custom Unsplash developer avatar matching the screenshot
  const avatarImage = "https://images.unsplash.com/vector-1742875355318-00d715aec3e8?q=80&w=880&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D/photo-1534528741775-53994a69daeb?auto=format&fit=facearea&facepad=2&w=256&h=256&q=80";

  return (
    <div className="pr-root">
      <Sidebar
        NAV_ITEMS={NAV_ITEMS}
        // avatarImage={avatarImage}
        user={user}
      />
      {/* ══ MAIN CONTENT ══ */}
      <main className="pr-main">
        {/* Header */}
        <header className="pr-header">
          <div>
            <h2>User Profile</h2>
            <p className="pr-subtitle">Manage your account preferences and security settings.</p>
          </div>
          <div className="pr-header-actions">
            <div className="pr-theme-toggle">
              <span>Theme</span>
              <button
                className="pr-theme-btn"
                onClick={handleThemeToggle}
                aria-label="Toggle dark mode"
              >
                <Icon name={darkMode ? "light_mode" : "dark_mode"} />
              </button>
            </div>
          </div>
        </header>

        {/* Content Layout Grid */}
        <div className="pr-grid">
          {/* Left Column */}
          <div className="pr-left-col">
            {/* User Profile Card */}
            <div className="glass-card pr-user-card">
              <div className="pr-avatar-container">
                <div className="pr-avatar-main">
                  <img src={avatarImage} alt="Profile" />
                </div>
                <div className="pr-edit-overlay" onClick={() => alert("Avatar upload clicked")}>
                  <Icon name="edit" />
                </div>
              </div>
              <h3 className="pr-user-name">{username}</h3>
              <p className="pr-user-email">{userEmail}</p>

              <div className="pr-divider"></div>

              <div className="pr-meta-row">
                <div className="pr-meta-item">
                  <span className="pr-meta-label">Joined</span>
                  <span className="pr-meta-val">Oct 2023</span>
                </div>
                <div className="pr-meta-item">
                  <span className="pr-meta-label">Plan</span>
                  <span className="pr-meta-val premium">Premium</span>
                </div>
              </div>
            </div>

            {/* Logout Button */}
            <button className="glass-card pr-logout-btn" onClick={handleLogout}>
              <Icon name="logout" />
              Log out from TaskPilot
            </button>
          </div>

          {/* Right Column */}
          <div className="pr-right-col">
            {/* Account Settings */}
            <div className="glass-card pr-settings-card">
              <div className="pr-card-header">
                <Icon name="manage_accounts" />
                <h3>Account Settings</h3>
              </div>

              <div className="pr-rows-list">
                <div className="pr-row-item" onClick={() => alert("Change password flow clicked")}>
                  <div className="pr-row-info">
                    <span className="pr-row-title">Change Password</span>
                    <span className="pr-row-desc">Update your security credentials</span>
                  </div>
                  <Icon name="chevron_right" className="pr-chevron" />
                </div>

                <div className="pr-row-item" onClick={() => alert("Email preferences flow clicked")}>
                  <div className="pr-row-info">
                    <span className="pr-row-title">Email Preferences</span>
                    <span className="pr-row-desc">{userEmail} (Primary)</span>
                  </div>
                  <Icon name="chevron_right" className="pr-chevron" />
                </div>
              </div>
            </div>

            {/* Notification Settings */}
            <div className="glass-card pr-settings-card">
              <div className="pr-card-header">
                <Icon name="notifications" />
                <h3>Notification Settings</h3>
              </div>

              <div className="pr-rows-list">
                {/* Email Notifications Switch */}
                <div className="pr-row-item">
                  <div className="pr-row-info">
                    <span className="pr-row-title">Email Notifications</span>
                    <span className="pr-row-desc">Daily digest and task reminders</span>
                  </div>
                  <label className="pr-switch">
                    <input
                      type="checkbox"
                      checked={emailNotifications}
                      onChange={() => setEmailNotifications(!emailNotifications)}
                    />
                    <span className="pr-slider"></span>
                  </label>
                </div>

                {/* Push Notifications Switch */}
                <div className="pr-row-item">
                  <div className="pr-row-info">
                    <span className="pr-row-title">Push Notifications</span>
                    <span className="pr-row-desc">Real-time alerts on your devices</span>
                  </div>
                  <label className="pr-switch">
                    <input
                      type="checkbox"
                      checked={pushNotifications}
                      onChange={() => setPushNotifications(!pushNotifications)}
                    />
                    <span className="pr-slider"></span>
                  </label>
                </div>

                {/* AI Suggestions Switch */}
                <div className="pr-row-item">
                  <div className="pr-row-info">
                    <span className="pr-row-title">AI Suggestions</span>
                    <span className="pr-row-desc">Smart prioritization and insights</span>
                  </div>
                  <label className="pr-switch">
                    <input
                      type="checkbox"
                      checked={aiSuggestions}
                      onChange={() => setAiSuggestions(!aiSuggestions)}
                    />
                    <span className="pr-slider"></span>
                  </label>
                </div>
              </div>
            </div>

            {/* Bottom Workspace Statistics Banner */}
            <div className="glass-card pr-stats-card">
              <div className="pr-stats-card-left">
                <h4>Workspace Statistics</h4>
                <p>
                  You've completed 142 tasks this month. You're in the top 5% of most productive
                  TaskPilots.
                </p>
              </div>
              <Link to="/Analytics" className="pr-stats-link">
                View full analytics
                <Icon name="arrow_forward" />
              </Link>

              {/* Sparkles and graph watermark vector background */}
              <div className="pr-stats-decor-wrap">
                <svg viewBox="0 0 150 120" xmlns="http://www.w3.org/2000/svg">
                  <defs>
                    <linearGradient id="stats-grad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.2" />
                      <stop offset="100%" stopColor="var(--primary)" stopOpacity="0.0" />
                    </linearGradient>
                  </defs>
                  
                  {/* Shaded Area under path */}
                  <path
                    d="M 10 90 Q 40 70 70 85 T 140 30 L 140 110 L 10 110 Z"
                    fill="url(#stats-grad)"
                  />
                  
                  {/* Smooth line */}
                  <path
                    d="M 10 90 Q 40 70 70 85 T 140 30"
                    fill="none"
                    stroke="var(--primary)"
                    strokeWidth="3.5"
                    strokeLinecap="round"
                  />
                  
                  {/* Endpoint dots */}
                  <circle cx="10" cy="90" r="3" fill="#fff" stroke="var(--primary)" strokeWidth="2" />
                  <circle cx="70" cy="85" r="3" fill="#fff" stroke="var(--primary)" strokeWidth="2" />
                  <circle cx="140" cy="30" r="3" fill="#fff" stroke="var(--primary)" strokeWidth="2" />

                  {/* Sparkle 1 */}
                  <path
                    d="M 30 40 L 32 44 L 36 45 L 32 46 L 30 50 L 28 46 L 24 45 L 28 44 Z"
                    fill="var(--primary)"
                    opacity="0.4"
                  />
                  
                  {/* Sparkle 2 */}
                  <path
                    d="M 110 50 L 112 56 L 118 57.5 L 112 59 L 110 65 L 108 59 L 102 57.5 L 108 56 Z"
                    fill="var(--primary)"
                    opacity="0.5"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
