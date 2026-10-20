const analyticsService=require("../services/analyticsService");

exports.analytics=async (req,res,next)=>{
    try{
        const result=await analyticsService.analytics(req);
        res.json(result);
    }catch(err){
        next(err);
    }
}