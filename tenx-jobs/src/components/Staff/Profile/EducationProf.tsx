import { Avatar, Button, Col, Row } from "antd";
import { FaLink } from "react-icons/fa";
import moment from "moment";

import DescriptionToggle from "../../commonComponents/DescriptionToggler";

import { calculateDuration } from "../../../utils/dateCalculator";
import { noProfile } from "../../../assets";
import { T_TraineeEducation } from "../../../types/profileResponse";
import '../../../styles/slidingCard.css'

  type SortedEducationProps = {
    userEdu: T_TraineeEducation;
  }

const MAX_DESCRIPTION_LENGTH = 250;
export default function EducationProf({userEdu}: SortedEducationProps) {

  const sortedEducation = [...userEdu.attributes].sort((a, b) => {
    return new Date(b.end_date).getTime() - new Date(a.end_date).getTime();
  });

  return (
    <>
      {userEdu?.attributes?.length >0 ?
      sortedEducation.map((edu, index) => (
        <Col span={24} className={`mobile-user-profile user-education-wrapper ${index !== userEdu.attributes.length - 1 ? 'with-border' : ''}`} key={index} >
          <Row gutter={8} className="mt-16">
            <Col span={24} >
              <div className="flex gap-16">
                <Avatar shape="square" size="small" className="work-experience-logo">
                  {edu.institution_name.charAt(0).toUpperCase()}
                </Avatar>
                <div className="full-width">
                  <div className="d-flex-between">
                    <h4>{edu.institution_name}</h4>
                  </div>
                  <div>
                    {edu.study_area && <p>{edu.study_area}</p>}
                    {edu.study_type  && <p>{edu.study_type}</p>}
                    <div className="flex-center gap-8">
                      {edu.country && <span>{edu.country}</span> }
                    </div>
                      {edu.score && <span>Score - {edu.score}</span>}
                  </div>
                  <div className="flex-center gap-8">
                      {moment(edu.start_date).format('DD MMM YYYY')} - {edu.end_date ? moment(edu.end_date).format('DD MMM YYYY') : 'Present'}
                      <p> {" •  "} {calculateDuration(edu.start_date, edu.end_date)}</p>
                    </div>
                  <br/><span className="mt-16">
                        {
                          edu.institution_url && <a href={edu.institution_url} target="_blank" rel="noreferrer">
                          <Button icon={<FaLink />} className="white-bg dark-orange-color mt-8">Visit Site</Button>
                        </a>
                        }
                      </span>
                  <DescriptionToggle bio={edu?.remark} maxDescriptionLength={MAX_DESCRIPTION_LENGTH} /> 
                </div>
              </div>
            </Col>
          </Row>
        </Col>
      )): 
      <Col span={24}>
          <div className="d-flex-center no-profile-data" style={{ marginBottom:"1rem"}}>
            <div className="d-flex-center no-profile-data-content" style={{flexDirection:"column"}}>
            <img src={noProfile} width={200} height={150} alt="no-profile" />
            <div className="text-center mt-16">
              <p>No Education provided</p>
            </div>
            </div>
          </div>
    </Col>
      }
    </>
  );
}