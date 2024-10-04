import {DisplayResume, AnalyseDoc, InterviewPrep, AllStatus} from '../components/main/index'
import { useState, useContext } from 'react';
import { Layout, Menu, Row, Col, Typography, Tabs } from 'antd';
import { ProviderContext } from '../context/context';
import { useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import '../styles/jobdetail/jobdetail.css'

const { Header, Content } = Layout;
const { Title, Text } = Typography;
const { TabPane } = Tabs;

const JobDetail = () => {
    const { latestsession, setStart } = useContext(ProviderContext)
    const { userId, jobId } = useParams()
    const [selectedTab, setSelectedTab] = useState('resume');

    const renderContent = () => {
    switch (selectedTab) {
        case 'overall-progress':
        return <AllStatus />;
        case 'interview':
        return <InterviewPrep />;
        default:
        return null; 
    }
    };

    useEffect(() => {
        // localStorage.removeItem("JobId")
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
                        {/* {selectedTab === 'resume' && <DisplayResume />}  */}
                        <Tabs
                        defaultActiveKey="resume"
                        activeKey={selectedTab}
                        onChange={setSelectedTab}
                        style={{ marginTop: '2px' }}
                        >
                        {/* <TabPane tab="Resume" key="resume" /> */}
                        {/* <TabPane tab="Analyze Document" key="analyze" /> */}
                        <TabPane tab="Overall Progress" key="overall-progress"/>
                        <TabPane tab="Interview Prep" key="interview" />
                        </Tabs>
                        {renderContent()} 
                    </Col>
                </Row>
          </Content>
        </Layout>
      );
}

export default JobDetail