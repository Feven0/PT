import { Card, Row, Col, Flex, Button } from 'antd'
import { useParams } from 'react-router-dom';
import { useState, useEffect, useContext } from 'react';
import { ProviderContext } from '../../context/context';
import Api from '../../Services/Services';
import users from '../../assets/mock-data/user_profiles.json';
import jobs from '../../assets/mock-data/job_profile.json';
import '../../styles/jobcard/jobcard.css'

const truncateSummary = (summary, wordLimit) => {
  const words = summary?.split(' ');
  if (words?.length > wordLimit) {
    return words?.slice(0, wordLimit).join(' ') + '...'; 
  }
  return summary;
};

const JobCard = ({ item, matchDegree }) => {
  const {latestsession} = useContext(ProviderContext)
  const { userId } = useParams()
  const [view, setView] = useState(true)
  const [loading, setLoading] = useState(false);
  const [sessionCreated, setSessionCreated] = useState(false);
  const limitedSummary = truncateSummary(item?.purpose, 3); 
  const filteredUser = users.filter(match => match?.user_profile_id === parseInt(userId as any));

  const session_create = async(job_profile_id) => {
      setView(false);
      setLoading(true);
      const filteredJob = jobs.filter(match => match.job_profile_id === job_profile_id);
      // console.log("myg", filteredJob)
      const data = {
        jobId: job_profile_id,
        userId: userId,
        name: filteredUser[0]?.name,
        cvJson: filteredUser[0],
        jbJson: filteredJob[0]
      };
      console.log("myg", data)
      
      try {
          const response = await Api.sessionCreate(data);
          console.log("session_created", response?.data);
          localStorage.setItem("jobId", job_profile_id)
          setSessionCreated(true);
      } catch (error) {
          console.error("Error creating session:", error);
      } finally {
          setLoading(false);
          setView(true);
      }
  }


  return (
    <Card style={{ height: 'auto' }}>
      <Card type="inner" title={item.role} extra={<a className='link' target='_blank' rel='noopener noreferrer' href={item['attributes.apply_link']}>More</a>}>
        <p>{limitedSummary}</p>
      </Card>

      <Flex justify='space-between'>
          <Row style={{ marginTop: '2px' }}>
            {sessionCreated || 
              (parseInt(latestsession?.userId) === parseInt(userId) && (parseInt(latestsession?.jobId) === item?.job_profile_id)) ? (
              <a className='link' href={`/job_detail/${userId}/${item.job_profile_id}`}>
                <Button className='job-btn' style={{ marginTop: '5px' }}>
                  Go
                </Button>
              </a>
            ) : (
              <Button 
                className='job-btn' 
                style={{ marginTop: '5px' }}
                onClick={() => session_create(item.job_profile_id)}
                disabled={loading}
              >
                {loading ? 'wait...' : 'Start'}
              </Button>
            )}
          </Row>

          <Row style={{ marginTop: '5px' }}>
            {matchDegree}
          </Row>
      </Flex>
    </Card>
  );
};

export default JobCard;