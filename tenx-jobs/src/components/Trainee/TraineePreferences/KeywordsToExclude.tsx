import { useState } from 'react';
import { Button, Col, Divider, Input, message, Row, Tag } from 'antd';
import { PlusOutlined, InfoCircleOutlined, CloseOutlined } from '@ant-design/icons';
import { useAppDispatch, useAppSelector } from '../../../redux/hooks/hooks';
import { capitalizeFirstChar, KeywordTags } from '../../../utils/commonUtils';
import { CombinedKeyword, KeywordObject } from '../../../types/preferenceTypes';
import { setPreferenceControlTag } from '../../../redux/slices/Preferences/preferenceControlSlice';
import { 
  addAbilitiesPreferenceExclude,
  addCertificateExclude,
  addKnowledgePreferenceExclude,
  addSkillExclude,
  addToolsPreferenceExclude,
  removeAbilitiesPreferenceExclude,
  removeCertificateExclude,
  removeKnowledgePreferenceExclude,
  removeSkillExclude,
  removeToolsPreferenceExclude,
} from "../../../redux/slices/Preferences/jobKeywordsExcludeSlice";
import '../../../styles/preference.css';

export default function KeywordsToExclude() {
  const [selectedKeyword, setSelectedKeyword] = useState<CombinedKeyword | null>(null);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [type, setType] = useState<string | null>(null);
  const [addingNewKeyword, setAddingNewKeyword] = useState(false);
  const [newRoleName, setNewRoleName] = useState('');
  const [showMore, setShowMore] = useState(false);

  const { job_keywords_exclude } = useAppSelector((state) => state.jobKeywordsExclude);
  const dispatch = useAppDispatch();

  const hasOtherCategories = KeywordTags.some(
    (category) => category !== 'skills' && (job_keywords_exclude[category] || []).length > 0
  );

  const handleTagClick = (keyword: CombinedKeyword) => {
    if (selectedTag === keyword.item) {
      setSelectedTag(null);
      setSelectedKeyword(null);
    }else {
      setSelectedKeyword(keyword);
      setSelectedTag(keyword.item);
    }
  };

  const handleTagClose = (keyword: CombinedKeyword) => {
    dispatch(setPreferenceControlTag(true));

    switch (keyword.category) {
      case 'skills':
        dispatch(removeSkillExclude(keyword.item));
        break;
      case 'certificates':
        dispatch(removeCertificateExclude(keyword.item));
        break;
      case 'tools':
        dispatch(removeToolsPreferenceExclude(keyword.item));
        break;
      case 'knowledge':
        dispatch(removeKnowledgePreferenceExclude(keyword.item));
        break;
      case 'abilities':
        dispatch(removeAbilitiesPreferenceExclude(keyword.item));
        break;
      default:
        break;
    }
    setSelectedKeyword(null);
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
          dispatch(addSkillExclude(trimmedRoleName));
          break;
        case 'certificates':
          dispatch(addCertificateExclude(trimmedRoleName));
          break;
        case 'tools':
          dispatch(addToolsPreferenceExclude(trimmedRoleName));
          break;
        case 'knowledge':
          dispatch(addKnowledgePreferenceExclude(trimmedRoleName));
          break;
        case 'abilities':
          dispatch(addAbilitiesPreferenceExclude(trimmedRoleName));
          break;
        default:
          break;
      }
      setNewRoleName('');
      setAddingNewKeyword(false);
    }
  };

  const handleCategoryChange = (newCategory: keyof KeywordObject) => {
    if (selectedKeyword) {
      const { item } = selectedKeyword;

      switch (selectedKeyword.category) {
        case 'skills':
          dispatch(removeSkillExclude(item));
          break;
        case 'certificates':
          dispatch(removeCertificateExclude(item));
          break;
        case 'tools':
          dispatch(removeToolsPreferenceExclude(item));
          break;
        case 'knowledge':
          dispatch(removeKnowledgePreferenceExclude(item));
          break;
        case 'abilities':
          dispatch(removeAbilitiesPreferenceExclude(item));
          break;
        default:
          break;
      }

      switch (newCategory) {
        case 'skills':
          dispatch(addSkillExclude(item));
          break;
        case 'certificates':
          dispatch(addCertificateExclude(item));
          break;
        case 'tools':
          dispatch(addToolsPreferenceExclude(item));
          break;
        case 'knowledge':
          dispatch(addKnowledgePreferenceExclude(item));
          break;
        case 'abilities':
          dispatch(addAbilitiesPreferenceExclude(item));
          break;
        default:
          break;
      }
      setSelectedKeyword({ ...selectedKeyword, category: newCategory });
      setType(newCategory);
      setSelectedTag(item); 
    }
  };

  return (
    <div>
      <Divider />
      <div className="d-flex-between roles-header mb-8">
        <span className="preference__header__title">Keywords to Exclude</span>
      </div>
      <div className="description-text">
        <InfoCircleOutlined />
        <span style={{ marginLeft: '8px' }}>
          These keywords will help avoid job listings with undesired skills, certificates, and more.
        </span>
      </div>

      <div className="keyword-section" style={{ padding: '0 1rem' }}>
        {KeywordTags.map((category) => {
          const categoryKeywords = job_keywords_exclude[category] || [];
          if (!showMore && category !== 'skills') return null;

          return (
            <div key={category} className="keyword-category">
              {categoryKeywords.length > 0 && <h4>{capitalizeFirstChar(category)}</h4>}
              <div className="excluded-tags flex" style={{ flexWrap: 'wrap' }}>
                {categoryKeywords.length > 0 ? (
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
                ) : null}
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
              opacity: addingNewKeyword ? 1 : 0.7,
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
                        handleCategoryChange(tag); 
                      } else {
                        setType(tag); 
                      }
                    }}
                    className="keywords__categories"
                  >
                    {capitalizeFirstChar(tag)}
                  </Tag>
                ))}
              </div>
            </Col>
            <Col xs={24} lg={12} className="mt-16 input__wrapper">
              <Input
                placeholder="Enter keyword name"
                value={newRoleName}
                onChange={(e) => setNewRoleName(e.target.value)}
                style={{ marginBottom: '16px' }}
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
