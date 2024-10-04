import { Card, Row, Col, Typography } from 'antd';
import resumeData from '../../assets/resume.json'
import '../../styles/DisplayResume/displayresume.css'

const { Title, Text } = Typography;
const DisplayResume = () => {
  return (
        <div className="resume-container">
          <Card className="resume-card" style={{ maxHeight: '90vh' }}>
            <Title level={2} className="resume-name">AI Engineer</Title>
            <Text className="resume-overview">{resumeData.overview}</Text>
    
            <Row gutter={16}>
              <Col >
                <Title level={4}>Key Responsibilities</Title>
                {Object.entries(resumeData.keyResponsibilities).map(([key, responsibilities]) => (
                  <div key={key}>
                    <Title level={5}>{key.replace(/([A-Z])/g, ' $1').trim()}</Title>
                    <ul>
                      {responsibilities.map((resp, index) => (
                        <li key={index}>
                          <Text>{resp.point}</Text>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </Col>
            </Row>
            
            <Row>
            <Col>
                <Title level={4}>Qualifications</Title>
                <Text strong>Educational Background:</Text>
                <Text>{resumeData.qualifications.educationalBackground}</Text>
                <Title level={5}>Technical Skills</Title>
                <ul>
                  {resumeData.qualifications.technicalSkills.map((skill, index) => (
                    <li key={index}>
                      <Text>{skill.point}</Text>
                    </li>
                  ))}
                </ul>
                <Title level={5}>Experience</Title>
                <ul>
                  {resumeData.qualifications.experience.map((exp, index) => (
                    <li key={index}>
                      <Text>{exp.point}</Text>
                    </li>
                  ))}
                </ul>
                <Title level={5}>Soft Skills</Title>
                <ul>
                  {resumeData.qualifications.softSkills.map((skill, index) => (
                    <li key={index}>
                      <Text>{skill.point}</Text>
                    </li>
                  ))}
                </ul>
                <Title level={5}>Preferred Qualifications</Title>
                <ul>
                  {resumeData.qualifications.preferredQualifications.map((qual, index) => (
                    <li key={index}>
                      <Text>{qual.point}</Text>
                    </li>
                  ))}
                </ul>
              </Col>
            </Row>
            <Title level={4}>What We Offer</Title>
            <ul>
              {resumeData.whatWeOffer.map((offer, index) => (
                <li key={index}>
                  <Text>{offer.point}</Text>
                </li>
              ))}
            </ul>
            
            <Text className="resume-call-to-action">{resumeData.callToAction}</Text>
          </Card>
        </div>
      );
    
}

export default DisplayResume