import React, { useState } from 'react';
import { Card, Col, Row, Table, Tag, Tooltip } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';
import EmptyJobHandler from "../commonComponents/EmptyJobHandler";
import { T_MatchDetails, TMatchAttributesExp } from "../../types/expandReactionTypes";
import '../../styles/slidingCard.css';

interface MatchDetailSectionProps {
  transformedMatchDetail: TMatchAttributesExp;
  columns: any[];
  isExpansion?: boolean;
}

export default function TraineeMatchDetails({ transformedMatchDetail, columns, isExpansion }: MatchDetailSectionProps) {
  const [expandedRowId, setExpandedRowId] = useState<React.Key | null>(null);
  if (!transformedMatchDetail) {
    return <EmptyJobHandler title="No Match Found" description="No match found for the selected job." />;
  }

  return (
    <>
      <Col span={24} className="match-detail-table-container">
        <Card
          title={
            <div className="d-flex-between">
              <span>{transformedMatchDetail?.title}</span>
              <span className="over-all-match-score">Overall Match Score - <span style={{
                color: Number(transformedMatchDetail?.overall_match_score) < 50 ? '#FF4405' : '#52C41A',
                fontWeight: 'bold'
              }}>{transformedMatchDetail?.overall_match_score}</span></span>
            </div>
          }
          className="full-width p-16"
        >
          <Table
            dataSource={transformedMatchDetail.match_detail}
            columns={columns}
            expandable={{
              expandedRowRender: (record: T_MatchDetails) => (
                <Row gutter={16} className="trainee-match-details-expanded-row">
                  <Col xs={24}>
                    <Card className="p-16">
                      <Row gutter={16}>
                        {record.matched_skills.length > 0 && (
                          <Col span={12} style={{padding:"0 1rem"}}>
                            <Tooltip className="mb-16" title="Skills listed in the job description that are available in your profile">
                              <div className="flex-center gap-8" style={{ marginBottom: "1rem" }}>
                                <QuestionCircleOutlined />
                                <span className="font-16 font-600">User SKAO</span>
                              </div>
                            </Tooltip>
                            <div className="flex gap-8" style={{ flexWrap: 'wrap' }}>
                              <ul style={{ listStyleType: 'disc', padding: 0 }}>
                              <span className="font-16">Skill Name</span>
                              {record.matched_skills.map((skill, skillIndex) => (
                                skill.skill_name && (
                                  <li key={skillIndex} style={{ wordWrap: 'break-word', marginBottom: '8px', marginTop:"8px" }}>
                                    {skill.skill_name.charAt(0).toUpperCase() + skill.skill_name.slice(1)}
                                  </li>
                                )
                              ))}
                            </ul>
                          </div>
                            {record.missing_skills.length > 0 && (
                              <div>
                                <Tooltip className="mb-16" title="Skills listed in the job description that are not available in your profile">
                                  <div className="flex-center gap-8 mt-16" style={{ marginBottom: "1rem" }}>
                                    <QuestionCircleOutlined />
                                    <span className="font-16">Job SKAO</span>
                                  </div>
                                </Tooltip>
                                <div className="flex gap-8" style={{ flexWrap: 'wrap' }}>
                                  {record.missing_skills.map((skill, skillIndex) => (
                                    skill && <Tag className="match-detail-tags-skills" key={skillIndex}>
                                      {skill}
                                    </Tag>
                                  ))}
                                </div>
                              </div>
                            )}
                          </Col>
                        )}
                        <Col span={12}>
                          <p>Job SFIA level: <span className="expansion-detail-text">{record.job_sfia_level}</span></p>
                          <p>User SFIA level: <span className="expansion-detail-text">{record.user_sfia_level}</span></p>
                          <p>Match Score: <span className="expansion-detail-text">{record.match_score}</span></p>
                          <p>Match Degree: <span className="expansion-detail-text">{record.match_degree}</span></p>
                          <Tooltip title="The UJC Similarity Score is a measure of how similar the job required competency is to the best matched user's competence.">
                            <div className="flex mt-8 gap-8">
                              <QuestionCircleOutlined />
                              <p>UJC Similarity Score - <span className="expansion-detail-text">{record.ujc_similarity_score}</span></p>
                            </div>
                          </Tooltip>
                        </Col>
                      </Row>
                    </Card>
                  </Col>
                </Row>
              ),
              expandedRowKeys: expandedRowId ? [expandedRowId] : [],
              onExpand: (expanded, record) => {
                setExpandedRowId(expanded ? record.key : null);
              },
            }}
            scroll={{ x: 768 }}
            pagination={false}
          />
        </Card>
      </Col>
      <Col xs={24} lg={isExpansion ? 24 : 14} className="mt-16 match-detail-cards-container">
        <Card title={<span>Rationale</span>} style={{ width: '100%' }}>
          <p style={{ padding: '0.5rem 1.5rem' }}>{transformedMatchDetail.rationale}</p>
        </Card>
      </Col>
    </>
  );
}
