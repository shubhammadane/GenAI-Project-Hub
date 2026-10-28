import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./AIPlanner.css";
import "./Tasks.css"; // Reuse modal overlay and input styling classes
import api from "../api/axios";
import History from "../components/History";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import {useAuth} from "../context/AuthContext";


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
  { icon: "psychology", label: "AI Planner", path: "/ai-planner", active: true },
  { icon: "account_circle", label: "Profile", path: "/profile" },
]; 




export default function AIPlanner() {
  const navigate = useNavigate();

  const [conversations, setConversations] = useState({});
  const [activeSessionId, setActiveSessionId] = useState("session-1");
  const [searchQuery, setSearchQuery] = useState("");
  const [inputVal, setInputVal] = useState("");
  const [generating, setGenerating] = useState(false);
  // const [user, setUser] = useState(null);
  const messagesEndRef = useRef(null);

  // Accept Modal States
  const [isAcceptModalOpen, setIsAcceptModalOpen] = useState(false);
  const [acceptPlanId, setAcceptPlanId] = useState(null);
  const [acceptStartDate, setAcceptStartDate] = useState("");
  const [acceptScheduleMode, setAcceptScheduleMode] = useState("daily");
  const [acceptScheduleDays, setAcceptScheduleDays] = useState("");
  const [acceptLoading, setAcceptLoading] = useState(false);
  const [acceptSuccess, setAcceptSuccess] = useState(false);
  const [acceptError, setAcceptError] = useState("");

  const {user,token,logout} =useAuth();
  

  // Scroll to bottom on new messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversations, activeSessionId, generating]);

  // Fetch User profile on mount
  useEffect(() => {
    const fetchProfile = async () => {
      if (!token) return;
      try {
        const res = await api.get("/auth/profile");
        setUser(res.data.user);
      } catch (err) {
        console.error("Error fetching user profile in AIPlanner:", err);
      }
    };

  }, []);

  // Fetch Saved Plans from History
  const fetchPlans = async () => {
    if (!token) return;
    try {
      const res = await api.get("/ai/plans");
      const plans = res.data;

      if (plans && plans.length > 0) {
        const planSessions = {};
        plans.forEach((plan) => {
          planSessions[plan.id.toString()] = {
            id: plan.id.toString(),
            title: plan.goal || plan.prompt || "Unnamed Plan",
            time: new Date(plan.created_at || plan.created_date).toLocaleDateString(),
            status: plan.status || "Pending",
            messages: [],
          };
        });

        setConversations(planSessions);
        
        // Default to active session being the first plan
        const firstPlanId = plans[0].id.toString();
        setActiveSessionId(firstPlanId);
      }
    } catch (err) {
      console.error("Error loading plans:", err);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, []);

  // Load plan details when activeSessionId changes (and it's a saved database ID)
  useEffect(() => {
    const loadSessionDetails = async () => {
      if (activeSessionId && !activeSessionId.startsWith("session-")) {
        // Read current messages length without creating a dependency on conversations state
        let currentMessagesLength = 0;
        setConversations((prev) => {
          currentMessagesLength = prev[activeSessionId]?.messages?.length || 0;
          return prev;
        });

        if (currentMessagesLength === 0) {
          try {
            setGenerating(true);
            const res = await api.get(`/ai/plans/${activeSessionId}`);
            const { plan, tasks } = res.data;

            const breakdownTasks = tasks.map((task) => ({
              name: `Day ${task.day_number || task.day}: ${task.title}`,
              desc: task.description,
              checked: plan.status === "Accepted",
              priority: task.priority,
              estimated_hours: task.estimated_hours,
            }));

            const flowBlocks = tasks.slice(0, 5).map((task) => ({
              time: `Day ${task.day_number || task.day}`,
              name: task.title,
              bg: "blue-bg",
            }));

            const userMessage = {
              sender: "user",
              text: plan.prompt || `Plan for: ${plan.goal}`,
            };

            const aiMessage = {
              sender: "ai",
              text: plan.summary || `Plan details for: ${plan.goal}`,
              hasAttachments: true,
              breakdownTitle: "TASK BREAKDOWN",
              breakdownTasks,
              flowTitle: "PLAN TIMELINE",
              flowBlocks,
              planId: plan.id,
              planGoal: plan.goal,
              durationDays: plan.duration_days,
              planDifficulty: plan.difficulty,
              estimatedHoursPerDay: plan.estimated_hours_per_day,
              status: plan.status,
              suggestions: plan.status === "Accepted" ? [] : ["Accept plan"],
            };

            setConversations((prev) => ({
              ...prev,
              [activeSessionId]: {
                ...prev[activeSessionId],
                messages: [userMessage, aiMessage],
              },
            }));
          } catch (err) {
            console.error("Error fetching single plan details:", err);
          } finally {
            setGenerating(false);
          }
        }
      }
    };

    loadSessionDetails();
  }, [activeSessionId]);

  // Filter history lists
  const filteredSessions = Object.values(conversations).filter((s) =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const activeSession = conversations[activeSessionId];

  // Reset chat / New Chat
  const handleNewChat = () => {
    const newSessionId = `session-${Date.now()}`;
    const newSession = {
      id: newSessionId,
      title: "New Planning Session",
      time: "Just now",
      status: "Pending",
      messages: [],
    };
    setConversations((prev) => ({
      [newSessionId]: newSession,
      ...prev,
    }));
    setActiveSessionId(newSessionId);
  };

  // Trigger submission
  const handleGenerate = async (promptText) => {
    const text = promptText || inputVal;
    if (!text.trim()) return;

    setInputVal("");
    setGenerating(true);

    // Append user message
    setConversations((prev) => {
      const active = prev[activeSessionId] || {
        id: activeSessionId,
        title: "New Planning Session",
        time: "Just now",
        status: "Pending",
        messages: [],
      };
      const updatedMessages = [...active.messages, { sender: "user", text }];
      const updatedSession = {
        ...active,
        messages: updatedMessages,
        title: active.title === "New Planning Session" ? text.substring(0, 24) : active.title,
      };
      return {
        ...prev,
        [activeSessionId]: updatedSession,
      };
    });

    try {
      const response = await api.post(
        "/ai/generate-plan",
        { prompt: text }
      );
      const data = response.data;

      if (!data.success) {
        throw new Error(data.message || "AI plan generation failed.");
      }
      const plan = data.plan;
      const planId = data.planId;
      
      const breakdownTasks = plan.tasks?.map((task) => ({
        name: `Day ${task.day || task.day_number}: ${task.title}`,
        desc: task.description,
        checked: false,
        priority: task.priority,
        estimated_hours: task.estimated_hours,
      })) || [];

      const flowBlocks = plan.tasks?.slice(0, 5).map((task) => ({
        time: `Day ${task.day || task.day_number}`,
        name: task.title,
        bg: "blue-bg",
      })) || [];

      setConversations((prev) => {
        const active = prev[activeSessionId];
        const updatedMessages = [
          ...active.messages,
          {
            sender: 'ai',
            text: plan.summary || `Generated plan for: ${plan.goal}`,
            hasAttachments: true,
            breakdownTitle: "TASK BREAKDOWN",
            breakdownTasks,
            flowTitle: "PLAN TIMELINE",
            flowBlocks,
            planId,
            planGoal: plan.goal,
            durationDays: plan.duration_days,
            planDifficulty: plan.difficulty,
            estimatedHoursPerDay: plan.estimated_hours_per_day,
            status: "Pending",
            
          },
        ];

        // Replace temporary session ID with plan ID in state keys
        const updatedSession = {
          ...active,
          id: planId.toString(),
          title: plan.goal || text.substring(0, 24),
          messages: updatedMessages,
          status: "Pending",
        };

        const nextConversations = { ...prev };
        delete nextConversations[activeSessionId];
        nextConversations[planId.toString()] = updatedSession;
        return nextConversations;
      });

      // Update active ID
      setActiveSessionId(planId.toString());

    } catch (err) {
      console.error("AI generation error:", err);
      setConversations((prev) => {
        const active = prev[activeSessionId];
        if (!active) return prev;
        const updatedMessages = [
          ...active.messages,
          {
            sender: 'ai',
            text: `Unable to generate plan: ${err.response?.data?.error || err.message}`,
            hasAttachments: false,
            suggestions: [],
          },
        ];

        return {
          ...prev,
          [activeSessionId]: {
            ...active,
            messages: updatedMessages,
          },
        };
      });
    } finally {
      setGenerating(false);
    }
  };

  // Open Accept Plan Modal
  const handleAcceptPrompt = (planId) => {
    setAcceptPlanId(planId);
    setAcceptStartDate(new Date().toISOString().split("T")[0]);
    setAcceptScheduleMode("daily");
    setAcceptScheduleDays("");
    setAcceptError("");
    setAcceptSuccess(false);
    setIsAcceptModalOpen(true);
  };

  // Submit Accept Plan
  const handleSubmitAccept = async () => {
    if (!acceptStartDate) {
      setAcceptError("Start Date is required.");
      return;
    }
    setAcceptLoading(true);
    setAcceptError("");
    setAcceptSuccess(false);

    try {
      const res = await api.post(
        `/ai/plans/${acceptPlanId}/accept`,
        {
          start_date: acceptStartDate,
          schedule_mode: acceptScheduleMode,
          schedule_days: acceptScheduleMode === "custom" ? acceptScheduleDays : null,
        }
      );

      if (!res.data.success) {
        throw new Error(res.data.message || "Failed to accept the plan.");
      }

      setAcceptSuccess(true);

      // Update the active session status in local state
      setConversations((prev) => {
        const nextConversations = { ...prev };
        const active = nextConversations[acceptPlanId.toString()];
        if (active) {
          active.status = "Accepted";
          active.messages = active.messages.map((msg) => {
            if (msg.sender === "ai" && msg.planId === acceptPlanId) {
              return {
                ...msg,
                status: "Accepted",
                suggestions: [],
                breakdownTasks: msg.breakdownTasks.map((t) => ({ ...t, checked: true })),
              };
            }
            return msg;
          });
        }
        return nextConversations;
      });

      // Redirect after showing success indicator
      setTimeout(() => {
        setIsAcceptModalOpen(false);
        navigate("/tasks");
      }, 1500);

    } catch (err) {
      console.error("Accept plan error:", err);
      setAcceptError(err.response?.data?.message || err.message || "An error occurred.");
    } finally {
      setAcceptLoading(false);
    }
  };

  const username = user?.username || user?.email?.split("@")[0] || "Alex Rivers";
  const avatarImage = "";

  return (
    <div className="pl-root">
      {/* ══ SIDEBAR + HISTORY ══ */}
      <Sidebar
        NAV_ITEMS={NAV_ITEMS}
        avatarImage={avatarImage}
        user={user}
      >
        <History
          handleNewChat={handleNewChat}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          filteredSessions={filteredSessions}
          activeSessionId={activeSessionId}
          setActiveSessionId={setActiveSessionId}
          setGenerating={setGenerating}
        />
      </Sidebar>

      {/* ══ CHAT INTERFACE ══ */}
      <ChatWindow
        activeSession={activeSession}
        handleAcceptPrompt={handleAcceptPrompt}
        generating={generating}
        handleGenerate={handleGenerate}
        messagesEndRef={messagesEndRef}
        inputVal={inputVal}
        setInputVal={setInputVal}
      />

      {/* ══ ACCEPT PLAN MODAL ══ */}
      {isAcceptModalOpen && (
        <div className="tk-modal-overlay" onClick={() => setIsAcceptModalOpen(false)}>
          <div className="tk-modal" onClick={(e) => e.stopPropagation()}>
            <div className="tk-modal-header">
              <h3>Accept Generated Plan</h3>
              <button className="tk-modal-close" onClick={() => setIsAcceptModalOpen(false)}>
                close
              </button>
            </div>

            {acceptError && (
              <div style={{ color: "var(--tp-error)", marginBottom: "12px", fontSize: "13px", fontWeight: "600" }}>
                {acceptError}
              </div>
            )}

            {acceptSuccess && (
              <div style={{ color: "var(--tp-success)", marginBottom: "12px", fontSize: "13px", fontWeight: "600" }}>
                Plan accepted successfully! Redirecting...
              </div>
            )}

            <div className="tk-modal-field">
              <label>Start Date</label>
              <input
                type="date"
                value={acceptStartDate}
                onChange={(e) => setAcceptStartDate(e.target.value)}
                disabled={acceptLoading || acceptSuccess}
              />
            </div>

            <div className="tk-modal-field">
              <label>Schedule Mode</label>
              <select
                value={acceptScheduleMode}
                onChange={(e) => setAcceptScheduleMode(e.target.value)}
                disabled={acceptLoading || acceptSuccess}
              >
                <option value="daily">Daily</option>
                <option value="weekdays">Weekdays</option>
                <option value="weekends">Weekends</option>
                <option value="custom">Custom</option>
              </select>
            </div>

            {acceptScheduleMode === "custom" && (
              <div className="tk-modal-field">
                <label>Selected Days (1=Mon, 7=Sun)</label>
                <input
                  type="text"
                  placeholder="e.g. 1,2,3,4,5"
                  value={acceptScheduleDays}
                  onChange={(e) => setAcceptScheduleDays(e.target.value)}
                  disabled={acceptLoading || acceptSuccess}
                />
              </div>
            )}

            <div className="tk-modal-footer">
              <button
                className="tk-modal-cancel"
                onClick={() => setIsAcceptModalOpen(false)}
                disabled={acceptLoading || acceptSuccess}
              >
                Cancel
              </button>
              <button
                className="tk-modal-submit"
                onClick={handleSubmitAccept}
                disabled={acceptLoading || acceptSuccess}
              >
                {acceptLoading ? "Accepting..." : "Accept Plan"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
