import { useState } from 'react';
import { Collapse } from 'antd';
import '../styles/InterviewChat/interviewchat.css';

const { Panel } = Collapse;

interface Data {
    evaluation: any
}

const RealTimeEvaluation: React.FC<Data> = ({ evaluation }) => {
    const [isVisible, setIsVisible] = useState(false);

    const toggleVisibility = () => {
        setIsVisible(!isVisible);
    };

    const overall = evaluation?.overall || [];

    // Check if evaluation is an array or an object
    const isArray = Array.isArray(evaluation);

    return (
        <div className='evaluation realtime-evaluation' 
            style={{ display: 'flex', gap: '2em', flexDirection: 'row-reverse', marginTop: '-4rem', marginBottom: '2rem', marginRight: '2.9rem' }}>
            
            <div
                className="hover-effect"
                title="Answer Relevance"
                style={{
                    backgroundColor: overall?.relevance === 'strong' ? '#48f50354' : 
                                    overall?.relevance === 'weak' ? '#ff000054' : 
                                    overall?.relevance === 'medium' ? '#7fc6f554' : '#000000',
                    display: 'inline-block',
                    borderRadius: '5px 15px 5px 15px',
                    cursor: 'pointer',                  
                }}
                onClick={() => toggleVisibility()} 
            >
                 <div
                className=''
                style={{  
                    display: 'inline-block',
                    padding: '1px 1rem 1px 1rem',
                    fontWeight: 'bold',
                    color: overall?.relevance === 'strong' ? '#02771b' : 
                    overall?.relevance === 'weak' ? '#FF0000' : 
                    overall?.relevance === 'medium' ? '#0797f7' : '#ffffff',
                    }}
                >
                    {overall?.relevance}
                </div>
            </div>

            {isVisible && (
                <div style={{
                    textAlign: 'justify', 
                    width: '30rem',
                    padding: '1.5rem',
                    borderRadius: '1rem',
                    color: '#333',
                    backgroundColor: '#f9f9f9', 
                    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)', 
                }}>
                    {isArray ? (
                        <Collapse defaultActiveKey={['1']} style={{ marginTop: '1rem' }}>
                            {evaluation.map((item: any, index: number) => (
                                <Panel 
                                    header={`Question ${index + 1}`} 
                                    key={index + 1} 
                                    style={{ backgroundColor: '#f3f5f7', border: 'none', borderRadius: '1rem' }}
                                >
                                    <div style={{ padding: '1rem', color: '#6b6666', lineHeight: '1.5rem' }}>
                                        <strong>Question:</strong> {item?.question}
                                    </div>
                                    <div style={{ padding: '1rem', color: '#6b6666', lineHeight: '1.5rem' }}>
                                        <strong>Evaluation:</strong> {item?.evaluation}
                                    </div>
                                </Panel>
                            ))}
                        </Collapse>
                    ) : (
                        <Collapse defaultActiveKey={['1']} style={{ marginTop: '1rem' }}>
                            <Panel 
                                header="Feedback" 
                                key="1" 
                                style={{ backgroundColor: '#f3f5f7', border: 'none', borderRadius: '1rem' }} 
                            >
                                <div className='message-text' style={{ padding: '1rem', color: '#6b6666', lineHeight: '1.5rem' }}>
                                    {overall?.feedback}
                                </div>
                            </Panel>
                        </Collapse>
                    )}
                </div>
            )}
        </div>
    );
};

export default RealTimeEvaluation;
