
import { Row, Col, Tag } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { T_TraineeCompetenciesAttributes } from "../../../types/profileResponse";
import { useAppSelector } from "../../../redux/hooks/hooks";

type SkillTagsProps = {
  handleSkillEdit: (skill: T_TraineeCompetenciesAttributes) => void;
}

export default function SkillsTags ({ handleSkillEdit }: SkillTagsProps)  {
  const { competencies } = useAppSelector((state) => state.traineeProfileResponse.user_profile)
  const {selectedCompetency: selectedSkill} = useAppSelector((state) => state.competencyApproval);
  const {selectedSkillsUUID} = useAppSelector((state) => state.selectedSkillsUUID)
  const competency = competencies?.attributes?.filter((skill) => skill.uuid === selectedSkillsUUID)[0]?.skills || selectedSkill?.skills
  

  return (
    <Row gutter={8} className="mt-32 skill-container-rows">
      <Col xs={24} lg={24} className="selected-skill-tags">
        <div
          className="expanded-details-summary selected-skills-expanded d-flex-between"
          style={{
            padding: "0.5rem",
          }}
        >
          <span>Skills</span>
          {selectedSkill && (
            <EditOutlined
              style={{ opacity: 0.5 }}
              onClick={() => handleSkillEdit(selectedSkill)}
            />
          )}
        </div>
        {competency.map((individualSkill, skillIndex) => (
          <Tag
            className="mt-8"
            key={skillIndex}
            style={{
              marginBottom: '8px',
              marginLeft: '12px',
              marginRight: '12px',
              padding: "0.25rem 0.5rem",
            }}
          >
            {individualSkill}
          </Tag>
        ))}
      </Col>
    </Row>
  );
}