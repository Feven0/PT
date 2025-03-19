import { useState, useEffect } from 'react';
import { Table, Button, Collapse, Form, Input, Select, Space } from 'antd';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons'; 
import Api from '../Services/Services';
import { LoadingSpinner } from './index';

const { Panel } = Collapse;
const { TextArea } = Input;
const { Option } = Select;

const UpdateTemplate = () => {
  const [templates, setTemplates] = useState([]);
  const [editingTemplate, setEditingTemplate] = useState<any>(null);
  const [form] = Form.useForm();
  const [currentCategory, setCurrentCategory] = useState(0); 
  const [loading, setLoad] = useState<any>(false);

  // Mock job profile data
  const mockJobProfiles = [
    { id: '46', name: 'Software Engineer' },
    { id: '1617', name: 'Data Scientist' },
    { id: '1651', name: 'AI Researcher' },
    { id: '47', name: 'Business Analyst' },
    { id: '58', name: 'Product Manager' },
  ];

  // Fetch templates
  const getTemplates = async () => {
    const data = { job_profile_id: 46 };
    const response = await Api.GetTemplates(data);
    setTemplates(response?.data || []);
  };

  useEffect(() => {
    getTemplates();
  }, []);

  // Handle input changes for template details
  const handleInputChange = (field: string, value: any) => {
    setEditingTemplate({
      ...editingTemplate,
      attributes: {
        ...editingTemplate.attributes,
        [field]: value,
      },
    });
  };

  // Handle input changes for template questions
  const handleQuestionChange = (category: string, index: number, field: string, value: string) => {
    const updatedQuestions = [...editingTemplate.attributes.attributes.template_questions[category]];
    updatedQuestions[index] = { ...updatedQuestions[index], [field]: value };
    setEditingTemplate({
      ...editingTemplate,
      attributes: {
        ...editingTemplate.attributes,
        attributes: {
          ...editingTemplate.attributes.attributes,
          template_questions: {
            ...editingTemplate.attributes.attributes.template_questions,
            [category]: updatedQuestions,
          },
        },
      },
    });
  };

  // Add a new question to a category
  const addQuestion = (category: string) => {
    const newQuestion = {
      question: '',
      time_limit: '',
      end_message: '',
      question_number: `${editingTemplate.attributes.attributes.template_questions[category].length + 1}`,
    };
    setEditingTemplate({
      ...editingTemplate,
      attributes: {
        ...editingTemplate.attributes,
        attributes: {
          ...editingTemplate.attributes.attributes,
          template_questions: {
            ...editingTemplate.attributes.attributes.template_questions,
            [category]: [...editingTemplate.attributes.attributes.template_questions[category], newQuestion],
          },
        },
      },
    });
  };

  // Remove a question from a category
  const removeQuestion = (category: string, index: number) => {
    const updatedQuestions = [...editingTemplate.attributes.attributes.template_questions[category]];
    updatedQuestions.splice(index, 1);
    setEditingTemplate({
      ...editingTemplate,
      attributes: {
        ...editingTemplate.attributes,
        attributes: {
          ...editingTemplate.attributes.attributes,
          template_questions: {
            ...editingTemplate.attributes.attributes.template_questions,
            [category]: updatedQuestions,
          },
        },
      },
    });
  };

  // Handle job profile ID selection
  const handleJobProfileChange = (value: string[]) => {
    setEditingTemplate({
      ...editingTemplate,
      attributes: {
        ...editingTemplate.attributes,
        tinder_job_profiles: {
          data: value.map((id) => ({ id })),
        },
      },
    });
  };

  // Submit the updated template
  const handleSubmit = async () => {
    try {
      setLoad(true)
      const data = {
        run_stage: 'dev',
        template_id: editingTemplate?.id, 
        name: editingTemplate?.attributes?.name, 
        type: editingTemplate?.attributes?.type, 
        template_questions: editingTemplate?.attributes?.attributes?.template_questions, 
        job_profile_ids: editingTemplate?.attributes?.tinder_job_profiles.data.map((profile: any) => profile.id), 
      };

      const response = await Api.UpdateTemplate(data); 
      console.log("update_response:", response?.data)
      setLoad(false)
      alert('Template Updated Successfully!')
      getTemplates(); 
    } catch (error) {
      console.error('Error updating template:', error);
    }
  };


  // Table columns configuration
  const columns = [
    { title: 'Name', dataIndex: ['attributes', 'name'], key: 'name' },
    { title: 'Type', dataIndex: ['attributes', 'type'], key: 'type' },
    {
      title: 'Expand',
      key: 'expand',
      render: (_:any, record: any) => (
        <Button onClick={() => setEditingTemplate(record)}>Expand</Button>
      ),
    },
  ];

  // Get current category's questions
  const currentCategoryKey = Object.keys(editingTemplate?.attributes?.attributes?.template_questions || {})[currentCategory];
  const currentQuestions = currentCategoryKey
    ? editingTemplate?.attributes?.attributes?.template_questions[currentCategoryKey]
    : [];

  return (
    <div>
      <Table columns={columns} dataSource={templates} rowKey="id" style={{margin: '50px'}}/>
        {editingTemplate && (
          <Collapse defaultActiveKey={['1']} style={{ marginTop: '20px' }}>
            <Panel header="Edit Template Details" key="1" style={{margin: '20px 150px 20px 150px'}}>
              <Form form={form} layout="vertical" onFinish={handleSubmit}>
                {/* Template Name */}
                <Form.Item label="Name">
                  <Input
                    value={editingTemplate.attributes.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                  />
                </Form.Item>

                {/* Template Type */}
                <Form.Item label="Type">
                  <Select
                    value={editingTemplate.attributes.type}
                    onChange={(value) => handleInputChange('type', value)}
                  >
                    <Option value="Interview">Interview</Option>
                    <Option value="Assessment">Assessment</Option>
                  </Select>
                </Form.Item>

                {/* Job Profile IDs */}
                <Form.Item label="Job Profile IDs">
                  <Select
                    mode="multiple"
                    value={editingTemplate.attributes.tinder_job_profiles.data.map((profile: any) => profile.id)}
                    onChange={handleJobProfileChange}
                    placeholder="Select Job Profiles"
                  >
                    {mockJobProfiles.map((profile) => (
                      <Option key={profile.id} value={profile.id}>
                        {profile.name}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>

                {/* Template Questions Navigation */}
                {currentCategoryKey && (
                  <div key={currentCategoryKey} style={{ marginBottom: '20px', backgroundColor: '#f8f4f4' }}>
                    <h3>{currentCategoryKey}</h3>
                    {currentQuestions.map((question: any, index: number) => (
                      <div key={index} style={{ marginBottom: '10px' }}>
                        <Space direction="vertical" size="middle" style={{ display: 'flex' }}>
                          <Form.Item label={`Question ${question.question_number}`}>
                            <TextArea
                              value={question.question}
                              onChange={(e) =>
                                handleQuestionChange(currentCategoryKey, index, 'question', e.target.value)
                              }
                            />
                          </Form.Item>

                          <Form.Item label="Time Limit">
                            <Input
                              value={question.time_limit}
                              onChange={(e) =>
                                handleQuestionChange(currentCategoryKey, index, 'time_limit', e.target.value)
                              }
                            />
                          </Form.Item>

                          <Form.Item label="End Message">
                            <Input
                              value={question.end_message}
                              onChange={(e) =>
                                handleQuestionChange(currentCategoryKey, index, 'end_message', e.target.value)
                              }
                            />
                          </Form.Item>

                          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '20px' }}>
                            <Button type="primary" onClick={() => addQuestion(currentCategoryKey)}>
                              <PlusOutlined /> Add Question
                            </Button>
                            <Button onClick={() => removeQuestion(currentCategoryKey, index)}>
                              <MinusCircleOutlined /> Remove Question
                            </Button>
                          </div>
                        </Space>
                      </div>
                    ))}
                  </div>
                )}

                {/* Navigation buttons */}
                <div style={{ marginTop: '20px' }}>
                  {currentCategory > 0 && (
                    <Button style={{ marginRight: '10px' }} onClick={() => setCurrentCategory(currentCategory - 1)}>
                      Back
                    </Button>
                  )}
                  {currentCategory < Object.keys(editingTemplate?.attributes?.attributes?.template_questions || {}).length - 1 && (
                    <Button onClick={() => setCurrentCategory(currentCategory + 1)}>
                      Next
                    </Button>
                  )}
                </div>

                <Form.Item style={{ marginTop: '20px' }}>
                  <Button type="primary" htmlType="submit">
                    Update Template  <span>{loading && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                    </span>
                  </Button>
                </Form.Item>
              </Form>
            </Panel>
          </Collapse>
        )}
    </div>
  );
};

export default UpdateTemplate;
