
import { Card, Col, Row, Tabs } from 'antd'
import { FileTextOutlined, FileOutlined, } from "@ant-design/icons";

//Components
import CreateTextAsset from "../../components/Trainee/Asset/CreateTextAsset";
import CreateFileAsset from "../../components/Trainee/Asset/CreateFileAsset";

const { TabPane } = Tabs

export default function CreateNewDirectAsset() {

    return (
            <Row gutter={[16, 16]} justify="center" className="mt-32">
                <Col xs={24} lg={20}>
                    <Card>
                    <Tabs defaultActiveKey="1">
                        <TabPane tab={<><FileTextOutlined />Text</>} key="2">
                            <CreateTextAsset />
                        </TabPane>
                        <TabPane tab={<><FileOutlined />Document</>} key="3">
                            <CreateFileAsset />
                        </TabPane>

                    </Tabs>
                    </Card>
                </Col>
            </Row>
    )
}
