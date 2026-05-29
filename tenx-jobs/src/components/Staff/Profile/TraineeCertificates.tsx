import { Avatar, Col, Row } from 'antd';
import moment from 'moment';

import { capitalizeFirstChar } from '../../../utils/commonUtils';
import { T_TraineeCertificates } from "../../../types/profileResponse";
import { no_experience } from "../../../assets";

type TCert = {
  certificates: T_TraineeCertificates;
};

export default function TraineeCertificates({ certificates}: TCert) {

  return (
    <>
      {certificates && certificates.attributes.length > 0 ? (
        certificates.attributes.map((cert, index) => (
          <Col
            span={24}
            key={index}
            className={`user-education-wrapper ${index !== certificates.attributes.length - 1 ? 'with-border' : ''}`}
          >
            <Row gutter={16} className="mt-16">
              <Col span={24}>
                <div className="flex gap-16">
                  <Avatar shape="square" size="small" className="certificate-logo">
                    {cert?.name?.charAt(0).toUpperCase()}
                  </Avatar>
                  <div className="full-width">
                    <div className="d-flex-between">
                      <h4>{capitalizeFirstChar(cert.name)}</h4>
                    </div>
                    <div>
                      <p>{cert.issuer}</p>
                      <div className="flex-center gap-8">
                        {moment(cert.date).format('DD MMM YYYY')}
                      </div>
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
                <p>There are no any certificates</p>
              </div>
            </div>
          </div>
        </Col>
      )}
    </>
  );
  
}
