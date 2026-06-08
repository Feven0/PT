import { useEffect, useState } from "react";
import { Button, Col, Collapse, Drawer, Row } from "antd";
import {PlusOutlined  } from "@ant-design/icons";
import { CollapseProps } from "antd/lib";
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';

//Components
import Bio from "../updatedProfile/Bio";
import Experience from "../updatedProfile/Experience";
import EducationProf from "../updatedProfile/EducationProf";
import VolunteerWork from "../updatedProfile/VolunteerWork";
import Projects from "../updatedProfile/Projects";
import TraineeAwards from "../updatedProfile/TraineeAwards";
import TraineeCertificates from "../updatedProfile/TraineeCertificates";
import TraineeLanguages from "../updatedProfile/TraineeLanguages";
import TraineeReference from "../updatedProfile/TraineeReference";
import Achievements from "../updatedProfile/Achievements";
import Publications from "../updatedProfile/Publications";
import AddJSONProfile from "./AddJSONProfile";
import AddLanguage from "./OtherProfiles/AddLanguage";
import AddVolunteerWork from "./OtherProfiles/AddVolunteerWork";
import AddCertificates from "./OtherProfiles/AddCertificates";
import AddAwards from "./OtherProfiles/AddAwards";
import AddAchievements from "./OtherProfiles/AddAchievements";
import AddPublications from "./OtherProfiles/AddPublications";
import AddReference from "./OtherProfiles/AddReference";

import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { resetEducation, resetExperience, resetProject } from "../../../redux/slices/experienceSlice";
import { resetAchievements, resetLanguages, resetTraineeAwards, resetTraineeCertificates, resetTraineePublications, resetTraineeReferences, resetVolunteerWork } from "../../../redux/slices/otherProfilesSlice";
import { setAchievementButtonEditing, setAwardButtonEditing, setCertificateButtonEditing, setLanguageButtonEditing, setPublicationButtonEditing, setReferenceButtonEditing, setVolunteerButtonEditing } from "../../../redux/slices/otherProfileSubmitButtonsSlice";
import StaffDataLoader from "../../commonComponents/StaffDataLoader";

