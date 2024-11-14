import { Typography } from 'antd';
import { RealTimeEvaluation } from './index'
import { CgProfile } from 'react-icons/cg'
import hr from '../assets/hr.jpg';
import ReactMarkdown from 'react-markdown';
import "../styles/InterviewChat/interviewchat.css"

const { Paragraph } = Typography;
interface Data {
    previous: any
}

interface Content {
    content: any
}


const PreviousChat: React.FC<Data> = ({previous}) => {
    console.log("covens",  previous)

    const MarkdownContent: React.FC<Content> = ({ content }) => {
        const formattedContent = content?.replace(/---/g, ' ');
        return (
            <div className="markdown-content" style={{width: '100%'}}>
                <ReactMarkdown>{formattedContent}</ReactMarkdown>
            </div>
        );
    };


  return (
    <>
        <div style={{ marginBottom: '2rem' }}>
            {previous.map((outerMessage: any, index: any) => {
                const message = outerMessage.attributes.attributes.message; 

                return (
                    <div className='chat_contain' key={index}>
                        {/* Candidate message rendering */}
                        {message.user_type === 'candidate' && message.content.response && (
                            <div className='messagecandidate' style={{ backgroundColor: '#ffffff', border: '1px solid #fcf8f8' }}>
                                <Paragraph style={{ margin: 0 }}>
                                    <CgProfile size={40} />
                                    <p className="message-text" style={{ fontSize: '1rem', lineHeight: '2rem' }}>
                                        {message.content.response}
                                    </p>
                                </Paragraph>
                            </div>
                        )}

                        {/* Assistant evaluation rendering */}
                        {message.user_type === 'assistant' && (
                            <div>
                                {message.content.realtime_evaluation && (
                                    <RealTimeEvaluation evaluation={message.content.realtime_evaluation} />
                                )}

                                {/* Assistant's response */}
                                {message.content.full_response && (
                                    <div className='messageassistant' style={{ marginTop: '1rem' }}>
                                        <img src={hr} alt="" className='profile-image' />                                    
                                        <Paragraph style={{ margin: 0, textAlign: 'justify', color: '#606060', fontSize: '1rem' }}>
                                        {message?.content?.time_limit !== "null" && (
                                            <div>
                                                time limit: {message?.content?.time_limit}
                                            </div> 
                                        )}
                                            <MarkdownContent content={message.content.full_response} />
                                        </Paragraph>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    </>
  )
}

export default PreviousChat