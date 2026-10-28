const express=require("express");
const router=express.Router();
const ai=require("../config/gemini");
const db=require("../config/db");
const {auth}=require("../middleware/auth");
const aiController=require("../controllers/aiController")

router.post("/generate-plan",auth, aiController.generatePlan );
router.get("/plans/:id",auth,aiController.getPlan);
router.get("/plans",auth,aiController.getPlans);
router.post("/plans/:id/accept",auth,aiController.acceptPlan);

module.exports=router;