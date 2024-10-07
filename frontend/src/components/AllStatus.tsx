import {useContext, useState, useEffect} from 'react';
import { Row, Col } from 'antd';
import { BarChart, LineChartOverall, RadarChart, SankeyChart, SankeyTime, LoadingIndicator } from './index'; 
import Api from '../Services/Services';
import { ProviderContext } from '../context/context';


const AllStatus = () => {
  const {latestsession} = useContext(ProviderContext);
  const [refresh, setRefresh] = useState(0);
  const [overall, setOverall] = useState({});


    const fetchOverall = async() => {
      const job_id = localStorage.getItem("jobId")
      const data = {
        userId: latestsession?.userId,
        sessionId: latestsession?.sessionId, 
        jobId: job_id
      }
      const response = await Api.overallmetrics(data)
      setOverall(response.data)
    }

    useEffect(() => {
      fetchOverall()
        const intervalId = setInterval(() => {
          setRefresh((prev) => prev + 1);
        }, 500000);
  
        return () => clearInterval(intervalId); 
    }, [refresh])

    const layoutStyle = {
      maxWidth: '90rem', 
      margin: '0 auto', 
      padding: '20px', 
      backgroundColor: '#ffffff',
    };

    const charts = [
      { title: 'Clarity', component: <SankeyChart communication={overall?.overall_clarity}/> },
      { title: 'Engagement', component: <SankeyChart communication={overall?.overall_engagement}/> },
      { title: 'Time Management', component: <SankeyTime time={overall?.overall_time_management}/> },
    ];

    const [currentIndex, setCurrentIndex] = useState(0);

    const nextChart = () => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % charts.length);
    };

    const prevChart = () => {
      setCurrentIndex((prevIndex) => (prevIndex - 1 + charts.length) % charts.length);
    };
    console.log("oooooooooooooer", overall?.error !== undefined)

    return (
      <>
          {(overall == undefined  || overall !== undefined || overall?.error === undefined) ?
            <div>
              <LoadingIndicator message={'Fetching Metrics...'}/>
            </div>
          :
            <div style={layoutStyle}>
              <h1>
                Overall Progress
              </h1>

              <div style={{marginLeft: '5rem'}}>
                {/* First Row */}
                <div style={{marginBottom: '2rem'}}>
                  <Row style={{  display: 'flex', margin: '0 4rem 0 4rem', gap:'2rem'}}>
                      <Col style={{backgroundColor: '#f1eded27', borderRadius: '3rem', padding:'0 4rem 0 4rem', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'}}>
                          <h3 style={{color: '#d1cccb'}}>Competency</h3>
                          <RadarChart data={overall?.overall_competency} />
                      </Col>
                      <Col style={{backgroundColor: '#ebe8e865', borderRadius: '3rem', padding:'0 4rem 0 4rem', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'}}>
                          <h3 style={{color: '#d1cccb'}}>Answer Relevancy</h3>
                          <LineChartOverall relevancy={overall?.overall_performance} />
                      </Col>
                  </Row>
                </div>            

                {/* Second Row */}
                <div>
                  <Row style={{ display: 'flex', margin: '0 4rem 0 4rem', gap: '2rem' }}>
                      <Col style={{backgroundColor: '#f1eded27', borderRadius: '3rem', padding:'0 1.5rem 0 1.5rem', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'}}>
                        <h3 style={{color: '#d1cccb'}}>Confidence</h3>
                        <BarChart confidenceData={overall?.overall_confidence} />
                      </Col>
                      
                      <Col style={{ backgroundColor: '#f1eded27', borderRadius: '3rem', padding: '0 2.5rem 0 2.5rem', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>                 
                            <div>
                              <h3 style={{color: '#d1cccb'}}>{charts[currentIndex].title}</h3>
                            </div>
                            <div style={{ marginTop: '1rem', display: 'flex', cursor: 'pointer' }}>
                                  <p onClick={prevChart} disabled={currentIndex === 0}>
                                      &lt;
                                  </p>
                                  <p onClick={nextChart} style={{ marginLeft: '1rem' }}>
                                      &gt;
                                  </p>
                            </div>
                          </div>
                              {charts[currentIndex].component}
                      </Col>
                  </Row>
                </div>
              </div>
            </div>
          }

      </>
    );
};

export default AllStatus;