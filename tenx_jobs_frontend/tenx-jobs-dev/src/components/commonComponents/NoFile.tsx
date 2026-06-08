import { useEffect, useState } from 'react'
import { Col, Row } from "antd"
import { loadingImg, loaderGif } from "../../assets"
import '../../styles/slidingCard.css'

export default function NoFile() {
  const [count, setCount] = useState(5);
  useEffect(() => {
    if (count > 0) {
      const timer = setTimeout(() => setCount(count - 1), 2000);
      return () => clearTimeout(timer);
    }
  }, [count]);

  return (
    <Row gutter={16} justify="center" style={{marginTop:"3rem"}}>
      <Col xs={24} lg={20} xxl={16} className="mobile-skills-header">
      <div className="d-flex-center full-width">
          <div 
              className="job-loading-handler-content">
            <img src={loadingImg} title="loader" width="150" height="130" style={{ background: "#fff" }} alt="Loading" />
            <span style={{
              marginTop:"1rem",
              marginLeft: "2rem"
            }}>
            <img src={loaderGif} title="loader" width={112} height={27} style={{ background: "#fff" }} alt="Loading" />
            </span>
              <p className="mt-16" style={{fontSize: "14px", textAlign:"center" }}>
              Learning is not attained by chance; it must be sought for with ardor and attended to with diligence
              </p>
            </div>
          </div>
      </Col>
    </Row>
  )
}

