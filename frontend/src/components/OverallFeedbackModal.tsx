import { useState } from 'react';
import { Modal, Button, Tabs, Collapse } from 'antd';
import { Metrics, RadarRealtime } from './index';

const { TabPane } = Tabs;
const { Panel } = Collapse;

interface Data {
    metricsData: any, evaluationData: any
  } 

const OverallFeedbackModal: React.FC<Data> =({metricsData, evaluationData}) => {
    const [isModalVisible, setIsModalVisible] = useState(false);
    const showModal = () => {
        setIsModalVisible(true);
    };

    const handleOk = () => {
        setIsModalVisible(false);
    };

    const handleCancel = () => {
        setIsModalVisible(false);
    };

    return (
        <div>
            <div className='overall-container'>
                <div className='overall-box'>
                    <div 
                    style={{marginLeft: '0.5rem', fontSize: '1rem'}}
                    onClick={showModal}>
                        {metricsData?.overall_performance_score}%
                    </div>
                </div>
            </div>

            <Modal
                title="Interview Feedback"
                visible={isModalVisible}
                onOk={handleOk}
                onCancel={handleCancel}
                footer={[
                    <Button key="back" onClick={handleCancel}>
                        Close
                    </Button>
                ]}
                width={800} 
            >
                <div style={{ maxHeight: '490px', overflowY: 'auto' }}>
                    <Tabs defaultActiveKey="1">
                        <TabPane tab="Evaluation" key="1">
                            <h1 style={{display: 'flex', justifyContent:'center'}}>
                                {evaluationData?.message}
                            </h1>
                            <Collapse style={{marginBottom: '1rem'}}>
                                <Panel header="Overall Evaluation" key="1" style={{textAlign: 'justify'}}>
                                    <p style={{color: '#7c7878'}}>
                                        {evaluationData?.evaluation}
                                    </p>
                                </Panel>
                            </Collapse>
                            <Collapse>
                                <Panel header="Recommendations" key="1">
                                    <ul style={{textAlign: 'justify'}}>
                                        {evaluationData?.recommendation.map((rec: any, index: any) => (
                                            <li key={index}>
                                                <a href={rec.link} target="_blank" rel="noopener noreferrer">
                                                    {rec.title}
                                                </a>
                                                <p style={{color: '#7c7878'}}>
                                                    - {rec.resource}
                                                </p>
                                            </li>
                                        ))}
                                    </ul>
                                </Panel>
                            </Collapse>

                            <div>
                                <h3>Competency Level</h3>
                                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', width: '94vh' }}>
                                    <RadarRealtime
                                        data={evaluationData?.competency}
                                    />
                                </div>
                            </div>
                        </TabPane>
                        <TabPane tab="Metrics" key="2">
                            <Metrics metricsData={metricsData}/>
                        </TabPane>
                    </Tabs>
                </div>
            </Modal>
        </div>
    );
};

export default OverallFeedbackModal;