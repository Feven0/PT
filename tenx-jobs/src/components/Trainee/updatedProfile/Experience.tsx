import { useEffect, useState } from "react";
import { Avatar, Button, Col, DatePicker, Drawer, Form, Input, message, Popconfirm, Row, Switch } from "antd";
import { useMutation } from "@apollo/client";
import { EditOutlined, PlusOutlined } from "@ant-design/icons";
import dayjs from "dayjs";
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';
import moment from "moment";

import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { CREATE_NOTIFICATION } from "../../../graphql/mutations/createNotification";
import { resetExperience, setExperience } from "../../../redux/slices/experienceSlice";
import DescriptionToggle from "../../commonComponents/DescriptionToggler";

import { calculateDuration } from "../../../utils/dateCalculator";
import { capitalizeFirstChar, format, formatDateToYYYYMMDD } from "../../../utils/commonUtils";

import { no_experience } from "../../../assets";
import useFetchUserProfile from "../../../hooks/useFetchUserProfile";
import useAxiosRequest from "../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../utils/getRunStage";

type UserExpProps = {
  setIsExperienceDetailVisible: (value: boolean) => void;
  isExperienceDetailVisible: boolean;
  handleMaximize: () => void;
  onMouseDown: () => void;
  onMouseUp: () => void;
  isResizing: boolean;
}

const { RangePicker } = DatePicker;
const {TextArea} = Input;

const MAX_DESCRIPTION_LENGTH = 200;
const run_stage = getRunStage();

