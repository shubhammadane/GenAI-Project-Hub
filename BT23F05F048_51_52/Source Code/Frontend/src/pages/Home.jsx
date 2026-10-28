import { Link } from "react-router-dom"
import "./Home.css"
import { useAuth} from "../context/AuthContext"
import taskplanner from "../assets/taskplanner.png"
// Inline SVGs for beautiful, self-contained, light-weight modern icons
const SearchIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="nav-search-icon" viewBox="0 0 24 24">
    <circle cx="11" cy="11" r="8"></circle>
    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
  </svg>
)

const PlayIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="watch-demo-icon" viewBox="0 0 24 24" style={{ marginRight: '6px' }}>
    <circle cx="12" cy="12" r="10"></circle>
    <polygon points="10 8 16 12 10 16 10 8"></polygon>
  </svg>
)

const DocIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
    <polyline points="10 9 9 9 8 9"></polyline>
  </svg>
)

const UsersIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
    <circle cx="9" cy="7" r="4"></circle>
    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
  </svg>
)

const ChartIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <line x1="18" y1="20" x2="18" y2="10"></line>
    <line x1="12" y1="20" x2="12" y2="4"></line>
    <line x1="6" y1="20" x2="6" y2="14"></line>
  </svg>
)

const CalendarIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
    <line x1="16" y1="2" x2="16" y2="6"></line>
    <line x1="8" y1="2" x2="8" y2="6"></line>
    <line x1="3" y1="10" x2="21" y2="10"></line>
  </svg>
)

const CheckIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="bullet-icon" viewBox="0 0 24 24">
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
)

const TwitterIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="social-icon" viewBox="0 0 16 16">
    <path d="M5.026 15c6.038 0 9.341-5.003 9.341-9.334 0-.14 0-.282-.006-.422A6.685 6.685 0 0 0 16 3.542a6.658 6.658 0 0 1-1.889.518 3.301 3.301 0 0 0 1.447-1.817 6.533 6.533 0 0 1-2.087.793A3.286 3.286 0 0 0 7.875 6.03a9.325 9.325 0 0 1-6.767-3.429 3.289 3.289 0 0 0 1.018 4.382A3.323 3.323 0 0 1 .64 6.575v.045a3.288 3.288 0 0 0 2.632 3.218 3.203 3.203 0 0 1-.865.115 3.23 3.23 0 0 1-.614-.057 3.283 3.283 0 0 0 3.067 2.277A6.588 6.588 0 0 1 .78 13.58a6.32 6.32 0 0 1-.78-.045A9.344 9.344 0 0 0 5.026 15z"/>
  </svg>
)

const LinkedinIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="social-icon" viewBox="0 0 16 16">
    <path d="M0 1.146C0 .513.526 0 1.175 0h13.65C15.474 0 16 .513 16 1.146v13.708c0 .633-.526 1.146-1.175 1.146H1.175C.526 16 0 15.487 0 14.854V1.146zm4.943 12.248V6.169H2.542v7.225h2.401zm-1.2-8.212c.837 0 1.358-.554 1.358-1.248-.015-.709-.52-1.248-1.342-1.248-.822 0-1.359.54-1.359 1.248 0 .694.521 1.248 1.327 1.248h.016zm4.908 8.212V9.359c0-.216.016-.432.08-.586.173-.431.568-.878 1.232-.878.869 0 1.216.662 1.216 1.634v3.865h2.401V9.25c0-2.22-1.184-3.252-2.764-3.252-1.274 0-1.845.7-2.165 1.193v.025h-.016a5.54 5.54 0 0 1 .016-.025V6.169h-2.4c.03.678 0 7.225 0 7.225h2.4z"/>
  </svg>
)

const ImageIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
    <circle cx="8.5" cy="8.5" r="1.5"></circle>
    <polyline points="21 15 16 10 5 21"></polyline>
  </svg>
)

const GearIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="3"></circle>
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
  </svg>
)

const CpuIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect>
    <rect x="9" y="9" width="6" height="6"></rect>
    <line x1="9" y1="1" x2="9" y2="4"></line>
    <line x1="15" y1="1" x2="15" y2="4"></line>
    <line x1="9" y1="20" x2="9" y2="23"></line>
    <line x1="15" y1="20" x2="15" y2="23"></line>
    <line x1="20" y1="9" x2="23" y2="9"></line>
    <line x1="20" y1="15" x2="23" y2="15"></line>
    <line x1="1" y1="9" x2="4" y2="9"></line>
    <line x1="1" y1="15" x2="4" y2="15"></line>
  </svg>
)

const ArrowRightIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <line x1="5" y1="12" x2="19" y2="12"></line>
    <polyline points="12 5 19 12 12 19"></polyline>
  </svg>
)

export default function Home() {

  const {user,isAuthenticated ,login ,logout } =useAuth();
  
  console.log(user);
  console.log(isAuthenticated)
  return (
    <div className="landing-container">
      {/* Navbar Header */}
      <header className="navbar">
        <div className="content-wrapper" style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Link to="/" className="logo">
            TaskPilot <span className="logo-accent">AI</span>
          </Link>

          <nav className="nav-links">
            <a href="#features" className="nav-link">Features</a>
          </nav>

          <div className="nav-actions">
            <div className="nav-search-container">
              <SearchIcon />
              <input type="text" placeholder="Search features..." className="nav-search-input" />
            </div>

            {isAuthenticated ? ( <button className="btn btn-primary btn-sm btn-pill" onClick={()=>logout()}>log out</button>)
            :(<div>
            <Link to="/login" className="btn btn-ghost btn-sm">Login</Link>
            <Link to="/register" className="btn btn-primary btn-sm btn-pill">Register</Link>
            </div>)
            }

                
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero content-wrapper">
        <div className="hero-content">
          <div className="badge-new">
            <span className="badge-icon"></span>
            NEW: AI Planner Released
          </div>
          <h1 className="hero-title">
            Master Your Time with <em>AI Intelligence</em>
          </h1>
          <p className="hero-desc">
            The next-generation task planner designed for high-performance teams and individuals. Automate scheduling, predict deadlines, and focus on what matters.
          </p>
          <div className="hero-actions">
            <Link to="/register" className="btn btn-primary btn-pill" style={{ padding: '12px 28px' }}>
              Get Started for Free
            </Link>
            <a href="#demo" className="watch-demo-link">
              <PlayIcon />
              Watch Demo
            </a>
          </div>
  
        </div>

        <div className="hero-visual">
          {/* <div className="hero-mockup-wrapper"> */}
            {/* <div className="hero-mockup-bg-shapes">
              <div className="hero-mockup-shape shape-1"></div>
              <div className="hero-mockup-shape shape-2"></div>
            </div> */}
            <div className="hero-mockup-graphic">
              <img src={taskplanner} alt="TaskPlanner preview" />
            </div>
          {/* </div> */}
        </div>
      </section>

      {/* Bento Grid Features Section */}
      <section id="features" className="features-section content-wrapper">
        <h2 className="section-tagline">Supercharge Productivity</h2>
        <p className="section-subtagline">
          Our ecosystem of tools is designed to seamlessly integrate AI into your daily workflow without the friction.
        </p>

        <div className="bento-grid">
          {/* Card 1: AI Task Breakdown */}
          <div className="bento-card span-2">
            <div className="card-icon-wrapper card-icon-blue">
              <DocIcon />
            </div>
            <h3>AI Task Breakdown</h3>
            <p>
              Input a complex goal and let TaskPilot slice it into manageable, actionable steps with estimated timeframes.
            </p>
            <div className="card-vis-breakdown">
              <div className="breakdown-row">
                <span className="breakdown-dot breakdown-dot-blue"></span>
                <div className="breakdown-bar breakdown-bar-1"></div>
                <span className="breakdown-estimate">+2 ESTIMATES</span>
              </div>
              <div className="breakdown-row">
                <span className="breakdown-dot breakdown-dot-purple"></span>
                <div className="breakdown-bar breakdown-bar-2"></div>
              </div>
              <div className="breakdown-row">
                <span className="breakdown-dot breakdown-dot-blue"></span>
                <div className="breakdown-bar breakdown-bar-3"></div>
              </div>
            </div>
          </div>

          {/* Card 2: Collaborative Sync */}
          <div className="bento-card bento-card-lavender">
            <div className="card-icon-wrapper card-icon-purple">
              <UsersIcon />
            </div>
            <h3>Collaborative Sync</h3>
            <p>
              Real-time presence and multi-user editing for teams that move fast.
            </p>
            <div className="card-vis-collaborative">
              <div className="avatar-stack">
                <div className="avatar avatar-blue">A</div>
                <div className="avatar avatar-purple">J</div>
                <div className="avatar avatar-green">M</div>
                <div className="avatar avatar-more">+8</div>
              </div>
            </div>
          </div>

          {/* Card 3: Insightful Analytics */}
          <div className="bento-card">
            <div className="card-icon-wrapper card-icon-purple">
              <ChartIcon />
            </div>
            <h3>Insightful Analytics</h3>
            <p>
              Visualize bottlenecks and track productivity trends with beautiful dashboards.
            </p>
            <div className="card-vis-analytics">
              <div className="chart-bar chart-bar-1"></div>
              <div className="chart-bar chart-bar-2"></div>
              <div className="chart-bar chart-bar-3"></div>
              <div className="chart-bar chart-bar-4"></div>
              <div className="chart-bar chart-bar-5"></div>
              <div className="chart-bar chart-bar-6"></div>
            </div>
          </div>

          {/* Card 4: Intelligent Scheduling */}
          <div className="bento-card span-2">
            <div className="card-icon-wrapper card-icon-blue">
              <CalendarIcon />
            </div>
            <h3>Intelligent Scheduling</h3>
            <p>
              Our AI cross-references your calendar and tasks to find the optimal slots for deep work.
            </p>
            <div className="card-vis-scheduling">
              <div className="sched-header">
                <span className="sched-title">Deep Work Slot</span>
                <span className="sched-time">8:00 AM - 10:30 AM</span>
              </div>
              <p className="sched-desc">
                *Found a gap in your schedule optimized for high-focus writing.*
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Context Aware Section */}
      <section className="highlight-section content-wrapper">
        <div className="highlight-visual">
          <div className="engine-card">
            <div className="engine-header">
              <div className="engine-logo">
                <CpuIcon />
              </div>
              <span className="engine-title">AI Planner Engine v2.0</span>
            </div>
            <div className="engine-lines">
              <div className="engine-line engine-line-1"></div>
              <div className="engine-line engine-line-2"></div>
              <div className="engine-line engine-line-1" style={{ width: '40%' }}></div>
            </div>
          </div>
        </div>

        <div className="highlight-content">
          <h2>The Future is <span>Context-Aware</span></h2>
          <p>
            Our proprietary AI doesn't just list tasks; it understands your energy levels, project deadlines, and historical productivity patterns to recommend exactly what you should do next.
          </p>
          <div className="highlight-bullets">
            <div className="bullet-item">
              <CheckIcon />
              Priority Prediction Algorithm
            </div>
            <div className="bullet-item">
              <CheckIcon />
              Energy-Level Scheduling
            </div>
            <div className="bullet-item">
              <CheckIcon />
              Automatic Slack & Gmail integration
            </div>
          </div>
        </div>
      </section>

      {/* Beautifully Simple Dashboard Showcase */}
      <section className="showcase-section content-wrapper">
        <h2 className="section-tagline">Beautifully Simple</h2>
        <p className="section-subtagline">
          A workspace that clears the clutter and puts your most important work front and center.
        </p>

        <div className="browser-mockup">
          <div className="browser-header">
            <div className="browser-dots">
              <span className="browser-dot dot-red"></span>
              <span className="browser-dot dot-yellow"></span>
              <span className="browser-dot dot-green"></span>
            </div>
            <div className="browser-address">app.taskpilot.ai/dashboard</div>
            <div className="browser-actions">
              <GearIcon />
              <div className="browser-avatar"></div>
            </div>
          </div>

          <div className="browser-content">
            <aside className="mock-sidebar">
              <div className="mock-sidebar-line mock-sidebar-line-md"></div>
              <div className="mock-sidebar-line mock-sidebar-line-lg" style={{ background: 'rgba(0,88,190,0.15)' }}></div>
              <div className="mock-sidebar-line mock-sidebar-line-sm"></div>
              <div className="mock-sidebar-line mock-sidebar-line-md"></div>
              <div className="mock-sidebar-line mock-sidebar-line-lg"></div>
            </aside>

            <main className="mock-main">
              <div className="mock-focus-header">
                <div className="mock-focus-title">
                  <h4>Your Daily Focus</h4>
                  <p>Monday, June 12th</p>
                </div>
                <button className="btn btn-primary btn-sm" style={{ borderRadius: '6px' }}>New Task</button>
              </div>

              <div className="mock-stats-row">
                <div className="mock-stat-card">
                  <div className="mock-stat-label">Tasks Done</div>
                  <div className="mock-stat-value">24 / 30</div>
                </div>
                <div className="mock-stat-card">
                  <div className="mock-stat-label">Focus Hours</div>
                  <div className="mock-stat-value">8.5 hrs</div>
                </div>
                <div className="mock-stat-card">
                  <div className="mock-stat-label">Efficiency</div>
                  <div className="mock-stat-value mock-stat-value-purple">92%</div>
                </div>
              </div>

              <div className="mock-task-list">
                <div className="mock-task-item">
                  <div className="mock-checkbox"></div>
                  <div className="mock-task-info">
                    <span className="mock-task-title">Finalize Q3 Strategy Deck</span>
                    <span className="mock-task-meta">Design Team • 2:00 PM</span>
                  </div>
                  <span className="mock-task-badge badge-high-priority">HIGH PRIORITY</span>
                </div>

                <div className="mock-task-item">
                  <div className="mock-checkbox mock-checkbox-checked">
                    <CheckIcon />
                  </div>
                  <div className="mock-task-info">
                    <span className="mock-task-title" style={{ textDecoration: 'line-through', opacity: 0.6 }}>Morning Standup Meeting</span>
                    <span className="mock-task-meta" style={{ opacity: 0.6 }}>All Hands • Completed</span>
                  </div>
                </div>
              </div>
            </main>
          </div>
        </div>
      </section>

      {/* Final CTA Banner */}
      <section className="cta-section content-wrapper">
        <div className="cta-banner">
          <h2>Ready to reclaim your time?</h2>
          <p className="cta-subtext">
            Join 20,000+ professionals and teams already scaling their productivity with TaskPilot AI.
          </p>
          <div className="cta-actions">
            <Link to="/register" className="btn btn-primary btn-pill" style={{ padding: '12px 32px' }}>
              Get Started Now
            </Link>
            <a href="#demo" className="btn btn-secondary btn-pill" style={{ padding: '12px 32px' }}>
              Schedule a Demo
            </a>
          </div>
          <span className="cta-note">No credit card required. 14-day free trial.</span>
        </div>
      </section>

      {/* Footer Section */}
      <footer className="footer">
        <div className="content-wrapper">
          <div className="footer-grid">
            <div className="footer-brand">
              <span className="footer-logo">
                TaskPilot <span className="footer-logo-accent">AI</span>
              </span>
              <p className="footer-desc">
                Designing the future of collaborative productivity through intelligent task orchestration.
              </p>
              <div className="footer-socials">
                <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="social-link">
                  <TwitterIcon />
                </a>
                <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="social-link">
                  <LinkedinIcon />
                </a>
              </div>
            </div>

            <div className="footer-col">
              <h5>Product</h5>
              <ul className="footer-links">
                <li className="footer-link-item"><a href="#features">Features</a></li>
                <li className="footer-link-item"><a href="#planner">AI Planner</a></li>
                <li className="footer-link-item"><a href="#integrations">Integrations</a></li>
                <li className="footer-link-item"><a href="#enterprise">Enterprise</a></li>
              </ul>
            </div>

            <div className="footer-col">
              <h5>Resources</h5>
              <ul className="footer-links">
                <li className="footer-link-item"><a href="#docs">Documentation</a></li>
                <li className="footer-link-item"><a href="#community">Community</a></li>
                <li className="footer-link-item"><a href="#api">API Reference</a></li>
                <li className="footer-link-item"><a href="#guides">Guides</a></li>
              </ul>
            </div>

            <div className="footer-col">
              <h5>Company</h5>
              <ul className="footer-links">
                <li className="footer-link-item"><a href="#about">About Us</a></li>
                <li className="footer-link-item"><a href="#careers">Careers</a></li>
                <li className="footer-link-item"><a href="#blog">Blog</a></li>
                <li className="footer-link-item"><a href="#press">Press</a></li>
              </ul>
            </div>

            <div className="footer-col">
              <h5>Legal</h5>
              <ul className="footer-links">
                <li className="footer-link-item"><a href="#privacy">Privacy Policy</a></li>
                <li className="footer-link-item"><a href="#terms">Terms of Service</a></li>
                <li className="footer-link-item"><a href="#cookies">Cookie Settings</a></li>
              </ul>
            </div>
          </div>

          <div className="footer-bottom">
            <span>© 2026 TaskPilot AI. All rights reserved. Built for high performance.</span>
            <div className="footer-status">
              <span>Status:</span>
              <span className="status-indicator"></span>
              <span style={{ color: '#10b981', fontWeight: 600 }}>Operational</span>
              <span>• v2.4.0</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}