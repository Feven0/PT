import { useState, useRef, useEffect } from 'react';
import { Typography, Card, message, Spin, Collapse } from 'antd';
import { OpenAI } from 'openai';
import WaveSurfer from 'wavesurfer.js';
import { AudioChatRecord, OverallFeedbackModal } from './index';
import useMiddleSocket from '../hooks/useMiddleSocket';
import fade from '../assets/fade-circles.svg';
import '../styles/AudioRecorder/audiorecorder.css'
const { Panel } = Collapse;

const { Title } = Typography;
const apiKey = `${import.meta.env.VITE_REACT_APP_OPENAI_KEY}`;

const Audio = () => {
        const { handleAudioInterview, loading, audiointerview, audioHistory, seconds, minutes, pause, reset, setLoading, setAudioInterview } = useMiddleSocket();
        // const {userId, jobId} = useParams()
        // const userId = 16
        // const jobId = 1045
        const latest = JSON.parse(localStorage.getItem("userSession"));
        const [audioUrl, setAudioUrl] = useState(null);
        const [audioUrls, setAudioUrls] = useState([]); 

        const [dataFromAudio, setDataFromAudio] = useState<any>(false);
        const [input, setInput] = useState<any>("");
        const [show, setShow] = useState<any>(true);
        const [counter, setCounter] = useState<any>(1);
        const [buffer, setBuffer] = useState('');

        const wavesurferRef = useRef(null);
        const openai = new OpenAI({ apiKey, dangerouslyAllowBrowser: true });

 
        console.log("audioooo caroline", audiointerview)
        console.log("audiohistory", audioHistory)

        let previous_question = "";
        let timerValue: any;

    const handleDataFromAudio = (audioTranscript: any) => {
        setInput(audioTranscript);
        console.log("transcription org.", audioTranscript)
        if(audioTranscript !== undefined){
            submitAudio(audioTranscript)
        }
    };

    function handleDataAudio(data: any) {
        setDataFromAudio(data);
    }

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
        const playAudioSequentially = async () => {
            if (audioUrls.length > 0) {
                for (const url of audioUrls) {
                    await new Promise((resolve) => {
                        wavesurferRef.current.load(url);
                        wavesurferRef.current.on('ready', () => {
                            wavesurferRef.current.play();
                        });
                        wavesurferRef.current.on('finish', () => {
                            resolve(); 
                        });
                    });
                }
                setAudioUrls([]);
            }
        };
        
        playAudioSequentially();
    }, [audioUrls]);

    const synthesizeAudio = async () => {
        const sentences = audiointerview
        try {
            setLoading(true); 
            const urls = [];
            
            for (const sentence of sentences) {
                console.log("AUDIO ENTRY", sentence)

                const mp3 = await openai.audio.speech.create({
                    model: "tts-1-hd",
                    voice: "nova",
                    input: sentence,
                });

                const audioBlob = new Blob([await mp3.arrayBuffer()], { type: 'audio/mpeg' });
                
                const url = URL.createObjectURL(audioBlob);
                
                urls.push(url); 
                setAudioUrls(urls); 
            }
            setLoading(false);
        } catch (error) {
            console.error("Error generating audio:", error);
            setLoading(false); 
        }
    };

    useEffect(() => {
        const processChunks = async () => {           
            // for (const chunk of audioHistory) {
            //     console.log("audiochunk", chunk); 
            //     await synthesizeAudio(); 
            // }
            await synthesizeAudio();
        };

        if (audiointerview.length > 0) {
            processChunks(); 
        }
    }, [audiointerview]); 


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
        wavesurferRef.current = WaveSurfer.create({
            container: '#waveform',
            audioContext: new (window.AudioContext || window.webkitAudioContext)(),
            waveColor: '#6c63ff',
            progressColor: '#ff6f61',
            height: 128,
            responsive: true,
        });

        return () => {
            wavesurferRef.current.destroy();
        };
    }, []);




    // const synthesizeAudio = async () => {
    //     const text = 'I have work at the station near the line street around New York. The station was dirty but wide enough to handle too many passengers.';
    //     const sentences = text.split('.').map(sentence => sentence.trim()).filter(sentence => sentence);
    //     // const sentences = ["I have work at the station near", "the line street around New York", "The station was dirty but wide", "enough to handle too many passengers"]
    //     for (const sentence of sentences) {
    //         const mp3 = await openai.audio.speech.create({
    //             model: "tts-1-hd",
    //             voice: "nova",
    //             input: sentence,
    //         });
    
    //         const audioBlob = new Blob([await mp3.arrayBuffer()], { type: 'audio/mpeg' });
    //         const url = URL.createObjectURL(audioBlob);
    //         console.log("alright", url)
    //         try {
    //             const arrayBuffer = await fetch(url).then(response => {
    //                 if (!response.ok) {
    //                     throw new Error('Network response was not ok');
    //                 }
    //                 return response.arrayBuffer();
    //             });
    //             const audioBuffer = await audioContextRef.current.decodeAudioData(arrayBuffer);
    
    //             // Update audio history
    //             setAudioHistory(prev => [...prev, sentence]);
    
    //             // Add the audio buffer and URL to the queue
    //             audioQueue.current.push({ buffer: audioBuffer, url });
    
    //             // Start playback if not already playing
    //             playNext();
    //         } catch (error) {
    //             console.error('Failed to fetch audio data:', error);
    //         } finally {
    //             // Clean up the URL after use
    //             URL.revokeObjectURL(url);
    //         }
    //     }
    // };



    return (
        <>
        <div style={{display: 'flex', gap: '15rem', margin: '0rem 5rem 0rem 10rem'}}>
            <div style={{ width: '600px' }}>
                <Card title="Audio Interview" bordered={true} >
                    <div style={{ 
                        fontSize: '20px', 
                        display: 'flex', 
                        justifyContent:'space-between',
                        // textAlign: 'end'
                        }}>
                        
                        {show && (<div>
                            <button style={{fontSize:'1rem',backgroundColor: '#f34e38', border: 'none', padding:'0.7rem', borderRadius: '0.6rem', cursor: 'pointer', width: '8rem'}} onClick={startInterview}>
                                start
                            </button>
                        </div>)}
                        <div>{String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}</div>                    
                    </div>
                    
                    {(loading || dataFromAudio) && <Spin indicator={<img src={fade} alt="" className='h-10' />} />}

                    <div 
                        id="waveform" 
                        style={{ width: '100%', height: '128px', marginTop: '20px' }} 
                        onClick={handleWaveformClick}
                    >
                        
                    </div>

                    <div>
                        <AudioChatRecord sendDataParent={handleDataAudio} sendDataToParent={handleDataFromAudio} pause={pause}/>
                    </div>
                </Card>
            </div>
            
            <div style={{display:'flex', flexDirection: 'column'}}>
                {(audiointerview !== undefined && !loading && audiointerview[0]?.content?.realtime_evaluation !== "null") &&(
                    <div style={{width: '28rem', bottom: '0', marginBottom: '0'}}>
                        <div style={{
                        textAlign: 'justify', 
                        width: '30rem',
                        padding: '1.5rem',
                        borderRadius: '1rem',
                        color: '#333',
                        backgroundColor: '#f9f9f9', 
                        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)', 
                    }}>
                        <Collapse defaultActiveKey={['1']} style={{ marginTop: '1rem' }}>
                            <Panel 
                                header="Feedback" 
                                key="1" 
                                style={{ backgroundColor: '#f3f5f7', border: 'none', borderRadius: '1rem' }} 
                            >
                                <div className='message-text' style={{ padding: '1rem', color: '#6b6666', lineHeight: '1.5rem' }}>{audiointerview[0]?.content?.realtime_evaluation?.overall?.feedback}</div>
                            </Panel>
                            <Panel 
                                header="Other Metrics" 
                                key="2" 
                                style={{ backgroundColor: '#f3f5f7', border: 'none', borderRadius: '1rem' }}
                            >
                                <div style={{ padding: '1rem' }}>
                                    {audiointerview[0]?.content?.realtime_evaluation?.communication_skills?.map((skill, index) => (
                                        <div key={index} style={{ marginBottom: '0.5rem' }}>
                                            <strong style={{ fontSize: '1.1rem' }}>
                                                {skill?.skill}: 
                                            </strong>
                                            <span style={{ marginLeft: '0.5rem', color: '#555' }}>{skill?.level}</span>
                                        </div>
                                    ))}
                                </div>
                            </Panel>
                        </Collapse>
                    </div>
                    </div>
                )}

                {(audiointerview !== undefined && !loading && audiointerview[0]?.content?.interview_evaluation !== "null") &&(
                    <div style={{marginTop: '1.8rem'}}>
                        <OverallFeedbackModal
                            metricsData={audiointerview[0]?.content?.interview_evaluation_metrics}
                            evaluationData={audiointerview[0]?.content?.interview_evaluation} 
                        />
                    </div>
                )}
            </div>
        </div>
            
        </>
    );
};

export default Audio;