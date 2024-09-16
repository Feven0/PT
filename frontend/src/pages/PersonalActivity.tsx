import React, { useState } from 'react';
import { Breadcrumb, Layout, Menu, theme } from 'antd';
import '../styles/PersonalActivity/personalactivity.css'
import { Status, ProfileDetail } from '../components/personal/index';

const { Header, Content, Footer } = Layout;

// // Placeholder components for Status and Activity
// const Status: React.FC = () => <div>Status Content</div>;
// const Activity: React.FC = () => <div>Activity Content</div>;

const PersonalActivity: React.FC = () => {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const [selectedKey, setSelectedKey] = useState<string>('status');

  const handleMenuClick = (e: any) => {
    setSelectedKey(e.key);
  };

  const menuItems = [
    { key: 'status', label: 'Status' },
    { key: 'activity', label: 'Activity' },
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
          {selectedKey === 'status' ? <Status /> : <ProfileDetail />}
        </div>
      </Content>
    </Layout>
  );
};

export default PersonalActivity;