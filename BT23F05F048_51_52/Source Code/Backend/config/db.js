require("dotenv").config();

 const mysql=require("mysql2");

 const connection=mysql.createPool({
    host:process.env.DB_HOST,
    user:process.env.DB_USER,
    password:process.env.DB_PASSWORD,
    database:process.env.DB_NAME ,
    dateStrings:true,
    waitForConnections:true,
    connectionLimit:10,
}
 );

 connection.getConnection((err)=>{
    if(err){
        console.log("Database connection failed:",err);
        return;
    }
    console.log("Database Connected!");
 });
module.exports=connection;