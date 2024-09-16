import { useState, useEffect, useContext } from 'react';
import { Button, Card, Input, Spin, Typography } from 'antd';
import { CgProfile } from 'react-icons/cg';
import ReactMarkdown from 'react-markdown';
import { AudioRecorder } from '../main/index';
import { ProviderContext } from '../../context/context';
import { useParams } from 'react-router-dom';
import Api from '../../Services/Services';
import hr from '../../assets/hr.jpg';
import fade from '../../assets/fade-circles.svg';
import useMiddleSocket from '../../hooks/useMiddleSocket';
import '../../styles/InterviewChat/interviewchat.css'; 


const { TextArea } = Input;
const { Paragraph } = Typography;

const InterviewChat = ({ chat }) => {
    const { handleInterview, interview, loading } = useMiddleSocket();
    const { session, setStart, latestinterviewchat } = useContext(ProviderContext);
    const [counter, setCounter] = useState(0);
    const [input, setInput] = useState("");
    const [dataFromAudio, setDataFromAudio] = useState(false);
    const [view, setShow] = useState(false);
    const { jbId, sessionId } = useParams();

    useEffect(() => {
        setStart(false);
    }, [setStart]);

    const filterBySessionId = (sessionId) => {
        return session.filter(item => item.sessionId === sessionId);
    };

    const filterBySessionIdAndJobId = async () => {
        const datas = { sessionId: sessionId, jbId: jbId };
        const response = await Api.fetchSessionJob(datas);
        return response.data.latest_user_data;
    };

    const onSendMessage = async () => {
        const filteredData = filterBySessionId(sessionId);
        const cv_path = filteredData[0].cvPath;
        const latestUserInfo = await filterBySessionIdAndJobId();

        handleInterview({ input, interview, cv_path, latestUserInfo, counter });
        setInput('');
        setCounter(counter < 5 ? counter + 1 : 0);
    };

    const handler = (event) => {
        if (event.keyCode === 13) {
            onSendMessage();
        }
    };

    const handleDataFromAudio = (audioTranscript) => {
        setInput((prevInput) => prevInput + ' ' + audioTranscript);
    };

    const handleDataAudio = (data) => {
        setDataFromAudio(data);
    };

    const MarkdownContent = ({ content }) => {
        const formattedContent = content.replace(/---/g, ' ');
        return (
            <div className="markdown-content">
                <ReactMarkdown>{formattedContent}</ReactMarkdown>
            </div>
        );
    };

    return (
        <div className='container-chat'>
            <Card className='chat-card' title="Interview Chat" bordered >
                <div className='' style={{marginBottom: '10px'}}>
                    <Button onClick={() => setShow(!view)} type="primary">
                        {view ? 'Hide Previous' : 'Show Previous'}
                    </Button>
                </div>

                {view && (
                    <div>
                        {chat?.map((message, index) => (
                            <div key={index} className="message">
                                {message.role === "candidate" && (
                                    <div className='candidate-message'>
                                        <CgProfile size={40} />
                                        <Paragraph className="text-justify text-gray-700">{message?.response}</Paragraph>
                                    </div>
                                )}
                                {message.role === "assistant" && (
                                    <div className="assistant-message">
                                        <img src={hr} alt="HR" className='profile-image' />
                                        <div className="assistant-content">
                                            <MarkdownContent content={message?.response} />
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {interview?.map((message, index) => (
                    <div key={index} className="message">
                        {message.role === "candidate" && (
                            <div className='candidate-message'>
                                <CgProfile size={40} />
                                <Paragraph className="text-justify text-gray-700">{message?.response}</Paragraph>
                            </div>
                        )}
                        {message.role === "assistant" && (
                            <div className="assistant-message">
                                <CgProfile size={40} />
                                <div className="assistant-content">
                                    <MarkdownContent content={message?.response} />
                                </div>
                            </div>
                        )}
                    </div>
                ))}
                {loading && <Spin indicator={<img src={fade} alt="" className='loading-icon' />} />}
            </Card>

            <div className='input-container'>
                <TextArea
                    value={input}
                    placeholder="Put your answer here"
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handler}
                    rows={4}
                    className="input-textarea"
                />
                <div className='audio-controls'>
                    <AudioRecorder sendDataParent={handleDataAudio} sendDataToParent={handleDataFromAudio} />
                    {dataFromAudio && <Spin indicator={<img src={fade} alt="" className='loading-icon' />} />}
                </div>
            </div>
        </div>
    );
};

export default InterviewChat;