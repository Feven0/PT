import { AllStatus, InterviewChat, Audio } from '../components/index'
import { useState, useContext } from 'react';
import { Layout, Row, Col, Tabs } from 'antd';
import { ProviderContext } from '../context/context';
import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import '../styles/jobdetail/jobdetail.css'

const { Content } = Layout;
const { TabPane } = Tabs;

const JobDetail = () => {
    const { setStart } = useContext(ProviderContext)
    const { jobId } = useParams()
    const [selectedTab, setSelectedTab] = useState('');

    const renderContent = () => {
    switch (selectedTab) {
        case 'overall-progress':
        return <AllStatus />;
        case 'interview':
        return <InterviewChat />;
        case 'audio':
        return <Audio />;
        default:
        return null; 
    }
    };

    useEffect(() => {
        if(jobId !== undefined){
            localStorage.setItem("JobId", jobId)
        }
    },[jobId])

    useEffect(() => {
        setStart(true);
    }, [setStart]);
    
    
    
      return (
        <Layout>
          <Content style={{ padding: '2px' }}>
                <Row>
                    <Col span={24}>
                        <Tabs
                        defaultActiveKey="resume"
                        activeKey={selectedTab}
                        onChange={setSelectedTab}
                        style={{ marginTop: '2px' }}
                        >
                        <TabPane tab="Overall Progress" key="overall-progress"/>
                        <TabPane tab="Interview Prep" key="interview" />
                        <TabPane tab="Audio Interview" key="audio" />
                        </Tabs>
                        {renderContent()} 
                    </Col>
                </Row>
          </Content>
        </Layout>
      );
}

export default JobDetail