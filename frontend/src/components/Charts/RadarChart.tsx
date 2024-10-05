import { Radar } from "@ant-design/plots";
import { Col, Row } from "antd";

const RadarChart = ({data}) => {

  const doubleArray = Array.isArray(data) && Array.isArray(data[0]) ? data : [data];

  const datas = doubleArray?.map((competencies, index) => {
    const type = `Interview ${index + 1}`;
    return competencies?.map(item => ({
        ...item,
        sfia_level: parseInt(item.sfia_level, 10), 
        type: type
    }));
  }).flat();


  const config = {
    data: datas,
    xField: "name",
    yField: "sfia_level",
    colorField: 'type',
    shapeField: 'smooth',
    area: {
      style: {
        fillOpacity: 0.5,
      },
    },
    point: {
        size: 2,
    },
    style: {
      lineWidth: 2,
    },
  };

  return (
    <Row>
      <Col style={{width: '25rem', height: '25rem' }}>
        <Radar {...config}/>
      </Col>
    </Row>
  );
};

export default RadarChart;