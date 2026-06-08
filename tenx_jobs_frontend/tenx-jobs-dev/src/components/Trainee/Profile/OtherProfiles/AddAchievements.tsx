import { Button, Col, DatePicker, Form, Input, message, Popconfirm, Row } from "antd";
import { useEffect } from "react";
import { useMutation } from "@apollo/client";
import moment from "moment";
import { useAppDispatch, useAppSelector } from "../../../../redux/hooks/hooks";
import {setAchievementUUID, setTraineeAchievements } from "../../../../redux/slices/otherProfilesSlice";
import { formatDateToYYYYMMDD } from "../../../../utils/commonUtils";
import { CREATE_NOTIFICATION } from "../../../../graphql/mutations/createNotification";
import useFetchUserProfile from "../../../../hooks/useFetchUserProfile";
import useAxiosRequest from "../../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../../utils/getRunStage";

const run_stage = getRunStage()
const {TextArea} = Input;

type AwardsProps = {
  setIsAchievementDrawerVisible: (value: boolean) => void;
}

export default function AddAchievements({setIsAchievementDrawerVisible}: AwardsProps) {
  const {achievements, achievementUUID} = useAppSelector(state => state.otherProfiles);
  const {allUserId, user_profile_id, user_role, trainee_id, batch} = useAppSelector(state => state.leapProfileId)
  const {achievementButtonEditing} = useAppSelector(state => state.otherProfileSubmitButtons)
  const  { fetchUserProfile } = useFetchUserProfile();

  const [form] = Form.useForm();
  const dispatch = useAppDispatch();
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  useEffect(() => {
    form.setFieldsValue({
      title: achievements?.title || "",
      date: achievements?.date && moment(achievements.date).isValid() ? moment(achievements.date) : moment(),
      description: achievements?.summary || "",
    })
  }, [achievements])
  const { makeRequest, loading } = useAxiosRequest();

  const onFinish = () => {
    let data = {}
    if(achievements.id === achievementUUID) {
     data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "achievements",
          uuid: achievementUUID,
          data: {
            title: achievements.title,
            date: formatDateToYYYYMMDD(achievements.date),
            summary: achievements.summary,
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
            code: "achievements",
            data: {
              title: achievements.title,
              date: formatDateToYYYYMMDD(achievements.date),
              summary: achievements.summary,
            }
          }
        ],
        status: "approved",  
      }
    }

    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Added a new achievement! `,
      notificationMessageTrainee: `Added a new achievement!`,
      where: "Achievements",
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

              if (achievements.id === achievementUUID) {
                message.success("Achievement updated successfully");
              } else {
                message.success("Achievement added successfully");
              }
              setIsAchievementDrawerVisible(false);
              dispatch(setAchievementUUID(""));
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
        <Form name="achievements_form" form={form} layout="vertical">
          <Form.Item
            label="Achievement Title"
            name="title"
            rules={[{ required: true, message: 'Please input achievement title!' }]}>
            <Input onChange={(e)=> dispatch(setTraineeAchievements({
              ...achievements, 
              title: e.target.value
            }))}
              placeholder="Please input achievement title!"/>
          </Form.Item>
          <Form.Item 
                name="date" 
                label="Date"
                rules={[{ required: true, message: 'Please select date'}]}>
              <DatePicker 
                style={{ width: '100%' }} 
                onChange={(_date, dateString) => {
                  if (typeof dateString === 'string') {
                    dispatch(setTraineeAchievements({
                      ...achievements, 
                      date: dateString
                    }));
                  }
                }}
              />
          </Form.Item>
            <Form.Item 
                  label="Description" 
                  tooltip="Award description" 
                  colon={false}
                  name="description"
                  className="applicationForm"
                  rules={[{ required: true, message: "Please input a description"}]}>
                <TextArea placeholder="Please input description" rows={4}
                      value={achievements?.summary ? achievements.summary : ""}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                      dispatch(setTraineeAchievements({ 
                      ...achievements, 
                      summary: e.target.value 
                      }))} />
          </Form.Item>
            <Form.Item className="update-submit-button">
            <Popconfirm okText="Yes" cancelText="No"
                  title="Are you sure you want to upload this achievement?"
                  onConfirm={() => onFinish()}
                  onCancel={() => {message.info("Achievement creation cancelled")}}>
                    <Button className="dark-orange-bg white-color" loading = {loading} >
                        {achievementButtonEditing ? "Update" : "Add Achievement"}
                  </Button>
            </Popconfirm>
          </Form.Item>
        </Form>
      </Col>
   </Row>
  )
}
