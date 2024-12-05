import { useState, useRef, useEffect } from 'react';
import { AudioOverallFeedbackModal, LoadingSpinner } from './index'
import { Card, Button, Spin, Collapse, Row, Col } from 'antd';

const { Panel } = Collapse;
import { OpenAI } from 'openai';
import WaveSurfer from 'wavesurfer.js';
import useMiddleSocket from '../hooks/useMiddleSocket';
import fade from '../assets/fade-circles.svg';
import '../styles/AudioRecorder/audiorecorder.css'
import Assembly from './Assembly';
import users from '../assets/mock-data/user_profiles.json';
import jobs from '../assets/mock-data/job_profile.json';
import { useParams } from 'react-router-dom';
import Api from '../Services/Services';

const apiKey = `${import.meta.env.VITE_REACT_APP_OPENAI_KEY}`;

const AudioSentence = () => {
    const { 
        handleAudioSentence, 
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
    const {userId, jobId} = useParams() 
    const latest = JSON.parse(localStorage.getItem("userSession") || 'null');        
    const [loadin, setLoad] = useState<any>(false);
    const [input, setInput] = useState<any>("");
    const [show, setShow] = useState<any>(true);
    const [counter, setCounter] = useState<any>(1);
    const [isOn, setOn] = useState(false);  
    const wavesurferRef = useRef<any>(null);
    const audioQueue = useRef<any>([]); 
    const isPlayingRef = useRef<any>(false); 
    const previousLengthRef = useRef<any>(0); 
    const [sessions, setSession] = useState<any>();
    const [startfetching, setStartFetch] = useState(true);
    const [open, setOpen] = useState<any>(false);
    let timerValue: any;

        // console.log("audio-chunks", audioChunk)
        console.log("audio-interview", audiointerview)

    const openai = new OpenAI({ apiKey, dangerouslyAllowBrowser: true });

 
        // console.log("audio-urls", audioUrls)
    console.log("sessions", isOn)

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
        const user_session = latest
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        pause();
        handleAudioSentence({ 
            input: input, 
            user_session: user_session,
            timerValue: timerValue
        });
        setCounter(counter < 9 ? counter + 1 : 1);
        setShow(false)
    }  

    const submitAudio = async(audioTranscript: any) => {;
        setAudioInterview([])
        setAudioInterviewChunk([])
        const user_session = latest
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        handleAudioSentence({ 
            input: audioTranscript, 
            user_session: user_session,
            timerValue: timerValue
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
        const delay = 6000;  
        const timer = setTimeout(() => {
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
        console.log("check this our", audiointerview.length > previousLengthRef.current)
        if (audiointerview.length > previousLengthRef.current) {
            const delay = setTimeout(() => {
                processNewChunks();
            }, 300); // 300ms debounce delay
    
            return () => clearTimeout(delay); 
        }
    }, [audiointerview]);
    
    const startSession = async() => {
        setOpen(false)
        setLoad(true)
        const filteredJob = jobs.filter(match => match.job_profile_id === parseInt(jobId as any));
        const filteredUser = users.filter(match => match?.user_profile_id === parseInt(userId as any));
        const data = {
            jobId: jobId,
            userId: userId,
            name: filteredUser[0]?.name,
            cvJson: filteredUser[0],
            jbJson: filteredJob[0]
        };
        const response = await Api.sessionCreate(data);
        localStorage.setItem("userSession", JSON.stringify(response?.data))
        setLoad(false)
        setOpen(true)
    }

    const fetchSession = async() =>{
        const latest = JSON.parse(localStorage.getItem("userSession") || 'null');        

        const data = {
            sessionId: latest?.id
        }
        const response = await Api.fetchSingleSession(data)
        console.log("session", response?.data)
        setSession(response?.data)
        setStartFetch(false);
    }

    useEffect(() => {
        if (startfetching) {
           fetchSession();
        }
    }, [startfetching == true]);

    return (
        <>
            <Button 
                style={{ 
                    margin:'1rem', 
                    textAlign:'center',  
                    color:'#ffffff', 
                    fontWeight: 'bolder', 
                    fontSize: '0.81rem'
                }}
                onClick={startSession}
                >
                    start new session
                    <span>
                        {loadin && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                    </span>
            </Button>
            
            {!open && (
                <Row gutter={16} style={{marginLeft: '6rem'}}>
                    <Col span={12}>
                        <Card title="Audio Interview" bordered={true}>
                            <div 
                                className='timer-container'
                                style={{ 
                                fontSize: '20px', 
                                display: 'flex', 
                                justifyContent:'space-between',
                                }}>
                                
                                {show && (
                                    <Button 
                                        type="primary"
                                        size="large"
                                        style={{ backgroundColor: '#f34e38', borderColor: '#f34e38' }}
                                        onClick={startInterview}
                                    >
                                        Start
                                    </Button>
                                )}

                                <div className='timer'>
                                    {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
                                </div>                    
                            </div>
                            
                            {(loading) && <Spin indicator={<img src={fade} alt="" className='h-10' />} />}

                            {audioHistory
                                ?.filter((item: any) => item?.user_type === 'assistant')
                                ?.slice(-1)
                                ?.map((message: any, index: any) => (
                                    <div className='audio-container' key={index}>
                                        {message?.content?.chunk_response !== "" && (
                                            <div className="chat-chunk-container">
                                                {message?.content?.time_limit !== "null" && (
                                                    <div>
                                                        time limit: {message?.content?.time_limit}
                                                    </div>
                                                )}
                                                {message?.content?.chunk_response?.map((msg: any, idx: any) => (
                                                    <p className="chat-chunk" key={idx}>
                                                        {msg}
                                                    </p>
                                                ))}
                                          
                                            </div>
                            )}

                            <div className='audio-container'>
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
                </div>
            ))}

                            <div>
                                <Assembly 
                                    sendDataToParent={handleDataFromAudio} 
                                /> 
                            </div>
                        </Card>
                    </Col>

                    {audioHistory?.length !== 0 && (
                        <Col span={10}>
                            <Card title="Real-Time Feedback" bordered={true}>
                                <Collapse accordion>
                                {audioHistory
                                    ?.filter((item: any) => item?.user_type === 'assistant') 
                                    ?.filter((item: any) => item?.content?.realtime_evaluation && item?.content?.realtime_evaluation !== 'null') 
                                    ?.map((item: any, index: any) => (
                                        <Panel 
                                        header={
                                            <strong>Interview Evaluation {index + 1}</strong>
                                        } 
                                        key={index}
                                        >
                                        {item?.content?.realtime_evaluation && (
                                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <div>
                                                    <p><strong>Overall Feedback:</strong> {item?.content?.realtime_evaluation?.overall?.feedback}</p>
                                                    {item?.content?.realtime_evaluation?.answer_relevancy?.length > 0 && (
                                                    <>
                                                        <p><strong>Answer Relevance:</strong> {item?.content?.realtime_evaluation?.answer_relevancy?.[0]?.level}%</p>                                                
                                                    </>
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                        </Panel>
                                    ))
                                    }
                                </Collapse>                      
                            </Card>

                            {sessions !== undefined && (
                                <div>
                                {sessions?.attributes?.i_persona_observer?.data !== null && (
                                    <span>
                                        {(() => {
                                            const item = sessions.attributes.i_persona_observer.data;
                                            return (
                                                <AudioOverallFeedbackModal
                                                    metricsData={item?.attributes?.attributes?.interview_evaluation_metrics}
                                                    evaluationData={item?.attributes?.attributes?.interview_evaluation} 
                                                />
                                            );
                                        })()}
                                    </span>
                                )}
                                </div>
                            )}
                        </Col>
                    )}
                </Row>
            )}
        </>

    );
};

export default AudioSentence;