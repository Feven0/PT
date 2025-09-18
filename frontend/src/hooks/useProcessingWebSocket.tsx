import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

interface ProcessingUpdate {
  job_id: string;
  status: string;
  step: string;
  message: string;
  progress: number;
  error?: any;
  timestamp: number;
}

interface ProcessingStatus {
  [jobId: string]: ProcessingUpdate;
}

const useProcessingWebSocket = (url: string) => {
  const [socket, setSocket] = useState<any>(null);
  const [processingStatuses, setProcessingStatuses] = useState<ProcessingStatus>({});
  const [subscribedJobs, setSubscribedJobs] = useState<Set<string>>(new Set());
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const newSocket = io(url, {
      query: {
        run_stage: 'dev'
      }
    });

    setSocket(newSocket);

    // Connection events
    newSocket.on('connect', () => {
      console.log('Connected to Processing WebSocket server');
      setIsConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from Processing WebSocket server');
      setIsConnected(false);
    });

    // Processing status events
    newSocket.on('processing_confirmed', (data: any) => {
      console.log('Processing connection confirmed:', data);
    });

    newSocket.on('processing_error', (error: any) => {
      console.error('Processing WebSocket error:', error);
    });

    // Main processing update event
    newSocket.on('processing_update', (data: ProcessingUpdate) => {
      console.log('Processing update received:', data);
      
      setProcessingStatuses((prev: ProcessingStatus) => ({
        ...prev,
        [data.job_id]: {
          ...data,
          timestamp: data.timestamp || Date.now()
        }
      }));

      // Handle specific status changes
      if (data.status === 'completed') {
        console.log(`✅ Job ${data.job_id} completed successfully!`);
      } else if (data.status === 'failed') {
        console.error(`❌ Job ${data.job_id} failed:`, data.message);
        if (data.error) {
          console.error('Error details:', data.error);
        }
      }
    });

    // S3 upload completion event
    newSocket.on('s3_upload_complete', (data: any) => {
      console.log('🎉 S3 upload completed:', data);
      console.log('📁 S3 URL:', data.s3_url);
      
      // Update processing status with S3 URL
      setProcessingStatuses((prev: ProcessingStatus) => ({
        ...prev,
        [data.job_id]: {
          ...prev[data.job_id],
          s3_url: data.s3_url,
          status: 'uploaded',
          message: 'File uploaded to S3 successfully',
          timestamp: Date.now()
        }
      }));
    });

    return () => {
      newSocket.disconnect();
    };
  }, [url]);

  // Start listening to processing updates for a specific job
  const startListening = (jobId: string) => {
    if (socket && !subscribedJobs.has(jobId)) {
      socket.emit('listen_processing', { job_id: jobId });
      setSubscribedJobs((prev: Set<string>) => new Set([...prev, jobId]));
      console.log(`Started listening to processing updates for job: ${jobId}`);
    }
  };

  // Stop listening to processing updates for a specific job
  const stopListening = (jobId: string) => {
    if (socket && subscribedJobs.has(jobId)) {
      socket.emit('stop_listening', { job_id: jobId });
      setSubscribedJobs((prev: Set<string>) => {
        const newSet = new Set(prev);
        newSet.delete(jobId);
        return newSet;
      });
      console.log(`Stopped listening to processing updates for job: ${jobId}`);
    }
  };

  // Get processing status for a specific job
  const getJobStatus = (jobId: string): ProcessingUpdate | null => {
    return processingStatuses[jobId] || null;
  };

  // Get all processing statuses
  const getAllStatuses = (): ProcessingStatus => {
    return processingStatuses;
  };

  // Check if a job is in progress
  const isJobInProgress = (jobId: string): boolean => {
    const status = processingStatuses[jobId];
    return status ? status.status === 'processing' : false;
  };

  // Check if a job is completed
  const isJobCompleted = (jobId: string): boolean => {
    const status = processingStatuses[jobId];
    return status ? status.status === 'completed' : false;
  };

  // Check if a job failed
  const isJobFailed = (jobId: string): boolean => {
    const status = processingStatuses[jobId];
    return status ? status.status === 'failed' : false;
  };

  // Get progress percentage for a job
  const getJobProgress = (jobId: string): number => {
    const status = processingStatuses[jobId];
    return status ? status.progress : 0;
  };

  // Clear status for a specific job
  const clearJobStatus = (jobId: string) => {
    setProcessingStatuses((prev: ProcessingStatus) => {
      const newStatuses = { ...prev };
      delete newStatuses[jobId];
      return newStatuses;
    });
  };

  // Clear all statuses
  const clearAllStatuses = () => {
    setProcessingStatuses({});
  };

  return {
    socket,
    processingStatuses,
    subscribedJobs,
    isConnected,
    startListening,
    stopListening,
    getJobStatus,
    getAllStatuses,
    isJobInProgress,
    isJobCompleted,
    isJobFailed,
    getJobProgress,
    clearJobStatus,
    clearAllStatuses
  };
};

export default useProcessingWebSocket;
