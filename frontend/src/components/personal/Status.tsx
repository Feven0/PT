import { Table, Collapse, Card, Progress, Typography, Row, Col, Dropdown, Menu } from 'antd';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { useState } from 'react';
import '../../styles/Status/status.css'

const { Panel } = Collapse;

const { Title, Text } = Typography;

const data = {
    "evaluation": {
        "performance_message": "Needs Improvement",
        "performance_percent": "50%",
        "confidence_level": "Low",
        "answer_relevance": {
            "relevant_answers": "55%",
            "irrelevant_answers": "45%"
        },
        "communication_skills": {
            "clarity": "Somewhat Clear",
            "engagement": "Somewhat Engaged"
        },
        "time_management": {
            "adherence": "71%",
            "time_taken": {
                "pass": "2",
                "failed": "1"
            },
            "status": "For question 1, time_taken (01:03) exceeds time_limit (2:00), for question 2, time_taken (00:31) is within time_limit (2:00), for question 3, time_taken (00:37) is within time_limit (2:00)."
        },
        "areas_of_improvement": [
            {
                "skill": "Detail Orientation",
                "description": "The candidate should provide more detailed responses, especially when discussing their experiences and projects, to better illustrate their skills and contributions."
            },
            {
                "skill": "Problem-Solving Articulation",
                "description": "The candidate should improve on articulating specific challenges faced in previous roles and the steps taken to overcome them, which would demonstrate their problem-solving capabilities more effectively."
            }
        ],
        "strengths": [
            {
                "skill": "Interest in AI",
                "description": "The candidate showed a strong interest in AI, which is essential for the role and indicates a passion for the field."
            }
        ],
        "overall_performance": {
            "rating": "2 stars",
            "comments": "The candidate has potential but needs to work on providing more comprehensive answers and demonstrating their skills more effectively during interviews."
        }
    }
}

const Status = () => {
  const { evaluation } = data;

  const convertPercentToNumber = (percentStr) => {
    return parseFloat(percentStr) || 0; 
  }

  const barData = [
      { name: 'Relevant Answers', value: convertPercentToNumber(evaluation.answer_relevance.relevant_answers) },
      { name: 'Irrelevant Answers', value: convertPercentToNumber(evaluation.answer_relevance.irrelevant_answers) }
  ];

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
          title: 'Skill',
          dataIndex: 'skill',
          key: 'skill',
          render: (text, record) => (
              <span onClick={() => onImprovementRowClick(record)} style={{ cursor: 'pointer', color: 'blue' }}>
                  {text}
              </span>
          )
      }
  ];

  const improvementData = evaluation?.areas_of_improvement.map((item, index) => ({
      key: `improvement-${index}`,
      skill: item.skill,
      description: item.description
  })) || [];

  const strengthData = evaluation?.strengths.map((item, index) => ({
      key: `strength-${index}`,
      skill: item.skill,
      description: item.description
  })) || [];



  return (
      <div style={{ padding: '20px' }}>
          <Title level={2}>Candidate Interview Evaluation</Title>
          <Row gutter={16}>
              <Col span={12}>
                  <Card title="Performance Overview">
                      <Text className="card-text">{evaluation.performance_message}</Text>
                      <Progress percent={parseInt(evaluation.performance_percent)} />
                      <Text strong className="card-text">Performance: {evaluation.performance_percent}</Text>
                      <Text strong className="card-text">Confidence Level: {evaluation.confidence_level}</Text>
                      {/* <Text strong className="card-text">Answer Relevance: {evaluation.answer_relevance}</Text> */}
                  </Card>
              </Col>
              <Col span={12}>
                    <Card title="Time Management">
                        <Text className="card-text">Adherence: {evaluation.time_management.adherence}</Text>
                        <Text className="card-text">Questions Completed on Time: {evaluation.time_management.time_taken.pass}</Text>
                        <Text className="card-text">Questions Not Completed on Time: {evaluation.time_management.time_taken.failed}</Text>
                    </Card>
              </Col>
          </Row>

          <Row gutter={16} style={{ marginTop: '20px' }}>
              <Col span={12}>
                  <Card title="Communication-Skills">
                      <Text className="card-text">Clarity: {evaluation.communication_skills.clarity}</Text>
                      <Text className="card-text">Engagement: {evaluation.communication_skills.engagement}</Text>
                  </Card>
              </Col>
              <Col span={12}>
                  <Card title="Answer Relevance Visualization">
                    <BarChart width={400} height={100} data={barData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#82ca9d" />
                    </BarChart>
                  </Card>
              </Col>
          </Row>

          <Row gutter={16} style={{ marginTop: '20px' }}>
              <Col span={12}>
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
              <Col span={12}>
              <Card title="Strengths">
                    <Table
                        columns={columns}
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
          </Row>

          <Row gutter={16} style={{ marginTop: '20px' }}>
            <Col span={24}>
                <Card title="Overall Performance Rating">
                    <div className='analysis-rating' style={{ display: 'flex', alignItems: 'center' }}>
                        <Text style={{ fontSize: '24px', fontWeight: 'bold', color: '#ff4d4f', marginRight: '8px' }}>
                            {evaluation.overall_performance.rating}
                        </Text>
                        <Text>{evaluation.overall_performance.comments}</Text>
                    </div>
                </Card>
            </Col>
         </Row>
      </div>
  );
};

export default Status;