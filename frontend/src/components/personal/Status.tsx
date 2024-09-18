import { Card, Progress, Typography, Row, Col, Dropdown, Menu } from 'antd';
import { PieChart, Pie, Cell } from 'recharts';
import '../../styles/Status/status.css'

const { Title, Text } = Typography;

const data = {
  evaluation: {
      performance_message: "Good",
      performance_percent: "60%",
      confidence_level: "Moderate",
      answer_relevance: "59%",
      communication_skills: {
          clarity: "Somewhat Clear",
          engagement: "Disengaged"
      },
      time_management: {
          adherence: "85%",
          time_taken: {
            pass: 4,
            failed: 1,
          }
      },
      areas_of_improvement: [
          {
              skill: "RAG",
              description: "Improve understanding of retrieval-augmented generation techniques."
          },
          {
              skill: "Python",
              description: "Enhance coding skills in Python, focusing on libraries."
          }
      ],
      strengths: [
          {
              skill: "Communication Skill",
              description: "Articulated thoughts clearly in some responses."
          },
          {
              skill: "Technical Knowledge",
              description: "Demonstrated solid understanding of AI concepts."
          }
      ],
      overall_performance: {
          rating: "3 stars",
          comments: "The candidate demonstrated good knowledge but needs to improve clarity."
      }
  }
};

const Status = () => {
  const { evaluation } = data;

  const pieData = [
      { name: 'Relevant Answers', value: 59 },
      { name: 'Irrelevant Answers', value: 41 }
  ];


  const areasMenu = (
      <Menu>
          {evaluation.areas_of_improvement.map((area, index) => (
              <Menu.Item key={index}>
                  <Text strong>{area.skill}: </Text>
                  <Text>{area.description}</Text>
              </Menu.Item>
          ))}
      </Menu>
  );

  const strengthsMenu = (
      <Menu>
          {evaluation.strengths.map((strength, index) => (
              <Menu.Item key={index}>
                  <Text strong>{strength.skill}: </Text>
                  <Text>{strength.description}</Text>
              </Menu.Item>
          ))}
      </Menu>
  );

  return (
      <div style={{ padding: '20px' }}>
          <Title level={2}>Candidate Evaluation</Title>
          <Row gutter={16}>
              <Col span={12}>
                  <Card title="Performance Overview">
                      <Text className="card-text">{evaluation.performance_message}</Text>
                      <Progress percent={parseInt(evaluation.performance_percent)} />
                      <Text strong className="card-text">Performance: {evaluation.performance_percent}</Text>
                      <Text strong className="card-text">Confidence Level: {evaluation.confidence_level}</Text>
                      <Text strong className="card-text">Answer Relevance: {evaluation.answer_relevance}</Text>
                  </Card>
              </Col>
              <Col span={12}>
                    <Card title="Time Management">
                        <Text className="card-text">Adherence: {evaluation.time_management.adherence}</Text>
                        <Text className="card-text">Questions Passed: {evaluation.time_management.time_taken.pass}</Text>
                        <Text className="card-text">Questions Failed: {evaluation.time_management.time_taken.failed}</Text>
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
                      <PieChart width={200} height={200}>
                          <Pie data={pieData} cx={100} cy={100} outerRadius={80} fill="#8884d8" label>
                              {pieData.map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={index === 0 ? '#82ca9d' : '#ff4d4f'} />
                              ))}
                          </Pie>
                      </PieChart>
                  </Card>
              </Col>
          </Row>

          <Row gutter={16} style={{ marginTop: '20px' }}>
              <Col span={12}>
                  <Card title="Areas of Improvement">
                      <Dropdown overlay={areasMenu} trigger={['click']}>
                          <a onClick={e => e.preventDefault()}>
                             View
                          </a>
                      </Dropdown>
                  </Card>
              </Col>
              <Col span={12}>
                  <Card title="Strengths">
                      <Dropdown overlay={strengthsMenu} trigger={['click']}>
                          <a onClick={e => e.preventDefault()}>
                              View
                          </a>
                      </Dropdown>
                  </Card>
              </Col>
          </Row>

          <Row gutter={16} style={{ marginTop: '20px' }}>
              <Col span={24}>
                  <Card title="Overall-Performance">
                      <Text>Rating: {evaluation.overall_performance.rating}</Text>
                      <Text style={{ marginLeft: '8px' }}>{evaluation.overall_performance.comments}</Text>
                  </Card>
              </Col>
          </Row>
      </div>
  );
};

export default Status;