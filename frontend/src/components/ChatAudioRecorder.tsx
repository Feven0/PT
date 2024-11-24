import { useState, useRef } from 'react';
import { FaMicrophoneAlt } from 'react-icons/fa';
import { FaCircleStop } from "react-icons/fa6";
import Api from '../Services/Services';
import "../styles/AudioRecorder/audiorecorder.css"
interface Data {
    sendDataParent: any, sendDataToParent: any
}

const AudioRecorder: React.FC<Data> = ({ sendDataParent, sendDataToParent }) => {
    const [isRecording, setIsRecording] = useState<any>(false);
    const [audioURL, setAudioURL] = useState<any>(null);
    const mediaRecorderRef = useRef<any>(null);
    const audioChunksRef = useRef<any>([]);
    const [data, setData] = useState("");
    console.log(audioURL, data)
    function handleClick(audio: any) {
        sendDataToParent(audio);
    }

    const startRecording = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        
        mediaRecorderRef.current.ondataavailable = (event: any) => {
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

    const uploadAudio = async (audioBlob: any) => {
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.wav'); 

        try {
            sendDataParent(true)
            const response = await Api.audioUpload(formData)
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