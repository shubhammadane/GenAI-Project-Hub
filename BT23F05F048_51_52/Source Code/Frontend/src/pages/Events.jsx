import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import "./Event.css";
import api from "../api/axios";
import Sidebar from "../components/Sidebar";
import {useAuth} from "../context/AuthContext"
/* ── Material Symbol helper ── */
const Icon = ({ name, className = "" }) => (
  <span className={`ms-icon material-symbols-outlined ${className}`}>{name}</span>
);

/* ── Navigation Items ── */
const NAV_ITEMS = [
  { icon: "dashboard", label: "Dashboard", path: "/dashboard" },
  { icon: "assignment", label: "Tasks", path: "/tasks" },
  { icon: "event", label: "Events", path: "/events", active: true },
  { icon: "monitoring", label: "Analytics", path: "/Analytics" },
  { icon: "psychology", label: "AI Planner", path: "/ai-planner" },
  { icon: "account_circle", label: "Profile", path: "/profile" },
];

const CloseIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="modal-close-icon" viewBox="0 0 24 24">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
)

const FloatingBrainIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="ai-floating-icon" viewBox="0 0 24 24">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1 0-3.12 3.02 3.02 0 0 1 0-3.88 2.5 2.5 0 0 1 0-3.12A2.5 2.5 0 0 1 9.5 2Z" fill="currentColor" opacity="0.15"></path>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 0-3.12 3.02 3.02 0 0 0 0-3.88 2.5 2.5 0 0 0 0-3.12A2.5 2.5 0 0 0 14.5 2Z" fill="currentColor" opacity="0.15"></path>
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1 0-3.12 3.02 3.02 0 0 1 0-3.88 2.5 2.5 0 0 1 0-3.12A2.5 2.5 0 0 1 9.5 2Z"></path>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 0-3.12 3.02 3.02 0 0 0 0-3.88 2.5 2.5 0 0 0 0-3.12A2.5 2.5 0 0 0 14.5 2Z"></path>
  </svg>
)


