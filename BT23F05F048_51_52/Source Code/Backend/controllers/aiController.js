const aiService= require("../services/aiService");
const ai=require("../config/gemini");
exports.generatePlan=async (req,res,next)=>{
    try{
        const {prompt} =req.body;
    const systemPrompt = `
       You are an AI Study Planner. 

Generate a personalized study plan.

Return ONLY valid JSON.

Rules:
1. Do not return markdown.
2. Do not use \`\`\`json.
3. Return JSON only.
4. difficulty must be exactly one of:
   - Easy
   - Medium
   - Hard
5. priority must be exactly one of:
   - High
   - Medium
   - Low
6. estimated_hours_per_day must be between 1 and 8.
7. estimated_hours must be between 1 and 8.
8. Number of tasks must equal duration_days.
9. Include exactly one task for each day, numbered sequentially from 1 to duration_days.
10. Return tasks in ascending day order.

JSON Format:

{
  "goal":"",
  "summary":"",
  "duration_days":0,
  "difficulty":"",
  "estimated_hours_per_day":0,
  "tasks":[
      {
        "day":1,
        "title":"",
        "description":"",
        "priority":"",
        "estimated_hours":0
      }
  ]
}

User Prompt:
${prompt}`;
   
   
        const response= await ai.models.generateContent({
            model:"gemini-2.5-flash",
            contents:systemPrompt
        });

        // remove markdown 

        let plan =response.text;
        plan =plan.replace(/```json/g ,"").replace(/```/g,"").trim();

        plan =JSON.parse(plan);
        if (Array.isArray(plan.tasks)) {
            plan.tasks.sort((firstTask, secondTask) => Number(firstTask.day) - Number(secondTask.day));
        }



        const resultPlan=await aiService.generatePlan(req.user.id,prompt,plan);
        res.json(resultPlan);
    }
    catch(err){
        next(err);
    }
    };

exports.acceptPlan=async (req,res,next)=>{
        try{
        const {id}=req.params;
        const {start_date ,schedule_mode,schedule_days}=req.body;
        const user_id=req.user.id;

    //  here user is accepting the plan and then the tasks are added
    // in the tasks table  - there are 3 mode (daily ,weekdays,weekends,custom)
    // case 1 -daily
    if(!start_date || !schedule_mode ){
        return res.status(400).json({
            success:false,
            message:"start date and schedule mode are required"
        });
    }
        const acceptPlanResult=await aiService.acceptPlan(id,user_id,start_date ,schedule_mode,schedule_days);
        res.json(acceptPlanResult);
        }
        catch(err){
            next(err);
        }
    };
exports.getPlans=async (req,res,next)=>{
        try{
            const allPlans=await aiService.getPlans(req.user.id);
            res.json(allPlans);
        }
        catch(err){
            next(err);
        }
};

exports.getPlan =async (req,res,next)=>{
    try{
        const {id}=req.params;

    const singlePlan=await aiService.getPlan(id,req.user.id);
    res.json(singlePlan);
    }
    catch(err){
        next(err);
        }
}