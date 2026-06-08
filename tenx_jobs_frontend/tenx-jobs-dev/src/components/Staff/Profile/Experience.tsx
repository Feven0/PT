import { Avatar, Col, Row } from "antd";
import moment from "moment";

import DescriptionToggle from "../../commonComponents/DescriptionToggler";
import { T_TraineeWorkExperience } from "../../../types/profileResponse";

import { calculateDuration } from "../../../utils/dateCalculator";
import { capitalizeFirstChar } from "../../../utils/commonUtils";
import { no_experience } from "../../../assets";

type UserExpProps = {
  userExp: T_TraineeWorkExperience
}

const MAX_DESCRIPTION_LENGTH = 200;

export default function Experience({ userExp}: UserExpProps) {
  return (
    <>
      {userExp?.attributes?.length > 0 ?
      userExp.attributes.map((exp, index) => (
        <Col span={24} key={index} className={`user-education-wrapper ${index !== userExp.attributes.length - 1 ? 'with-border' : ''}`}>
          <Row gutter={16} className="mt-16">
            <Col span={24}>
              <div className="flex gap-16">
                <Avatar shape="square" size="small" className="work-experience-logo">
                  {exp?.role?.charAt(0).toUpperCase()}
                </Avatar>
                <div className="full-width">
                  <div className="d-flex-between">
                  <h4>{capitalizeFirstChar(exp.role)}</h4>
                  </div>
                  <div>
                    <p>{exp.company}</p>
                    <p>{exp.location}</p>
                    <div className="flex-center gap-8">
                      {moment(exp.start_date).format('DD MMM YYYY')} - {exp.end_date ? moment(exp.end_date).format('DD MMM YYYY') : 'Present'}
                      <p> {" •  "} {calculateDuration(exp.start_date, exp.end_date)}</p>
                    </div>
                  </div>
                  <DescriptionToggle
                    bio={Array.isArray(exp?.summary) 
                      ? exp.summary.join(" ") 
                      : typeof exp?.summary === "string"
                      ? exp.summary 
                      : ""
                    } 
                    maxDescriptionLength={MAX_DESCRIPTION_LENGTH} 
                  />
                </div>
              </div>
            </Col>
          </Row>
        </Col>
      )):
      <Col span={24}>
         <div className="d-flex-center no-profile-data" style={{ marginBottom:"1rem"}}>
            <div className="d-flex-center no-profile-data-content" style={{flexDirection:"column"}}>
            <img src={no_experience} width={200} height={150} alt="no-profile" />
            <div className="text-center mt-16">
              <p>This trainee has no work experience</p>
            </div>
            </div>
          </div>
    </Col>
      }
    </>
  );
}

