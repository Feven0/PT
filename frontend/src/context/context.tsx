import React, { useState, useEffect, ReactNode } from "react";
import Api from "../Services/Services";

interface ProviderValue {
    session?: any; 
    latestsession?: any; 
}

export const ProviderContext = React.createContext<ProviderValue | undefined>(undefined);

interface Children {
    children: ReactNode; 
}

export const PersonaContext: React.FC<Children> = ({ children }) => {
    const [session, setSession] = useState<any>(undefined); 
    const [latestsession, setLatestSession] = useState<any>(undefined);
    const [refresh, setRefresh] = useState(0);
    
    const sessionData = async () => {
        const userId = localStorage.getItem("userId");
        const response = await Api.fetchSession({ userId });
        setSession(response.data.all_user_data);
        setLatestSession(response.data.latest_user_data);
    };

    useEffect(() => {
        sessionData();
        const intervalId = setInterval(() => {
            setRefresh((prev) => prev + 1);
        }, 5000);

        return () => clearInterval(intervalId);
    }, [refresh]);

    return (
        <ProviderContext.Provider value={{ session, latestsession }}>
            {children}
        </ProviderContext.Provider>
    );
};