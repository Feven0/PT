import { Avatar, Button, Col, Drawer, Row } from 'antd';
import { EditOutlined, PlusOutlined } from '@ant-design/icons';
import moment from 'moment';
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';

import { capitalizeFirstChar } from '../../../utils/commonUtils';
import AddCertificates from "../Profile/OtherProfiles/AddCertificates";
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { setCertificateUUID, setTraineeCertificates } from "../../../redux/slices/otherProfilesSlice";
import { setCertificateButtonEditing } from "../../../redux/slices/otherProfileSubmitButtonsSlice";
import { no_experience } from "../../../assets";

type TCert = {
  width: number;
  handleMaximize: () => void;
  closeDrawerCertificate: () => void;
  setIsCertificateModalVisible: (value: boolean) => void;
  onMouseDown: (e: any) => void;
  isCertificateModalVisible: boolean;
};

export default function TraineeCertificates({ isCertificateModalVisible, closeDrawerCertificate, width, onMouseDown, handleMaximize, setIsCertificateModalVisible }: TCert) {
  const dispatch = useAppDispatch();
  const {certificates } = useAppSelector((state) => state.traineeProfileResponse.user_profile)
  const handleAddCertificate = () => setIsCertificateModalVisible(true);

  const handleEditCertificate = (uuid: string) => {
    dispatch(setCertificateButtonEditing(true));
    const certificate = certificates.attributes.find((cert) => cert.uuid === uuid);
    dispatch(setCertificateUUID(uuid));
    dispatch(setTraineeCertificates({
      id: certificate?.uuid || "",
      name: certificate?.name || "",
      issuer: certificate?.issuer || "",
      date: certificate?.date || "",
    }));
    setIsCertificateModalVisible(true);
  }

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
                      <div className="flex gap-16" onClick={()=>handleEditCertificate(cert.uuid)}>
                        <EditOutlined className="cursor-pointer" />
                      </div>
                    </div>
                    <div>
                      <p>{cert.issuer}</p>
                      {moment(cert.date, 'YYYY-MM-DD', true).isValid() && (
                        <div className="flex-center gap-8">
                          {moment(cert.date).format('DD MMM YYYY')}
                        </div>
                      )}
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
                <p>Input your previous <span className="profile-empty-name">certifications </span>details to showcase your skills and accomplishments.</p>
              </div>
              <Button
                className="dark-orange-bg white-color mt-16"
                icon={<PlusOutlined />}
                onClick={handleAddCertificate}
              >
                Add Certificate
              </Button>
            </div>
          </div>
        </Col>
      )}
  
      <Drawer
        title={
          <div className="d-flex-between mr-16">
            <span>Add Certificate</span>
            <Button 
              type="text" 
              style={{ border: 'none' }}
              icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
              onClick={handleMaximize}
            />
          </div>
        }
        placement="right"
        closable={true}
        onClose={closeDrawerCertificate}
        open={isCertificateModalVisible}
        width={width}
        className="drawer-container close-btn-position"
      >
        <div className="dynamic-drawer-width" onMouseDown={onMouseDown} />
        <AddCertificates setIsCertificateModalVisible={setIsCertificateModalVisible} />
      </Drawer>
    </>
  );
  
}
