import { Card } from 'antd'
import '../../styles/jobcard/jobcard.css'

const MyJobCard = ({item, selectedCvId}) => {
  return (
    <>
      <Card className='card' type="inner" title={item.name} extra={<a className='link' href={`/main_activity/${item.id}/${selectedCvId}`}>More</a>}>
        <p>Lorem ipsum dolor, sit amet consectetur adipisicing elit...</p>
      </Card>
    </>
  )
}

export default MyJobCard