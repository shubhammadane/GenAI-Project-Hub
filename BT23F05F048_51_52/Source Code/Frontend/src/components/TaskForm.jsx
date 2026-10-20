import { useEffect } from 'react'
import './TaskForm.css'
export default function TaskForm({title,setTitle,AddTask,priority,setPriority,category ,setCategory ,due_date,setdue_date,editingTask,setEditingTask,EditTask}){
    
    useEffect(()=>{
        if(editingTask){
            setTitle(editingTask.title);
            setPriority(editingTask.priority);
            setCategory(editingTask.category);
            setdue_date(editingTask.due_date);
        }
    },[editingTask]);

    return (
        <div className="TaskForm">
            
        <input type="text" placeholder="Enter Task" onChange={(e)=>setTitle(e.target.value)} value={title}/>
        
       
        <p>set priority</p>
        <select value={priority} onChange={(e)=> setPriority(e.target.value)} required>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
        </select>
        
        <p>set task category</p>
        <select value={category} onChange={(e)=> setCategory(e.target.value)} required>
            <option value="Study">Study</option>     
            <option value="Work">Work</option>     
            <option value="Personal">Personal</option>     
            <option value="Health">Health</option>     
        </select>
        
        <input type="date" value={due_date} onChange={(e)=> setdue_date(e.target.value)} required/>
        <button onClick={()=> {
            if(editingTask){
                EditTask(editingTask);
            }else{
                AddTask();
            }
        }}>{ editingTask ? "Update Task" : "Add Task"}</button>

         </div>

    )
}