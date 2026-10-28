const express=require("express");
const router=express.Router();
const db=require("../config/db");
const {auth}=require("../middleware/auth");
const dashboardController=require("../controllers/dashboardController")

router.get("/",auth,dashboardController.getDashboardData);

module.exports=router;