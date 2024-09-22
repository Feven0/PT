// useMiddleSocket.js
import { useEffect, useState, useCallback, useContext } from 'react';
import useWebSocket from './useWebSocket';
import { useStopwatch } from 'react-timer-hook';
import { ProviderContext } from '../context/context';
import Api from '../Services/Services';

interface AnalysisResponse {
  response: {
    percentage: string | number | undefined | null;
  },
  question: {
    percentage: string | number | undefined | null;
  };
}


const useMiddleSocket = () => {
  const [socket, analysis, setChatAnalysis, interview, setChatInterview, cvanalysis, setCVAnalysis, interview_metrics, setEvaluationMetrics] = useWebSocket('http://0.0.0.0:5500');
  const { latestinterviewchat, latestUserData, latestsession, setStart } = useContext(ProviderContext);
  const [loading, setLoading] = useState(false);
  const [isloading, setIsLoading] = useState(false);
  const [latestAnalyseResponse, setLatestAnalyseResponse] = useState<AnalysisResponse | null>(null);
  const [latestInterviewResponse, setLatestInterviewResponse] = useState<AnalysisResponse | null>(null);
  const [sessionId, setSessionId] = useState<string>("");
  const [isStarted, setIsStarted] = useState(false);  
  const [count, setCount] = useState();
  const { seconds, minutes, start, pause, reset } = useStopwatch({ autoStart: false});


  useEffect(() => {
    if (socket) {
      socket.on('initial connect', (message: any) => {
        console.log("sessionInit", message)
        // localStorage.setItem("al", JSON.stringify(message))
        
      });
    }
  }, [socket]);


  useEffect(() => {
    if (socket) {
      socket.on('analyse', (message: any) => {
        setChatAnalysis((prevMessages: any) => {
          if (!prevMessages.some((m: any) => m.query === message.query)) {
            return [...prevMessages, ...message];
          }
          return prevMessages;
        });
  
        setLatestAnalyseResponse(message); 
        setLoading(false);
      });
    } 

  }, [socket, analysis]);

  const handleAnalyse = async (data: any) => {
    setLoading(true)
    await socket?.emit('analyse', {
      message: data.input, 
      cvPath: data.profile,
      user: data.latestUserInfo});
  };

  const save_metrics_to_db = async(response_metrics) => {
    if(interview_metrics !== "") {
      const data = {
        user_session: latestsession,
        user: latestUserData,
      }
      const combinedData = {
        response: response_metrics,
        data: data,
      };
      const response = await Api.saveEvaluationMetrics(combinedData)
    }

  }

  useEffect(() => {
    if (socket) {
        socket.on('interview chat', (data) => {
            const { message, response_metrics } = data
            setChatInterview((prevMessages: any) => {
              if (!prevMessages.some((m: any) => m.query === message.query)) {
                return [...prevMessages, ...message];
              }
              return prevMessages;
            });

            setEvaluationMetrics(response_metrics);
            if (response_metrics !== "") {
              save_metrics_to_db(response_metrics)
            } else {
              console.log("not saving metrics to db")
            }
            
            setLatestInterviewResponse(message);
              reset(); 
            setLoading(false);
            console.log("count_inter", count === 4)  
            if(count === 4) {
              pause()
            }
      });
    } 
  }, [socket, interview]);


  const handleInterview = async (data: any) => {
    setLoading(true)
    await socket?.emit('interview chat', { 
      response: data.input, 
      history: data.interview, 
      user_session: data.user_session,
      user: data.latestUserInfo,
      question_counter: data.counter,
      time_taken: data.timerValue
    });
    setCount(data.counter)
  };


  useEffect(() => {
    if (socket) {
      socket.on('cv analyse', (message: any) => {
        setCVAnalysis((prevMessages: any) => {
          if (!prevMessages.some((m: any) => m.query === message.query)) {
            return [...prevMessages, message];
          }
          return prevMessages;
        });
        setLatestAnalyseResponse(message); 
        setLoading(false);
        setIsLoading(false)
      });
    }
  }, [socket, setCVAnalysis]);

  const handleCVAnalyse = async (data: any) => {
    setIsLoading(true)
    setLoading(true)
    await socket?.emit('cv analyse', { userId: data.id, message: data.input, sessionId: sessionId});
  };

  return {
    handleInterview,
    interview,
    setChatInterview,
    handleAnalyse,
    analysis, 
    setChatAnalysis,
    loading,
    latestAnalyseResponse,
    latestInterviewResponse,
    cvanalysis,
    handleCVAnalyse,
    sessionId,
    isloading,
    seconds,
    minutes,
    start,
    pause,
    reset,
    isStarted, setIsStarted,
    setCount,
    interview_metrics, setEvaluationMetrics
  };
};

export default useMiddleSocket;