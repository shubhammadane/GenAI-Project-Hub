import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
// import './App.css'
import Navbar from './components/Navbar'
import Tasks from './pages/Tasks'
import Analytics from './pages/Analytics'
import Events from './pages/Events'
import Login from './pages/Login'
import Home from './pages/Home'
import Register from './pages/Register'
import Profile from './pages/Profile'
import AIPlanner from './pages/AIPlanner'
import AdminDashboard from './pages/AdminDashboard'
import Dashboard from './pages/Dashboard'
import { BrowserRouter ,Routes,Route} from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import AdminRoute from './components/AdminRoute'

function App() {
  
    const [tasks ,setTasks]=useState([]);

  return (
    
    <AuthProvider>
    <BrowserRouter>
    <Routes>
      <Route 
      path="/"
      element={<Home/>}/>

      <Route
      path="/tasks"
      element={<ProtectedRoute><Tasks tasks={tasks} setTasks={setTasks}/></ProtectedRoute>}
      />

      <Route 
      path="/events"
      element={<Events/>}
      />
      <Route 
      path="/Analytics"
      element={<ProtectedRoute><Analytics  tasks={tasks} setTasks={setTasks}/></ProtectedRoute>}
      />

      <Route
      path="/dashboard"
      element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />

      <Route
      path="/login"
      element={<Login></Login>} />

      <Route
      path="/register"
      element={<Register></Register>} />

      <Route
      path="/profile"
      element={<Profile />} />

      <Route
      path="/ai-planner"
      element={<ProtectedRoute><AIPlanner /></ProtectedRoute>} />

      <Route
      path="/admin"
      element={<AdminRoute><AdminDashboard /></AdminRoute>} />
      
    </Routes>
    </BrowserRouter>
    </AuthProvider>
  )
}

export default App
