import { useEffect, useState, useContext } from 'react';
import { MyInterview, MyAnalyseChat, MyJobAnalyse} from "./index"
import {DisplayResume} from '../main/index'
import { Layout, Menu, Row, Col, Typography, Tabs } from 'antd';
import { Link, useParams } from 'react-router-dom';
import Api from '../../Services/Services';
import { ProviderContext } from '../../context/context';

const { Header, Content } = Layout;
const { Title, Text } = Typography;
const { TabPane } = Tabs;

const MainActivity = () => {
    const { latestsession } = useContext(ProviderContext)
    const [selectedTab, setSelectedTab] = useState('resume');

    const renderContent = () => {
    switch (selectedTab) {
        case 'analyze':
        return <MyJobAnalyse data={analysis !== undefined && (analysis)}  chatanalysis={chatanalysis}/>;
        case 'interview':
        return <MyInterview chat={chatinterview}/>;
        default:
        return null; 
    }
    };

    const [refresh, setRefresh] = useState(0);
    const [activeComponent, setActiveComponent] = useState('A');
    const [show, setShow] = useState(false)
    const [chatanalysis, setChatAnalysis] = useState([])
    const [chatinterview, setChatInterview] = useState([])
    const [analysis, setAnalysis] = useState([])

    let { jbId, sessionId } = useParams();

    const dataFetch = async() => {
        const data = {
            sessionId: sessionId,
            jbId: jbId            
        }
        // console.log("get h", analysis !== undefined)
        const response = await Api.fetchSessionJob(data)
        // console.log("get hold", response.data.latest_analysis)
        setChatAnalysis(response.data.latest_analysischat)
        setChatInterview(response.data.latest_interviewchat)
        setAnalysis(response.data.latest_analysis)
    }

    useEffect(() => {
        dataFetch()
        const intervalId = setInterval(() => {
        setRefresh((prev) => prev + 1); 
        }, 10000);
        return () => clearInterval(intervalId);
    }, [refresh, jbId, sessionId]); 

    const handleMenuClick = (component: any) => {
        setActiveComponent(component);
    };

  return (
    <Layout >
          <Content style={{ padding: '2px' }}>
                <Row>
                    <Col span={24}>
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

                        {selectedTab === 'resume' && <DisplayResume />}
                    </Col>
                </Row>
          </Content>
        </Layout>
  )
}

export default MainActivity