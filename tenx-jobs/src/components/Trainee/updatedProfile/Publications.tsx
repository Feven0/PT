
import { Avatar, Button, Col, Drawer, Row } from "antd"
import { PlusOutlined, EditOutlined } from "@ant-design/icons"
import moment from "moment";
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';
import { useState } from "react";
import { FaExternalLinkAlt } from "react-icons/fa";

import { capitalizeFirstChar } from "../../../utils/commonUtils"
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { resetTraineePublications, setPublicationUUID, setTraineePublications } from "../../../redux/slices/otherProfilesSlice";
import { setPublicationButtonEditing } from "../../../redux/slices/otherProfileSubmitButtonsSlice";
import DescriptionToggle from "../../commonComponents/DescriptionToggler";
import AddPublications from "../Profile/OtherProfiles/AddPublications";
import { no_experience } from "../../../assets";
import '../../../styles/staff.css'

type T_Publications = {
  width: number,
  handleMaximize: () => void,
  closeDrawerPublication: () => void,
  onMouseDown: (e: any) => void,
  isPublicationDrawerVisible: boolean,
  setIsPublicationDrawerVisible: (value: boolean) => void,
}

const MAX_DESCRIPTION_LENGTH = 250;

export default function Publications({
  isPublicationDrawerVisible,
  closeDrawerPublication,
  width,
  onMouseDown,
  handleMaximize,
  setIsPublicationDrawerVisible
  }: T_Publications) {
    
    const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
    const {publications } = useAppSelector((state) => state.traineeProfileResponse.user_profile)

    const dispatch = useAppDispatch();

    const handleMouseEnter = (index: number) => setHoveredIndex(index);
    const handleMouseLeave = () => setHoveredIndex(null);

  const handleAddPublications = () => {
    dispatch(resetTraineePublications());
    dispatch(setPublicationButtonEditing(false));
    setIsPublicationDrawerVisible(true);
  }

  const handlePublicationEditClick = (uuid: string) => {
    dispatch(setPublicationButtonEditing(true));
    const progLang = publications.attributes.find((pub) => pub.uuid === uuid);
    dispatch(setPublicationUUID(uuid));
    dispatch(setTraineePublications({
      id: progLang?.uuid || "",
      name: progLang?.name || "",
      publisher: progLang?.publisher || "",
      release_date: progLang?.release_date || "",
      url: progLang?.url || "",
      summary: progLang?.summary || "",
    }))
    setIsPublicationDrawerVisible(true);
  }

  return (<>
    {publications.attributes.length > 0 ? (
      publications.attributes.map((pub, index) => (
        <Col span={24} key={index}
          onMouseEnter={() => handleMouseEnter(index)}
          onMouseLeave={handleMouseLeave}
         className={`user-education-wrapper ${index !== publications.attributes.length - 1 ? 'with-border' : ''}`}>
          <Row gutter={16} className="mt-16">
            <Col span={24}>
              <div className="flex gap-16">
                <Avatar shape="square" size="small" className="award-logo">
                  {pub?.name?.charAt(0).toUpperCase()}
                </Avatar>
                <div className="full-width">
                  <div className="d-flex-between">
                    <h4>{capitalizeFirstChar(pub.name)}</h4>
                         {hoveredIndex === index && (
                        <div className="flex gap-16">
                          <EditOutlined
                            className="cursor-pointer"
                            onClick={() => handlePublicationEditClick(pub.uuid)}
                          />
                        </div>
                      )}
                  </div>
                  <div>
                    <div className="flex-center gap-8">
                    <p>{pub.publisher}</p>
                    {"• "}
                    {moment(pub.release_date, 'YYYY-MM-DD', true).isValid() &&  (
                      <div className="flex-center gap-8">
                        {moment(pub.release_date).format('DD MMM YYYY')} 
                      </div>
                    )}
                    </div>
                    {
                    pub.url && 
                    <Button className="publication-button mt-16"
                    >
                      <a 
                        href={pub.url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="flex-center gap-8"
                        >
                        <span>Show Publication</span> <FaExternalLinkAlt />                      </a>
                    </Button>
                    }
                  </div>
                  <DescriptionToggle
                    bio={Array.isArray(pub?.summary)
                      ? pub.summary.join(" ")
                      : typeof pub?.summary === "string"
                        ? pub.summary
                        : ""
                    }
                    maxDescriptionLength={MAX_DESCRIPTION_LENGTH} 
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
              <p>Input your previous <span className="profile-empty-name">publications</span> details to showcase your works.</p>
            </div>
            <Button
              className="dark-orange-bg white-color mt-16"
              icon={<PlusOutlined />}
              onClick={handleAddPublications}>
              Add Publications
            </Button>
            </div>
          </div>
    </Col>
    )}
    <Drawer
          title={<div className="d-flex-between mr-16"><span>Add Programming Language</span>
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
            <AddPublications setIsPublicationDrawerVisible ={setIsPublicationDrawerVisible}/>
        </Drawer>
    </>
  )
}
