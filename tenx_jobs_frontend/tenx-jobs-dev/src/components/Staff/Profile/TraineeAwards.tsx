import { Avatar, Col, Row } from "antd"
import moment from "moment"

import { capitalizeFirstChar } from "../../../utils/commonUtils"
import DescriptionToggle from "../../commonComponents/DescriptionToggler"
import { T_TraineeAward } from "../../../types/profileResponse"
import { no_experience } from "../../../assets"

type TAwards = {
  awards: T_TraineeAward,
}

export default function TraineeAwards({awards}: TAwards) {

  return (<>
    {awards.attributes.length > 0 ? (
      awards.attributes.map((award, index) => (
        <Col span={24} key={index}
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
                  </div>
                  <div>
                    <p>{award.awarder}</p>
                    <div className="flex-center gap-8">
                      {moment(award.date).format('DD MMM YYYY')} 
                    </div>
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
              <p>This trainee has no Awards</p>
            </div>
            </div>
          </div>
    </Col>
    )}
    </>
  )
}
