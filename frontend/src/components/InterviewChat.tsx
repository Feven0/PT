import { useState, useEffect, useContext } from 'react';
import { Card, Input, Button, Spin, Typography } from 'antd';
import fade from '../assets/fade-circles.svg';
import useMiddleSocket from '../hooks/useMiddleSocket';
import { useParams } from 'react-router-dom';
import hr from '../assets/hr.jpg';
import { CgProfile } from 'react-icons/cg'
import ReactMarkdown from 'react-markdown';
import { ProviderContext } from '../context/context';
import {AudioRecorder, RealTimeEvaluation, OverallFeedbackModal, PreviousChat, LoadingSpinner} from './index'
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
    const { handleInterview, interview, loading, seconds, minutes, pause, setChatInterview } = useMiddleSocket();
    const { latestsession, setStart} = useContext<any>(ProviderContext);
    const [counter, setCounter] = useState<any>(1);
    const [input, setInput] = useState<any>("");
    const [dataFromAudio, setDataFromAudio] = useState<any>(false);
    const [start, setClickStart] = useState<any>(false);
    const [lastTimerValue, setLastTimerValue] = useState<any>('00:00'); 
    const [clarifications, setClarifications] = useState<any>({}); 
    const [load, setLoading] = useState<any>({}); 
    const [clickCount, setClickCount] = useState<any>({}); 
    const [sessions, setSession] = useState<any>([]);
    const userSession = JSON.parse(localStorage.getItem("userSession"));
    const sessionId = userSession?.latest_user_data?._additional?.id;
    const latestudata = userSession?.latest_user_data;
    const [viewloading, setShow] = useState(false);
    const [loadingSessionId, setLoadingSessionId] = useState(null);

    const charLimit = 1200; 
    console.log("chat-history", interview)
    const [isHovered, setIsHovered] = useState(false);

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

    let previous_question = "";
    let timerValue: any;
    

    const onSendMessage = (timerValue: any) => {
        const user_session = latestudata;
        previous_question = interview[interview?.length-1]?.content?.response?.question
        handleInterview({ 
            input, 
            interview, 
            user_session,
            counter,
            timerValue,
            previous_question
        });
        setInput('');
        setCounter(counter < 9 ? counter + 1 : 1);
    };

    const handler = () => {
        // if (event.keyCode === 13) { 
            timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            onSendMessage(timerValue);
            pause();
            setLastTimerValue(timerValue); 
        // }
    };

    const startInterview = async() => {
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

        // if(response.data !== undefined){
            setClickStart(true)
            handleInterview({ 
                input: input, 
                interview: interview, 
                user_session: latestudata,
                counter: counter,
                timerValue: lastTimerValue,
                previous_question: previous_question
            });
            setCounter(counter < 9 ? counter + 1 : 1);

        // }
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
            // setError('');
        } 
    };

    const fetchChatHistory = async (sessionId) => {
        console.log("sessionID", sessionId)
        setLoadingSessionId(sessionId);  
        const data = {
        sessionId: sessionId, 
        }
        const response = await Api.fetchChatHistory(data)
        setChatInterview(response?.data[0]?.chathistory)
        setLoadingSessionId(null);
    }


    const fetchSession = async() =>{
        const userId= localStorage.getItem("userId")
        const response = await Api.fetchSession({userId})
        console.log("sessions", response.data)
        setSession(response.data?.all_user_data)
    }

    useEffect(() => {
        setStart(false);
        fetchSession()
    }, [setStart]);
   
    return (
        <>
            <div className="interview-chat-container">
                <div 
                style={{ 
                    display: 'flex',
                    flexDirection: 'column-reverse', 
                    width:'10rem', 
                    gap:'1rem',   
                    maxHeight: '500px',  
                    overflowY: 'scroll',   
                    padding: '0.5rem',
                    marginTop: '3rem',
                    scrollbarWidth: 'none',  
                    msOverflowStyle: 'none', 
                    WebkitOverflowScrolling: 'touch',  
                    cursor: 'pointer'
                    }}>
               {sessions?.map((session, index) => (
                    <div style={{ display: 'flex', gap: '1rem' }} key={index} onClick={() => fetchChatHistory(session?._additional?.id)}>
                    <div className="session">
                        {new Date(session?.createdAt).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        })}
                        {' at '}
                        {new Date(session?.createdAt).toLocaleTimeString('en-US', {
                        hour: 'numeric',
                        minute: 'numeric',
                        hour12: true,
                        })}
                    </div>

                    {loadingSessionId === session.id && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                    </div>
                ))}
                </div>

                <Card className="chat-box" style={{ height: '34rem', width: '60rem', overflowY: 'auto' }}>
                    {/* <PreviousChat/> */}
                    
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
                                    {(message?.content?.realtime_evaluation !== "null" && message?.content?.realtime_evaluation !== undefined) && (
                                        <RealTimeEvaluation
                                            evaluation={message.content.realtime_evaluation}
                                        />
                                    )}
                                </div>
                            ))}

                            {(message?.user_type == 'assistant' && (
                                <div>
                                    {(message?.content?.response !== "null" && message?.content?.response !== undefined) && (
                                        <div className='messageassistant'>
                                            <img src={hr} alt="" className='profile-image' />
                                            <Paragraph style={{ margin: 0, textAlign: 'justify', color: '#606060', fontSize: '1rem' }}>
                                                {/* <MarkdownContent content={message?.assistant?.response?.start_message} /> */}
                                                    <div>
                                                        time limit: {message?.content?.response?.time_limit}
                                                    </div>
                                                    <div style={{color:'black'}}>
                                                        <MarkdownContent content={message?.content?.response?.question} />
                                                    </div>
                                                    
                                                    <MarkdownContent content={message?.content?.response?.end_message} />
                                                
                                                <div style={{ display: 'flex', alignItems: 'center' }}>
                                                    <div
                                                        onClick={() => clarify_question(message?.content?.response?.question)}
                                                        className='clarify'
                                                        style={{ pointerEvents: (clickCount[message?.content?.response?.question] || 0) >= 2 ? 'none' : 'auto', opacity: (clickCount[message?.content?.response?.question] || 0) >= 2 ? 0.5 : 1 }}>
                                                        Clarify
                                                    </div>
                                                    {load[message?.content?.response?.question] && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                                                </div>

                                                {clarifications[message?.content?.response?.question] && (
                                                    <div className='clarification'>
                                                        <MarkdownContent content={clarifications[message?.content?.response?.question]} />
                                                    </div>
                                                )}
                                            </Paragraph>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    ))}

                    {(interview?.[interview.length - 1]?.content?.interview_evaluation !== "null" && interview?.[interview.length - 1]?.content?.interview_evaluation !== undefined) && (
                        <OverallFeedbackModal
                        metricsData={interview?.[interview.length - 1]?.content?.interview_evaluation_metrics}
                        evaluationData={interview?.[interview.length - 1]?.content?.interview_evaluation} 
                        />
                    )}

                    {loading && <Spin indicator={<img src={fade} alt="" className='h-10' />} />}
                </Card>
                
                <div className='chat-timer-box'>
                    <div>
                        {!start && (
                            <Button 
                            style={{ margin:'7rem', textAlign:'center', width: '30vh', height: '10vh', color:'#ffffff', fontWeight: 'bolder', fontSize: '1.42rem' }}
                            className='start-btn' 
                            onClick={startInterview}
                            >
                                Start
                            </Button>
                        )}
                    </div>

                    {start && (
                        <div>
                            <div style={{ fontSize: '50px', textAlign: 'center' }}>
                                {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
                            </div>
                    
                            <div className='input-container' style={{width: '28rem'}}>
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