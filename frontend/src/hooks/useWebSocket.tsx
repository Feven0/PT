import { useEffect, useState, useContext } from 'react';
import io from 'socket.io-client';
import Cookies from "js-cookie";
import { v4 as uuidv4 } from "uuid";

const useWebSocket = (url: any) => {
  const [socket, setSocket] = useState<any>(null);
  const [analysis, setChatAnalysis] = useState<any[]>([]);
  const [interview, setChatInterview] = useState<any[]>([]);
  const [cvanalysis, setCVAnalysis] = useState<any[]>([]);
  
  useEffect(() => {
    const newSocket = io(url);
    setSocket(newSocket);

    newSocket.on('initial connect', () => {
      console.log('Connected to WebSocket server');
    });

    newSocket.on('analyse', (message) => {
      console.log(`Received response: ${message}`);
      setChatAnalysis((prevMessages) => [...prevMessages, ...message]);
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

  return [socket,analysis, setChatAnalysis, interview, setChatInterview, cvanalysis, setCVAnalysis];
};

export default useWebSocket;