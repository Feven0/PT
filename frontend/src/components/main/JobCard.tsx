import { Card, Row, Col, Flex, Button } from 'antd'
import { useParams } from 'react-router-dom';
import { useState } from 'react';
import Api from '../../Services/Services';
import users from '../../assets/mock-data/user_profiles.json';
import '../../styles/jobcard/jobcard.css'

const truncateSummary = (summary, wordLimit) => {
  const words = summary.split(' ');
  if (words.length > wordLimit) {
    return words.slice(0, wordLimit).join(' ') + '...'; 
  }
  return summary;
};

const JobCard = ({ item, matchDegree }) => {
  const { userId } = useParams()
  const [view, setView] = useState(true)
  const [loading, setLoading] = useState(false);
  const [sessionCreated, setSessionCreated] = useState(false);
  const limitedSummary = truncateSummary(item.summary, 3); 
  const filteredUserMatch = users.filter(match => match.user_profile_id === parseInt(userId as any));


  const session_create = async() => {
      setView(false);
      setLoading(true);
      const data = {
        email: "test@gmail.com",
        userId: userId,
        name: filteredUserMatch[0]?.name,
        cvJson: filteredUserMatch[0]
      };

      try {
        const response = await Api.sessionCreate(data);
        console.log("session_created", response?.data);
        setSessionCreated(true);
      } catch (error) {
        console.error("Error creating session:", error);
      } finally {
        setLoading(false);
        setView(true);
      }
  }

  return (
    <Card title={item.company_info_name} style={{ height: 'auto' }}>
      <Card type="inner" title={item.title} extra={<a className='link' target='_blank' rel='noopener noreferrer' href={item['attributes.apply_link']}>More</a>}>
        <p>{limitedSummary}</p>
      </Card>

      <Flex justify='space-between'>
        <Row style={{marginTop: '2px'}}>
          {/* <a className='link' href={`/job_detail/${userId}/${item.job_profile_id}`}>Go</a> */}
          {sessionCreated ? (
            <a className='link' href={`/job_detail/${userId}/${item.job_profile_id}`}>
              <Button className='job-btn' style={{ marginTop: '5px' }}>
                Go
              </Button>
            </a>
          ) : (
            <Button 
              className='job-btn' 
              style={{ marginTop: '5px' }}
              onClick={session_create}
              disabled={loading}
            >
              {loading ? 'wait...' : 'Start'}
            </Button>
          )}
        </Row>
        <Row style={{marginTop: '5px'}}>
          {matchDegree}
        </Row>
      </Flex>
    </Card>
  );
};

export default JobCard;