import { useState, useEffect } from 'react';
import { Card, Input, Button, Spin } from 'antd';
import fade from '../assets/fade-circles.svg';
import useMiddleSocket from '../hooks/useMiddleSocket';
import {ChatAudioRecorder, OverallFeedbackModal, LoadingSpinner, Messages} from './index'
import Api from '../Services/Services';
import "../styles/InterviewChat/interviewchat.css"

const InterviewChat = () => {
    const { 
        handleInterview, 
        seconds, 
        minutes, 
        reset, 
        pause, 
        interview, 
        setChatInterview, 
        startfetching, 
        setStartFetch,
        startchat, 
        setChat } = useMiddleSocket();
    const [input, setInput] = useState<any>("");
    const [dataFromAudio, setDataFromAudio] = useState<any>(false);
    const [loadin, setLoad] = useState<any>(false);
    const [sessions, setSession] = useState<any>([]);
    const latest = JSON.parse(localStorage.getItem("userSession") || 'null');       
    // console.log("latest_session_info", interview) 
    const [loadingSessionId, setLoadingSessionId] = useState(null);
    const [isHovered, setIsHovered] = useState(false);
    let timerValue: any;
    const charLimit = 1200; 

    const buttonStyle = {
        color: '#ffffff',
        fontWeight: 'bolder',
        fontSize: '1rem',
        backgroundColor: isHovered ? '#888888' : '#a5a2a2', 
        border: 'none', 
        padding: '8px 20px', 
        cursor: 'pointer', 
        transition: 'background-color 0.3s',
        borderRadius: '5px 0 5px 0'
    };

    const ExecuteInterview = () => {
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        const user_session = latest;
        handleInterview({ 
            input, 
            user_session,
            timerValue,
            job_profile_id: 1686,
            all_user_id: 1959
        });
        setInput('');
        setChat(true) 
    };

    const handler = () => {
        ExecuteInterview();
        pause();
    };

    const startSession = async() => {
        setLoad(true)
        const data = {
            job_profile_id: 128,
            all_user_id: 1959
        };
        const response = await Api.sessionCreate(data);
        localStorage.setItem("userSession", JSON.stringify(response?.data))
        if(response?.data){  
            timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            handleInterview({ 
                input, 
                user_session: response?.data,
                timerValue,
                job_profile_id: 128,
                all_user_id: 1959
            });
            setInput('');
            setChat(true) 
        }
        setChatInterview([])
        setLoad(false)
    }

    const handleDataFromAudio = (audioTranscript: any) => {
        setInput((prevInput: any) => prevInput + ' ' + audioTranscript);
    };

    function handleDataAudio(data: any) {
        setDataFromAudio(data);
    }

    const handleChange = (e: any) => {
        const newInput = e.target.value;  
        if (newInput.length <= charLimit) {
            setInput(newInput);
        }
    };

    const fetchChatHistory = async (session: any) => {
        const sessionId = session?.id
        setLoadingSessionId(sessionId)
        setChat(false) 
        setChatInterview([])
            const data = {
                sessionId: sessionId
            }
            const response = await Api.fetchChatHistory(data)
            const fetched_session = await Api.fetchSingleSession(data)
            localStorage.setItem("userSession", JSON.stringify(fetched_session?.data))

            // console.log("fetching data...", response?.data)
            // console.log("fetching data observers...", fetched_session?.data)

        setChatInterview(response?.data?.total)
        setLoadingSessionId(null);
        if(fetched_session?.data?.attributes?.status == 'Complete'){
            setChat(false)
            reset() 
        }
        else {
           setChat(true) 
        }        
    }

    const fetchSession = async() =>{
        const data = {
            job_profile_id: 128,
            all_user_id: 1959
        }
        const response = await Api.fetchSession(data)
        // console.log("sessions", response?.data)
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
            <div className="interview-chat-container">
                <div style={{marginTop: '2rem'}}>                
                    <div>
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
                        
                        <div
                            style={{ 
                                display: 'flex',
                                flexDirection: 'column', 
                                width:'24rem',  
                                maxHeight: '500px',  
                                overflowY: 'scroll',   
                                padding: '0.5rem',
                                scrollbarWidth: 'none',  
                                msOverflowStyle: 'none', 
                                WebkitOverflowScrolling: 'touch',  
                                cursor: 'pointer'
                            }}
                        >
                        {sessions?.map((session: any, index: any) => (
                            <div 
                                key={session.id} 
                                className="session" 
                                style={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-between', 
                                    alignItems: 'center', 
                                    backgroundColor: '#ffffff', 
                                    borderRadius: '10px', 
                                    marginBottom: '10px',
                                    padding: '10px' 
                                }}>
                                <div onClick={() => fetchChatHistory(session)}>
                                    {new Date(session?.attributes?.createdAt).toLocaleDateString('en-US', {
                                        month: 'short',
                                        day: 'numeric',
                                    })}
                                    {' at '}
                                    {new Date(session?.attributes?.createdAt).toLocaleTimeString('en-US', {
                                        hour: '2-digit',
                                        minute: '2-digit',
                                        hour12: true,
                                    })}
                                </div>
                                {session?.attributes?.i_persona_observer?.data !== null && (
                                    <span>
                                        {(() => {
                                            const item = session.attributes.i_persona_observer.data;
                                            return (
                                                <OverallFeedbackModal
                                                    key={index}
                                                    metricsData={item?.attributes?.attributes?.interview_evaluation_metrics}
                                                    evaluationData={item?.attributes?.attributes?.interview_evaluation} 
                                                />
                                            );
                                        })()}
                                    </span>
                                )}
                                <span 
                                    onClick={() => fetchChatHistory(session)}
                                    style={{ 
                                        color: session?.attributes?.status === 'Incomplete' ? 'rgba(255, 0, 0, 0.63)' : 'rgba(0, 128, 0, 0.603)' }}>
                                    {session?.attributes?.status}
                                </span>
                                {loadingSessionId === session.id && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <Card className="chat-box" style={{ height: '36rem', width: '50rem', overflowY: 'auto' }}>
                   <Messages interview={interview}/>
            </Card>
            
            <div className='chat-timer-box' style={{}}>
                {(startchat) && (
                    <div>
                        <div style={{ fontSize: '50px', textAlign: 'center' }}>
                            {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
                        </div>
                
                        <div className='input-container' style={{width: '25rem'}}>
                            <Input.TextArea
                                value={input}
                                placeholder="Put your answer here"
                                onChange={handleChange}
                                rows={2}
                                className="input-area"
                            />
                            <div style={{ margin: '5px', color: '#d1cccb' }}>
                                <span>{`you must follow character limit:
                                    ${input.length}/${charLimit}`}
                                </span>
                            </div>
                            
                            <div className='actions'>
                                <div className='actions-audio'>
                                    <ChatAudioRecorder sendDataParent={handleDataAudio} sendDataToParent={handleDataFromAudio} />
                                    {dataFromAudio && <Spin indicator={<img src={fade} alt="" className='actions-load' />} />}
                                </div>
                                <div style={{marginTop: '0.97rem'}}>
                                    <button 
                                    onClick={handler}
                                    style={buttonStyle}
                                    onMouseEnter={() => setIsHovered(true)}
                                    onMouseLeave={() => setIsHovered(false)}
                                    className='actions-btn'>
                                        submit
                                    </button>
                                </div>
                            </div>
                        </div>                            
                    </div>
                )}
            </div>
            </div>
        </>
    );
};

export default InterviewChat;