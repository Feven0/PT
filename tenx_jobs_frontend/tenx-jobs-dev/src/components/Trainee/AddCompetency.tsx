import { useState } from "react";
import { Button, Card, Col, Flex, Form, Input, InputNumber, message, Popconfirm, Row, Select, Typography } from "antd";
import { useMutation } from "@apollo/client";
import { DeleteOutlined, PlusOutlined } from "@ant-design/icons";

import { capitalizeFirstChar, sources } from "../../utils/commonUtils";
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import { addSession, removeSession, resetEvidenceForm } from "../../redux/slices/updateEvidenceSlice";
import useEvidenceForm from "../../hooks/useEvidenceForm";
import { setEvidence } from "../../redux/slices/experienceSlice";
import { CREATE_NOTIFICATION } from "../../graphql/mutations/createNotification";
import useAxiosRequest from "../../hooks/useAxiosRequest";
import useFetchUserProfile from "../../hooks/useFetchUserProfile";
import '../../styles/slidingCard.css'
import { getRunStage } from "../../utils/getRunStage";

const { TextArea } = Input;
const { Paragraph } = Typography


const run_stage = getRunStage();

type addCompetencyProps = {
  setIsAddCompetenceDrawerVisible: (value: boolean) => void;
}

export default function AddCompetency({ setIsAddCompetenceDrawerVisible }: addCompetencyProps) {
  const [sourceLinkMap, setSourceLinkMap] = useState<{ name: string; link: string }>({
    name: '',
    link: '',
  });

  const [formData, setFormData] = useState({
    description: '',
    rationale: '',
    sfia_level: 1,
    competency_name: '',
    skills: [],
    experience_level: '',
    abilities: [],
    knowledge: [],
    attitude: [],
    sfia_estimation_method: '',
  })
  
  const { sessions } = useAppSelector((state) => state.updatedEvidenceForm)
  const { evidence } = useAppSelector((state) => state.experience)
  const { allUserId, user_profile_id, user_role, trainee_id, batch } = useAppSelector(state => state.leapProfileId)

  const { makeRequest, loading } = useAxiosRequest();
  const  { fetchUserProfile } = useFetchUserProfile();

  const { handleSelectChange, handleMaxSectionChange, capitalizedOptions } = useEvidenceForm();
  const [form] = Form.useForm();
  const dispatch = useAppDispatch();
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  const handleSourceChange = (value: string) => {
    setSourceLinkMap((prevState) => ({
      ...prevState,
      name: value,
    }));
  };

  const handleLinkChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSourceLinkMap((prevState) => ({
      ...prevState,
      link: e.target.value,
    }));
  };

  const onFinish = () => {

    const evidenceData = {
      source: sourceLinkMap,
      remark: evidence?.remark,
      sentiment: "",
      confidence_degree: "",
      sfia_level_requested: evidence.sfia_level_requested?.toString() || "",
      sfia_level_approved: "",
      sfia_dimensions_approved: [],
      verified_by: "",
      sfia_dimensions_requested: (sessions && sessions.length > 0 &&
        sessions.every(session => session.name !== "" && session.level !== null))
        ? sessions.map(session => ({
          name: session.name,
          level: session.level?.toString() || ""
        }))
        : [],
      status: "Request for approval",
    };

    const data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "competencies",
          data: {
            abilities: formData.abilities || [],
            attitude: formData.attitude || [],
            knowledge: formData.knowledge || [],
            others: [],
            sfia_estimation_method: formData.sfia_estimation_method || "",
            description: formData.description,
            display: capitalizeFirstChar(formData.competency_name),
            evidence: [evidenceData],
            name: formData.competency_name,
            rationale: formData.rationale,
            sfia_level: formData.sfia_level.toString(),
            experience_level: formData.experience_level || "",
            skills: formData.skills,
            status: "draft",
          }
        }
      ],
    }
    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Added Competency: ${formData.competency_name}`,
      notificationMessageTrainee: `Added Competency: ${formData.competency_name}`,
      where: "Competencies",
      traineeLink: `/trainee/trainee-profile`,
      staffLink: `/staff/trainee_details/${allUserId}/${trainee_id}/${user_profile_id}`,
    }
    form.validateFields()
    .then(() => {
      makeRequest({
        url: '/sjob/put-user-profile',
        method: 'POST',
        data,
        onSuccess: (response) => {
          if (response.status === 200) {
            createNotification({
              variables: {
                sender: allUserId,
                group: 1,
                detail: details,
                origin: "leap",
                batch,
              },
              onCompleted(data) {
                if (data?.createNotification?.data.id) {
                  message.success("Notification created successfully");
                } else {
                  message.error("Notification creation failed");
                }
              },
            });
            message.success("Competency added successfully");
            form.resetFields();
            dispatch(setEvidence({ sfia_level_requested: 1, remark: "" }));
            dispatch(resetEvidenceForm());
            fetchUserProfile();
            setIsAddCompetenceDrawerVisible(false);
            setFormData({
              description: '',
              rationale: '',
              sfia_level: 1,
              competency_name: '',
              skills: [],
              experience_level: '',
              abilities: [],
              knowledge: [],
              attitude: [],
              sfia_estimation_method: '',
            });
          } else {
            message.error("Failed to add competency");
          }
        },
        onError: () => {
          // console.error("Error:", error);
        }
      });
    })
    .catch(() => {
      // console.error("Validate Failed:", info);
    });
  }

  return (
    <Row gutter={16} justify="center" className="add__competency__container">
      <Col span={24}>
        <Form form={form} layout="vertical" name="add__competency-form">
          <Row gutter={16} justify="center">
            <Col xs={24} lg={12}>
                <Form.Item
                    label="Competency Name"
                    name="competency_name"
                    rules={[
                      {
                        required: true,
                        message: "Please input the competency name!",
                      },
                    ]}
                  >
                    <Input
                      placeholder="Competency name"
                      onChange={(e) => setFormData({
                        ...formData,
                        competency_name: e.target.value
                      })}
                      />
                  </Form.Item>
            </Col>
            <Col xs={24} lg={12}>
            <Form.Item
                  label="Skills"
                  name="skills"
                  rules={[
                    {
                      required: true,
                      message: "Please input the competency skills!",
                    },
                  ]}
                >
                  <Select 
                     mode="tags"
                     placeholder="Skills"
                     onChange={(value) => setFormData({
                      ...formData,
                      skills: value
                    })}
                  >
                 </Select>
                </Form.Item>
            </Col>               
              <Col xs={24} lg={12}>
                <Form.Item
                  label="Description"
                  name="description"
                  rules={[
                    {
                      required: true,
                      message: "Please input the competency description!",
                    },
                  ]}
                >
                  <TextArea 
                    rows={4} 
                    placeholder="Competency description"
                    onChange={(e) => setFormData({
                      ...formData,
                      description: e.target.value
                    })}
                     />
                </Form.Item>
              </Col>
              <Col xs={24} lg={12}>
                <Form.Item
                  label="Rationale"
                  name="rationale"
                  rules={[
                    {
                      required: false,
                      message: "Please input the competency rationale!",
                    },
                  ]}
                >
                  <TextArea 
                    rows={4} 
                    placeholder="Competency rationale"
                    onChange={(e) => setFormData({
                      ...formData,
                      rationale: e.target.value
                    })}
                     />
                </Form.Item>
              </Col>
              <Col span={24}>
                <h3>Evidence</h3>
              </Col>
              <Col span={24}>
              <Row gutter={16}>
                <Col xs={24} lg={12}>
                  <Form.Item name="source"
                    rules={[{ required: true, message: 'Please select source!' }]}
                    label="Source">
                    <Select onChange={handleSourceChange}>
                      {sources.map((source) => (
                        <Select.Option key={source} value={source}>
                          {source}
                        </Select.Option>
                      ))}
                    </Select>
                </Form.Item>
                </Col>
                <Col xs={24} lg={12}>
                  <Form.Item name="link" label="Link">
                    <Input onChange={handleLinkChange} />
                </Form.Item>
                </Col>
              </Row>
              <Paragraph className="mt-8">SFIA Dimension </Paragraph>
              <Form.List
                name="sessions"
                initialValue={sessions}
                rules={[]}
              >
                {(sessions, { add, remove }) => (
                  <div style={{ display: 'flex', rowGap: 16, flexDirection: 'column' }}>
                    {sessions.map((field) => {
                      return (
                        <Card
                          size="small"
                          title={
                            <div className="d-flex-between">
                              <p style={{fontSize:"12px", fontStyle:"normal"}}>{`SFIA Dimension-${field.name + 1}`}</p>
                              {sessions.length > 0 && (
                                <Flex justify='flex-end'>
                                  <Button
                                    style={{ background: "#FF4405", color: "#FFF" }}
                                    icon={<DeleteOutlined />}
                                    onClick={() => {
                                      dispatch(removeSession(field.name));
                                      remove(field.name)
                                    }}
                                  />
                                </Flex>
                              )}
                            </div>
                          }
                          key={field.key}
                        >
                          <Row gutter={[16, 16]}>
                            <Col span={12}>
                              <Form.Item
                                label="Name"
                                name={[field.name, 'name']}
                                rules={[{ required: false, message: 'Please select SFIA Dimension name!' }]}
                                tooltip="Select SFIA Dimension"
                              >
                                <Select
                                  options={capitalizedOptions}
                                  placeholder="Select name"
                                  onChange={(value) => handleSelectChange(value, field.name)}
                                  value={field.name.toString()}
                                />
                              </Form.Item>
                            </Col>
                            <Col span={12}>
                              <Form.Item
                                label="Level"
                                name={[field.name, 'level']}
                                rules={[{ required: false, message: 'Please input level!' }]}
                                tooltip="SFIA Level starting from 1 to 5"
                              >
                                <InputNumber
                                  placeholder='Level'
                                  style={{ width: "100%" }}
                                  min={1}
                                  max={5}
                                  value={field.name}
                                  onChange={(value) => handleMaxSectionChange(value, field.name)}
                                />
                              </Form.Item>
                            </Col>

                          </Row>
                        </Card>
                      )
                    })}

                    {sessions.length < 5 && (
                      <Button type="dashed"
                        onClick={() => {
                          dispatch(addSession());
                          add();
                        }}
                        block
                        icon={<PlusOutlined />}
                      >
                        Add Item
                      </Button>
                    )}
                  </div>
                )}
              </Form.List>
              <Form.Item
                label="SFIA level requested"
                rules={[{ required: true, message: 'Please input level!' }]}
                name="sfia_level_requested" className="mt-16">
                <InputNumber
                  min={1}
                  max={7}
                  style={{ width: "100%" }}
                  value={evidence.sfia_level_requested}
                  onChange={(value) => dispatch(setEvidence({
                    ...evidence,
                    sfia_level_requested: value
                  }))}
                />
              </Form.Item>

              <Form.Item label="Remark" name="remark" className="mt-16">
                <TextArea rows={4} onChange={(e) => dispatch(setEvidence({
                  ...evidence,
                  remark: e.target.value
                }))} />
              </Form.Item>
              </Col>
              <Form.Item className="update-submit-button">
                <Popconfirm
                  title="Are you sure you want to add this competency?"
                  onConfirm={() => onFinish()}
                  onCancel={() => {
                    message.info("Competency adding cancelled");
                  }}
                  okText="Yes"
                  cancelText="No">
                  <Button className="dark-orange-bg white-color"
                    loading={loading}
                  >
                    Add Competency
                  </Button>
                </Popconfirm>
              </Form.Item>
          </Row>
        </Form>
      </Col>
    </Row>
  )
}
