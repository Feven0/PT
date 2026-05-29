import { useEffect } from 'react';
import { Card, Col, Row } from "antd";

//Styles and assets
import { loadingImg, loaderGif } from "../../assets"
import '../../styles/slidingCard.css'

type JobLoadingProps = {
  count: number;
  setCount: (count: number) => void;
};

export default function JobLoading({ count, setCount }: JobLoadingProps) {

  useEffect(() => {
    if (count > 0) {
      const timer = setTimeout(() => setCount(count - 1), 2000);
      return () => clearTimeout(timer);
    }
  }, [count]);

  return (
    <Row gutter={8} justify="center" className="mt-16" style={{height:"100vh"}}>
      <Col xs={24} lg={20} style={{ textAlign: 'center'}}>
        <Card className="job-loading-handler"
          title={<span/>}
          style={{ width:"100%"}}>
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
              <p className="mt-16" style={{fontSize: "14px" }}>
              Learning is not attained by chance; it must be sought for with ardor and attended to with diligence
              </p>
            </div>
          </div>
        </Card>
      </Col>
    </Row>
  )
}
