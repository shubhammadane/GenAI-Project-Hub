const Icon = ({ name, className = "", style = {} }) => (
  <span className={`ms-icon material-symbols-outlined ${className}`} style={style}>{name}</span>
);

import { useAuth } from "../context/AuthContext";

export default function ChatWindow({
  activeSession,
  handleAcceptPrompt,
  generating,
  handleGenerate,
  messagesEndRef,
  inputVal,
  setInputVal
}) {
    const {user}=useAuth();
    return (
        
        <>
      <main className="pl-chat-col">
        <div className="pl-chat-messages">
          {!activeSession || activeSession.messages.length === 0 ? (
            /* Welcome Center Dashboard View */
            <div className="pl-welcome-wrap">
              <div className="pl-welcome-icon-box">
                <Icon name="psychology" />
              </div>
              <h2 className="pl-welcome-title">AI Task Planner</h2>
              <p className="pl-welcome-subtitle">
                Transform your abstract goals into actionable, hour-by-hour schedules with intelligent
                task decomposition.
              </p>
            </div>
          ) : (
            /* Messages List View */
            activeSession.messages.map((msg, i) => (
              <div key={i} className={`pl-message-row ${msg.sender}`}>
                {msg.sender === "ai" && (
                  <div className="pl-msg-avatar">
                    <Icon name="smart_toy" />
                  </div>
                )}
                
                <div className="pl-msg-bubble">
                  {msg.text}

                  {/* Plan Metadata Row */}
                  {msg.sender === "ai" && msg.planId && (
                    <div className="pl-plan-meta" style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
                      gap: "12px",
                      marginTop: "14px",
                      padding: "12px",
                      background: "rgba(0, 88, 190, 0.04)",
                      borderRadius: "12px",
                      border: "1px solid rgba(0, 88, 190, 0.08)",
                      fontSize: "12px",
                      color: "var(--on-surface)"
                    }}>
                      <div>
                        <strong style={{ color: "var(--outline)" }}>Goal:</strong>
                        <div style={{ fontWeight: "700", marginTop: "2px" }}>{msg.planGoal}</div>
                      </div>
                      <div>
                        <strong style={{ color: "var(--outline)" }}>Duration:</strong>
                        <div style={{ fontWeight: "700", marginTop: "2px" }}>{msg.durationDays} Days</div>
                      </div>
                      <div>
                        <strong style={{ color: "var(--outline)" }}>Difficulty:</strong>
                        <div style={{ fontWeight: "700", marginTop: "2px" }}>{msg.planDifficulty}</div>
                      </div>
                      {msg.estimatedHoursPerDay && (
                        <div>
                          <strong style={{ color: "var(--outline)" }}>Est. Hours/Day:</strong>
                          <div style={{ fontWeight: "700", marginTop: "2px" }}>{msg.estimatedHoursPerDay} hrs</div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Decomposed Breakdown & Flow Attachments */}
                  {msg.hasAttachments && (
                    <div className="pl-msg-attachments">
                      {/* Task Breakdown Card */}
                      <div className="pl-attach-card purple-theme">
                        <div className="pl-attach-header">
                          <Icon name="schema" />
                          <h4 className="pl-attach-title">{msg.breakdownTitle}</h4>
                        </div>
                        <div className="pl-tasks-breakdown">
                          {msg.breakdownTasks.map((t, idx) => (
                            <div key={idx} className="pl-breakdown-item">
                              <span className={`pl-circle-indicator ${t.checked ? "checked" : ""}`}></span>
                              <div className="pl-breakdown-info">
                                <span className="pl-breakdown-name">{t.name}</span>
                                <span className="pl-breakdown-desc">{}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Today's Optimized Flow Card */}
                      <div className="pl-attach-card blue-theme">
                        <div className="pl-attach-header">
                          <Icon name="today" />
                          <h4 className="pl-attach-title">{msg.flowTitle}</h4>
                        </div>
                        <div className="pl-flow-timeline">
                          {msg.flowBlocks.map((f, idx) => (
                            <div key={idx} className="pl-timeline-row">
                              <span className="pl-timeline-time">{f.time}</span>
                              <div className={`pl-timeline-block ${f.bg}`}>{f.name}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Attachment specific quick suggestions */}
                  {msg.sender === "ai" && msg.planId && (
                    <div className="pl-msg-actions">
                      <button
                        className="pl-accept-plan-btn"
                        onClick={() => handleAcceptPrompt(msg.planId)}
                        disabled={generating || msg.status === "Accepted"}
                        style={msg.status === "Accepted" ? { background: "rgba(0, 88, 190, 0.2)", cursor: "not-allowed", color: "var(--outline)" } : {}}
                      >
                        {msg.status === "Accepted" ? "Plan Accepted" : "Accept Generated Plan"}
                      </button>
                    </div>
                  )}

                </div>

                {msg.sender === "user" && (
                  <div className="pl-msg-avatar">
                    {user.username[0].toUpperCase()}
                  </div>
                )}
              </div>
            ))
          )}

          {/* Typing Loading Indicator */}
          {generating && (
            <div className="pl-message-row ai">
              <div className="pl-msg-avatar">
                <Icon name="smart_toy" />
              </div>
              <div className="pl-msg-bubble">
                <div className="pl-typing-indicator">
                  <span className="pl-dot"></span>
                  <span className="pl-dot"></span>
                  <span className="pl-dot"></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Prompt bottom bar */}
        <div className="pl-input-area">
          <div className="pl-input-bar-wrap">
            <button className="pl-attach-btn" onClick={() => alert("File attachment clicked")}>
              <Icon name="attach_file" />
            </button>
            <input
              type="text"
              className="pl-text-input"
              placeholder="Type your goal or paste a project brief..."
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleGenerate();
              }}
              disabled={generating}
            />
            <button
              className="pl-generate-btn"
              onClick={() => handleGenerate()}
              disabled={generating}
            >
              <span>Generate</span>
              <Icon name="auto_awesome" />
            </button>
          </div>
          <span className="pl-disclaimer">TaskPilot AI can make mistakes. Check important info.</span>
        </div>
      </main>
      </>
    )
}