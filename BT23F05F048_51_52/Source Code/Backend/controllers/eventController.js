const eventService=require("../services/eventService");

exports.getEvents= async (req,res,next)=>{
    try{
        const user_id=req.user.id;
        const result=await eventService.getEvents(user_id);
        res.json(result);
    }catch(err){
        next(err);
    }    
};
exports.getSingleEvent=async (req,res,next)=>{
    try{
        const {id}=req.params;
        const user_id=req.user.id;
        const result=await eventService.getSingleEvent(id,user_id);
        res.json(result);
    }catch(err){
        next(err);
    }
};
exports.upcomingEvent=async (req,res,next)=>{
    try{
        const user_id=req.user.id;
        const result=await eventService.upcomingEvent(user_id);
        res.json(result);
    }catch(err){
        next(err);
    }
};
exports.todaysEvent=async (req,res,next)=>{
    try{
        const user_id=req.user.id;
        const result=await eventService.todaysEvent(user_id);
        res.json(result);        
    }catch(err){
        next(err);
    }
}
exports.createEvent=async (req,res,next)=>{
    try{
        const result=await eventService.createEvent(req.user.id,req.body);
        res.json(result);

    }catch(err){
        next(err);
    }
};
exports.updateEvent=async (req,res,next)=>{
    try{
        const result=await eventService.updateEvent(req.user.id,req.params.id,req.body);
        res.json(result);
    }catch(err){
        next(err);
    }
};
exports.deleteEvent=async (req,res,next)=>{
    try{
        const {id}=req.params;
        const result=await eventService.deleteEvent(req.user.id,id);
        res.json(result);
    }catch(err){
        next(err);
    }
}
