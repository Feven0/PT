import { Avatar, Button, Col, Drawer, Row } from "antd"
import { PlusOutlined, EditOutlined } from "@ant-design/icons"
import moment from "moment"
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';
import { useState } from "react";

import { capitalizeFirstChar } from "../../../utils/commonUtils"
import DescriptionToggle from "../../commonComponents/DescriptionToggler"
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { resetAchievements, setAchievementUUID, setTraineeAchievements } from "../../../redux/slices/otherProfilesSlice";
import { setAchievementButtonEditing } from "../../../redux/slices/otherProfileSubmitButtonsSlice";
import AddAchievements from "../Profile/OtherProfiles/AddAchievements";

import { no_experience } from "../../../assets";

type T_Achievements = {
  width: number,
  handleMaximize: () => void,
  closeAchievementDrawer: () => void,
  onMouseDown: (e: any) => void,
  isAchievementDrawerVisible: boolean,
  setIsAchievementDrawerVisible: (value: boolean) => void,
}

export default function Achievements({
  isAchievementDrawerVisible,
  closeAchievementDrawer,
  width,
  onMouseDown,
  handleMaximize,
  setIsAchievementDrawerVisible
  }: T_Achievements) {
    
    const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
    const {achievements } = useAppSelector((state) => state.traineeProfileResponse.user_profile)

    const dispatch = useAppDispatch();

    const handleMouseEnter = (index: number) => setHoveredIndex(index);
    const handleMouseLeave = () => setHoveredIndex(null);

  const handleAddAChievements = () => {
    dispatch(resetAchievements());
    dispatch(resetAchievements());
    setIsAchievementDrawerVisible(true);
  }

  const handleAwardEditClick = (uuid: string) => {
    dispatch(setAchievementButtonEditing(true));
    const achievementsState = achievements.attributes.find((awd) => awd.uuid === uuid);
    dispatch(setAchievementUUID(uuid));
    dispatch(setTraineeAchievements({
      id: achievementsState?.uuid || "",
      title: achievementsState?.title || "",
      summary: achievementsState?.summary || "",
      date: achievementsState?.date || "",
    }))
    setIsAchievementDrawerVisible(true);
  }

  return (<>
    {achievements.attributes.length > 0 ? (
      achievements.attributes.map((achievement, index) => (
        <Col span={24} key={index}
          onMouseEnter={() => handleMouseEnter(index)}
          onMouseLeave={handleMouseLeave}
         className={`user-education-wrapper ${index !== achievements.attributes.length - 1 ? 'with-border' : ''}`}>
          <Row gutter={16} className="mt-16">
            <Col span={24}>
              <div className="flex gap-16">
                <Avatar shape="square" size="small" className="award-logo">
                  {achievement?.title?.charAt(0).toUpperCase()}
                </Avatar>
                <div className="full-width">
                  <div className="d-flex-between">
                    <h4>{capitalizeFirstChar(achievement.title)}</h4>
                         {hoveredIndex === index && (
                        <div className="flex gap-16">
                          <EditOutlined
                            className="cursor-pointer"
                            onClick={() => handleAwardEditClick(achievement.uuid)}
                          />
                        </div>
                      )}
                  </div>
                  <div>
                    <p>{achievement.title}</p>
                    {moment(achievement.date, 'YYYY-MM-DD', true).isValid() && (
                      <div className="flex-center gap-8">
                        {moment(achievement.date).format('DD MMM YYYY')}
                      </div>
                    )}
                  </div>
                  <DescriptionToggle
                    bio={Array.isArray(achievement?.summary)
                      ? achievement.summary.join(" ")
                      : typeof achievement?.summary === "string"
                        ? achievement.summary
                        : ""
                    }
                    maxDescriptionLength={150} 
                  />
                </div>
              </div>
            </Col>
          </Row>
        </Col>
      ))
    ) : (
      <Col span={24}>
      <div className="d-flex-center no-profile-data" style={{ marginBottom:"1rem"}}>
        <div className="d-flex-center no-profile-data-content" style={{flexDirection:"column"}}>
          <img src={no_experience} width={200} height={150} alt="no-profile" />
            <div className="text-center mt-16">
              <p>Input your previous <span className="profile-empty-name">achievements</span> details to showcase your accomplishments.</p>
            </div>
            <Button
              className="dark-orange-bg white-color mt-16"
              icon={<PlusOutlined />}
              onClick={handleAddAChievements}>
              Add Achievements
            </Button>
            </div>
          </div>
    </Col>
    )}
    <Drawer
          title={<div className="d-flex-between mr-16"><span>Add Achievement</span>
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
            <AddAchievements setIsAchievementDrawerVisible ={setIsAchievementDrawerVisible}/>
        </Drawer>
    </>
  )
}
