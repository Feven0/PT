import { useState } from 'react';
import { Table, Col, Card, Typography } from 'antd';
import {LineChart} from './index'
import '../styles/Status/metrics.css'

const { Text } = Typography;


const ProgressIndicator = ({ currentValue, maxValue }) => {
  const percentage = (currentValue / maxValue) * 100;

  return (
      <div style={{ display: 'flex', alignItems: 'center' }}>
          <strong style={{ marginLeft: '0.4rem', marginRight: '0.5rem' }}>
              {currentValue} out of {maxValue}
          </strong>
          <div style={{ width: '100px', height: '4px', backgroundColor: '#e0e0e0', borderRadius: '2px' }}>
              <div
                  style={{
                      width: `${percentage}%`,
                      height: '100%',
                      backgroundColor: '#39b54a', 
                      borderRadius: '2px',
                  }}
              />
          </div>
      </div>
  );
};

const StarRating = ({ rating }) => {
    const totalStars = 4;
    const stars = Array.from({ length: totalStars }, (_, index) => (
        <span
            key={index}
            className={`star ${index < rating ? 'filled' : ''}`} 
        >
            ★
        </span>
    ));

    return <div className="star-rating">{stars}</div>;
};

const Metrics = ({metricsData}) => {
    const [expandedImprovementKeys, setExpandedImprovementKeys] = useState([]);
    const [expandedStrengthKeys, setExpandedStrengthKeys] = useState([]);

    const onImprovementRowClick = (record) => {
      const newExpandedKeys = expandedImprovementKeys.includes(record.key)
          ? expandedImprovementKeys.filter(key => key !== record.key)
          : [...expandedImprovementKeys, record.key];
      setExpandedImprovementKeys(newExpandedKeys);
  };

  const onStrengthRowClick = (record) => {
      const newExpandedKeys = expandedStrengthKeys.includes(record.key)
          ? expandedStrengthKeys.filter(key => key !== record.key)
          : [...expandedStrengthKeys, record.key];
      setExpandedStrengthKeys(newExpandedKeys);
  };

  const columns = [
    {
        dataIndex: 'skill',
        key: 'skill',
        render: (text, record) => (
            <span onClick={() => onImprovementRowClick(record)} style={{ cursor: 'pointer'}}>
                {text}
            </span>
        )
    }
];

const strength_columns = [
  {
      dataIndex: 'skill',
      key: 'skill',
      render: (text, record) => (
          <span onClick={() => onStrengthRowClick(record)} style={{ cursor: 'pointer'}}>
              {text}
          </span>
      )
  }
];

const improvementData = metricsData?.areas_of_improvement?.map((item, index) => ({
    key: `improvement-${index}`,
    skill: item.skill,
    description: item.description
})) || [];

const strengthData = metricsData?.strength?.map((item, index) => ({
    key: `strength-${index}`,
    skill: item.skill,
    description: item.description
})) || [];


    const performanceData = metricsData?.performance.reduce((acc, metric) => {
        acc[metric.name] = metric.level || metric.term; 
        return acc;
    }, {});

    const timeData = metricsData?.time_management
    const relevancy = metricsData?.relevancy

    return (
        <div className=''>
          <Col>
            <div style={{ display:'flex', justifyContent: 'center', gap: '10px', fontSize:'1.3rem' }}>
               {metricsData?.message}
            </div>
            <div style={{ display:'flex', justifyContent: 'center', gap: '10px', marginBottom: '20px' }}>
                <StarRating rating={metricsData?.rating} />
            </div>

            <Col>
              <Card title="Answer Relevance">
                <LineChart relevancy={relevancy} />
              </Card>
            </Col>

            <Col>
              <Card title="Time Management">
                  <Text className="card-text">
                    <small>Questions Completed on Time:</small> 
                  <ProgressIndicator currentValue={timeData?.pass} maxValue={timeData?.pass + timeData?.fail} /> 
                  </Text>
                  <Text className="card-text">
                    <small>Questions Not Completed on Time:</small> 
                      <ProgressIndicator currentValue={timeData?.fail} maxValue={timeData?.pass + timeData?.fail} /> 
                  </Text>
              </Card>
            </Col>

            <Col>
              <Card title="Confidence">
              <Text>
                <small>Level -</small>
                <strong style={{marginLeft: '0.4rem'}}>{performanceData.confidence_level}</strong>                
              </Text>
              </Card>
            </Col>

            <Col>
                <Card title="Areas of Improvement">
                    <Table
                        columns={columns}
                        dataSource={improvementData}
                        pagination={false}
                        expandedRowRender={record => (
                            <ul>
                                <li>{record.description}</li>
                            </ul>
                        )}
                        expandedRowKeys={expandedImprovementKeys}
                        onExpand={(expanded, record) => {
                            if (expanded) {
                                setExpandedImprovementKeys([...expandedImprovementKeys, record.key]);
                            } else {
                                setExpandedImprovementKeys(expandedImprovementKeys.filter(key => key !== record.key));
                            }
                        }}
                    />
                </Card>
              </Col>


              <Col>
                  <Card title="Strength">
                      <Table
                          columns={strength_columns}
                          dataSource={strengthData}
                          pagination={false}
                          expandedRowRender={record => (
                              <ul>
                                  <li>{record.description}</li>
                              </ul>
                          )}
                          expandedRowKeys={expandedStrengthKeys}
                          onExpand={(expanded, record) => {
                              if (expanded) {
                                  setExpandedStrengthKeys([...expandedStrengthKeys, record.key]);
                              } else {
                                  setExpandedStrengthKeys(expandedStrengthKeys.filter(key => key !== record.key));
                              }
                          }}
                      />
                  </Card>
              </Col>
          </Col>
        </div>
    );
};

export default Metrics;