import { Button, Col, DatePicker, Form, Input, message, Popconfirm, Row, Switch } from "antd";
import { useEffect, useState } from "react";
import dayjs from "dayjs";
import { useMutation } from "@apollo/client";
import { useAppDispatch, useAppSelector } from "../../../../redux/hooks/hooks";
import {resetVolunteerWork, setVolunteerId, setVolunteerWork } from "../../../../redux/slices/otherProfilesSlice";
import { formatDateToYYYYMMDD } from "../../../../utils/commonUtils";
import { CREATE_NOTIFICATION } from "../../../../graphql/mutations/createNotification";
import useFetchUserProfile from "../../../../hooks/useFetchUserProfile";
import useAxiosRequest from "../../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../../utils/getRunStage";

const run_stage = getRunStage();

const { RangePicker } = DatePicker;
const {TextArea} = Input;

type VolunteerWork = {
  setIsVolunteerModalVisible: (value: boolean) => void;
}

export default function AddVolunteerWork({setIsVolunteerModalVisible}: VolunteerWork) {
  const {volunteer, volunteerUUID} = useAppSelector(state => state.otherProfiles);
  const {allUserId, user_profile_id, user_role, trainee_id, batch} = useAppSelector(state => state.leapProfileId)
  const [isStillWorking, setIsStillWorking] = useState(false);
  const {volunteerButtonEditing} = useAppSelector(state => state.otherProfileSubmitButtons)
  const  { fetchUserProfile } = useFetchUserProfile();

  const [form] = Form.useForm();
  const dispatch = useAppDispatch();
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  useEffect(() => {
    form.setFieldsValue({
      organization: volunteer.organization,
      position: volunteer.position,
      duration: [
        volunteer.duration[0] && dayjs(volunteer.duration[0]).isValid() 
          ? dayjs(volunteer.duration[0]) 
          : dayjs(), 
        volunteer.duration[1] && dayjs(volunteer.duration[1]).isValid() 
          ? dayjs(volunteer.duration[1]) 
          : dayjs() 
      ],      
      summary: volunteer.summary,
      url: volunteer.url
    })
  } , [volunteer])
  const { makeRequest, loading } = useAxiosRequest();

  const onFinish = () => {
    let data = {}
    if(volunteer.id === volunteerUUID){
    data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "volunteer",
          uuid: volunteerUUID,
          data: {
            organization: volunteer.organization,
            position: volunteer.position,
            start_date: formatDateToYYYYMMDD(volunteer.duration[0]),
            end_date: formatDateToYYYYMMDD(volunteer.duration[1]),
            summary: volunteer.summary,
            url: volunteer.url
          }
        }
      ],
      status: "approved",  
    }
  }else {
    data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "volunteer",
          data: {
            organization: volunteer.organization,
            position: volunteer.position,
            start_date: formatDateToYYYYMMDD(volunteer.duration[0]),
            end_date: formatDateToYYYYMMDD(volunteer.duration[1]),
            summary: volunteer.summary,
            url: volunteer.url
          }
        }
      ],
      status: "approved",
    }
  }

    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Added a new volunteer work! `,
      notificationMessageTrainee: `Added a new volunteer work!`,
      where: "Volunteer Work",
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

              if (volunteer.id === volunteerUUID) {
                message.success("Volunteer work updated successfully");
              } else {
                message.success("Volunteer work added successfully");
              }
              message.success("Volunteer work added successfully");
              dispatch(resetVolunteerWork());
              setIsVolunteerModalVisible(false);
              fetchUserProfile();
              form.resetFields();
              dispatch(setVolunteerId(""));
            } else {
              console.error("Volunteer work update failed");
            }
          },
          onError: (error) => {
            console.log("Error:", error);
          }
        });
      })
      .catch((info) => {
        console.error("Validate Failed:", info);
      });
  }

  const handleWorkingRangePickerChange = (value: any) => {
    const dates = value?.map((date: any) => date ? dayjs(date).toDate().toISOString() : null) as [string, (string | null)];
    if (isStillWorking) {
      dispatch(setVolunteerWork({
        ...volunteer,
        duration: [dates[0], null]
      }));
    } else {
      dispatch(setVolunteerWork({
        ...volunteer,
        duration: [dates[0], dates[1] as string]
      }));
    }
  };

  const handleWorkSwitchChange = (checked: boolean) => {
    setIsStillWorking(checked);
    if (checked) {
      dispatch(setVolunteerWork({
        ...volunteer,
        duration: [volunteer.duration[0], null]
      }));
    }
  };

  return (
   <Row gutter={16}>
      <Col span={24}>
        <Form name="volunteer_form" form={form} layout="vertical">
          <Form.Item
            label="Organization"
            name="organization"
            rules={[{ required: true, message: 'Please input organization!' }]}>
            <Input onChange={(e)=> dispatch(setVolunteerWork({
              ...volunteer, organization: e.target.value}))}
              placeholder="Please input organization!"/>
          </Form.Item>
          <Form.Item 
                name="duration" 
                label="Duration"
                initialValue={
                  volunteer.duration.length > 0 ? [
                    volunteer.duration[0] ? dayjs(volunteer.duration[0]) : null,
                    volunteer.duration[1] ? dayjs(volunteer.duration[1]) : null]
                      : null
              }
                rules={[{ required: true, message: 'Please select duration'}]}>
          <RangePicker style={{ width: '100%' }} 
                   disabled={[false, isStillWorking]}
                   placeholder={["Start Date", "End Date"]}
                  onChange={handleWorkingRangePickerChange}/>
          </Form.Item>
            <Form.Item name="switch" label="Still Working here" colon={false}>
              <Switch 
              checked={volunteer.duration[1] === null || volunteer.duration[1]=== "" || volunteer.duration[1]=== undefined}
              onChange={handleWorkSwitchChange} />
            </Form.Item>
            <Form.Item
              label="Position"
              name="position"
              rules={[{ required: true, message: 'Please input position!' }]}>
              <Input onChange={(e)=> dispatch(setVolunteerWork({
                ...volunteer, position: e.target.value
              }))} placeholder="Please input position"/>
            </Form.Item>
              <Form.Item
                label="URL"
                name="url"
                rules={[{ required: false, type:"url", message: 'Please input url!' }]}>
              <Input onChange={(e)=> dispatch(setVolunteerWork({
                ...volunteer, url: e.target.value
              }))} placeholder="Please input url"/>
            </Form.Item>
            <Form.Item 
                  label="Description" 
                  tooltip="Experience description" 
                  colon={false}
                  name="description"
                  className="applicationForm-Ckeditor"
                  rules={[{ required: true, message: "Please input a description"}]}>
                <TextArea placeholder="Please input description" rows={4}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                      dispatch(setVolunteerWork({ ...volunteer, summary: e.target.value }))} />
          </Form.Item>
            <Form.Item className="update-submit-button">
            <Popconfirm okText="Yes" cancelText="No"
                  title="Are you sure you want to upload this volunteer work?"
                  onConfirm={() => onFinish()}
                  onCancel={() => {message.info("Profile creation cancelled")}}>
                    <Button className="dark-orange-bg white-color" loading = {loading} >
                        {volunteerButtonEditing ? "Update" : "Add Volunteer Work"}
                  </Button>
            </Popconfirm>
          </Form.Item>
        </Form>
      </Col>
   </Row>
  )
}
