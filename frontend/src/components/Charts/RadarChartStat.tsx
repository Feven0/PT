import { Radar } from "@ant-design/plots";
import { Col, Row } from "antd";

interface Data {
  data: any
}

const RadarChartStat: React.FC<Data> = ({ data }) => {
  const transformData = (data: any) => {
    return [
      { value: data?.avg_confidence, name: 'Confidence' },
      { value: data?.avg_clarity, name: 'Clarity' },
      { value: data?.avg_engagment, name: 'Engagement' },
    ];
  };

  const transformedData = transformData(data);

  const config = {
    data: transformedData,
    xField: "name",
    yField: "value",
    area: {
      style: {
        fill: 'rgba(24, 144, 255, 0.3)', 
        stroke: '#1890ff',
        lineWidth: 2, 
      },
    },
    point: {
      size: 5,
      style: {
        fill: '#1890ff',
        stroke: '#fff', 
        lineWidth: 2, 
      },
    },
    line: {
      style: {
        stroke: '#1890ff', 
        lineWidth: 2,
      },
    },
    smooth: true,
  };

  return (
    <Row style={{ backgroundColor: '#f1eded27', padding: '1rem', borderRadius: '8px' }}>
      <Col style={{ width: '25rem', height: '25rem', marginTop: '4rem' }}>
        <Radar {...config} />
      </Col>
      <Col style={{ marginLeft: '2rem', marginTop: '4rem', textAlign: 'left' }}>
        {/* <h3 style={{ color: '#1890ff' }}>Average Scale Standards</h3> */}
        <ul style={{ listStyleType: 'none', padding: '1rem', backgroundColor:'#ffffff', borderRadius: '10px' }}>
          <li style={{ margin: '0.5rem 0', fontSize: '13px', color: 'lightcoral' }}>
            <strong>1.00 - 1.49</strong> (Poor)
          </li>
          <li style={{ margin: '0.5rem 0', fontSize: '13px', color: '#ffa500' }}>
            <strong>1.50 - 1.99</strong> (Between Poor and Good)
          </li>
          <li style={{ margin: '0.5rem 0', fontSize: '13px', color: 'lightgreen' }}>
            <strong>2.00 - 2.49</strong> (Good)
          </li>
          <li style={{ margin: '0.5rem 0', fontSize: '13px', color: '#32cd32' }}>
            <strong>2.50 - 2.99</strong> (Between Good and Excellent)
          </li>
          <li style={{ margin: '0.5rem 0', fontSize: '13px', color: '#008000' }}>
            <strong>3.00</strong> (Excellent)
          </li>
        </ul>
      </Col>
    </Row>
  );
};

export default RadarChartStat;