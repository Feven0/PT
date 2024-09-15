import { Card } from 'antd'
import '../styles/jobcard/jobcard.css'

const JobCard = ({item}) => {
  return (
    <>
      <Card title={item.company}>
        <Card type="inner" title={item.name} extra={<a className='link' href={`/job_detail/${item.id}`}>More</a>}>
          <p>Lorem ipsum dolor, sit amet consectetur adipisicing elit...</p>
        </Card>
      </Card>
    </>
  )
}

export default JobCard