import { Radar } from "@ant-design/plots";
import { Col, Row } from "antd";

interface Data {
  data: any;
}

const RadarRealtime: React.FC<Data> = ({ data }) => {
  const datas = Array.isArray(data) ? data.map((item) => ({
    name: item.name,
    sfia_level: parseInt(item.sfia_level, 10),
  })) : [];

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

export default RadarRealtime;