import { useState, useEffect, useContext } from 'react';
import { Input, Button, Card, Typography, Spin, Row } from 'antd';
import fade from '../../assets/fade-circles.svg';
import useMiddleSocket from '../../hooks/useMiddleSocket';
import { ProviderContext } from '../../context/context';
import ReactMarkdown from 'react-markdown';

const { Text, Title, Paragraph } = Typography;

const AnalyseChat = ({ latestanalysischat, latestUserData }) => {
  const { loading, analysis, handleAnalyse } = useMiddleSocket();
  const { latestsession, setStart } = useContext(ProviderContext);
  const [input, setInput] = useState('');
  const [show, setShow] = useState(false);
  const [previousChatAnalysis, setInitialChatAnalysis] = useState(latestanalysischat);

  useEffect(() => {
    setStart(false);
  }, []);

  const onSendMessage = () => {
    const latestUserInfo = latestUserData;
    const cv_path = latestsession?.cvPath;
    handleAnalyse({ input, cv_path, latestUserInfo });
    setInput('');
  };

  const handleKeyDown = (event) => {
    if (event.keyCode === 13) {
      onSendMessage();
    }
  };

  const MarkdownContent = ({ content }) => {
    const formattedContent = content.replace(/---/g, ' ');
    return (
      <div className="markdown-content text-justify p-2 px-6 font-lato leading-loose">
        <ReactMarkdown>{formattedContent}</ReactMarkdown>
      </div>
    );
  };

  return (
    <>
        <Row>
            <button 
            onClick={() => setShow(!show)}
            className='btn-load'>
                {!show? 'Previous' : 'Hide'}
            </button>
        </Row>

        <Card style={{ maxHeight: '40rem', maxWidth: '35rem', overflowY: 'auto' }}>
            {show ?
                <div style={{ marginBottom: '16px' }}>
                {previousChatAnalysis?.map((message, index) => (
                <div key={index}>
                    {message.role === "user" && (
                    <div className="mt-1 mb-3">
                        <Card style={{ backgroundColor: '#f0f0f0', borderRadius: '8px' }}>
                        <Paragraph style={{ margin: 0, color: '#1a1a1a' }}>
                            {message?.response}
                        </Paragraph>
                        </Card>
                    </div>
                    )}
                    {message.role === "assistant" && (
                    <div className="mx-2">
                        <Card style={{ backgroundColor: '#fafafa', borderRadius: '8px' }}>
                        <Paragraph style={{ margin: 0, color: '#606060' }}>
                            <ReactMarkdown>{message?.response}</ReactMarkdown>
                        </Paragraph>
                        </Card>
                    </div>
                    )}
                </div>
                ))}
                {loading && <Spin indicator={<img src={fade} alt="" className='h-10' />} />}
            </div>
                :
                <div style={{ marginBottom: '16px' }}>
                {analysis?.map((message, index) => (
                <div key={index}>
                    {message.role === "user" && (
                    <div className="mt-1 mb-3">
                        <Card style={{ backgroundColor: '#f0f0f0', borderRadius: '8px' }}>
                        <Paragraph style={{ margin: 0, color: '#1a1a1a' }}>
                            {message?.response}
                        </Paragraph>
                        </Card>
                    </div>
                    )}
                    {message.role === "assistant" && (
                    <div className="mx-2">
                        <Card style={{ backgroundColor: '#fafafa', borderRadius: '8px' }}>
                        <Paragraph style={{ margin: 0, color: '#606060' }}>
                            <ReactMarkdown>{message?.response}</ReactMarkdown>
                        </Paragraph>
                        </Card>
                    </div>
                    )}
                </div>
                ))}
                {loading && <Spin indicator={<img src={fade} alt="" className='h-10' />} />}
            </div>
            }

        <Input.TextArea
            value={input}
            placeholder="Follow up question?"
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={3}
            style={{ marginBottom: '8px' }}
        />
        <Button type="primary" onClick={onSendMessage} style={{ width: '100%' }}>
            Send
        </Button>
        </Card>
    </>
  );
};

export default AnalyseChat;