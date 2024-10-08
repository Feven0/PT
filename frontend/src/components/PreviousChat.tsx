import { useState, useContext } from 'react';
import { Button,Typography } from 'antd';
import {RealTimeEvaluation, OverallFeedbackModal, LoadingSpinner} from './index'
import { CgProfile } from 'react-icons/cg'
import hr from '../assets/hr.jpg';
import ReactMarkdown from 'react-markdown';
import { ProviderContext } from '../context/context';
import "../styles/InterviewChat/interviewchat.css"
import Api from '../Services/Services';

const { Paragraph } = Typography;

interface Content {
    content: any
}

const PreviousChat = () => {
    const {latestsession} = useContext<any>(ProviderContext)
    const [viewloading, setShow] = useState(false);
    const [previous, setChatHistory] = useState([])
    const [fetch, setFetch] = useState(false)

    const MarkdownContent: React.FC<Content> = ({ content }) => {
        const formattedContent = content?.replace(/---/g, ' ');
        return (
            <div className="markdown-content" style={{width: '100%'}}>
                <ReactMarkdown>{formattedContent}</ReactMarkdown>
            </div>
        );
    };

    const fetchChatHistory = async () => {
        if(latestsession !== undefined){
          setShow(true)
          let job_id = localStorage.getItem("jobId")
          const data = {
            userId: latestsession?.userId,
            sessionId: latestsession?.sessionId, 
            jobId: job_id
        }
          const response = await Api.fetchChatHistory(data)
          setChatHistory(response?.data)
          setShow(false)
          setFetch(true)
        }
    }

  return (
    <>
        <div className="btn-hide">
            {fetch? (
                <Button 
                    onClick={() => setFetch(!fetch)} 
                    style={{ backgroundColor: 'antiquewhite', borderColor: 'antiquewhite', color: 'darkslategray' }}
                >
                    Hide
                </Button>
            ):(
                <Button 
                onClick={fetchChatHistory} 
                style={{ backgroundColor: 'antiquewhite', borderColor: 'antiquewhite', color: 'darkslategray' }}
            >
                Previous  {viewloading && (<LoadingSpinner style={{ marginLeft: '5px' }} />)}
            </Button>
            )}
            
        </div>

        {fetch &&(
            <div style={{ marginBottom: '2rem' }}>
              {previous?.map((outerMessage:any, index:any) => (
                    <div key={index} style={{ marginBottom: '2rem' }}> 
                        {outerMessage?.chathistory?.map((innerMessage:any, innerIndex:any) => (
                            <div className='chat_contain' key={innerIndex}>
                                {innerMessage?.candidate?.response  && innerMessage.candidate.response !== "null"  && (
                                    <div className='messagecandidate' style={{ backgroundColor: '#ffffff', border: '2px solid #fcf8f8' }}>
                                        <Paragraph style={{ margin: 0 }}>
                                            <CgProfile size={40} />
                                            <p className="message-text" style={{ fontSize: '1rem', lineHeight: '2rem'}}>    
                                                {innerMessage.candidate.response}
                                            </p>
                                        </Paragraph>
                                    </div>
                                )}

                                {innerMessage?.assistant?.realtime_evaluation !== "null" && innerMessage?.assistant?.realtime_evaluation !== undefined && (
                                    <RealTimeEvaluation evaluation={innerMessage.assistant.realtime_evaluation} />
                                )}

                                {innerMessage?.assistant?.response && innerMessage.assistant.response !== "null" && (
                                    <div className='messageassistant'>
                                        <img src={hr} alt="" className='profile-image' />
                                        <Paragraph style={{ margin: 0, textAlign: 'justify', color: '#606060', fontSize: '1rem' }}>
                                            <MarkdownContent content={innerMessage.assistant.response.start_message} />
                                            <div style={{ color: 'black' }}>
                                                <MarkdownContent content={innerMessage.assistant.response.question} />
                                            </div>
                                            <MarkdownContent content={innerMessage.assistant.response.end_message} />
                                        </Paragraph>
                                    </div>
                                )}
                            </div>
                        ))}
                            {/* Check for overall evaluation after mapping chat history */}
                            {outerMessage?.chathistory?.length > 0 && (
                                outerMessage.chathistory[outerMessage.chathistory.length - 1]?.assistant?.overall_evaluation && (
                                    <OverallFeedbackModal 
                                        metricsData={outerMessage.chathistory[outerMessage.chathistory.length - 1]?.assistant?.metrics}
                                        evaluationData={outerMessage.chathistory[outerMessage.chathistory.length - 1]?.assistant?.overall_evaluation}
                                    />
                                )
                            )}
                    </div>
                ))} 
            </div>
         )}
    </>
  )
}

export default PreviousChat