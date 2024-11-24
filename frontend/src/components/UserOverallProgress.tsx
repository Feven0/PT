import { useState, useEffect } from 'react'
import Api from '../Services/Services'
import { useParams } from 'react-router-dom'
import { ProgressBarChart } from './index'

const AllProgress = () => {
    const {userId} = useParams()
    const [progress, setAllProgress] = useState({});
    const [refresh, setRefresh] = useState(0);


    const fetchOverall = async() => {
        const data = {
          alluser: userId
        }
        const response = await Api.UserAllSessionMetrics(data)
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
        gap: '40px', 
        justifyContent: 'center', 
        marginTop: '3rem', 
        backgroundColor:'#ffffff'}}
    >
        <ProgressBarChart data={progress}/>
    </div>
  )
}

export default AllProgress