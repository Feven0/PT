import { Card, Typography, Collapse, Row, Col } from 'antd';
import '../../styles/Status/allstatus.css'; 

const { Title, Text } = Typography;
const { Panel } = Collapse;


const AllStatus = () => {
  const metricsData = [
    {
      "title": "performance_change",
      "description": "Your performance has improved slightly, with the performance percentage increasing from 45% to 50%. However, the overall rating has improved to 3 stars, indicating that while progress has been made, further improvement is necessary."
    },
    {
      "title": "confidence_change",
      "description": "Your confidence level has increased from Low to High, suggesting a positive shift in your self-assurance during interviews."
    },
    {
      "title": "engagement_change",
      "description": "Your engagement has improved from Disengaged to Somewhat Engaged, indicating a better connection with the interview process."
    },
    {
      "title": "irrelevant_answers_change",
      "description": "The percentage of irrelevant answers has decreased from 60% to 55%, showing a slight improvement in the relevance of your responses."
    },
    {
      "title": "relevant_answers_change",
      "description": "The percentage of relevant answers has increased from 40% to 45%, indicating that you are providing more pertinent information in your responses."
    },
    {
      "title": "overall_performance",
      "description": "Overall, you have shown improvement in several areas, including confidence and engagement. However, you still need to enhance your technical knowledge and detail orientation to achieve a higher performance rating."
    },
    {
      "title": "time_management",
      "description": "You have demonstrated effective time management, passing 5 out of 5 timed questions, which indicates you are managing your response time well."
    },
    {
      "skill": {
        "technical": {
          "title": "technical_knowledge",
          "previous": "Low",
          "current": "Low",
          "recommendation": "Focus on gaining practical experience in computer vision techniques."
        },
        "detail": {
          "title": "detail_orientation",
          "previous": "Low",
          "current": "Low",
          "recommendation": "Practice providing detailed responses to behavioral questions."
        }
      }
    }
  ]
  
  return (
      <div className="status-container">
        <Title level={2} className="status-title">Evaluation of Candidate's Interview Progress</Title>
  
        <Card className="status-card">
          <Collapse accordion>
            {metricsData.map(item => {
              if (item.skill) {
                return (
                  <Panel header="Skills Improvement" key="skills">
                    <Row gutter={16}>
                      <Col span={12}>
                        <Title level={4}>{item.skill.technical.title.replace(/_/g, ' ')}</Title>
                        <Text>Previous: {item.skill.technical.previous}</Text><br />
                        <Text>Current: {item.skill.technical.current}</Text><br />
                        <Text>Recommendation: {item.skill.technical.recommendation}</Text>
                      </Col>
                      <Col span={12}>
                        <Title level={4}>{item.skill.detail.title.replace(/_/g, ' ')}</Title>
                        <Text>Previous: {item.skill.detail.previous}</Text><br />
                        <Text>Current: {item.skill.detail.current}</Text><br />
                        <Text>Recommendation: {item.skill.detail.recommendation}</Text>
                      </Col>
                    </Row>
                  </Panel>
                );
              }
              return (
                <Panel header={item.title.replace(/_/g, ' ')} key={item.title}>
                  <Text>{item.description}</Text>
                </Panel>
              );
            })}
          </Collapse>
        </Card>
      </div>
    );
  };
  
  export default AllStatus;