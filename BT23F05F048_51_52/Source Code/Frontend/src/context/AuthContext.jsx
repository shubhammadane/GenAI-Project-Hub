import {createContext ,useContext,useEffect,useState} from "react";

const AuthContext =createContext(null);

export function AuthProvider({children}){
    const [user,setUser] =useState(()=>{
        const raw =localStorage.getItem("user");
        return raw ? JSON.parse(raw) :null;
    });
    const [token ,setToken] =useState(()=> localStorage.getItem("token"));

    useEffect(()=>{
        if(token){
            localStorage.setItem("token",token);
        }else{
            localStorage.removeItem("token");
        }
    },[token]);

    useEffect(()=>{
        if(user){
            localStorage.setItem("user",JSON.stringify(user));
        }else{
            localStorage.removeItem("user");
        }
    },[user]);

    const login=({token,user}) => {
        setToken(token);
        setUser(user);
    };
    
    const logout=()=>{
        setToken(null);
        setUser(null);
    }

    const value={
        user,
        token,
        isAuthenticated:Boolean(token),
        login,
        logout,
    };
    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
export function useAuth(){
    return useContext(AuthContext);
}