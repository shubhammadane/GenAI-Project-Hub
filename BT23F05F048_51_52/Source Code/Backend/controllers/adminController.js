const adminService=require("../services/adminService");

exports.admin=async (req, res ,next)=>{
    try{
        const result=await adminService.admin();
        res.json(result);
    }catch(err){
        next(err);
    }
}