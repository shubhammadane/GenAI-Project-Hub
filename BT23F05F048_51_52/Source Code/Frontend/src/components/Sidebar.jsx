import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import './Sidebar.css';

const Icon = ({ name, className = "" }) => (
  <span className={`ms-icon material-symbols-outlined ${className}`}>{name}</span>
);

export default function Sidebar({ NAV_ITEMS = [], avatarImage, user, children }) {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    const className = "sidebar-collapsed";
    if (collapsed) {
      document.body.classList.add(className);
    } else {
      document.body.classList.remove(className);
    }
    return () => {
      document.body.classList.remove(className);
    };
  }, [collapsed]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <aside className={`pl-sidebar ${collapsed ? "collapsed" : ""} ${children ? "with-history" : ""}`}>
      <div className="pl-brand">
        <div className="pl-brand-text">
          <h1>TaskPilot AI</h1>
          <p>Premium Workspace</p>
        </div>
        <button
          type="button"
          className="pl-sidebar-toggle"
          onClick={() => setCollapsed((prev) => !prev)}
          aria-label={collapsed ? "Open sidebar" : "Close sidebar"}
        >
          <Icon name={collapsed ? "chevron_right" : "chevron_left"} />
        </button>
      </div>

      <ul className="pl-nav">
        {NAV_ITEMS.map(({ icon, label, path, active }) => (
          <li key={label}>
            <Link to={path} className={`pl-nav-item ${active ? "active" : ""}`}>
              <Icon name={icon} />
              <span className="pl-nav-label">{label}</span>
            </Link>
          </li>
        ))}
      </ul>

      {children && !collapsed? <div className="pl-history-slot">{children}</div> : null}

      <div className="pl-sidebar-bottom">
        <div className="pl-user-profile">
          <div className="pl-avatar">{user?.username?.[0]?.toUpperCase()}</div>
          <div className="pl-user-info">
            <p>{user?.username}</p>
            <p>{user?.role}</p>
          </div>
          <button className="pl-logout-btn" onClick={handleLogout} title="Log Out">
            <Icon name="logout" />
          </button>
        </div>
      </div>
    </aside>
  );
}