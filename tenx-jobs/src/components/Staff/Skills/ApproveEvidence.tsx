import { Button, Card, Col, Flex, Form, InputNumber, message, Popconfirm, Row, Select, Typography } from "antd";
import { useEffect, useState } from "react";
import { useMutation } from "@apollo/client";
import { useParams } from "react-router-dom";
import { DeleteOutlined, PlusOutlined } from "@ant-design/icons";

import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import useEvidenceForm from "../../../hooks/useEvidenceForm";
import { setRequestedData } from "../../../redux/slices/evidenceApprovalSlice";
import { CREATE_NOTIFICATION } from "../../../graphql/mutations/createNotification";
import useFetchTraineeProfileForStaff from "../../../hooks/useFetchTraineeProfileForStaff";
import { addSession, removeSession } from "../../../redux/slices/updateEvidenceSlice";
import useAxiosRequest from "../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../utils/getRunStage";

const { Paragraph } = Typography
const run_stage = getRunStage();

type ApproveEvidenceProps = {
  uuid: string;
  setIsEvidenceEditOn: (value: boolean) => void;
}

export default function ApproveEvidence({ uuid, setIsEvidenceEditOn }: ApproveEvidenceProps) {
  const [status, setStatus] = useState("approved")
  const { allUserID  } = useParams()
  const { user_profile_id } = useParams()
  const { trainee_id } = useParams()

  const { requestedData, sfia_level } = useAppSelector((state) => state.evidenceApproval);
  const { evidence } = useAppSelector((state) => state.experience)
  const { user_role, batch } = useAppSelector(state => state.leapProfileId)
  const { competencies } = useAppSelector((state) => state.traineeProfileResponse.user_profile)
  const competency = competencies?.attributes?.filter((competency) => competency.uuid === uuid)[0]

  const dispatch = useAppDispatch()
  const [form] = Form.useForm();
  const [createNotification] = useMutation(CREATE_NOTIFICATION);
  const fetchUserProfile = useFetchTraineeProfileForStaff({ allUserID, user_profile_id });
  const { capitalizedOptions } = useEvidenceForm();

  useEffect(() => {
    dispatch(setRequestedData({
      ...requestedData,
      verified_by: "Staff",
      sfia_level_requested: requestedData.sfia_level_requested,
      requested_by: "Trainee",
      status: status,
    }))
  }, [])

  const { makeRequest, loading } = useAxiosRequest();

  const handleSelectChange = (value: string, index: number) => {
    const updatedDimensionsApproved = [...requestedData.sfia_dimensions_approved];

    const updatedDimension = {
      ...requestedData.sfia_dimensions_requested[index],
      name: value,
    };

    const existingIndex = updatedDimensionsApproved.findIndex((dimension) =>
      dimension.name === updatedDimension.name && dimension.level === updatedDimension.level
    );

    if (existingIndex !== -1) {
      updatedDimensionsApproved[existingIndex] = updatedDimension;
    } else {
      updatedDimensionsApproved.push(updatedDimension);
    }
  };

  const handleLevelChange = (value: number | null, index: number) => {
    if (value === null) return;

    const updatedApprovedDimensions = [...requestedData.sfia_dimensions_approved];
    const updatedDimension = {
      ...requestedData.sfia_dimensions_requested[index],
      level: value,
    };

    const existingIndex = updatedApprovedDimensions.findIndex((dimension) =>
      dimension.name === updatedDimension.name
    );

    if (existingIndex !== -1) {
      updatedApprovedDimensions[existingIndex] = updatedDimension;
    } else {
      updatedApprovedDimensions.push(updatedDimension);
    }

    dispatch(setRequestedData({
      ...requestedData,
      sfia_dimensions_approved: updatedApprovedDimensions,
    }));
  };

  const handleSentimentChange = (value: string) => {
    dispatch(setRequestedData({
      ...requestedData,
      sentiment: value.toLowerCase()
    }));
  };

  const handleConfidenceChange = (value: string) => {
    dispatch(setRequestedData({
      ...requestedData,
      confidence_degree: value
    }));
  };

  const onFinish = () => {
    const updatedEvidence = competency.evidence.map((evidence, index) => {
      if (index.toString() === requestedData.key) {
        const updatedData = { ...requestedData };
        delete updatedData.key;
        return updatedData;
      }
      return evidence;
    });

    const data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserID,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "competencies",
          uuid: uuid,
          data: {
            abilities: competency?.abilities,
            attitude: competency?.attitude,
            description: competency?.description,
            display: competency?.display,
            evidence: updatedEvidence,
            experience_level: competency?.experience_level,
            history: competency?.history,
            knowledge: competency?.knowledge,
            rationale: competency?.rationale,
            name: competency?.name,
            others: competency?.others,
            skills: competency?.skills,
            sfia_level: sfia_level,
          },
        },
      ],
      status: status,
    }
    
    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Updated Evidences! `,
      notificationMessageTrainee: `Updated Evidences!`,
      where: "Competencies",
      traineeLink: `/trainee/trainee-profile`,
      staffLink: `/staff/trainee_details/${allUserID}/${trainee_id}/${user_profile_id}`,
    }
      makeRequest({
        url: '/sjob/put-user-profile',
        method: 'POST',
        data: data,
        onSuccess: (response) => {
          if (response.status === 200) {
          createNotification({
            variables: {
              sender: allUserID,
              group: 1,
              detail: details,
              origin: "leap",
              batch: batch,
            },
            onCompleted: (notificationData) => {
              if (notificationData?.createNotification?.data.id) {
                message.success("Notification created successfully");
              } else {
                message.error("Notification creation failed");
              }
            }
          });
          form.resetFields();
          fetchUserProfile();
          setIsEvidenceEditOn(false);
          setStatus("approved");
          message.success("Evidence approved successfully");
        } else {
          message.error("Evidence approval failed");
        }
        },
        onError: (error) => {
          message.error("Error approving evidence:", error);
        }
      });
  }

  return (
    <Row gutter={16}>
      <Col span={24}>
        <Form layout="vertical"
          initialValues={{
            sfia_level_requested: requestedData?.sfia_level_requested,
            sentiment: evidence.sentiment || "neutral",
            confidence_degree: evidence.confidence_degree || "medium",
          }}
          onFinish={onFinish}>
          <Paragraph>SFIA Dimensions to be approved</Paragraph>
          <Form.List
            name="sessions"
            initialValue={requestedData?.sfia_dimensions_requested}
            rules={[]}
          >
            {(sessions, { remove, add }) => (
              <div style={{ display: 'flex', rowGap: 16, flexDirection: 'column' }}>
                {sessions.map((field, index) => {
                  return (
                    <Card
                      size="small"
                      title={
                        <div className="d-flex-between">
                          <span>{`SFIA Dimension-${field.name + 1}`}</span>
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
                            rules={[{ required: true, message: 'Please select SFIA_Dimension name!' }]}
                            tooltip="Select SFIA_Dimension"
                          >
                            <Select
                              options={capitalizedOptions}
                              placeholder="Select name"
                              onChange={(value) => handleSelectChange(value, index)}
                              value={field.name.toString()}
                            />
                          </Form.Item>
                        </Col>
                        <Col span={12}>
                          <Form.Item
                            label="Level"
                            name={[field.name, 'level']}
                            rules={[{ required: true, message: 'Please input level!' }]}
                            tooltip="SFIA Level starting from 1 to 4"
                          >
                            <InputNumber
                              placeholder='Level'
                              style={{ width: "100%" }}
                              min={1}
                              max={5}
                              value={field.name}
                              onChange={(value) => handleLevelChange(value as number, index)}
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
          <Form.Item label="SFIA level requested" name="sfia_level_requested" className="mt-16">
            <InputNumber
              min={1}
              max={7}
              style={{ width: "100%" }}
              value={requestedData?.sfia_level_requested}
              readOnly
            />
          </Form.Item>
          <Form.Item label="SFIA level approved" name="sfia_level_approved" className="mt-16">
            <InputNumber
              min={1}
              max={7}
              style={{ width: "100%" }}
              onChange={(value) => dispatch(setRequestedData({
                ...requestedData,
                sfia_level_approved: value
              }))}
            />
          </Form.Item>
          <Form.Item
            label="Sentiment"
            rules={[{ required: true, message: 'Please input sentiment!' }]}
            name="sentiment">
            <Select
              defaultValue="neutral"
              placeholder="Select Sentiment"
              value={evidence.sentiment}
              onChange={handleSentimentChange}
            >
              <Select.Option value="neutral">Neutral</Select.Option>
              <Select.Option value="positive">Positive</Select.Option>
              <Select.Option value="negative">Negative</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            label="Confidence Degree"
            rules={[{ required: true, message: 'Please select confidence degree!' }]}
            name="confidence_degree">
            <Select
              defaultValue="medium"
              placeholder="Select Confidence Degree"
              value={evidence.confidence_degree}
              onChange={handleConfidenceChange}
            >
              <Select.Option value="medium">Medium</Select.Option>
              <Select.Option value="high">High</Select.Option>
              <Select.Option value="low">Low</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Status"
            rules={[{ required: true, message: 'Please select status!' }]}
            name="status">
            <Select
              defaultValue="approved"
              placeholder="Select selected status"
              value={status}
              onChange={(value) => setStatus(value)}
            >
              <Select.Option value="approved">Approved</Select.Option>
              <Select.Option value="rejected">Rejected</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item className="skill-submit-button">
            <Popconfirm
              title="Are you sure you want to approve this evidence?"
              onConfirm={() => onFinish()}
              onCancel={() => {
                message.info("Evidence approving cancelled");
              }}
              okText="Yes"
              cancelText="No">
              <Button className="dark-orange-bg white-color"
                loading={loading}
              >
                Save
              </Button>
            </Popconfirm>
          </Form.Item>
        </Form>
      </Col>
    </Row>
  )
}
