import { 
    JobOverallProgress, 
    InterviewChat, 
    Audio, 
    UserOverallProgress,
    DashboardLayout } from '../components/index'
import { useState} from 'react';
import { Layout, Row, Col, Tabs } from 'antd';
import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import '../styles/jobdetail/jobdetail.css'

const { Content } = Layout;
const { TabPane } = Tabs;

const JobDetail = () => {
    const { jobId } = useParams()
    const [selectedTab, setSelectedTab] = useState('');

    const renderContent = () => {
    switch (selectedTab) {
        case 'all-stat':
        return <UserOverallProgress/>
        case 'overall-progress':
        return <JobOverallProgress/>;
        case 'interview':
        return <InterviewChat/>;
        case 'audio':
        return <Audio/>;
        case 'admin-dashboard':
        return <DashboardLayout/>;
        default:
        return null; 
    }
    };

    useEffect(() => {
        if(jobId !== undefined){
            localStorage.setItem("JobId", jobId)
        }
    },[jobId])   
    
    
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
                        <TabPane tab="All Status" key="all-stat"/>
                        <TabPane tab="Overall Job Progress" key="overall-progress"/>
                        <TabPane tab="Chat Interview" key="interview" />
                        <TabPane tab="Audio" key="audio" />
                        <TabPane tab="Admin Dashboard" key="admin-dashboard" />
                        </Tabs>
                        {renderContent()} 
                    </Col>
                </Row>
            </Content>
        </Layout>
    );
}

export default JobDetail