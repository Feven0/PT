
import { useState } from 'react';
import { Button, Col, Divider, message, Row, Tag } from 'antd';
import { InfoCircleOutlined, PlusOutlined, CloseOutlined } from '@ant-design/icons';
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { allCompanySizes, capitalizeFirstChar, normalizeType, priorityLevels } from "../../../utils/commonUtils";
import { useIconRender } from "../../../hooks/useIconRender";
import { PrioritySettingType } from "../../../types/preferenceTypes";
import { addCompanySizePreference, removeCompanySizePreference, updateCompanySizePriority } from "../../../redux/slices/Preferences/companySizeSlice";
import AddNewPref from "./Empty/AddNewPref";
import { setPreferenceControlTag } from "../../../redux/slices/Preferences/preferenceControlSlice";

export default function CompanySizePreference() {
  const [addingNewCompanySize, setAddingNewCompanySize] = useState(false); 
  const [selectedCompanySize, setSelectedCompanySize] = useState<PrioritySettingType | null>(null);
  const [newRolePriority, setNewRolePriority] = useState<'high' | 'medium' | 'low' | null>(null); 
  const [newRoleName, setNewRoleName] = useState('');

  const { company_size } = useAppSelector((state) => state.companySizePreference);

  const { renderIcon } = useIconRender();
  const dispatch = useAppDispatch()

  const allCompanySize = allCompanySizes.filter(
    (type) =>
      !company_size.some((emp) => normalizeType(emp.name) === normalizeType(type))
  );

  const handleTagClick = (role: PrioritySettingType) => setSelectedCompanySize(selectedCompanySize === role ? null : role);
  const handleAddRoleClick = () => setAddingNewCompanySize(!addingNewCompanySize); 

  const handleTagClose = (roleName: string) => {
    dispatch(removeCompanySizePreference(roleName));
    dispatch(setPreferenceControlTag(true));
    if (selectedCompanySize?.name === roleName) {
      setSelectedCompanySize(null);
    }
  };

  const handlePriorityClick = (priority: 'high' | 'medium' | 'low') => {
    if (selectedCompanySize) {
      dispatch(updateCompanySizePriority({ name: selectedCompanySize.name, priority }));
      dispatch(setPreferenceControlTag(true));
      setSelectedCompanySize(null);
    } else if (addingNewCompanySize) {
      setNewRolePriority(priority); 
    }
  };

  const handleAddNewRole = () => {
    if(!newRolePriority) {
      message.error('Please select a priority level for the new role.');
      return;
    }
    if (newRoleName) {
      dispatch(addCompanySizePreference({ name: newRoleName, priority: newRolePriority }));
      dispatch(setPreferenceControlTag(true));
      setNewRoleName(''); 
      setAddingNewCompanySize(false);
    }
  };
 
  return (
    <>
      <Divider/>
      <div className="d-flex-between roles-header">
         <span className="preference__header__title">Company size</span>
      </div>
      <div className="description-text">
         <InfoCircleOutlined />
         <span style={{marginLeft:"8px"}}>
          These keywords help you find the job you want by precisely targeting the company size that aligns with your career goals.
        </span>
      </div>
      {(company_size?.length === 0 && !addingNewCompanySize)? (
        <AddNewPref
         desc="Refine your search by the type of education, like Bachelor's or Master's."
         showAddButton={handleAddRoleClick}
         />
      ) : (
        <div className="company-size-tags-div mt-16 industry-tag-div">
          {company_size?.map((cs: PrioritySettingType) => (
            <Tag
              key={cs.name}
              className="preference__tags roles-tag"
              color={selectedCompanySize?.name === cs.name ? '#FF4405' : undefined}
              style={{
                backgroundColor: selectedCompanySize?.name === cs.name ? '#FF4405' : undefined,
                color: selectedCompanySize?.name === cs.name ? '#fff' : undefined,
                cursor: 'pointer',
                fontSize: "14px"
              }}
              closable
              onClose={() => handleTagClose(cs.name)}
              onClick={() => handleTagClick(cs)}
            >
              {renderIcon(cs.priority)}
              {capitalizeFirstChar(cs.name)}
            </Tag>
          ))}
          { 
          allCompanySize.length > 0 &&
            <Button
            style={{ 
              borderColor: '#FF4405',
              background: addingNewCompanySize ? '#FF4405' : '#fff',
              color: addingNewCompanySize ? '#fff' : '#333',
              opacity: addingNewCompanySize ? 1 : 0.7,
            }}
            icon={!addingNewCompanySize ?  <PlusOutlined />: <CloseOutlined />}
            onClick={handleAddRoleClick}
          >
            {addingNewCompanySize ? 'Cancel' : 'New'}
          </Button>
       }
        </div>
        
      )}
     
        {(selectedCompanySize || addingNewCompanySize) && (
        <Row gutter={16} className="mt-16 input__wrapper-row">
          <Col xs={24} lg={12} className="input__wrapper">
          <div className="mt-16 industry-tag-div">
              {allCompanySize.map((type) => (
                <Tag
                  key={type}
                  color={
                    addingNewCompanySize && newRoleName === type ? '#FF4405' : undefined
                  }
                  style={{
                    color: addingNewCompanySize && newRoleName === type ? '#fff' : '#000',
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
             <div className="mt-8 industry-tag-div">
              {priorityLevels.map((priority) => (
                <Tag
                  key={priority}
                  color={
                    selectedCompanySize && selectedCompanySize.priority === priority
                      ? '#FF4405'
                      : 
                      addingNewCompanySize && newRolePriority === priority
                      ? '#FF4405'
                      : undefined
                  }
                  style={{
                    color:
                      (selectedCompanySize && selectedCompanySize.priority === priority) ||
                      (addingNewCompanySize && newRolePriority === priority)
                        ? '#fff'
                        : '#000',
                    cursor: 'pointer',
                    marginBottom: '0.5rem',
                    padding: '0.25rem 0.5rem',
                  }}
                  closable={!!(selectedCompanySize && selectedCompanySize.priority === priority)}
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
