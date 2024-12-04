import { Card, Statistic, Row, Col, Tag } from 'antd';
interface Data {
    statusData: any
}

const StatusDashboard: React.FC<Data> = ({ statusData }) => {
    return (
      <>
        {statusData && Object.keys(statusData).length > 0 && (
          <div style={{ padding: '16px' }}>
            <Card title="Session Overview" style={{ marginBottom: 16 }}>
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic title="Total Interview Sessions" value={statusData?.session_count} />
                </Col>
                <Col span={12}>
                  <Statistic title="Complete Interview Sessions" value={statusData?.complete_sessions} />
                </Col>
              </Row>
              <Row gutter={16} style={{ marginTop: 8 }}>
                <Col span={12}>
                  <Statistic title="Incomplete Interview Sessions" value={statusData?.incomplete_sessions} />
                </Col>
              </Row>
            </Card>
  
            <Card title="Job Profile Overview" style={{ marginBottom: 16 }}>
              <Statistic title="Total Job Profiles" value={statusData?.job_profile_count} />
              <div style={{ marginTop: 8 }}>
                <h4>Job Profile Frequency:</h4>
                {statusData?.job_profile_frequency?.map((item: any, index:any) => (
                  <Tag key={index} color="blue" style={{ marginBottom: 8 }}>
                    Job Role: {item?.job_title} - {item?.count} times
                  </Tag>
                ))}
              </div>
            </Card>
  
            <Card title="User Profile Overview" style={{ marginBottom: 16 }}>
              <Statistic title="Total User Profiles" value={statusData?.user_profile_count} />
              <div style={{ marginTop: 8 }}>
                <h4>User Profile Frequency:</h4>
                {statusData?.user_profile_frequency.map((item: any, index: any) => (
                  <Tag key={index} color="green" style={{ marginBottom: 8 }}>
                    Trainee: {item.name} - {item.count} times
                  </Tag>
                ))}
              </div>
            </Card>
          </div>
        )}
      </>
    );
  };
  
export default StatusDashboard;
  