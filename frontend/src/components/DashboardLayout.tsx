import { useState, useEffect, useRef } from 'react';
import { Layout, Menu } from 'antd';
import { DashboardOutlined, FileTextOutlined } from '@ant-design/icons';
import { StatusDashboard, AdminDashboard, AllDataFilterAdmin } from './index';
import Api from '../Services/Services';
import { LoadingIndicator } from './index';

const { Sider, Content } = Layout;

const DashboardLayout = () => {
  const [selectedComponent, setSelectedComponent] = useState('status');
  const [isDataFetched, setIsDataFetched] = useState(false); 
  const [isStatusDataFetched, setIsStatusDataFetched] = useState(false);

  const summary_data = useRef([]);
  const aggregated_data = useRef([]);
  const statusData = useRef({});

  const fetchData = async () => {
    try {
      const responsestatus = await Api.ApplicationManager();
      summary_data.current = responsestatus?.data?.summary_response;
      aggregated_data.current = responsestatus?.data?.aggregated;

      setIsDataFetched(true); 
      console.log('data fetching data:', summary_data.current);

      const response = await Api.AnalyticsOverview();
      statusData.current = response.data;
      setIsStatusDataFetched(true); 
      console.log('statusdata fetching data:', statusData.current);

    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  useEffect(() => {
    fetchData();
    const intervalId = setInterval(() => {
      fetchData(); 
    }, 500000);

    return () => clearInterval(intervalId);
  }, []);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={150} theme="light">
        <Menu
          mode="inline"
          defaultSelectedKeys={['1']}
          onSelect={({ key }) => setSelectedComponent(key)}
        >
          <Menu.Item key="status" icon={<DashboardOutlined />}>
            Overview
          </Menu.Item>
          <Menu.Item key="admin" icon={<FileTextOutlined />}>
            Trainees
          </Menu.Item>
          <Menu.Item key="admin-details" icon={<FileTextOutlined />}>
            Details
          </Menu.Item>
        </Menu>
      </Sider>
      <Layout>
        {!isDataFetched ? ( 
          <Content>
            <LoadingIndicator message={'Loading Admin Data...'} />
          </Content>
        ) : (
          <Content style={{ padding: '0 12px', minHeight: 280 }}>
            {selectedComponent === 'status' && (
              isStatusDataFetched ? ( 
                <StatusDashboard statusData={statusData.current} />
              ) : (
                <LoadingIndicator message={'Loading Overview...'} /> 
              )
            )}
            {selectedComponent === 'admin' && (
                <AllDataFilterAdmin data={aggregated_data.current} />
            )}
            {selectedComponent === 'admin-details' && (
              <AdminDashboard data={summary_data.current}/>
            )}
          </Content>
        )}
      </Layout>
    </Layout>
  );
};

export default DashboardLayout;
