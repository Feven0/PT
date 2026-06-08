import { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import Slider from "react-slick";
import { Button, Card, Col, Divider, Form, InputNumber, Modal, Row } from 'antd';
import { EyeOutlined, CheckOutlined, InfoCircleOutlined } from '@ant-design/icons';

import { setCoverLetterInfo, setTemplateInfo } from "../../../redux/slices/Preferences/resumeTemplateSlice";
import { setPreferenceControlTag } from "../../../redux/slices/Preferences/preferenceControlSlice";
import { useAppSelector } from "../../../redux/hooks/hooks";
import { templates } from "../../../utils/commonUtils";
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import '../../../styles/preference.css'
import TemplatePreviewer from "./TemplatePreviewer";

type PdfFile = {
  name: string;
  value: string; 
}

export default function CVTemplate() {
  const dispatch = useDispatch();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<{ 
    template_name: string; 
    image: string; 
    image2:PdfFile 
    template_id: string; 
    max_work_experience: number; 
    max_projects: number; 
    max_page: number } | null>(null);

  const { resume, cover_letter } = useAppSelector((state) => state.resumePreference);
  const [form] = Form.useForm();
  useEffect(() => {
    const matchedTemplate = templates.find(template => template.template_id === resume.template_id);
    if (matchedTemplate) {
      setSelectedTemplate(matchedTemplate);
    }
  }, [resume.template_id]);

  useEffect(() => {
    form.setFieldsValue({
      max_work_experience: resume.max_work_experience,
      max_projects: resume.max_projects,
      max_pages: resume.max_page,
      cover_letter_max_pages: cover_letter?.max_page,
    });
  }, [resume]);

  const handleCardClick = (template: { 
          template_name: string; 
          image: string; 
          image2:PdfFile;
          template_id: string; 
          max_work_experience: number; 
          max_projects: number; 
          max_page: number }) => {
    dispatch(setTemplateInfo({
      ...resume,
      template_id: template.template_id,
      template_name: template.template_name,
    }));
    dispatch(setPreferenceControlTag(true));
    setSelectedTemplate(template);
    // setIsModalVisible(false);
  };

  const handleSaveTemplate = (template: {
       template_name: string; 
       image: string; 
       image2: PdfFile;
       template_id: string; 
       max_work_experience: number; 
       max_projects: number; 
       max_page: number }) => {
    dispatch(setTemplateInfo({
      ...resume,
      template_id: template.template_id,
      template_name: template.template_name,
    }));
    dispatch(setPreferenceControlTag(true));
    setIsModalVisible(false);
  };


  const handleCancel = () => {
    setIsModalVisible(false);
    setSelectedTemplate(null);
  };

  const settings = {
    dots: true,
    infinite: false,
    speed: 500,
    slidesToShow: 3,
    slidesToScroll: 2,
    initialSlide: 0,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 3,
          slidesToScroll: 3,
          infinite: false,
          dots: true
        }
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 2,
          initialSlide: 2
        }
      },
      {
        breakpoint: 480,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1
        }
      }
    ]
  };


  return (
    <>
        <div className="d-flex-between roles-header">
          <span className="preference__header__title">Application Template</span>
        </div>
      <div className="description-text">
        <InfoCircleOutlined />
        <span style={{ marginLeft: "8px" }}>
          Review and select a template for your application to to best showcase your qualifications and experience.
        </span>
     </div>
     {templates?.length > 3 ? (
      <div className="mt-16 templates__slider">
      <Slider {...settings}>
        {templates?.map((template) => (
          <Card
            className={`slider-card ${selectedTemplate?.template_id === template.template_id ? 'selected-card' : 'template-card'}`}
            key={template.template_id}
            cover={<img alt={template.template_name} src={template.image} />}
            onClick={() => handleCardClick(template)}
            actions={[
              <div className="template-actions d-flex-between" style={{
                paddingLeft: "0.5rem",
                paddingRight: "0.5rem",
              }}>
                <span
                  className="template-title"
                  style={{ flex: 1, textAlign: 'start' }}
                >
                  {template.template_name}
                </span>
                <EyeOutlined onClick={() => setIsModalVisible(true)} />
              </div>
            ]}
          >
            {selectedTemplate?.template_id === template.template_id && (
              <div className="selected-card-text">
                <span className="selected-card-icon">
                  <CheckOutlined />
                </span>
              </div>
            )}
          </Card>
        ))}
      </Slider>
      </div>
    ) : (
      <div className="flex-center gap-8 mt-16 p-16"> 
      {
      templates?.map((template) => (
        <Card
          className={`slider-card ${selectedTemplate?.template_id === template.template_id ? 'selected-card' : 'template-card'}`}
          key={template.template_id}
          cover={<img alt={template.template_name} src={template.image} />}
          onClick={() => handleCardClick(template)}
          style={{
            display: "inline-block",
          }}
          actions={[
            <div className="template-actions d-flex-between" style={{
              paddingLeft: "0.5rem",
              paddingRight: "0.5rem",
            }}>
              <span
                className="template-title"
                style={{ flex: 1, textAlign: 'start' }}
              >
                {template.template_name}
              </span>
              <EyeOutlined onClick={() => setIsModalVisible(true)} />
            </div>
          ]}
        >
          {selectedTemplate?.template_id === template.template_id && (
            <div className="selected-card-text">
              <span className="selected-card-icon">
                <CheckOutlined />
              </span>
            </div>
          )}
        </Card>
      ))}
      </div>
    )}
    <div className="d-flex-between roles-header application-format-container">
      <span className="preference__header__title">Application Format</span>
      </div>
      <div className="description-text">
        <InfoCircleOutlined />
        <span style={{ marginLeft: "8px" }}>
         Write basic application format details here and customize the page size, content inclusion, and the level of detail presented in your application.
        </span>
    </div>
    <div className="company-size-tags-div mt-16 industry-tag-div" style={{padding:"1rem"}}>
        <Form layout="vertical" form={form} name="days_since_extracted_form">
          <span className="cover_letter">CV Format</span>
          <Divider />
            <Row gutter={16} className="full-width">
                <Col xs={24} md={12} lg={8}>
                  <Form.Item name="max_work_experience" label="Max work experience">
                    <InputNumber
                      className="full-width"
                      min={1}
                      max={20}
                      placeholder="Enter here"
                      onChange={(value) => {
                        if (typeof value === 'number') {
                          dispatch(setTemplateInfo({
                            ...resume,
                            max_work_experience: value,
                          }));
                        }
                      }}
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12} lg={8}>
                  <Form.Item name="max_projects" label="Max Projects">
                    <InputNumber
                      className="full-width"
                      min={1}
                      placeholder="Enter here"
                      onChange={(value) => {
                        if (typeof value === 'number') {
                          dispatch(setTemplateInfo({
                            ...resume,
                            max_projects: value,
                          }));
                        }
                      }}
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12} lg={8}>
                  <Form.Item name="max_pages" label="Max Pages">
                    <InputNumber
                      className="full-width"
                      min={1}
                      max={5}
                      placeholder="Enter here"
                      onChange={(value) => {
                        if (typeof value === 'number') {
                          dispatch(setTemplateInfo({
                            ...resume,
                            max_page: value,
                          }));
                        }
                      }}
                    />
                  </Form.Item>
                </Col>
                <span className="cover_letter">Cover Letter Format</span>
                <Divider />
                <Col xs={24} md={12} lg={8}>
                  <Form.Item name="cover_letter_max_pages" className="mt-16" label="Max Pages">
                    <InputNumber
                      className="full-width"
                      min={1}
                      max={5}
                      placeholder="Enter here"
                      onChange={(value) => {
                        if (typeof value === 'number') {
                          dispatch(setCoverLetterInfo({
                            max_page: value,
                          }));
                        }
                      }}
                    />
                  </Form.Item>
                </Col>
            </Row>
        </Form>
    </div>
      <Modal
        title={`${selectedTemplate?.template_name} template`}
        open={isModalVisible}
        footer={null}
        width={1200}
        onCancel={handleCancel}>
        <div>
          {selectedTemplate && <TemplatePreviewer file={[selectedTemplate.image2]} />}
        </div>
        <div className="d-flex-center mt-16">
          {selectedTemplate && (
            <Button
              className="dark-orange-bg white-color"
              onClick={() => handleSaveTemplate(selectedTemplate)}>
              Select this template
            </Button>
          )}
        </div>
      </Modal>
    </>
  );
}
