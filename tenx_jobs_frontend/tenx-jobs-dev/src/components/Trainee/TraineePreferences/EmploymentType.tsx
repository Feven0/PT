
import { useState } from 'react';
import { Button, Col, message, Row, Tag } from 'antd';
import { InfoCircleOutlined, PlusOutlined, CloseOutlined } from '@ant-design/icons';
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { allEmploymentTypes, capitalizeFirstChar, normalizeType, priorityLevels } from "../../../utils/commonUtils";
import { useIconRender } from "../../../hooks/useIconRender";
import { PrioritySettingType } from "../../../types/preferenceTypes";
import { addEmployment, removeEmployment, updateEmploymentPriority } from "../../../redux/slices/Preferences/employmentTypeSlice";
import AddNewPref from "./Empty/AddNewPref";
import { setPreferenceControlTag } from "../../../redux/slices/Preferences/preferenceControlSlice";

export default function EmploymentType() {
  const [addingNewEmpType, setAddingNewEmpType] = useState(false); 
  const [selectedEmpType, setSelectedRole] = useState<PrioritySettingType | null>(null);
  const [newEmpTypePriority, setNewEmpTypePriority] = useState<'high' | 'medium' | 'low' | null>(null); 
  const [newRoleName, setNewRoleName] = useState('');

  const { employment } = useAppSelector((state) => state.employmentType);
  const { renderIcon } = useIconRender();
  const dispatch = useAppDispatch()

  const handleTagClick = (role: PrioritySettingType) => setSelectedRole(selectedEmpType === role ? null : role);
  const handleAddRoleClick = () => setAddingNewEmpType(!addingNewEmpType); 

  const availableEmpTypes = allEmploymentTypes.filter(
    (type) =>
      !employment.some((emp) => normalizeType(emp.name) === normalizeType(type))
  );

  const handleTagClose = (roleName: string) => {
    dispatch(removeEmployment(roleName));
    dispatch(setPreferenceControlTag(true));
    if (selectedEmpType?.name === roleName) {
      setSelectedRole(null);
    }
  };

  const handlePriorityClick = (priority: 'high' | 'medium' | 'low') => {
    if (selectedEmpType) {
      dispatch(updateEmploymentPriority({ name: selectedEmpType.name, priority }));
      dispatch(setPreferenceControlTag(true));
      setSelectedRole(null);
    } else if (addingNewEmpType) {
      setNewEmpTypePriority(priority); 
    }
  };

  const handleAddNewRole = () => {
    if(!newEmpTypePriority) {
      message.error('Please select a priority level for the new role.');
      return;
    }
    if (newRoleName) {
      dispatch(addEmployment({ name: newRoleName, priority: newEmpTypePriority }));
      dispatch(setPreferenceControlTag(true));
      setNewRoleName(''); 
      setAddingNewEmpType(false);
    }
  };

  return (
    <>
      <div className="d-flex-between roles-header">
        <span className="preference__header__title">Employment types</span>
      </div>
      <div className="description-text">
        <InfoCircleOutlined />
        <span style={{ marginLeft: "8px" }}>
          Refine your search by the type of employment, like full-time or contract.
        </span>
      </div>
      {(employment?.length === 0 && !addingNewEmpType) ? (
        <AddNewPref
          desc="Refine your search by the type of employment, like full-time or contract."
          showAddButton={handleAddRoleClick}
         />
      ) : (
        <div className="company-size-tags-div mt-16 industry-tag-div">
          {employment?.map((emp: PrioritySettingType) => (
            <Tag
              key={emp.name}
              className="preference__tags roles-tag"
              color={selectedEmpType?.name === emp.name ? '#FF4405' : undefined}
              style={{
                backgroundColor: selectedEmpType?.name === emp.name ? '#FF4405' : undefined,
                color: selectedEmpType?.name === emp.name ? '#fff' : undefined,
                cursor: 'pointer',
                fontSize: "14px"
              }}
              closable
              onClose={() => handleTagClose(emp.name)}
              onClick={() => handleTagClick(emp)}
            >
              {renderIcon(emp.priority)}
              {capitalizeFirstChar(emp.name)}
            </Tag>
          ))}
          {availableEmpTypes.length > 0 && (
              <Button
                style={{ 
                  borderColor: '#FF4405',
                  background: addingNewEmpType ? '#FF4405' : 'white',
                  color: addingNewEmpType ? 'white' : '#000',
                  opacity: addingNewEmpType ? 1 : 0.7,
                }}
                icon={!addingNewEmpType ? <PlusOutlined /> : <CloseOutlined />}
                onClick={handleAddRoleClick}
              >
                {addingNewEmpType ? 'Cancel' : 'New'}
              </Button>
            )}
        </div>
      )}
        {(selectedEmpType || addingNewEmpType) && (
          <Row gutter={16} className="mt-16 input__wrapper-row">
          <Col xs={24} lg={12} className="input__wrapper">
           <div className="mt-16 industry-tag-div">
              {availableEmpTypes.map((type) => (
                <Tag
                  key={type}
                  color={
                    addingNewEmpType && newRoleName === type ? '#FF4405' : undefined
                  }
                  style={{
                    color: addingNewEmpType && newRoleName === type ? '#fff' : '#000',
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
            {priorityLevels?.map((priority) => (
              <Tag
                key={priority}
                color={
                  selectedEmpType && selectedEmpType.priority === priority
                    ? '#FF4405'
                    : 
                    addingNewEmpType && newEmpTypePriority === priority
                    ? '#FF4405'
                    : undefined
                }
                style={{
                  color:
                    (selectedEmpType && selectedEmpType.priority === priority) ||
                    (addingNewEmpType && newEmpTypePriority === priority)
                      ? '#fff'
                      : '#000',
                  cursor: 'pointer',
                  marginBottom: '0.5rem',
                  padding: '0.25rem 0.5rem',
                }}
                closable={!!(selectedEmpType && selectedEmpType.priority === priority)}
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
