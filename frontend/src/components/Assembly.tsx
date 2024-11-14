// import React, { useState, useRef } from "react";
// import useMiddleSocket from "../hooks/useMiddleSocket";

const Assembly: React.FC = () => {
  // const { transcript, handleAssemblyTTS } = useMiddleSocket();
  // const [isRecording, setIsRecording] = useState(false);
  // const audioContextRef = useRef<AudioContext | null>(null);
  // const latest = JSON.parse(localStorage.getItem("userSession") || 'null');

  // const startRecording = async () => {
  //   audioContextRef.current = new AudioContext({ sampleRate: 16000 });
  //   const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  //   const source = audioContextRef.current.createMediaStreamSource(stream);
  //   const processor = audioContextRef.current.createScriptProcessor(4096, 1, 1);
  //   let pcmDataBuffer: any[] = [];
  
  //   // const sendData = () => {
  //   //   if (pcmDataBuffer.length > 0) {
  //   //     const concatenatedData = pcmDataBuffer.reduce((acc, currentBuffer) => {
  //   //       const currentArray = new Uint8Array(acc.length + currentBuffer.byteLength);
  //   //       currentArray.set(acc);
  //   //       currentArray.set(new Uint8Array(currentBuffer), acc.length);
  //   //       return currentArray;
  //   //     }, new Uint8Array(0));

        
  //   //     const data = {
  //   //       latest: latest,
  //   //       audioblob: pcmDataBuffer[pcmDataBuffer.length - 3]
  //   //     };
  //   //     console.log('Ready to start over:', pcmDataBuffer);

  //   //     console.log('Sending audio data to AssemblyAI:', data?.audioblob);
  //   //     handleAssemblyTTS(data); 
  //   //     pcmDataBuffer = []; 
  //   //   }
  
  //   //   setTimeout(sendData, 5000);
  //   // };
  
  //   // sendData();
  
  //   processor.onaudioprocess = (event) => {
  //     const inputBuffer = event.inputBuffer.getChannelData(0); // Mono channel
  //     const pcmData = new Int16Array(inputBuffer.length);
  
  //     for (let i = 0; i < inputBuffer.length; i++) {
  //       pcmData[i] = Math.max(-32768, Math.min(32767, inputBuffer[i] * 32767)); // Convert to PCM16
  //     }

  //     pcmDataBuffer.push(pcmData.buffer);
  //     const data = {
  //       latest: latest,
  //       audioblob: pcmData.buffer
  //     }
  //     handleAssemblyTTS(data)
  //   };
  
  //   source.connect(processor);
  //   processor.connect(audioContextRef.current.destination);
  
  //   setIsRecording(true);
  // };
  
  // const stopRecording = () => {
  //   if (audioContextRef.current) {
  //     audioContextRef.current.close();
  //   }
  //   setIsRecording(false);
  // };

  return (
    <div>
      {/* <button onClick={startRecording} disabled={isRecording}>
        Start Recording
      </button>
      <button onClick={stopRecording} disabled={!isRecording}>
        Stop Recording
      </button>
      <div>
        <h2>Transcript:</h2>
        <p>{transcript}</p>
      </div> */}
    </div>
  );
};

export default Assembly;
