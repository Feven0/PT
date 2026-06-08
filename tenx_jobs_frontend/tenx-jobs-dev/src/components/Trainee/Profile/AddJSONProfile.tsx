import {Button, Form, message, Popconfirm, Upload } from "antd";
import { InboxOutlined } from '@ant-design/icons';
import type {UploadProps } from 'antd';
import { useMutation } from "@apollo/client";

//Components
import JSONEditor from "./JSONEditor";

//Redux and Custom hooks
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { resetProfileJson, setProfileJson } from "../../../redux/slices/profileUploadSlice";
import { CREATE_NOTIFICATION } from "../../../graphql/mutations/createNotification";
import useAxiosRequest from "../../../hooks/useAxiosRequest";
import useFetchUserProfile from "../../../hooks/useFetchUserProfile";
import { getRunStage } from "../../../utils/getRunStage";
import { useState } from "react";

const { Dragger } = Upload;
const run_stage = getRunStage();

type ProfileData = {
  setUploadProfileModal: (value: boolean) => void;
}

export default function AddJSONProfile({setUploadProfileModal}: ProfileData) {
  const {profileJson} = useAppSelector(state => state.profileUpload);
  const {user_role, allUserId, user_profile_id, batch, trainee_id} = useAppSelector(state => state.leapProfileId)
  const {profile} = profileJson;
  const [fileList, setFileList] = useState<any[]>([])

  const dispatch = useAppDispatch();
  const [form] = Form.useForm()
  const [createNotification] = useMutation(CREATE_NOTIFICATION);
  const { makeRequest, loading } = useAxiosRequest();
  const  { fetchUserProfile } = useFetchUserProfile();

  const props: UploadProps = {
    name: 'file',
    multiple: false, 
    accept: ".json",
    fileList,
    beforeUpload(file) {
      if (file.type === 'application/json') {
        const reader = new FileReader();
        reader.onload = (event) => {
          dispatch(setProfileJson({
            ...profileJson,
            profile: event.target?.result as string
          }))
        };
        reader.readAsText(file);
        setFileList([file]); 
      } else {
        console.error('Please upload a JSON file');
      }
      return false;
    },
    onDrop(e) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/json') {
        const reader = new FileReader();
        reader.onload = (event) => {
          dispatch(setProfileJson({
            ...profileJson,
            profile: event.target?.result as string
          }))
        };
        reader.readAsText(file);
        setFileList([file]);
      } else {
        console.error('Please drop a JSON file');
      }
      return false; 
    },
    onRemove: () => {
      dispatch(setProfileJson({
        ...profileJson,
        profile: ""
      }))
      setFileList([]);
    }
  };

  const onFinish = () => {
    const postData = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: JSON.parse(profile),
      status: ""
    }

    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Added a new profile! `,
      notificationMessageTrainee: `Added a new profile!`,
      where: "Skills",
      traineeLink: `/trainee/trainee-profile`,
      staffLink: `/staff/trainee_details/${allUserId}/${trainee_id}/${user_profile_id}`,
    }

    makeRequest({
      url: '/sjob/post-linkedin-profile-export',
      method: 'POST',
      data: postData,
      onSuccess: (response) => {
        if(response.status === 200) {
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
              message.error("Notification creation failed");
            }
          }
        });
        message.success("Profile uploaded successfully");
        dispatch(resetProfileJson());
        form.resetFields();
        setUploadProfileModal(false);
        fetchUserProfile();
      } else {
        message.error("Profile upload failed");
        }
      },
      onError: (error) => {
        message.error(`Profile upload failed:, ${error}`);
      }
    });
  }

  return (
        <Form 
          name="json-form"
          form ={form}
          layout="vertical">
            <Form.Item colon={false} name="image"
               className="manual-rubrics-dragger-wrapper"
                tooltip="Application form image">
                    <Dragger {...props} maxCount={1}>
                        <p className="ant-upload-drag-icon">
                            <InboxOutlined style={{ color: "#FF4405" }} type="inbox" accept=".json" />
                        </p>
                        <p className="ant-upload-text">Click or drag file to this area to upload</p>
                    </Dragger>
                </Form.Item>

                <Form.Item label="Profile Content" name="content"
                    rules={[{}]}>
                   <JSONEditor />
                </Form.Item>
                <Form.Item className="flex-end">
                    <Popconfirm okText="Yes" cancelText="No"
                      title="Are you sure you want to upload this Profile?"
                      onConfirm={() => onFinish()}
                      onCancel={() => {message.info("Profile creation cancelled")}}>
                        <Button className="dark-orange-bg white-color" loading = {loading} >
                          Upload
                      </Button>
                    </Popconfirm>
               </Form.Item>
         </Form>
  )
}

