import { useRef, useState, useCallback, useEffect } from 'react';
import { Modal, Form, Row, Col, App, Button, Popconfirm, Select, Divider, Input, Typography, Space, InputRef } from 'antd';
import { useParams } from 'react-router-dom';
import { getSingularPluralString } from "../../../utils/getSingularPluralString";
import { useAppDispatch, useAppSelector } from '../../../redux/hooks/hooks';
import { CREATE_NOTIFICATION } from "../../../graphql/mutations/createNotification";
import { PlusOutlined } from '@ant-design/icons';
import { ApplicationStatusFilterOptions } from "../../../utils/ApplicationStatusFilterOptions";
import { useMutation } from '@apollo/client';
import useAxiosRequest from "../../../hooks/useAxiosRequest";
import { resetSelectedRows } from "../../../redux/slices/tableExtension";
import { getRunStage } from "../../../utils/getRunStage";

type ApplyStatusFormProps = {
  setVisible: (visible: boolean) => void;
  refetch: () => void;
  apply_status?: string;
  idList?: {
    user_reaction_id: number;
    job_trainee_id: number;
    job_id: number;
  },
  isExpandDetails?: boolean;
  setIsExpandDetails?: (value: boolean) => void;
  }

const { Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const run_stage = getRunStage();

export default function ApplyStatusForm({ setVisible, refetch, apply_status, idList, isExpandDetails, setIsExpandDetails }: ApplyStatusFormProps) {
  const [form] = Form.useForm();
  const { message } = App.useApp();
  const { user_role } = useAppSelector((state) => state.leapProfileId);
  const {user_profile_id, all_user_id} = useParams()
  const [response, setResponse] = useState<any>(null);
  const trainee_id = useAppSelector(state => state.IdList.trainee_id)

  const {allUserId} = useAppSelector(state => state.leapProfileId)
  const inputRef = useRef<InputRef>(null);
  const { selectedRows } = useAppSelector((state) => state.tableExtension);
  const [items, setItems] = useState(() => {
    const baseItems = ApplicationStatusFilterOptions();
    
    if (user_role === "Staff") {
      return [{ value: 'Applied(System)', text: 'Applied(System)' }, ...baseItems];
    }
    return baseItems;
  });

  const { makeRequest, loading, error } = useAxiosRequest();
  const dispatch = useAppDispatch();
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  const addItem = useCallback(() => {
    const name = form.getFieldValue('newStatus');
    if (!name) return;

    setItems((prevItems) => [...prevItems, { value: name, text: name }]);
    form.setFieldsValue({ newStatus: '' });
    setTimeout(() => inputRef.current?.focus(), 0);
  }, [form]);
 
  const handleCreateCancel = useCallback(() => {
    setVisible(false);
    setIsExpandDetails && setIsExpandDetails(false);
    form.resetFields();
  }, [setVisible, form]);

  const onFinish = useCallback((values: { applicationStatus: string, description: string }) => {
    const id_list = selectedRows.map((row: any) => ({
      user_reaction_id: row.user_reaction_id,
      job_trainee_id: row.job_trainee_id || "",
      job_id: row.job_id,
    }));
      const requestData = {
        user_role: user_role,
        run_stage: run_stage,
        all_user_id: all_user_id,
        trainee_id: trainee_id,
        id_list: idList ? [idList] : id_list,
        application_status: values.applicationStatus,
        description: values.description,
      };
      makeRequest({
        url: '/sjob/put-job-application-status',
        method: 'POST',
        data: requestData,
        onSuccess: (response) => {
          if (response.status === 200) {
            setResponse(response);
            dispatch(resetSelectedRows());
            message.success("Job status updated successfully");
          }
        },
        onError: () => {}
      });
  }, []);

  useEffect(() => {
    if (error) {
      handleCreateCancel()
    }

    if (response) {
      if (response.status === 200) {
        let successCount = 0;
        let failureCount = 0;
        response?.feedback?.forEach((feedback:any) => {
          if (feedback.status === 200) {
            successCount++;
          } else if (feedback.status === 400) {
            failureCount++;
          }
        });
        if (successCount > 0) {
          createNotification({
            variables: {
              sender: allUserId,
              group: 1,
              details: {
                traineeId: trainee_id,
                notificationMessageTeam: "Added job status",
                notificationMessageTrainee: "Updated job status",
                where: "Engagement",
                traineeLink: "/trainee/my-jobs",
                staffLink: `staff/trainee_engagements/${all_user_id}/${user_profile_id}`,
              }
            },
            onCompleted(data){
              if (data?.createNotification?.data.id) {
              message.success("Notification Created Successfully")
              }
            }
          })
         message.success(`${successCount} out of ${selectedRows.length} records updated successfully`);
        }
        
        if (failureCount > 0) {
          message.error(`${failureCount} out of ${selectedRows.length} records were failed to update`);
        }
        setVisible(false);
        refetch();
        handleCreateCancel();
      }
    }
  }
  , [error, response]);


  const dropdownRender = (menu: React.ReactNode) => (
    <>
      {menu}
      <Divider style={{ margin: '8px 0' }} />
      <Space style={{ padding: '0 8px 4px' }}>
        <Form.Item name="newStatus" noStyle>
          <Input placeholder="Add new Status" ref={inputRef} />
        </Form.Item>
        <Button type="text" icon={<PlusOutlined />} onClick={addItem}>
          Add
        </Button>
      </Space>
    </>
  );
  

  return (
    <Modal
      title={<div style={{
        borderBottom: "1px solid #E8E8E8",
      }}><span>Change Status</span></div>}
      open={true}
      onCancel={handleCreateCancel}
      footer={null}
    >
      <Form
        form={form}
        className="mt-16"
        layout="vertical"
        onFinish={onFinish}
        autoComplete="off"
      >
        {
          !isExpandDetails && <span style={{ fontSize: "1rem", marginBottom: "1rem" }}>
          You have selected {getSingularPluralString(selectedRows.length, 'row')}
        </span>
        }
        <Form.Item
          name="applicationStatus"
          tooltip="Your current application status"
          initialValue={apply_status}
          label={<Text className='job_label--element'>Status</Text>}
          rules={[{ required: true, message: 'Please select a status' }]}
        >
          <Select
            placeholder="Select"
            dropdownRender={dropdownRender}
            value={apply_status}
            onChange={(value) => form.setFieldsValue({ applicationStatus: value })}
          >
            {items.map(item => (
              <Option key={item.value} value={item.value}>
                {item.text}
              </Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item
          name="description"
          tooltip="Add short description for the job status update"
          label={<Text className='job_label--element'>Status Description</Text>}
          rules={[{ type: 'string', min: 2 }]}
        >
          <TextArea
            placeholder="Add description for the status (optional)"
            maxLength={250}
          />
        </Form.Item>
        <Form.Item>
          <Row gutter={[16, 16]}>
            <Col span={24}>
              <Space>
                <Popconfirm
                  title="Are you sure you want to update this apply status?"
                  onConfirm={form.submit}
                  onCancel={() => message.info("Apply status updating cancelled")}
                  okText="Yes"
                  cancelText="No"
                >
                  <Button
                    className="dark-orange-bg white-color"
                    loading={loading}
                  >
                    Update
                  </Button>
                </Popconfirm>
                <Button type="text" style={{ color: "#F5222D" }} onClick={handleCreateCancel}>
                  Cancel
                </Button>
              </Space>
            </Col>
          </Row>
        </Form.Item>
      </Form>
    </Modal>
  );
}
