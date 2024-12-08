import { useState, useEffect } from 'react'
import Api from '../Services/Services'
import { ProgressBarChart, UserOverall } from './index'
import { Row, Col } from 'antd';

const AllProgress = () => {
    const [progress, setAllProgress] = useState({});
    const [status, setStatus] = useState([]);
    const [refresh, setRefresh] = useState(0);


    const fetchOverall = async() => {
        const data = {
          all_user_id: 1959
        }
        const response = await Api.UserAllSessionMetrics(data)
        const responsestatus = await Api.UserStatus(data)
        console.log("useroveralldata", responsestatus.data)
        setStatus(responsestatus.data)
        setAllProgress(response.data)
      }
  
      useEffect(() => {
        fetchOverall()
          const intervalId = setInterval(() => {
            setRefresh((prev) => prev + 1);
          }, 500000);
  
          return () => clearInterval(intervalId); 
      }, [refresh])
  
  return (
    <div style={{
      display: 'flex', 
      justifyContent: 'center',  
      alignItems: 'center',    
      backgroundColor: '#f0f2f5',
      margin: '0px 3rem 0px 3rem'
    }}>
        <Row gutter={50}>
          <Col span={16}>
            <UserOverall data={status}/>
          </Col>
          <Col 
            style={{
              display: 'flex', 
              gap: '40px', 
              justifyContent: 'center', 
              marginTop: '3rem', 
              backgroundColor:'#ffffff'}}
          >
              <ProgressBarChart data={progress}/>
          </Col>
        </Row>
    </div>
  )
}

export default AllProgress