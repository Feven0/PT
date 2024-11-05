import { useEffect, useState } from 'react';
import useWebSocket from './useWebSocket';
import { useStopwatch } from 'react-timer-hook';
import { message } from 'antd';

interface AnalysisResponse {
  response: {
    percentage: string | number | undefined | null;
  },
  question: {
    percentage: string | number | undefined | null;
  };
}

const useMiddleSocket = () => {
  const [socket, interview, setChatInterview, audiointerview, setAudioInterview, audioHistory, setAudioHistory] = useWebSocket(`${import.meta.env.VITE_REACT_APP_SOCKET_URL}`);
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


  // useEffect(() => {
  //   if (socket) {
  //       socket.on('interview chat', (message) => {
  //           // setChatInter(message)
  //           setChatInter((prevMessages: any) => {
  //             if (!prevMessages.some((m: any) => m.query === message.query)) {
  //               return [...prevMessages, ...message];
  //             }
  //             return prevMessages;
  //           });

  //           setChatInterview((prevMessages: any) => {
  //             if (!prevMessages.some((m: any) => m.query === message.query)) {
  //               return [...prevMessages, ...message];
  //             }
  //             return prevMessages;
  //           });
            
  //           setLatestInterviewResponse(message);
  //             reset(); 
  //           setLoading(false);
  //           console.log("count_inter_ques", count === 8)  
  //           if(count === 8) {
  //             pause()
  //           }
  //     });
  //   } 
  // }, [socket, interview]);
  
    useEffect(() => {
      if (socket) {
        socket.on('initial connect', (message) => {
          console.log("sessionInit", message);
        });
  
        socket.on('interview chat', (message) => {
          console.log(`Instant received message: `, message);
          setLatestInterviewResponse(message);
          reset();
          setLoading(false);
        });
  
        socket.on('error', (error) => {
          console.error(error.message);
        });
      }
    }, [socket]);
  
    const handleInterview = async (data: any) => {
      console.log("Handling interview data:", data.input);
      const chat = [{
        user_type: "candidate",
        content_type: "answer",
        complete: false,
        content: {
          response: data.input,
          time_taken: data.timerValue,
          realtime_evaluation: "null"
        }
      }];
  
      setChatInterview((prevMessages) => {
        if (!Array.isArray(prevMessages)) {
          return [...chat];
        }
        return [...prevMessages, ...chat];
      });
  
      setLoading(true);
      await socket?.emit('interview chat', { 
        response: data.input, 
        history: data.interview, 
        user_session: data.user_session,
        question_counter: data.counter,
        time_taken: data.timerValue,
        previous_question: data.previous_question
      });
      setCount(data.counter);
    };
 


  useEffect(() => {
    if (socket) {
        socket.on('audio chat', (message: any) => {
            setAudioInterview((prevMessages: any) => {
              if (!prevMessages.some((m: any) => m.query === message.query)) {
                return [...prevMessages, ...message];
              }
              return prevMessages;
            });
            setAudioHistory((prevMessages: any) => {
              if (!prevMessages.some((m: any) => m.query === message.query)) {
                return [...prevMessages, ...message];
              }
              return prevMessages;
            });
            // setAudioHistory((prevMessages: any) => [
            //   ...prevMessages,
            //   message, // Add each new chunk to the history
            // ]);
            // reset(); 
            setLoading(false);
            //console.log("count_inter_quest", count === 4)  
            if(count === 4) {
              pause()
            }
      });
    } 
  }, [socket, interview]);

  const handleAudioInterview = async (data: any) => {
    // const chat = [{
    //   "user_type": "candidate",
    //   "content_type": "answer",
    //   "complete": false,
    //   "content": {
    //       "response": data.input,
    //       "time_taken": data.timerValue,
    //       "realtime_evaluation": "null"
    //   }
    //   }]
    // setAudioHistory((prevMessages: any) => {
    //   if (!Array.isArray(prevMessages)) {
    //     return [...chat];
    //   }
    //   return [...prevMessages, ...chat];
    // });
    
    setLoading(true)
    await socket?.emit('audio chat', { 
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
    handleAudioInterview,
    audiointerview,
    setAudioInterview,
    setLoading,
    audioHistory, 
    setAudioHistory,
    
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