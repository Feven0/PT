import { Button, Card, Col, Flex, Form, InputNumber, message, Popconfirm, Row, Select, Typography } from "antd";
import { useEffect, useState } from "react";
import { DeleteOutlined, PlusOutlined } from "@ant-design/icons";

import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import useEvidenceForm from "../../../hooks/useEvidenceForm";
import { setRequestedData } from "../../../redux/slices/evidenceApprovalSlice";
import { addSession, removeSession } from "../../../redux/slices/updateEvidenceSlice";

const { Paragraph } = Typography

type ApproveEvidenceProps = {
  uuid: string;
  setIsEvidenceEditOn: (value: boolean) => void;
}

export default function ChangeEvidenceStatus({ setIsEvidenceEditOn }: ApproveEvidenceProps) {
  const { requestedData } = useAppSelector((state) => state.evidenceApproval);
  const { evidence } = useAppSelector((state) => state.experience)
  const [status, setStatus] = useState("approved")
  const [form] = Form.useForm();

  const dispatch = useAppDispatch()
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
      sentiment: value.toLowerCase() || "neutral"
    }));
  };

  const handleConfidenceChange = (value: string) => {
    dispatch(setRequestedData({
      ...requestedData,
      confidence_degree: value || "medium"
    }));
  };

  const onFinish = () => setIsEvidenceEditOn(false);

  return (
    <Row gutter={16}>
      <Col span={24}>
        <Form layout="vertical" form={form}
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
              <Button className="dark-orange-bg white-color">
                Save
              </Button>
            </Popconfirm>
          </Form.Item>
        </Form>
      </Col>
    </Row>
  )
}
