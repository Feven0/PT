import { useState, useEffect } from 'react';
import { Input, Row, Col } from "antd";
import { JobCard } from '../components/index';
import data from '../assets/mock-data/job_match.json';
import jobs from '../assets/mock-data/job_profile.json';
import { useParams } from 'react-router-dom';
import '../styles/jobs/jobs.css';


interface MatchDegrees {
  [key: string]: number; 
}


const Jobs = () => {
  const {userId} = useParams()
  
  const [searchQuery, setSearchQuery] = useState<any>('');

  const filteredMatches = data.filter((match:any) => match.user_profile_id === parseInt(userId as any));
  const jobProfileIds = filteredMatches.map((match:any) => match.job_profile_id);
  const filteredJobs = jobs.filter((job:any) => jobProfileIds.includes(job.job_profile_id));
  const { Search } = Input;

  const matchDegrees: MatchDegrees = {}; 

  filteredMatches.forEach((match:any) => {
    matchDegrees[match.job_profile_id] = match.match_attributes_overall_match_degree;
  });

  // Function to get match degree for a specific job
  const getMatchDegree = (jobId:any) => {
    const match = filteredMatches.find(match => match.job_profile_id === jobId);
    return match ? match.match_attributes_overall_match_degree : null;
  };

  useEffect(() => {
    // localStorage.removeItem("JobId")
    if(userId !== undefined){
        localStorage.setItem("userId", userId)
    }
  },[userId])


  return (
    <>
      <Row justify="end" className='search' style={{ marginTop: '50px' }}>
        <Col>
          <Search 
            placeholder="input search text" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            enterButton 
            style={{ width: '30rem' }}
          />
        </Col>
      </Row>
      <Row gutter={16} style={{ margin: '40px' }}>
        {filteredJobs?.map(job => (
          <Col span={6} key={job.job_profile_id}>
            <JobCard 
              item={job} 
              matchDegree={getMatchDegree(job.job_profile_id)}
            />
          </Col>
        ))}
      </Row>
    </>
  );
};

export default Jobs;
