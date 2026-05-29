import { useEffect, useState } from 'react'
import { Avatar, Button, Col, DatePicker, Drawer, Form, Input, message, Popconfirm, Row, Select, Switch, Typography } from "antd";
import { useMutation } from "@apollo/client";
import {EditOutlined, PlusOutlined} from "@ant-design/icons";
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';
import { FaLink } from "react-icons/fa";
import moment from "moment";
import dayjs from "dayjs";

import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { resetEducation, setEducation } from "../../../redux/slices/experienceSlice";
import { CREATE_NOTIFICATION } from "../../../graphql/mutations/createNotification";
import DescriptionToggle from "../../commonComponents/DescriptionToggler";
import { format, formatDateToYYYYMMDD } from "../../../utils/commonUtils";

import { noProfile } from "../../../assets";
import { calculateDuration } from "../../../utils/dateCalculator";
import useFetchUserProfile from "../../../hooks/useFetchUserProfile";
import useAxiosRequest from "../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../utils/getRunStage";
import '../../../styles/slidingCard.css'

  type SortedEducationProps = {
    handleMaximize: () => void;
    setIsEducationFormVisible: (value: boolean) => void;
    isEducationFormVisible: boolean;
    onMouseDown: () => void;
    onMouseUp: () => void;
    isResizing: boolean;
    showEducationDrawer: () => void;
  }

const { Text } = Typography;
const { RangePicker } = DatePicker;
const { TextArea } = Input;

const MAX_DESCRIPTION_LENGTH = 250;
const run_stage = getRunStage();

