import React, { useState, useEffect, useRef } from 'react';
import { Button, Card, Typography, Space, Alert, Divider } from 'antd';
import { PlayCircleOutlined, StopOutlined, SoundOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

interface TranscriptionResult {
  turn_order: number;
  turn_is_formatted: boolean;
  end_of_turn: boolean;
  transcript: string;
  end_of_turn_confidence: number;
  words: Array<{
    text: string;
    word_is_final: boolean;
    start: number;
    end: number;
    confidence: number;
  }>;
}

const AssemblyAITest: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState<string>('');
  const [currentTurn, setCurrentTurn] = useState<string>('');
  const [sessionId, setSessionId] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [isConnected, setIsConnected] = useState(false);
  const [audioDuration, setAudioDuration] = useState<number>(0);
  
  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // AssemblyAI API key - you should move this to environment variables
  const API_KEY = "49e5f82458584a70b847f477a035ce48";
  const WS_URL = "wss://api.assemblyai.com/v2/realtime/ws";
  
  // Get temporary token for WebSocket authentication
  const getTemporaryToken = async () => {
    try {
      // Use the correct endpoint from the documentation
      const response = await fetch('https://streaming.assemblyai.com/v3/token?expires_in_seconds=60', {
        method: 'GET',
        headers: {
          'Authorization': API_KEY,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`Failed to get token: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('🔑 Temporary token received:', data.token ? 'Token received' : 'No token');
      return data.token;
    } catch (error) {
      console.error('❌ Error getting temporary token:', error);
      throw error;
    }
  };

  const startRecording = async () => {
    try {
      console.log('🎤 Starting recording process...');
      setError('');
      
      // Check browser compatibility
      console.log('🔍 Checking browser compatibility...');
      console.log('navigator.mediaDevices:', !!navigator.mediaDevices);
      console.log('getUserMedia support:', !!navigator.mediaDevices?.getUserMedia);
      console.log('WebSocket support:', !!window.WebSocket);
      console.log('AudioContext support:', !!window.AudioContext);
      
      // Get microphone access
      console.log('🎙️ Requesting microphone access...');
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        } 
      });
      
      console.log('✅ Microphone access granted');
      console.log('Stream tracks:', stream.getTracks().length);
      console.log('Audio tracks:', stream.getAudioTracks().length);
      
      streamRef.current = stream;
      
      // Create audio context for processing
      console.log('🔊 Creating AudioContext...');
      const audioContext = new AudioContext({ sampleRate: 16000 });
      console.log('AudioContext sample rate:', audioContext.sampleRate);
      console.log('AudioContext state:', audioContext.state);
      audioContextRef.current = audioContext;
      
      // Get temporary token for WebSocket authentication
      console.log('🔑 Getting temporary token...');
      const temporaryToken = await getTemporaryToken();
      
      // Create WebSocket connection
      console.log('🌐 Creating WebSocket connection...');
      const wsUrl = `${WS_URL}?sample_rate=16000&token=${temporaryToken}`;
      console.log('WebSocket URL:', wsUrl.replace(temporaryToken, 'TOKEN_HIDDEN'));
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      
      ws.onopen = () => {
        console.log('✅ WebSocket connected successfully');
        setIsConnected(true);
        setIsRecording(true);
        
        // Send initial configuration
        const config = {
          type: "UpdateConfiguration",
          end_of_turn_confidence_threshold: 0.4,
          min_end_of_turn_silence_when_confident: 400,
          max_turn_silence: 1280
        };
        console.log('📤 Sending configuration:', config);
        ws.send(JSON.stringify(config));
      };
      
      ws.onmessage = (event) => {
        try {
          console.log('📨 Raw WebSocket message received:', event.data);
          const data = JSON.parse(event.data);
          console.log('📋 Parsed message data:', data);
          
          switch (data.type) {
            case 'Begin':
              console.log('🚀 Session started with ID:', data.id);
              setSessionId(data.id);
              break;
              
            case 'Turn':
              console.log('🔄 Turn data received:', data);
              handleTurnData(data as TranscriptionResult);
              break;
              
            case 'Termination':
              console.log('🏁 Session terminated, duration:', data.audio_duration_seconds);
              setAudioDuration(data.audio_duration_seconds);
              break;
              
            case 'Error':
              console.error('❌ AssemblyAI Error:', data.error);
              setError(`AssemblyAI Error: ${data.error}`);
              break;
              
            default:
              console.log('❓ Unknown message type:', data.type);
              // Handle authentication errors that don't have a type field
              if (data.error) {
                console.error('❌ Authentication/API Error:', data.error);
                if (data.error === 'Not authorized') {
                  setError('Authentication failed. Please check your API key.');
                } else {
                  setError(`API Error: ${data.error}`);
                }
              }
          }
        } catch (err) {
          console.error('❌ Error parsing WebSocket message:', err);
          console.error('Raw message:', event.data);
        }
      };
      
      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        console.error('WebSocket readyState:', ws.readyState);
        setError('WebSocket connection error');
      };
      
      ws.onclose = (event) => {
        console.log('🔌 WebSocket disconnected');
        console.log('Close code:', event.code);
        console.log('Close reason:', event.reason);
        console.log('Was clean:', event.wasClean);
        setIsConnected(false);
        setIsRecording(false);
      };
      
      // Start audio processing
      startAudioProcessing(stream, audioContext, ws);
      
    } catch (err) {
      console.error('❌ Error starting recording:', err);
      const error = err as Error;
      console.error('Error details:', {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
      setError(`Failed to start recording: ${error.message || String(err)}`);
    }
  };

  const startAudioProcessing = (stream: MediaStream, audioContext: AudioContext, ws: WebSocket) => {
    console.log('🎵 Starting audio processing...');
    
    const source = audioContext.createMediaStreamSource(stream);
    console.log('📡 Created media stream source');
    
    const processor = audioContext.createScriptProcessor(4096, 1, 1);
    console.log('⚙️ Created script processor with buffer size:', 4096);
    
    let audioChunkCount = 0;
    
    processor.onaudioprocess = (event) => {
      if (ws.readyState === WebSocket.OPEN) {
        const inputBuffer = event.inputBuffer;
        const inputData = inputBuffer.getChannelData(0);
        
        // Log first few audio chunks for debugging
        if (audioChunkCount < 3) {
          console.log(`🎧 Audio chunk ${audioChunkCount}:`, {
            length: inputData.length,
            sampleRate: inputBuffer.sampleRate,
            duration: inputBuffer.duration,
            firstFewSamples: Array.from(inputData.slice(0, 5))
          });
        }
        
        // Convert float32 to int16
        const int16Array = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          int16Array[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
        }
        
        // Convert to base64 and send
        const base64 = btoa(String.fromCharCode(...new Uint8Array(int16Array.buffer)));
        
        if (audioChunkCount < 3) {
          console.log(`📤 Sending audio chunk ${audioChunkCount}, base64 length:`, base64.length);
        }
        
        ws.send(base64);
        audioChunkCount++;
      } else {
        console.warn('⚠️ WebSocket not open, skipping audio chunk. ReadyState:', ws.readyState);
      }
    };
    
    source.connect(processor);
    processor.connect(audioContext.destination);
    console.log('🔗 Audio processing chain connected');
  };

  const handleTurnData = (data: TranscriptionResult) => {
    console.log('🔄 Processing turn data:', {
      end_of_turn: data.end_of_turn,
      turn_is_formatted: data.turn_is_formatted,
      transcript: data.transcript,
      confidence: data.end_of_turn_confidence,
      word_count: data.words?.length
    });
    
    if (data.end_of_turn) {
      // Final transcript
      console.log('✅ Final transcript received:', data.transcript);
      setTranscript(prev => prev + (prev ? ' ' : '') + data.transcript);
      setCurrentTurn('');
      
      if (data.turn_is_formatted) {
        console.log('✨ Formatted transcript:', data.transcript);
      }
    } else {
      // Partial transcript
      console.log('⏳ Partial transcript:', data.transcript);
      setCurrentTurn(data.transcript);
    }
  };

  const stopRecording = () => {
    console.log('🛑 Stopping recording...');
    
    if (wsRef.current) {
      console.log('📤 Sending terminate message to WebSocket');
      wsRef.current.send(JSON.stringify({ type: "Terminate" }));
      wsRef.current.close();
      wsRef.current = null;
    }
    
    if (streamRef.current) {
      console.log('🎙️ Stopping audio tracks');
      streamRef.current.getTracks().forEach(track => {
        console.log('Stopping track:', track.kind, track.label);
        track.stop();
      });
      streamRef.current = null;
    }
    
    if (audioContextRef.current) {
      console.log('🔊 Closing AudioContext');
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    setIsRecording(false);
    setIsConnected(false);
    setCurrentTurn('');
    console.log('✅ Recording stopped');
  };

  const clearTranscript = () => {
    setTranscript('');
    setCurrentTurn('');
    setSessionId('');
    setAudioDuration(0);
  };

  useEffect(() => {
    return () => {
      // Cleanup on component unmount
      if (isRecording) {
        stopRecording();
      }
    };
  }, []);

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto' }}>
      <Title level={2}>
        <SoundOutlined /> AssemblyAI Streaming Test
      </Title>
      
      <Paragraph>
        This page tests AssemblyAI's Universal Streaming API in the browser. 
        It captures audio from your microphone and sends it to AssemblyAI for real-time transcription.
      </Paragraph>

      {error && (
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: '16px' }}
        />
      )}

      <Card title="Recording Controls" style={{ marginBottom: '16px' }}>
        <Space>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={startRecording}
            disabled={isRecording}
            size="large"
          >
            Start Recording
          </Button>
          
          <Button
            danger
            icon={<StopOutlined />}
            onClick={stopRecording}
            disabled={!isRecording}
            size="large"
          >
            Stop Recording
          </Button>
          
          <Button onClick={clearTranscript} disabled={isRecording}>
            Clear Transcript
          </Button>
        </Space>
        
        <div style={{ marginTop: '16px' }}>
          <Text strong>Status: </Text>
          <Text type={isConnected ? 'success' : 'secondary'}>
            {isConnected ? 'Connected & Recording' : 'Disconnected'}
          </Text>
        </div>
        
        {sessionId && (
          <div>
            <Text strong>Session ID: </Text>
            <Text code>{sessionId}</Text>
          </div>
        )}
        
        {audioDuration > 0 && (
          <div>
            <Text strong>Audio Duration: </Text>
            <Text>{audioDuration.toFixed(2)} seconds</Text>
          </div>
        )}
      </Card>

      <Card title="Live Transcription">
        <div style={{ minHeight: '200px', padding: '16px', backgroundColor: '#f5f5f5', borderRadius: '6px' }}>
          {transcript && (
            <div>
              <Text strong>Final Transcript:</Text>
              <Paragraph style={{ marginTop: '8px', fontSize: '16px' }}>
                {transcript}
              </Paragraph>
            </div>
          )}
          
          {currentTurn && (
            <div>
              {transcript && <Divider />}
              <Text strong>Current Turn (Live):</Text>
              <Paragraph style={{ marginTop: '8px', fontSize: '16px', color: '#1890ff' }}>
                {currentTurn}
              </Paragraph>
            </div>
          )}
          
          {!transcript && !currentTurn && (
            <Text type="secondary">Start recording to see transcription...</Text>
          )}
        </div>
      </Card>

      <Card title="Browser Compatibility Info" style={{ marginTop: '16px' }}>
        <ul>
          <li>✅ WebSocket API support</li>
          <li>✅ Web Audio API support</li>
          <li>✅ getUserMedia API support</li>
          <li>✅ Base64 encoding support</li>
        </ul>
        
        <Alert
          message="Note"
          description="This implementation uses direct WebSocket connection to AssemblyAI's streaming API, bypassing their JavaScript SDK to ensure browser compatibility."
          type="info"
          style={{ marginTop: '16px' }}
        />
        
        <Alert
          message="CORS Issue"
          description="The browser is blocking the token request due to CORS policy. According to AssemblyAI documentation, temporary tokens should be generated on the server side to avoid exposing API keys. For testing purposes, we're trying the correct endpoint."
          type="warning"
          style={{ marginTop: '16px' }}
        />
        
        <Alert
          message="Server-Side Solution"
          description="For production, create a server endpoint that generates temporary tokens using your API key, then call that endpoint from the frontend."
          type="info"
          style={{ marginTop: '16px' }}
        />
      </Card>
    </div>
  );
};

export default AssemblyAITest;
