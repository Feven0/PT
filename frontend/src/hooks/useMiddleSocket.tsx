import { useEffect, useState } from 'react';
import useWebSocket from './useWebSocket';
import { useStopwatch } from 'react-timer-hook';

interface AnalysisResponse {
  response: {
    percentage: string | number | undefined | null;
  },
  question: {
    percentage: string | number | undefined | null;
  };
}


const useMiddleSocket = () => {
  const [socket, interview, setChatInterview] = useWebSocket(`${import.meta.env.VITE_REACT_APP_SOCKET_URL}`);
  const [loading, setLoading] = useState(false);
  const [latestInterviewResponse, setLatestInterviewResponse] = useState<AnalysisResponse | null>(null);
  const [isStarted, setIsStarted] = useState(false);  
  const [count, setCount] = useState();
  const { seconds, minutes, start, pause, reset } = useStopwatch({ autoStart: false});


  useEffect(() => {
    if (socket) {
      socket.on('initial connect', (message: any) => {
        console.log("sessionInit", message)        
      });
    }
  }, [socket]);


  useEffect(() => {
    if (socket) {
        socket.on('interview chat', (message) => {
            setChatInterview((prevMessages: any) => {
              if (!prevMessages.some((m: any) => m.query === message.query)) {
                return [...prevMessages, ...message];
              }
              return prevMessages;
            });
            
            setLatestInterviewResponse(message);
              reset(); 
            setLoading(false);
            console.log("count_inter_ques", count === 8)  
            if(count === 8) {
              pause()
            }
      });
    } 
  }, [socket, interview]);


  const handleInterview = async (data: any) => {
    console.log("jj", data.input)
    const chat = [{
      "user_type": "candidate",
      "content_type": "answer",
      "complete": false,
      "content": {
          "response": data.input,
          "time_taken": data.timerValue,
          "realtime_evaluation": "null"
      }
      }]
    setChatInterview((prevMessages: any) => [...prevMessages, ...chat]);
    setLoading(true)
    await socket?.emit('interview chat', { 
      response: data.input, 
      history: data.interview, 
      user_session: data.user_session,
      question_counter: data.counter,
      time_taken: data.timerValue,
      previous_question: data.previous_question
    });
    setCount(data.counter)
  };

  return {
    handleInterview,
    interview,
    setChatInterview,
    loading,
    seconds,
    minutes,
    start,
    pause,
    reset,
    isStarted, 
    setIsStarted,
    setCount,
  };
};

export default useMiddleSocket;