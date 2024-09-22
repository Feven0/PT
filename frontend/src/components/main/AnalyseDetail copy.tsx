import { useState, useContext } from 'react';
import { Button, Card, Typography } from 'antd';
import { ProviderContext } from '../../context/context';
import "../../styles/AnalyseDetail/analysedetail.css"

const { Title, Text } = Typography;

const AnalyseDetail = ({ realtimeanalysis, dblatestanalysis }) => {
  const analysis =  realtimeanalysis?.length !== 0? realtimeanalysis : dblatestanalysis;
  const [currentSlide, setCurrentSlide] = useState(0);
  const totalSlides = Math.ceil(analysis?.analysis?.section?.length / 2) + 1;
  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1 < totalSlides ? prev + 1 : prev));
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 >= 0 ? prev - 1 : prev));
  };

  const getSlideContent = (index) => {
    const start = index * 2;
    const end = start + 2;
    const sectionsToShow = analysis?.analysis?.section.slice(start, end);

    return sectionsToShow.map((item, idx) => (
      <Card key={idx} style={{ marginBottom: '16px' }}>
        <Title level={4} style={{ color: 'red' }}>{item.title}</Title>
        <Text>{item.description}</Text>
      </Card>
    ));
  };

  return (
    <>
      <div className='analyse-box' style={{  height: '60vh', padding: '16px', border: '1px solid #ddd', borderRadius: '8px', overflow: 'auto' }}>
        <Title level={3} style={{ textAlign: 'center' }}>{analysis?.analysis?.header}</Title>
        <div className='percentage-result'>
            <h1><small className='small'>Should i apply? </small>{analysis?.evaluation?.message}</h1>
            <h2><small className='small'>Match Score:</small> {analysis?.evaluation?.percentage}</h2>
        </div>
        <div style={{ margin: '16px 0' }}>
          {Array.from({ length: totalSlides }).map((_, index) => (
            <div key={index} style={{ display: currentSlide === index ? 'block' : 'none' }}>
              {getSlideContent(index)}
            </div>
          ))}
          <div style={{ display: currentSlide === totalSlides - 1 ? 'block' : 'none' }}>
            <Card>
              <Title level={4} style={{ color: 'red' }}>{analysis?.analysis?.overall?.title}</Title>
              <Text>{analysis?.analysis?.overall?.description}</Text>
            </Card>
          </div>

          <div style={{ display: currentSlide === totalSlides - 1 ? 'block' : 'none' }}>
            <Card>
              <Title level={4} style={{ color: 'red' }}>Resources</Title>
              {analysis?.analysis?.recommendation?.length >0 &&
                 (analysis?.analysis?.recommendation.map((item, index)=>(
                  <div className='analysis-resource' key={index}>
                  <div>
                    <a href={`https://${item.link}`} target="_blank" rel="noopener noreferrer">
                      {item.type}
                    </a>
                  </div>
                  <div>{item.resource}</div>                  
                </div>
                    
              )))}              
            </Card>
          </div>
        </div>

        <div style={{ textAlign: 'center' }}>
          {currentSlide > 0 && (
            <Button onClick={prevSlide} style={{ marginRight: '8px' }}>
              Previous
            </Button>
          )}
          {currentSlide < totalSlides - 1 && (
            <Button onClick={nextSlide}>
              Next
            </Button>
          )}
        </div>
      </div>
    </>
  );
};

export default AnalyseDetail;