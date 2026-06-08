import { Avatar, Button, Col, Drawer, Row } from 'antd';
import { EditOutlined, PlusOutlined } from '@ant-design/icons';
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';

import { capitalizeFirstChar } from '../../../utils/commonUtils';
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import {setReferenceUUID, setTraineeReferences } from "../../../redux/slices/otherProfilesSlice";
import { setCertificateButtonEditing } from "../../../redux/slices/otherProfileSubmitButtonsSlice";
import DescriptionToggle from "../../commonComponents/DescriptionToggler";
import AddReference from "../Profile/OtherProfiles/AddReference";
import { no_experience } from "../../../assets";

type TCert = {
  width: number;
  handleMaximize: () => void;
  closeReferenceDrawer: () => void;
  setIsReferenceDrawerVisible: (value: boolean) => void;
  onMouseDown: (e: any) => void;
  isReferenceDrawerVisible: boolean;
};

const MAX_DESCRIPTION_LENGTH = 200;

export default function TraineeReference({ isReferenceDrawerVisible, closeReferenceDrawer, width, onMouseDown, handleMaximize, setIsReferenceDrawerVisible }: TCert) {
  const { references } = useAppSelector((state) => state.traineeProfileResponse.user_profile)
  const dispatch = useAppDispatch();

  const handleAddCertificate = () => setIsReferenceDrawerVisible(true);

  const handleEditCertificate = (uuid: string) => {
    dispatch(setCertificateButtonEditing(true));
    const ref = references.attributes.find((cert) => cert.uuid === uuid);
    dispatch(setReferenceUUID(uuid));
    dispatch(setTraineeReferences({
      id: ref?.uuid || "",
      priority: ref?.priority || 0,
      reference_text: ref?.reference_text || "",
      contact: {
        full_name: ref?.contact[0].full_name || "",
        email: ref?.contact[0].email || "",
        relationship: ref?.contact[0].relationship || "",
        phone: ref?.contact[0].phone || [],
        remark: ref?.contact[0].remark || []
      }
    }));
    setIsReferenceDrawerVisible(true);
  }

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
                      <div className="flex gap-16" onClick={()=>handleEditCertificate(ref.uuid)}>
                        <EditOutlined className="cursor-pointer" />
                      </div>
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
                <p>Input your previous <span className="profile-empty-name">reference </span>details to showcase your professional history.</p>
              </div>
              <Button
                className="dark-orange-bg white-color mt-16"
                icon={<PlusOutlined />}
                onClick={handleAddCertificate}
              >
                Add Reference
              </Button>
            </div>
          </div>
        </Col>
      )}
  
      <Drawer
        title={
          <div className="d-flex-between mr-16">
            <span>Add Reference</span>
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
        onClose={closeReferenceDrawer}
        open={isReferenceDrawerVisible}
        width={width}
        className="drawer-container close-btn-position"
      >
        <div className="dynamic-drawer-width" onMouseDown={onMouseDown} />
        <AddReference setIsReferenceDrawerVisible={setIsReferenceDrawerVisible} />
      </Drawer>
    </>
  );
  
}
