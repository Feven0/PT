import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

const useWebSocket = (url: string) => {
  const [socket, setSocket] = useState<any>(null);
  const [interview, setChatInterview] = useState<any[]>([]);
  const [audioInterview, setAudioInterview] = useState<any[]>([]);
  const [audioHistory, setAudioHistory] = useState<any[]>([]);

  useEffect(() => {
    const newSocket = io(url);
    setSocket(newSocket);

    newSocket.on('initial connect', () => {
      console.log('Connected to WebSocket server');
    });

    newSocket.on('interview chat', (message) => {
      // console.log(`Received response: ${message}`);
      setChatInterview((prevMessages) => {
        if (!Array.isArray(prevMessages)) {
          // console.error("prevMessages is not an array:", prevMessages);
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
      // console.log(`Received time_limit reesponse: ${message}`);

      setChatInterview((prevMessages) => {
          if (!Array.isArray(prevMessages)) {
              // console.error("prevMessages is not an array:", prevMessages);
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
                          full_response: message[0]?.content?.full_response,
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
      // console.log(`Received realtime response: ${message}`);
      setChatInterview((prevMessages) => {
          if (!Array.isArray(prevMessages)) {
              // console.error("prevMessages is not an array:", prevMessages);
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
                          realtime_evaluation: message[0]?.content?.realtime_evaluation
                      }
                  }
              ];
          } else {
              return [...prevMessages, message];
          }
      });
    });

    newSocket.on('interview done', (message) => {
      console.log("interview done", message)
    });

    newSocket.on('audio chat', (message) => {
      setAudioInterview((prevMessages) => [...prevMessages, message]);
      setAudioHistory((prevMessages) => [...prevMessages, message]);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
    });

    return () => {
      newSocket.disconnect();
    };
  }, [url]);

  return [socket, interview, setChatInterview, audioInterview, setAudioInterview, audioHistory, setAudioHistory];
};

export default useWebSocket;