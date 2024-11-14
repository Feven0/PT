import { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { OpenAI } from 'openai';
import Api from '../Services/Services';
const apiKey = `${import.meta.env.VITE_REACT_APP_OPENAI_KEY}`;
const openai = new OpenAI({ apiKey, dangerouslyAllowBrowser: true });

const AudioPlayer = () => {
    const [audioHistory, setAudioHistory] = useState<any>([]);
    const [audioUrl, setAudioUrl] = useState<any>(null);
    const wavesurferRef = useRef<any>(null);
    const wavesurferInstance = useRef<any>(null);
    // const audioContextRef = useRef(new (window.AudioContext || window.webkitAudioContext)());
    console.log(setAudioHistory, openai)
    // Set up WaveSurfer instance
    useEffect(() => {
        wavesurferInstance.current = WaveSurfer.create({
            container: wavesurferRef.current,
            //audioContext: audioContextRef.current,
            waveColor: '#6c63ff',
            progressColor: '#ff6f61',
            height: 128,
            //responsive: true,
        });

        // Cleanup on unmount
        return () => {
            wavesurferInstance.current.destroy();
        };
    }, []);

    const fetchAudio = async (inputText: any) => {
        const data = { text: inputText.toString() };
        try {
            // Set the response type to 'blob'
            const response = await Api.audio(data);
            console.log("idea", response)
            // Check if the response is OK
            // if (response.status !== 200) {
            //     throw new Error('Network response was not ok');
            // }
    
            // Get the Blob from the response
            const audioBlob = response.data;
            const blob = new Blob([audioBlob], { type : 'plain/text' });
            const blo = new Blob([await blob.arrayBuffer()], { type: 'audio/mpeg' });


            // Log the type and size of the audioBlob
            console.log("Received audioBlob:", typeof(blo));
            console.log("Type of audioBlob:", Object.prototype.toString.call(blo));
            console.log("Size of audioBlob:", blo.size); // Should be greater than 0
    
            // Create a URL for the audio Blob
            const url = URL.createObjectURL(blo);
            console.log("Generated Blob URL:", url);
    
            // Load the Blob URL into Wavesurfer
            wavesurferInstance.current.load(url);
            setAudioUrl(url); // Store the URL if needed
    
        } catch (error) {
            console.error('Error fetching audio:', error);
        }
    };

    const handlePlay = () => {
        if (wavesurferInstance.current) {
            wavesurferInstance.current.play();
        }
    };

    const handlePause = () => {
        if (wavesurferInstance.current) {
            wavesurferInstance.current.pause();
        }
    };

    return (
        <>
            <div>
                <button onClick={() => fetchAudio("Today is a wonderful day to build something people love!")}>
                    Fetch Audio
                </button>
                <div ref={wavesurferRef} style={{ width: '100%', height: '128px', marginTop: '20px' }} />
                <button onClick={handlePlay} disabled={!audioUrl}>
                    Play
                </button>blob
                <button onClick={handlePause} disabled={!audioUrl}>
                    Pause
                </button>

                <div className="chat-chunk-container">
                    {audioHistory.map((msg: any, index: any) => (
                        <p key={index} className="chat-chunk">{msg}</p>
                    ))}
                </div>
            </div>
        </>
    );
};

export default AudioPlayer;