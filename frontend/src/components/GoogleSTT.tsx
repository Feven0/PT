import React, { useState, useRef, useEffect } from 'react';
import { FaMicrophoneAlt, FaCircleStop } from 'react-icons/fa';
import { Input, Button } from 'antd';
import { EditOutlined, CheckOutlined } from '@ant-design/icons';
import useMiddleSocket from '../hooks/useMiddleSocket';

interface Data {
  sendDataToParent: any
}

const GoogleSTT: React.FC<Data> = ({ sendDataToParent }) => {
    const { 
        googleTranscript, 
        googleFinalHistory, 
        googleLiveInterim, 
        handleGoogleTranscribe, 
        stopGoogleTranscribe,
        setGoogleTranscriptionComplete 
    } = useMiddleSocket();
    
    const [isRecording, setIsRecording] = useState(false);
    const [hasActiveSession, setHasActiveSession] = useState(false);
    const audioContextRef = useRef<AudioContext | null>(null);
    const processorRef = useRef<ScriptProcessorNode | null>(null);
    const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
    const mediaStreamRef = useRef<MediaStream | null>(null);
    const latest = JSON.parse(localStorage.getItem("userSession") || 'null');        
    const [isEditing, setIsEditing] = useState<boolean>(false); 
    
    // Compose Google transcript like OpenAIRealtimeTest.tsx does
    const googleComposed = ([...googleFinalHistory, googleLiveInterim]
        .filter(Boolean)
        .join(' ') || '').trim();
    
    // Fallback to googleTranscript if googleComposed is empty (like OpenAIRealtimeTest.tsx)
    const finalTranscript = googleComposed || googleTranscript || '';
    
    const [editText, setEditText] = useState<string>(finalTranscript); 

    // Listen for transcription completion to update session state
    useEffect(() => {
        const handleTranscriptionComplete = () => {
            setHasActiveSession(false);
        };

        window.addEventListener('google-transcription-complete', handleTranscriptionComplete);
        
        return () => {
            window.removeEventListener('google-transcription-complete', handleTranscriptionComplete);
        };
    }, []);

    function handleClick(audio: any) {
        sendDataToParent(audio);
    }

    const setupAudio = async () => {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaStreamRef.current = stream;
        const source = audioContextRef.current.createMediaStreamSource(stream);
        sourceRef.current = source;
        const processor = audioContextRef.current.createScriptProcessor(8192, 1, 1);
        processorRef.current = processor;
        
        processor.onaudioprocess = (event) => {
            const inputBuffer = event.inputBuffer.getChannelData(0);
            const pcmData = new Int16Array(inputBuffer.length);
            for (let i = 0; i < inputBuffer.length; i++) {
                pcmData[i] = Math.max(-32768, Math.min(32767, inputBuffer[i] * 32767));
            }
            
            const data = {
                latest: latest,
                audioblob: pcmData.buffer
            };
            handleGoogleTranscribe(data);
        };
        
        source.connect(processor);
        processor.connect(audioContextRef.current.destination);
    };

    const teardownAudio = async () => {
        if (processorRef.current) {
            processorRef.current.disconnect();
            processorRef.current.onaudioprocess = null as any;
        }
        if (sourceRef.current) sourceRef.current.disconnect();
        if (audioContextRef.current) await audioContextRef.current.close();
        if (mediaStreamRef.current) mediaStreamRef.current.getTracks().forEach(t => t.stop());
    };

    const startRecording = async () => {
        if (isRecording) return;
        
        // Reset Google STT state
        setGoogleTranscriptionComplete({ status: "pending", message: "Recording..." });
        setHasActiveSession(true);
        
        await setupAudio();
        setIsRecording(true);
    };

    const stopRecording = async () => {
        if (!isRecording || !hasActiveSession) return;
        
        await teardownAudio();
        await stopGoogleTranscribe();
        setIsRecording(false);
        setHasActiveSession(false);
        
        // Update edit text with final transcript after a short delay
        // to ensure the final transcript is received
        setTimeout(() => {
            setEditText(finalTranscript);
        }, 100);
    };

    const handleEditClick = () => {
        setIsEditing(true);
        setEditText(googleComposed); 
    };

    const handleSave = () => {
        // Update the transcript with edited text
        // Note: This would need to be implemented in useMiddleSocket if we want to persist edits
        setIsEditing(false); 
    };

    const handleSubmit = () => {
        handleClick(googleComposed);
    }

    return (
        <div className="audio-recorder-container">
            <div className="audio-recorder-chat">
                {isRecording ? (
                    <FaCircleStop
                        size={30}
                        className="audio-stop"
                        onClick={stopRecording}
                    />
                ) : (
                    <FaMicrophoneAlt
                        size={30}
                        className="audio-start"
                        onClick={startRecording}
                    />
                )}

                {googleComposed?.length !== 0 && (
                    <div className="audio-chunk-container">
                        {isEditing ? (
                            <>
                                <Input.TextArea 
                                    value={editText} 
                                    onChange={(e) => setEditText(e.target.value)} 
                                    autoSize
                                    style={{ marginRight: '10px', width: '300px' }} 
                                />
                                <CheckOutlined 
                                    onClick={handleSave} 
                                    style={{ cursor: 'pointer', color: 'green', fontSize: '18px', marginRight: '10px' }} 
                                />
                                <Button 
                                    type="primary" 
                                    onClick={handleSubmit}
                                    style={{ fontSize: '14px', height: '32px', lineHeight: '32px' }}
                                >
                                    Submit Answer
                                </Button>
                            </>
                        ) : ( 
                            <>
                                <span>
                                    {googleComposed}
                                </span>
                                <EditOutlined 
                                    onClick={handleEditClick} 
                                    style={{ marginLeft: '10px', cursor: 'pointer', color: 'blue', fontSize: '18px' }} 
                                />
                                <Button 
                                    type="primary" 
                                    onClick={handleSubmit}
                                    style={{ marginLeft: '10px', fontSize: '14px', height: '32px', lineHeight: '32px' }}
                                >
                                    Submit Answer
                                </Button>
                            </>
                        )}
                    </div>
                )} 
            </div>
        </div>
    );
};

export default GoogleSTT;
