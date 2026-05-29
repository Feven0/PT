import { Avatar, Button, Col, Drawer, Row } from "antd"
import { PlusOutlined, EditOutlined } from "@ant-design/icons"
import moment from "moment"
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';
import { useState } from "react";

import { capitalizeFirstChar } from "../../../utils/commonUtils"
import DescriptionToggle from "../../commonComponents/DescriptionToggler"
import AddAwards from "../Profile/OtherProfiles/AddAwards"
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { resetTraineeAwards, setAwardUUID, setTraineeAwards } from "../../../redux/slices/otherProfilesSlice";
import { setAwardButtonEditing } from "../../../redux/slices/otherProfileSubmitButtonsSlice";
import { no_experience } from "../../../assets";

type TAwards = {
  width: number,
  handleMaximize: () => void,
  closeDrawerAward: () => void,
  onMouseDown: (e: any) => void,
  isAwardModalVisible: boolean,
  setIsAwardModalVisible: (value: boolean) => void,
}

export default function TraineeAwards({
  isAwardModalVisible,
  closeDrawerAward,
  width,
  onMouseDown,
  handleMaximize,
  setIsAwardModalVisible
  }: TAwards) {
    
  const { awards } = useAppSelector((state) => state.traineeProfileResponse.user_profile)

    const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
    const dispatch = useAppDispatch();

    const handleMouseEnter = (index: number) => setHoveredIndex(index);
    const handleMouseLeave = () => setHoveredIndex(null);

  const handleAddAwards = () => {
    dispatch(resetTraineeAwards());
    setIsAwardModalVisible(true);
  }

  const handleAwardEditClick = (uuid: string) => {
    dispatch(setAwardButtonEditing(true));
    const award = awards.attributes.find((awd) => awd.uuid === uuid);
    dispatch(setAwardUUID(uuid));
    dispatch(setTraineeAwards({
      id: award?.uuid || "",
      title: award?.title || "",
      awarder: award?.awarder || "",
      date: award?.date || "",
      summary: award?.summary || "",
      url: award?.url || ""
    }))
    setIsAwardModalVisible(true);
  }

  return (<>
    {awards.attributes.length > 0 ? (
      awards.attributes.map((award, index) => (
        <Col span={24} key={index}
          onMouseEnter={() => handleMouseEnter(index)}
          onMouseLeave={handleMouseLeave}
         className={`user-education-wrapper ${index !== awards.attributes.length - 1 ? 'with-border' : ''}`}>
          <Row gutter={16} className="mt-16">
            <Col span={24}>
              <div className="flex gap-16">
                <Avatar shape="square" size="small" className="award-logo">
                  {award?.title?.charAt(0).toUpperCase()}
                </Avatar>
                <div className="full-width">
                  <div className="d-flex-between">
                    <h4>{capitalizeFirstChar(award.title)}</h4>
                         {hoveredIndex === index && (
                        <div className="flex gap-16">
                          <EditOutlined
                            className="cursor-pointer"
                            onClick={() => handleAwardEditClick(award.uuid)}
                          />
                        </div>
                      )}
                  </div>
                  <div>
                    <p>{award.awarder}</p>
                    {moment(award.date, 'YYYY-MM-DD', true).isValid() && (
                      <div className="flex-center gap-8">
                        {moment(award.date).format('DD MMM YYYY')}
                      </div>
                    )}
                  </div>
                  <DescriptionToggle
                    bio={Array.isArray(award?.summary)
                      ? award.summary.join(" ")
                      : typeof award?.summary === "string"
                        ? award.summary
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
              <p>Input your previous <span className="profile-empty-name">work experience </span> details to showcase your skills and accomplishments.</p>
            </div>
            <Button
              className="dark-orange-bg white-color mt-16"
              icon={<PlusOutlined />}
              onClick={handleAddAwards}>
              Add Volunteer Work
            </Button>
            </div>
          </div>
    </Col>
    )}
    <Drawer
          title={<div className="d-flex-between mr-16"><span>Add Award</span>
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
    </>
  )
}
