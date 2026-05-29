import { Col, Row, Avatar, Drawer, Button, Form, Input, Switch, Select, Popconfirm, message, DatePicker, Typography } from 'antd';
import { EditOutlined, PlusOutlined } from '@ant-design/icons';
import { useEffect, useState } from "react";
import dayjs from "dayjs";
import { useMutation } from "@apollo/client";
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';
import moment from "moment";

// Components
import DescriptionToggle from "../../commonComponents/DescriptionToggler";

// Redux and custom hooks
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { setProject } from "../../../redux/slices/experienceSlice";
import useFetchUserProfile from "../../../hooks/useFetchUserProfile";
import useAxiosRequest from "../../../hooks/useAxiosRequest";

// GraphQL
import { CREATE_NOTIFICATION } from "../../../graphql/mutations/createNotification";

// Utils
import { format, formatDateToYYYYMMDD } from "../../../utils/commonUtils";
import { calculateDuration } from "../../../utils/dateCalculator";

//Styles and Images
import { no_project } from "../../../assets";
import '../../../styles/slidingCard.css'
import { getRunStage } from "../../../utils/getRunStage";

type ProjectsProps = {
  isProjectFormVisible: boolean;
  setIsProjectFormVisible: (value: boolean) => void;
  isResizing: boolean;
  handleMaximize: () => void;
  onMouseDown: (e: React.MouseEvent<HTMLDivElement, MouseEvent>) => void;
  onMouseUp: () => void;
}

const { RangePicker } = DatePicker;
const { Text } = Typography;
const run_stage = getRunStage();
const MAX_DESCRIPTION_LENGTH = 200;

const { TextArea } = Input;

