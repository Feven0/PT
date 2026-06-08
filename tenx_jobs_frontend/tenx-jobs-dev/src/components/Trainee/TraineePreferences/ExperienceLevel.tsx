
import { useState } from 'react';
import { Button, Col, Divider, message, Row, Tag } from 'antd';
import { InfoCircleOutlined, PlusOutlined, CloseOutlined } from '@ant-design/icons';
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { allExperienceLevels, capitalizeFirstChar, normalizeType, priorityLevels } from "../../../utils/commonUtils";
import { useIconRender } from "../../../hooks/useIconRender";
import { PrioritySettingType } from "../../../types/preferenceTypes";
import { addExperienceLevelPreference, removeExperienceLevelPreference, updateExperienceLevelPreferencePriority } from "../../../redux/slices/Preferences/experienceLevelSlice";
import AddNewPref from "./Empty/AddNewPref";
import { setPreferenceControlTag } from "../../../redux/slices/Preferences/preferenceControlSlice";

export default function ExperienceLevel() {
  const [addingNewRole, setAddingNewRole] = useState(false); 
  const [selectedRole, setSelectedRole] = useState<PrioritySettingType | null>(null);
  const [newRolePriority, setNewRolePriority] = useState<'high' | 'medium' | 'low' | null>(null); 
  const [newRoleName, setNewRoleName] = useState('');

  const { experience_level } = useAppSelector((state) => state.experienceLevelPreference);
  const { renderIcon } = useIconRender();
  const dispatch = useAppDispatch()

  const handleTagClick = (role: PrioritySettingType) => setSelectedRole(selectedRole === role ? null : role);
  const handleAddRoleClick = () => setAddingNewRole(!addingNewRole); 

  const availableExpLevels = allExperienceLevels.filter(
    (type) =>
      !experience_level.some((emp) => normalizeType(emp.name) === normalizeType(type))
  );

  const handleTagClose = (roleName: string) => {
    dispatch(removeExperienceLevelPreference(roleName));
    dispatch(setPreferenceControlTag(true));
    if (selectedRole?.name === roleName) {
      setSelectedRole(null);
    }
  };

  const handlePriorityClick = (priority: 'high' | 'medium' | 'low') => {
    if (selectedRole) {
      dispatch(updateExperienceLevelPreferencePriority({ name: selectedRole.name, priority }));
      dispatch(setPreferenceControlTag(true));
      setSelectedRole(null);
    } else if (addingNewRole) {
      setNewRolePriority(priority); 
    }
  };

  const handleAddNewRole = () => {
    if(!newRolePriority) {
      message.error('Please select a priority level for the new role.');
      return;
    }
    if (newRoleName) {
      dispatch(addExperienceLevelPreference({ name: newRoleName, priority: newRolePriority }));
      dispatch(setPreferenceControlTag(true));
      setNewRoleName(''); 
      setAddingNewRole(false);
    }
  };

  return (
    <>
      <Divider />
      <div className="d-flex-between roles-header">
        <span className="preference__header__title">Experience levels</span>
      </div>
      <div className="description-text">
        <InfoCircleOutlined />
        <span style={{ marginLeft: "8px" }}>
          Target jobs that match your experience level.
        </span>
      </div>
      {(experience_level?.length === 0 && !addingNewRole ) ? (
        <AddNewPref
          desc="Target jobs that match your experience level."
          showAddButton={handleAddRoleClick}
         />
      ) : (
        <div className="company-size-tags-div mt-16 industry-tag-div">
          {experience_level?.map((exp: PrioritySettingType) => (
            <Tag
              key={exp.name}
              className="preference__tags roles-tag"
              color={selectedRole?.name === exp.name ? '#FF4405' : undefined}
              style={{
                backgroundColor: selectedRole?.name === exp.name ? '#FF4405' : undefined,
                color: selectedRole?.name === exp.name ? '#fff' : undefined,
                cursor: 'pointer',
                fontSize: "14px"
              }}
              closable
              onClose={() => handleTagClose(exp.name)}
              onClick={() => handleTagClick(exp)}
            >
              {renderIcon(exp.priority)}
              {capitalizeFirstChar(exp.name)}
            </Tag>
          ))}
         {
          availableExpLevels.length > 0 && (
            <Button
            style={{  
              borderColor: '#FF4405',
              background: addingNewRole ? '#FF4405' : 'white',
              color: addingNewRole ? 'white' : '#000',
              opacity: addingNewRole ? 1 : 0.7,
            }}
            icon={ !addingNewRole ? <PlusOutlined /> : <CloseOutlined />}
            onClick={handleAddRoleClick}
          >
              {addingNewRole ? 'Cancel' : 'New'}
          </Button>
          )
         }
        </div>
      )}
        {(selectedRole || addingNewRole) && (
          <Row gutter={16} className="mt-16 input__wrapper-row">
            <Col xs={24} lg={12}  className="input__wrapper">
            <div className="mt-16 industry-tag-div">
              {availableExpLevels.map((type) => (
                <Tag
                  key={type}
                  color={
                    addingNewRole && newRoleName === type ? '#FF4405' : undefined
                  }
                  style={{
                    color: addingNewRole && newRoleName === type ? '#fff' : '#000',
                    cursor: 'pointer',
                    marginBottom: '0.5rem',
                    padding: '0.25rem 0.5rem',
                  }}
                  onClick={() => setNewRoleName(type)}
                >
                  {capitalizeFirstChar(type)}
                </Tag>
              ))}
            </div>
              <div className="mt-16 industry-tag-div">
                  {priorityLevels.map((priority) => (
                    <Tag
                      key={priority}
                      color={
                        selectedRole && selectedRole.priority === priority
                          ? '#FF4405'
                          : 
                          addingNewRole && newRolePriority === priority
                          ? '#FF4405'
                          : undefined
                      }
                      style={{
                        color:
                          (selectedRole && selectedRole.priority === priority) ||
                          (addingNewRole && newRolePriority === priority)
                            ? '#fff'
                            : '#000',
                        cursor: 'pointer',
                        marginBottom: '0.5rem',
                        padding: '0.25rem 0.5rem',
                      }}
                      closable={!!(selectedRole && selectedRole.priority === priority)}
                      onClose={(e) => {
                        e.preventDefault();
                        handlePriorityClick(priority as 'high' | 'medium' | 'low');
                      }}
                      onClick={() => {
                        handlePriorityClick(priority as 'high' | 'medium' | 'low');
                      }}
                    >
                      {capitalizeFirstChar(priority)}
                    </Tag>
                  ))}
                </div>
              <Button className="dark-orange-bg white-color mt-16" onClick={handleAddNewRole}>
                Add
              </Button>
              
            </Col>
            </Row>
        )}
        <Divider />
    </>
  );
}
