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
  const { seconds, minutes, start, pause, reset } = useStopwatch({ autoStart: false});
  const [openaiTranscript, setOpenaiTranscript] = useState<string>("");
  const [whisperTranscript, setWhisperTranscript] = useState<string>("");
  const [googleTranscript, setGoogleTranscript] = useState<string>("");
  const [geminiTranscript, setGeminiTranscript] = useState<string>("");
  const [fwTranscript, setFwTranscript] = useState<string>("");


    // In your React component
    useEffect(() => {
      if (socket) {
        socket.on('initial connect', (message: any) => {
          console.log("sessionInit", message);
        });
      }
    }, [socket]);

    // ------------------------------------------------------------------------------------------------
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

    // --------------------------- Gemini Live streaming wiring ---------------------------
    useEffect(() => {
      if (socket) {
        socket.on('audio transcribe gemini', (message: any) => {
          if (typeof message === 'string') {
            setGeminiTranscript(prev => (prev ? prev + ' ' : '') + message);
          }
          console.log('[GEMINI][RX]', message);
        });
      }
      return () => {
        socket?.off?.('audio transcribe gemini');
      };
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
        template_id: null,
        time_taken: data.timerValue,
        challenge_id: data.challenge_id,
        job_profile_id: data.job_profile_id,
        all_user_id: data.all_user_id,
        template: false
      });
    };

    // --------------------------- OpenAI Realtime wiring (legacy) ---------------------------
    useEffect(() => {
      if (socket) {
        socket.on('audio transcribe openai', (message: any) => {
          if (typeof message === 'string') {
            setOpenaiTranscript(prev => (prev ? prev + ' ' : '') + message);
          }
        });
      }
      return () => {
        socket?.off?.('audio transcribe openai');
      };
    }, [socket]);

    const handleOpenAITranscribe = async (data: any) => {
      await socket?.emit('audio transcribe openai', {
        user_session: data.latest,
        audioblob: data.audioblob
      });
    };

    const stopOpenAITranscribe = async () => {
      await socket?.emit('audio transcribe openai', { audioblob: null });
    };

    // --------------------------- Whisper batch STT wiring ---------------------------
    useEffect(() => {
      if (socket) {
        socket.on('audio transcribe whisper', (message: any) => {
          if (typeof message === 'string') {
            setWhisperTranscript(prev => (prev ? prev + ' ' : '') + message);
          }
        });
      }
      return () => {
        socket?.off?.('audio transcribe whisper');
      };
    }, [socket]);

    // --------------------------- Google STT streaming wiring ---------------------------
    useEffect(() => {
      if (socket) {
        socket.on('audio transcribe google', (message: any) => {
          if (typeof message === 'string') {
            setGoogleTranscript(prev => (prev ? prev + ' ' : '') + message);
          }
          console.log('[GOOGLE][RX]', message);
        });
      }
      return () => {
        socket?.off?.('audio transcribe google');
      };
    }, [socket]);

    // --------------------------- faster-whisper local wiring ---------------------------
    useEffect(() => {
      if (socket) {
        socket.on('audio transcribe fw', (message: any) => {
          if (typeof message === 'string') {
            setFwTranscript(prev => (prev ? prev + ' ' : '') + message);
          }
          // console.log('[FW][RX]', message);
        });
      }
      return () => {
        socket?.off?.('audio transcribe fw');
      };
    }, [socket]);

    const handleTemplateInterview = async (data: any) => {
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
        template_id: data.template_id,
        time_taken: data.timerValue,
        job_profile_id: data.job_profile_id,
        challenge_id: data.challenge_id,
        all_user_id: data.all_user_id,
        template: true
      });
    };

    const handleChallengeInterview = async (data: any) => {
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
        challenge_id: 26,
        time_taken: data.timerValue,
        job_profile_id: 0,
        all_user_id: data.all_user_id,
        challenge: true
      });
    };



    // ------------------------------------------------------------------------------------------------
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
        audioblob: data.audioblob    
      });
    };
 


  // ------------------------------------------------------------------------------------------------
  useEffect(() => {
    if (socket) {
        socket.on('audio chat sentence', () => {
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
      template_id: null,
      time_taken: data.timerValue,
      job_profile_id: data.job_profile_id,
      all_user_id: data.all_user_id,
      template: false
    });
  };

  const handleTemplateAudioInterview = async (data: any) => {
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
  
      setLoading(true);
      await socket?.emit('audio chat sentence', { 
        response: data.input, 
        user_session: data.user_session,
        template_id: data.template_id,
        time_taken: data.timerValue,
        job_profile_id: data.job_profile_id,
        challenge_id: data.challenge_id,
        all_user_id: data.all_user_id,
        template: true
      });
    };

    const handleChallengeAudioInterview = async (data: any) => {
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
  
      setLoading(true);
      await socket?.emit('audio chat sentence', { 
        response: data.input, 
        user_session: data.user_session,
        challenge_id: 26,
        time_taken: data.timerValue,
        job_profile_id: 0,
        all_user_id: data.all_user_id,
        challenge: true
      });
    };

  

  return {
    socket,
    audiointerview,
    setAudioInterview,
    setLoading,
    audioHistory, 
    setAudioHistory,
    transcript, 
    handleAssemblyTTS,
    handleOpenAITranscribe,
    openaiTranscript,
    stopOpenAITranscribe,
    whisperTranscript,
    googleTranscript,
    geminiTranscript,
    fwTranscript,
    audioChunk, 
    setAudioInterviewChunk,
    handleAudioSentence,
    setAssemblyTTS,
    done, 
    setDone,
    chunk,

    startfetching, 
    setStartFetch,
    startchat, 
    setChat,
    
    handleInterview,
    handleTemplateInterview, 
    handleChallengeInterview,
    handleTemplateAudioInterview,
    handleChallengeAudioInterview,
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
    handleGoogleTranscribe: async (data: any) => {
      await socket?.emit('audio transcribe google', {
        user_session: data?.latest,
        audioblob: data?.audioblob,
      });
    },
    stopGoogleTranscribe: async () => {
      await socket?.emit('audio transcribe google', { audioblob: null });
    },
    handleGeminiTranscribe: async (data: any) => {
      await socket?.emit('audio transcribe gemini', {
        user_session: data?.latest,
        audioblob: data?.audioblob,
      });
    },
    stopGeminiTranscribe: async () => {
      await socket?.emit('audio transcribe gemini', { audioblob: null });
    },
    handleFwTranscribe: async (data: any) => {
      await socket?.emit('audio transcribe fw', {
        user_session: data?.latest,
        audioblob: data?.audioblob,
      });
    },
    stopFwTranscribe: async () => {
      await socket?.emit('audio transcribe fw', { audioblob: null });
    },
  };
};

export default useMiddleSocket;