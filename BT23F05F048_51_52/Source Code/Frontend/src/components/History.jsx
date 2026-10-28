const Icon = ({ name, className = "", style = {} }) => (
  <span className={`ms-icon material-symbols-outlined ${className}`} style={style}>{name}</span>
);

export default function History({
  handleNewChat,
  searchQuery,
  setSearchQuery,
  filteredSessions = [],
  activeSessionId,
  setActiveSessionId,
  setGenerating
}) {
    return(
        <div className="pl-history-panel">
        <div className="pl-history-header">
          <h2>History</h2>
          <button className="pl-new-chat-btn" onClick={handleNewChat} title="New Planning Session">
            <Icon name="add_box" />
          </button>
        </div>

        {/* Optional History Search Bar */}
        <div
          style={{
            position: "relative",
            marginBottom: "16px",
          }}
        >
          <input
            type="text"
            placeholder="Search history..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              padding: "8px 12px 8px 34px",
              border: "1px solid rgba(114, 119, 133, 0.15)",
              borderRadius: "8px",
              fontSize: "12px",
              background: "#fff",
              outline: "none",
            }}
          />
          <Icon
            name="search"
            style={{
              position: "absolute",
              left: "10px",
              top: "50%",
              transform: "translateY(-50%)",
              fontSize: "16px",
              color: "var(--outline)",
            }}
          />
        </div>

        <ul className="pl-history-list">
          {filteredSessions.map((session) => (
            <li key={session.id} className="pl-history-item">
              <button
                className={`pl-history-card ${activeSessionId === session.id ? "active" : ""}`}
                onClick={() => {
                  setActiveSessionId(session.id);
                  setGenerating(false);
                }}
              >
                <span className="pl-history-title">{session.title}</span>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%", marginTop: "2px" }}>
                  <span className="pl-history-time" style={{ fontSize: "10px", color: "var(--outline)" }}>{session.time}</span>
                  <span style={{
                    fontSize: "9px",
                    fontWeight: "700",
                    textTransform: "uppercase",
                    padding: "2px 6px",
                    borderRadius: "99px",
                    background: session.status === "Accepted" ? "rgba(0, 88, 190, 0.08)" : "rgba(114, 119, 133, 0.08)",
                    color: session.status === "Accepted" ? "var(--primary)" : "var(--outline)",
                  }}>
                    {session.status || "Pending"}
                  </span>
                </div>
              </button>
            </li>
          ))}
          {filteredSessions.length === 0 && (
            <p style={{ fontSize: "12px", color: "var(--outline)", textAlign: "center", marginTop: "20px" }}>
              No history found
            </p>
          )}
        </ul>
      </div>
    )
}