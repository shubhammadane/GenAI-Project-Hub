import './TaskCard.css'
import { useState } from 'react';
export default function TaskCard({task ,DeleteTask,Complete,setEditingTask}){
  

    let styles = task.completed
  ? {
      textDecoration:"line-through",
      color:"gray"
    }
  : {};

  let priorityStyle={}
  if(task.priority==="High"){
    priorityStyle={"color":"red"};
  }
  else if(task.priority === "Medium"){
    priorityStyle={"color":"orange"};
  }
  else{
    priorityStyle={"color":"green"}
  }

    return (
        <div className='taskCard'  >

          <h3 style={styles} className="task-title">{task.title}</h3>
          <p style={priorityStyle}>Priority :{task.priority}</p>
          <p>Category:{task.category}</p>
          <p>due:{task.due_date}</p>
          <button className="delBtn" onClick={()=>DeleteTask(task.id)}>Delete</button>
         
          <button className="markBtn" onClick={()=>Complete(task)}>{task.completed ? "Undo" : "Complete"}</button>
          
          <button onClick={()=>setEditingTask(task)}>Edit</button>

          </div>

    )
}