const db=require("../config/db");

exports.getEvents= (user_id)=>{
    return new Promise((resolve,reject)=>{
        const q="SELECT * FROM events where user_id=? ORDER BY event_date,event_time";  
        db.query(q,[user_id],(err,result)=>{
            if(err){
                return reject(err);
            }
            resolve(result);
        })        
    })
};

exports.getSingleEvent =(id,user_id)=>{
    return new Promise((resolve,reject)=>{
        
    const q="SELECT * FROM events WHERE id=? AND user_id=?";
    
    db.query(q,[id,user_id],(err,result)=>{
        if(err){
            return reject(err);
                }
        resolve(result);
    });        
    });
};

exports.upcomingEvent=(user_id)=>{
    return new Promise((resolve,reject)=>{
    const q="SELECT * FROM events WHERE user_id=? AND event_date>=CURDATE() ORDER BY event_date,event_time";

    db.query(q,[user_id],(err,result)=>{
        if(err){
            return reject(err);
        }
        resolve(result);
    })        
    })
};

exports.todaysEvent=(user_id)=>{
    return new Promise((resolve,reject)=>{
    const q="SELECT * FROM events WHERE user_id=? AND event_date=CURDATE()";
    db.query(q,[user_id],(err,result)=>{
        if(err){
            return reject(err);
        }
        resolve(result);
    })        
    })
};

exports.createEvent=(user_id,data)=>{
    return new Promise((resolve,reject)=>{
        const q=`INSERT INTO events (title,description ,event_date, event_time, location , category, priority,
        reminder,completed,user_id) values(?,?,?,?,?,?,?,?,?,?)`;

        db.query(q,[data.title,
        data.description ,
        data.event_date,
        data.event_time,
        data.location ,
        data.category,
        data.priority,
        data.reminder,
        data.completed,
        user_id
        ] , (err,result)=>{
            if(err){
               return reject(err);
            }

            const q2="INSERT INTO app_events (user_id,event_type) VALUES(?,'Created Event')";
            db.query(q2,[user_id],(err2,result2)=>{
                if(err2){
                console.error("failed to log add event",err2);
            }
                resolve({
                message:"Event created successfully",
                id:result.insertId
            });
        });
        });
    })
};

exports.updateEvent=(user_id,eventId,data)=>{
    return new Promise((resolve,reject)=>{
        const q=" UPDATE events SET title=? ,description=?, event_date=?, event_time=?,location=?,category=?, priority=? ,reminder=?,completed=? WHERE id=? AND user_id=? ";

    db.query(q,[data.title,
        data.description || null,
        data.event_date,
        data.event_time,
        data.location,
        data.category || "Personal",
        data.priority || "Medium",
        data.reminder ||false,
        data.completed ||false,
        eventId,
        user_id]
        ,(err,result)=>{
            if(err){
                return reject(err);
            }

            const q2="INSERT INTO app_events (user_id,event_type) VALUES(?,'Updated Event')"
            db.query(q2,[user_id],(err2,result2)=>{
                if(err2){
               console.error("failed to log update event",err2);
            }
            resolve({
                message:"Event Updated"
            })
            })
            
        })        
    })
};

exports.deleteEvent=(user_id,id)=>{
    return new Promise((resolve,reject)=>{
    const q="DELETE FROM events WHERE user_id=? AND id=?";

    db.query(q,[user_id,id],(err,result)=>{
        if(err){
                return reject(err);
            }

            const q2="INSERT INTO app_events (user_id,event_type) VALUES(?,'Deleted Event')"
            db.query(q2,[user_id],(err2,result2)=>{
                if(err2){
                console.error("failed to log delete event",err2);
            }
            resolve({
                message:"Event Deleted"
            })
            });
    })        
    })
}