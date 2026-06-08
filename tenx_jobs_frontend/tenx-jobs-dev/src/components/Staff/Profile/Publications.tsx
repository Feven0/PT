
import { Avatar, Button, Col, Row } from "antd"
import moment from "moment";
import { FaExternalLinkAlt } from "react-icons/fa";

import { capitalizeFirstChar } from "../../../utils/commonUtils"
import {useAppSelector } from "../../../redux/hooks/hooks";
import DescriptionToggle from "../../commonComponents/DescriptionToggler";
import { no_experience } from "../../../assets";
import '../../../styles/staff.css'

const MAX_DESCRIPTION_LENGTH = 250;

export default function Publications() {
  const {publications } = useAppSelector((state) => state.traineeProfileResponse.user_profile)

  return (<>
    {publications.attributes.length > 0 ? (
      publications.attributes.map((pub, index) => (
        <Col span={24} key={index}
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
                        <span>Show Publication</span> <FaExternalLinkAlt /> </a>
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
      <div className="d-flex-center no-profile-data" style={{ marginBottom: "1rem" }}>
        <div className="d-flex-center no-profile-data-content" style={{ flexDirection: "column" }}>
          <img src={no_experience} width={200} height={150} alt="no-profile" />
          <div className="text-center mt-16">
            <p>There are no publications for this profile</p>
          </div>
        </div>
      </div>
    </Col>
    )}
    </>
  )
}
