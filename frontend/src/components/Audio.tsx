import { useState, useRef, useEffect } from 'react';
import { LoadingSpinner } from './index'
import { Card, Button, Spin, Collapse, Row, Col } from 'antd';
const { Panel } = Collapse;
import WaveSurfer from 'wavesurfer.js';
import useMiddleSocket from '../hooks/useMiddleSocket';
import fade from '../assets/fade-circles.svg';
import '../styles/AudioRecorder/audiorecorder.css'
import Assembly from './Assembly';
import Api from '../Services/Services';


const Audio = () => {
    const { 
        handleAudioSentence,
        handleTemplateAudioInterview,
        handleChallengeAudioInterview,
        loading, 
        audiointerview, 
        audioHistory, 
        startchat,
        seconds, 
        minutes, 
        setLoading, 
        setAudioInterview} = useMiddleSocket();
    const latest = JSON.parse(localStorage.getItem("userSession") || 'null');        
    const [input, setInput] = useState<any>("");
    const wavesurferRef = useRef<any>(null);
    const audioQueue = useRef<any>([]); 
    const isPlayingRef = useRef<any>(false); 
    const previousLengthRef = useRef<any>(0); 
    const [_sessions, setSession] = useState<any>();
    const [startfetching, setStartFetch] = useState(true);
    let timerValue: any;

    console.log("audio-interview", audiointerview)
    console.log("audio-history", audioHistory)
    
    const chooseTemplate = async (_id: any) => {
        const data = {
            job_profile_id: 46,
            all_user_id: 1959,
            template: true,
            generate: false,
            external: false,
            challenge: false,
            template_id: 50, 
            challenge_id: 0
        };
        const response = await Api.sessionCreate(data);
        console.log("response", response?.data)
        localStorage.setItem("userSession", JSON.stringify(response?.data))
        if(response?.data){  
            timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            handleTemplateAudioInterview({ 
                input, 
                user_session: response?.data,
                template_id: 50,
                challenge_id: 0,
                job_profile_id: 46,
                timerValue,
                all_user_id: 1959
            });
        }
        setInput('');

    }

    const chooseChallenge = async(_id: any) => {
        const data = {
            job_profile_id: 0,
            all_user_id: 1959,
            template: false,
            generate: false,
            external: false,
            challenge: true,
            template_id: 0, 
            challenge_id: 26
        };

        const response = await Api.sessionCreate(data);
        localStorage.setItem("userSession", JSON.stringify(response?.data))
        if(response?.data){  
            timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            handleChallengeAudioInterview({ 
                input, 
                user_session: response?.data,
                challenge_id: 26,
                timerValue,
                job_profile_id: 0,
                all_user_id: 1959
            });
        }
        setInput('');
    }

        
    const [template_id, _setTemplateId] = useState<number>(50);
    const [challenge_id, _setChallengId] = useState<number>(0);
    const [job_profile_id, _setJobProfileId] = useState<number>(46); 

    const ExecuteInterview = (audioTranscript: any) => {
        setAudioInterview([])

        const temp_id = template_id || latest?.template_id || 0;
        const cha_id = challenge_id || latest?.challenge_id || 0;
        const job_id = job_profile_id || latest?.job_profile_id || 0;

        const isTempValid = temp_id > 0;
        const isChallengeValid = cha_id > 0;
        const isJobProfileValid = job_id > 0;

        if (isTempValid && isChallengeValid) {
            console.log("🎯 Executing Template with Challenge");
            ExecutiveTemplate(temp_id, job_id, cha_id, audioTranscript);
        } 
        else if (isTempValid && isJobProfileValid) {
            console.log("📄 Executing Template with Job Profile");
            ExecutiveTemplate(temp_id, job_id, cha_id, audioTranscript);
        }
        else if (!isTempValid && isChallengeValid) {
            console.log("🔥 Executing Challenge");
            ExecutiveChallenge(cha_id, audioTranscript);
        } 
        else if (!isTempValid && !isChallengeValid && isJobProfileValid) {
            console.log("🛠️ Generating Interview with Job Profile");
            ExecuteAudioInterview(audioTranscript);
        } 
        else {
            console.warn("⚠️ Invalid configuration: No valid identifiers provided");
        }
    };

    const ExecutiveTemplate = async (temp_id: any, job_id: any, cha_id: any, audioTranscript:any) => {
        setAudioInterview([])
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        const user_session = latest;    
        console.log("*)9-0TYIGHVYONHUPIONUMKJNUONUIH", user_session)
        handleTemplateAudioInterview({ 
            input: audioTranscript, 
            user_session: user_session,
            template_id: temp_id,
            challenge_id: cha_id,
            job_profile_id: job_id,
            timerValue,
            all_user_id: 1959
        });
        setInput('');
    }

    const ExecutiveChallenge = async (_id: any, audioTranscript:any) => {
        setAudioInterview([])
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        const user_session = latest;   
        console.log("USER RESPONSE ************** USER RESPONSE", input) 
        handleChallengeAudioInterview({ 
            input: audioTranscript, 
            user_session: user_session,
            challenge_id: 26,
            timerValue,
            job_profile_id: 0,
            all_user_id: 1959
        });
        setInput('');
    }

    const handleDataFromAudio = (audioTranscript: any) => {
        setInput(audioTranscript);
        if(audioTranscript !== undefined){  
            previousLengthRef.current = 0;
            audioQueue.current = []
            ExecuteInterview(audioTranscript)
        }
    };
    
    const startSession = async() => {
        setLoading(true)
        const data = {
            job_profile_id: 232,
            all_user_id: 1920,
            template: false,
            generate: true,
            external: false,
            challenge: false,
            template_id: 0, 
            challenge_id: 0
        };
        const response = await Api.sessionCreate(data);
        localStorage.setItem("userSession", JSON.stringify(response?.data))
        if(response?.data){  
            timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            handleAudioSentence({ 
                input, 
                user_session: response?.data,
                timerValue,
                job_profile_id: 232,
                all_user_id: 1920
            });
            setInput('');
            setLoading(false)
        }
        
    }

    const ExecuteAudioInterview = (audioTranscript: any) => {
        setAudioInterview([])
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        const user_session = latest;
        handleAudioSentence({ 
            input: audioTranscript, 
            user_session,
            timerValue,
            job_profile_id: 46,
            all_user_id: 1959
        });
        setInput('');
    };

    const handleWaveformClick = (e: any) => {
        const waveformWidth = e.currentTarget.clientWidth;
        const clickPosition = e.clientX - e.currentTarget.getBoundingClientRect().left;
        const seekTo = clickPosition / waveformWidth;
    
        if (wavesurferRef.current) {
          wavesurferRef.current.seekTo(seekTo);
          wavesurferRef.current.play();
        }
      };
    
    const waveformContainerRef = useRef<HTMLDivElement | null>(null);
    
    useEffect(() => {
        if (!waveformContainerRef.current) return;

        wavesurferRef.current = WaveSurfer.create({
            container: waveformContainerRef.current,
            waveColor: '#080808',
            progressColor: '#f50202',
            height: 38
        });

        wavesurferRef.current.on('finish', () => {
            if (audioQueue.current.length > 0 && !isPlayingRef.current) {
                playNextAudio();
            }
        });

        return () => {
            if (wavesurferRef.current) {
                wavesurferRef.current.destroy();
                wavesurferRef.current = null;
            }
        };
    }, [startchat]);


      const playNextAudio = async () => {
        if (audioQueue.current.length > 0 && !isPlayingRef.current) {
            const nextUrl = audioQueue.current.shift(); 
            isPlayingRef.current = true;  

            if (wavesurferRef.current) {
                wavesurferRef.current.load(nextUrl); 

                wavesurferRef.current.once('ready', () => {
                    wavesurferRef.current.play();  
                });

                wavesurferRef.current.once('finish', () => {
                    isPlayingRef.current = false; 
                    if (audioQueue.current.length > 0) {
                        playNextAudio();  
                    }
                });
            } else {
                console.error("WaveSurfer instance is not initialized.");
            }
        }
    };

    const synthesizeAudio = async (newChunks: any) => {
        try {
            if (newChunks.length > 0) {
                const concatenatedBlob = await concatenateChunks(newChunks);  
                const url = URL.createObjectURL(concatenatedBlob);
                audioQueue.current.push(url);  

                if (!isPlayingRef.current) {
                    playNextAudio();  
                }
            } else {
                console.error('No audio interview chunks available');
            }
        } catch (error) {
            console.error('Error processing audio:', error);
        }
    };

    const concatenateChunks = async (chunks: any) => {
        const arrays = await Promise.all(chunks.map(async (chunkUrl: any) => {
            const response = await fetch(chunkUrl);
            const arrayBuffer = await response.arrayBuffer();
            return new Uint8Array(arrayBuffer);
        }));

        const totalLength = arrays.reduce((sum, arr) => sum + arr.length, 0);
        const concatenated = new Uint8Array(totalLength);

        let offset = 0;
        arrays.forEach(arr => {
            concatenated.set(arr, offset);
            offset += arr.length;
        });

        return new Blob([concatenated], { type: 'audio/mpeg' });
    };

    const processNewChunks = async () => {
        console.log("let me see", audiointerview)
        const newChunks = audiointerview.slice(previousLengthRef.current);  
        console.log("break it off with  her", newChunks)
        if (newChunks.length > 0) {
            await synthesizeAudio(newChunks);
            previousLengthRef.current = audiointerview.length;  
            setLoading(false)  
        }
    };

    useEffect(() => {
        if (audiointerview.length > previousLengthRef.current) {
            setLoading(true)
            processNewChunks();  
        }
    }, [audiointerview]);

    const fetchSession = async() =>{
        const latest = JSON.parse(localStorage.getItem("userSession") || 'null');        
        console.log("session", latest)
        console.log("everyonetooo", `${import.meta.env.VITE_REACT_APP_BACKEND_URL}`)

        const data = {
            sessionId: latest?.id
        }
        const response = await Api.fetchSingleSession(data)
        // check the storage session match with the new session id
        console.log("session", latest)
        setSession(response?.data)
        setStartFetch(true);
    }

    useEffect(() => {
        if (startfetching) {
           fetchSession();
        }
    }, [startfetching == true]);

    return (
        <>            
            {/* {!open && ( */}
                <Row gutter={16} style={{marginLeft: '6rem'}}>
                {/* {(!startchat) && ( */}
                    <Col span={12}>
                        <Card title="Audio Interview" bordered={true}>
                            <div>
                                <Button onClick={chooseTemplate}>Template</Button>
                                <Button onClick={chooseChallenge}>Challenge</Button>
                            </div>
                            <div 
                                className='timer-container'
                                style={{ 
                                fontSize: '20px', 
                                display: 'flex', 
                                justifyContent:'space-between',
                                }}>
                                
                                <Button 
                                    type="primary"
                                    size="large"
                                    style={{ backgroundColor: '#f34e38', borderColor: '#f34e38' }}
                                    onClick={startSession}
                                >
                                    Start
                                </Button>

                                <div className='timer'>
                                    {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
                                </div>                    
                            </div>

                            {loading && <Spin indicator={<img src={fade} alt="" className='actions-load' />} />}

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
                                </div>
                            ))}

                            <div className='audio-container'>
                                {/* {isOn && ( */}
                                {loading && <LoadingSpinner style={{ marginLeft: '5px' }} />}

                                    {/* <div 
                                        id="waveform" 
                                        style={{ 
                                            width: '50%', 
                                            height: '20px', 
                                            marginTop: '0px', 
                                            marginBottom: '10px' 
                                        }} 
                                        className='waveform'
                                        onClick={handleWaveformClick}
                                    >                        
                                    </div>    */}
                                    <div
                                        ref={waveformContainerRef}
                                        style={{
                                            width: '50%',
                                            height: '20px',
                                            marginTop: '0px',
                                            marginBottom: '10px'
                                        }}
                                        className='waveform'
                                        onClick={handleWaveformClick}
                                    />
                                {/* )}  */}
                            </div>
                            
                            <div>
                                <Assembly 
                                    sendDataToParent={handleDataFromAudio} 
                                /> 
                            </div>
                        </Card>
                    </Col>
                 {/* )} */}
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
                                    ))}
                                </Collapse>                      
                            </Card>

                            {/* {sessions !== undefined && (
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
                            )} */}
                        </Col>
                    )}
                </Row>
            {/* )} */}
        </>

    );
};

export default Audio;