import { useState } from 'react';
import { Modal, Button, Tabs, Collapse } from 'antd';
import { LiquidAntd, Metrics, RadarChart } from './index';

const { TabPane } = Tabs;
const { Panel } = Collapse;

interface Overall {
    metricsData: any,
    evaluationData: any
}
const OverallFeedbackModal: React.FC<Overall> = ({metricsData, evaluationData}) => {
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
                    <button 
                        className='view-btn'                    
                        style={{ marginTop: '2.6rem', border: 'none', cursor: 'pointer' }} 
                        onClick={showModal}>
                        Feedback
                    </button>
                    <LiquidAntd 
                        percent={evaluationData?.overall_performance} />
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
                                        {evaluationData?.recommendation.map((rec:any, index:any) => (
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
                            <div style={{ textAlign: 'justify', marginTop: '2rem', color:'#534d4d' }}>
                                {evaluationData?.conclusion_statement}
                            </div>

                            <div>
                                <h3>Competency Level</h3>
                                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', width: '94vh' }}>
                                    <RadarChart
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