import { useEffect, useState } from 'react';
import useWebSocket from './useWebSocket';
import { useStopwatch } from 'react-timer-hook';

const useMiddleSocket = () => {
  const [
    socket, 
    interview, 
    setChatInterview, 
    audiointerview, 
    setAudioInterview, 
    audioHistory, 
    setAudioHistory, 
    transcript, 
    setAssemblyTTS,
    audioChunk, 
    setAudioInterviewChunk, 
    loading, 
    setLoading, 
    done, 
    setDone, 
    chunk] = useWebSocket(`${import.meta.env.VITE_REACT_APP_SOCKET_URL}`);
  const [startfetching, setStartFetch] = useState(true);
  const [startchat, setChat] = useState<any>(false);
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
        socket.on('initial connect', (message: any) => {
          console.log("sessionInit", message);
        });

        socket.on('interview chat', (message: any) => {
          console.log(message)
          reset();
          setLoading(false);
          setStartFetch(true);
        });

        socket.on('interview done', (message: any) => {
          console.log("interview done", message)
          setStartFetch(true);
          setChat(false)
          pause()
        })

        socket.on('error', (error: any) => {
          console.error(error.message);
        });
      }
    }, [socket]);
  
    const handleInterview = async (data: any) => {
      const chat = [{
        user_type: "candidate",
        content_type: "answer",
        content: {
          response: data.input,
          time_taken: data.timerValue,
          realtime_evaluation: "null"
        }
      }];
  
      setChatInterview((prevMessages: any) => {
        if (!Array.isArray(prevMessages)) {
          return [...chat];
        }
        return [...prevMessages, ...chat];
      });
  
      setLoading(true);
      await socket?.emit('interview chat', { 
        response: data.input, 
        user_session: data.user_session,
        time_taken: data.timerValue,
        jobId: data.jobId,
        alluserId: data.alluserId
      });
    };

    useEffect(() => {
      if (socket) {
          socket.on('audio transcribe', (message: any) => {
              setAssemblyTTS((prevMessages: any) => {
                if (!prevMessages.some((m: any) => m.query === message.query)) {
                  return [...prevMessages, ...message];
                }
                return prevMessages;
              });
        });
      } 
    }, [socket, transcript]);
  
    const handleAssemblyTTS = async (data: any) => {   
      await socket?.emit('audio transcribe', {
        user_session: data.latest,
        audioblob: data.audioblob,
        question_counter: 1,
        response: ''      
      });
    };
 
  useEffect(() => {
    if (socket) {
        socket.on('audio chat', (message: any) => {
            setAudioHistory((prevMessages: any) => {
              if (!prevMessages.some((m: any) => m.query === message.query)) {
                return [...prevMessages, ...message];
              }
              return prevMessages;
            });
            setLoading(false);
            if(count === 4) {
              pause()
            }
      });
    } 
  }, [socket]);

  const handleAudioInterview = async (data: any) => {    
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

  useEffect(() => {
    if (socket) {
        socket.on('audio chat sentence', () => {
        //  console.log(message)
          reset();
          setLoading(false);
          setStartFetch(true);
      });
    } 
  }, [socket]);

  const handleAudioSentence = async (data: any) => {    
    setLoading(true)
    const chat = [{
      user_type: "candidate",
      content_type: "answer",
      content: {
        response: data.input,
        time_taken: data.timerValue,
        realtime_evaluation: "null"
      }
    }];

    setAudioHistory((prevMessages: any) => {
      if (!Array.isArray(prevMessages)) {
        return [...chat];
      }
      return [...prevMessages, ...chat];
    });

    await socket?.emit('audio chat sentence', { 
      response: data.input, 
      user_session: data.user_session,
      time_taken: data.timerValue
    });
    setCount(data.counter)
  };

  useEffect(() => {
    if (socket) {
        socket.on('audio double chunk', (message: any) => {
            setAudioHistory((prevMessages: any) => {
              if (!prevMessages.some((m: any) => m.query === message.query)) {
                return [...prevMessages, ...message];
              }
              return prevMessages;
            });
            setLoading(false);
            if(count === 4) {
              pause()
            }
      });
    } 
  }, [socket]);

  const handleAudioDouble = async (data: any) => {    
    setLoading(true)
    await socket?.emit('audio double chunk', { 
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
    transcript, 
    handleAssemblyTTS,
    audioChunk, 
    setAudioInterviewChunk,
    handleAudioSentence,
    handleAudioDouble,
    setAssemblyTTS,
    done, 
    setDone,
    chunk,

    startfetching, 
    setStartFetch,
    startchat, 
    setChat,
    
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