import { useState } from 'react';
import { Button, Col, Input, message, Row, Tag } from 'antd';
import { InfoCircleOutlined, PlusOutlined, CloseOutlined } from '@ant-design/icons';
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { capitalizeFirstChar, priorityLevels } from "../../../utils/commonUtils";
import { useIconRender } from "../../../hooks/useIconRender";
import { PrioritySettingType } from "../../../types/preferenceTypes";
import { addJobIndustry, removeJobIndustry, updateJobIndustryPriority } from "../../../redux/slices/Preferences/jobIndustrySlice";
import AddNewPref from "./Empty/AddNewPref";
import { setPreferenceControlTag } from "../../../redux/slices/Preferences/preferenceControlSlice";

export default function JobIndustryPreference() {
  const [addingNewIndustry, setAddingNewIndustry] = useState(false); 
  const [selectedIndustry, setSelectedIndustry] = useState<PrioritySettingType | null>(null);
  const [newIndustryPriority, setNewIndustryPriority] = useState<'high' | 'medium' | 'low' | null>(null); 
  const [newIndustry, setIndustry] = useState('');

  const { industry } = useAppSelector((state) => state.industryPreference);
  const {renderIcon} = useIconRender();
  const dispatch = useAppDispatch()

  const handleTagClick = (role: PrioritySettingType) => setSelectedIndustry(selectedIndustry === role ? null : role);
  const handleAddIndustry = () => setAddingNewIndustry(!addingNewIndustry); 

  const handleTagClose = (roleName: string) => {
    dispatch(removeJobIndustry(roleName));
    dispatch(setPreferenceControlTag(true));
    if (selectedIndustry?.name === roleName) {
      setSelectedIndustry(null);
    }
  };

  const handlePriorityClick = (priority: 'high' | 'medium' | 'low') => {
    if (selectedIndustry) {
      dispatch(updateJobIndustryPriority({ name: selectedIndustry.name, priority }));
      dispatch(setPreferenceControlTag(true));
      setSelectedIndustry(null);
    } else if (addingNewIndustry) {
      setNewIndustryPriority(priority); 
    }
  }

  const handleAddNewRole = () => {
    if(!newIndustryPriority) {
      message.error('Please select a priority level for the new role.');
      return;
    }
    if (newIndustry) {
      dispatch(addJobIndustry({ name: newIndustry, priority: newIndustryPriority }));
      dispatch(setPreferenceControlTag(true));
      setIndustry(''); 
      setAddingNewIndustry(false);
    }
  };

 
  return (
    <>
      <div className="d-flex-between roles-header mb-8">
         <span className="preference__header__title">Industry</span>
      </div>
      <div className="description-text">
         <InfoCircleOutlined />
         <span style={{marginLeft:"8px"}}>Select industries here to tailor your job search results to match roles and opportunities specifically within that field</span> 
      </div>
        {(industry?.length === 0 && !addingNewIndustry) ? 
        <AddNewPref
          desc="Select industries here to tailor your job search results to match roles and opportunities specifically within that field"
          showAddButton={handleAddIndustry}
         />:
          <div className="company-size-tags-div mt-16 industry-tag-div">
          {industry?.map((role: PrioritySettingType) => (
            <Tag
              key={role.name}
              className="preference__tags roles-tag"
              color={selectedIndustry?.name === role.name ? '#FF4405' : undefined}
              style={{
                backgroundColor: selectedIndustry?.name === role.name ? '#FF4405' : undefined,
                color: selectedIndustry?.name === role.name ? '#fff' : undefined,
                cursor: 'pointer',
                fontSize: "14px"
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
            background: addingNewIndustry ? '#FF4405' : 'white',
            color: addingNewIndustry ? 'white' : '#000',
            opacity: addingNewIndustry ? 1 : 0.7,
          }}
          icon={ !addingNewIndustry ? <PlusOutlined /> : <CloseOutlined />}
          onClick={handleAddIndustry}
        >
          {addingNewIndustry ? 'Cancel' : 'New'}
        </Button>
        </div>
        }
        {(selectedIndustry || addingNewIndustry) && (
            <Row gutter={16} className="mt-16 input__wrapper-row">
              <Col xs={24} lg={12} className="input__wrapper">
                <Input
                  placeholder="Enter industry name"
                  value={newIndustry}
                  className="mt-16"
                  onChange={(e) => setIndustry(e.target.value)}
                  style={{ marginBottom: '8px' }}
                />

              <div className="mt-16 industry-tag-div">
                {priorityLevels?.map((priority) => (
                  <Tag
                    key={priority}
                    color={
                      selectedIndustry && selectedIndustry.priority === priority
                        ? '#FF4405'
                        : 
                        addingNewIndustry && newIndustryPriority === priority
                        ? '#FF4405'
                        : undefined
                    }
                    style={{
                      color:
                        (selectedIndustry && selectedIndustry.priority === priority) ||
                        (addingNewIndustry && newIndustryPriority === priority)
                          ? '#fff'
                          : '#000',
                      cursor: 'pointer',
                      marginBottom: '0.5rem',
                      padding: '0.25rem 0.5rem',
                    }}
                    closable={!!(selectedIndustry && selectedIndustry.priority === priority)}
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
