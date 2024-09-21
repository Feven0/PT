import { Table, Collapse, Card, Progress, Typography, Row, Col, Dropdown, Menu } from 'antd';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { useState, useContext, useEffect } from 'react';
import { ProviderContext } from '../../context/context';
import Api from '../../Services/Services';
import '../../styles/Status/status.css'

const { Panel } = Collapse;

const { Title, Text } = Typography;

const Status = () => {
    const { latestsession, latestUserData} = useContext(ProviderContext);
    const [metrics, setEvalMetrics] = useState<any>();
    const [refresh, setRefresh] = useState(1);
    const evaluation = metrics || {};
    
    const fetchMetrics = async() => {
        const dt = {
            userId: latestsession?.userId,
            sessionId: latestsession?.sessionId,
            jbId: latestUserData?.jbId
        }
        const response = await Api.fetchEvaluationMetrics(dt)
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
    

  const convertPercentToNumber = (percentStr) => {
    return parseFloat(percentStr) || 0; 
  }

  const barData = [
      { name: 'Relevant Answers', value: convertPercentToNumber(evaluation?.relevant_answers) },
      { name: 'Irrelevant Answers', value: convertPercentToNumber(evaluation?.irrelevant_answers) }
  ];

  const [expandedImprovementKeys, setExpandedImprovementKeys] = useState([]);
  const [expandedStrengthKeys, setExpandedStrengthKeys] = useState([]);

  const onImprovementRowClick = (record) => {
      const newExpandedKeys = expandedImprovementKeys.includes(record.key)
          ? expandedImprovementKeys.filter(key => key !== record.key)
          : [...expandedImprovementKeys, record.key];
      setExpandedImprovementKeys(newExpandedKeys);
  };

  const onStrengthRowClick = (record) => {
      const newExpandedKeys = expandedStrengthKeys.includes(record.key)
          ? expandedStrengthKeys.filter(key => key !== record.key)
          : [...expandedStrengthKeys, record.key];
      setExpandedStrengthKeys(newExpandedKeys);
  };

  const columns = [
      {
          title: 'Skill',
          dataIndex: 'skill',
          key: 'skill',
          render: (text, record) => (
              <span onClick={() => onImprovementRowClick(record)} style={{ cursor: 'pointer', color: 'blue' }}>
                  {text}
              </span>
          )
      }
  ];

  const strength_columns = [
    {
        title: 'Skill',
        dataIndex: 'skill',
        key: 'skill',
        render: (text, record) => (
            <span onClick={() => onStrengthRowClick(record)} style={{ cursor: 'pointer', color: 'blue' }}>
                {text}
            </span>
        )
    }
];

  const improvementData = evaluation?.improvement?.map((item, index) => ({
      key: `improvement-${index}`,
      skill: item.skill,
      description: item.description
  })) || [];

  const strengthData = evaluation?.strength?.map((item, index) => ({
      key: `strength-${index}`,
      skill: item.skill,
      description: item.description
  })) || [];



  return (
      <div style={{ padding: '20px' }}>
          <Title level={2}>Candidate Interview Evaluation</Title>
          <Row gutter={16}>
              <Col span={12}>
                  <Card title="Performance Overview">
                      <Text className="card-text">{evaluation?.performance_message}</Text>
                      <Progress percent={parseInt(evaluation?.performance_percent)} />
                      <Text strong className="card-text">Performance: {evaluation?.performance_percent}</Text>
                      <Text strong className="card-text">Confidence Level: {evaluation?.confidence_level}</Text>
                      {/* <Text strong className="card-text">Answer Relevance: {evaluation.answer_relevance}</Text> */}
                  </Card>
              </Col>
              <Col span={12}>
                    <Card title="Time Management">
                        <Text className="card-text">Adherence: {evaluation?.adherence}</Text>
                        <Text className="card-text">Questions Completed on Time: {evaluation?.timer_pass}</Text>
                        <Text className="card-text">Questions Not Completed on Time: {evaluation?.timer_failed}</Text>
                    </Card>
              </Col>
          </Row>

          <Row gutter={16} style={{ marginTop: '20px' }}>
              <Col span={12}>
                  <Card title="Communication-Skills">
                      <Text className="card-text">Clarity: {evaluation?.clarity}</Text>
                      <Text className="card-text">Engagement: {evaluation?.engagement}</Text>
                  </Card>
              </Col>
              <Col span={12}>
                  <Card title="Answer Relevance Visualization">
                    <BarChart width={400} height={100} data={barData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#82ca9d" />
                    </BarChart>
                  </Card>
              </Col>
          </Row>

          <Row gutter={16} style={{ marginTop: '20px' }}>
              <Col span={12}>
                <Card title="Areas of Improvement">
                    <Table
                        columns={columns}
                        dataSource={improvementData}
                        pagination={false}
                        expandedRowRender={record => (
                            <ul>
                                <li>{record.description}</li>
                            </ul>
                        )}
                        expandedRowKeys={expandedImprovementKeys}
                        onExpand={(expanded, record) => {
                            if (expanded) {
                                setExpandedImprovementKeys([...expandedImprovementKeys, record.key]);
                            } else {
                                setExpandedImprovementKeys(expandedImprovementKeys.filter(key => key !== record.key));
                            }
                        }}
                    />
                </Card>
              </Col>
              <Col span={12}>
              <Card title="Strength">
                    <Table
                        columns={strength_columns}
                        dataSource={strengthData}
                        pagination={false}
                        expandedRowRender={record => (
                            <ul>
                                <li>{record.description}</li>
                            </ul>
                        )}
                        expandedRowKeys={expandedStrengthKeys}
                        onExpand={(expanded, record) => {
                            if (expanded) {
                                setExpandedStrengthKeys([...expandedStrengthKeys, record.key]);
                            } else {
                                setExpandedStrengthKeys(expandedStrengthKeys.filter(key => key !== record.key));
                            }
                        }}
                    />
                </Card>
              </Col>
          </Row>

          <Row gutter={16} style={{ marginTop: '20px' }}>
            <Col span={24}>
                <Card title="Overall Performance Rating">
                    <div className='analysis-rating' style={{ display: 'flex', alignItems: 'center' }}>
                        <Text style={{ fontSize: '24px', fontWeight: 'bold', color: '#ff4d4f', marginRight: '8px' }}>
                            {evaluation?.rating}
                        </Text>
                        <Text>{evaluation?.comments}</Text>
                    </div>
                </Card>
            </Col>
         </Row>
      </div>
  );
};

export default Status;