import { Row, Col, Typography } from 'antd';
import { GeneralAggregateCountStats } from "../../../types/statsTypes";
const { Text, Title } = Typography;

export default function CountStats({
  maleCount = 0,
  femaleCount = 0,
  excellentPerformers = 0,
  goodPerformers = 0,
  poorPerformers = 0,
}: GeneralAggregateCountStats) {
  return (
      <Row gutter={8} className="mt-16"  justify="center" style={{padding:"0.5rem"}}>
        <Col xs={24} lg={20}>
        <Row gutter={8} justify="center" style={{border:"1px solid whitesmoke", padding:"0.5rem"}}>
        <Col xs={8} sm={6} md={4}>
          <StatItem label="Male" value={maleCount} />
        </Col>
        <Col xs={8} sm={6} md={4}>
          <StatItem label="Female" value={femaleCount} />
        </Col>
        <Col xs={8} sm={6} md={4}>
          <StatItem label="Excellent" value={excellentPerformers} />
        </Col>
        <Col xs={8} sm={6} md={4}>
          <StatItem label="Good" value={goodPerformers} />
        </Col>
        <Col xs={8} sm={6} md={4}>
          <StatItem label="Poor" value={poorPerformers} />
        </Col>
        </Row>
        </Col>
      </Row>
  );
}

function StatItem({ label, value }: { label: string; value: number }) {
  return (
    <Col span={8} style={{ textAlign: 'center' }}>
      <Text type="secondary">{label}</Text>
      <Title level={2}>{value}</Title>
    </Col>
  );
}
