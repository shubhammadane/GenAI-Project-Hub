const express = require("express");
const router = express.Router();
const db = require("../config/db");
const { auth, isAdmin } = require("../middleware/auth");
const adminController=require("../controllers/adminController");

router.get("/",[auth,isAdmin],adminController.admin);

module.exports = router;