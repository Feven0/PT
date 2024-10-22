
const apiKey = `${import.meta.env.VITE_REACT_APP_OPENAI_KEY}`; 
import { useState, useRef, useEffect } from 'react';
import { OpenAI } from 'openai'; 
import WaveSurfer from 'wavesurfer.js';

const Audio = () => {
        const [userInput, setUserInput] = useState("");
        const [audioUrl, setAudioUrl] = useState(null);
        const wavesurferRef = useRef(null);
        const openai = new OpenAI({ apiKey, dangerouslyAllowBrowser: true });
    
        const handleInputChange = (e) => {
            setUserInput(e.target.value); // Update user input
        };
    
        const handleSubmit = async (e) => {
            e.preventDefault(); // Prevent form submission
            if (!userInput) return; // Do nothing if input is empty
    
            // Synthesize audio for user input
            await synthesizeAudio(userInput);
            setUserInput(""); // Clear input after submission
        };
    
        const synthesizeAudio = async (text) => {
            try {
                const mp3 = await openai.audio.speech.create({
                    model: "tts-1-hd",
                    voice: "alloy",
                    input: text,
                });
    
                // Create a blob from the response
                const audioBlob = new Blob([await mp3.arrayBuffer()], { type: 'audio/mpeg' });
                const url = URL.createObjectURL(audioBlob);
                
                // Revoke the previous audio URL to free up memory
                if (audioUrl) {
                    URL.revokeObjectURL(audioUrl);
                }
    
                setAudioUrl(url); // Set the new audio URL
            } catch (error) {
                console.error("Error generating audio:", error);
            }
        };
    
        useEffect(() => {
            // Initialize WaveSurfer
            wavesurferRef.current = WaveSurfer.create({
                container: '#waveform',
                audioContext: new (window.AudioContext || window.webkitAudioContext)(),
                waveColor: 'purple',
                progressColor: 'orange',
                height: 128,
                responsive: true,
            });
    
            // Load the audio URL into WaveSurfer
            if (audioUrl) {
                wavesurferRef.current.load(audioUrl);
                wavesurferRef.current.on('ready', () => {
                    // Optionally start playing automatically when ready
                });
            }
    
            return () => {
                wavesurferRef.current.destroy(); // Cleanup on unmount
            };
        }, [audioUrl]);
    
        // Handle click on the waveform
        const handleWaveformClick = (e) => {
            const waveformWidth = e.currentTarget.clientWidth; // Get the width of the waveform container
            const clickPosition = e.clientX - e.currentTarget.getBoundingClientRect().left; // Get click position relative to the container
            const seekTo = clickPosition / waveformWidth; // Calculate the seek position as a fraction of the total width
    
            if (wavesurferRef.current) {
                wavesurferRef.current.seekTo(seekTo); // Seek to the clicked position
                wavesurferRef.current.play(); // Play from the clicked position
            }
        };
    
        return (
            <div>
                <h1>Audio Chat</h1>
                <form onSubmit={handleSubmit}>
                    <input 
                        type="text" 
                        value={userInput} 
                        onChange={handleInputChange} 
                        placeholder="Ask something..." 
                    />
                    <button type="submit">Send</button>
                </form>
                <div 
                    id="waveform" 
                    style={{ width: '100%', height: '128px' }} 
                    onClick={handleWaveformClick}
                ></div>
            </div>
        );
};

export default Audio;