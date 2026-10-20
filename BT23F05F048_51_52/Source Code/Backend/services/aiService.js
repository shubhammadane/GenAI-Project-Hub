const db=require("../config/db");

exports.generatePlan =(user_id,prompt,plan)=>{
    // return api.post("/ai/generate-plan",{prompt},authHeaders);
     return new Promise((resolve,reject)=>{

                // store the plan 
        const q =`INSERT INTO plans ( 
        user_id,
        prompt ,
        goal,
        summary,
        duration_days,
        estimated_hours_per_day,
        difficulty
        ) VALUES (?,?,?,?,?,?,?)`;

        db.query(q,[user_id ,
            prompt ,
            plan.goal ,
            plan.summary,
            plan.duration_days ,
            plan.estimated_hours_per_day ,
            plan.difficulty] ,
            (err,result)=>{
               
                if(err){
                    return reject(err);
                }

                const q2=`INSERT INTO plan_tasks (plan_id,day_number,title,description,priority,estimated_hours) VALUES(?,?,?,?,?,?)`;
                const plan_id=result.insertId;
                


                // if no tasks generated
                if(!plan.tasks || plan.tasks.length ===0){
                    return res.status(400).json({
                        success:false,
                        message:"AI did not generate any tasks"
                    })
                }

                // using a inserted var to track the insert
                let inserted=0;

                for(const task of plan.tasks){
                    db.query(q2 ,[plan_id,task.day ,task.title ,task.description ,task.priority ,task.estimated_hours] ,(err,result2)=>{
                        if(err){
                            return res.status(500).json({
                                message:err.message
                            })
                        }
                        inserted++;

                        // if all task inserted
                        if(inserted === plan.tasks.length){

                         resolve({
                            success:true,
                            message:"plan generated successfully",
                            planId:plan_id,
                            plan :plan
                        });
                    }

                    })
                }
                
                console.log("plan stored in the database")            
        })

       
     })

};

exports.acceptPlan=(id,user_id,start_date ,schedule_mode,schedule_days)=>{
    // return api.post(`/ai/plans/${planId}/accept`,
    //     body,
    //     authHeaders
    // );
    return new Promise((resolve,reject)=>{
         const q1=`SELECT * FROM  plans WHERE id=? AND user_id=?`;
    db.query(q1,[id,user_id],(err,result)=>{
        if(err){
            return reject(err);
        }
        if(result.length === 0){
            return res.status(404).json({
                success:false,
                message:"plan not found"
            });
        }
        // to prevent double accepting same plan
        if(result[0].status ==="Accepted"){
            return res.status(400).json({
                success:false,
                message:"This plan has already been accepted"
            })
        }
        //  update the plan 
        const q2 =`UPDATE plans SET schedule_mode=?,start_date=? ,status='Accepted',schedule_days=? WHERE id=?`;

        db.query(q2,[schedule_mode ,start_date,schedule_days,id],(err,result2)=>{
            if(err){
                return res.status(500).json({
                    message:err.message
                });
            }

    if(schedule_mode ==="daily"){
    const q3= `SELECT * FROM plan_tasks WHERE  plan_id =? ORDER BY day_number`;
    db.query(q3,[id],(err,result3)=>{
        if(err){
                return res.status(500).json({
                    message:err.message
                });
            }

            if(result3.length===0){
                 return res.status(404).json({
                   success:false,
                   message:"No tasks found for this plan"
                  });
}

            let inserted=0;
            const startDate=new Date(start_date);
            
            const q4=`INSERT INTO tasks (title,priority,due_date,user_id,description,estimated_hours) VALUES(?,?,?,?,?,?)`;
            for(const task of result3){
                const due_date=new Date(startDate);
                due_date.setDate(
                    due_date.getDate() + (task.day_number -1)
                );
                const due_dateString=due_date.toISOString().split("T")[0];
                

                db.query(q4,[task.title ,task.priority,due_dateString,user_id,task.description,task.estimated_hours],(err,result4)=>{
                    if(err){
                        return res.status(500).json({
                            message:err.message
                        })
                    }
                    inserted++;

                    if(inserted === result3.length){
                    resolve({
                        success:true,
                        message:"tasks added successful!"
                    });
                }
                });
            }
    });

        } });
        
    });


    })
};

exports.getPlans =(user_id)=>{
    // return api.get("/ai/plans",authHeaders);
    return new Promise((resolve,reject)=>{
    const q=`SELECT * FROM plans WHERE user_id=?`;

    db.query(q,[user_id],(err,result)=>{
        if(err){
            return reject(err);
        }
        resolve(result);
    });
    })

};

exports.getPlan=(id,user_id)=>{
    // return api.get(`/ai/plans/${id}`,authHeaders);

    return new Promise((resolve,reject)=>{
        const q=`SELECT * FROM plans WHERE id=? AND user_id=?`;

    db.query(q,[id,user_id],async(err,result1)=>{
        if(err){
            return reject(err);
        }

        if(result1.length ===0){
            return res.status(404).json({
                success:false,
                message:"plan not found"
            });
        }
        const q2=`SELECT * FROM plan_tasks WHERE plan_id=? ORDER BY day_number, id`;

        db.query(q2 ,[id],async(tasksError,result2)=>{
            if(tasksError){
                console.log("failed to fetch tasks",tasksError)
            }

            resolve({
                plan:result1[0],
                tasks:result2
            });
        });
    });
    })
    
};