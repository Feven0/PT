import { lazy, useEffect, useState } from "react";
import { Button, Col, Drawer, Form, Input, message, Popconfirm } from "antd";
import { EditOutlined, PlusOutlined } from '@ant-design/icons';
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';
import { useMutation } from "@apollo/client";

import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { setUserBio } from "../../../redux/slices/experienceSlice";

import { CREATE_NOTIFICATION } from "../../../graphql/mutations/createNotification";

import useFetchUserProfile from "../../../hooks/useFetchUserProfile";
import useAxiosRequest from "../../../hooks/useAxiosRequest";
import { noProfile } from "../../../assets";
import { getRunStage } from "../../../utils/getRunStage";
const DescriptionToggle = lazy(() => import("../../commonComponents/DescriptionToggler"));

type TBio = {
  onMouseDown: () => void;
  onMouseUp: () => void;
  isResizing: boolean;
  handleMaximize: () => void;
  setDrawerVisible: (value: boolean) => void;
  drawerVisible: boolean;
}

const { TextArea } = Input;
const MAX_DESCRIPTION_LENGTH = 420;
const run_stage = getRunStage();

export default function Bio({ onMouseDown, onMouseUp, isResizing, handleMaximize, setDrawerVisible, drawerVisible }: TBio) {
  const [width, setWidth] = useState(540);
  const  { fetchUserProfile } = useFetchUserProfile();
  const { userBio } = useAppSelector(state => state.experience);
  const { basics:bio } = useAppSelector((state) => state.traineeProfileResponse.user_profile)
  const { allUserId, user_profile_id, user_role, trainee_id, batch } = useAppSelector(state => state.leapProfileId);
  const [form] = Form.useForm();
  
  const dispatch = useAppDispatch();
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  useEffect(() => {
    const onMouseMoveHandler = (e: MouseEvent) => {
      if (isResizing) {
        const offsetRight =
          document.body.offsetWidth - (e.clientX - document.body.offsetLeft);
        const minWidth = 540;
        if (offsetRight > minWidth) {
          setWidth(offsetRight);
        }
      }
    };
    document.addEventListener("mousemove", onMouseMoveHandler);
    document.addEventListener("mouseup", onMouseUp);

    return () => {
      document.removeEventListener("mousemove", onMouseMoveHandler);
      document.removeEventListener("mouseup", onMouseUp);
    };
  }, [isResizing]);

  const showBioDrawer = () => {
    form.setFieldsValue({bio: bio.attributes[0].personal_statement});
    setDrawerVisible(true);
  }

  const closeBioDrawer = () => {
    form.resetFields()
    setDrawerVisible(false);
    setWidth(540);
  };

  const handleBioChange = (e: any) => dispatch(setUserBio(e.target.value));
  const handleBioDrawer = () => setDrawerVisible(true);
  const { makeRequest, loading } = useAxiosRequest();

  const handleBioUpdate = () => {
   const data = {
    user_role: user_role,
    run_stage: run_stage,
    all_user_id: allUserId,
    user_profile_id: user_profile_id,
    user_profile: [
      {
        code: "basics",
        uuid: bio.attributes[0]?.uuid,
        data: {
          email: bio.attributes[0].email,
          full_name: bio.attributes[0].full_name,
          location: bio.attributes[0].location,
          media: bio.attributes[0].media,
          phone: bio.attributes[0].phone,
          role: bio.attributes[0].role,
          name_title: bio.attributes[0].name_title,
          personal_statement: userBio
        }
      }
    ],
    status: "approved",  
  }

  const details = {
    traineeId: trainee_id,
    notificationMessageTeam: `Added a new bio! `,
    notificationMessageTrainee: `Added a new bio!`,
    where: "Bio",
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
                message.error("Notification creation failed");
              }
            },
          });
          message.success("Bio updated successfully");
          setDrawerVisible(false);
          fetchUserProfile();
          form.resetFields();
        } 
      },
      onError: () => {},
    });
  })
  .catch(() => { });
  };

  return (
    <>
    {bio.attributes.length > 0 ?
    <>
      <div className="flex-end cursor-pointer bio-edit-icon" onClick={showBioDrawer}>
        <EditOutlined className="edit-outlined-icon"/>
      </div>
      <Col span={24} className="mobile-user-profile user-bio-container">
          <DescriptionToggle bio={bio.attributes[0].personal_statement} maxDescriptionLength={MAX_DESCRIPTION_LENGTH} />
      </Col>
      </>
      :
      <Col span={24}>
          <div className="d-flex-center no-profile-data" style={{flexDirection:"column", marginBottom:"1rem"}}>
            <h3>No Personal information</h3>
            <img src={noProfile} width={200} alt="no-profile" />
            <p>There are currently no bio details available for display at this time!</p>
            <Button
              className="dark-orange-bg white-color mt-16"
              icon={<PlusOutlined />}
              onClick={handleBioDrawer}>
              Add Bio
            </Button>
          </div>
    </Col>
    }
      <Drawer
        placement="right"
        onClose={closeBioDrawer}
        open={drawerVisible}
        className="close-btn-position"
        width={width}
        title={
          <div className="d-flex-between">
            Update Bio
            <Button type='text'
              style={{ border: 'none', marginRight:"1rem" }}
              icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
              onClick={handleMaximize} />
          </div>
        }
      >
        <div className="dynamic-drawer-width" onMouseDown={onMouseDown} />
          <Form form={form} layout="vertical" onFinish={handleBioUpdate}>
            <Form.Item name="bio" label="Bio" rules={[{ required: true, message: 'Please enter your bio' }]}>
              <TextArea rows={10} onChange={handleBioChange} />
            </Form.Item>
            <Form.Item className="update-submit-button">
              <Popconfirm
                okText="Yes"
                cancelText="No"
                title="Are you sure you want to update bio?"
                onConfirm={() => handleBioUpdate()}
                onCancel={() => { message.info("Bio updating cancelled") }} >
                <Button loading={loading} className="dark-orange-bg white-color">
                  Update
                </Button>
              </Popconfirm>
            </Form.Item>
          </Form>
      </Drawer>
    </>
  );
}
