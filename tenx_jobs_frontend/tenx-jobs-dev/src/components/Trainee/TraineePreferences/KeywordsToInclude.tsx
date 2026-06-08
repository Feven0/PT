import { useState } from 'react';
import { Button, Col, Input, Row, Tag, message } from 'antd';
import { PlusOutlined, InfoCircleOutlined, CloseOutlined } from '@ant-design/icons';
import { useAppDispatch, useAppSelector } from '../../../redux/hooks/hooks';
import { capitalizeFirstChar, KeywordTags } from '../../../utils/commonUtils';
import { CombinedKeyword, KeywordObject } from '../../../types/preferenceTypes';
import {
  addSkill,
  addCertificate,
  addToolsPreference,
  addKnowledgePreference,
  addAbilitiesPreference,
  removeSkill,
  removeCertificate,
  removeToolsPreference,
  removeKnowledgePreference,
  removeAbilitiesPreference
} from '../../../redux/slices/Preferences/jobKeywordsIncludeSlice';
import { setPreferenceControlTag } from '../../../redux/slices/Preferences/preferenceControlSlice';
import '../../../styles/preference.css';

export default function KeywordsToInclude() {
  const [selectedKeyword, setSelectedKeyword] = useState<CombinedKeyword | null>(null);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [type, setType] = useState<string | null>(null);
  const [addingNewKeyword, setAddingNewKeyword] = useState(false);
  const [newRoleName, setNewRoleName] = useState('');
  const [showMore, setShowMore] = useState(false);

  const { job_keywords_include } = useAppSelector((state) => state.jobKeywordsInclude);
  const dispatch = useAppDispatch();

  const handleTagClick = (keyword: CombinedKeyword) => {
    if (selectedTag === keyword.item) {
      setSelectedTag(null);
      setSelectedKeyword(null);
    } else {
      setSelectedKeyword(keyword);
      setSelectedTag(keyword.item);
    }
  };

  const handleTagClose = (keyword: CombinedKeyword) => {
    dispatch(setPreferenceControlTag(true));
    switch (keyword.category) {
      case 'skills':
        dispatch(removeSkill(keyword.item));
        break;
      case 'certificates':
        dispatch(removeCertificate(keyword.item));
        break;
      case 'tools':
        dispatch(removeToolsPreference(keyword.item));
        break;
      case 'knowledge':
        dispatch(removeKnowledgePreference(keyword.item));
        break;
      case 'abilities':
        dispatch(removeAbilitiesPreference(keyword.item));
        break;
      default:
        break;
    }
    setSelectedKeyword(null);
    setSelectedTag(null); 
  };

  const handleAddNewKeyword = () => {
    if (!type) {
      message.error('Please select a category for the new keyword.');
      return;
    }

    if (newRoleName.trim()) {
      const trimmedRoleName = newRoleName.trim();
      dispatch(setPreferenceControlTag(true));
      switch (type) {
        case 'skills':
          dispatch(addSkill(trimmedRoleName));
          break;
        case 'certificates':
          dispatch(addCertificate(trimmedRoleName));
          break;
        case 'tools':
          dispatch(addToolsPreference(trimmedRoleName));
          break;
        case 'knowledge':
          dispatch(addKnowledgePreference(trimmedRoleName));
          break;
        case 'abilities':
          dispatch(addAbilitiesPreference(trimmedRoleName));
          break;
        default:
          break;
      }
      setNewRoleName('');
      setAddingNewKeyword(false);
    }
  };

  const updateKeywordCategory = (newCategory: keyof KeywordObject) => {
    if (selectedKeyword) {
      dispatch(setPreferenceControlTag(true));
      switch (selectedKeyword.category) {
        case 'skills':
          dispatch(removeSkill(selectedKeyword.item));
          break;
        case 'certificates':
          dispatch(removeCertificate(selectedKeyword.item));
          break;
        case 'tools':
          dispatch(removeToolsPreference(selectedKeyword.item));
          break;
        case 'knowledge':
          dispatch(removeKnowledgePreference(selectedKeyword.item));
          break;
        case 'abilities':
          dispatch(removeAbilitiesPreference(selectedKeyword.item));
          break;
        default:
          break;
      }
      const updatedKeyword = { ...selectedKeyword, category: newCategory };

      switch (newCategory) {
        case 'skills':
          dispatch(addSkill(updatedKeyword.item));
          break;
        case 'certificates':
          dispatch(addCertificate(updatedKeyword.item));
          break;
        case 'tools':
          dispatch(addToolsPreference(updatedKeyword.item));
          break;
        case 'knowledge':
          dispatch(addKnowledgePreference(updatedKeyword.item));
          break;
        case 'abilities':
          dispatch(addAbilitiesPreference(updatedKeyword.item));
          break;
        default:
          break;
      }

      setSelectedKeyword(updatedKeyword);
      setSelectedTag(updatedKeyword.item);
      setType(newCategory);
    }
  };

  const hasOtherCategories = KeywordTags.some(
    (category) => category !== 'skills' && (job_keywords_include[category] || []).length > 0
  );

  return (
    <div>
      <div className="d-flex-between roles-header mb-8">
        <span className="preference__header__title">Keywords to Include</span>
      </div>
      <div className="description-text">
        <InfoCircleOutlined />
        <span style={{ marginLeft: '8px' }}>
          These keywords help you find the job you want more precisely based on skills, certificates, and more.
        </span>
      </div>

      <div className="keyword-section" style={{ padding: "0 1rem" }}>
        {KeywordTags.map((category) => {
          const categoryKeywords = job_keywords_include[category] || [];
          if (!showMore && category !== 'skills') return null; 

          return (
            <div key={category} className="keyword-category">
              {categoryKeywords.length > 0 && <h4>{capitalizeFirstChar(category)}</h4>}
              <div className="included-tags flex" style={{ flexWrap: 'wrap' }}>
                {categoryKeywords.length > 0 && (
                  categoryKeywords.map((item) => (
                    <Tag
                      key={item}
                      color={selectedTag === item ? '#FF4405' : undefined}
                      closable={selectedTag === item}
                      onClick={() => handleTagClick({ category, item })}
                      onClose={() => handleTagClose({ category, item })}
                      style={{
                        backgroundColor: selectedTag === item ? '#FF4405' : undefined,
                        color: selectedTag === item ? '#fff' : undefined,
                      }}
                      className="keyword-tag"
                    >
                      {capitalizeFirstChar(item)}
                    </Tag>
                  ))
                ) }
              </div>
            </div>
          );
        })}
        <div className="add-new-keyword">
          {hasOtherCategories && (
            <div className="show-more-button">
              <Button onClick={() => setShowMore(!showMore)}>
                {showMore ? 'Show Less' : 'More Keywords'}
              </Button>
            </div>
          )}
          <Button
            style={{
              borderColor: '#FF4405',
              background: addingNewKeyword ? '#FF4405' : 'white',
              color: addingNewKeyword ? 'white' : '#000',
              opacity: addingNewKeyword ? 1 : 0.7
            }}
            icon={!addingNewKeyword ? <PlusOutlined /> : <CloseOutlined />}
            onClick={() => {
                setAddingNewKeyword(!addingNewKeyword)
                }
              }
          >
            {addingNewKeyword ? 'Cancel' : 'New'}
          </Button>
        </div>

        {(addingNewKeyword || selectedKeyword) && (
          <Row gutter={16} className="mt-16 keyword__input__wrapper-row">
            <Col span={24}>
              <span>Categories</span>
              <div className="mt-8 industry-tag-div">
                {KeywordTags.map((tag) => (
                  <Tag
                    key={tag}
                    color={type === tag ? '#FF4405' : 'default'}
                    onClick={() => {
                      if (selectedKeyword) {
                        updateKeywordCategory(tag); 
                      } else {
                        setType(tag); 
                      }
                    }}
                    className="keywords__categories">
                    {capitalizeFirstChar(tag)}
                  </Tag>
                ))}
              </div>
            </Col>
            <Col xs={24} lg={12} className="input__wrapper mt-16">
              <Input
                placeholder="Enter keyword name"
                value={newRoleName}
                onChange={(e) => setNewRoleName(e.target.value)}
              />
              <Button className="dark-orange-bg white-color mt-16" onClick={handleAddNewKeyword}>
                Add
              </Button>
            </Col>
          </Row>
        )}
      </div>
    </div>
  );
}
