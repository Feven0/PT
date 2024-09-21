import React, { useState, useContext, useEffect } from 'react';
import { Breadcrumb, Layout, Menu, theme } from 'antd';
import '../styles/PersonalActivity/personalactivity.css'
import { Status, AllStatus } from '../components/main/index';
import { ProviderContext } from '../context/context';
const { Header, Content, Footer } = Layout;



const EvaluationStatus: React.FC = () => {
  const {setStart} = useContext(ProviderContext)
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

  const menuItems = [
    { key: 'status', label: 'Current Metrics' },
    { key: 'allstatus', label: 'All Metrics Progress' },
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
          {selectedKey === 'status' ? <Status /> : <AllStatus />}
        </div>
      </Content>
    </Layout>
  );
};

export default EvaluationStatus;