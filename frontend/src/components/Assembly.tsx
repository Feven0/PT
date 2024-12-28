import React, { useState, useRef } from "react";
import useMiddleSocket from "../hooks/useMiddleSocket";
import { FaMicrophoneAlt } from 'react-icons/fa';
import { FaCircleStop } from "react-icons/fa6";
import { EditOutlined, CheckOutlined } from '@ant-design/icons';
import { Input, Button } from 'antd';

interface Data {
  sendDataToParent: any
}

const Assembly: React.FC<Data> = ({ sendDataToParent }) => {
    const { transcript, setAssemblyTTS, handleAssemblyTTS } = useMiddleSocket();
    const [isRecording, setIsRecording] = useState(false);
    const audioContextRef = useRef<AudioContext | null>(null);
    const latest = JSON.parse(localStorage.getItem("userSession") || 'null');        
    const [isEditing, setIsEditing] = useState<boolean>(false); 
    const [editText, setEditText] = useState<string>(transcript.join(' ')); 
    console.log(isEditing)
    function handleClick(audio: any) {
      sendDataToParent(audio);
    }

    const startRecording = async () => {
      setAssemblyTTS([]); 

      audioContextRef.current = new AudioContext({ sampleRate: 16000 });
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const source = audioContextRef.current.createMediaStreamSource(stream);
      const processor = audioContextRef.current.createScriptProcessor(4096, 1, 1);
      let pcmDataBuffer: any[] = [];

      processor.onaudioprocess = (event) => {
        const inputBuffer = event.inputBuffer.getChannelData(0); // Mono channel
        const pcmData = new Int16Array(inputBuffer.length);

        for (let i = 0; i < inputBuffer.length; i++) {
          pcmData[i] = Math.max(-32768, Math.min(32767, inputBuffer[i] * 32767)); // Convert to PCM16
        }

        pcmDataBuffer.push(pcmData.buffer);
        const data = {
          latest: latest,
          audioblob: pcmData.buffer
        }
        handleAssemblyTTS(data)
      };

      source.connect(processor);
      processor.connect(audioContextRef.current.destination);

      setIsRecording(true);
    };

    const stopRecording = () => {
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      setIsRecording(false);
    };

    
    const handleEditClick = () => {
        setIsEditing(true);
        setEditText(transcript.join(' ')); 
    };

    const handleSave = () => {
        setAssemblyTTS(editText.split(' '));
        setIsEditing(false); 
    };

    const handleSubmit = () => {
      handleClick(transcript.join(' '))
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

        {transcript?.length !== 0 && (
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
                  {transcript.join(' ')}
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
  );
};

export default Assembly;
