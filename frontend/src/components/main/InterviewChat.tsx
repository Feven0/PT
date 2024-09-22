import { useState, useEffect, useContext } from 'react';
import { Card, Input, Button, Spin, Typography } from 'antd';
import fade from '../../assets/fade-circles.svg';
import useMiddleSocket from '../../hooks/useMiddleSocket';
import hr from '../../assets/hr.jpg';
import { CgProfile } from 'react-icons/cg'
import ReactMarkdown from 'react-markdown';
import { AudioRecorder } from './index';
import { Link } from 'react-router-dom';
import { ProviderContext } from '../../context/context';
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
    const [lastTimerValue, setLastTimerValue] = useState('00:00'); 
    const bool = true;

    useEffect(() => {
        setStart(false);
    }, [setStart]);

    console.log('counter Value:', counter);

    const onSendMessage = (timerValue: any) => {
        const latestUserInfo = latestUserData;
        const user_session = latestsession;
        console.log('Last counter Value:', counter);

        handleInterview({ 
            input, 
            interview, 
            latestUserInfo,
            user_session,
            counter,
            timerValue
        });
        setInput('');
        setCounter(counter < 5 ? counter + 1 : 1);
    };

    const handler = (event) => {
        if (event.keyCode === 13) {  
            const timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            onSendMessage(timerValue);
            pause();
            setLastTimerValue(timerValue); 
        }
    };

   

    const handleDataFromAudio = (audioTranscript) => {
        setInput((prevInput) => prevInput + ' ' + audioTranscript);
    };

    function handleDataAudio(data) {
        setDataFromAudio(data);
    }

    const MarkdownContent = ({ content }) => {
        const formattedContent = content.replace(/---/g, ' ');
        return (
            <div className="markdown-content" style={{width: '100%'}}>
                <ReactMarkdown>{formattedContent}</ReactMarkdown>
            </div>
        );
    };

    return (
        <>
            <div className="interview-chat-container">
                <Card className="chat-box" style={{ height: '25rem', width: '55rem', overflowY: 'auto' }}>
                    <div className="btn-hide">
                        <Button 
                            onClick={() => setShow(!view)} 
                            style={{ backgroundColor: 'antiquewhite', borderColor: 'antiquewhite', color: 'darkslategray' }}
                        >
                            {!view ? 'Previous' : 'Hide'}
                        </Button>
                    </div>

                    {view && (
                        <div>
                            {initialChatInterview?.map((message, index) => (
                                <div className='' key={index}>
                                    {message.role === "candidate" && (
                                        <div className='messagecandidate'>
                                            <Paragraph style={{ margin: 0}}>
                                                <CgProfile  size={40}/>
                                                <p className="message-text">{message?.response}</p>
                                            </Paragraph>
                                        </div>
                                    )}
                                    <br />
                                    {message.role === "assistant" && (
                                        <div className='messageassistant'>
                                            <img src={hr} alt="" className='profile-image' />
                                            <Paragraph style={{ margin: 0, textAlign:'justify', color: '#606060' }}>
                                                <MarkdownContent content={message?.response} />
                                            </Paragraph>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {interview?.map((message, index) => (
                        <div className='chat_contain' key={index}>
                            {message.role === "candidate" && (
                                <div className='messagecandidate'>
                                    <Paragraph style={{ margin: 0}}>
                                        <CgProfile  size={40}/>
                                        <Text className="message-text">{message?.response}</Text>
                                    </Paragraph>
                                </div>
                            )}
                            {message.role === "assistant" && (
                                <div className='messageassistant'>
                                    <img src={hr} alt="" className='profile-image' />
                                    <Paragraph style={{ margin: 0, textAlign:'justify', color: '#606060' }}>
                                        <MarkdownContent content={message?.response} />                                   
                                    </Paragraph>
                                </div>
                            )}
                        </div>
                    ))}
                    {loading && <Spin indicator={<img src={fade} alt="" className='h-10' />} />}
                </Card>
                
                <div className='chat-timer-box'>
                    <div style={{ fontSize: '50px', textAlign: 'center' }}>
                        {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
                    </div>
             
                    <div className='input-container' style={{width: '28rem'}}>
                        <Input.TextArea
                            value={input}
                            placeholder="Put your answer here"
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handler}
                            rows={2}
                            className="input-area"
                        />
                        <div className='actions'>
                            <AudioRecorder sendDataParent={handleDataAudio} sendDataToParent={handleDataFromAudio} />
                            {dataFromAudio && <Spin indicator={<img src={fade} alt="" className='actions-load' />} />}
                        </div>
                    </div>

                    <div className='progress-btn'>
                        {counter === 1 && (
                            <Link to={`/evaluation_status/${bool}`}>
                                <Button className='progress-button'>check progress</Button>
                            </Link>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
};

export default InterviewChat;