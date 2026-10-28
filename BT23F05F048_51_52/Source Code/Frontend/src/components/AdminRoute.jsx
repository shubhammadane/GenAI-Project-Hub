import {Navigate} from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function AdminRoute({children}){
    const {isAuthenticated ,user} =useAuth();
    if(!isAuthenticated || user?.role !== "admin"){
        return <Navigate to="/dashboard" replace />
    }
    return children;
}