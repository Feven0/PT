
import { Button, Col, Form, Input, InputNumber, message, Popconfirm, Row, Select } from "antd";
import { useEffect } from "react";
import { useMutation } from "@apollo/client";
import { useAppDispatch, useAppSelector } from "../../../../redux/hooks/hooks";
import {setReferenceUUID, setTraineeReferences } from "../../../../redux/slices/otherProfilesSlice";
import { CREATE_NOTIFICATION } from "../../../../graphql/mutations/createNotification";
import useFetchUserProfile from "../../../../hooks/useFetchUserProfile";
import useAxiosRequest from "../../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../../utils/getRunStage";

const run_stage = getRunStage()
const {TextArea} = Input;

const {Option} = Select;
type AwardsProps = {
  setIsReferenceDrawerVisible: (value: boolean) => void;
}

export default function AddReference({setIsReferenceDrawerVisible}: AwardsProps) {
  const {reference, referenceUUID} = useAppSelector(state => state.otherProfiles);
  const {allUserId, user_profile_id, user_role, trainee_id, batch} = useAppSelector(state => state.leapProfileId)
  const {referenceButtonEditing} = useAppSelector(state => state.otherProfileSubmitButtons)
  const  { fetchUserProfile } = useFetchUserProfile();

  const [form] = Form.useForm();
  const dispatch = useAppDispatch();
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  useEffect(() => {
    const parseArray = (str:string) => {
      try {
          return JSON.parse(str.replace(/'/g, '"'));
      } catch {
          return [];
      }
  };

  const parseJsonArray = (str: string) => {
    try {
        return JSON.parse(str);
    } catch (error) {
        console.error("Error parsing JSON:", error);
        return []; 
    }
  };

  const phoneArray = Array.isArray(reference.contact.phone)
      ? reference.contact.phone
      : parseArray(reference.contact.phone || '[]');

  const remarkArray = Array.isArray(reference.contact.remark)
  ? reference.contact.remark
  : parseJsonArray(reference.contact.remark || '[]'); 

    form.setFieldsValue({
      level: reference.priority,
      description: reference.reference_text,
      full_name: reference.contact.full_name,
      email: reference.contact.email,
      relationship: reference.contact.relationship,
      phone: phoneArray,
      remark: remarkArray,
    })
  }, [reference])
  const { makeRequest, loading } = useAxiosRequest();

  const onFinish = () => {
    let data = {}
    if(reference.id === referenceUUID){ 
     data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "references",
          uuid: referenceUUID,
          data: {
            priority: reference.priority,
            reference_text: reference.reference_text,
            contact: {
              full_name: reference.contact.full_name,
              email: reference.contact.email,
              relationship: reference.contact.relationship,
              phone: reference.contact.phone,
              remark: reference.contact.remark
            }
          }
        }
      ],
      status: "approved",  
    }
    }else{
      data = {
        user_role: user_role,
        run_stage: run_stage,
        all_user_id: allUserId,
        user_profile_id: user_profile_id,
        user_profile: [
          {
            code: "references",
            data: {
              priority: reference.priority,
              reference_text: reference.reference_text,
              contact: {
                full_name: reference.contact.full_name,
                email: reference.contact.email,
                relationship: reference.contact.relationship,
                phone: reference.contact.phone,
                remark: reference.contact.remark
              }
            }
          }
        ],
        status: "approved",  
      }
    }

    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Added a new reference! `,
      notificationMessageTrainee: `Added a new reference!`,
      where: "References",
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
                  console.error("Notification creation failed");
                }
              },
            });
            if (reference.id === referenceUUID) {
              message.success("Reference updated successfully");
            } else {
              message.success("Reference added successfully");
            }
            message.success("Reference added successfully"); 
            setIsReferenceDrawerVisible(false);
            dispatch(setReferenceUUID(""));
            fetchUserProfile();
            form.resetFields();
          } 
        },
        onError: () => {},
      });
    })
    .catch(() => {});
  }

  return (
   <Row gutter={16}>
      <Col span={24}>
        <Form name="reference_form" form={form} layout="vertical">
          <Form.Item
            label="Priority"
            name="level"
            rules={[
              { 
                required: true, 
                message: 'Please input priority!' 
              }]}>
            <InputNumber 
              min={1}
              max={10}
              style={{ width: '100%' }}
                onChange={
                  (value)=> dispatch(setTraineeReferences({
              ...reference, 
              priority: value as number
            }))}
              placeholder="eg. 5"/>
          </Form.Item>

            <Form.Item 
                  label="Reference" 
                  tooltip="Reference" 
                  colon={false}
                  name="description"
                  className="applicationForm"
                  rules={[{ required: true, message: "Please input a reference"}]}>
                <TextArea placeholder="Please input description" rows={4}
                      value={reference?.reference_text ? reference.reference_text : ""}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                      dispatch(setTraineeReferences({ 
                      ...reference, 
                      reference_text: e.target.value 
                      }))} />
          </Form.Item>
          <Form.Item
            label="Full Name"
            name="full_name"
            rules={[{ required: true, message: 'Please input full name!' }]}>
            <Input onChange={(e)=> dispatch(setTraineeReferences({
              ...reference, 
              contact: {
                ...reference.contact,
                full_name: e.target.value
              }
            }))}
              placeholder="Please input full name!"/>
          </Form.Item>
          <Form.Item
            label="Email"
            name="email"
            rules={[{ required: true, message: 'Please input email!' }]}>
            <Input onChange={(e)=> dispatch(setTraineeReferences({
              ...reference, 
              contact: {
                ...reference.contact,
                email: e.target.value
              }
            }))}
              placeholder="Please input email!"/>
          </Form.Item>
          <Form.Item
            label="Relationship"
            name="relationship"
            rules={[{ required: true, message: 'Please input relationship!' }]}>
            <Select
              placeholder="Please select relationship"
              onChange={(value)=> dispatch(setTraineeReferences({
                ...reference, 
                contact: {
                  ...reference.contact,
                  relationship: value
                }
              }))}>
              <Option value="You Worked together in the same group">You Worked together in the same group</Option>
              <Option value="You studied together">You studied together</Option>
            </Select>
          </Form.Item>
          <Form.Item
            label="Phone"
            name="phone"
            rules={[{ required: true, message: 'Please input phone!' }]}>
            <Select mode="tags"
              placeholder="Please input phone"
              onChange={(value)=> dispatch(setTraineeReferences({
                ...reference, 
                contact: {
                  ...reference.contact,
                  phone: value
                }
              }))}>
            </Select>
          </Form.Item>
          <Form.Item
            label="Remark"
            name="remark"
            rules={[{ required: true, message: 'Please input remark!' }]}>
            <TextArea onChange={(e)=> dispatch(setTraineeReferences({
              ...reference, 
              contact: {
                ...reference.contact,
                remark: [e.target.value]
              }
            }))}
              placeholder="Please input remark!"/>
            </Form.Item>
            <Form.Item className="update-submit-button">
            <Popconfirm okText="Yes" cancelText="No"
                  title="Are you sure you want to upload this reference?"
                  onConfirm={() => onFinish()}
                  onCancel={() => {message.info("Reference creation cancelled")}}>
                    <Button className="dark-orange-bg white-color" loading = {loading} >
                        {referenceButtonEditing ? "Update" : "Add Reference"}
                  </Button>
            </Popconfirm>
          </Form.Item>
        </Form>
      </Col>
   </Row>
  )
}
