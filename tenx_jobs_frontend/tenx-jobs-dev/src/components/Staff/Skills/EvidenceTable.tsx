
import { Row, Col, Table, Divider } from 'antd';
import { ToTopOutlined } from '@ant-design/icons';
import { T_TraineeCompetencyEvidence } from "../../../types/profileResponse";
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { setEvidences } from "../../../redux/slices/evidenceMssagesSlice";
import { capitalizeFirstChar } from "../../../utils/commonUtils";
import EvidenceMessage from "./EvidenceMessage";


type EvidenceTableProps = {
  columns: any;
  expandedRowId: string | null;
  setExpandedRowId: (id: string | null) => void;
  setIsEvidenceUploadExpanded: (expanded: boolean) => void;
  addKeyToEvidence: (evidence: T_TraineeCompetencyEvidence[]) => T_TraineeCompetencyEvidence[];
}

export default function EvidenceTable({ 
  columns, 
  expandedRowId, 
  setExpandedRowId, 
  setIsEvidenceUploadExpanded,
  addKeyToEvidence,
}: EvidenceTableProps) {

  const { competencies: skills } = useAppSelector((state) => state.traineeProfileResponse.user_profile)
  const {selectedSkillsUUID} = useAppSelector((state) => state.selectedSkillsUUID)
  const selectedSkills = skills.attributes.filter((skill) => skill.uuid === selectedSkillsUUID)

  const dispatch = useAppDispatch();
  const handleUploadEvidence = () => setIsEvidenceUploadExpanded(true)

  const handleExpand = (expanded: boolean, record: T_TraineeCompetencyEvidence) => {
    if (expanded) {
      setExpandedRowId(record?.key ?? null);
      dispatch(setEvidences(record)); 
    } else {
      setExpandedRowId(null);
    }
  };

  return (
    <Row gutter={8} className="skill-container-rows">
      <Col span={24}>
        <div className="d-flex-between" style={{ margin: '1rem' }}>
          <span>Evidence</span>
          <div
            className="flex-center gap-8 cursor-pointer"
            onClick={handleUploadEvidence}
          >
            <ToTopOutlined className="dark-orange-color font-16" />
            <span>Upload Evidence</span>
          </div>
        </div>
        <Table
          className="mt-16"
          dataSource={addKeyToEvidence(selectedSkills[0]?.evidence ?? [])}
          columns={columns}
          expandable={{
            expandedRowRender: (record: T_TraineeCompetencyEvidence) => (
              <Row gutter={16} className="skill-container-rows">
                {record.sfia_dimensions_requested.length > 0 && (
                  <Col xs={24} lg={12}>
                    <p className="mb-8">
                      {record.sfia_dimensions_requested.length > 0 && <strong>SFIA Dimension Requested</strong>}
                    </p>
                    <div className="flex gap-8" style={{ flexWrap: 'wrap', flexDirection: "column" }}>
                      {record.sfia_dimensions_requested.map((dimension: { name: string; level: number }, index: number) => (
                        <span key={index}>
                          {capitalizeFirstChar(dimension.name)} - {dimension.level}
                        </span>
                      ))}
                    </div>
                  </Col>
                )}
                {record.sfia_dimensions_approved.length > 0 && (
                  <Col xs={24} lg={12}>
                    <p className="mb-8">
                      {record.sfia_dimensions_approved.length > 0 && <strong>SFIA Dimension Approved</strong>}
                    </p>
                    <div className="flex gap-8" style={{ flexWrap: 'wrap', flexDirection: "column" }}>
                      {record.sfia_dimensions_approved.map((dimension: { name: string; level: number }, index: number) => (
                        <span key={index}>
                          {capitalizeFirstChar(dimension.name)} - {dimension.level}
                        </span>
                      ))}
                    </div>
                  </Col>
                )}
                <Divider />
                {record.remark && (
                  <Col xs={24}>
                    <p className="mb-8">
                      <strong>Remark</strong>
                    </p>
                    <div className="flex gap-8" style={{ flexWrap: 'wrap' }}>
                      <p>{record.remark}</p>
                    </div>
                  </Col>

                )}
                <Divider />
                <EvidenceMessage />
              </Row>
            ),
            expandedRowKeys: expandedRowId ? [expandedRowId] : [],
            onExpand: handleExpand
          }}
          scroll={{ x: 768 }}
          pagination={false}
        />
      </Col>
    </Row>
  );
}