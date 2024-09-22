import { useContext } from 'react';
import { Card, Typography, Collapse } from 'antd';
import { ProviderContext } from '../../context/context';
import "../../styles/AnalyseDetail/analysedetail.css";

const { Title, Text } = Typography;
const { Panel } = Collapse;

const AnalyseDetail = ({ realtimeanalysis, dblatestanalysis }) => {
  const analysis = realtimeanalysis?.length !== 0 ? realtimeanalysis : dblatestanalysis;
  console.log("anlsy", realtimeanalysis?.length !== 0 || dblatestanalysis?.length !== 0, realtimeanalysis?.length !== 0 , dblatestanalysis?.length !== 0, realtimeanalysis, dblatestanalysis)
  return (
    <>
      {(realtimeanalysis?.length !== 0 || dblatestanalysis?.length !== 0) &&(
        <div className='analyse-box' style={{ height: '70vh', boxShadow: '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', padding: '16px', border: '1px solid #ddd', borderRadius: '8px', overflow: 'auto' }}>
          <Title level={3} style={{ textAlign: 'center' }}>{analysis?.analysis?.header}</Title>
          <div className='percentage-result'>
            <h1><small className='small'>Should I apply? </small>{analysis?.analysis?.evaluation?.message}</h1>
            <h2><small className='small'>Match Score:</small> {analysis?.analysis?.evaluation?.percentage}</h2>
          </div>

          <Collapse accordion>
            {analysis?.analysis?.section.map((item, index) => (
              <Panel header={item.title} key={index}>
                <Card style={{ marginBottom: '16px' }}>
                  <Text>{item.description}</Text>
                </Card>
              </Panel>
            ))}
            
            <Panel header={analysis?.analysis?.overall?.title} key="overall">
              <Card style={{ marginBottom: '16px' }}>
                <Text>{analysis?.analysis?.overall?.description}</Text>
              </Card>
            </Panel>

            <Panel header="Resources" key="resources">
            <Card>
              {analysis?.analysis?.recommendation?.length > 0 &&
                analysis?.analysis?.recommendation.map((item, index) => (
                  <div className='analysis-resource' key={index}>
                    <div>
                      <a href={`https://${item.link}`} target="_blank" rel="noopener noreferrer">
                        {item.type}
                      </a>
                    </div>
                    <div>{item.resource}</div>
                  </div>
                ))}
            </Card>
            </Panel>
          </Collapse>
        </div>
      )}
    </>
  );
};

export default AnalyseDetail;