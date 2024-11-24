import { useState, useRef, useEffect } from 'react';
import { Card, Spin } from 'antd';
import useMiddleSocket from '../hooks/useMiddleSocket';
import fade from '../assets/fade-circles.svg';
import '../styles/AudioRecorder/audiorecorder.css'
import Assembly from './Assembly';
import AudioPlayer from './AudioPlayer';


const Audio = () => {
        const { 
            handleAudioInterview, 
            loading, 
            audiointerview, 
            audioHistory, 
            seconds, 
            minutes, 
            pause, 
            setAudioInterview,
            audioChunk,
            setAudioInterviewChunk,
            done,
            chunk } = useMiddleSocket();

        const latest = JSON.parse(localStorage.getItem("userSession") || 'null');        
        const [input, setInput] = useState<any>("");
        const [show, setShow] = useState<any>(true);
        const [counter, setCounter] = useState<any>(1);
        const audioQueue = useRef<any>([]); 
        // const isPlayingRef = useRef<any>(false); 
        const previousLengthRef = useRef<any>(0); 
        let previous_question = "";
        let timerValue: any;

    const handleDataFromAudio = (audioTranscript: any) => {
        setInput(audioTranscript);
        if(audioTranscript !== undefined){  
            previousLengthRef.current = 0;
            audioQueue.current = []
            submitAudio(audioTranscript)
        }
    };

    const startInterview = async() => {
        if(audiointerview !== undefined){
            previous_question = audiointerview[0]?.content?.response?.question
        }
        const user_session = latest
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        pause();
        handleAudioInterview({ 
            input: input, 
            interview: audioHistory, 
            user_session: user_session,
            counter: counter,
            timerValue: timerValue,
            previous_question: previous_question
        });
        setCounter(counter < 9 ? counter + 1 : 1);
        setShow(false)
    }  

    const submitAudio = async(audioTranscript: any) => {;
        setAudioInterview([])
        setAudioInterviewChunk([])
        if(audiointerview !== undefined){
            previous_question = audiointerview[0]?.content?.response?.question
        }
        const user_session = latest
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        handleAudioInterview({ 
            input: audioTranscript, 
            interview: audioHistory, 
            user_session: user_session,
            counter: counter,
            timerValue: timerValue,
            previous_question: previous_question
        });
        setCounter(counter < 9 ? counter + 1 : 1);
    }

    useEffect(() => {
        const delay = 6000;  
        const timer = setTimeout(() => {
            // setIsVisible(true);  
        }, delay);

        return () => clearTimeout(timer);  
    }, [audioChunk]);
    

    // useEffect(() => {
    //     if (!wavesurferRef.current) {
    //         wavesurferRef.current = WaveSurfer.create({
    //             container: '#waveform', // Your container element
    //             waveColor: 'violet',
    //             progressColor: 'purple',
    //             // other options...
    //         });
    //     }
    
    //     // Clean up WaveSurfer instance on unmount
    //     return () => {
    //         if (wavesurferRef.current) {
    //             wavesurferRef.current.destroy();
    //             wavesurferRef.current = null;
    //         }
    //     };
    // }, []);

    // // Load the audio URL into WaveSurfer when `aud` changes
    // useEffect(() => {
    //     if (aud && wavesurferRef.current) {
    //         wavesurferRef.current.load(aud); // Load the audio URL into WaveSurfer

    //         // Optional: Play the audio when it's ready
    //         wavesurferRef.current.once('ready', () => {
    //             wavesurferRef.current.play();
    //         });
    //     }
    // }, [aud]); // Trigger this effect when `aud` changes

    // // API call to fetch the synthesized audio
    // const Api = {
    //     textToSpeech: async () => {
    //         return axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/synthesize`, {}, {
    //             responseType: 'blob',  // Expecting binary data (Blob)
    //         });/tts
    //     },
    // };

    // // Function to synthesize audio
    // const synthesizeAudio = async () => {
    //     try {
    //         setLoading(true);
    
    //         const response = await Api.textToSpeech();  // Call the FastAPI backend
    
    //         if (response && response.data) {
    //             const blob = response.data;
    //             console.log("Blob size:", blob.size); // Log the blob size
    //             if (blob.size === 0) {
    //                 console.error('Received an empty audio file.');
    //                 return;
    //             }
    
    //             const audioBlob = new Blob([await blob.arrayBuffer()], { type: 'audio/mpeg' });
    //             const url = URL.createObjectURL(audioBlob);
    //             setAudd(url);  // Set the audio URL in state
    //         } else {
    //             console.error('Error:', response.data.error);
    //         }
    
    //         setLoading(false);
    //     } catch (error) {
    //         console.error('Error generating audio:', error);
    //         setLoading(false);
    //     }
    // };
    

    // const synthesizeAudio = async () => {
    //     // console.log('New chunks for synthesis:', newChunks);
    //     const newChunks = ['I can dance, but she can code', 'can', 'dance', ',', 'she', 'does', 'coding']
    //     try {
    //         setLoading(true);
    
    //         // for (const sentence of newChunks) {
    //         console.log("entry", "sentence")
    //         const mp3 = await openai.audio.speech.create({
    //             model: "tts-1",
    //             voice: "nova",
    //             input: "sentence",
    //         });
            
    //         const audioBlob = new Blob([await mp3.arrayBuffer()], { type: 'audio/mpeg' });
    //         const url = URL.createObjectURL(audioBlob);
    //         console.log("cardi", url)
    //         setAudd(url)
    //         audioQueue.current.push(url);    
             
    //         // }
    //            if (!isPlayingRef.current) {
    //                 playNextAudio(); 
    //             }
    
    //         setLoading(false);
    //     } catch (error) {
    //         console.error('Error generating audio:', error);
    //         setLoading(false);
    //     }
    // };
    
    // const synthesizeAudio = async (newc: any) => {
    //     try {
    //         setLoading(true);
    
    //         if (newc.length > 0) {
    //             newc.forEach((chunkUrl: any) => {
    //                 audioQueue.current.push(chunkUrl);  
    //             });
    
    //             if (!isPlayingRef.current) {
    //                 playNextAudio(); 
    //             }
    //         } else {
    //             console.error('No audio interview chunks available');
    //         }
    
    //         setLoading(false);
    //     } catch (error) {
    //         console.error('Error processing audio:', error);
    //         setLoading(false);
    //     }
    // };

    
    return (
        <>
        <div>
            <p>Response comes in a chunk per socket emit</p>

        </div>
        <div style={{display: 'flex', gap: '15rem', margin: '0rem 5rem 0rem 29rem'}}>
            <div style={{ width: '600px' }}>
                <Card title="Audio Interview" bordered={true}>                    
                    <div 
                        className='timer-container'
                        style={{ 
                        fontSize: '20px', 
                        display: 'flex', 
                        justifyContent:'space-between',
                        }}>
                        
                        {show && (<div>
                            <button 
                                style={{
                                    fontSize:'1rem',
                                    backgroundColor: '#f34e38', 
                                    border: 'none', 
                                    padding:'0.7rem', 
                                    borderRadius: '0.6rem', 
                                    cursor: 'pointer', 
                                    width: '8rem'}} 
                                    // onClick={synthesizeAudio}
                                    onClick={startInterview}
                                >
                                start
                            </button>
                        </div>)}
                        <div className='timer'>
                            {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
                        </div>                    
                    </div>
                    
                    {(loading) && <Spin indicator={<img src={fade} alt="" className='h-10' />} />}
                    
                    <div className='audio-container'>    
                        {chunk && (              
                            <div className="chat-chunk-container">                            
                                {audioChunk?.map((item: any, index: any) => (
                                    <p className="chat-chunk" key={index}>
                                        {item}
                                    </p> 
                                ))}
                            </div> 
                            
                        )}

                        {done && (
                        <AudioPlayer
                         audiointerview={audiointerview}/>)}
                    </div>    

                    <div>
                        <Assembly
                            sendDataToParent={handleDataFromAudio} 
                        /> 
                    </div>
                </Card>
            </div>
        </div>            
        </>
    );
};

export default Audio;