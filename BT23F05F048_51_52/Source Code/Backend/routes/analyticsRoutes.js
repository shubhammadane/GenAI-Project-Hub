const express=require("express");
const router=express.Router();
const db=require("../config/db");
const {auth}=require("../middleware/auth");
const analyticsController=require("../controllers/analyticsController");

router.get("/",auth,analyticsController.analytics);

module.exports=router;