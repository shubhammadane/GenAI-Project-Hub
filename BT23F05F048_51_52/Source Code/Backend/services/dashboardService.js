const db=require("../config/db")

exports.getDashboardData=(userId)=>{
    return new Promise((resolve,reject)=>{
        const taskQuery="SELECT COUNT(*) AS totalTask , SUM(completed=1) AS completedTasks ,SUM(completed=0) AS pendingTasks FROM tasks WHERE user_id=?";

    db.query(taskQuery,[userId] ,(err,taskResult)=>{
        if(err){
           return reject(err);
        }   
    
    const eventQuery=`SELECT title,event_date,priority,event_time ,location FROM events WHERE user_id=? AND event_date>=CURDATE() AND DATEDIFF(event_date,CURDATE())<=7`;

    db.query(eventQuery ,[userId],(err2,eventResult)=>{
        if(err2){
            console.error("failed to get Event Result",err2);
        } 
         const todayTaskQuery=`SELECT * FROM tasks WHERE user_id =? AND due_date=CURDATE()`;

        db.query(todayTaskQuery ,[userId] ,(err3,todaysTasks)=>{
            if(err3){
                console.error("failed to get todaysTask",err3);
            }
            
            const recentActivityQuery="SELECT id,event_type AS action ,created_at AS Time FROM app_events WHERE user_id=? ORDER BY created_at DESC LIMIT 5";
            db.query(recentActivityQuery,[userId],(recentActivityErr,recentActivityResult)=>{
                if(recentActivityErr){
                    console.error("failed to get recent activity",recentActivityErr);
                }

           resolve({
            totalTasks:taskResult[0].totalTask,
            completedTasks:taskResult[0].completedTasks || 0,
            pendingTasks:taskResult[0].pendingTasks || 0,
            totalEvents:eventResult.length  ,
            upcomingEvents:eventResult.length || 0,
            todaysEvents:eventResult || 0,
            todaysTasks :todaysTasks,
            recentActivity:recentActivityResult
            
        });
    });
    });

          });

         });
    })
}