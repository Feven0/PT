import { useState, useRef, useEffect } from 'react';
import { Card, Spin } from 'antd';
import { OpenAI } from 'openai';
import WaveSurfer from 'wavesurfer.js';
import useMiddleSocket from '../hooks/useMiddleSocket';
import fade from '../assets/fade-circles.svg';
import '../styles/AudioRecorder/audiorecorder.css'
import Assembly from './Assembly';

const apiKey = `${import.meta.env.VITE_REACT_APP_OPENAI_KEY}`;

const Audio2Chunk = () => {
        const { 
            handleAudioDouble, 
            loading, 
            audiointerview, 
            audioHistory, 
            seconds, 
            minutes, 
            pause, 
            setLoading, 
            setAudioInterview,
            audioChunk,
            setAudioInterviewChunk } = useMiddleSocket();
        const latest = JSON.parse(localStorage.getItem("userSession") || 'null');        
        const [input, setInput] = useState<any>("");
        const [show, setShow] = useState<any>(true);
        const [counter, setCounter] = useState<any>(1);
        const [isVisible, setIsVisible] = useState(false);  
        const wavesurferRef = useRef<any>(null);
        const [isOn, setOn] = useState(false);  
        const audioQueue = useRef<any>([]); 
        const isPlayingRef = useRef<any>(false); 
        const previousLengthRef = useRef<any>(0); 

        // console.log("audiointerview", audiointerview)
        // console.log("mother", audioQueue)

        const openai = new OpenAI({ apiKey, dangerouslyAllowBrowser: true });

 
        // console.log("audioooo caroline", audioUrls)
        // console.log("audiohistory", audioHistory)

        let previous_question = "";
        let timerValue: any;

    const handleDataFromAudio = (audioTranscript: any) => {
        setInput(audioTranscript);
        if(audioTranscript !== undefined){  
            previousLengthRef.current = 0;
            audioQueue.current = []
            setOn(false)
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
        handleAudioDouble({ 
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
        handleAudioDouble({ 
            input: audioTranscript, 
            interview: audioHistory, 
            user_session: user_session,
            counter: counter,
            timerValue: timerValue,
            previous_question: previous_question
        });
        setCounter(counter < 9 ? counter + 1 : 1);
    }


    const handleWaveformClick = (e: any) => {
        const waveformWidth = e.currentTarget.clientWidth;
        const clickPosition = e.clientX - e.currentTarget.getBoundingClientRect().left;
        const seekTo = clickPosition / waveformWidth;
    
        if (wavesurferRef.current) {
          wavesurferRef.current.seekTo(seekTo);
          wavesurferRef.current.play();
        }
      };
    
      useEffect(() => {
        if (isOn && !wavesurferRef.current) {
          wavesurferRef.current = WaveSurfer.create({
            container: '#waveform',
            waveColor: '#080808',
            progressColor: '#f50202',
            height: 38,
          });
        }
    
        return () => {
          if (wavesurferRef.current) {
            wavesurferRef.current.destroy();
            wavesurferRef.current = null;
          }
        };
      }, [isOn]); 

    useEffect(() => {
        const delay = 7000;  
        const timer = setTimeout(() => {
            setIsVisible(true);  
        }, delay);

        return () => clearTimeout(timer);  
    }, [audioChunk]);

    
    const playNextAudio = async () => {
        if (audioQueue.current.length > 0 && !isPlayingRef.current) {
            const nextUrl = audioQueue.current[0];
            isPlayingRef.current = true;
    
            wavesurferRef.current.load(nextUrl);
            wavesurferRef.current.once('ready', () => {
                wavesurferRef.current.play();
            });
    
            wavesurferRef.current.once('finish', async () => {
                audioQueue.current.shift();
                isPlayingRef.current = false;
    
                await new Promise(resolve => setTimeout(resolve, 500));  
                if (audioQueue.current.length > 0) {
                    playNextAudio();
                }
            });
        }
    };   
    
    const synthesizeAudio = async (newChunks: any) => {
        console.log('New chunks for synthesis:', newChunks);
    
        try {
            setLoading(true);
    
            for (const sentence of newChunks) {
                const mp3 = await openai.audio.speech.create({
                    model: "tts-1",
                    voice: "nova",
                    input: sentence,
                });
    
                const audioBlob = new Blob([await mp3.arrayBuffer()], { type: 'audio/mpeg' });
                const url = URL.createObjectURL(audioBlob);
    
                audioQueue.current.push(url);
    
                if (!isPlayingRef.current) {
                    playNextAudio(); 
                }
            }
    
            setLoading(false);
        } catch (error) {
            console.error('Error generating audio:', error);
            setLoading(false);
        }
    };

    const processNewChunks = async () => {
        const newChunks = audiointerview.slice(previousLengthRef.current);
    
        if (newChunks.length > 0) {
            console.log('New Chunks:', newChunks);   
            setOn(true) 
            await synthesizeAudio(newChunks);    
            previousLengthRef.current = audiointerview.length;
        }
    };

    useEffect(() => {
        if (audiointerview.length > previousLengthRef.current) {
            const delay = setTimeout(() => {
                processNewChunks();
            }, 300); 
    
            return () => clearTimeout(delay); 
        }
    }, [audiointerview]);
        

    
    return (
        <>
        <div>
            <p>Displaying two set of chunks(10 token per chunk)</p>
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
                        {isVisible && (
                            <div className="chat-chunk-container">                            
                                {audioChunk.map((item: any, index: any) => (
                                    <p className="chat-chunk" key={index}>
                                        {item}
                                    </p> 
                                ))}
                            </div> 
                        )} 

                        {isOn && (
                            <div 
                                id="waveform" 
                                style={{ width: '50%', height: '20px', marginTop: '0px', marginBottom: '10px' }} 
                                className='waveform'
                                onClick={handleWaveformClick}
                            >                        
                            </div>   
                        )} 
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

export default Audio2Chunk;