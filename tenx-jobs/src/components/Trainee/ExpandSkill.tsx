import { Col, Card, Row, List, Divider } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { T_TraineeCompetenciesAttributes, T_TraineeCompetencyEvidence } from "../../types/profileResponse";
import EvidenceTable from "./Profile/Skills/EvidenceTable";
import SkillsTags from "./Profile/Skills/SkillsTags";
import { Key } from "react";
import { useAppSelector } from "../../redux/hooks/hooks";

type ExpandedSkillCardProps ={
  handleSkillEdit: (skill: T_TraineeCompetenciesAttributes) => void;
  setIsSkillExpanded: (expanded: boolean) => void;
  expandedRowId: Key | null;
  setExpandedRowId: (id: string | null) => void;
  setIsEvidenceUploadExpanded: (expanded: boolean) => void;
  addKeyToEvidence: (evidence: T_TraineeCompetencyEvidence[]) => T_TraineeCompetencyEvidence[]; 
  setSelectSkillUUID: (uuid: string) => void;
  getSfiaLevelStyle: (level: string) => React.CSSProperties;
  columns: any[]; 
}

export default function  ExpandSkill({
  handleSkillEdit,
  setIsSkillExpanded,
  expandedRowId,
  setExpandedRowId,
  setIsEvidenceUploadExpanded,
  addKeyToEvidence,
  getSfiaLevelStyle,
  columns
}: ExpandedSkillCardProps)  {
  const {selectedCompetency: selectedSkill} = useAppSelector((state) => state.competencyApproval);
  return (
    <Col span={24} className="skills-expanded-container expanded-detail-skill-wrapper">
      <Card
        className="full-width expanded-skills-card"
        title={<div className="d-flex-between" style={getSfiaLevelStyle(selectedSkill?.sfia_level ?? '0')}>
          <div className="flex-center gap-8">
            <div className="see-skills-card"><ArrowLeftOutlined onClick={() => setIsSkillExpanded(false)} />
            </div>
            {selectedSkill?.display}
          </div>
          <div className="flex-center gap-8">
            <span className="skills-change-request">Sfia Level</span>
            <span className="skills-sfia-level">{selectedSkill?.sfia_level}</span>
          </div>
        </div>
        }
      >
        <div className="expanded-details" style={{ margin: "1rem" }}>
          <div className="expanded-details-summary">
            <span style={{ padding: "0 0.5rem" }}>Competency Description</span>
          </div>
          <p style={{ padding: "0.25rem 0.75rem", marginTop: "0.5rem" }}>{selectedSkill?.description}</p>
          <div className="expanded-details-summary mt-16">
            <span style={{ padding: "0 0.5rem" }}>Rationale</span>
          </div>
          <p style={{ padding: "0.25rem 0.75rem", marginTop: "0.5rem" }}>{selectedSkill?.rationale}</p>
        </div>
        <SkillsTags  handleSkillEdit={handleSkillEdit} />
        {selectedSkill?.knowledge && selectedSkill?.knowledge.length > 0 && (
          <Row gutter={8} className="mt-16 skill-container-rows">
            <Col xs={24} lg={24} className="selected-skill-tags">
              <div className="expanded-details-summary d-flex-between" style={{
                padding: "0.5rem"
              }}>
                <span>Knowledge</span>
              </div>
              {selectedSkill?.knowledge.map((knowledge, knowledgeIndex) => (
                <List key={knowledgeIndex} size="small">
                  <List.Item>{knowledge}</List.Item>
                </List>
              ))}
            </Col>
          </Row>
        )}
        <Divider />
        <EvidenceTable
          columns={columns}
          expandedRowId={expandedRowId ? expandedRowId.toString() : null}
          setExpandedRowId={setExpandedRowId}
          setIsEvidenceUploadExpanded={setIsEvidenceUploadExpanded}
          addKeyToEvidence={addKeyToEvidence}
        />
      </Card>
    </Col>
  );
}
