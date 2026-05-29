import { Button, Col, Divider, Form, Input, InputRef, message, Row, Select, Space, Typography } from 'antd';
import React, {useRef, useState } from 'react'
import { PlusOutlined, } from "@ant-design/icons";
import { useMutation } from '@apollo/client';

//Redux and Custom Hooks
import { useAppSelector } from "../../redux/hooks/hooks";

//GraphQL queries
import { CREATE_NOTIFICATION } from "../../graphql/mutations/createNotification";

//Utility Functions
import { ApplicationStatusFilterOptions } from "../../utils/ApplicationStatusFilterOptions";
import NoFile from "../commonComponents/NoFile";
import { useParams } from "react-router-dom";
import ServerError from "../commonComponents/ServerError";
import useUserReactions from "../../hooks/useUserReactions";
import StaffDataLoader from "../commonComponents/StaffDataLoader";
import useAxiosRequest from "../../hooks/useAxiosRequest";
import { getRunStage } from "../../utils/getRunStage";
// import '../../../styles/Jobs.css'

const { TextArea } = Input;

 const { Text } = Typography

 export type JobStatus = {
  setIsModalVisible: React.Dispatch<React.SetStateAction<boolean>>;
  jobId?: string | number;
 }

 const run_stage = getRunStage();

export default function AddJobStatus({ setIsModalVisible }: JobStatus) {
  const [name, setName] = useState('');
  const [items, setItems] = useState(ApplicationStatusFilterOptions());
  const { allUserId,  user_role, trainee_id, user_profile_id } = useAppSelector((state) => state.leapProfileId)
  const {id} = useParams() as {id: string}

  const { loading, error, response, sendResult } = useUserReactions()
  const { makeRequest, loading:formLoading } = useAxiosRequest();

    const [createNotification] = useMutation(CREATE_NOTIFICATION);

    const inputRef = useRef<InputRef>(null);

      const returnUserIds = response?.reactions[0]?.data
      .filter((item: any) => item.user_reaction_id === id)
      .map((item: any) => ({
        user_reaction_id: item.user_reaction_id,
        job_id: item.job_id,
        job_trainee_id: item.job_trainee_id,
      }));

    const onNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setName(event.target.value);
    };

    const [form] = Form.useForm();
    const { Option } = Select;

    const addItem = (e: React.MouseEvent<HTMLAnchorElement>) => {
        e.preventDefault();
        setItems([...items, { value: name || `New item ${items.length + 1}`, text: name || `New item ${items.length + 1}` }]);
        setName('');
        setTimeout(() => {
            inputRef.current?.focus();
        }, 0);
    };

    const onFinish = (values: any) => {
        const postData = { 
          user_role: user_role,
          run_stage: run_stage,
          all_user_id: allUserId,
          trainee_id: trainee_id,
          id_list: returnUserIds,
          application_status: values.applicationStatus,
          description: values.description,
        }    
        form.validateFields().then(() => {      
          makeRequest({
            url: '/sjob/put-job-application-status',
            method: 'POST',
            data: postData,
            onSuccess: (response) => {
              if(response.status === 200) {
              createNotification({
                variables: {
                  sender: allUserId,
                  group: 1,
                  details: {
                    traineeId: trainee_id,
                    notificationMessageTeam: "Added job status",
                    notificationMessageTrainee: "Updated job status",
                    where: "Engagement",
                    traineeLink: `trainee/reaction_expand/details/${id}`,
                    staffLink: `/staff/trainee_details/${allUserId}/${trainee_id}/${user_profile_id}`,
                  },
                },
                onCompleted(data) {
                  if (data?.createNotification?.data.id) {
                    message.success("Notification Created Successfully");
                  }
                },
              });
              message.success("Job status updated successfully");
              setIsModalVisible(false);
              sendResult();
              window.location.reload(); 
            }else {
              message.error('Error updating records');
            }
          },
            onError: () => {},
          });
      
          form.resetFields(); 
        }).catch(() => {});
    }
  
    const handleCreateCancel = () => {
        setIsModalVisible(false)
        form.resetFields();
    };

  if (!response) return  <NoFile/> 
  if (loading) return <StaffDataLoader />
  if (error) return <ServerError/>

    return (
        <Form
            form={form}
            layout="vertical"
            onFinish={onFinish}
            autoComplete="off">
            <Form.Item
                name="applicationStatus"
                tooltip='Your current application status'
                initialValue={'Interested'}
                label={<Text className='job_label--element'>Status</Text>}
                rules={[{ required: true }, 
                        { type: 'string', warningOnly: true }, 
                        { type: 'string', min: 2 }]}>
                <Select
                    defaultValue={'Interested'}
                    placeholder="select"
                    dropdownRender={menu => (
                        <>
                            {menu}
                            <Divider style={{ margin: '8px 0' }} />
                            <Space style={{ padding: '0 8px 4px' }}>
                                <Input
                                    placeholder="Add new Status"
                                    ref={inputRef}
                                    value={name}
                                    onChange={onNameChange} />
                                  <Button className="dark-orange-bg white-color" type="text" icon={<PlusOutlined />} onClick={addItem}>
                                      Add
                                  </Button>
                            </Space>
                        </>
                    )}>
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
                rules={[{ type: 'string', warningOnly: true }, { type: 'string', min: 2 }]}>
                <TextArea placeholder="Add description for the status(optional)" maxLength={250} />
            </Form.Item>
            <Form.Item>
                <Row gutter={[16, 16]}>
                    <Col>
                        <Space>
                            <Button 
                                loading={formLoading}
                                className="white-color dark-orange-bg" 
                                htmlType="submit">
                                Submit
                            </Button>
                            <Button type="text" style={{ color: "#F5222D" }} onClick={handleCreateCancel}>
                                Cancel
                            </Button>
                        </Space>
                    </Col>

                </Row>
            </Form.Item>
        </Form>

    )
}