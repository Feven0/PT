import { useEffect, useState } from 'react';
import io from 'socket.io-client';

const useWebSocket = (url: any) => {
  const [socket, setSocket] = useState<any>(null);
  const [interview, setChatInterview] = useState<any[]>([]);
  
  useEffect(() => {
    const newSocket = io(url);
    setSocket(newSocket);

    newSocket.on('initial connect', () => {
      console.log('Connected to WebSocket server');
    });

    newSocket.on('interview chat', (message) => {
      console.log(`Received response: ${message}`);
      setChatInterview((prevMessages) => [...prevMessages, ...message]);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
    });

    return () => {
      newSocket.disconnect();
    };
  }, [url]);

  return [socket, interview, setChatInterview];
};

export default useWebSocket;