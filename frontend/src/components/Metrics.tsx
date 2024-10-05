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
    const totalStars = 5;
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
    const evaluation_metrics = {
      "evaluation": {
        "performance": [
          {
            "name": "performance",
            "term": "Average",
            "reason": "Responses were satisfactory but lacked depth and specific examples, particularly in technical discussions."
          },
          {
            "name": "performance_level",
            "level": "60",
            "reason": "The overall performance indicated a basic understanding of AI concepts, but several gaps were present in technical details and teamwork examples."
          },
          {
            "name": "confidence_level",
            "level": "Average",
            "reason": "The candidate appeared unsure during responses, particularly when asked to elaborate on technical experiences."
          },
          {
            "name": "rating",
            "level": "2",
            "reason": "The rating reflects a need for improvement in providing detailed and confident responses."
          }
        ],
        "areas_of_improvement": [
          {
            "skill": "Technical Skills",
            "description": "You should improve your ability to discuss specific technologies and methodologies used in your projects. Providing detailed examples of your work with machine learning models, including challenges faced and solutions implemented, would enhance your responses."
          },
          {
            "skill": "Team Collaboration",
            "description": "You need to provide more comprehensive examples of teamwork experiences. Instead of vague statements, share specific situations that highlight your contributions, the challenges faced, and the outcomes achieved."
          }
        ],
        "strength": [
          {
            "skill": "Problem-Solving",
            "description": "You demonstrated a genuine passion for tackling complex problems and a willingness to learn, which is a strong foundation for a role in AI engineering."
          },
          {
            "skill": "Communication Skills",
            "description": "You communicated your background and experiences clearly, showing an ability to articulate your qualifications effectively, even if more detail was needed."
          }
        ],
        "time_management": {
          "fail": 0,
          "pass": 8
        },
        "relevancy": [
          {
            "index": 1,
            "level": "90",
            "reason": "The response was highly relevant, addressing both educational qualifications and practical experience in AI, which are crucial for the role."
          },
          {
            "index": 2,
            "level": "90",
            "reason": "Your background in machine learning and experience with AI projects directly relate to the responsibilities of the Senior AI Engineer position."
          },
          {
            "index": 3,
            "level": "80",
            "reason": "Most of your response was relevant, but it lacked specific examples of projects and challenges faced."
          },
          {
            "index": 4,
            "level": "30",
            "reason": "The response only mentioned the use of PyTorch without any specific examples or details about projects, making it largely irrelevant to the question."
          },
          {
            "index": 5,
            "level": "30",
            "reason": "The response only vaguely addresses teamwork without providing context or specifics about the experience."
          },
          {
            "index": 6,
            "level": "30",
            "reason": "The answer provided was very vague and did not adequately address the question about teamwork and collaboration."
          },
          {
            "index": 7,
            "level": "30",
            "reason": "The response only vaguely addresses teamwork without providing substantial context or detail."
          },
          {
            "index": 8,
            "level": "30",
            "reason": "The response only vaguely addresses teamwork without providing substantial context or detail."
          }
        ]
      }
    }

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