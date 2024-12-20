import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

const useWebSocket = (url: string) => {
  const [socket, setSocket] = useState<any>(null);
  const [interview, setChatInterview] = useState<any[]>([]);
  const [audioInterview, setAudioInterview] = useState<any[]>([]);
  const [audioChunk, setAudioInterviewChunk] = useState<any[]>([]);
  const [audioHistory, setAudioHistory] = useState<any[]>([]);
  const [transcript, setAssemblyTTS] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [chunk, setChunkDone] = useState(false);


  useEffect(() => {
    const newSocket = io(url);
    setSocket(newSocket);

    newSocket.on('initial connect', () => {
      console.log('Connected to WebSocket server');
    });

        // ================================= text To text Sockets =============================//

    newSocket.on('interview chat', (message) => {
      setChatInterview((prevMessages) => {
        if (!Array.isArray(prevMessages)) {
          return [message]; 
        }

        if (prevMessages.length > 0 && prevMessages[prevMessages.length - 1].user_type === 'assistant') {
          const lastMessage = prevMessages[prevMessages.length - 1];
          const currentResponse = Array.isArray(lastMessage?.content?.chunk_response)
            ? lastMessage?.content?.chunk_response
            : [];

            const newResponse = Array.isArray(message?.content?.chunk_response) 
            ? [...currentResponse, ...message?.content?.chunk_response] 
            : [...currentResponse, message[0]?.content?.chunk_response]; 
    
          return [
            ...prevMessages.slice(0, -1), 
            {
              ...lastMessage,
              content: {
                ...lastMessage.content,
                chunk_response: newResponse 
              }
            }
          ];
        } else {

          return [...prevMessages, ...message];
        }
      });
    });

    newSocket.on('time_limit', (message) => {
      setChatInterview((prevMessages) => {
          if (!Array.isArray(prevMessages)) {
              return [message];
          }
  
          const lastMessage = prevMessages[prevMessages.length - 1];
  
          if (lastMessage && lastMessage.user_type === 'assistant') {
              return [
                  ...prevMessages.slice(0, -1),
                  {
                      ...lastMessage,
                      content: {
                          ...lastMessage.content,
                          time_limit:  message[0]?.content?.time_limit
                      }
                  }
              ];
          } else {
              return [...prevMessages, message];
          }
      });
    });

    newSocket.on('realtime', (message) => {
      setChatInterview((prevMessages) => {
          if (!Array.isArray(prevMessages)) {
              return [message];
          }

          const lastMessage = prevMessages[prevMessages.length - 1];

          if (lastMessage && lastMessage.user_type === 'assistant') {
              return [
                  ...prevMessages.slice(0, -1),
                  {
                      ...lastMessage,
                      content: {
                          ...lastMessage.content,
                          realtime_evaluation: message[0]?.content?.realtime_evaluation,
                          full_response: message[0]?.content?.full_response
                      }
                  }
              ];
          } else {
              return [...prevMessages, message];
          }
      });
    });

    newSocket.on('last_realtime_evaluation', (message) => {
      
      setChatInterview((prevMessages) => [...prevMessages, ...message]);      
    });

    newSocket.on('interview done', (message) => {
      setDone(true);
      setLoading(false);
      console.log("interview done", message)
    });

    // ================================= ================= =============================//



    
    // ================================= Audio To Audio Sockets =============================//
    newSocket.on('audio transcribe', (message) => {
      console.log('audio transcribe', message);
        setAssemblyTTS((prevMessages) => [...prevMessages, message]);
    });
      
    newSocket.on('audio chat sentence', (message) => {
      setAudioHistory((prevMessages) => {
        if (!Array.isArray(prevMessages)) {
          return [message]; 
        }

        if (prevMessages.length > 0 && prevMessages[prevMessages.length - 1].user_type === 'assistant') {
          const lastMessage = prevMessages[prevMessages.length - 1];
          const currentResponse = Array.isArray(lastMessage?.content?.chunk_response)
            ? lastMessage?.content?.chunk_response
            : [];

            const newResponse = Array.isArray(message?.content?.chunk_response) 
            ? [...currentResponse, ...message?.content?.chunk_response] 
            : [...currentResponse, message[0]?.content?.chunk_response]; 
    
          return [
            ...prevMessages.slice(0, -1), 
            {
              ...lastMessage,
              content: {
                ...lastMessage.content,
                chunk_response: newResponse 
              }
            }
          ];
        } else {

          return [...prevMessages, ...message];
        }
      });
    });

    newSocket.on('audio_time_limit', (message) => {
      setAudioHistory((prevMessages) => {
          if (!Array.isArray(prevMessages)) {
              return [message];
          }
  
          const lastMessage = prevMessages[prevMessages.length - 1];
  
          if (lastMessage && lastMessage.user_type === 'assistant') {
              return [
                  ...prevMessages.slice(0, -1),
                  {
                      ...lastMessage,
                      content: {
                          ...lastMessage.content,
                          time_limit:  message[0]?.content?.time_limit
                      }
                  }
              ];
          } else {
              return [...prevMessages, message];
          }
      });
    });

    newSocket.on('audio_realtime', (message) => {
      setAudioHistory((prevMessages) => {
          if (!Array.isArray(prevMessages)) {
              return [message];
          }

          const lastMessage = prevMessages[prevMessages.length - 1];
          if (lastMessage && lastMessage.user_type === 'assistant') {
              return [
                  ...prevMessages.slice(0, -1),
                  {
                      ...lastMessage,
                      content: {
                          ...lastMessage.content,
                          realtime_evaluation: message[0]?.content?.realtime_evaluation,
                          full_response: message[0]?.content?.full_response
                      }
                  }
              ];
          } else {
              return [...prevMessages, message];
          }          
      });

    });

    newSocket.on('last_audio_realtime_evaluation', (message) => {
      setAudioHistory((prevMessages) => [...prevMessages, ...message]);      
    });


    newSocket.on('audio-one-chunk', (message) => {
      setAudioInterviewChunk((prevMessages) => [...prevMessages, message]);
    });

    newSocket.on('audio-single-chunk-sentence', (message) => {
      setAudioInterview((prevMessages) => [...prevMessages, message]);
    });

    
    newSocket.on('audio-single-chunk', (message) => {
      const blob = new Blob([message], { type: "audio/mpeg" });
      const audioUrl = URL.createObjectURL(blob);
      setAudioInterview((prevMessages) => [...prevMessages, audioUrl]);
    });

    newSocket.on('audio-single-text-chunk',(message) => {
      setAudioInterviewChunk((prevMessages) => [...prevMessages, message]);
    })

    newSocket.on('audio-single-text-chunk-done',() => {
      setChunkDone(true);
    })

        // ================================= ================= =============================//


    newSocket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
    });

    return () => {
      newSocket.disconnect();
    };
  }, [url]);

  return [
    socket, 
    interview, 
    setChatInterview, 
    audioInterview, 
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
    chunk, 
    setChunkDone
  ];
};

export default useWebSocket;