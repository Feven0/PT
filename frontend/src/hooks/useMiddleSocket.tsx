// useMiddleSocket.js
import { useEffect, useState, useCallback, useContext } from 'react';
import useWebSocket from './useWebSocket';
import Cookies from "js-cookie";
import { v4 as uuidv4 } from "uuid";
import { ProviderContext } from '../context/context';

interface AnalysisResponse {
  response: {
    percentage: string | number | undefined | null;
  },
  question: {
    percentage: string | number | undefined | null;
  };
}


const useMiddleSocket = () => {
  const [socket, messages, setMessages, analysis, setChatAnalysis, interview, setChatInterview, upload, setUpload, cvanalysis, setCVAnalysis] = useWebSocket('http://0.0.0.0:8000');
  const [loading, setLoading] = useState(false);
  const [isloading, setIsLoading] = useState(false);
  const [latestAnalyseResponse, setLatestAnalyseResponse] = useState<AnalysisResponse | null>(null);
  const [latestInterviewResponse, setLatestInterviewResponse] = useState<AnalysisResponse | null>(null);
  const [sessionId, setSessionId] = useState<string>("");


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
      cvPath: data.cv_path,
      user: data.latestUserInfo});
  };

  useEffect(() => {
    if (socket) {
      socket.on('interview chat', (message: any) => {
        setChatInterview((prevMessages: any) => {
          if (!prevMessages.some((m: any) => m.query === message.query)) {
            return [...prevMessages, ...message];
          }
          return prevMessages;
        });
        setLatestInterviewResponse(message);
        setLoading(false);
      });
    } 
  }, [socket, interview]);

  const handleInterview = async (data: any) => {
    setLoading(true)
    await socket?.emit('interview chat', { 
      response: data.input, 
      history: data.interview, 
      cvPath: data.cv_path,
      user: data.latestUserInfo,
      question_counter: data.counter
    });
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
    console.log("id", data)
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
    isloading
  };
};

export default useMiddleSocket;