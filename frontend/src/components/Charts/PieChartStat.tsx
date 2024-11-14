import { Pie } from '@ant-design/plots';
import { Col, Row } from 'antd';

interface Data {
  data: any
}

const PieChartStat : React.FC<Data> = ({ data }) => {
  const chartData = [
    { type: 'On-time', value: data?.avg_time_management?.average_pass_rate },
    { type: 'Late', value: data?.avg_time_management?.average_fail_rate }
  ];

  const config = {
    data: chartData,
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    label: {
      type: 'inner',
      offset: '-50%', 
      content: '{percentage}%',
      style: {
        fontSize: 16,
        textAlign: 'center',
      },
    },
    interactions: [{ type: 'element-active' }],
    color: ['lightgreen', 'lightcoral'], 
  };

  return (
    <Row style={{ backgroundColor: '#f1eded27', padding: '1rem' }}>
      <h3>Time Management</h3>
      <Col style={{ width: '25rem', height: '25rem' }}>
        <Pie {...config} />
      </Col>
    </Row>
  );
};

export default PieChartStat;