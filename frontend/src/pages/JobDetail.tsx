import {DisplayResume, AnalyseDoc, InterviewPrep} from '../components/main/index'
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
    const { latestsession } = useContext(ProviderContext)
    const { id } = useParams()
    const [selectedTab, setSelectedTab] = useState('resume');

    const renderContent = () => {
    switch (selectedTab) {
        case 'analyze':
        return <AnalyseDoc />;
        case 'interview':
        return <InterviewPrep />;
        default:
        return null; 
    }
    };

    useEffect(() => {
        // localStorage.removeItem("JobId")
        if(id !== undefined){
            localStorage.setItem("JobId", id)
        }
    },[id])
    
    
    
      return (
        <Layout >
          <Content style={{ padding: '2px' }}>
                    <Link to="/jobs">
                        <Text className='header'>Ipersona</Text>
                    </Link>
                <Row>
                    <Text className='pdf'>{latestsession?.fileName}</Text>
                </Row>

                <Row>
                    <Col span={24}>
                        {selectedTab === 'resume' && <DisplayResume />} {/* Show the resume by default */}
                        <Tabs
                        defaultActiveKey="resume"
                        activeKey={selectedTab}
                        onChange={setSelectedTab}
                        style={{ marginTop: '20px' }}
                        >
                        <TabPane tab="Resume" key="resume" />
                        <TabPane tab="Analyze Document" key="analyze" />
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