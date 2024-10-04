import {useState, useEffect} from 'react'
import { MyInterviewChat } from './index'
import { PercentageCard } from '../main/index';
import useMiddleSocket from '../../hooks/useMiddleSocket';
// import '../../styles/InterviewChat/interviewchat.css'; 
import { Button, Typography, Card, Row } from 'antd';


const MyInterview = ({chat}) => {
  const { handleInterview, interview, loading,  latestInterviewResponse } = useMiddleSocket();
  const [open, setOpen] = useState('none');
  const handleReadyClick = (component: any) => {
    setOpen(component);
  };

  const { Text, Title } = Typography;

  return (
    <div className="relative">
     {open === 'none' &&
      <Card className="interview-card" style={{ margin: 'auto', textAlign: 'center' }}>
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
      }

      
      {open === 'ready' &&
        <Row className='chat_container'>
          <MyInterviewChat chat={chat}/>
          <PercentageCard/>
        </Row>
      } 
    </div>
  )
}

export default MyInterview