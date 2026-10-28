import { Link } from "react-router-dom"
export default function Navbar(){
    return(
        <nav>
        
        <Link to='/'>
        Dashboard
        </Link>
        {"|"}

        <Link to="/events">
        Events
        </Link>
        {"|"}
        
        <Link to="/analytics">
        Analytics
        </Link>
        {"|"}
        <Link to="/login">login</Link>

        </nav>
    )
}