import React,{ useState, useEffect } from "react";
import Api from "../Services/Services";
export const ProviderContext = React.createContext();


export const PersonaContext = ({ children }) => {
    const [jbId, setJobId] = useState()
    const [userData, setUserData] = useState()
    const [latestUserData, setLatestUserData] = useState()
    const [latestanalysis, setLatestAnalysis] = useState([])
    const [latestanalysischat, setLatestAnalysisChat] = useState([])
    const [latestinterviewchat, setLatestInterviewChat] = useState([])
    const [session, setSession] = useState()
    const [latestsession, setLatestSession] = useState()
    const [refresh, setRefresh] = useState(0);
    const [start, setStart] = useState(true)
    const userId = 'a82d3efe-0289-4acf-a93b-fcc768355e5b'
    
    

    const sessionData = async () => {
      const response = await Api.fetchSession({userId})
      console.log("responding second...", response.data)
      setSession(response.data.all_user_data)
      setLatestSession(response.data.latest_user_data)
    }

    const sessionJobData = async () => {
      if(start){
        if(latestsession !== undefined){
          const job_id = localStorage.getItem("JobId")
          console.log("job Id..", job_id)
          const data = {sessionId: latestsession?.sessionId, jbId: job_id}
          const response = await Api.fetchSessionJob(data)
          console.log("responding session job...", response.data)
          setUserData(response.data.latest_user_data)
          setLatestUserData(response.data.latest_user_data)
          setLatestAnalysis(response.data.latest_analysis)
          setLatestAnalysisChat(response.data.latest_analysischat)
          setLatestInterviewChat(response.data.latest_interviewchat)
        }
      }
    }
    
    console.log("record", start)

    useEffect(() => {
      if (start) {
        sessionData();
        sessionJobData(); 
        const intervalId = setInterval(() => {
          setRefresh((prev) => prev + 1);
        }, 500000);
  
        return () => clearInterval(intervalId); 
      }
    }, [start, latestsession]);
    
      return (
        <ProviderContext.Provider
          value={{
            userData,
            setUserData,
            setJobId,
            latestUserData,
            latestanalysis,
            latestanalysischat,
            latestinterviewchat,
            session,
            latestsession,
            setStart
            }}
          >
          {children}
        </ProviderContext.Provider>
      )
  };


