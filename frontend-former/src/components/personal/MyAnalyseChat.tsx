import { useState, useEffect, useContext } from 'react';
import { Button, Card, Input, Spin, Typography } from 'antd';
import ReactMarkdown from 'react-markdown';
import { useParams } from 'react-router-dom';
import Api from '../../Services/Services';
import fade from '../../assets/fade-circles.svg';
import useMiddleSocket from '../../hooks/useMiddleSocket';
import { ProviderContext } from '../../context/context';

const { TextArea } = Input;
const { Paragraph } = Typography;

const MyAnalyseChat = ({ chat }) => {
    const { loading, analysis, handleAnalyse } = useMiddleSocket();
    const { session, setStart } = useContext(ProviderContext);
    const [input, setInput] = useState("");
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
        handleAnalyse({ input, cv_path, latestUserInfo });
        setInput('');
    };

    const handler = (event) => {
        if (event.keyCode === 13) {
            onSendMessage();
        }
    };

    const MarkdownContent = ({ content }) => {
        const formattedContent = content.replace(/---/g, ' ');
        return (
            <div className="markdown-content text-justify p-2">
                <ReactMarkdown>{formattedContent}</ReactMarkdown>
            </div>
        );
    };

    return (
        <div>
            <Card className='shadow-xl mb-3' style={{ width: '30rem', maxHeight: '38rem', overflowY: 'auto' }}>
                <div className='flex justify-center mb-2'>
                    <Button onClick={() => setShow(!view)} type="primary">
                        {view ? 'Hide Previous' : 'Show Previous'}
                    </Button>
                </div>

                {view && (
                    <div>
                        {chat?.map((message, index) => (
                            <div key={index} className="mb-3">
                                {message.role === "user" && (
                                    <div className="text-gray-900 rounded p-2">
                                        {message?.response}
                                    </div>
                                )}
                                {message.role === "assistant" && (
                                    <Paragraph className="text-gray-500 bg-gray-50 p-3 mb-3">
                                        <MarkdownContent content={message?.response} />
                                    </Paragraph>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {analysis?.map((message, index) => (
                    <div key={index} className="mb-3">
                        {message.role === "user" && (
                            <div className="text-gray-900 rounded p-2">
                                {message?.response}
                            </div>
                        )}
                        {message.role === "assistant" && (
                            <Paragraph className="text-gray-500 bg-gray-50 p-3 mb-3">
                                <MarkdownContent content={message?.response} />
                            </Paragraph>
                        )}
                    </div>
                ))}

                {loading && <Spin indicator={<img src={fade} alt="" className='h-10' />} />}
            </Card>

            <TextArea
                className="w-full"
                rows={4}
                value={input}
                placeholder="Follow up question?"
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handler}
                style={{ resize: 'none', borderRadius: '8px' }}
            />
        </div>
    );
};

export default MyAnalyseChat;