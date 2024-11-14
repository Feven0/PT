import { useState, useEffect } from 'react';
import { Card, Input, Button, Spin, Typography } from 'antd';
import fade from '../assets/fade-circles.svg';
import useMiddleSocket from '../hooks/useMiddleSocket';
import { useParams } from 'react-router-dom';
import hr from '../assets/hr.jpg';
import { CgProfile } from 'react-icons/cg'
import ReactMarkdown from 'react-markdown';
import {AudioRecorder, RealTimeEvaluation, OverallFeedbackModal, LoadingSpinner} from './index'
import Api from '../Services/Services';
import "../styles/InterviewChat/interviewchat.css"
import users from '../assets/mock-data/user_profiles.json';
import jobs from '../assets/mock-data/job_profile.json';

const { Paragraph } = Typography;

interface MarkdownContentProps {
    content?: string; 
}

const InterviewChat = () => {
    const {userId, jobId} = useParams()
    const { 
        handleInterview, 
        loading, 
        seconds, 
        minutes, 
        reset, 
        pause, 
        interview, 
        setChatInterview, 
        startfetching, 
        setStartFetch,
        ready, 
        setReady,
        startchat, 
        setChat } = useMiddleSocket();
    const [input, setInput] = useState<any>("");
    const [dataFromAudio, setDataFromAudio] = useState<any>(false);
    const [loadin, setLoad] = useState<any>(false);
    const [lastTimerValue, setLastTimerValue] = useState<any>('00:00'); 
    const [clarifications, setClarifications] = useState<any>({}); 
    const [load, setLoading] = useState<any>({}); 
    const [clickCount, setClickCount] = useState<any>({}); 
    const [sessions, setSession] = useState<any>([]);
    const latest = JSON.parse(localStorage.getItem("userSession") || 'null');        
    const [loadingSessionId, setLoadingSessionId] = useState(null);
    const [isHovered, setIsHovered] = useState(false);
    let timerValue: any;
    const charLimit = 1200; 
    console.log(lastTimerValue)

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

    const clarify_question = async (question: any) => {
        setClickCount((prev: any) => ({
            ...prev,
            [question]: (prev[question] || 0) + 1,
        }));

        if ((clickCount[question] || 0) >= 2) return;

        setLoading((prev: any) => ({ ...prev, [question]: true })); 
        const data = { question };
        try {
            const response = await Api.clarify(data);
            setClarifications((prev: any) => ({
                ...prev,
                [question]: response?.data?.clarification,
            }));
        } catch (error) {
            console.error("Error fetching clarification:", error);
        } finally {
            setLoading((prev: any) => ({ ...prev, [question]: false })); 
        }
    };   
    
    const startInterview = () => {
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        const user_session = latest;
        handleInterview({ 
            input, 
            user_session,
            timerValue
        });
        setInput('');
        setLastTimerValue(timerValue); 
        setReady(false)
        setChat(true) 
    };

    const handler = () => {
        startInterview();
        pause();
    };

    const startSession = async() => {
        const filteredJob = jobs.filter(match => match.job_profile_id === parseInt(jobId as any));
        const filteredUser = users.filter(match => match?.user_profile_id === parseInt(userId as any));
        setLoad(true)
        const data = {
            jobId: jobId,
            userId: userId,
            name: filteredUser[0]?.name,
            cvJson: filteredUser[0],
            jbJson: filteredJob[0]
        };
        const response = await Api.sessionCreate(data);
        localStorage.setItem("userSession", JSON.stringify(response?.data))
        setReady(true)
        setChatInterview([])
        setLoad(false)
    }

    const handleDataFromAudio = (audioTranscript: any) => {
        setInput((prevInput: any) => prevInput + ' ' + audioTranscript);
    };

    function handleDataAudio(data: any) {
        setDataFromAudio(data);
    }

    const MarkdownContent: React.FC<MarkdownContentProps> =  ({ content }) => {
        const formattedContent = content?.replace(/---/g, ' ');
        return (
            <div className="markdown-content" style={{width: '100%'}}>
                <ReactMarkdown>{formattedContent}</ReactMarkdown>
            </div>
        );
    };

    const handleChange = (e: any) => {
        const newInput = e.target.value;  
        if (newInput.length <= charLimit) {
            setInput(newInput);
        }
    };

    const fetchChatHistory = async (session: any) => {
        const sessionId = session?.id
        setReady(false)
        setLoadingSessionId(sessionId)
        setChat(false) 
        setChatInterview([])
            const data = {
                sessionId: sessionId
            }
            const response = await Api.fetchChatHistory(data)
            const fetched_session = await Api.fetchSingleSession(data)
            localStorage.setItem("userSession", JSON.stringify(fetched_session?.data))

            console.log("fetching data...", response?.data)
        setChatInterview(response?.data?.total)
        setLoadingSessionId(null);
        if(response?.data?.count == 0) {
            setReady(true)
        }
        if(fetched_session?.data?.attributes?.status == 'Complete'){
            setReady(false)
            setChat(false)
            reset() 
        }
        else {
           setChat(true) 
        }        
    }

    const fetchSession = async() =>{
        const userId= localStorage.getItem("userId")
        const data = {
            alluser: userId,
            jobId: jobId
        }
        const response = await Api.fetchSession(data)
        console.log("sessions", response?.data)
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
                        {sessions.map((session: any, index: any) => (
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
                                {session?.attributes?.i_persona_observer?.data !== undefined && (
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
                    <div>
                        {interview?.map((message: any, index: any) => (
                            <div className='chat_contain' key={index}>
                                {(message?.user_type == 'candidate' && message?.content?.response) && (
                                    <div className='messagecandidate' style={{ backgroundColor: '#ffffff', border: '1px solid #fcf8f8' }}>
                                        <Paragraph style={{ margin: 0 }}>
                                            <CgProfile size={40} />
                                            <p className="message-text" style={{ fontSize: '1rem', lineHeight: '2rem'}}>    
                                                {message?.content?.response}
                                            </p>
                                        </Paragraph>
                                    </div>
                                )}

                                {(message?.user_type == 'assistant' && (
                                    <div>
                                        {(message?.content?.realtime_evaluation !== "" && message?.content?.realtime_evaluation !== "null") && (
                                            <RealTimeEvaluation
                                                evaluation={message.content.realtime_evaluation}
                                            />
                                        )}
                                    </div>
                                ))}
                                
                                {(message?.user_type == 'assistant' && (
                                    <div>
                                        {(message?.content?.chunk_response?.length > 0)  ? (
                                            <div className='messageassistant'>
                                                <img src={hr} alt="" className='profile-image' />
                                                <Paragraph style={{ margin: 0, textAlign: 'justify', color: '#606060', fontSize: '1rem' }}>
                                                    {message?.content?.time_limit !== "null" && (
                                                        <div>
                                                            time limit: {message?.content?.time_limit}
                                                        </div> 
                                                    )}
                                                    
                                                    {message?.content?.chunk_response !== "" && (          
                                                    <div className="chat-chunk-container">
                                                        {message?.content?.chunk_response?.map((msg: any, index: any) => (
                                                            <p className="chat-chunk" key={index}>
                                                                {msg}
                                                            </p>
                                                        ))}
                                                    </div>
                                                    )}
                                                            
                                                    
                                                    <div style={{ display: 'flex', alignItems: 'center' }}>
                                                        <div
                                                            onClick={() => clarify_question(message?.content?.full_response)}
                                                            className='clarify'
                                                            style={{ pointerEvents: (clickCount[message?.content?.full_response] || 0) >= 2 ? 'none' : 'auto', opacity: (clickCount[message?.content?.full_response] || 0) >= 2 ? 0.5 : 1 }}>
                                                            Clarify
                                                        </div>
                                                        {load[message?.content?.full_response] && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                                                    </div>

                                                    {clarifications[message?.content?.full_response] && (
                                                        <div className='clarification'>
                                                            <MarkdownContent content={clarifications[message?.content?.full_response]} />
                                                        </div>
                                                    )}
                                                </Paragraph>
                                            </div>
                                        ):(
                                            <div>
                                                {message?.content?.full_response !== "" && (
                                                <div className='messageassistant'>                                                            
                                                    <img src={hr} alt="" className='profile-image' />
                                                    <Paragraph style={{ margin: 0, textAlign: 'justify', color: '#606060', fontSize: '1rem' }}>
                                                        {message?.content?.time_limit !== "null" && (
                                                            <div>
                                                                time limit: {message?.content?.time_limit}
                                                            </div> 
                                                        )}
                                                        
                                                                    
                                                        <div className="chat-chunk-container">
                                                            {message?.content?.full_response}
                                                        </div>
                                                                
                                                        
                                                        <div style={{ display: 'flex', alignItems: 'center' }}>
                                                            <div
                                                                onClick={() => clarify_question(message?.content?.full_response)}
                                                                className='clarify'
                                                                style={{ pointerEvents: (clickCount[message?.content?.full_response] || 0) >= 2 ? 'none' : 'auto', opacity: (clickCount[message?.content?.full_response] || 0) >= 2 ? 0.5 : 1 }}>
                                                                Clarify
                                                            </div>
                                                            {load[message?.content?.full_response] && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                                                        </div>

                                                        {clarifications[message?.content?.full_response] && (
                                                            <div className='clarification'>
                                                                <MarkdownContent content={clarifications[message?.content?.full_response]} />
                                                            </div>
                                                        )}
                                                    </Paragraph>
                                                    </div>
                                                    
                                                )}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        ))}

                        {loading && <Spin indicator={<img src={fade} alt="" className='h-10' />} />}
                    </div>
            </Card>
            
            <div className='chat-timer-box' style={{}}>
                <div>
                    {ready && (
                        <Button 
                        style={{ 
                            margin:'7rem', 
                            textAlign:'center', 
                            width: '30vh', 
                            height: '10vh', 
                            color:'#ffffff', 
                            fontWeight: 'bolder', 
                            fontSize: '1.42rem'
                        }}
                        className='start-btn' 
                        onClick={startInterview}
                        >
                            Ready
                        </Button>
                    )}
                </div>

                {(ready || startchat) && (
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
                                    <AudioRecorder sendDataParent={handleDataAudio} sendDataToParent={handleDataFromAudio} />
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