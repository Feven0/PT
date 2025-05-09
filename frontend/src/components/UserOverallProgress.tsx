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
        const data_status = {
            "run_stage": "dev-prod",
            "all_user_id": 1959,
            "cursor": {
                      "page": 1, 
                      "pageSize": 20,
                      "page_count": 1,
                      "page_size": 20,
                      "query": {},
                      "total": 58
                  },
            "filter": {},
            "limit": 7,
            "since": 7,
            "information_level": "minimal",
            "return_skip": false
          }
        const response = await Api.UserAllSessionMetrics(data)
        const responsestatus = await Api.UserStatus(data_status)
        console.log("engagement", responsestatus?.data)
        const stat = responsestatus?.data?.jobs;
        let data_stat = [];
        if (stat) {
          data_stat = stat[0]?.data
        }
        setStatus(data_stat)
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