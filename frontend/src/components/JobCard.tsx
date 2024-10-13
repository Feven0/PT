import { Card, Row, Flex, Button } from 'antd'
import { useParams } from 'react-router-dom';
import { useState, useContext } from 'react';
import { ProviderContext } from '../context/context';
import Api from '../Services/Services';
import users from '../assets/mock-data/user_profiles.json';
import jobs from '../assets/mock-data/job_profile.json';
import '../styles/jobcard/jobcard.css'

const truncateSummary = (summary:any, wordLimit:any) => {
  const words = summary?.split(' ');
  if (words?.length > wordLimit) {
    return words?.slice(0, wordLimit).join(' ') + '...'; 
  }
  return summary;
};

interface JobCardProps {
  item:  any; 
  matchDegree: any 
}


const JobCard : React.FC<JobCardProps> = ({ item, matchDegree }) => {
  const {latestsession} = useContext<any>(ProviderContext)
  const { userId } = useParams<any>()
  // const [view, setView] = useState<any>(true)
  const [loading, setLoading] = useState<any>(false);
  const [sessionCreated, setSessionCreated] = useState<any>(false);
  const limitedSummary = truncateSummary(item?.purpose, 3); 
  const filteredUser = users.filter(match => match?.user_profile_id === parseInt(userId as any));

  const session_create = async(job_profile_id: any) => {
      // setView(false);
      setLoading(true);
      const filteredJob = jobs.filter(match => match.job_profile_id === job_profile_id);
      const data = {
        jobId: job_profile_id,
        userId: userId,
        name: filteredUser[0]?.name,
        cvJson: filteredUser[0],
        jbJson: filteredJob[0]
      };
      console.log(data)

      try {
          const response = await Api.sessionCreate(data);
          console.log(response)
          localStorage.setItem("JobId", job_profile_id)
          setSessionCreated(true);
      } catch (error) {
          console.error("Error creating session:", error);
      } finally {
          setLoading(false);
          // setView(true);
      }
  }


  return (
    <Card style={{ height: 'auto' }}>
      <Card type="inner" title={item.role} extra={<a className='link' target='_blank' rel='noopener noreferrer'
       href={item['attributes.apply_link']}>More</a>}>
        <p>{limitedSummary}</p>
      </Card>

      <Flex justify='space-between'>
          <Row style={{ marginTop: '2px' }}>
            {sessionCreated || 
              (parseInt(latestsession?.userId) === parseInt(userId || '0') && (parseInt(latestsession?.jobId) === item?.job_profile_id)) ? (
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