export default function Events() {
  const [events, setEvents] = useState([])


  const todayObj = new Date()
  const [currentMonth, setCurrentMonth] = useState(todayObj.getMonth())
  const [currentYear, setCurrentYear] = useState(todayObj.getFullYear())
  const [selectedDay, setSelectedDay] = useState(todayObj.getDate())
  const [showModal, setShowModal] = useState(false)
  const [viewMode, setViewMode] = useState("Month")
  const [editingEvent,setEditingEvent]=useState(false);
  const [editingId,setEditingId]=useState(null);
  // Form states
  const [title, setTitle] = useState("");

  const formatYYYYMMDD = (d) => {
    const y = d.getFullYear()
    const m = (d.getMonth() + 1) < 10 ? `0${d.getMonth() + 1}` : d.getMonth() + 1
    const day = d.getDate() < 10 ? `0${d.getDate()}` : d.getDate()
    return `${y}-${m}-${day}`
  }

  const [eventDate, setEventDate] = useState(formatYYYYMMDD(todayObj))
  const [eventTime, setEventTime] = useState("")
  const [description, setDescription] = useState("")
  const [location, setLocation] = useState("")
  const [category, setCategory] = useState("Personal")
  const [priority, setPriority] = useState("High")
  const [reminder, setReminder] = useState(false)
  const [completed, setCompleted] = useState(false)
 
  const resetForm = () => {
    setTitle("")
    setDescription("")
    setEventTime("")
    setLocation("")
    setCategory("Personal")
    setPriority("High")
    setReminder(false)
    setCompleted(false)
    setEventDate(formatYYYYMMDD(todayObj))
  }

  const openNewEventModal = () => {
    setEditingEvent(false)
    setEditingId(null)
    resetForm()
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingEvent(false)
    setEditingId(null)
    resetForm()
  }

 const {user,token,logout} =useAuth();
  const authHeaders = {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }

  const todayYear = todayObj.getFullYear()
  const todayMonth = (todayObj.getMonth() + 1) < 10 ? `0${todayObj.getMonth() + 1}` : todayObj.getMonth() + 1
  const yearMonthPrefix = `${todayYear}-${todayMonth}`

  

  const fetchEvents = async () => {
    try {
      const res = await api.get("/events", authHeaders)
      if (res.data && res.data.length > 0) {
        setEvents(res.data)
      } else {
        setEvents([])
      }
    } catch (err) {
      console.log("Could not load from API, falling back to default events", err)
      setEvents([])
    }
  }

  useEffect(() => {
    fetchEvents()
  }, [])

  const addEvent = async (e) => {
    e.preventDefault()
    console.log("add is clicked")
    if (!title.trim()) return

    const newEvent = {
      title,
      description,
      event_date: eventDate,
      event_time: eventTime || "12:00 PM",
      location: location || "N/A",
      category,
      priority,
      reminder,
      completed,
    }

    try {
      await api.post("/events", newEvent, authHeaders)
      await fetchEvents()
    } catch (err) {
      console.log("Axios error, saving locally", err)
      // fallback local save
      setEvents(prev => [...prev, { id: "local-" + Date.now(), ...newEvent }])
    }

    // Reset Form & Close Modal
    setTitle("")
    setDescription("")
    setEventTime("")
    setLocation("")
    setCategory("Personal")
    setPriority("High")
    setReminder(false)
    setCompleted(false)
    setShowModal(false)
  }

  const deleteEvent = async (id) => {
    try {
      await api.delete(`/events/${id}`, authHeaders)
      await fetchEvents()
    } catch (err) {
      console.log("Delete API error, deleting locally", err)
      setEvents(prev => prev.filter(e => e.id !== id))
    }
  }

  // edit event
  const handleOpenEdit =(event)=>{
    setEditingEvent(true)
    setEditingId(event.id)
    setTitle(event.title || "")
    setDescription(event.description || "")
    setEventDate(event.event_date?.split("T")[0] || formatYYYYMMDD(todayObj))
    setEventTime(event.event_time || "")
    setLocation(event.location || "")
    setCategory(event.category || "Personal")
    setPriority(event.priority || "High")
    setReminder(event.reminder)
    setCompleted(event.completed)
    setShowModal(true)
  };

  const handleEditEvent=async (e)=>{
  e.preventDefault();
    console.log("edit button clicked");
    console.log(editingId)
   if(!title || !title.trim()) return;
   try{
    await api.put(
      `/events/${editingId}`,
      {
        title,
        description,
        event_date:eventDate,
        event_time:eventTime,
        location,
        category,        
        priority,
        reminder,
        completed
      },
      authHeaders
    );
    await fetchEvents();
    setEditingEvent(false)
    setEditingId(null)
    resetForm()
    setShowModal(false)

   }catch(err){
    console.error("Error updating Event:",err);
   }
  }

  // Get active day date string (e.g. 2026-07-04)
  const getSelectedDateString = () => {
    const monthStr = (currentMonth + 1) < 10 ? `0${currentMonth + 1}` : `${currentMonth + 1}`
    const dayStr = selectedDay < 10 ? `0${selectedDay}` : selectedDay
    return `${currentYear}-${monthStr}-${dayStr}`
  }

  // Events belonging to the currently selected day
  const activeTimelineEvents = events.filter(
    (event) => event.event_date?.split("T")[0] === getSelectedDateString()
  )

  // Sorted upcoming events (future dates in the calendar, starting from today)
  const sortedUpcomingEvents = [...events]
    .filter(event => {
      const dateStr = event.event_date?.split("T")[0]
      if (!dateStr) return false
      const eventDateObj = new Date(dateStr)
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      return eventDateObj >= today
    })
    .sort((a, b) => new Date(a.event_date) - new Date(b.event_date))

  const getMonthName = (monthIndex) => {
    const monthNames = [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"
    ]
    return monthNames[monthIndex]
  }

  const handlePrevMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11)
      setCurrentYear(prev => prev - 1)
    } else {
      setCurrentMonth(prev => prev - 1)
    }
  }

  const handleNextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0)
      setCurrentYear(prev => prev + 1)
    } else {
      setCurrentMonth(prev => prev + 1)
    }
  }

  // Render calendar cells dynamically with prefix and suffix empty days
  const renderCalendarCells = () => {
    const cells = []
    
    // First day of the month
    const firstDayIndex = new Date(currentYear, currentMonth, 1).getDay()
    
    // Number of days in the current month
    const totalDays = new Date(currentYear, currentMonth + 1, 0).getDate()
    
    // Number of days in the previous month (to show dates for empty cells at the start)
    const prevTotalDays = new Date(currentYear, currentMonth, 0).getDate()
    
    // Render padding cells from the previous month
    for (let i = firstDayIndex - 1; i >= 0; i--) {
      const prevDay = prevTotalDays - i
      cells.push(
        <div key={`prev-${prevDay}`} className="grid-day-cell empty-day-cell">
          <span className="day-number" style={{ opacity: 0.3 }}>{prevDay}</span>
        </div>
      )
    }
    
    // Today's date info to highlight current day
    const today = new Date()
    const isCurrentMonthYear = today.getFullYear() === currentYear && today.getMonth() === currentMonth
    
    // Render current month's cells
    for (let day = 1; day <= totalDays; day++) {
      const isToday = isCurrentMonthYear && day === today.getDate()
      const isSelected = day === selectedDay
      
      const monthStr = (currentMonth + 1) < 10 ? `0${currentMonth + 1}` : `${currentMonth + 1}`
      const dayStr = day < 10 ? `0${day}` : `${day}`
      const dateStr = `${currentYear}-${monthStr}-${dayStr}`
      
      const dayEvents = events.filter((e) => e.event_date?.split("T")[0] === dateStr)
      
      cells.push(
        <div
          key={`current-${day}`}
          className={`grid-day-cell ${isToday ? "today" : ""} ${isSelected ? "selected" : ""}`}
          onClick={() => {
            setSelectedDay(day)
            setEventDate(dateStr)
          }}
        >
          <span className="day-number">{day}</span>
          <div className="grid-day-events">
            {dayEvents.map((event) => (
              <div
                key={event.id}
                className={`calendar-event-badge event-${event.category || "Personal"}`}
                title={event.title}
              >
                {event.title}
              </div>
            ))}
          </div>
        </div>
      )
    }
    
    // Render padding cells for the next month to make the grid complete (multiple of 7)
    const totalRendered = cells.length
    const remainingCells = (7 - (totalRendered % 7)) % 7
    for (let day = 1; day <= remainingCells; day++) {
      cells.push(
        <div key={`next-${day}`} className="grid-day-cell empty-day-cell">
          <span className="day-number" style={{ opacity: 0.3 }}>{day}</span>
        </div>
      )
    }
    
    return cells
  }

  const handleAISynthesis = () => {
    alert("AI Planner: Generating optimized schedule based on your energy levels and task priorities...")
  }

  return (
    <div className="events-page-wrapper">
      <Sidebar
        NAV_ITEMS={NAV_ITEMS}
        // avatarImage={avatarImage}
        user={user}
      />

      {/* Main Content */}
      <main className="main-events-content">
        {/* Calendar Grid Section */}
        <section className="calendar-section">
          {/* Calendar Header */}
          <header className="calendar-header">
            <div className="calendar-title-group">
              <h2>{getMonthName(currentMonth)} {currentYear}</h2>
              <p>Manage your high-velocity schedule.</p>
            </div>
            <div className="calendar-controls">
              <div className="view-selector">
                <button className={`view-btn ${viewMode === "Month" ? "active" : ""}`} onClick={() => setViewMode("Month")}>Month</button>
                <button className={`view-btn ${viewMode === "Week" ? "active" : ""}`} onClick={() => setViewMode("Week")}>Week</button>
                <button className={`view-btn ${viewMode === "Day" ? "active" : ""}`} onClick={() => setViewMode("Day")}>Day</button>
              </div>
              <button className="nav-arrow-btn" onClick={handlePrevMonth}>
                <Icon name="chevron_left" className="arrow-icon" />
              </button>
              <button className="nav-arrow-btn" onClick={handleNextMonth}>
                <Icon name="chevron_right" className="arrow-icon" />
              </button>
            </div>
          </header>

          {/* Grid Layout wrapper */}
          <div className="calendar-grid-wrapper">
            <div className="grid-day-labels">
              <div>SUN</div>
              <div>MON</div>
              <div>TUE</div>
              <div>WED</div>
              <div>THU</div>
              <div>FRI</div>
              <div>SAT</div>
            </div>
            <div className="grid-days">
              {renderCalendarCells()}
            </div>
          </div>
        </section>

        {/* Right Sidebar: Event Focus */}
        <aside className="events-sidebar">
          <div className="sidebar-focus-header">
            <h3>Events Focus</h3>
            <button className="btn-add-event" type="button" onClick={openNewEventModal}>
              <Icon name="add" className="add-icon" />
            </button>
          </div>

          {/* Selected Day Timeline */}
          <div className="timeline-section-title">
            <Icon name="calendar_today" className="timeline-icon" />
            <span>Today's Timeline</span>
          </div>

          <div className="timeline-events-list">
            {activeTimelineEvents.length > 0 ? (
              activeTimelineEvents.map((event) => (
                <div key={event.id} className={`focus-event-card focus-card-${event.category || "Personal"}`} onClick={()=>handleOpenEdit(event)}>
                  <div className="focus-card-header">
                    <span className={`focus-card-category category-${event.category || "Personal"}`}>
                      {event.category}
                    </span>
                    <div className="focus-card-actions">
                      <button type="button" className="focus-action-btn delete" onClick={(e) => { e.stopPropagation(); deleteEvent(event.id); }}>
                        <Icon name="delete" className="focus-action-icon" />
                      </button>
                    </div>
                  </div>
                  <h4 className="focus-card-title">{event.title}</h4>
                  <div className="focus-card-meta">
                    <div className="meta-row">
                      <Icon name="schedule" className="meta-icon" />
                      <span>{event.event_time}</span>
                    </div>
                    {event.location && event.location !== "N/A" && (
                      <div className="meta-row">
                        {event.location.includes("Zoom") || event.location.includes("Google") ? (
                          <Icon name="videocam" className="meta-icon" />
                        ) : (
                          <Icon name="place" className="meta-icon" />
                        )}
                        <span>{event.location}</span>
                      </div>
                    )}
                  </div>
                  {event.priority && (
                    <span className={`focus-card-priority-badge priority-${event.priority}`}>
                      {event.priority} Priority
                    </span>
                  )}
                </div>
              ))
            ) : (
              <p style={{ padding: "0 8px", fontSize: "14px", color: "var(--outline)", textAlign: "center" }}>
                No events scheduled for this day. Click "+" to schedule.
              </p>
            )}
          </div>

          {/* Upcoming Section */}
          <div className="upcoming-section-title">
            <Icon name="event_upcoming" className="timeline-icon" />
            <span>Upcoming Events</span>
          </div>

          <div className="upcoming-events-list">
            {sortedUpcomingEvents.slice(0, 3).map((event) => {
              const dateParts = event.event_date.split("T")[0].split("-");
              const monthIndex = parseInt(dateParts[1], 10) - 1;
              const dayNum = parseInt(dateParts[2], 10);
              const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
              const monthStr = monthNames[monthIndex] || "Sep";
              const displayDay = isNaN(dayNum) ? "14" : dayNum;
              return (
                <div
                  key={event.id}
                  className="upcoming-event-item"
                  onClick={() => {
                    const eventYear = parseInt(dateParts[0], 10);
                    const eventMonth = parseInt(dateParts[1], 10) - 1;
                    if (!isNaN(eventYear)) setCurrentYear(eventYear);
                    if (!isNaN(eventMonth)) setCurrentMonth(eventMonth);
                    setSelectedDay(isNaN(displayDay) ? todayObj.getDate() : displayDay);
                  }}
                >
                  <div className="date-badge">
                    <span className="date-month">{monthStr}</span>
                    <span className="date-day">{displayDay}</span>
                  </div>
                  <div className="upcoming-info">
                    <h5>{event.title}</h5>
                    <p className="upcoming-meta">
                      {event.event_time} • {event.location || "Remote"}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Tip of the Week Card */}
          <div className="tip-container">
            <div className="tip-card">
              <div className="tip-overlay"></div>
              <img
                className="tip-bg-img"
                alt="Workspace desk at dusk"
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuAJvngPAMdC5GSlmE9q6POrdpzIk3n32FLEbXpPx8naXFzu_vq5TLWxpV6wnRIU2Bs3kq33rup0lsQMhe8hxFvZbx4Vrhocw9Ok4Nxw-QCKSSzLRyVc4Z_QUHHtJRP8zw1BymHqVrZQhgSnCmRvgujmGqmwEfD1bVK_w2np3Fhk3srhoSthRGxnUdX9Lm6vBoqf6VUdc558xlKgStamuDxHqMaMNHRplM3Q1P8dr8TBLCNwmcHjJcHly95977ClIT5-juiFoe6CVcFu"
              />
              <div className="tip-content">
                <p className="tip-tag">Tip of the week</p>
                <p className="tip-text">Batch your meetings in the morning to preserve deep-work focus in the afternoons.</p>
              </div>
            </div>
          </div>
        </aside>
      </main>

      {/* Floating AI Assistant Trigger */}
      {/* <button className="ai-planner-floating-btn" onClick={handleAISynthesis}>
        <FloatingBrainIcon />
        <div className="ai-tooltip">Plan with AI</div>
      </button> */}

      {/* Glassmorphic Event Insert Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>{editingEvent ?"Edit Event":"Schedule New Event"}</h3>
              <button type="button" className="modal-close-btn" onClick={closeModal}>
                <CloseIcon />
              </button>
            </div>
            <form className="modal-form" onSubmit={editingEvent? handleEditEvent:addEvent}>
              <div className="input-group">
                <label className="input-label" htmlFor="event-title">Event Title</label>
                <input
                  id="event-title"
                  type="text"
                  className="modal-input"
                  placeholder="e.g. Client Sync, Gym"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
              </div>

              <div className="form-row">
                <div className="input-group">
                  <label className="input-label" htmlFor="event-date">Date</label>
                  <input
                    id="event-date"
                    type="date"
                    className="modal-input"
                    value={eventDate}
                    onChange={(e) => setEventDate(e.target.value)}
                    required
                  />
                </div>
                <div className="input-group">
                  <label className="input-label" htmlFor="event-time">Time</label>
                  <input
                    id="event-time"
                    type="time"
                    className="modal-input"
                    placeholder="e.g. 10:00 AM - 11:30 AM"
                    value={eventTime}
                    onChange={(e) => setEventTime(e.target.value)}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="input-group">
                  <label className="input-label" htmlFor="event-category">Category</label>
                  <select
                    id="event-category"
                    className="modal-select"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                  >
                    <option value="Meeting">Meeting</option>
                    <option value="Personal">Personal</option>
                    <option value="Interview">Interview</option>
                    <option value="Exam">Exam</option>
                    <option value="Birthday">Birthday</option>
                  </select>
                </div>
                <div className="input-group">
                  <label className="input-label" htmlFor="event-priority">Priority</label>
                  <select
                    id="event-priority"
                    className="modal-select"
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                  >
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>
              </div>

              <div className="input-group">
                <label className="input-label" htmlFor="event-location">Location</label>
                <input
                  id="event-location"
                  type="text"
                  className="modal-input"
                  placeholder="e.g. Conference Room B, Zoom Link"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                />
              </div>

              <div className="input-group">
                <label className="input-label" htmlFor="event-desc">Description</label>
                <textarea
                  id="event-desc"
                  className="modal-textarea"
                  placeholder="Event details..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>

              <div className="modal-checkbox-row">
                <input
                  id="event-reminder"
                  type="checkbox"
                  className="modal-checkbox"
                  checked={reminder}
                  onChange={(e) => setReminder(e.target.checked)}
                />
                <label htmlFor="event-reminder" className="modal-checkbox-label">Set Email Reminder</label>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-secondary btn-sm" onClick={closeModal} style={{ borderRadius: '6px' }}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary btn-sm" style={{ borderRadius: '6px' }}>
                  {editingEvent ?"Save changes":"Schedule Event"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}