export default function EducationProf({
  handleMaximize, 
  setIsEducationFormVisible, 
  onMouseDown,
  showEducationDrawer,
  onMouseUp,
  isResizing,
  isEducationFormVisible
}: SortedEducationProps) {
  const [isStillStudying, setIsStillStudying] = useState(false);
  const [width, setWidth] = useState(540);
  const [isEducationHoverTrue, setIsEducationHoverTrue] = useState<number | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const {allUserId, user_profile_id, user_role, trainee_id, batch} = useAppSelector(state => state.leapProfileId)
  const {education} = useAppSelector(state => state.experience)
  const { education: userEdu} = useAppSelector((state) => state.traineeProfileResponse.user_profile)

  const  { fetchUserProfile } = useFetchUserProfile();

  const [form] = Form.useForm();
  const dispatch = useAppDispatch();
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  const handleEducationMouseEnter = (index: number) => setIsEducationHoverTrue(index);
  const handleEducationMouseLeave = () => setIsEducationHoverTrue(null);
  const { makeRequest, loading } = useAxiosRequest();

  useEffect(() => {
    const onMouseMoveHandler = (e: MouseEvent) => {
      if (isResizing) {
        const offsetRight = document.body.offsetWidth - (e.clientX - document.body.offsetLeft);
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

  const sortedEducation = [...userEdu.attributes].sort((a, b) => {
    return new Date(b.end_date).getTime() - new Date(a.end_date).getTime();
  });

  const handleEducationEditClick = (index:number) => {
    setIsEditing(true);
    const selectedEdu = sortedEducation[index];
    setSelectedId(selectedEdu.uuid);
    dispatch(setEducation({
      id: selectedEdu.uuid,
      school: selectedEdu.institution_name,
      study_type: selectedEdu.study_type,
      duration: [
        selectedEdu.start_date && dayjs(selectedEdu.start_date).isValid() 
          ? dayjs(selectedEdu.start_date).format(format) 
          : dayjs().format(format),
          selectedEdu.end_date && dayjs(selectedEdu.end_date).isValid() 
          ? dayjs(selectedEdu.end_date).format(format) 
          : dayjs().format(format) 
      ],
      description: selectedEdu.remark,
      coursework: selectedEdu.courses,
      country: selectedEdu.country,
      study_area: selectedEdu.study_area,
      institution_url: selectedEdu.institution_url,
      score: selectedEdu.score
    }));

    form.setFieldsValue({
      schoolName: selectedEdu.institution_name,
      duration: [
        selectedEdu.start_date && dayjs(selectedEdu.start_date).isValid() ? dayjs(selectedEdu.start_date) : dayjs(), 
        selectedEdu.end_date && dayjs(selectedEdu.end_date).isValid() ? dayjs(selectedEdu.end_date) : dayjs() 
      ],
      description: selectedEdu.remark,
      courseWork: selectedEdu.courses,
      country: selectedEdu.country,
      degree: selectedEdu.study_type,
      study_area: selectedEdu.study_area,
      institution_url: selectedEdu.institution_url,
      study_type: selectedEdu.study_type,
      score: selectedEdu.score
    });
    setIsEducationFormVisible(true);
  };

  const handleStudyingRangePickerChange = (value: any) => {
    const dates = value?.map((date: any) => date ? dayjs(date).toDate().toISOString() : null) as [string, string];
    if (isStillStudying) {
      dispatch(setEducation({
        ...education,
        duration: [dates[0], null]
      }));
    } else {
      dispatch(setEducation({
        ...education,
        duration: [dates[0], dates[1]]
      }));
    }
  };

    // Handle switch change for education
    const handleEducationSwitchChange = (checked: boolean) => {
      setIsStillStudying(checked);
      if (checked) {
        dispatch(setEducation({
          ...education,
          duration: [education.duration[0], null]
        }));
      }
    }

    const closeEducationDrawer = () => {
      form.resetFields()
      setIsEducationFormVisible(false);
      setWidth(540);
    } 

    const onEduFinish = () => {
      let data  = {}
      if(education.id !== selectedId) {
        data = {
          user_role: user_role,
          run_stage: run_stage,
          all_user_id: allUserId,
          user_profile_id: user_profile_id,
          user_profile: [
            {
              code: "education",
              data: {
                institution_name: education.school,
                study_type: education.study_type,
                start_date: formatDateToYYYYMMDD(education.duration[0]),
                end_date: formatDateToYYYYMMDD(education.duration[1]),
                remark: education.description,
                country: education.country,
                courses: education.coursework,
                score: education.score,
                study_area: education.study_area,
                institution_url: education.institution_url,
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
              code: "education",
              uuid: selectedId,
              data: {
                institution_name: education.school,
                study_type: education.study_type,
                start_date: formatDateToYYYYMMDD(education.duration[0]),
                end_date: formatDateToYYYYMMDD(education.duration[1]),
                remark: education.description,
                country: education.country,
                courses: education.coursework,
                score: education.score,
                study_area: education.study_area,
                institution_url: education.institution_url,
              }
            }
          ],
          status: "approved",  
        }
      }

      const details = {
        traineeId: trainee_id,
        notificationMessageTeam: `Added a new education! `,
        notificationMessageTrainee: `Added a new education!`,
        where: "education",
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
              message.success("Education added successfully");
              dispatch(resetEducation());
              setIsEducationFormVisible(false);
              form.resetFields();
              fetchUserProfile();
            }
          },
          onError: () => {}
        });
      })
      .catch(() => {});
    }

  return (
    <>
      {userEdu?.attributes?.length >0 ?
      sortedEducation.map((edu, index) => (
        <Col span={24} className={`mobile-user-profile user-education-wrapper ${index !== userEdu.attributes.length - 1 ? 'with-border' : ''}`} key={index} >
          <Row gutter={8} className="mt-16">
            <Col span={24} onMouseEnter={() => handleEducationMouseEnter(index)} onMouseLeave={handleEducationMouseLeave}>
              <div className="flex gap-16">
                <Avatar shape="square" size="small" className="work-experience-logo">
                  {edu.institution_name.charAt(0).toUpperCase()}
                </Avatar>
                <div className="full-width">
                  <div className="d-flex-between">
                    <h4>{edu.institution_name}</h4>
                    {isEducationHoverTrue === index && (
                      <div className="flex gap-16">
                        <EditOutlined className="cursor-pointer" onClick={() => handleEducationEditClick(index)} />
                      </div>
                    )}
                  </div>
                  <div>
                    <p>{edu.study_area}</p>
                    <p>{edu.study_type}</p>
                    <div className="flex-center gap-8">
                      {edu.country && <span>{edu.country}</span> }
                    </div>
                      {edu.score && <span>Score - {edu.score}</span>}
                  </div>
                    {moment(edu.start_date, 'YYYY-MM-DD', true).isValid() && 
                    (!edu.end_date || moment(edu.end_date, 'YYYY-MM-DD', true).isValid()) && (
                      <div className="flex-center gap-8">
                        {moment(edu.start_date).format('DD MMM YYYY')} - {edu.end_date ? moment(edu.end_date).format('DD MMM YYYY') : 'Present'}
                        <p>&nbsp;•&nbsp; {calculateDuration(edu.start_date, edu.end_date)}</p>
                      </div>
                    )}
                  <br/><span className="mt-16">
                        {
                          edu.institution_url && <a href={edu.institution_url} target="_blank" rel="noreferrer">
                          <Button icon={<FaLink />} className="white-bg dark-orange-color mt-8">Visit Site</Button>
                        </a>
                        }
                      </span>
                  <DescriptionToggle bio={edu?.remark} maxDescriptionLength={MAX_DESCRIPTION_LENGTH} /> 
                </div>
              </div>
            </Col>
          </Row>
        </Col>
      )): 
      <Col span={24}>
          <div className="d-flex-center no-profile-data" style={{ marginBottom:"1rem"}}>
            <div className="d-flex-center no-profile-data-content" style={{flexDirection:"column"}}>
            <img src={noProfile} width={200} height={150} alt="no-profile" />
            <div className="text-center mt-16">
              <p>Provide details about your <span className="profile-empty-name"> educational background</span> to demonstrate your qualifications.</p>
            </div>
            <Button
              className="dark-orange-bg white-color mt-16"
              icon={<PlusOutlined />}
              onClick={showEducationDrawer}>
              Add Education
            </Button>
            </div>
          </div>
    </Col>
      }
       <Drawer title={<div className="d-flex-between mr-16"><span>{isEditing ? "Edit Education" : "Add Education"}</span>
          <Button type='text' style={{ border: 'none' }}
                icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
                onClick={handleMaximize}>
          </Button>
           </div>} placement="right" 
           className="work-experience-drawer close-btn-position" 
            onClose={closeEducationDrawer}
            width={width}
            open={isEducationFormVisible}>
            <div className="dynamic-drawer-width" onMouseDown={onMouseDown}/>
            <Form form={form} name="educationForm" layout="vertical" onFinish={onEduFinish}>
              <div className="work-experience-edit-form">
                <Row gutter={[16, 16]}>
                    <Col span={24}>
                        <Form.Item name="schoolName" label="School"
                            rules={[{required: true, message: 'Please enter school name'}]}>
                            <Input placeholder="What is your school name?"
                                    onChange={(e) =>
                                      dispatch(setEducation({ ...education, school: e.target.value }))
                                }
                            />
                        </Form.Item>
                    </Col>
                    <Col span={24}>
                        <Form.Item name="institution_url" label="URL"
                            rules={[{required: false, type: 'url', message: 'Please enter school url'}]}>
                            <Input placeholder="Input your institution url?"
                                    onChange={(e) =>
                                      dispatch(setEducation({ ...education, institution_url: e.target.value }))
                                    }
                            />
                        </Form.Item>
                    </Col>
                    <Col span={24}>
                        <Form.Item name="country" label="Country"
                            rules={[{required: true, message: 'Please enter school country'}]}>
                          <Input placeholder="Input country of your institution"
                                    onChange={(e) =>
                                      dispatch(setEducation({ ...education, country: e.target.value }))
                              }
                            />
                        </Form.Item>
                    </Col>
                    <Col span={24}>
                        <Form.Item name="degree" label="Degree"
                            rules={[{required: true, message: 'Please enter your degree'}]}>
                            <Input placeholder="eg. Bachelor's, PhD, Masters" 
                              onChange={(e) =>
                                dispatch(setEducation({ ...education, study_type: e.target.value }))
                              }
                              />
                        </Form.Item>
                    </Col>
                    <Col span={24}>
                        <Form.Item name="study_area" label="Study Area"
                            rules={[{required: true, message: 'Please enter your study area'}]}>
                            <Input placeholder="eg. Computer Science, Physics" 
                              onChange={(e) =>
                                dispatch(setEducation({ ...education, study_area: e.target.value }))
                              }
                              />
                        </Form.Item>
                    </Col>
                    <Col span={24}>
                        <Form.Item name="score" label="Score"
                            rules={[{required: true,  message: 'Please enter your score' }]}>
                            <Input placeholder="eg. 3.95 on scale of 4.0" 
                              onChange={(e) =>
                                dispatch(setEducation({ ...education, score: e.target.value }))
                              }
                              />
                        </Form.Item>
                    </Col>
                    <Col span={24}>
                        <Form.Item name="duration" label="Duration"
                            initialValue={
                              education.duration.length > 0 ? [
                                education.duration[0] ? dayjs(education.duration[0]) : null,
                                education.duration[1] ? dayjs(education.duration[1]) : null]
                                  : null
                          }
                            rules={[{required: true, message: 'Please select duration' }]}>
                            <RangePicker style={{ width: '100%' }}  
                            disabled={[false, isStillStudying]}
                            onChange={handleStudyingRangePickerChange}
                            />
                        </Form.Item>
                        <Form.Item name="switch" label="Still Studying here" colon={false}>
                          <Switch 
                          checked={education.duration[1] === null || education.duration[1]=== "" || education.duration[1]=== undefined}
                           onChange={handleEducationSwitchChange} />
                      </Form.Item>
                    </Col>
                    <Col span={24}>
                      <Form.Item label="Description" tooltip="Education description" colon={false}
                          name="description"
                          className="applicationForm-Ckeditor"
                          rules={[{ required: true,  message: "Please input a description"}]}>
                            <TextArea placeholder="Please input description" rows={4}
                            value={education.description}
                            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                              dispatch(setEducation({ ...education, description: e.target.value }))
                            }
                         />
                      </Form.Item>
                    </Col>
                    <Col span={24}>
                      <Form.Item name="courseWork" label={<Text>Course Work</Text>} rules={[{ required: true }]}>
                        <Select mode="tags"
                          maxTagTextLength={20}
                          placeholder="e.g Data Structure, Algorithms, C++, Calculus"
                          notFoundContent={<div>Enter course work</div>}
                          onChange={(values) =>{
                            dispatch(setEducation({ ...education, coursework: values }))
                          }}
                        />
                    </Form.Item>
                </Col>
                </Row>
                <Form.Item className="update-submit-button">
                  <Popconfirm okText="Yes" cancelText="No"
                    title="Are you sure you want to add this Education?"
                    onConfirm={() => onEduFinish()}
                    onCancel={() => {
                      message.info("Education creation cancelled");
                    }}>
                      <Button className="dark-orange-bg white-color" loading = {loading}>
                          {isEditing ? "Update" : "Add Education"}
                      </Button>
                  </Popconfirm>
               </Form.Item>
            </div>
        </Form>
      </Drawer>
    </>
  );
}