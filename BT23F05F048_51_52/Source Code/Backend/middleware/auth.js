const jwt=require("jsonwebtoken")

const auth=(req,res,next)=>{

    const authHeader=req.headers.authorization;
    
    if(!authHeader){
        return res.status(401).json({
            message:"No Token"
        });
    }

    const token = authHeader.split(" ")[1];

    try{
        const decoded=
        jwt.verify(
            token,
            process.env.JWT_SECRET
        );
        req.user=decoded;
        next();
    }
    catch(err){
        return res.status(401).json({
            message:"Invalid Token"
        });
    }
};

const isAdmin=(req,res,next)=>{

    if(req.user?.role ==="admin") return next();
    
        return res.status(403).json({
            message:"Access Denied. Admin privileges required!"
        });
    
}
module.exports={auth,isAdmin};