export default function Experience({ setIsExperienceDetailVisible, isExperienceDetailVisible, handleMaximize, onMouseDown, onMouseUp, isResizing }: UserExpProps) {
  const [width, setWidth] = useState(540);
  const [isStillWorking, setIsStillWorking] = useState(false);
  const [isHoverTrue, setIsHoverTrue] = useState<number | null>(null);
  const [selectedID, setSelectedID] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const {work_experience: userExp } = useAppSelector((state) => state.traineeProfileResponse.user_profile)
  
  const {experience} = useAppSelector(state => state.experience)
  const {allUserId, user_profile_id, user_role, batch, trainee_id} = useAppSelector(state => state.leapProfileId)
  const  { fetchUserProfile } = useFetchUserProfile();

  const dispatch = useAppDispatch()
  const [form] = Form.useForm();
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

  const handleMouseEnter = (index: number) => setIsHoverTrue(index);
  const handleMouseLeave = () => setIsHoverTrue(null);
  const { makeRequest, loading } = useAxiosRequest();

  const onExpFinish = () => {
      let data = {}
      if(experience.id !== selectedID){
      data = {
        user_role,
        run_stage: run_stage,
        all_user_id: allUserId,
        user_profile_id: user_profile_id,
        profile_type: "other",
        user_profile: [
          {
            code: "work_experience",
            data: {
              start_date: formatDateToYYYYMMDD(experience.duration[0]),
              end_date: formatDateToYYYYMMDD(experience.duration[1]),
              company: experience.company,
              role: experience.role,
              summary: experience.description,
              location: experience.location,
            }
          }
        ],
        status: "approved",  
      }
    }else{
      data = {
        user_role,
        run_stage: run_stage,
        all_user_id: allUserId,
        user_profile_id: user_profile_id,
        profile_type: "other",
        user_profile: [
          {
            code: "work_experience",
            uuid: selectedID,
            data: {
              start_date: formatDateToYYYYMMDD(experience.duration[0]),
              end_date: formatDateToYYYYMMDD(experience.duration[1]),
              company: experience.company,
              role: experience.role,
              summary: experience.description,
              location: experience.location,
            }
          }
        ],
        status: "approved",  
      }
    }

    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Added a new experience! `,
      notificationMessageTrainee: `Added a new experience!`,
      where: "Experience",
      traineeLink: `/trainee/profile`,
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
              message.success("Experience added successfully");
              dispatch(resetExperience());
              setIsExperienceDetailVisible(false);
              form.resetFields();
              fetchUserProfile();
            } 
          },
          onError: () => {}
        });
      })
      .catch(() => { });
    }
  
    const handleEditClick = (index:number) => {
      setIsEditing(true);
      const selectedExp = userExp.attributes[index];
      setSelectedID(selectedExp.uuid);
      dispatch(setExperience({
        id: selectedExp.uuid,
        role: selectedExp.role,
        company: selectedExp.company,
        duration: [
          selectedExp.start_date && dayjs(selectedExp.start_date).isValid() 
            ? dayjs(selectedExp.start_date).format(format) 
            : dayjs().format(format),
          selectedExp.end_date && dayjs(selectedExp.end_date).isValid() 
            ? dayjs(selectedExp.end_date).format(format) 
            : dayjs().format(format) 
        ],
        description: selectedExp.summary,
        location: selectedExp.location,
      }));
  
      form.setFieldsValue({
        roleName: selectedExp.role,
        company: selectedExp.company,
        duration: [
          selectedExp.start_date && dayjs(selectedExp.start_date).isValid() ? dayjs(selectedExp.start_date) : dayjs(), 
          selectedExp.end_date && dayjs(selectedExp.end_date).isValid() ? dayjs(selectedExp.end_date) : dayjs() 
        ],
        location: selectedExp.location,
        description: selectedExp.summary,
      });
      setIsExperienceDetailVisible(true);
    };

  const handleRangePickerChange = (value: any) => {
    const dates = value?.map((date: any) => date ? dayjs(date).toDate().toISOString() : null) as [string, (string | null)];
    if (isStillWorking) {
      dispatch(setExperience({
        ...experience,
        duration: [dates[0], null]
      }));
    } else {
      dispatch(setExperience({
        ...experience,
        duration: [dates[0], dates[1] as string]
      }));
    }
  };

  // Handle switch change for experience
  const handleSwitchChange = (checked: boolean) => {
    setIsStillWorking(checked);
    if (checked) {
      dispatch(setExperience({
        ...experience,
        duration: [experience.duration[0], null]
      }));
    }
  };

  const closeDrawer = () =>{ 
    form.resetFields()
    setIsExperienceDetailVisible(false);
    setWidth(540);
  }

  const handleAddExperience = () => setIsExperienceDetailVisible(true);

  return (
    <>
      {userExp?.attributes?.length > 0 ?
      userExp.attributes.map((exp, index) => (
        <Col span={24} key={index} className={`user-education-wrapper ${index !== userExp.attributes.length - 1 ? 'with-border' : ''}`}>
          <Row gutter={16} className="mt-16">
            <Col span={24} onMouseEnter={() => handleMouseEnter(index)} onMouseLeave={handleMouseLeave}>
              <div className="flex gap-16">
                <Avatar shape="square" size="small" className="work-experience-logo">
                  {exp?.role?.charAt(0).toUpperCase()}
                </Avatar>
                <div className="full-width">
                  <div className="d-flex-between">
                  <h4>{capitalizeFirstChar(exp.role)}</h4>
                    {isHoverTrue === index && (
                      <div className="flex gap-16">
                        <EditOutlined className="cursor-pointer" onClick={() => handleEditClick(index)} />
                      </div>
                    )}
                  </div>
                  <div>
                    <p>{exp.company}</p>
                    <p>{exp.location}</p>
                     {moment(exp.start_date, 'YYYY-MM-DD', true).isValid() && 
                      (!exp.end_date || moment(exp.end_date, 'YYYY-MM-DD', true).isValid()) && (
                        <div className="flex-center gap-8">
                          {moment(exp.start_date).format('DD MMM YYYY')} - {exp.end_date ? moment(exp.end_date).format('DD MMM YYYY') : 'Present'}
                          <p>&nbsp; • &nbsp; {calculateDuration(exp.start_date, exp.end_date)}</p>
                        </div>
                      )}
                  </div>
                  <DescriptionToggle
                    bio={Array.isArray(exp?.summary) 
                      ? exp.summary.join(" ") 
                      : typeof exp?.summary === "string"
                      ? exp.summary 
                      : ""
                    } 
                    maxDescriptionLength={MAX_DESCRIPTION_LENGTH} 
                  />
                </div>
              </div>
            </Col>
          </Row>
        </Col>
      )):
      <Col span={24}>
         <div className="d-flex-center no-profile-data" style={{ marginBottom:"1rem"}}>
            <div className="d-flex-center no-profile-data-content" style={{flexDirection:"column"}}>
            <img src={no_experience} width={200} height={150} alt="no-profile" />
            <div className="text-center mt-16">
              <p>Input your previous <span className="profile-empty-name">work experience </span> details to showcase your skills and accomplishments.</p>
            </div>
            <Button
              className="dark-orange-bg white-color mt-16"
              icon={<PlusOutlined />}
              onClick={handleAddExperience
              }>
              Add Experience
            </Button>
            </div>
          </div>
    </Col>
      }

      <Drawer title={<div className="d-flex-between mr-16" >{isEditing ? "Edit Experience" : "Add Experience"}
          <Button
            type='text'
            style={{ border: 'none' }}
            icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
            onClick={handleMaximize} />
            </div>} 
            placement="right" 
            className="work-experience-drawer close-btn-position" 
            onClose={closeDrawer} 
            open={isExperienceDetailVisible}
            width={width}>
            <div className="dynamic-drawer-width" onMouseDown={onMouseDown} />
            <Form form={form} name="workExperienceForm" layout="vertical" onFinish={onExpFinish}>
                <Row gutter={[16, 16]}>
                    <Col span={24}>
                        <Form.Item name="roleName" label="Role Name"
                            rules={[{
                                    required: true,
                                    message: 'Please enter role name',
                                }]}
                        >
                          <Input placeholder="Please input role"  
                            onChange={(e) =>
                              dispatch(setExperience({ ...experience, role: e.target.value }))
                        } />
                        </Form.Item>
                    </Col>
                    <Col span={24}>
                        <Form.Item
                            name="company"
                            label="Company/Employer"
                            rules={[{
                                    required: true,
                                    message: 'Please enter company/employer',
                                }]} >
                            <Input placeholder="Please input company/employer"
                            onChange={(e) =>
                              dispatch(setExperience({ ...experience, company: e.target.value }))
                            }
                            />
                        </Form.Item>
                    </Col>
                    <Col span={24}>
                        <Form.Item
                            name="location"
                            label="Location"
                            rules={[{
                                    required: false,
                                    message: 'Please enter location',
                                }]} >
                            <Input placeholder="Please input location"
                            onChange={(e) =>
                              dispatch(setExperience({ ...experience, location: e.target.value }))
                            }
                            />
                        </Form.Item>
                    </Col>
                    <Col span={24}>
                      
                      <Form.Item label="Duration" colon={false} name="duration"
                          tooltip="Experience duration start date and end date"
                          initialValue={
                              experience.duration.length > 0 ? [
                                experience.duration[0] ? dayjs(experience.duration[0]) : null,
                                experience.duration[1] ? dayjs(experience.duration[1]) : null]
                                  : null
                          }
                          rules={[{
                                  required: true,
                                  message: "Please select a duration for this field",
                              }]}>
                        <RangePicker
                          style={{ width: "100%" }}
                          placeholder={["Start Date", "End Date"]}
                          onChange={handleRangePickerChange}
                          disabled={[false, isStillWorking]}
                        />
                  </Form.Item>
                  <Form.Item label="Still working here" colon={false}>
                        <Switch 
                        checked={experience.duration[1] === null || experience.duration[1]=== "" || experience.duration[1]=== undefined}
                         onChange={handleSwitchChange} />
                    </Form.Item>
                </Col>
                    <Col span={24}>
                      <Form.Item label="Description" tooltip="Experience description" colon={false}
                          name="description"
                          className="applicationForm-Ckeditor"
                          rules={[{
                                  required: true,
                                  message: "Please input a description",
                                   }]}>
                            <TextArea placeholder="Please input description" rows={4}
                            value={experience.description}
                            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                              dispatch(setExperience({ ...experience, description: e.target.value }))
                            }
                         />
                      </Form.Item>
                    </Col>
                </Row>
              <Form.Item className="update-submit-button">
                <Popconfirm
                  title="Are you sure you want to add this Experience?"
                  onConfirm={() => onExpFinish()}
                  onCancel={() => {
                    message.info("Experience creation cancelled");
                  }}
                  okText="Yes"
                  cancelText="No">
                    <Button
                      className="dark-orange-bg white-color"
                      loading = {loading}>
                        {isEditing ? "Update" : "Add Experience"}
                    </Button>
                </Popconfirm>
              </Form.Item>
        </Form>
        </Drawer>
    </>
  );
}

