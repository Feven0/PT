import { Avatar, Col, Row } from "antd"
import moment from "moment"

import { capitalizeFirstChar } from "../../../utils/commonUtils"
import { calculateDuration } from "../../../utils/dateCalculator"
import DescriptionToggle from "../../commonComponents/DescriptionToggler"
import { no_experience } from "../../../assets"
import { T_TraineeVolunteer } from "../../../types/profileResponse"

type TVolunteer = {
  volunteer: T_TraineeVolunteer
}

export default function VolunteerWork({volunteer}: TVolunteer) {

  return (
    <>
      {volunteer?.attributes?.length > 0 ? (
        volunteer.attributes.map((vol, index) => (
          <Col
            span={24}
            key={index}
            className={`user-education-wrapper ${index !== volunteer.attributes.length - 1 ? 'with-border' : ''}`}>
            <Row gutter={16} className="mt-16">
              <Col span={24}>
                <div className="flex gap-16">
                  <Avatar shape="square" size="small" className="work-experience-logo">
                    {vol?.position?.charAt(0).toUpperCase()}
                  </Avatar>
                  <div className="full-width">
                    <div className="d-flex-between">
                      <h4>{capitalizeFirstChar(vol.position)}</h4>
                    </div>
                    <div>
                      <p>{vol.organization}</p>
                      <div className="flex-center gap-8">
                        {moment(vol.start_date).format('DD MMM YYYY')} - {vol.end_date ? moment(vol.end_date).format('DD MMM YYYY') : 'Present'}
                        <p>{" • "} {calculateDuration(vol.start_date, vol.end_date)}</p>
                      </div>
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
                <p>There are no volunteer works for this profile</p>
              </div>
            </div>
          </div>
        </Col>
      )}
    </>
  );

}