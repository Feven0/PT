import { useState, useEffect, useContext } from 'react';
import { Card, Input, Button, Spin, Typography, Flex, Tooltip } from 'antd';
import fade from '../../assets/fade-circles.svg';
import useMiddleSocket from '../../hooks/useMiddleSocket';
import hr from '../../assets/hr.jpg';
import { CgProfile } from 'react-icons/cg'
import ReactMarkdown from 'react-markdown';
import { Link } from 'react-router-dom';
import { ProviderContext } from '../../context/context';
import {AudioRecorder, RealTimeEvaluation, OverallFeedbackModal, PreviousChat, LoadingSpinner} from './index'
import Api
 from '../../Services/Services';
import "../../styles/InterviewChat/interviewchat.css"

const { Text, Paragraph } = Typography;

const InterviewChat = () => {

    const { handleInterview, interview, loading, latestInterviewResponse, seconds, minutes, pause, setCount, interview_metrics } = useMiddleSocket();
    const { latestinterviewchat, latestUserData, latestsession, setStart } = useContext(ProviderContext);
    const [counter, setCounter] = useState(1);
    const [input, setInput] = useState("");
    const [dataFromAudio, setDataFromAudio] = useState(false);
    const [initialChatInterview, setInitialChatInterview] = useState(latestinterviewchat);
    const [view, setShow] = useState(false);
    const [start, setClickStart] = useState(false);
    const [lastTimerValue, setLastTimerValue] = useState('00:00'); 
    const [clarifications, setClarifications] = useState({}); 
    const [load, setLoading] = useState({}); 
    const [clickCount, setClickCount] = useState({}); 
    const [error, setError] = useState('');
    const charLimit = 1200; 

    const [isHovered, setIsHovered] = useState(false);

    const buttonStyle = {
        color: '#ffffff',
        fontWeight: 'bolder',
        fontSize: '1rem',
        backgroundColor: isHovered ? '#888888' : '#a5a2a2', 
        border: 'none', 
        padding: '10px 20px', 
        cursor: 'pointer', 
        transition: 'background-color 0.3s',
    };

    const clarify_question = async (question) => {
        setClickCount((prev) => ({
            ...prev,
            [question]: (prev[question] || 0) + 1,
        }));

        if ((clickCount[question] || 0) >= 2) return;

        setLoading((prev) => ({ ...prev, [question]: true })); 
        const data = { question };
        try {
            const response = await Api.clarify(data);
            setClarifications((prev) => ({
                ...prev,
                [question]: response?.data?.clarification,
            }));
        } catch (error) {
            console.error("Error fetching clarification:", error);
        } finally {
            setLoading((prev) => ({ ...prev, [question]: false })); 
        }
    };   

    let previous_question = "";
    let timerValue: any;
    
    useEffect(() => {
        setStart(false);
    }, [setStart]);

    // console.log('counter Value:', counter);
    console.log('current interview length:', interview);


    const onSendMessage = (timerValue: any) => {
        const user_session = latestsession;
        previous_question = interview[interview?.length-1]?.assistant?.response?.question

        handleInterview({ 
            input, 
            interview, 
            // latestUserInfo,
            user_session,
            counter,
            timerValue,
            previous_question
        });
        setInput('');
        setCounter(counter < 9 ? counter + 1 : 1);
    };

    const handler = (event) => {
        // if (event.keyCode === 13) {  
            timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            onSendMessage(timerValue);
            pause();
            setLastTimerValue(timerValue); 
        // }
    };

    const startInterview = () => {
        setClickStart(true)

        handleInterview({ 
            input: input, 
            interview: interview, 
            // latestUserInfo: latestUserData,
            user_session: latestsession,
            counter: counter,
            timerValue: lastTimerValue,
            previous_question: previous_question
        });
        setCounter(counter < 9 ? counter + 1 : 1);
    }  

    const handleDataFromAudio = (audioTranscript) => {
        setInput((prevInput) => prevInput + ' ' + audioTranscript);
    };

    function handleDataAudio(data) {
        setDataFromAudio(data);
    }

    const MarkdownContent = ({ content }) => {
        const formattedContent = content?.replace(/---/g, ' ');
        return (
            <div className="markdown-content" style={{width: '100%'}}>
                <ReactMarkdown>{formattedContent}</ReactMarkdown>
            </div>
        );
    };

    const handleChange = (e) => {
        const newInput = e.target.value;
  
        if (newInput.length <= charLimit) {
            setInput(newInput);
            setError('');
        } else {
            setError(`Character limit of ${charLimit} exceeded.`);
        }
    };

   
    return (
        <>
            <div className="interview-chat-container">
                <Card className="chat-box" style={{ height: '30rem', width: '55rem', overflowY: 'auto' }}>
                <PreviousChat/>
                
                {interview?.map((message, index) => (
                    <div className='chat_contain' key={index}>
                        {message?.candidate?.response && (
                            <div className='messagecandidate' style={{ backgroundColor: '#ffffff', border: '1px solid #fcf8f8' }}>
                                <Paragraph style={{ margin: 0 }}>
                                    <CgProfile size={40} />
                                    <p className="message-text" style={{ fontSize: '1rem', lineHeight: '2rem'}}>    
                                        {message?.candidate?.response}
                                    </p>
                                </Paragraph>
                            </div>
                        )}

                        {(message?.assistant?.realtime_evaluation !== "null" && message?.assistant?.realtime_evaluation !== undefined) && (
                            <RealTimeEvaluation
                                evaluation={message.assistant.realtime_evaluation}
                            />
                        )}

                        {(message?.assistant?.response !== "null" && message?.assistant?.response !== undefined) && (
                            <div className='messageassistant'>
                                <img src={hr} alt="" className='profile-image' />
                                <Paragraph style={{ margin: 0, textAlign: 'justify', color: '#606060', fontSize: '1rem' }}>
                                    {/* <MarkdownContent content={message?.assistant?.response?.start_message} /> */}
                                        <div>
                                            time limit: {message?.assistant?.response?.time_limit}
                                        </div>
                                        <div style={{color:'black'}}>
                                            <MarkdownContent content={message?.assistant?.response?.question} />
                                        </div>
                                        
                                        <MarkdownContent content={message?.assistant?.response?.end_message} />
                                    
                                    <div style={{ display: 'flex', alignItems: 'center' }}>
                                        <div
                                            onClick={() => clarify_question(message?.assistant?.response?.question)}
                                            className='clarify'
                                            style={{ pointerEvents: (clickCount[message?.assistant?.response?.question] || 0) >= 2 ? 'none' : 'auto', opacity: (clickCount[message?.assistant?.response?.question] || 0) >= 2 ? 0.5 : 1 }}>
                                            Clarify
                                        </div>
                                        {load[message?.assistant?.response?.question] && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                                    </div>

                                    {clarifications[message?.assistant?.response?.question] && (
                                        <div className='clarification'>
                                            <MarkdownContent content={clarifications[message?.assistant?.response?.question]} />
                                        </div>
                                    )}
                                </Paragraph>
                            </div>
                        )}
                    </div>
                ))}

                {(interview?.[interview.length - 1]?.assistant?.overall_evaluation !== "null" && interview?.[interview.length - 1]?.assistant?.overall_evaluation !== undefined) && (
                    <OverallFeedbackModal
                     metricsData={interview?.[interview.length - 1]?.assistant?.metrics}
                     evaluationData={interview?.[interview.length - 1]?.assistant?.overall_evaluation} 
                    />
                )}

                {loading && <Spin indicator={<img src={fade} alt="" className='h-10' />} />}
                </Card>
                
                <div className='chat-timer-box'>
                    <div>
                        {!start && (
                            <Button 
                            style={{ margin:'7rem', textAlign:'center', width: '30vh', height: '10vh' }}
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
                                    <div style={{marginTop: '0.6rem'}}>
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