import { Avatar, Button, Col, Drawer, Row } from "antd";
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';

import {EditOutlined, PlusOutlined  } from "@ant-design/icons";
import { capitalizeFirstChar } from "../../../utils/commonUtils";
import AddLanguage from "../Profile/OtherProfiles/AddLanguage";
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { setLanguages, setLanguageUUID } from "../../../redux/slices/otherProfilesSlice";
import { setLanguageButtonEditing } from "../../../redux/slices/otherProfileSubmitButtonsSlice";

import { no_experience } from "../../../assets";

type TraineeLanguagesProps = {
  width: number;
  handleMaximize: () => void;
  closeDrawerLanguage: () => void;
  onMouseDown: (e: any) => void;
  isLanguageModalVisible: boolean;
  setIsLanguageModalVisible: (value: boolean) => void;
}

export default function TraineeLanguages({ isLanguageModalVisible, setIsLanguageModalVisible, width, handleMaximize, closeDrawerLanguage, onMouseDown }: TraineeLanguagesProps) {
  const { languages } = useAppSelector((state) => state.traineeProfileResponse.user_profile)
  const dispatch = useAppDispatch();

  const handleAddLanguage = () => setIsLanguageModalVisible(true);

  const handleEditLanguage = (uuid: string) => {
    dispatch(setLanguageButtonEditing(true));
    const language = languages.attributes.find((lang) => lang.uuid === uuid);    
    dispatch(setLanguageUUID(uuid))
    dispatch(setLanguages({
      id: language?.uuid || "",
      fluency: language?.fluency || "",
      language: language?.language || ""
    })
  );
  setIsLanguageModalVisible(true);
  }

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
                      <div className="flex gap-16" onClick={()=>handleEditLanguage(lang.uuid)}>
                        <EditOutlined className="cursor-pointer" />
                      </div>
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
                  Input your previous <span className="profile-empty-name">languages </span>details to showcase your skills and accomplishments.
                </p>
              </div>
              <Button
                className="dark-orange-bg white-color mt-16"
                icon={<PlusOutlined />}
                onClick={handleAddLanguage}
              >
                Add Language
              </Button>
            </div>
          </div>
        </Col>
      )}
  
      <Drawer
        title={
          <div className="d-flex-between mr-16">
            <span>Add Volunteer Work</span>
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
        onClose={closeDrawerLanguage}
        open={isLanguageModalVisible}
        width={width}
        className="drawer-container close-btn-position"
      >
        <div className="dynamic-drawer-width" onMouseDown={onMouseDown} />
        <AddLanguage setIsLanguageModalVisible={setIsLanguageModalVisible} />
      </Drawer>
    </>
  );
}  
