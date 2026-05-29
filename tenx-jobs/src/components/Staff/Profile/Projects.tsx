import { Col, Row, Avatar} from 'antd';
import moment from "moment";

// Components
import DescriptionToggle from "../../commonComponents/DescriptionToggler";
import { T_TraineeProjects } from "../../../types/profileResponse";
import { calculateDuration } from "../../../utils/dateCalculator";
import { no_project } from "../../../assets";
import '../../../styles/slidingCard.css'

type ProjectsProps = {
  projects:T_TraineeProjects
}

const MAX_DESCRIPTION_LENGTH = 200;
export default function Projects({ projects}: ProjectsProps){
  const isValidDate = (date: string) => moment(date, moment.ISO_8601, true).isValid();

  return (
    <>
    {projects?.attributes?.length > 0 ? 
      projects.attributes.map((attr, attrIndex) => {
        const formattedStartDate = isValidDate(attr.start_date) ? moment(attr.start_date).format('DD MMM YYYY') : '';
        const formattedEndDate = attr.end_date && isValidDate(attr.end_date) ? moment(attr.end_date).format('DD MMM YYYY') : 'Present';
        const duration = isValidDate(attr.start_date) && isValidDate(attr.end_date) ? calculateDuration(attr.start_date, attr.end_date) : '';

        return (
          <Col
            span={24}
            className={`mobile-user-profile user-education-wrapper ${attrIndex !== projects.attributes.length - 1 ? "with-border" : ""}`}
            key={attrIndex}
          >
            <Row gutter={8} className="mt-16">
              <Col span={24}>
                <div className="flex gap-16">
                  <Avatar shape="square" size={28} className="work-experience-logo">
                    {attr?.title?.charAt(0).toUpperCase()}
                  </Avatar>
                  <div className="full-width">
                    <div className="d-flex-between">
                      <h4>{attr?.title}</h4>
                    </div>
                    <div className="flex gap-8">
                      {formattedStartDate && (
                        <>
                          {formattedStartDate} - {formattedEndDate}
                          {duration && <p>{" • "}{duration}</p>}
                        </>
                      )}
                    </div>
                    <DescriptionToggle 
                      bio={Array.isArray(attr?.summary) 
                        ? attr.summary.join(" ") 
                        : typeof attr?.summary === "string" 
                        ? attr.summary 
                        : ""
                      } 
                      maxDescriptionLength={MAX_DESCRIPTION_LENGTH} 
                    />
                    {attr?.url && (
                      <p>
                        <a href={attr.url} target="_blank" rel="noopener noreferrer">
                          {attr.url}
                        </a>
                      </p>
                    )}
                  </div>
                </div>
              </Col>
            </Row>
          </Col>
        );
      })
    : (
      <Col span={24}>
        <div className="d-flex-center no-profile-data" style={{ marginBottom: "1rem" }}>
          <div className="d-flex-center no-profile-data-content" style={{ flexDirection: "column" }}>
            <img src={no_project} width={200} height={150} alt="no-profile" />
            <div className="text-center mt-16">
              <p>There are no project details</p>
            </div>
          </div>
        </div>
      </Col>
    )}
  </>
  );
}

