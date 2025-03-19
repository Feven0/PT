import { useState } from 'react';
import { Card } from 'antd';
import { Button } from 'antd';
import { Input, Form, Select } from 'antd';
import Api from '../Services/Services';
import { LoadingSpinner } from './index'

const { TextArea } = Input;
const { Option } = Select;

const TemplateForm = () => {
  const [formData, setFormData] = useState<any>({
    name: '',
    type: 'interview',
    template_questions: {
      Ability: [{ question: '', time_limit: '', end_message: '', ideal_answer: '' }],
      Closing: [{ question: '', time_limit: '', end_message: '', ideal_answer: '' }],
      Technical: [{ question: '', time_limit: '', end_message: '', ideal_answer: '' }],
      Background: [{ question: '', time_limit: '', end_message: '', ideal_answer: '' }],
      Behavioral: [{ question: '', time_limit: '', end_message: '', ideal_answer: '' }],
      Introduction: [{ question: '', time_limit: '', end_message: '', ideal_answer: '' }],
    },
    job_profile_ids: [],
  });
  const [jsonInput, setJsonInput] = useState('');
  const [loading, setLoad] = useState<any>(false);


  const handleChange = (e: any) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleQuestionChange = (category: any, index: any, field: any, value: any) => {
    const updatedQuestions = [...formData.template_questions[category]];
    updatedQuestions[index] = { ...updatedQuestions[index], [field]: value };
    setFormData({
      ...formData,
      template_questions: {
        ...formData.template_questions,
        [category]: updatedQuestions,
      },
    });
  };

  const handleJobProfileChange = (selectedJobProfiles: any) => {
    setFormData({ ...formData, job_profile_ids: selectedJobProfiles });
  };

  const handleJsonChange = (e: any) => {
    setJsonInput(e.target.value);
  };

  const handleJsonSubmit = () => {
    try {
      const parsedJson = JSON.parse(jsonInput);
      if (parsedJson && parsedJson.Ability) {
        setFormData((prevState: any) => ({
          ...prevState,
          template_questions: parsedJson,
        }));
      } else {
        alert('Invalid JSON format. Please check the structure.');
      }
    } catch (error) {
      alert('Invalid JSON format. Please check the structure.');
    }
  };

  const handleSubmit = async () => {
      setLoad(true)
      const payload = {
        run_stage: 'dev',
        name: formData.name,
        type: formData.type,
        template_questions: formData.template_questions,
        job_profile_ids: formData.job_profile_ids
      };
    
      try {
        const response = await Api.SaveTemplate(payload )
        console.log('Response:', response?.data);
        setLoad(false)
        alert('Template Created Successfully!')
      } catch (error) {
        console.error('Error submitting form:', error);
      }
  };
  

  const [currentStep, setCurrentStep] = useState(0);
  const questionCategories = [
    { label: 'Ability', key: 'Ability' },
    { label: 'Closing', key: 'Closing' },
    { label: 'Technical', key: 'Technical' },
    { label: 'Background', key: 'Background' },
    { label: 'Behavioral', key: 'Behavioral' },
    { label: 'Introduction', key: 'Introduction' },
  ];

  const nextStep = () => {
    if (currentStep < questionCategories.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <Card style={{ padding: '24px', width: '100%', maxWidth: '600px', margin: 'auto' }}>
      <Form onFinish={handleSubmit} layout="vertical">
        <Form.Item label="Template Name" required>
          <Input
            name="name"
            placeholder="Enter template name"
            value={formData.name}
            onChange={handleChange}
          />
        </Form.Item>

        <Form.Item label="Template Type" required>
          <Input
            name="type"
            placeholder="Enter template type"
            value={formData.type}
            onChange={handleChange}
          />
        </Form.Item>

        {/* Option to paste the full JSON */}
        <Form.Item label="Or paste template questions as JSON">
          <TextArea
            rows={4}
            placeholder="Paste the entire JSON for template questions"
            value={jsonInput}
            onChange={handleJsonChange}
          />
        </Form.Item>

        <Button type="primary" onClick={handleJsonSubmit} style={{ marginBottom: '16px' }}>
          Submit JSON
        </Button>

        {/* Job Profile ID Selector */}
        <Form.Item label="Select Job Profiles">
          <Select
            mode="multiple"
            placeholder="Select job profile IDs"
            value={formData.job_profile_ids}
            onChange={handleJobProfileChange}
          >
            <Option value="46">Job1</Option>
            <Option value="1651">Job2</Option>
          </Select>
        </Form.Item>


        <h3 className="text-lg font-semibold mb-2">
          {questionCategories[currentStep].label} Questions
        </h3>
        {formData.template_questions[questionCategories[currentStep].key].map(
          (question: any, index: any) => (
            <div key={index} className="mb-4">
              <Form.Item label={`Question ${index + 1}`}>
                <TextArea
                  rows={2}
                  placeholder="Enter question"
                  value={question.question}
                  onChange={(e) =>
                    handleQuestionChange(
                      questionCategories[currentStep].key,
                      index,
                      'question',
                      e.target.value
                    )
                  }
                />
              </Form.Item>
              <Form.Item label="Time Limit">
                <Input
                  placeholder="Enter time limit (e.g., 02:00)"
                  value={question.time_limit}
                  onChange={(e) =>
                    handleQuestionChange(
                      questionCategories[currentStep].key,
                      index,
                      'time_limit',
                      e.target.value
                    )
                  }
                />
              </Form.Item>
              <Form.Item label="End Message">
                <TextArea
                  rows={2}
                  placeholder="Enter end message"
                  value={question.end_message}
                  onChange={(e) =>
                    handleQuestionChange(
                      questionCategories[currentStep].key,
                      index,
                      'end_message',
                      e.target.value
                    )
                  }
                />
              </Form.Item>
            </div>
          )
        )}


        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button onClick={prevStep} disabled={currentStep === 0}>
            Back
          </Button>
          <Button onClick={nextStep} disabled={currentStep === questionCategories.length - 1}>
            Next
          </Button>
        </div>
        <br/>
        <Button type="primary" htmlType="submit" className="w-full">
          Submit Template <span>{loading && <LoadingSpinner style={{ marginLeft: '5px' }} />}</span>
        </Button>
      </Form>
    </Card>
  );
};

export default TemplateForm;