type TraineeProfileDetailProps = {
  loading: boolean;
}
export default function TraineeProfileDetail({loading}: TraineeProfileDetailProps) {
  const [isExperienceDetailVisible, setIsExperienceDetailVisible] = useState(false);
  const [isEducationFormVisible, setIsEducationFormVisible] = useState(false);
  const [isProjectFormVisible, setIsProjectFormVisible] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [width, setWidth] = useState(540);
  const [uploadProfileModal, setUploadProfileModal] = useState(false)
  const [isLanguageModalVisible, setIsLanguageModalVisible] = useState(false);
  const [isAwardModalVisible, setIsAwardModalVisible] = useState(false);
  const [isCertificateModalVisible, setIsCertificateModalVisible] = useState(false);
  const [isVolunteerModalVisible, setIsVolunteerModalVisible] = useState(false);
  const [isAchievementDrawerVisible, setIsAchievementDrawerVisible] = useState(false);
  const [isPublicationDrawerVisible, setIsPublicationDrawerVisible] = useState(false);
  const [isReferenceDrawerVisible, setIsReferenceDrawerVisible] = useState(false);
  const { awards, basics:bio, education, volunteer,  languages, projects, work_experience:experience, certificates } = useAppSelector((state) => state.traineeProfileResponse.user_profile)
  const {awardButtonEditing, achievementButtonEditing, referenceButtonEditing, volunteerButtonEditing, languageButtonEditing, certificateButtonEditing, publicationButtonEditing} = useAppSelector(state => state.otherProfileSubmitButtons)

  const dispatch = useAppDispatch();
  
  const showDrawer = () => {
    setIsExperienceDetailVisible(true);
    dispatch(resetExperience());
  } 

  const showDrawerAward = () => {
    dispatch(setAwardButtonEditing(false));
    dispatch(resetTraineeAwards());
    setIsAwardModalVisible(true);
  }

  const showDrawerLanguage = () =>  {
     dispatch(setLanguageButtonEditing(false));
     dispatch(resetLanguages());
     setIsLanguageModalVisible(true)
    };

  const showDrawerReference = () => {
    dispatch(setReferenceButtonEditing(false));
    dispatch(resetTraineeReferences())
    setIsReferenceDrawerVisible(true);
  }

  const showDrawerPublication = () => {
    dispatch(setPublicationButtonEditing(false));
    dispatch(resetTraineePublications());
    setIsPublicationDrawerVisible(true);
  }

  const showAchievementDrawer = () => {
    dispatch(setAchievementButtonEditing(false));
    dispatch(resetAchievements());
    setIsAchievementDrawerVisible(true);
  }
  
  const showDrawerVolunteer = () => {
    dispatch(setVolunteerButtonEditing(false));
    dispatch(resetVolunteerWork());
    setIsVolunteerModalVisible(true);
  }
  const showDrawerCertificate = () => {
    dispatch(setCertificateButtonEditing(false));
    dispatch(resetTraineeCertificates());
    setIsCertificateModalVisible(true)
  };

  const closeDrawerVolunteer = () => setIsVolunteerModalVisible(false);
  const closeDrawerAward = () => setIsAwardModalVisible(false);
  const closeDrawerCertificate = () => setIsCertificateModalVisible(false);
  const closeDrawerLanguage = () => setIsLanguageModalVisible(false);
  const closeAchievementDrawer = () => setIsAchievementDrawerVisible(false);
  const closeDrawerPublication = () => setIsPublicationDrawerVisible(false);
  const closeReferenceDrawer = () => setIsReferenceDrawerVisible(false);

  const showEducationDrawer = () => {
    dispatch(resetEducation());
    setIsEducationFormVisible(true);
  }

  const showProjectDrawer = () => {
    dispatch(resetProject());
    setIsProjectFormVisible(true);
  }

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

  const onMouseDown = () => setIsResizing(true);
  const onMouseUp = () => setIsResizing(false);

  const handleMaximize = () => {
    const newWidth = width === 2000 ? 540 : 2000;
    setWidth(newWidth);
  };
 
  if(uploadProfileModal && !education && !bio && !projects && !experience && !volunteer && !awards && !certificates && !languages) {
    return <AddJSONProfile setUploadProfileModal={setUploadProfileModal} />
  }

  const items: CollapseProps['items'] = [
    {
      key: '1',
      label: 'Volunteer Work',
      children: <VolunteerWork 
                width={width}
                closeDrawerVolunteer={closeDrawerVolunteer}
                onMouseDown={onMouseDown}
                handleMaximize={handleMaximize}
                setIsVolunteerModalVisible={setIsVolunteerModalVisible}
                isVolunteerModalVisible={isVolunteerModalVisible} />,
      extra: <PlusOutlined 
              className="plus-outlined-icon" 
              onClick={showDrawerVolunteer} 
              
              />
    },
    {
      key: '2',
      label: 'Awards',
      children: <TraineeAwards 
                width={width}
                closeDrawerAward={closeDrawerAward}
                onMouseDown={onMouseDown}
                handleMaximize={handleMaximize}
                setIsAwardModalVisible={setIsAwardModalVisible}
                isAwardModalVisible={isAwardModalVisible}
                />,
      extra: <PlusOutlined 
              className="plus-outlined-icon" 
              onClick={showDrawerAward} />
    },
    {
      key: '3',
      label: 'Certificates',
      children: <TraineeCertificates
                width={width}
                closeDrawerCertificate={closeDrawerCertificate}
                onMouseDown={onMouseDown}
                handleMaximize={handleMaximize}
                setIsCertificateModalVisible={setIsCertificateModalVisible}
                isCertificateModalVisible={isCertificateModalVisible}
                />,
      extra: <PlusOutlined 
              className="plus-outlined-icon" 
              onClick={showDrawerCertificate} />
    },
    {
      key: '4',
      label: 'Languages',
      children: <TraineeLanguages
                  width={width}
                  closeDrawerLanguage={closeDrawerLanguage}
                  onMouseDown={onMouseDown}
                  handleMaximize={handleMaximize}
                  isLanguageModalVisible={isLanguageModalVisible}
                  setIsLanguageModalVisible={setIsLanguageModalVisible}
                 />,
      extra: <PlusOutlined 
              className="plus-outlined-icon" 
              onClick={showDrawerLanguage} />
    },
    {
      key: '5',
      label: 'Achievements',
      children: <Achievements 
                width={width}
                closeAchievementDrawer={closeAchievementDrawer}
                onMouseDown={onMouseDown}
                handleMaximize={handleMaximize}
                setIsAchievementDrawerVisible={setIsAchievementDrawerVisible}
                isAchievementDrawerVisible={isAchievementDrawerVisible}
                />,
      extra: <PlusOutlined 
              className="plus-outlined-icon" 
              onClick={showAchievementDrawer} />
    },
    {
      key: '6',
      label: 'Publications',
      children: <Publications 
                width={width}
                closeDrawerPublication={closeDrawerPublication}
                onMouseDown={onMouseDown}
                handleMaximize={handleMaximize}
                setIsPublicationDrawerVisible={setIsPublicationDrawerVisible}
                isPublicationDrawerVisible={isPublicationDrawerVisible}
                />,
      extra: <PlusOutlined 
              className="plus-outlined-icon" 
              onClick={showDrawerPublication} />
    },
    {
      key: '7',
      label: 'References',
      children: <TraineeReference 
                width={width}
                closeReferenceDrawer={closeReferenceDrawer}
                onMouseDown={onMouseDown}
                handleMaximize={handleMaximize}
                setIsReferenceDrawerVisible={setIsReferenceDrawerVisible}
                isReferenceDrawerVisible={isReferenceDrawerVisible}
                />,
      extra: <PlusOutlined 
              className="plus-outlined-icon" 
              onClick={showDrawerReference} />
    },
  ]

  if(loading)  return <StaffDataLoader/>
  
  return (
    <Row gutter={16} justify="center" className="profile-detail-container">
       <div className="full-width white-bg bio-card">
        <div className="d-flex-between profile__titles">
         <h3>Bio</h3>
        </div>
        <Bio
          onMouseUp={onMouseUp}
          onMouseDown={onMouseDown}
          isResizing={isResizing}
          drawerVisible={drawerVisible}
          setDrawerVisible={setDrawerVisible}
          handleMaximize={handleMaximize}
          />
      </div>
      
        {/* Experience */}
        <Col span={24}>
          <Row gutter={16}>
            <div className="full-width white-bg">
            <div className="d-flex-between other-profile__titles">
                <h3>Work Experience</h3>
                <div className="flex-center gap-16">
                  <PlusOutlined onClick={showDrawer} className="plus-outlined-icon"/>
                </div>
              </div>
            <Experience
              isExperienceDetailVisible={isExperienceDetailVisible}
              setIsExperienceDetailVisible={setIsExperienceDetailVisible}
              isResizing={isResizing}          
              handleMaximize={handleMaximize}
              onMouseUp={onMouseUp}
              onMouseDown={onMouseDown}
              />
            </div>
          </Row>
        </Col>

        {/* Education */}
        <Col span={24}>
          <Row gutter={16}>
            <div className="full-width white-bg">
            <div className="d-flex-between other-profile__titles">
                  <h3>Education</h3>
                  <div className="flex-center gap-16">
                    <PlusOutlined onClick={showEducationDrawer} className="plus-outlined-icon" />
                  </div>
            </div>
            <EducationProf
                isEducationFormVisible={isEducationFormVisible}
                setIsEducationFormVisible={setIsEducationFormVisible}
                onMouseUp={onMouseUp}
                onMouseDown={onMouseDown}
                isResizing={isResizing}  
                showEducationDrawer={showEducationDrawer}
                handleMaximize={handleMaximize}/>
          </div>
          </Row>
         </Col>

          {/* Projects */}
          <Col span={24}>
            <Row gutter={16}>
              <div className="full-width white-bg">
              <div className="d-flex-between other-profile__titles">
                    <h3>Projects</h3>
                    <div className="flex-center gap-16">
                      <PlusOutlined onClick={showProjectDrawer} className="plus-outlined-icon" />
                    </div>
                  </div>
                <Projects
                  isResizing={isResizing}
                  handleMaximize={handleMaximize}
                  onMouseUp={onMouseUp}
                  onMouseDown={onMouseDown}
                  isProjectFormVisible={isProjectFormVisible}
                  setIsProjectFormVisible={setIsProjectFormVisible}/>
            </div>
            </Row>
         </Col>
         <Col span={24} className="mt-16 other-details-container other-details-title" >
              <div className="full-width white-bg br-8 p-16">
                  <h3>Miscellaneous</h3>
              </div>
         </Col>
         <Col span={24} className="other-details-container">
          <Collapse  
              style={{background:"#fff"}} 
              className="other-details-collapse"
              items={items} 
              defaultActiveKey={['1']} 
              />
        </Col>
        <Drawer
          title={<div className="d-flex-between mr-16"><span>{languageButtonEditing ? "Update Languages" : "Add Language"}</span>
            <Button 
              type='text' 
              style={{ border: 'none' }}
              icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
              onClick={handleMaximize}>
            </Button>
             </div>}
            placement="right"
            closable={true}
            onClose={closeDrawerLanguage}
            open={isLanguageModalVisible}
            width={width}
            className="drawer-container close-btn-position"
            >
            <div className="dynamic-drawer-width" onMouseDown={onMouseDown}/>
          <AddLanguage setIsLanguageModalVisible={setIsLanguageModalVisible}/>
        </Drawer>
        <Drawer
          title={<div className="d-flex-between mr-16"><span>{volunteerButtonEditing ? "Update Volunteer" : "Add Volunteer Work"}</span>
            <Button 
              type='text' 
              style={{ border: 'none' }}
              icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
              onClick={handleMaximize}>
            </Button>
             </div>}
            placement="right"
            closable={true}
            onClose={closeDrawerVolunteer}
            open={isVolunteerModalVisible}
            width={width}
            className="drawer-container close-btn-position"
            >
            <div className="dynamic-drawer-width" onMouseDown={onMouseDown}/>
            <AddVolunteerWork setIsVolunteerModalVisible={setIsVolunteerModalVisible}/>
        </Drawer>
        <Drawer
          title={<div className="d-flex-between mr-16"><span> {awardButtonEditing ? "Update Award" : "Add Award"}</span>
            <Button 
                  type='text' 
                  style={{ border: 'none' }}
                  icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
                  onClick={handleMaximize}>
            </Button>
             </div>}
            placement="right"
            closable={true}
            onClose={closeDrawerAward}
            open={isAwardModalVisible}
            width={width}
            className="drawer-container close-btn-position"
            >
            <div className="dynamic-drawer-width" onMouseDown={onMouseDown}/>
            <AddAwards setIsAwardModalVisible={setIsAwardModalVisible}/>
        </Drawer>
        
        {/* Certificate Drawer */}
        <Drawer
          title={<div className="d-flex-between mr-16"><span> {certificateButtonEditing ? "Update Certificate" : "Add Certificate"}</span>
            <Button 
                  type='text' 
                  style={{ border: 'none' }}
                  icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
                  onClick={handleMaximize}>
            </Button>
             </div>}
            placement="right"
            closable={true}
            onClose={closeDrawerCertificate}
            open={isCertificateModalVisible}
            width={width}
            className="drawer-container close-btn-position"
            >
            <div className="dynamic-drawer-width" onMouseDown={onMouseDown}/>
            <AddCertificates setIsCertificateModalVisible={setIsCertificateModalVisible}/>
        </Drawer>

        {/* Drawer for achievements */}
        <Drawer
          title={<div className="d-flex-between mr-16"><span> {achievementButtonEditing ? "Update Achievement" : "Add Achievement"}</span>
            <Button 
                  type='text' 
                  style={{ border: 'none' }}
                  icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
                  onClick={handleMaximize}>
            </Button>
             </div>}
            placement="right"
            closable={true}
            onClose={closeAchievementDrawer}
            open={isAchievementDrawerVisible}
            width={width}
            className="drawer-container close-btn-position"
            >
            <div className="dynamic-drawer-width" onMouseDown={onMouseDown}/>
            <AddAchievements setIsAchievementDrawerVisible={setIsAchievementDrawerVisible}/>
        </Drawer>
       {/* Publications Drawer */}
        <Drawer
          title={<div className="d-flex-between mr-16"><span>{publicationButtonEditing ? "Update Publications" : "Add Publication"}</span>
            <Button 
                  type='text' 
                  style={{ border: 'none' }}
                  icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
                  onClick={handleMaximize}>
            </Button>
             </div>}
            placement="right"
            closable={true}
            onClose={closeDrawerPublication}
            open={isPublicationDrawerVisible}
            width={width}
            className="drawer-container close-btn-position"
            >
            <div className="dynamic-drawer-width" onMouseDown={onMouseDown}/>
            <AddPublications setIsPublicationDrawerVisible={setIsPublicationDrawerVisible}/>
        </Drawer>

        {/* References Drawer */}
        <Drawer
          title={<div className="d-flex-between mr-16"><span>{referenceButtonEditing ? "Update Reference" : "Add Reference"}</span>
            <Button 
                  type='text' 
                  style={{ border: 'none' }}
                  icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
                  onClick={handleMaximize}>
            </Button>
             </div>}
            placement="right"
            closable={true}
            onClose={closeReferenceDrawer}
            open={isReferenceDrawerVisible}
            width={width}
            className="drawer-container close-btn-position"
            >
            <div className="dynamic-drawer-width" onMouseDown={onMouseDown}/>
            <AddReference setIsReferenceDrawerVisible={setIsReferenceDrawerVisible}/>
        </Drawer>
    </Row>
  )
}

