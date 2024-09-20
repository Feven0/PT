import { Card, Row, Col, Flex } from 'antd'
import '../../styles/jobcard/jobcard.css'

const truncateSummary = (summary, wordLimit) => {
  const words = summary.split(' ');
  if (words.length > wordLimit) {
    return words.slice(0, wordLimit).join(' ') + '...'; 
  }
  return summary;
};

const JobCard = ({ item, matchDegree }) => {
  const limitedSummary = truncateSummary(item.summary, 3); 
  console.log("degree", matchDegree)

  return (
    <Card title={item.company_info_name} style={{ height: 'auto' }}>
      <Card type="inner" title={item.title} extra={<a className='link' target='_blank' rel='noopener noreferrer' href={item.applyLink}>More</a>}>
        <p>{limitedSummary}</p>
      </Card>

      <Flex justify='space-between'>
        <Row style={{marginTop: '2px'}}>
          <a className='link' href={`/job_detail/${item.job_profile_id}`}>Go</a>
        </Row>
        <Row style={{marginTop: '2px'}}>
          {matchDegree}
        </Row>
      </Flex>
    </Card>
  );
};

export default JobCard;