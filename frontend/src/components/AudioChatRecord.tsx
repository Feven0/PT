import { useState, useRef } from 'react';
import { FaMicrophoneAlt } from 'react-icons/fa';
import { FaCircleStop } from "react-icons/fa6";
import Api from '../Services/Services';
import "../styles/AudioRecorder/audiorecorder.css";

const AudioChatRecord = ({ sendDataParent, sendDataToParent, pause }) => {
    const [isRecording, setIsRecording] = useState(false);
    const [audioURL, setAudioURL] = useState(null);
    const [audioBlob, setAudioBlob] = useState();
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const handleClick = (audio: any) => {
        sendDataToParent(audio);
    };

    const startRecording = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        
        mediaRecorderRef.current.ondataavailable = (event) => {
            audioChunksRef.current.push(event.data);
        };

        mediaRecorderRef.current.onstop = () => {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
            const url = URL.createObjectURL(audioBlob);
            setAudioURL(url);
            audioChunksRef.current = [];
            setAudioBlob(audioBlob);
        };

        mediaRecorderRef.current.start();
        setIsRecording(true);
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const uploadAudio = async (audioBlob: any) => {
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.wav'); 

        try {
            sendDataParent(true);
            const response = await Api.audioUpload(formData);
            handleClick(response.data.transcription);
            sendDataParent(false);
            
            //----------------------------------------//
            setAudioURL(null);
            setIsRecording(false);
            //----------------------------------------//
        } catch (error) {
            console.error('Error uploading audio:', error);
        }
    };

    const redoRecording = () => {
        setAudioURL(null);
        setIsRecording(false);
    };

    const submit = () => {
        pause()
        console.log("something")
        if (audioBlob) {
            uploadAudio(audioBlob);   
        }
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
            </div>

            {audioURL && (
                  <audio controls>
                    <source src={audioURL} type="audio/mpeg" />
                </audio>
            )}

            {audioURL && !isRecording && (
                <div className="audio-controls">                    
                    <button onClick={redoRecording} className="redo-button">
                        Redo Recording
                    </button>
                    <button className="submit-button" onClick={submit}>
                        Submit Answer
                    </button>
                </div>
            )}
        </div>
    );
};

export default AudioChatRecord;