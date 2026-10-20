import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import "./Tasks.css";
import api from "../api/axios";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";
/* ── Material Symbol helper ── */
const Icon = ({ name, className = "" }) => (
  <span className={`ms material-symbols-outlined ${className}`}>{name}</span>
);

/* ── Navigation Items ── */
const NAV_ITEMS = [
  { icon: "dashboard", label: "Dashboard", path: "/dashboard" },
  { icon: "assignment", label: "Tasks", path: "/tasks" ,active: true},
  { icon: "event", label: "Events", path: "/events" },
  { icon: "monitoring", label: "Analytics", path: "/Analytics" },
  { icon: "psychology", label: "AI Planner", path: "/ai-planner" },
  { icon: "account_circle", label: "Profile", path: "/profile" },
]; 

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  // const [user,setUser]=useState();
  /* Form Fields */
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("Medium");
  const [category, setCategory] = useState("Work");
  const [due_date, setdue_date] = useState("");
  const [status, setStatus] = useState("Pending");

  const {user,token}=useAuth();
  // const authHeaders = {
  //   headers: {
  //     Authorization: `Bearer ${token}`,
  //   },
  // };

  // Fetch Tasks
  const fetchTasks = async () => {
    try {
      const result = await api.get("/tasks");
     
      setTasks(result.data);
    } catch (err) {
      console.error("Error fetching tasks:", err);
    }
  };


  useEffect(() => {
    fetchTasks();
  }, []);

  // Open modal for adding
  const handleOpenAdd = () => {
    setEditingTask(null);
    setTitle("");
    setDescription("");
    setPriority("Medium");
    setCategory("Work");
    setdue_date("");
    setStatus("Pending");
    setIsModalOpen(true);
  };

  // Open modal for editing
  const handleOpenEdit = (task) => {
    setEditingTask(task);
    setTitle(task.title || "");
    setDescription(task.description || "");
    setPriority(task.priority || "Medium");
    setCategory(task.category || "Work");
    setdue_date(task.due_date || "");
    setStatus(task.completed || task.status === "Review" || task.status === "Completed" ? "Completed" : "Pending");
    setIsModalOpen(true);
  };

  const mapStatusForApi = (statusValue) => (statusValue === "Completed" ? "Review" : "To Do");
  const normalizeDueDate = (value) => (value === undefined || value === null || value === "" ? null : value);

  // Add Task
  const handleAddTask = async () => {
    if (!title.trim()) return;
    try {
      await api.post(
        "/tasks",
        {
          title,
          description,
          priority,
          category,
          due_date: normalizeDueDate(due_date),
          status: mapStatusForApi(status),
          completed: status === "Completed",
        }
      );
      fetchTasks();
      setIsModalOpen(false);
    } catch (err) {
      console.error("Error adding task:", err);
    }
  };

  // Edit Task
  const handleEditTask = async () => {
    if (!editingTask || !title.trim()) return;
    try {
      await api.put(
        `/tasks/${editingTask.id}`,
        {
          title,
          description,
          priority,
          category,
          due_date: normalizeDueDate(due_date),
          status: mapStatusForApi(status),
          completed: status === "Completed",
        }
      );
      fetchTasks();
      setIsModalOpen(false);
    } catch (err) {
      console.error("Error editing task:", err);
    }
  };

  // Delete Task
  const handleDeleteTask = async (id) => {
    const confirmDelete = window.confirm("Delete this task?");
    if (!confirmDelete) return;
    try {
      await api.delete(`/tasks/${id}`);
      fetchTasks();
    } catch (err) {
      console.error("Error deleting task:", err);
    }
  };

  // Quick move status (e.g. dragging/clicking to shift column)
  const handleMoveStatus = async (task, newStatus) => {
    try {
      console.log(task);
      console.log(task.due_date);
      await api.put(
        `/tasks/${task.id}`,
        {
          title: task.title,
          description: task.description || "",
          priority: task.priority || "Medium",
          category: task.category || "Work",
          due_date: normalizeDueDate(task.due_date),
          status: mapStatusForApi(newStatus),
          completed: newStatus === "Completed",
        }
      );
      fetchTasks();
    } catch (err) {
      console.error("Error moving task:", err);
    }
  };

  // Filtering & task section matching
  const filteredTasks = tasks.filter((task) => {
    const term = search.toLowerCase();
    const matchesSearch =
      task.title?.toLowerCase().includes(term) ||
      task.description?.toLowerCase().includes(term) ||
      task.category?.toLowerCase().includes(term) ||
      task.priority?.toLowerCase().includes(term);
    return matchesSearch;
  });

  const isCompletedTask = (task) => task.completed || task.status === "Review" || task.status === "Completed";

  const pendingTasks = filteredTasks.filter((task) => !isCompletedTask(task));
  const completedTasks = filteredTasks.filter((task) => isCompletedTask(task));

  const renderTaskCard = (task, sectionId) => {
    const completed = isCompletedTask(task);

    return (
      <div
        key={task.id}
        className={`tk-card ${completed ? "done" : ""}`}
        onClick={() => handleOpenEdit(task)}
      >
        <span className={`tk-cat-tag cat-${(task.category || "work").toLowerCase()}`}>
          {task.category || "Work"}
        </span>

        <h4 className={`tk-card-title ${completed ? "done" : ""}`}>{task.title}</h4>

        {task.description && <p className="tk-card-desc">{task.description}</p>}

        <div className="tk-card-footer">
          <div
            className={`tk-priority ${
              task.priority === "High"
                ? "pri-high"
                : task.priority === "Low"
                ? "pri-low"
                : "pri-medium"
            }`}
          >
            <Icon
              name={
                task.priority === "High"
                  ? "error"
                  : task.priority === "Low"
                  ? "arrow_downward"
                  : "drag_handle"
              }
            />
            {task.priority || "Medium"}
          </div>

          {task.due_date && (
            <div className="tk-due-date">
              <Icon name="calendar_month" />
              {task.due_date}
            </div>
          )}

          <div className="tk-card-actions" onClick={(e) => e.stopPropagation()}>
            {sectionId !== "active" && (
              <button
                className="tk-card-btn"
                title="Move to Added Tasks"
                onClick={() => handleMoveStatus(task, "Pending")}
              >
                arrow_back
              </button>
            )}
            {sectionId !== "completed" && (
              <button
                className="tk-card-btn"
                title="Mark as Completed"
                onClick={() => handleMoveStatus(task, "Completed")}
              >
                check
              </button>
            )}
            <button
              className="tk-card-btn danger"
              title="Delete"
              onClick={() => handleDeleteTask(task.id)}
            >
              delete
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="tasks-root">
      <Sidebar
        NAV_ITEMS={NAV_ITEMS}
        user={user}
      />

      {/* ══ MAIN ══ */}
      <main className="tk-main">
        {/* Topbar */}
        <header className="tk-topbar">
          <h2>Tasks</h2>
          <div className="tk-search-wrap">
            <Icon name="search" />
            <input
              type="text"
              placeholder="Search tasks, priorities, or tags..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="tk-topbar-actions">
            <button className="tk-icon-btn">
              <Icon name="filter_list" />
            </button>
            <button className="tk-add-btn" onClick={handleOpenAdd}>
              <Icon name="add" />
              Add Task
            </button>
          </div>
        </header>

        {/* Board */}
        <div className="tk-board">
          <section className="tk-section">
            <div className="tk-section-header">
              <div className="tk-section-title">
                <div className="tk-section-indicator active" />
                <h3>Added Tasks</h3>
                <span className="tk-section-count">{pendingTasks.length}</span>
              </div>
            </div>

            <div className="tk-cards">
              {pendingTasks.map((task) => renderTaskCard(task, "active"))}

              <button
                className="tk-add-card-btn"
                onClick={() => {
                  handleOpenAdd();
                  setStatus("Pending");
                }}
              >
                <Icon name="add" />
                Add Task
              </button>
            </div>
          </section>

          <section className="tk-section">
            <div className="tk-section-header">
              <div className="tk-section-title">
                <div className="tk-section-indicator completed" />
                <h3>Completed Tasks</h3>
                <span className="tk-section-count completed">{completedTasks.length}</span>
              </div>
            </div>

            <div className="tk-cards">
              {completedTasks.map((task) => renderTaskCard(task, "completed"))}

              <button
                className="tk-add-card-btn"
                onClick={() => {
                  handleOpenAdd();
                  setStatus("Completed");
                }}
              >
                <Icon name="add" />
                Add Task
              </button>
            </div>
          </section>
        </div>
      </main>

      {/* ══ ADD/EDIT MODAL ══ */}
      {isModalOpen && (
        <div className="tk-modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="tk-modal" onClick={(e) => e.stopPropagation()}>
            <div className="tk-modal-header">
              <h3>{editingTask ? "Edit Task" : "Create New Task"}</h3>
              <button className="tk-modal-close" onClick={() => setIsModalOpen(false)}>
                close
              </button>
            </div>

            <div className="tk-modal-field">
              <label>Task Title</label>
              <input
                type="text"
                placeholder="e.g. Refactor Authentication Flow"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>

            <div className="tk-modal-field">
              <label>Description</label>
              <textarea
                placeholder="Describe this task..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div className="tk-modal-row">
              <div className="tk-modal-field">
                <label>Priority</label>
                <select value={priority} onChange={(e) => setPriority(e.target.value)}>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>

              <div className="tk-modal-field">
                <label>Category</label>
                <select value={category} onChange={(e) => setCategory(e.target.value)}>
                  <option value="Work">Work</option>
                  <option value="Personal">Personal</option>
                  <option value="Study">Study</option>
                  <option value="Health">Health</option>
                </select>
              </div>
            </div>

            <div className="tk-modal-row">
              <div className="tk-modal-field">
                <label>Due Date</label>
                <input
                  type="date"
                  value={due_date}
                  onChange={(e) => setdue_date(e.target.value)}
                />
              </div>

              <div className="tk-modal-field">
                <label>Task State</label>
                <select value={status} onChange={(e) => setStatus(e.target.value)}>
                  <option value="Pending">Pending</option>
                  <option value="Completed">Completed</option>
                </select>
              </div>
            </div>

            <div className="tk-modal-footer">
              <button className="tk-modal-cancel" onClick={() => setIsModalOpen(false)}>
                Cancel
              </button>
              <button
                className="tk-modal-submit"
                onClick={editingTask ? handleEditTask : handleAddTask}
              >
                {editingTask ? "Save Changes" : "Create Task"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}