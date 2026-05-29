import { useNavigate } from "react-router-dom";
import { useEffect, useState } from 'react'
import {MailOutlined, PhoneOutlined,ExportOutlined, EditOutlined,  WhatsAppOutlined, SkypeOutlined , LinkedinOutlined, EnvironmentOutlined, GithubOutlined, MediumOutlined } from "@ant-design/icons";
import { Avatar, Button, Card, Col, Drawer, Modal, Row, Tabs, Tooltip } from "antd"
import type { TabsProps } from 'antd';
import { FaTelegramPlane } from "react-icons/fa";
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';
import { FaLink } from "react-icons/fa6";

//Components
import ServerError from "../../components/commonComponents/ServerError"
import AddJSONProfile from "../../components/Trainee/Profile/AddJSONProfile";
import TraineeProfileDetail from "../../components/Trainee/Profile/TraineeProfileDetail"
import Skills from "../../components/Trainee/Skills";
import EditPersonalDetails from "../../components/Trainee/updatedProfile/EditPersonalDetails";

//Redux and Custom Hooks
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks"
import { setProfileTabs } from "../../redux/slices/tabsSlice";

//Types
import { T_TraineeLocation } from "../../types/profileResponse";
import useFetchUserProfile from "../../hooks/useFetchUserProfile";
import '../../styles/slidingCard.css'