export default function Projects({
    isProjectFormVisible, 
    isResizing,
    onMouseDown,
    onMouseUp,
    handleMaximize,
    setIsProjectFormVisible}: ProjectsProps){
  const [isStillWorkingProject, setIsStillWorkingProject] = useState(false);
  const [isProjectHoverTrue, setProjectHoverTrue] = useState<number | null>(null);
  const [width, setWidth] = useState(540);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  
  const {allUserId, user_profile_id, user_role, trainee_id, batch} = useAppSelector(state => state.leapProfileId)
  const { project} = useAppSelector(state => state.experience)
  const { projects } = useAppSelector((state) => state.traineeProfileResponse.user_profile)

  const  { fetchUserProfile } = useFetchUserProfile();
  const { makeRequest, loading } = useAxiosRequest();
  
  const dispatch = useAppDispatch();
  const [form] = Form.useForm();
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  const handleProjectMouseEnter = (index: number) => setProjectHoverTrue(index);
  const handleProjectMouseLeave = () => setProjectHoverTrue(null);

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

  const closeProjectDrawer = () => {
    form.resetFields()
    setIsProjectFormVisible(false);
    setWidth(540);
  }

  const handleProjectEditClick = (index: number) => {
    setIsEditing(true);
    const selectedProject = projects.attributes[index];
    const tools = selectedProject.tools.length > 0 ? selectedProject.tools : [];

    setSelectedId(selectedProject.uuid);
    dispatch(setProject({
      id: selectedProject.uuid,
      name: selectedProject.title,
      duration: [
        selectedProject.start_date && dayjs(selectedProject.start_date).isValid() 
          ? dayjs(selectedProject.start_date).format(format) 
          : dayjs().format(format),
          selectedProject.end_date && dayjs(selectedProject.end_date).isValid() 
          ? dayjs(selectedProject.end_date).format(format) 
          : dayjs().format(format) 
      ],
      description: selectedProject.summary,
      url: selectedProject.url,
      tools: tools
    }));
  
    form.setFieldsValue({
      projectName: selectedProject.title,
      duration: [
        selectedProject.start_date && dayjs(selectedProject.start_date).isValid() ? dayjs(selectedProject.start_date) : dayjs(), 
        selectedProject.end_date && dayjs(selectedProject.end_date).isValid() ? dayjs(selectedProject.end_date) : dayjs() 
      ],
      desc: selectedProject.summary,
      url: selectedProject.url,
      tools: selectedProject.tools.length > 0 ? selectedProject.tools : undefined,
      focus_area: selectedProject.focus_area
    });
  
    setIsProjectFormVisible(true);
  };
  
  const onProjectFinish = () => {
    let data = {}
    if(selectedId !== project.id) {
     data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "projects",
          data: {
            title: project.title,
            focus_area: project.focus_area,
            start_date: formatDateToYYYYMMDD(project.duration[0]),
            end_date: formatDateToYYYYMMDD(project.duration[1]),
            summary: project.description,
            url: project.url,
            tools: project.tools,
            highlights: []
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
            code: "projects",
            uuid: selectedId,
            data: {
              title: project.title,
              focus_area: project.focus_area,
              start_date: formatDateToYYYYMMDD(project.duration[0]),
              end_date: formatDateToYYYYMMDD(project.duration[1]),
              summary: project.description,
              url: project.url,
              tools: project.tools,
              highlights: []
            }
          }
        ],
        status: "approved",  
      }
    }

    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Added a new project! `,
      notificationMessageTrainee: `Added a new project!`,
      where: "Projects",
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
              message.success("Project added successfully");
              setIsProjectFormVisible(false);
              form.resetFields();
              fetchUserProfile();
            } 
          },
          onError: () => {},
        });
      })
      .catch(() => {});
  }

   // Handle switch change for project
   const handleProjectSwitchChange = (checked: boolean) => {
    setIsStillWorkingProject(checked);
    if (checked) {
      dispatch(setProject({
        ...project,
        duration: [project.duration[0], null]
      }));
    }
  }

  // Handle switch change for project
  const handleProjectRangePickerChange = (value: any) => {
    const dates = value?.map((date: any) => date ? dayjs(date).toDate().toISOString() : null) as [string, string];
    if (isStillWorkingProject) {
      dispatch(setProject({
        ...project,
        duration: [dates[0], null]
      }));
    } else {
      dispatch(setProject({
        ...project,
        duration: [dates[0], dates[1]]
      }));
    }
  }

  const handleProjectDrawerOpener = () => setIsProjectFormVisible(true);

  return (
    <>
      {projects?.attributes?.length > 0 ? 
        projects.attributes.map((attr, attrIndex) => (
          <Col span={24} className={`mobile-user-profile user-education-wrapper ${attrIndex !== projects.attributes.length - 1 ? "with-border":""}`} key={attrIndex}>
            <Row gutter={8} className="mt-16">
              <Col span={24} onMouseEnter={() => handleProjectMouseEnter(attrIndex)} onMouseLeave={handleProjectMouseLeave}>
                <div className="flex gap-16">
                  <Avatar shape="square" size={28} className="work-experience-logo">
                    {attr?.title.charAt(0).toUpperCase()}
                  </Avatar>
                  <div className="full-width">
                    <div className="d-flex-between">
                      <h4>{attr?.title}</h4>
                      {isProjectHoverTrue === attrIndex && (
                        <div className="flex gap-16">
                          <EditOutlined className="cursor-pointer" onClick={() => handleProjectEditClick(attrIndex)} />
                        </div>
                      )}
                    </div>
                    {moment(attr.start_date, 'YYYY-MM-DD', true).isValid() && 
                    (!attr.end_date || moment(attr.end_date, 'YYYY-MM-DD', true).isValid()) && (
                      <div className="flex gap-8">
                        {moment(attr.start_date).format('DD MMM YYYY')} - {attr.end_date ? moment(attr.end_date).format('DD MMM YYYY') : 'Present'}
                        <p>&nbsp; •  &nbsp; {calculateDuration(attr.start_date, attr.end_date)}</p>
                      </div>
                    )}
                    <DescriptionToggle 
                      bio={Array.isArray(attr?.summary) 
                        ? attr.summary.join(" ") 
                        : typeof attr?.summary === "string" 
                        ? attr.summary 
                        : ""
                      } 
                      maxDescriptionLength={MAX_DESCRIPTION_LENGTH} 
                    />
                    {(attr?.url && attr?.url !=="None") && <p>
                      <a href={attr?.url} target="_blank" rel="noopener noreferrer">
                        {attr?.url}
                      </a>
                    </p>}
                  </div>
                </div>
              </Col>
            </Row>
          </Col>
        ))
      :<Col span={24}>
        <div className="d-flex-center no-profile-data" style={{ marginBottom:"1rem"}}>
            <div className="d-flex-center no-profile-data-content" style={{flexDirection:"column"}}>
            <img src={no_project} width={200} height={150} alt="no-profile" />
            <div className="text-center mt-16">
              <p>Showcase your key <span className="profile-empty-name">projects</span> to highlight your expertise and accomplishments.</p>
            </div>
            <Button
              className="dark-orange-bg white-color mt-16"
              icon={<PlusOutlined />}
              onClick={handleProjectDrawerOpener}>
               Add Projects
            </Button>
            </div>
          </div>
        </Col>
        }
      <Drawer title={<div className="d-flex-between mr-16"><span>{isEditing ? "Edit Project" :  "Add Project"}</span>
          <Button type='text' style={{ border: 'none' }} icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
                onClick={handleMaximize} />
           </div>} placement="right" className="work-experience-drawer close-btn-position" 
            onClose={closeProjectDrawer}
            width={width}
            open={isProjectFormVisible}>
            <div className="dynamic-drawer-width" onMouseDown={onMouseDown}/>
            <Form form={form} 
                  name="projectForm"
                 layout="vertical" 
                 onFinish={onProjectFinish}>
                <Row gutter={[16, 16]}>
                    <Col span={24}>
                        <Form.Item name="projectName" label="Title"
                            rules={[{
                                    required: true,
                                    message: 'Please enter project title',
                                }]} >
                            <Input placeholder="What is your project title?"
                                    onChange={(e) =>
                                      dispatch(setProject({ ...project, title: e.target.value }))
                                    }/>
                        </Form.Item>
                    </Col>
                    <Col span={24}>
                        <Form.Item name="url" label="URL"
                            rules={[{
                                    required: true,
                                    type: 'url',
                                    message: 'Please enter Project URL',
                                }]}>
                            <Input placeholder="https://www.example.com" 
                              onChange={(e) =>
                                dispatch(setProject({ ...project, url: e.target.value }))
                              }/>
                        </Form.Item>
                    </Col>
                    <Col span={24}>
                        <Form.Item
                               name="duration" 
                               label="Duration"
                               initialValue={
                                project.duration.length > 0 ? [
                                  project.duration[0] ? dayjs(project.duration[0]) : null,
                                  project.duration[1] ? dayjs(project.duration[1]) : null]
                                    : null
                            }
                            rules={[{
                                    required: true,
                                    message: 'Please select project duration',
                                }]} >
                            <RangePicker style={{ width: '100%' }}  
                                disabled={[false, isStillWorkingProject]}
                                onChange={handleProjectRangePickerChange}
                            />
                        </Form.Item>
                        <Form.Item label="Still Working on" colon={false}>
                          <Switch  checked={project.duration[1] === null || project.duration[1]=== "" || project.duration[1]=== undefined} onChange={handleProjectSwitchChange} />
                      </Form.Item>
                    </Col>
                    <Col span={24}>
                        <Form.Item name="focus_area" label="Focus Area"
                            rules={[{
                                    required: false,
                                    message: 'Please enter project focus area',
                                }]}>
                            <Input placeholder="e.g. Medical Image Analysis" 
                              onChange={(e) =>
                                dispatch(setProject({ ...project, focus_area: e.target.value }))
                              }/>
                        </Form.Item>
                    </Col>
                    <Col span={24}>
                      <Form.Item 
                          label="Description" 
                          tooltip="Project description" colon={false}
                          name="desc"
                          className="applicationForm-Ckeditor"
                          rules={[{
                                  required: false,
                                  message: "Please input a description",
                                   }]}>
                            <TextArea 
                                placeholder="Please input description" 
                                rows={4}
                                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                                dispatch(setProject({ ...project, description: e.target.value }))
                            }
                         />
                      </Form.Item>
                    </Col>
                    <Col span={24}>
                      <Form.Item name="tools" label={<Text>Tools</Text>} rules={[{ required: false }]}>
                        <Select mode="tags"
                          maxTagTextLength={20}
                          placeholder="e.g React, Node, Express, MongoDB"
                          notFoundContent={<div>Enter tools</div>}
                          onChange={(values) =>{
                            dispatch(setProject({ ...project, tools: values }))
                          }}
                        />
                    </Form.Item>
                </Col>
                </Row>
                <Form.Item className="update-submit-button">
                    <Popconfirm okText="Yes" cancelText="No"
                      title="Are you sure you want to add this Projects?"
                      onConfirm={() => onProjectFinish()}
                      onCancel={() => {message.info("Project creation cancelled")}}>
                        <Button className="dark-orange-bg white-color" loading = {loading}>
                          {isEditing ? "Update" : "Add Project"}
                      </Button>
                    </Popconfirm>
               </Form.Item>
          </Form>
      </Drawer>
    </>
  );
}

