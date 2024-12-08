import { Spin, Typography } from 'antd';
import fade from '../assets/fade-circles.svg';
import hr from '../assets/hr.jpg';
import { CgProfile } from 'react-icons/cg'
import {RealTimeEvaluation,LoadingSpinner} from './index'
import "../styles/InterviewChat/interviewchat.css"
import ReactMarkdown from 'react-markdown';
import { useState } from 'react';
import Api from '../Services/Services';
import useMiddleSocket from '../hooks/useMiddleSocket';
const { Paragraph } = Typography;

interface Data {
    interview?: any; 
}

interface MarkdownContentProps {
    content?: string; 
}

const Messages: React.FC<Data> = ({interview}) => {
    const { loading } = useMiddleSocket();
    const [clarifications, setClarifications] = useState<any>({}); 
    const [load, setLoading] = useState<any>({}); 
    const [clickCount, setClickCount] = useState<any>({}); 


    const MarkdownContent: React.FC<MarkdownContentProps> =  ({ content }) => {
        const formattedContent = content?.replace(/---/g, ' ');
        return (
            <div className="markdown-content" style={{width: '100%'}}>
                <ReactMarkdown>{formattedContent}</ReactMarkdown>
            </div>
        );
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

  return (
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
  )
}

export default Messages