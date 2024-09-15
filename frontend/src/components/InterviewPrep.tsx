import { useCallback, useContext, useState } from 'react';
import { Button, Typography, Card } from 'antd';
import { InterviewChat } from './index';
import useMiddleSocket from '../hooks/useMiddleSocket';
import { ProviderContext } from '../context/context';
import '../styles/InterviewChat/interviewchat.css'; 
const { Text, Title } = Typography;

const InterviewPrep = () => {
  const { handleInterview, interview, loading, latestInterviewResponse } = useMiddleSocket();
  const {latestinterviewchat} = useContext(ProviderContext)
  const [open, setOpen] = useState('none');

  const handleReadyClick = (component) => {
    setOpen(component);
  };

  return (
    <>
      <div className="interview-container">
        {open === 'none' && (
          <Card className="interview-card" style={{ width: '100%', maxWidth: '600px', margin: 'auto', textAlign: 'center' }}>
            <Title level={3}>Want to get ready for the job?</Title>
            <Text className="text-gray-400" style={{ display: 'block', marginBottom: '16px' }}>
              How about having an interview?
            </Text>
            <Button 
              type="primary" 
              onClick={() => handleReadyClick('ready')} 
              className="interview-button"
              style={{ backgroundColor: '#f5222d', borderColor: '#f5222d' }}
            >
              Sure
            </Button>
          </Card>
        )}
      </div>

      {open === 'ready' && 
      <div className='interview-box'>
          <InterviewChat />
          <Card className='card_box' title='Performance'>
            <Card type="inner">
              <Title>Good Job!</Title>
              <Text className='interview_percent'>70%</Text>
            </Card>
          </Card>
      </div>
      
      }
    </>
  );
};

export default InterviewPrep;