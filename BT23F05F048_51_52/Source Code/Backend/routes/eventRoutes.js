const express=require("express");
const router=express.Router();
const db=require("../config/db");
const {auth}=require("../middleware/auth");
const eventController=require("../controllers/eventController");

router.get("/",auth,eventController.getEvents);
router.get("/:id",auth,eventController.getSingleEvent);
router.get("/upcoming",auth,eventController.upcomingEvent);
router.get("/today",auth,eventController.todaysEvent);
router.post("/",auth,eventController.createEvent);
router.put("/:id",auth,eventController.updateEvent);
router.delete("/:id",auth,eventController.deleteEvent);



module.exports=router;
