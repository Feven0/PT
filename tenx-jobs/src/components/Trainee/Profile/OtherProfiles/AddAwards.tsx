import { Button, Col, DatePicker, Form, Input, message, Popconfirm, Row } from "antd";
import { useEffect } from "react";
import { useMutation } from "@apollo/client";
import moment from "moment";
import { useAppDispatch, useAppSelector } from "../../../../redux/hooks/hooks";
import {resetTraineeAwards, setAwardUUID, setTraineeAwards } from "../../../../redux/slices/otherProfilesSlice";
import { formatDateToYYYYMMDD } from "../../../../utils/commonUtils";
import { CREATE_NOTIFICATION } from "../../../../graphql/mutations/createNotification";
import useFetchUserProfile from "../../../../hooks/useFetchUserProfile";
import useAxiosRequest from "../../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../../utils/getRunStage";

const run_stage = getRunStage()
const {TextArea} = Input;

type AwardsProps = {
  setIsAwardModalVisible: (value: boolean) => void;
}

export default function AddAwards({setIsAwardModalVisible}: AwardsProps) {
  const {awards, awardUUID} = useAppSelector(state => state.otherProfiles);
  const {allUserId, user_profile_id, user_role, trainee_id, batch} = useAppSelector(state => state.leapProfileId)
  const {awardButtonEditing} = useAppSelector(state => state.otherProfileSubmitButtons)
  const  { fetchUserProfile } = useFetchUserProfile();

  const [form] = Form.useForm();
  const dispatch = useAppDispatch();
  const { makeRequest, loading } = useAxiosRequest();
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  useEffect(() => {
    form.setFieldsValue({
      awarder: awards.awarder,
      title: awards.title,
      date: awards.date && moment(awards.date).isValid() ? moment(awards.date) : moment(),
      description: awards.summary,
      url: awards.url
    })
  }, [awards])

  const onFinish = () => {
    let data = {}
    if(awards.id === awardUUID) {
     data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "awards",
          uuid: awardUUID,
          data: {
            awarder: awards.awarder,
            title: awards.title,
            date: formatDateToYYYYMMDD(awards.date),
            summary: awards.summary,
            url: awards.url
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
            code: "awards",
            data: {
              awarder: awards.awarder,
              title: awards.title,
              date: formatDateToYYYYMMDD(awards.date),
              summary: awards.summary,
              url: awards.url
            }
          }
        ],
        status: "approved",  
      }
    }

    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Added a new award! `,
      notificationMessageTrainee: `Added a new award!`,
      where: "Awards",
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
                batch: batch,
              },
              onCompleted(data) {
                if (data?.createNotification?.data.id) {
                  message.success("Notification created successfully");
                } else {
                  console.error("Notification creation failed");
                }
              },
            });

            if (awards.id === awardUUID) {
              message.success("Award updated successfully");
            } else {
              message.success("Award added successfully");
            }
            message.success("Award added successfully");
            dispatch(resetTraineeAwards());
            setIsAwardModalVisible(false);
            dispatch(setAwardUUID(""));
            fetchUserProfile();
            form.resetFields();
          } 
        },
        onError: () => {}
      });
    })
    .catch(() => {});
  }

  return (
   <Row gutter={16}>
      <Col span={24}>
        <Form name="award_form" form={form} layout="vertical">
          <Form.Item
            label="Awarding Organization"
            name="awarder"
            rules={[{ required: true, message: 'Please input organization!' }]}>
            <Input onChange={(e)=> dispatch(setTraineeAwards({
              ...awards, awarder: e.target.value}))}
              placeholder="Please input Awarding organization!"/>
          </Form.Item>
          <Form.Item
              label="Title"
              name="title"
              rules={[{ required: true, message: 'Please input award title!' }]}>
              <Input onChange={(e)=> dispatch(setTraineeAwards({
                ...awards, title: e.target.value
              }))} placeholder="Please input award title"/>
            </Form.Item>
          <Form.Item 
                name="date" 
                label="Date"
                rules={[{ required: true, message: 'Please select duration'}]}>
              <DatePicker 
                style={{ width: '100%' }} 
                onChange={(_date, dateString) => {
                  if (typeof dateString === 'string') {
                    dispatch(setTraineeAwards({
                      ...awards, 
                      date: dateString
                    }));
                  }
                }}
              />
          </Form.Item>
          <Form.Item
              label="URL"
              name="url"
              rules={[{ required: false, message: 'Please input award url!' }]}>
              <Input onChange={(e)=> dispatch(setTraineeAwards({
                ...awards, url: e.target.value
              }))} placeholder="Please input award url if any"/>
            </Form.Item>
            <Form.Item 
                  label="Description" 
                  tooltip="Award description" 
                  colon={false}
                  name="description"
                  className="applicationForm-Ckeditor"
                  rules={[{ required: true, message: "Please input a description"}]}>
                <TextArea placeholder="Please input description" rows={4}
                      value={awards.summary}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                      dispatch(setTraineeAwards({ ...awards, summary: e.target.value }))} />
          </Form.Item>
            <Form.Item className="update-submit-button">
            <Popconfirm okText="Yes" cancelText="No"
                  title="Are you sure you want to upload this award?"
                  onConfirm={() => onFinish()}
                  onCancel={() => {message.info("Profile creation cancelled")}}>
                    <Button className="dark-orange-bg white-color" loading = {loading} >
                        {awardButtonEditing ? "Update" : "Add Award"}
                  </Button>
            </Popconfirm>
          </Form.Item>
        </Form>
      </Col>
   </Row>
  )
}
