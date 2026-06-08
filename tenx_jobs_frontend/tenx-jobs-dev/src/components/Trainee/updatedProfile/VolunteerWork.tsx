import { Avatar, Button, Col, Drawer, Row } from "antd"
import { EditOutlined, PlusOutlined } from "@ant-design/icons"
import moment from "moment"
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';
import { useState } from "react";

import { capitalizeFirstChar } from "../../../utils/commonUtils"
import { calculateDuration } from "../../../utils/dateCalculator"
import DescriptionToggle from "../../commonComponents/DescriptionToggler"
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { setVolunteerId, setVolunteerWork } from "../../../redux/slices/otherProfilesSlice";
import AddVolunteerWork from "../Profile/OtherProfiles/AddVolunteerWork";
import { setVolunteerButtonEditing } from "../../../redux/slices/otherProfileSubmitButtonsSlice";
import { no_experience } from "../../../assets";

type TVolunteer = {
  width: number,
  onMouseDown: (e: any) => void,
  handleMaximize: () => void,
  closeDrawerVolunteer: () => void,
  isVolunteerModalVisible: boolean,
  setIsVolunteerModalVisible: (value: boolean) => void
}

export default function VolunteerWork({
  width,
  onMouseDown,
  handleMaximize,
  closeDrawerVolunteer,
  isVolunteerModalVisible,
  setIsVolunteerModalVisible,
}: TVolunteer) {
  const {  volunteer } = useAppSelector((state) => state.traineeProfileResponse.user_profile)
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const dispatch = useAppDispatch();

  const handleMouseEnter = (index: number) =>  setHoveredIndex(index);
  const handleMouseLeave = () => setHoveredIndex(null);
  const handleAddVolunteer = () =>  setIsVolunteerModalVisible(true);

  const handleAEditVolunteer = (uuid: string) => {
    dispatch(setVolunteerButtonEditing(true));
    const vol = volunteer.attributes.find((vol) => vol.uuid === uuid);
    dispatch(setVolunteerId(uuid));
    dispatch(setVolunteerWork({
      id: vol?.uuid || "",
      position: vol?.position || "",
      organization: vol?.organization || "",
      duration: [vol?.start_date || "", vol?.end_date || null],
      summary: vol?.summary || ""
    }))
    setIsVolunteerModalVisible(true);
  }

  return (
    <>
      {volunteer?.attributes?.length > 0 ? (
        volunteer.attributes.map((vol, index) => (
          <Col
            span={24}
            key={index}
            className={`user-education-wrapper ${index !== volunteer.attributes.length - 1 ? 'with-border' : ''}`}
            onMouseEnter={() => handleMouseEnter(index)}
            onMouseLeave={handleMouseLeave}
          >
            <Row gutter={16} className="mt-16">
              <Col span={24}>
                <div className="flex gap-16">
                  <Avatar shape="square" size="small" className="work-experience-logo">
                    {vol?.position?.charAt(0).toUpperCase()}
                  </Avatar>
                  <div className="full-width">
                    <div className="d-flex-between">
                      <h4>{capitalizeFirstChar(vol.position)}</h4>
                      {hoveredIndex === index && (
                        <div className="flex gap-16">
                          <EditOutlined className="cursor-pointer" onClick={() => handleAEditVolunteer(vol.uuid)} />
                        </div>
                      )}
                    </div>
                    <div>
                      <p>{vol.organization}</p>
                      {moment(vol.start_date, 'YYYY-MM-DD', true).isValid() && 
                        (!vol.end_date || moment(vol.end_date, 'YYYY-MM-DD', true).isValid()) && (
                          <div className="flex-center gap-8">
                            {moment(vol.start_date).format('DD MMM YYYY')} - {vol.end_date ? moment(vol.end_date).format('DD MMM YYYY') : 'Present'}
                            <p>&nbsp; • &nbsp; {calculateDuration(vol.start_date, vol.end_date)}</p>
                          </div>
                        )}
                    </div>
                    <DescriptionToggle
                      bio={Array.isArray(vol?.summary)
                        ? vol.summary.join(" ")
                        : typeof vol?.summary === "string"
                          ? vol.summary
                          : ""
                      }
                      maxDescriptionLength={100}
                    />
                  </div>
                </div>
              </Col>
            </Row>
          </Col>
        ))
      ) : (
        <Col span={24}>
          <div className="d-flex-center no-profile-data" style={{ marginBottom: "1rem" }}>
            <div className="d-flex-center no-profile-data-content" style={{ flexDirection: "column" }}>
              <img src={no_experience} width={200} height={150} alt="no-profile" />
              <div className="text-center mt-16">
                <p>Input your previous <span className="profile-empty-name">work experience </span> details to showcase your skills and accomplishments.</p>
              </div>
              <Button
                className="dark-orange-bg white-color mt-16"
                icon={<PlusOutlined />}
                onClick={handleAddVolunteer}
              >
                Add Volunteer Work
              </Button>
            </div>
          </div>
        </Col>
      )}
      <Drawer
        title={
          <div className="d-flex-between mr-16">
            <span>Add Volunteer Work</span>
            <Button
              type="text"
              style={{ border: 'none' }}
              icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
              onClick={handleMaximize}
            />
          </div>
        }
        placement="right"
        closable
        onClose={closeDrawerVolunteer}
        open={isVolunteerModalVisible}
        width={width}
        className="drawer-container"
      >
        <div className="dynamic-drawer-width" onMouseDown={onMouseDown} />
        <AddVolunteerWork setIsVolunteerModalVisible={setIsVolunteerModalVisible} />
      </Drawer>
    </>
  );

}