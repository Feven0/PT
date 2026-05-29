import { Avatar,Col, Row } from 'antd';
import { capitalizeFirstChar } from '../../../utils/commonUtils';
import { no_experience } from "../../../assets";
import { useAppSelector } from "../../../redux/hooks/hooks";
import DescriptionToggle from "../../commonComponents/DescriptionToggler";

const MAX_DESCRIPTION_LENGTH = 200;

export default function References() {
  const { references } = useAppSelector((state) => state.traineeProfileResponse.user_profile)

  return (
    <>
      {references && references.attributes.length > 0 ? (
        references.attributes.map((ref, index) => (
          <Col
            span={24}
            key={index}
            className={`user-education-wrapper ${index !== references.attributes.length - 1 ? 'with-border' : ''}`}
          >
            <Row gutter={16} className="mt-16">
              <Col span={24}>
                <div className="flex gap-16">
                  <Avatar shape="square" size="small" className="certificate-logo">
                    {`R-${index + 1}`}
                  </Avatar>
                  <div className="full-width">
                    <div className="d-flex-between">
                      <h4>{capitalizeFirstChar(ref?.contact[0].full_name)}</h4>
                    </div>
                    <div>
                      <p className="text-muted">{ref.contact[0].relationship}</p>
                    </div>
                    <div className="mt-16">
                    <DescriptionToggle
                     bio={Array.isArray(ref?.reference_text) 
                      ? ref.reference_text.join(" ") 
                      : typeof ref?.reference_text === "string"
                      ? ref.reference_text 
                      : ""
                    } 
                    maxDescriptionLength={MAX_DESCRIPTION_LENGTH} 
                  />

                    </div>
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
              <p>There are no references for this profile</p>
            </div>
          </div>
        </div>
    </Col>
      )}
    </>
  );
  
}
