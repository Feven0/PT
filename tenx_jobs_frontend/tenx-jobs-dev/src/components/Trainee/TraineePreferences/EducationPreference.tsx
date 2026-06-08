import { useState } from 'react';
import { Button, Col, Input, message, Row, Tag } from 'antd';
import { InfoCircleOutlined,PlusOutlined, CloseOutlined } from '@ant-design/icons';
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { capitalizeFirstChar, priorityLevels } from "../../../utils/commonUtils";
import { useIconRender } from "../../../hooks/useIconRender";
import { PrioritySettingType } from "../../../types/preferenceTypes";
import { addEducationPreference, removeEducationPreference, updateEducationPriority } from "../../../redux/slices/Preferences/educationPreferenceSlice";
import AddNewPref from "./Empty/AddNewPref";
import { setPreferenceControlTag } from "../../../redux/slices/Preferences/preferenceControlSlice";

export default function EducationPreference() {
  const [addingNewRole, setAddingNewRole] = useState(false); 
  const [selectedRole, setSelectedRole] = useState<PrioritySettingType | null>(null);
  const [newRolePriority, setNewRolePriority] = useState<'high' | 'medium' | 'low' | null>(null); 
  const [newRoleName, setNewRoleName] = useState('');

  const { education } = useAppSelector((state) => state.educationPreference);
  const { renderIcon } = useIconRender();
  const dispatch = useAppDispatch();

  const handleTagClick = (role: PrioritySettingType) => setSelectedRole(selectedRole === role ? null : role);
  const handleAddRoleClick = () => setAddingNewRole(!addingNewRole); 

  const handleTagClose = (roleName: string) => {
    dispatch(removeEducationPreference(roleName));
    dispatch(setPreferenceControlTag(true));
    if (selectedRole?.name === roleName) {
      setSelectedRole(null);
    }
  };

  const handlePriorityClick = (priority: 'high' | 'medium' | 'low') => {
    if (selectedRole) {
      dispatch(updateEducationPriority({ name: selectedRole.name, priority }));
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
      dispatch(addEducationPreference({ name: newRoleName, priority: newRolePriority }));
      dispatch(setPreferenceControlTag(true));
      setNewRoleName(''); 
      setAddingNewRole(false);
    }
  };


  return (
    <>
      <div className="d-flex-between roles-header mb-8">
        <span className="preference__header__title">Education</span>
      </div>
      <div className="description-text">
        <InfoCircleOutlined />
        <span style={{ marginLeft: "8px" }}>
          These keywords target jobs that match your education level and qualifications.
        </span>
      </div>
      {(education?.length === 0 && !addingNewRole) ? (
       <AddNewPref
        desc="Refine your search by the type of education, like Bachelor's or Master's."
        showAddButton={handleAddRoleClick}
         />
      ) : (
        <div className="company-size-tags-div mt-16 industry-tag-div">
          {education?.map((role: PrioritySettingType) => (
            <Tag
              key={role.name}
              className="preference__tags roles-tag"
              color={selectedRole?.name === role.name ? '#FF4405' : undefined}
              style={{
                backgroundColor: selectedRole?.name === role.name ? '#FF4405' : undefined,
                color: selectedRole?.name === role.name ? '#fff' : undefined,
                cursor: 'pointer',
              }}
              closable
              onClose={() => handleTagClose(role.name)}
              onClick={() => handleTagClick(role)}
            >
              {renderIcon(role.priority)}
              {capitalizeFirstChar(role.name)}
            </Tag>
          ))}
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
          
        </div>
        
      )}
         {(selectedRole || addingNewRole) && (
          <Row gutter={16} className="mt-16 input__wrapper-row">
            <Col xs={24} lg={12} className="input__wrapper">
              <Input
                placeholder="Enter role name"
                value={newRoleName}
                className="mt-16"
                onChange={(e) => setNewRoleName(e.target.value)}
                style={{ marginBottom: '8px' }}
              />
                <div className="mt-16 industry-tag-div">
                  {priorityLevels?.map((priority) => (
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
    </>
  );
}
