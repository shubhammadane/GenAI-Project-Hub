import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import axios from "axios"
import "./Login.css"
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";

// Inline SVGs for self-contained, light-weight modern icons
const BrainLogoIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1 0-3.12 3.02 3.02 0 0 1 0-3.88 2.5 2.5 0 0 1 0-3.12A2.5 2.5 0 0 1 9.5 2Z"></path>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 0-3.12 3.02 3.02 0 0 0 0-3.88 2.5 2.5 0 0 0 0-3.12A2.5 2.5 0 0 0 14.5 2Z"></path>
  </svg>
)

const MailIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="input-icon" viewBox="0 0 24 24">
    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
    <polyline points="22,6 12,13 2,6"></polyline>
  </svg>
)

const LockIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="input-icon" viewBox="0 0 24 24">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
  </svg>
)

const ArrowForwardIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="btn-submit-icon" viewBox="0 0 24 24">
    <line x1="5" y1="12" x2="19" y2="12"></line>
    <polyline points="12 5 19 12 12 19"></polyline>
  </svg>
)

const TerminalIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="social-btn-icon" viewBox="0 0 24 24">
    <polyline points="4 17 10 11 4 5"></polyline>
    <line x1="12" y1="19" x2="20" y2="19"></line>
  </svg>
)

export default function Login() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [errorMsg, setErrorMsg] = useState("")
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const {login} =useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrorMsg("")
    setLoading(false)

    if (!email || !password) {
      setErrorMsg("Please enter both email and password.")
      return
    }

    try {
      setLoading(true)
      const res = await api.post("/auth/login", {
        email,
        password,
      });
      login({token:res.data.token ,user:res.data.user});
      
      navigate("/dashboard")
    } catch (err) {
      console.error(err)
      setErrorMsg("Invalid credentials. Please try again.")
    } finally {
      setLoading(false)
    }
  };

  return (
    <div className="login-container">
      {/* Ambient Glow */}
      <div className="login-glow-bg"></div>

      <div className="login-content">
        {/* Branding Header */}
        <div className="login-branding">
          <div className="login-logo-container">
            <div className="login-logo-box">
              {/* <BrainLogoIcon /> */}
            </div>
            <h1 className="login-title">TaskPilot AI</h1>
          </div>
          <p className="login-subtitle">Premium Workspace</p>
        </div>

        {/* Login Form Card */}
        <div className="login-card">
          <form className="login-form" onSubmit={handleSubmit}>
            {errorMsg && (
              <div style={{ color: "var(--error)", fontSize: "14px", padding: "8px", background: "var(--error-container)", borderRadius: "var(--rounded-md)", border: "1px solid rgba(186, 26, 26, 0.2)" }}>
                {errorMsg}
              </div>
            )}

            {/* Email Field */}
            <div className="input-group">
              <label className="input-label" htmlFor="email">Email</label>
              <div className="input-wrapper">
                <MailIcon />
                <input
                  id="email"
                  type="email"
                  className="login-input"
                  placeholder="name@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="input-group">
              <div className="input-label-row">
                <label className="input-label" htmlFor="password">Password</label>
                <a href="#forgot" className="forgot-password-link">Forgot Password?</a>
              </div>
              <div className="input-wrapper">
                <LockIcon />
                <input
                  id="password"
                  type="password"
                  className="login-input"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* Remember Me */}
            <div className="remember-row">
              <input
                id="remember"
                type="checkbox"
                className="remember-checkbox"
              />
              <label htmlFor="remember" className="remember-label">Remember me</label>
            </div>

            {/* Submit Button */}
            <button className="btn-submit" type="submit" disabled={loading}>
              {loading ? "Logging in..." : "Login"}
              {!loading && <ArrowForwardIcon />}
            </button>
          </form>
        </div>

        {/* Register Link */}
        <p className="signup-redirect">
          Don't have an account?
          <Link to="/register" className="signup-link">Sign up</Link>
        </p>

        {/* Footer Small */}
        <footer className="login-footer">
          <p className="login-footer-text">© 2026 TaskPilot AI. All rights reserved.</p>
        </footer>
      </div>

      {/* Side Graphic (Watermark Accent) */}
      <div className="login-watermark">
        <h2 className="watermark-text-primary">Productivity</h2>
        <h2 className="watermark-text-tertiary">Accelerated</h2>
      </div>
    </div>
  )
}