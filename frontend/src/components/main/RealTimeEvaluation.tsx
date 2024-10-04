import { useState } from 'react';
import { Collapse, Dropdown, Button } from 'antd';
import '../../styles/InterviewChat/interviewchat.css'

const { Panel } = Collapse;

const RealTimeEvaluation = ({ evaluation }) => {
    const [isVisible, setIsVisible] = useState(false);
    const [visibleIndex, setVisibleIndex] = useState(null);

    const toggleVisibility = (index) => {
        setIsVisible(!isVisible);
        setVisibleIndex(index);
    };

    const overall = evaluation.overall || []
    const answerRelevancy = evaluation.answer_relevancy || [];
    const communicationSkills = evaluation.communication_skills || [];

    return (
        <div className='evaluation realtime-evaluation' 
            style={{ display: 'flex', gap: '2em', flexDirection: 'row-reverse', marginTop: '-4rem', marginBottom: '1rem', marginRight: '2.9rem' }}>
            
            <div
                className="hover-effect"
                title="Answer Relevance"
                style={{
                    backgroundColor: overall.relevance === 'strong' ? '#48f50354' : 
                                    overall.relevance === 'weak' ? '#ff000054' : 
                                    overall.relevance === 'medium' ? '#7fc6f554' : '#000000',
                    display: 'inline-block',
                    borderRadius: '5px 15px 5px 15px',
                    cursor: 'pointer',                  
                }}
                onClick={() => toggleVisibility(0)} 
            >
                 <div
                className=''
                style={{  
                    display: 'inline-block',
                    padding: '1px 1rem 1px 1rem',
                    fontWeight: 'bold',
                    color: overall.relevance === 'strong' ? '#02771b' : 
                    overall.relevance === 'weak' ? '#FF0000' : 
                    overall.relevance === 'medium' ? '#0797f7' : '#ffffff',
                    }}
                >
                    {overall.relevance}
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
                    <Collapse defaultActiveKey={['1']} style={{ marginTop: '1rem' }}>
                        <Panel 
                            header="Feedback" 
                            key="1" 
                            style={{ backgroundColor: '#f3f5f7', border: 'none', borderRadius: '1rem' }} 
                        >
                            <div className='message-text' style={{ padding: '1rem', color: '#6b6666', lineHeight: '1.5rem' }}>{overall.feedback}</div>
                        </Panel>
                        <Panel 
                            header="Other Metrics" 
                            key="2" 
                            style={{ backgroundColor: '#f3f5f7', border: 'none', borderRadius: '1rem' }}
                        >
                            <div style={{ padding: '1rem' }}>
                                {communicationSkills.map((skill, index) => (
                                    <div key={index} style={{ marginBottom: '0.5rem' }}>
                                        <strong style={{ fontSize: '1.1rem' }}>
                                            {skill.skill}: 
                                        </strong>
                                        <span style={{ marginLeft: '0.5rem', color: '#555' }}>{skill.level}</span>
                                    </div>
                                ))}
                            </div>
                        </Panel>
                    </Collapse>
                </div>
            )}
        </div>
    );
};

export default RealTimeEvaluation;