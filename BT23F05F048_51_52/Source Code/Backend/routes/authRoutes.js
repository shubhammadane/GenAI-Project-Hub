const express=require("express");
const router=express.Router();
const db=require("../config/db");
const bcrypt=require("bcrypt");
const jwt=require("jsonwebtoken");
const {auth}=require("../middleware/auth");
const authController=require("../controllers/authController");
require("dotenv").config();

router.post("/register",authController.register);
router.post("/login",authController.login);


router.get("/profile",
    auth,(req,res)=>{
        res.json({
            user:req.user
        });
    }
);

module.exports=router;