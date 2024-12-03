import {useState, useEffect} from 'react'
import { Layout, Menu } from 'antd';
import { DashboardOutlined, FileTextOutlined} from '@ant-design/icons';
import {StatusDashboard, AdminDashboard} from './index';
import Api from '../Services/Services';
import {LoadingIndicator} from './index';

const { Sider, Content } = Layout;

const DashboardLayout = () => {
  const [selectedComponent, setSelectedComponent] = useState('status');
  const [statusData, setStatusData] = useState({});
  const [data, setData] = useState([]);
  const [refresh, setRefresh] = useState(0);

  const fetchData = async() => {
        const responsestatus = await Api.ApplicationManager()
        setData(responsestatus.data)
        const response = await Api.AnalyticsOverview()
        setStatusData(response.data)
    }

    useEffect(() => {
        fetchData()
            const intervalId = setInterval(() => {
            setRefresh((prev) => prev + 1);
            }, 500000);

        return () => clearInterval(intervalId); 
    }, [refresh])

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={250} theme="light">
        <Menu
          mode="inline"
          defaultSelectedKeys={['1']}
          onSelect={({ key }) => setSelectedComponent(key)}
        >
          <Menu.Item key="status" icon={<DashboardOutlined />}>
            Overview
          </Menu.Item>
          <Menu.Item key="admin" icon={<FileTextOutlined />}>
            Details
          </Menu.Item>
        </Menu>
      </Sider>
      <Layout>
        {(Object.keys(statusData).length == 0) ? (
           <Content>
              <LoadingIndicator message={'Wait...'}/>
            </Content> 
        ):
        ( 
          <Content style={{ padding: '0 24px', minHeight: 280 }}>
            {selectedComponent === 'status' && <StatusDashboard statusData={statusData} />}
            {selectedComponent === 'admin' && <AdminDashboard data={data} />}
            </Content>
            
        )}
      </Layout>
    </Layout>
  );
};

export default DashboardLayout;
