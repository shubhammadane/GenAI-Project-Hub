import TaskCard from "./TaskCard"
export default function TaskList({tasks,DeleteTask,Complete,setEditingTask}){
    return (
        <>
        {tasks.map((task)=> <TaskCard key={task.id} task={task} DeleteTask={DeleteTask} Complete={Complete} setEditingTask={setEditingTask}></TaskCard>)}
        </>
    )
}