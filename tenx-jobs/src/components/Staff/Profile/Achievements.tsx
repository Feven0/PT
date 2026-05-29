import { Avatar, Col, Row } from "antd"
import moment from "moment"

import { capitalizeFirstChar } from "../../../utils/commonUtils"
import DescriptionToggle from "../../commonComponents/DescriptionToggler"
import { useAppSelector } from "../../../redux/hooks/hooks";
import { no_experience } from "../../../assets";

export default function Achievements() {
  const {achievements } = useAppSelector((state) => state.traineeProfileResponse.user_profile)

  return (<>
    {achievements.attributes.length > 0 ? (
      achievements.attributes.map((achievement, index) => (
        <Col span={24} key={index}
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
      <div className="d-flex-center no-profile-data" style={{ marginBottom: "1rem" }}>
        <div className="d-flex-center no-profile-data-content" style={{ flexDirection: "column" }}>
          <img src={no_experience} width={200} height={150} alt="no-profile" />
          <div className="text-center mt-16">
            <p>There are no achievements for this profile</p>
          </div>
        </div>
      </div>
    </Col>
    )}
    </>
  )
}