export default function TraineeProfile() {
  const [uploadProfileModal, setUploadProfileModal] = useState(false)
  const [isPersonalInfoDrawerOpen, setIsPersonalInfoDrawerOpen] = useState(false)
  const [width, setWidth] = useState(540);
  const [isResizing, setIsResizing] = useState(false);
  const {username} = useAppSelector((state) => state.user)
  const {profileTab} = useAppSelector((state)=> state.tabs)
  const { awards, basics, education, competencies, projects, work_experience, certificates } = useAppSelector((state) => state.traineeProfileResponse.user_profile)

  const { fetchUserProfile, loading, error } = useFetchUserProfile();
  const dispatch = useAppDispatch()
  const navigate = useNavigate()

  useEffect(() => {
   fetchUserProfile()
  }, []); 

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

  const handleMaximize = () => {
    const newWidth = width === 2000 ? 540 : 2000;
    setWidth(newWidth);
  };

  const onMouseDown = () => setIsResizing(true);
  const onMouseUp = () => setIsResizing(false);
  const showModal = () => setUploadProfileModal(true)
  const closeModal = () => setUploadProfileModal(false)
  const closePersonalInfoDrawer = () => setIsPersonalInfoDrawerOpen(false)
  
  const items: TabsProps['items'] = [
    {
      key: '1',
      label: 'Competencies',
      children:competencies && <Skills loading={loading}/>
      },
    {
      key: '2',
      label: 'Profile Details',
      children: (basics && work_experience && projects && education && awards && certificates ) &&
                <TraineeProfileDetail loading={loading}/>
          },
    
  ];

const displayName = basics?.attributes[0]?.full_name || username;
const location = basics?.attributes[0]?.location;
const initials = displayName.split(' ').filter(part => part.length > 0).slice(0, 2).map(part => part[0].toUpperCase()).join(''); 

const isLocationValid = (location: T_TraineeLocation) => {
  return Object.values(location).every(
    (value) => typeof value === 'string' && value.trim() !== ''
  );
};

const handleExportContent = () =>  navigate('/trainee/export-profile')
const handleEditPersonalInfo = () => setIsPersonalInfoDrawerOpen(true)
const handleTabOnchange = (key: string) => dispatch(setProfileTabs(key))

const getIconByName = (name: string) => {
  switch (name.toLowerCase()) {
    case 'main':
      return <PhoneOutlined />;
    case 'whatsapp':
      return <WhatsAppOutlined />;
    case 'telegram':
      return <FaTelegramPlane/>;
    case 'skype':
      return <SkypeOutlined />;
    default:
      return <PhoneOutlined />; 
  }
};

const roleText = basics?.attributes[0]?.role;

const truncatedRole = roleText
  ? roleText
      .split('|') 
      .slice(0, 2) 
      .map((role) => role.trim()) 
      .join(' | ') + ' ...'
  : '';

  // if(loading) return <StaffDataLoader/>
  if(error) return <ServerError/>

return (
 
   <Row gutter={16} justify="center" style={{marginTop:"3rem"}}>
   <Col xs={24} lg={22} xxl={18} className="mobile-skills-details" style={{marginBottom:"2rem"}}>
     <Row gutter={16} justify="center" className="mobile-skills-inner-details">
       <Col xs={24} lg={16 }>
        <Card className="full-width white-bg trainee__profile__card">
              <Tabs 
                  defaultActiveKey={profileTab}
                  items={items} 
                  onChange={handleTabOnchange}
                  tabBarExtraContent={
                    <div className="flex-center gap-16">
                      <Button className="dark-orange-bg white-color" onClick={showModal}> Upload Profile</Button>
                      <ExportOutlined className="white-bg dark-orange-color font-18" onClick={handleExportContent}/>
                  </div>
                  }
            />
        </Card>
         </Col>
          {basics?.attributes.length > 0 && (
            <Col xs={24} lg={8} className="user-info-wrapper">
              <Card
                className="white-bg"
                title={
                  <div className="flex-center gap-8" style={{ padding: "0.5rem 0" }}>
                    <Avatar shape="square" size={50}>
                        {initials}
                      </Avatar>
                    <div className="flex" style={{ flexDirection: "column" }}>
                      <span className="user-name-text">{displayName}</span>
                    
                      <Tooltip title={roleText || ''} placement="top">
                      <p
                        className="user-name-sub-text"
                        style={{
                          wordBreak: 'break-word',
                          whiteSpace: 'normal',
                        }}
                      >
                        {truncatedRole}
                      </p>
                    </Tooltip>
                    </div>
                  </div>
                }
                actions={[
                  <div className="flex-end gap-8 pr-16">
                    <Button className="user-action-buttons" onClick={handleEditPersonalInfo} type="text" icon={<EditOutlined />}>
                      Edit
                    </Button>
                  </div>
                ]}
              >
                <div>
                  {basics?.attributes[0]?.email && (
                    <span className="flex gap-8">
                      <MailOutlined /> <p>{basics?.attributes[0]?.email}</p>
                    </span>
                  )}
                  {basics?.attributes[0]?.phone.length > 0 && (
                  <div className="mt-8">
                    {basics.attributes[0].phone.map((phoneEntry, index) => (
                      <span key={index} className="flex-center gap-8">
                        {getIconByName(phoneEntry.name)}
                        <p>{phoneEntry.value}</p>
                      </span>
                    ))}
                  </div>
                )}
                  {basics?.attributes[0].media &&
                  basics?.attributes[0].media.map((me) => {
                    let icon;
                    switch (me.name.toLowerCase()) {
                      case 'linkedin':
                        icon = <LinkedinOutlined />;
                        break;
                      case 'github':
                        icon = <GithubOutlined />;
                        break;
                      case 'medium':
                        icon = <MediumOutlined />;
                        break;
                      default:
                        icon = <FaLink />; 
                    }

                    return (
                      <span className="flex gap-8 mt-8" key={me.link}>
                        {icon}
                        <a href={me.link} target="_blank" rel="noopener noreferrer">
                          {me.name}
                        </a>
                      </span>
                    );
                  })}
                  {location && isLocationValid(location) && (
                      <span className="flex gap-8 mt-8">
                        <EnvironmentOutlined /><p>{location.address}</p>
                      </span>
                    )}
                </div>
              </Card>
            </Col>
          )}
     </Row>
   </Col>
   <Modal
      title="Upload Profile"
      open={uploadProfileModal}
      onCancel={closeModal}
      footer={null}
      width={1000}
    >
      <AddJSONProfile setUploadProfileModal={setUploadProfileModal}/>
    </Modal>
      <Drawer
          title={<div className="d-flex-between" style={{ marginRight: "1rem" }}>Edit Personal Information
            <Button
              type='text'
              style={{ border: 'none' }}
              icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
              onClick={handleMaximize} />
          </div>}
          placement="right"
          onClose={closePersonalInfoDrawer}
          width={width}
          className="close-btn-position"
          open={isPersonalInfoDrawerOpen}>
          <div className="dynamic-drawer-width" onMouseDown={onMouseDown}/>
      <EditPersonalDetails closeDrawer={closePersonalInfoDrawer} />
    </Drawer>
 </Row>
)
}
