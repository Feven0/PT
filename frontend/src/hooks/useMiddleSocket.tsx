import { useEffect, useState, useRef } from 'react';
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
  // Google: maintain finals history + live interim for self-correction UX
  const [googleTranscript, setGoogleTranscript] = useState<string>("");
  const [googleFinalHistory, setGoogleFinalHistory] = useState<string[]>([]);
  const [googleLiveInterim, setGoogleLiveInterim] = useState<string>("");
  const [geminiTranscript, setGeminiTranscript] = useState<string>("");
  const [fwTranscript, setFwTranscript] = useState<string>("");
  const [assemblyaiTranscript, setAssemblyaiTranscript] = useState<string>("");
  const [googleTranscriptionComplete, setGoogleTranscriptionComplete] = useState<{status: string, message: string}>({ status: "pending", message: "Ready for new recording" });
  // Refs to avoid stale reads when composing transcript string and for debounce finalize
  const googleFinalHistoryRef = useRef<string[]>([]);
  const googleLiveInterimRef = useRef<string>("");
  const googleLiveFinalizeTimerRef = useRef<number | null>(null);
  useEffect(() => {
    googleFinalHistoryRef.current = googleFinalHistory;
  }, [googleFinalHistory]);
  useEffect(() => {
    googleLiveInterimRef.current = googleLiveInterim;
  }, [googleLiveInterim]);

  const finalizeLiveIntoHistory = () => {
    const live = (googleLiveInterimRef.current || '').trim();
    if (!live) return;
    setGoogleFinalHistory(prev => {
      const next = [...prev, live];
      googleFinalHistoryRef.current = next;
      setGoogleLiveInterim("");
      setGoogleTranscript((next.join(' ') || '').trim());
      return next;
    });
  };

  const scheduleFinalizeDebounce = () => {
    if (googleLiveFinalizeTimerRef.current) {
      clearTimeout(googleLiveFinalizeTimerRef.current);
    }
    // Promote live to finals after short inactivity to preserve context when backend only sends strings
    googleLiveFinalizeTimerRef.current = window.setTimeout(() => {
      finalizeLiveIntoHistory();
      googleLiveFinalizeTimerRef.current = null;
    }, 1200);
  };


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

    // --------------------------- Google STT streaming wiring with epoch-aware appending and live self-correction ---------------------------
    useEffect(() => {
      if (socket) {
        socket.on('audio transcribe google', (message: any) => {
          // Backend may send string (legacy) or structured payload
          if (typeof message === 'string') {
            // Legacy: treat as live interim for self-correction
            setGoogleLiveInterim(message);
            const base = (googleFinalHistoryRef.current.join(' ') || '').trim();
            const live = message.trim();
            setGoogleTranscript([base, live].filter(Boolean).join(' ').trim());
            console.log('[GOOGLE][RX][STR]', message.substring(0, 80));
            scheduleFinalizeDebounce();
            return;
          }

          const text = (message?.text ?? '').toString();
          const isFinal = Boolean(message?.is_final);
          const isUtteranceEnd = Boolean(message?.is_utterance_end);
          const epoch = Number(message?.restart_epoch ?? 0);
          const resultSeq = Number(message?.result_seq ?? -1);

          if (!text.trim()) return;

          if (isFinal) {
            // Cancel any pending debounce that might promote live interims
            if (googleLiveFinalizeTimerRef.current) {
              clearTimeout(googleLiveFinalizeTimerRef.current);
              googleLiveFinalizeTimerRef.current = null;
            }
            // Append final to history; clear live interim; rebuild transcript from new history
            setGoogleFinalHistory(prev => {
              // Dedupe: skip if same as last final already stored
              if (prev.length > 0 && prev[prev.length - 1] === text) {
                // Still clear live and rebuild full transcript
                setGoogleLiveInterim("");
                setGoogleTranscript((prev.join(' ') || '').trim());
                return prev;
              }
              const next = [...prev, text];
              googleFinalHistoryRef.current = next;
              setGoogleLiveInterim("");
              setGoogleTranscript((next.join(' ') || '').trim());
              return next;
            });
            console.log('[GOOGLE][RX][FINAL]', { epoch, resultSeq, preview: text.substring(0, 80) });
          } else {
            // Live self-correction: update interim only; do not overwrite history
            setGoogleLiveInterim(text);
            const base = (googleFinalHistoryRef.current.join(' ') || '').trim();
            const live = text.trim();
            setGoogleTranscript([base, live].filter(Boolean).join(' ').trim());
            console.log('[GOOGLE][RX][INTERIM]', { epoch, resultSeq, preview: text.substring(0, 60) });
            // Do not schedule debounce for structured interims (e.g., utterance_end payloads);
            // let explicit finals control history to avoid duplicates.
            if (!isUtteranceEnd) {
              // If desired in future, we could debounce here for non-utterance end interims.
            }
          }
        });

        // Listen for restart/stop markers to optionally handle UI grouping later
        socket.on('speech_event', (evt: any) => {
          if (evt?.type === 'STREAM_RESTARTING') {
            const payload = evt?.payload || evt; // server sends { type, payload }
            console.log('[GOOGLE][EVENT][STREAM_RESTARTING]', {
              current_epoch: payload?.current_restart_epoch,
              next_epoch: payload?.next_restart_epoch,
            });
            // Append server-provided last_final_text if new
            const last = (payload?.last_final_text || '').trim();
            if (last) {
              setGoogleFinalHistory(prev => {
                if (prev.length === 0 || prev[prev.length - 1] !== last) {
                  const next = [...prev, last];
                  googleFinalHistoryRef.current = next;
                  return next;
                }
                return prev;
              });
            }
            // Do not clear live; let it continue post-restart
            setGoogleTranscript((googleFinalHistoryRef.current.join(' ') || '').trim());
          } else if (evt?.type === 'STOP_SNAPSHOT') {
            const payload = evt?.payload || evt;
            console.log('[GOOGLE][EVENT][STOP_SNAPSHOT]', payload);
            const last = (payload?.last_final_text || '').trim();
            if (last) {
              setGoogleFinalHistory(prev => {
                if (prev.length === 0 || prev[prev.length - 1] !== last) {
                  const next = [...prev, last];
                  googleFinalHistoryRef.current = next;
                  return next;
                }
                return prev;
              });
            }
            // Clear live on stop; rebuild transcript from finals
            setGoogleLiveInterim("");
            setGoogleTranscript((googleFinalHistoryRef.current.join(' ') || '').trim());
          }
        });
      }
      return () => {
        socket?.off?.('audio transcribe google');
        socket?.off?.('speech_event');
        if (googleLiveFinalizeTimerRef.current) {
          clearTimeout(googleLiveFinalizeTimerRef.current);
          googleLiveFinalizeTimerRef.current = null;
        }
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

    // --------------------------- AssemblyAI streaming wiring ---------------------------
    useEffect(() => {
      if (socket) {
        socket.on('audio transcribe', (message: any) => {
          if (typeof message === 'string') {
            setAssemblyaiTranscript(prev => (prev ? prev + ' ' : '') + message);
          }
          console.log('[ASSEMBLYAI][RX]', message);
        });
        
        socket.on('transcription_complete', (message: any) => {
          console.log('[ASSEMBLYAI][COMPLETE]', message);
          // Emit a custom event to notify components that transcription is complete
          window.dispatchEvent(new CustomEvent('assemblyai-transcription-complete', { detail: message }));
        });

        socket.on('google_transcription_complete', (message: any) => {
          console.log('[GOOGLE][COMPLETE]', message);
          setGoogleTranscriptionComplete(message);
          // Emit a custom event to notify components that transcription is complete
          window.dispatchEvent(new CustomEvent('google-transcription-complete', { detail: message }));
        });
      }
      return () => {
        socket?.off?.('audio transcribe');
        socket?.off?.('transcription_complete');
        socket?.off?.('google_transcription_complete');
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
    googleFinalHistory,
    googleLiveInterim,
    googleTranscriptionComplete,
    setGoogleTranscriptionComplete,
    geminiTranscript,
    fwTranscript,
    assemblyaiTranscript,
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