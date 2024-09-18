import { useState, useEffect, useContext } from 'react';
import { Card, Input, Button, Spin, Typography } from 'antd';
import fade from '../../assets/fade-circles.svg';
import useMiddleSocket from '../../hooks/useMiddleSocket';
import hr from '../../assets/hr.jpg';
import { CgProfile } from 'react-icons/cg'
import ReactMarkdown from 'react-markdown';
import { AudioRecorder } from './index';
import { ProviderContext } from '../../context/context';
import "../../styles/InterviewChat/interviewchat.css"

const { Text } = Typography;

const InterviewChat = () => {

    const { handleInterview, interview, loading, latestInterviewResponse, seconds, minutes, pause, setCount } = useMiddleSocket();
    const { latestinterviewchat, latestUserData, latestsession, setStart } = useContext(ProviderContext);
    const [counter, setCounter] = useState(0);
    const [input, setInput] = useState("");
    const [dataFromAudio, setDataFromAudio] = useState(false);
    const [initialChatInterview, setInitialChatInterview] = useState(latestinterviewchat);
    const [view, setShow] = useState(false);
    const [lastTimerValue, setLastTimerValue] = useState('00:00'); 
  
    useEffect(() => {
        setStart(false);
    }, [setStart]);


    const onSendMessage = (timerValue: any) => {
        const latestUserInfo = latestUserData;
        const cv_path = latestsession?.cvPath;
        console.log('Last Timer Value:', timerValue);

        handleInterview({ 
            input, 
            interview, 
            latestUserInfo,
            cv_path,
            counter,
            timerValue
        });
        setInput('');
        setCounter(counter < 5 ? counter + 1 : 0);
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
            <div className="markdown-content" style={{width: '40rem'}}>
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
                                <div className='chat_contain' key={index}>
                                    {message.role === "candidate" && (
                                        <div className='messagecandidate'>
                                            <CgProfile  size={40}/>
                                            <Text className="message-text">{message?.response}</Text>
                                        </div>
                                    )}
                                    {message.role === "assistant" && (
                                        <div className='messageassistant'>
                                            <img src={hr} alt="" className='profile-image' />
                                            <div className="message-response">
                                                <MarkdownContent content={message?.response} />
                                            </div>
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
                                    <CgProfile  size={40}/>
                                    <Text className="message-text">{message?.response}</Text>
                                </div>
                            )}
                            {message.role === "assistant" && (
                                <div className='messageassistant'>
                                    <img src={hr} alt="" className='profile-image' />
                                    <div className="message-response">
                                        <MarkdownContent content={message?.response} />                                   
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                    {loading && <Spin indicator={<img src={fade} alt="" className='h-10' />} />}
                </Card>
                
                <div>
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
                </div>
            </div>
        </>
    );
};

export default InterviewChat;