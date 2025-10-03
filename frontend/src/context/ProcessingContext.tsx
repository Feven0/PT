import React, { createContext, useContext } from 'react';
import useProcessingWebSocket from '../hooks/useProcessingWebSocket';

type ProcessingContextValue = ReturnType<typeof useProcessingWebSocket> | null;

const ProcessingContext = createContext<ProcessingContextValue>(null);

export const ProcessingProvider = ({ children }: { children: React.ReactNode }) => {
  const wsUrl = (import.meta as any).env?.VITE_WS_URL || import.meta.env.VITE_REACT_APP_SOCKET_URL;
  const processing = useProcessingWebSocket(wsUrl);
  return (
    <ProcessingContext.Provider value={processing}>
      {children}
    </ProcessingContext.Provider>
  );
};

export const useProcessing = () => {
  const ctx = useContext(ProcessingContext);
  if (!ctx) {
    throw new Error('useProcessing must be used within ProcessingProvider');
  }
  return ctx;
};


