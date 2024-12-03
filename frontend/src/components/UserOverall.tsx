import { Table, Tag } from 'antd';
interface Data {
  data: any
}

const UserOverall: React.FC<Data> = ({ data }) => {
  const columns = [
    {
      title: 'Job ID',
      dataIndex: 'jobId',
      key: 'jobId',
    },
    {
      title: 'Job Title',
      dataIndex: 'job_title',
      key: 'job_title',
    },
    {
      title: 'Job Match Score',
      dataIndex: 'job_match_score',
      key: 'job_match_score',
      render: (score: any) => (
        <Tag color={score >= 50 ? 'green' : 'red'}>{score}</Tag> 
      ),
    },
    {
      title: 'Job Match',
      dataIndex: 'job_match',
      key: 'job_match',
    },
    {
      title: 'Interviews',
      dataIndex: 'interviews',
      key: 'interviews',
    },
    {
      title: 'Score',
      dataIndex: 'score',
      key: 'score',
      render: (score: any) => (
        <Tag color={score >= 50 ? 'blue' : 'volcano'}>{score}</Tag> 
      ),
    },
  ];

  return (
    <div>
      <h2>Job List</h2>
      <Table
        dataSource={data}
        columns={columns}
        rowKey="jobId" 
        pagination={false}
      />
    </div>
  );
};

export default UserOverall;
