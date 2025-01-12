import { useState } from 'react';
import { Row, Col, Card, Table, Select, Spin, Button,  Progress } from 'antd';
import { PerformanceChart, LineChartAdmin } from '../index';
import Api from '../../Services/Services';
import { SearchOutlined } from '@ant-design/icons'; 
import { DatePicker, Space } from 'antd';
import moment from 'moment';
import dayjs from 'dayjs';
const defaultDate = dayjs();
const { Option } = Select;

const Dashboard = () => {
  const [overview, setOverview] = useState<any>({});
  const [users, setUsers] = useState([]);
  const [allusers, setAllUsers] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [performancedata, setPerformance] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadinguser, setLoadingUser] = useState(false);
  const [loadingjob, setLoadingJob] = useState(false);
  const [loadingper, setLoadingPer] = useState(false);
  const [limit, setLimit] = useState(10);  
  const [since, setSince] = useState(4);   

  const fetchOverview = async (limit: any, since: any) => {
    setLoading(true);
    const data = { limit, since };
    const response = await Api.AdminOverview(data);
    setOverview(response.data);
    setLoading(false);
  };

  const fetchUsers = async (limit: any, since: any) => {
    setLoadingUser(true);
    const data = { limit, since };
    const response = await Api.AdminUsers(data);
    setUsers(response?.data?.top10 || []);
    setAllUsers(response?.data?.alldata || []);
    setLoadingUser(false);
  };

  const fetchJobs = async (limit: any, since: any) => {
    setLoadingJob(true);
    const data = { limit, since };
    const response = await Api.AdminJobs(data);
    setJobs(response?.data?.top10 || []);
    console.log("job-response",response?.data?.top10 || [])

    setLoadingJob(false);
  };

  const fetchPerformances = async (limit: any, since: any) => {
    setLoadingPer(true);
    const data = { limit, since };
    const response = await Api.AdminUserMetrics(data);
    setPerformance(response?.data || []);
    setLoadingPer(false);
  };

  // Handle Limit & Since Changes
  const handleLimitChange = (value: any) => {
    setLimit(value);
  };

  const handleSinceChange = (value: any) => {
    setSince(value);
  };

  const handleOverviewSearch = () => fetchOverview(limit, since);
  const handleUsersSearch = () => fetchUsers(limit, since);
  const handleJobsSearch = () => fetchJobs(limit, since);
  const handlePerformanceSearch = () => fetchPerformances(limit, since);

  const userColumns = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Gender', dataIndex: 'gender', key: 'gender' },
    { title: 'Nationality', dataIndex: 'nationality', key: 'nationality' },
    { title: '#Interviews', dataIndex: 'total_interviews_count', key: 'total_interviews_count' },
  ];

  const jobColumns = [
    { title: 'Job Title', dataIndex: 'job_title', key: 'job_title' },
    { title: 'Company', dataIndex: 'company_name', key: 'company_name' },
    { title: 'Location', dataIndex: 'location', key: 'location' },
    { title: '#Interviews', dataIndex: 'total_interviews_count', key: 'total_interviews_count' },
  ];

  const userJobInterviewColumns = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { 
      title: 'Jobs/Interviews Taken', 
      key: 'jobs_interviews', 
      render: (record: any) => `${record.job_count} Jobs / ${record.total_interviews_count} Interviews` 
    },
    { title: 'Gender', dataIndex: 'gender', key: 'gender' },
    { title: 'Nationality', dataIndex: 'nationality', key: 'nationality' }
  ];

  const [selectedDate, setSelectedDate] = useState<any>(moment()); 
  const handleDateChange = (date: any) => {
    setSelectedDate(date);
  };

  const selectedMonth = selectedDate ? selectedDate.format('YYYY-MM') : null;

  const daysInMonth = (overview?.daily_sessions_by_month && overview.daily_sessions_by_month[selectedMonth])
    ? Object.keys(overview.daily_sessions_by_month[selectedMonth]).map(Number)
    : [];
  
  const sessionCounts = (overview?.daily_sessions_by_month && overview.daily_sessions_by_month[selectedMonth])
    ? Object.values(overview.daily_sessions_by_month[selectedMonth])
    : [];
  
  const chartData = daysInMonth.map((day, index) => ({
    day: `Day ${day}`,  
    sessionCount: sessionCounts[index],  
  }));
  

  const completionPercentage = (overview?.complete_sessions / overview?.total_interview_sessions) * 100;


  return (
    <div>
      {/* Overview Section */}
      <Row gutter={16} style={{ marginBottom: 20 }}>
        <Col span={24}>
          <Card
            title={
              <Row gutter={16} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Col>Overview</Col>
                <Col>
                  <Select value={limit} onChange={handleLimitChange} style={{ width: 100, marginRight: 10 }}>
                    <Option value={0}>0</Option>
                    <Option value={10}>10</Option>
                    <Option value={20}>20</Option>
                    <Option value={50}>50</Option>
                  </Select>
                  <Select value={since} onChange={handleSinceChange} style={{ width: 150, marginRight: 10 }}>
                    <Option value={0}>Last 0 Days</Option>
                    <Option value={4}>Last 4 Days</Option>
                    <Option value={7}>Last 7 Days</Option>
                    <Option value={14}>Last 14 Days</Option>
                    <Option value={30}>Last 30 Days</Option>
                  </Select>
                  <Button
                    type="link"
                    icon={<SearchOutlined />}
                    onClick={handleOverviewSearch}
                    style={{ padding: 0 }}
                  />
                </Col>
              </Row>
            }
            bordered={false}
          >
            {loading ? <Spin /> : 
            <div>
                <Row gutter={16}>
                    <Col span={8}>
                      <Card title="Total Trainees" bordered={false}>
                        <span style={{ fontWeight: 'bold', fontSize: '30px' }}>
                          {overview?.user_profile_count}
                        </span>
                      </Card>
                      <Card title="Total Jobs" bordered={false}>
                        <span style={{ fontWeight: 'bold', fontSize: '30px' }}>
                          {overview?.job_profile_count}
                        </span>
                      </Card>
                    </Col>

                    <Col span={8}>
                      <Card title="Total Interviews" bordered={false} >
                        <span style={{ fontWeight: 'bold', fontSize: '30px' }}>
                          {overview?.user_profile_count}
                        </span>
                        <div>
                          <LineChartAdmin chartData={chartData} />
                          <Space direction="vertical">
                            <DatePicker 
                              defaultValue={defaultDate}
                              value={selectedDate} 
                              onChange={handleDateChange} 
                              picker="month"  
                              format="YYYY-MM" 
                            />
                          </Space>
                        </div>
                      </Card>
                    </Col>

                    <Col span={8}>
                      <Card title="Interview Completion" bordered={false}>
                        <Progress 
                          percent={completionPercentage} 
                          status="active" 
                          format={percent => `${percent?.toFixed(2)}%`} 
                        />
                        
                        <div style={{ borderTop: '1px solid lightgrey', margin: '20px 0' }}></div>
                        <p>Today Interviews {overview?.today_sessions}</p>
                        <p>This Week Interviews {overview?.current_week_sessions}</p>
                        <p>This Month Interviews {overview?.current_month_sessions}</p>

                      </Card>
                    </Col>
                </Row>
            </div>}
          </Card>
        </Col>
      </Row>

      {/* Users Section */}
      <Row gutter={16} style={{ marginBottom: 20 }}>
        <Col span={24}>
          <Card
            title={
              <Row gutter={16} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Col>Top Users</Col>
                <Col>
                  <Select value={limit} onChange={handleLimitChange} style={{ width: 100, marginRight: 10 }}>
                    <Option value={0}>0</Option>
                    <Option value={10}>10</Option>
                    <Option value={20}>20</Option>
                    <Option value={50}>50</Option>
                  </Select>
                  <Select value={since} onChange={handleSinceChange} style={{ width: 150, marginRight: 10 }}>
                    <Option value={0}>Last 0 Days</Option>
                    <Option value={4}>Last 4 Days</Option>
                    <Option value={7}>Last 7 Days</Option>
                    <Option value={14}>Last 14 Days</Option>
                    <Option value={30}>Last 30 Days</Option>
                  </Select>
                  <Button
                    type="link"
                    icon={<SearchOutlined />}
                    onClick={handleUsersSearch}
                    style={{ padding: 0 }}
                  />
                </Col>
              </Row>
            }
            bordered={false}
          >
            {loadinguser ? <Spin /> : <Table columns={userColumns} dataSource={users} rowKey="user_profile_id" pagination={false} />}
          </Card>
        </Col>
      </Row>


      {/* Performance Section */}
      <Row gutter={16} style={{ marginBottom: 20 }}>
        <Col span={24}>
          <Card
            title={
              <Row gutter={16} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Col>Performance Chart</Col>
                <Col>
                  <Select value={limit} onChange={handleLimitChange} style={{ width: 100, marginRight: 10 }}>
                    <Option value={0}>0</Option>
                    <Option value={10}>10</Option>
                    <Option value={20}>20</Option>
                    <Option value={50}>50</Option>
                  </Select>
                  <Select value={since} onChange={handleSinceChange} style={{ width: 150, marginRight: 10 }}>
                    <Option value={0}>Last 0 Days</Option>
                    <Option value={4}>Last 4 Days</Option>
                    <Option value={7}>Last 7 Days</Option>
                    <Option value={14}>Last 14 Days</Option>
                    <Option value={30}>Last 30 Days</Option>
                  </Select>
                  <Button
                    type="link"
                    icon={<SearchOutlined />}
                    onClick={handlePerformanceSearch}
                    style={{ padding: 0 }}
                  />
                </Col>
              </Row>
            }
            bordered={false}
          >
            {loadingper ? <Spin /> : <PerformanceChart data={performancedata} />}
          </Card>
        </Col>
      </Row>

      {/* Jobs Section */}
      <Row gutter={16} style={{ marginBottom: 20 }}>
        <Col span={24}>
          <Card
            title={
              <Row gutter={16} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Col>Top Jobs</Col>
                <Col>
                  <Select value={limit} onChange={handleLimitChange} style={{ width: 100, marginRight: 10 }}>
                    <Option value={0}>0</Option>
                    <Option value={10}>10</Option>
                    <Option value={20}>20</Option>
                    <Option value={50}>50</Option>
                  </Select>
                  <Select value={since} onChange={handleSinceChange} style={{ width: 150, marginRight: 10 }}>
                    <Option value={0}>Last 0 Days</Option>
                    <Option value={4}>Last 4 Days</Option>
                    <Option value={7}>Last 7 Days</Option>
                    <Option value={14}>Last 14 Days</Option>
                    <Option value={30}>Last 30 Days</Option>
                  </Select>
                  <Button
                    type="link"
                    icon={<SearchOutlined />}
                    onClick={handleJobsSearch}
                    style={{ padding: 0 }}
                  />
                </Col>
              </Row>
            }
            bordered={false}
          >
            {loadingjob ? <Spin /> : <Table columns={jobColumns} dataSource={jobs} rowKey="job_profile_id" pagination={false} />}
          </Card>
        </Col>
      </Row>


      {/* All user data Section */}
      <Row gutter={16} style={{ marginBottom: 20 }}>
        <Col span={24}>
          <Card
            title={
              <Row gutter={16} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Col>Trainees</Col>
              </Row>
            }
            bordered={false}
          >
            {loadinguser ? <Spin /> : <Table columns={userJobInterviewColumns} dataSource={allusers} rowKey="user_profile_id" pagination={false} />}
          </Card>
        </Col>
      </Row>

    </div>
  );
};

export default Dashboard;
