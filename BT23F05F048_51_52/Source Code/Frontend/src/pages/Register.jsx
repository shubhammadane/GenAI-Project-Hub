import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import "./Register.css";
import api from "../api/axios";
import {useAuth} from "../context/AuthContext";

export default function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [agreeToTerms, setAgreeToTerms] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const {login} =useAuth();
  const navigate = useNavigate();

  const register = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setSuccess(false);

    if (!username.trim() || !email.trim() || !password || !confirmPassword) {
      setErrorMsg("All fields are required.");
      return;
    }

    if (password !== confirmPassword) {
      setErrorMsg("Passwords do not match.");
      return;
    }

    if (!agreeToTerms) {
      setErrorMsg("You must agree to the Terms of Service and Privacy Policy.");
      return;
    }

    try {
      setLoading(true);
      
      // Post registration request to backend
      await api.post("/auth/register", {
        username,
        email,
        password,
      });

      // Automatically log in the user upon successful registration
      const result = await api.post("/auth/login", {
        email,
        password,
      });

     
      login({token:result.data.token ,user:result.data.user});

      setSuccess(true);

      // Brief animation buffer before redirection
      setTimeout(() => {
        navigate("/dashboard");
      }, 1500);
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data && err.response.data.message) {
        setErrorMsg(err.response.data.message);
      } else {
        setErrorMsg("Registration failed. Please try again.");
      }
    } finally {
      if (!success) {
        setLoading(false);
      }
    }
  };

  return (
    <div className="register-container">
      {/* Fixed Header Navigation */}
      <header className="register-header">
        <div className="register-header-logo">
          <span
            className="material-symbols-outlined text-primary text-3xl"
            style={{ fontVariationSettings: "'FILL' 1" }}
          >
            psychology
          </span>
          <span className="register-logo-text">TaskPilot AI</span>
        </div>
        <div>
          <Link className="register-header-link" to="/">
            Back to home
            <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
          </Link>
        </div>
      </header>

      {/* Atmospheric Background glow circles */}
      <div className="register-glow-bg">
        <div className="register-glow-1"></div>
        <div className="register-glow-2"></div>
      </div>

      {/* Main Container */}
      <main className="register-main">
        <div className="register-content">
          {/* Welcome Intro */}
          <div className="register-welcome-header">
            <h1 className="register-welcome-title">Create your workspace</h1>
            <p className="register-welcome-subtitle">
              Intelligent precision for high-velocity teams.
            </p>
          </div>

          {/* Registration Card */}
          <div className="register-card">
            <form className="register-form" onSubmit={register}>
              {errorMsg && (
                <div
                  style={{
                    color: "var(--error)",
                    fontSize: "14px",
                    padding: "10px",
                    background: "var(--error-container)",
                    borderRadius: "var(--rounded-md)",
                    border: "1px solid rgba(186, 26, 26, 0.2)",
                  }}
                >
                  {errorMsg}
                </div>
              )}

              {/* Username Input */}
              <div className="register-input-group">
                <label className="register-input-label" htmlFor="username">
                  Username
                </label>
                <div className="register-input-wrapper">
                  <span className="material-symbols-outlined register-input-icon">
                    person
                  </span>
                  <input
                    className="register-input"
                    id="username"
                    name="username"
                    placeholder="johndoe"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* Email Address Input */}
              <div className="register-input-group">
                <label className="register-input-label" htmlFor="email">
                  Email Address
                </label>
                <div className="register-input-wrapper">
                  <span className="material-symbols-outlined register-input-icon">
                    mail
                  </span>
                  <input
                    className="register-input"
                    id="email"
                    name="email"
                    placeholder="name@company.com"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* Password Grid */}
              <div className="register-password-grid">
                <div className="register-input-group">
                  <label className="register-input-label" htmlFor="password">
                    Password
                  </label>
                  <div className="register-input-wrapper">
                    <span className="material-symbols-outlined register-input-icon">
                      lock
                    </span>
                    <input
                      className="register-input"
                      id="password"
                      name="password"
                      placeholder="••••••••"
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="register-input-group">
                  <label className="register-input-label" htmlFor="confirm_password">
                    Confirm
                  </label>
                  <div className="register-input-wrapper">
                    <span className="material-symbols-outlined register-input-icon">
                      verified_user
                    </span>
                    <input
                      className="register-input"
                      id="confirm_password"
                      name="confirm_password"
                      placeholder="••••••••"
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Terms Checkbox */}
              <div className="register-terms-row">
                <input
                  className="register-terms-checkbox"
                  id="terms"
                  type="checkbox"
                  checked={agreeToTerms}
                  onChange={(e) => setAgreeToTerms(e.target.checked)}
                  required
                />
                <label className="register-terms-label" htmlFor="terms">
                  I agree to the{" "}
                  <a className="register-terms-link" href="#terms" onClick={(e) => e.preventDefault()}>
                    Terms of Service
                  </a>{" "}
                  and{" "}
                  <a className="register-terms-link" href="#privacy" onClick={(e) => e.preventDefault()}>
                    Privacy Policy
                  </a>
                  .
                </label>
              </div>

              {/* CTA Submit Button */}
              <button
                className={`register-btn-submit ${success ? "success" : ""}`}
                type="submit"
                disabled={loading || success}
              >
                {success ? (
                  <>
                    <span className="material-symbols-outlined">check_circle</span> Success!
                  </>
                ) : loading ? (
                  <>
                    <span className="material-symbols-outlined animate-spin">sync</span> Creating...
                  </>
                ) : (
                  <>
                    Create Account
                    <span className="material-symbols-outlined">rocket_launch</span>
                  </>
                )}
              </button>

            </form>

            {/* Redirect back to Login */}
            <div className="register-redirect">
              Already have an account?
              <Link className="register-redirect-link" to="/login">
                Login
              </Link>
            </div>
          </div>

        </div>
      </main>

      {/* Visual Bento Accent: Bottom Left AI status */}
      <div className="badge-active-planning">
        <div className="badge-active-planning-card">
          <div className="badge-active-planning-icon-box">
            <span className="material-symbols-outlined text-[22px]">auto_awesome</span>
          </div>
          <div>
            <p className="badge-active-planning-title">AI Planning Active</p>
            <p className="badge-active-planning-subtitle">Setting up your neural workspace...</p>
          </div>
        </div>
      </div>

      {/* Visual Bento Accent: Top Right system status */}
      <div className="badge-system-status">
        <div className="badge-system-status-card">
          <div className="badge-dots-row">
            <div className="badge-dot active"></div>
            <div className="badge-dot"></div>
            <div className="badge-dot"></div>
          </div>
          <p className="badge-system-status-text">system_status: initializing</p>
        </div>
      </div>
    </div>
  );
}