const db=require("../config/db")

exports.analytics=(req)=>{
    return new Promise((resolve,reject)=>{
        const query1="SELECT COUNT(*) AS totalTasks ,SUM(completed=1) AS completedTasks ,SUM(completed=0) AS pendingTasks ,ROUND(SUM(completed=1)*100/COUNT(*),2) AS completionRate FROM tasks WHERE user_id=?";
    db.query(query1,[req.user.id],(err,taskResult)=>{
        if(err){
            return reject(err);
        }
        

        const query2="SELECT COUNT(*) AS upcomingEvents FROM events WHERE user_id=? AND event_date>=CURDATE()";

        db.query(query2,[req.user.id],(err2,eventResult)=>{
            if(err2){
                console.error("failed to fetch events",err2);
            }

            const query3="SELECT category,COUNT(*) AS count FROM tasks WHERE user_id=? GROUP BY category";

            db.query(query3 ,[req.user.id],(err3,categoryResult)=>{
                if(err3){
                    console.error("failed to fetch categoryResult ",err3);
                
                }

                const query4="SELECT priority,COUNT(*) AS count FROM tasks WHERE user_id=? GROUP BY priority";

                db.query(query4 ,[req.user.id],(err4,priorityResult)=>{
                    if(err4){
                        console.error("failed to fetch priority result",err4);
                    }

                    const query5="SELECT MONTH(due_date) AS monthNumber, MONTHNAME(due_date) AS month, COUNT(*) AS count FROM tasks WHERE user_id=? GROUP BY MONTH(due_date), MONTHNAME(due_date) ORDER BY MONTH(due_date)";

                    db.query(query5,[req.user.id],(err5,monthResult)=>{
                        if(err5){
                            console.error("failed to fetch monthResult",err5);
                        }

                        const query6=`SELECT 
                        DAYNAME(due_date) AS day,
                        DAYOFWEEK(due_date) AS dayOrder,
                        SUM(completed=1) AS completed,
                        SUM(completed=0) AS remaining
                        FROM tasks
                        WHERE user_id=?
                        AND YEARWEEK(due_date, 1)=YEARWEEK(CURDATE(), 1)
                        GROUP BY DAYNAME(due_date), DAYOFWEEK(due_date)
                        ORDER BY dayOrder`;
                        
                        db.query(query6,[req.user.id],(err6,weekResult)=>{
                            if(err6){
                                console.error("failed to fetch weekResult",err6);
                            }

                            resolve({
                                overview:{
                                    totalTasks:taskResult[0].totalTasks ||0,
                                    completedTasks:taskResult[0].completedTasks||0,
                                    pendingTasks:taskResult[0].pendingTasks ||0,
                                    completionRate:taskResult[0].completionRate ||0,
                                    upcomingEvents:eventResult[0].upcomingEvents ||0
                                },
                                 weeklyProductivity: weekResult,
                                    categories:categoryResult,
                                    priority:priorityResult,
                                    monthResult:monthResult
                            });
                        })
                    })
                })
            })
        })

    })
    })
}