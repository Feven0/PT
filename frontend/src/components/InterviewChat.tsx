import { useState, useEffect } from 'react';
import { Card, Input, Button, Spin } from 'antd';
import fade from '../assets/fade-circles.svg';
import useMiddleSocket from '../hooks/useMiddleSocket';
import {
    ChatAudioRecorder, 
    OverallFeedbackModal, 
    LoadingSpinner, 
    Messages,
    CancelModal
} from './index'
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
    console.log("latest_session_info", interview) 
    const [loadingSessionId, setLoadingSessionId] = useState(null);
    const [isHovered, setIsHovered] = useState(false);
    let timerValue: any;
    const charLimit = 1200; 
    const [showCancelModal, setShowCancelModal] = useState(false);
    const [loading, setLoading] = useState(false);
    const [questions, setQuestions] = useState<any>([]); 
    const handleClose = () => setShowCancelModal(false);
    const handleShow = () => setShowCancelModal(true);


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
        const inputToSend = questions.length > 0 ? questions : input;    
        handleInterview({ 
            input: inputToSend, 
            user_session,
            timerValue,
            job_profile_id: 232,
            all_user_id: 1920
        });    
        setInput('');
        setQuestions([]); 
        setChat(true); 
    };
    

    const handler = () => {
        ExecuteInterview();
        pause();
    };

    const startSession = async() => {
        setLoad(true)
        const data = {
            job_profile_id: 232,
            all_user_id: 1920
        };
        const response = await Api.sessionCreate(data);
        localStorage.setItem("userSession", JSON.stringify(response?.data))
        if(response?.data){  
            timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            handleInterview({ 
                input, 
                user_session: response?.data,
                timerValue,
                job_profile_id: 232,
                all_user_id: 1920
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
        if(fetched_session?.data?.attributes?.status == 'Completed'){
            setChat(false)
            reset() 
        }
        else if(fetched_session?.data?.attributes?.status == 'Incomplete') {
           setChat(true) 
        }        
    }

    const closeSession = async() => {
        const user_session = latest;        
        const obj = {
            user_session: user_session,
            job_profile_id: 232,
            all_user_id: 1920
        }
        const param = {data: obj}
        const response = await Api.CloseSession(param)
        console.log("response-close", response?.data)
    }

    const deleteSession = async() => {
        const user_session = latest;
        const data = {sessionId: user_session?.id}
        const response = await Api.DeleteSession(data)
        console.log("response-delete", response?.data)
    }

    const fetchSession = async() =>{
        const data = {
            job_profile_id: 232,
            all_user_id: 1920
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
        
    const handleConfirm = async (action: any) => {
        setLoading(true);
        try {
            if (action === 'pause') {
                // Logic to pause the interview
                window.location.reload();
                console.log("Interview paused.");
            } else if (action === 'stopEvaluate') {
                // Logic to stop and evaluate
                await closeSession()
                console.log("Interview stopped and evaluated.");
                window.location.reload();
            } else if (action === 'stopDelete') {
                // Logic to stop and delete
                await deleteSession()
                console.log("Interview stopped and deleted.");
                window.location.reload();
            }
        } catch (error) {
            console.error("Error during session action:", error);
        } finally {
            setLoading(false);
            handleClose();
        }
    };

    // const handleKeyPress = (e: any) => {
    //     if (e.key === 'Enter' && !e.shiftKey && input.trim() !== '' && interview?.length === 21) {
    //         setQuestions([...questions, input.trim()]);
    //         setInput(''); 
    //         e.preventDefault(); 
    //     }
    // };

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
                        {/* Display userjob sessions */}
                        {(Array.isArray(sessions) && sessions.length > 0) && (
                            <div>
                                {sessions.map((session: any, index: any) => (
                                    session?.attributes?.status !== 'Deleted' && (  // Condition to check before rendering
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
                                                    color: session?.attributes?.status === 'Incomplete' ? 'rgba(255, 0, 0, 0.63)' : 'rgba(0, 232, 0, 0.603)' }}>
                                                {session?.attributes?.status}
                                            </span>
                                            {loadingSessionId === session.id && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                                        </div>
                                    )
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
            
            {/* Interview Chats */}
            <Card className="chat-box" style={{ height: '36rem', width: '50rem', overflowY: 'auto' }}>
                <Messages interview={interview}/>
            </Card>
            
            {/* Input area */}
            <div className='chat-timer-box' style={{}}>
                {(startchat) && (
                    <div>
                        {/* cancel section */}
                        <div>
                            <Card>
                                <Button 
                                    style={{ 
                                        margin: '1rem', 
                                        textAlign: 'center',  
                                        color: '#ffffff', 
                                        fontWeight: 'bolder', 
                                        fontSize: '0.81rem' 
                                    }}
                                    onClick={handleShow}
                                >
                                    Cancel
                                    <span>
                                        {loading && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                                    </span>
                                </Button>
                            </Card>

                            {/* Modal for confirmation */}
                            <CancelModal 
                                visible={showCancelModal} 
                                handleClose={handleClose} 
                                handleConfirm={handleConfirm}
                            />
                        </div>
                       
                        {/* Input area */}
                        <div>
                            <div style={{ fontSize: '50px', textAlign: 'center' }}>
                                {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
                            </div>
                    
                            <div className='input-container' style={{width: '25rem'}}>
                                <Input.TextArea
                                    value={input}
                                    placeholder="Put your answer here"
                                    onChange={handleChange}
                                    // onKeyPress={handleKeyPress}
                                    rows={2}
                                    className="input-area"
                                />
                                <div style={{ margin: '5px', color: '#d1cccb' }}>
                                    <span>{`you must follow character limit:
                                        ${input.length}/${charLimit}`}
                                    </span>
                                </div>

                                {interview?.length === 21 && (
                                    <div>
                                        <ul>
                                            {questions.map((question: any, index: any) => (
                                                <li key={index}>{question}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                                
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
                    </div>
                )}
            </div>

          </div>
        </>
    );
};

export default InterviewChat;