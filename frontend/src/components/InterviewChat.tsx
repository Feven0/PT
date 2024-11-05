import { useState, useEffect, useContext } from 'react';
import { Card, Input, Button, Spin, Typography } from 'antd';
import fade from '../assets/fade-circles.svg';
import useMiddleSocket from '../hooks/useMiddleSocket';
import { useParams } from 'react-router-dom';
import hr from '../assets/hr.jpg';
import { CgProfile } from 'react-icons/cg'
import ReactMarkdown from 'react-markdown';
import { ProviderContext } from '../context/context';
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
    const { handleInterview, loading, seconds, minutes, pause, interview, setChatInterview, inter } = useMiddleSocket();
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
    const [observer, setObserver] = useState<any>([]);
    const latest = JSON.parse(localStorage.getItem("userSession"));
    const [viewloading, setShow] = useState(false);
    const [loadingSessionId, setLoadingSessionId] = useState(null);

    const charLimit = 1200; 
    // console.log("chat-history", inter)
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
        const user_session = latest;
        // previous_question = interview[interview?.length-1]?.content?.response?.question
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
        localStorage.setItem("userSession", JSON.stringify(response?.data?.latest_user_data))
        
        // if(response.data !== undefined){
            setClickStart(true)
            handleInterview({ 
                input: input, 
                interview: interview, 
                user_session: response?.data?.latest_user_data,
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
    // console.log("observers", observer)

    const fetchChatHistory = async (sessionId) => {
        setLoadingSessionId(sessionId);  
        const data = {
            sessionId: sessionId, 
        }
        const response = await Api.fetchChatHistory(data)
        const responseobs = await Api.fetchChatObserver(data)
        console.log("fetching data...", response?.data)
        setChatInterview(response?.data[0]?.chathistory)
        setObserver(responseobs?.data[0])
        setLoadingSessionId(null);
    }


    const fetchSession = async() =>{
        const userId= localStorage.getItem("userId")
        const response = await Api.fetchSession({userId})
        console.log("sessions", response.data)
        setSession(response.data?.all_user_data)
        //setLatest(response?.data?.latest_user_data)
        // setSession(data?.all_user_data)  
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
                    width:'34rem',  
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
                    <div key={index} >
                    <div className="session" style={{ display: 'flex', gap: '1rem', backgroundColor:'#ffffff', borderRadius: '10px', marginBottom: '10px'}}>
                        <div onClick={() => fetchChatHistory(session?.id)}>
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

                        {/* {interview[interview.length - 1]?.complete !== undefined &&(
                            <div
                                style={{
                                    marginLeft: '0.6rem',
                                    background: interview[interview.length - 1]?.complete === true ? '#8af5aa' : '#f58a8a', 
                                    color: 'white', 
                                    padding: '0.2rem 0.5rem', 
                                    borderRadius: '4px' 
                                }}
                            >
                                {interview[interview.length - 1]?.complete === true? 'complete' : 'Incomplete'}
                            </div>  
                        )} 
                        <div style={{fontSize:'11px', textAlign:'end'}}>hide</div>  */}
                    </div>
                    {loadingSessionId === session.id && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                    </div>
                ))}


                </div>

                <Card className="chat-box" style={{ height: '34rem', width: '70rem', overflowY: 'auto' }}>
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
                                    {(message?.content?.realtime_evaluation !== "" && message?.content?.realtime_evaluation !== undefined) && (
                                        <RealTimeEvaluation
                                            evaluation={message.content.realtime_evaluation}
                                        />
                                    )}
                                </div>
                            ))}
                            
                            

                            {(message?.user_type == 'assistant' && (
                                <div>
                                    {(message?.content?.chunk_response.length !== 0 && message?.content?.chunk_response !== undefined) && (
                                        <div className='messageassistant'>
                                            <img src={hr} alt="" className='profile-image' />
                                            <Paragraph style={{ margin: 0, textAlign: 'justify', color: '#606060', fontSize: '1rem' }}>
                                                {/* <MarkdownContent content={message?.assistant?.response?.start_message} /> */}                                        

                                                {message?.content?.time_limit !== "null" && (
                                                    <div>
                                                        time limit: {message?.content?.time_limit}
                                                    </div> 
                                                )}
                                                    {/* <div style={{color:'black'}}>
                                                        <MarkdownContent content={message?.content?.response?.question} />
                                                    </div>
                                                     */}
                                                            
                                                        <div className="chat-chunk-container">
                                                            {message?.content?.chunk_response.map((msg, index) => (
                                                                <p className="chat-chunk">
                                                                    {/* <MarkdownContent content={msg} /> */}
                                                                    {msg}
                                                                </p>
                                                            ))}
                                                        </div>
                                                          
                                                       
                            
                                                    {/* <MarkdownContent content={message?.content?.response?.end_message} /> */}
                                                
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
                            ))}
                        </div>
                    ))}

                    {(observer?.interview_evaluation !== "null" && observer?.interview_evaluation !== undefined) && (
                        <OverallFeedbackModal
                        metricsData={observer?.interview_evaluation_metrics}
                        evaluationData={observer?.interview_evaluation} 
                        />
                    )}

                    {loading && <Spin indicator={<img src={fade} alt="" className='h-10' />} />}
                </Card>
                
                <div className='chat-timer-box' style={{}}>
                    <div>
                        {!start && (
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
                                Start
                            </Button>
                        )}
                    </div>

                    {start && (
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