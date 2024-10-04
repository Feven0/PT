import React, { useState, useContext, useEffect } from 'react';
import { Breadcrumb, Layout, Menu, theme } from 'antd';
import '../styles/PersonalActivity/personalactivity.css'
import { Status, AllStatus } from '../components/main/index';
import { ProviderContext } from '../context/context';
import Api from '../Services/Services';


const { Header, Content, Footer } = Layout;


const EvaluationStatus: React.FC = () => {
  const {latestsession, latestUserData, setStart} = useContext(ProviderContext)
  const [metrics, setEvalMetrics] = useState<any>();
  const [refresh, setRefresh] = useState(1);
  
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const [selectedKey, setSelectedKey] = useState<string>('status');

  useEffect(() => {
    setStart(true);
  }, [setStart]);

  const handleMenuClick = (e: any) => {
    setSelectedKey(e.key);
  };


  const fetchMetrics = async() => {
    const dt = {
        userId: latestsession?.userId,
        sessionId: latestsession?.sessionId,
        jbId: latestUserData?.jbId
    }
    const response = await Api.fetchEvaluationMetrics(dt)
    console.log("response status", response?.data?.all_metrics_data?.slice(-2))
    setEvalMetrics(response?.data?.latest_evaluation_metrics)
}

useEffect(() =>{
    if (refresh) {
        fetchMetrics()

        const timer = setTimeout(() => {
            setRefresh(null);
        }, 6000);

        return () => clearTimeout(timer);
    }
},[refresh])

  const menuItems = [
    { key: 'status', label: 'Current Metrics' },
    { key: 'allstatus', label: 'Last Two-Interview Progress' },
  ];

  return (
    <Layout>
        <div className="demo-logo" />
        <Menu
          className="custom-menu" 
          mode="horizontal"
          selectedKeys={[selectedKey]}
          onClick={handleMenuClick}
          items={menuItems}
          style={{ flex: 1, minWidth: 0 }}
        />
      <Content style={{ padding: '0 48px' }}>
        <div
          style={{
            background: colorBgContainer,
            minHeight: 280,
            padding: 24,
            borderRadius: borderRadiusLG,
          }}
        >
          {selectedKey === 'status' ? <Status metrics={metrics}/> : <AllStatus />}
        </div>
      </Content>
    </Layout>
  );
};

export default EvaluationStatus;