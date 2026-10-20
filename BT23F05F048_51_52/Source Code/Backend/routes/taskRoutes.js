const express=require("express");
const router=express.Router();

const {auth}=require("../middleware/auth");
const taskController=require("../controllers/taskController");

router.get("/", auth, taskController.getTasks);
router.post("/", auth, taskController.createTask);
router.patch("/:id/completed", auth, taskController.toggleCompleted);
router.put("/:id", auth, taskController.updateTask);
router.delete("/:id", auth, taskController.deleteTask);

module.exports=router;