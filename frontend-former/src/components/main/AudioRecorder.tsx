import React, { useState, useRef } from 'react';
import { FaMicrophoneAlt } from 'react-icons/fa';
import { FaCircleStop } from "react-icons/fa6";

import Api from '../../Services/Services';
import "../../styles/AudioRecorder/audiorecorder.css"

const AudioRecorder = ({ sendDataParent, sendDataToParent }) => {
    const [isRecording, setIsRecording] = useState(false);
    const [audioURL, setAudioURL] = useState(null);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const [data, setData] = useState("");

    function handleClick(audio: any) {
        sendDataToParent(audio);
    }

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
            uploadAudio(audioBlob); 
        };

        mediaRecorderRef.current.start();
        setIsRecording(true);
    };

    const stopRecording = () => {
        mediaRecorderRef.current.stop();
        setIsRecording(false);
    };

    const uploadAudio = async (audioBlob) => {
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.wav'); // Change the file name as needed

        try {
            sendDataParent(true)
            const response = await Api.audioUpload(formData)
            console.log('Transcription:', response.data);
            setData(response.data.transcription)
            handleClick(response.data.transcription)
            sendDataParent(false)
        } catch (error) {
            console.error('Error uploading audio:', error);
        }
    };

    return (
        <div className="">
            <div className="audio-recorder">
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
        </div>
    );
};

export default AudioRecorder;