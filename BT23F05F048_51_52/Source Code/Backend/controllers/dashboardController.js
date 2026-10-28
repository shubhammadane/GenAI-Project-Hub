const dashboardService=require("../services/dashboardService");

exports.getDashboardData=async (req,res,next)=>{
    try{
        const result=await dashboardService.getDashboardData(req.user.id);
        res.json(result);
    }catch(err){
        next(err);
    }
}