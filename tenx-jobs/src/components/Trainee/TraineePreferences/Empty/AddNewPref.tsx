import { Button, Col, Row } from "antd"
import { PlusOutlined } from '@ant-design/icons'
import { no_experience } from "../../../../assets"
import '../../../../styles/preference.css'

type PrefProps = {
  desc: string;
  showAddButton: () => void;
}

export default function AddNewPref({desc, showAddButton}: PrefProps) {
  return (
    <Row gutter={16} justify="center">
      <Col xs={24} lg={12} className="text-center">
        <div>
            <img src={no_experience} alt="No Job Keywords" className="no-data-img" />
            <p className="no-data-description">{desc} </p>
            <Button style={{ borderColor: '#FF4405'}} 
            className="mt-16 dark-orange-bg white-color" icon={<PlusOutlined />} onClick={showAddButton}>
              New
            </Button>
        </div>
      </Col>
    </Row>
  )
}
