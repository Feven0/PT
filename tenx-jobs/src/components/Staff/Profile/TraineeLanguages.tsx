import { Avatar, Col, Row } from "antd";
import { no_experience } from "../../../assets";
import { capitalizeFirstChar } from "../../../utils/commonUtils";
import { T_TraineeLanguages } from "../../../types/profileResponse";

type TraineeLanguagesProps = {
  languages: T_TraineeLanguages;
}

export default function TraineeLanguages({ languages }: TraineeLanguagesProps) {

  return (
    <>
      {languages && languages.attributes.length > 0 ? (
        languages.attributes.map((lang, index) => (
          <Col
            span={24}
            key={index}
            className={`user-education-wrapper ${index !== languages.attributes.length - 1 ? 'with-border' : ''}`}
          >
            <Row gutter={16} className="mt-16">
              <Col span={24}>
                <div className="flex gap-16">
                  <Avatar shape="square" size="small" className="language-logo">
                    {lang.language.charAt(0).toUpperCase()}
                  </Avatar>
                  <div className="full-width">
                    <div className="d-flex-between">
                      <h4>{capitalizeFirstChar(lang.language)}</h4>
                    </div>
                    <div>
                      <p>{lang.fluency}</p>
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
                <p>
                  This trainee has no languages added
                </p>
              </div>
            </div>
          </div>
        </Col>
      )}
    </>
  );
}  
