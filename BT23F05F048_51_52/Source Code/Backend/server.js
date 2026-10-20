const express=require("express");
const cors=require("cors");
const app=express();
require("dotenv").config();
const errorHandler=require("./middleware/errorHandler.js")
const auth=require("./middleware/auth.js");

const taskRoutes=require("./routes/taskRoutes.js");
const eventRoutes=require("./routes/eventRoutes.js");
const analyticsRoutes=require("./routes/analyticsRoutes.js");
const dashboardRoutes=require("./routes/dashboardRoutes.js");
const authRoutes=require("./routes/authRoutes.js");
const aiRoutes=require("./routes/aiRoutes.js");
const adminRoutes=require("./routes/adminRoutes.js")

app.use(cors());
app.use(express.json());

app.use("/tasks",taskRoutes);
app.use("/events",eventRoutes);
app.use("/analytics",analyticsRoutes);
app.use("/dashboard",dashboardRoutes);
app.use("/auth",authRoutes);
app.use("/ai",aiRoutes);
app.use("/admin",adminRoutes);
app.use(errorHandler);

app.get("/",(req,res)=>{
    res.send("server is listening!");
})


app.listen(process.env.PORT,'0.0.0.0',()=>{
    console.log(`server is listening at port ${process.env.PORT}`);
})