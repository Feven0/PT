import { useParams } from "react-router-dom";
import { Row, Col, Tag, Card, Divider, Pagination, Drawer, Button, Modal, Tooltip, Form, message, Popconfirm, Select, Input, Table } from 'antd';
import { useEffect, useRef, useState } from "react"
import { EyeOutlined, SearchOutlined, UnorderedListOutlined, AppstoreFilled } from '@ant-design/icons';
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';
import { useMutation } from "@apollo/client";

//Components
import TagComponent from "../../commonComponents/Tag";
import EvidenceTable from "./EvidenceTable";
import ChangeEvidenceStatus from "./ChangeEvidenceStatus";
import EmptyJobHandler from "../../commonComponents/EmptyJobHandler";

import useTagType from "../../../hooks/useTags";
import { getSfiaLevelStyle } from "../../../utils/getSfiaLevel";
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { setRequestedData, setSfiaLevel, setSkillOfSelectedEvidence } from "../../../redux/slices/evidenceApprovalSlice";
import { setSelectedCompetency } from "../../../redux/slices/staffCompetencySlice";
import { T_TraineeCompetenciesAttributes, T_TraineeCompetencyEvidence } from "../../../types/profileResponse";
import { setUserProfileSkillTitle } from "../../../redux/slices/profileSkillSlice";
import { resetSkill, setSkill } from "../../../redux/slices/experienceSlice";
import useFetchTraineeProfileForStaff from "../../../hooks/useFetchTraineeProfileForStaff";
import { resetTraineeSifaLevel, setCompetencyDescription, setCompetencyRationale, setTraineeSifaLevel } from "../../../redux/slices/updatingTraineeSifaLevelSlice";
import { setSelectedGridView } from "../../../redux/slices/gridViewSlice";
import { CREATE_NOTIFICATION } from "../../../graphql/mutations/createNotification";
import useAxiosRequest from "../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../utils/getRunStage";
import '../../../styles/staff.css'
import '../../../styles/slidingCard.css'

const run_stage = getRunStage();

const { TextArea } = Input;

export default function DraftCompetencies() {
  const { allUserID, trainee_id } = useParams()
  const { user_profile_id } = useParams()
  const {batch, allUserId} = useAppSelector(state => state.user)
  const ref = useRef<HTMLDivElement>(null);

  const [expandedRowId, setExpandedRowId] = useState<React.Key | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [isDrawerVisible, setIsDrawerVisible] = useState<boolean>(false);
  const [width, setWidth] = useState(800);
  const [selectedSkillUUID, setSelectedSkillUUID] = useState<string>("");
  const [isResizing, setIsResizing] = useState(false);
  const [isEvidenceEditOn, setIsEvidenceEditOn] = useState(false)
  const [page, setPage] = useState(1);
  const [paginationSize, setPaginationSize] = useState(10);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [filteredData, setFilteredData] = useState<T_TraineeCompetenciesAttributes[]>([]);
  const [gridViewItems, setGridViewItems] = useState<T_TraineeCompetenciesAttributes[]>([]);

  const gridView = useAppSelector((state) => state.gridView.selectedTab)
  const { competencies: skills } = useAppSelector((state) => state.traineeProfileResponse.user_profile)
  const { selectedCompetency } = useAppSelector((state) => state.competencyApproval)
  const { user_role } = useAppSelector(state => state.leapProfileId)
  const { requestedData } = useAppSelector((state) => state.evidenceApproval);
  const { competencies } = useAppSelector((state) => state.traineeProfileResponse.user_profile)

  const { skill } = useAppSelector((state) => state.experience)
  const { sfia_level, competency_description, competency_rationale } = useAppSelector((state) => state.updatingTraineeSifaLevel)
  const { getType } = useTagType();
  const dispatch = useAppDispatch()
  const [form] = Form.useForm();

  const fetchUserProfile = useFetchTraineeProfileForStaff({ allUserID, user_profile_id });
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = gridViewItems.slice(indexOfFirstItem, indexOfLastItem);
  
  const handlePageChange = (page: number) => setCurrentPage(page);
  const handlePageSizeChange = (size: number) => setItemsPerPage(size);

  const closeDrawer = () => {
    setIsDrawerVisible(false);
    setSelectedSkillUUID('');
  }

  const closeModal = () => {
    dispatch(setRequestedData({
      ...requestedData,
      sfia_level_requested: "",
      verified_by: "Staff",
      requested_by: "Trainee",
      status: "",
    }))
    setIsEvidenceEditOn(false)
  }

  useEffect(() => {
    const onMouseMoveHandler = (e: MouseEvent) => {
      if (isResizing) {
        const offsetRight =
          document.body.offsetWidth - (e.clientX - document.body.offsetLeft);
        const minWidth = 800;
        if (offsetRight > minWidth) {
          setWidth(offsetRight);
        }
      }
    };
    document.addEventListener("mousemove", onMouseMoveHandler);
    document.addEventListener("mouseup", onMouseUp);

    return () => {
      document.removeEventListener("mousemove", onMouseMoveHandler);
      document.removeEventListener("mouseup", onMouseUp);
    };
  }, [isResizing]);

  useEffect(() => {
    setFilteredData(extractData().draftStatus);
    const filteredSkills = skills.attributes.filter(skill => skill.status === 'draft');
    setGridViewItems(filteredSkills);
  }, []);

  const handleMaximize = () => {
    const newWidth = width === 2000 ? 800 : 2000;
    setWidth(newWidth);
  };

  const { makeRequest, loading } = useAxiosRequest();

  const onMouseDown = () => setIsResizing(true);
  const onMouseUp = () => setIsResizing(false);

  const handleCompetencyApproval = (record: T_TraineeCompetencyEvidence) => {
    dispatch(setRequestedData(record));
    const sfiaLevel = selectedCompetency?.sfia_level ?? null;
    const skills = selectedCompetency?.skills ?? [];
    dispatch(setSfiaLevel(sfiaLevel))
    dispatch(setSkillOfSelectedEvidence(skills))
    setIsEvidenceEditOn(true)
  }

  const extractData = () => {
    const draftStatus = skills.attributes
      .filter((attr: T_TraineeCompetenciesAttributes) => attr.name !== "" && attr.status === "draft")
      .map((attr) => {
        const requestsCount = attr.evidence?.filter(ev => ev.status !== "approved" && ev.status !== "verified").length || 0;
  
        return {
          key: attr.uuid,
          name: attr.name,
          uuid: attr.uuid,
          display: attr.display,
          sfia_level: attr.sfia_level,
          status: attr.status,
          skills: attr.skills,
          description: attr.description,
          rationale: attr.rationale,
          abilities: attr.abilities,
          attitude: attr.attitude,
          knowledge: attr.knowledge,
          others: attr.others,
          sfia_estimation_method: attr.sfia_estimation_method,
          experience_level: attr.experience_level,
          evidence: attr.evidence,
          history: attr.history,
          credibility: attr.credibility,
          verified_by: attr.verified_by,
          requested_by: attr.requested_by,
          requestsCount,
        };
      })
      .sort((a, b) => b.requestsCount - a.requestsCount);
  
    
    return { draftStatus };
  };

  const showEditSfiaLevelDrawer = (skill: T_TraineeCompetenciesAttributes) => {
    dispatch(setSelectedCompetency(skill))
    setSelectedSkillUUID(skill.uuid);
    if (selectedCompetency?.sfia_level) {
      dispatch(setTraineeSifaLevel(selectedCompetency.sfia_level));
    }
    if (selectedCompetency?.description) {
      dispatch(setCompetencyDescription(selectedCompetency.description));
    }
    if (selectedCompetency?.rationale) {
      dispatch(setCompetencyRationale(selectedCompetency.rationale));
    }
    dispatch(setUserProfileSkillTitle(skill.display));
    setIsDrawerVisible(true);

    form.setFieldsValue({
      sfiaLevel: skill?.sfia_level,
      display: skill.display,
      individualSkills: skill.skills,
      competency_description: skill?.description,
      competency_rationale: skill?.rationale
    });
  }
  
  const competency_columns = [
    {
      title: '#',
      key: 'index',
      width: "4%",
      render: (_text: string, _record: T_TraineeCompetenciesAttributes, index: number) => (page - 1) * paginationSize + index + 1,
    },
    {
      title: "Competency",
      dataIndex: "display",
      key: "display",
    },
    {
      title: "SFIA Level",
      dataIndex: "sfia_level",
      key: "sfia_level",
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (_text: string, record: T_TraineeCompetenciesAttributes) => {
        return (
          <TagComponent ref={ref} text={record.status} type={getType(record.status)} />
        );
      },
    },
    {
      title: "Requests",
      key: "requests",
      render: (_text: string, record: T_TraineeCompetenciesAttributes) => {
        const requestsCount = record.evidence?.filter(ev => ev.status !== "approved" && ev.status !== "verified").length || 0;
        return <span>{requestsCount}</span>;
      },
    },
    {
      title: "Preview",
      key: "preview",
      render: (_text: string, record: T_TraineeCompetenciesAttributes) => (
        <EyeOutlined
          style={{ cursor: "pointer", color: "#FF4405" }}
          onClick={() => showEditSfiaLevelDrawer(record)}
        />
      ),
    },
  ];

  const columns = [
    {
      title: "Sfia level requested",
      dataIndex: "sfia_level_requested",
      key: "sfia_level_requested",
      render: (_text: string, record: T_TraineeCompetencyEvidence) => {
        return (
          <span>{record.sfia_level_requested ? record.sfia_level_requested : "--"}</span>
        );
      }
    },
    {
      title: "Sfia level approved",
      dataIndex: "sfia_level_approved",
      key: "sfia_level_approved",
      render: (_text: string, record: T_TraineeCompetencyEvidence) => {
        return (
          record?.sfia_level_approved ?
            <span>{record.sfia_level_approved}</span>
            : <span>--</span>
        )
      }
    },
    {
      title: "Source",
      dataIndex: "source",
      key: "source",
      render: (_text: string, record: T_TraineeCompetencyEvidence) => {
        const { link, name } = record.source || {};
        return (
          <div>
            {link && link.trim() !== "" ? (
              <a href={link} target="_blank" rel="noreferrer">
                {name}
              </a>
            ) : (
              <span>{name}</span>
            )}
          </div>
        );
      },
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (_text: string, record: T_TraineeCompetencyEvidence) => {
        return (
          <TagComponent ref={ref} text={record.status} type={getType(record.status)} />
        )
      }
    },
    {
      title: "Last Message",
      dataIndex: "message",
      key: "message",
      render: (_text: string, record: T_TraineeCompetencyEvidence) => {
        return (
          <Tooltip title={record.message && record?.message?.length > 0 ? record.message[record.message.length - 1].content : "--"}>
            <span>{record.message && record?.message?.length > 0 ? record.message[record.message.length - 1].content.substring(0, 10) : "--"}</span>
          </Tooltip>
        )
      }
    },
    {
      title: "Change Request",
      key: "approve",
      render: (_text: string, record: T_TraineeCompetencyEvidence) => {
        return (
          (record.status !== "approved" && record.status !== "verified") && (
            <Button
              type="text"
              className="staff-competency-approval-button"
              onClick={() => handleCompetencyApproval(record)}
            >
              Change
            </Button>
          )
        );
      }
    }
  ]

  const addKeyToEvidence = (evidence: T_TraineeCompetencyEvidence[]): T_TraineeCompetencyEvidence[] => {
    return evidence.map((ev, index) => ({
      ...ev,
      key: `${index}`
    }));
  };

  const handleSkillsChange = (selectedSkills: string[]) => {
    dispatch(
      setSkill({
        ...skill,
        individualSkills: selectedSkills,
      })
    );
  };

  const onFinish = () => {
  const competency = competencies?.attributes?.filter((competency) => competency.uuid === selectedSkillUUID)[0]
    const selectedSkills = skills.attributes.find(skill => skill.uuid === selectedSkillUUID);
    const updatedEvidence = competency.evidence.map((evidence, index) => {
      if (index.toString() === requestedData.key) {
        // const updatedData = { ...requestedData };
        const updatedData = { 
          ...requestedData, 
          status: "approved",         
          verified_by: "Staff",       
          requested_by: "Trainee"
        };
        delete updatedData.key;
        return updatedData;
      }
      return evidence;
    });

    const data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserID,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "competencies",
          uuid: selectedSkillUUID,
          data: {
            abilities: selectedSkills?.abilities,
            attitude: selectedSkills?.attitude,
            description: competency_description,
            display: selectedSkills?.display,
            evidence: updatedEvidence,
            knowledge: selectedSkills?.knowledge,
            name: selectedSkills?.name,
            others: selectedSkills?.others,
            rationale: competency_rationale,
            sfia_level: sfia_level,
            sfia_estimation_method: selectedSkills?.sfia_estimation_method,
            experience_level: selectedSkills?.experience_level,
            skills: skill?.individualSkills
          }
        }
      ],
      status: "approved",
    }

    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Approved competency ${selectedSkills?.name}`,
      notificationMessageTrainee: `Approved competency ${selectedSkills?.name}`,
      where: "Competency Approval",
      traineeLink: `/trainee/trainee-profile`,
      staffLink: `/staff/trainee_details/${allUserID}/${trainee_id}/${user_profile_id}`,
    }

    form.validateFields().then(async () => {
      await makeRequest({
        url: '/sjob/put-user-profile',
        method: 'POST',
        data,
        onSuccess: () => {
          createNotification({
            variables: {
              sender: allUserId,
              group: 1,
              detail: details,
              origin: "leap",
              batch: Number(batch),
            },
            onCompleted(data) {
              if (data?.createNotification?.data.id) {
                message.success("Notification created successfully");
              } else {
                console.error("Notification creation failed");
              }
            }
          });
          message.success("Competency approved successfully");
          dispatch(resetSkill());
          dispatch(resetTraineeSifaLevel());
          setIsEvidenceEditOn(false);
          fetchUserProfile();
          closeDrawer();
          form.resetFields();
        },
        onError: () => {
        }
      });
    })
    .catch((error) => {
      message.error("Error approving competency", error);
    });
  };

  const handleDecline = () => {
    const selectedSkills = skills.attributes.find(skill => skill.uuid === selectedSkillUUID);
    const updatedEvidence = selectedSkills?.evidence?.map(evidence => ({
      ...evidence,
      status: "rejected",         
      verified_by: "Staff",       
      requested_by: "Trainee"
  }));

    const data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserID,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "competencies",
          uuid: selectedSkillUUID,
          data: {
            abilities: selectedSkills?.abilities,
            attitude: selectedSkills?.attitude,
            description: selectedSkills?.description,
            display: selectedSkills?.display,
            evidence: updatedEvidence,
            knowledge: selectedSkills?.knowledge,
            name: selectedSkills?.name,
            others: selectedSkills?.others,
            rationale: selectedSkills?.rationale,
            sfia_level: selectedSkills?.sfia_level,
            sfia_estimation_method: selectedSkills?.sfia_estimation_method,
            experience_level: selectedSkills?.experience_level,
            skills: skill?.individualSkills,
          }
        }
      ],
      status: "rejected", 
    }

    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Declined competency ${selectedSkills?.name}`,
      notificationMessageTrainee: `Declined competency ${selectedSkills?.name}`,
      where: "Competency Approval",
      traineeLink: `/trainee/trainee-profile`,
      staffLink: `/staff/trainee_details/${allUserID}/${trainee_id}/${user_profile_id}`,
    }

    form.validateFields().then(async () => {
      await makeRequest({
        url: '/sjob/put-user-profile',
        method: 'POST',
        data,
        onSuccess: () => {
          createNotification({
            variables: {
              sender: allUserId,
              group: 1,
              detail: details,
              origin: "leap",
              batch: Number(batch),
            },
            onCompleted(data) {
              if (data?.createNotification?.data.id) {
                message.success("Notification created successfully");
              } else {
                message.error("Notification creation failed");
              }
            }
          });
          message.success("Competency declined successfully");
          setIsEvidenceEditOn(false);
          dispatch(resetSkill());
          dispatch(resetTraineeSifaLevel());
          fetchUserProfile();
          closeDrawer();
          form.resetFields();
        },
        onError: (error) => {
          message.error("Error declining competency", error);
        }
      });
    })
    .catch((error) => {
      message.error("Error with declining competency", error);
    });
  }

  const {draftStatus } = extractData();
  const onSearch = (value: string) => {
    const fil = draftStatus?.filter((item) => {
      const lowercasedValue = value.toLowerCase();
      return (
        item.name.toLowerCase().includes(lowercasedValue) ||
        item.sfia_level.toString().toLowerCase().includes(lowercasedValue) ||
        item.status.toLowerCase().includes(lowercasedValue)
      );
    });
  
    setFilteredData(fil);
  };


const onGridViewSearch = (value: string) => {
  if(value.trim() !== "") {
    const cur = currentItems.filter((item) => {
      const lowercasedValue = value.toLowerCase();
      return (
        item.name.toLowerCase().includes(lowercasedValue) ||
        item.sfia_level.toString().toLowerCase().includes(lowercasedValue) ||
        item.status.toLowerCase().includes(lowercasedValue)
      );
      
    });    
    return setGridViewItems(cur);
  }
  const filteredSkills = skills.attributes.filter(skill => skill.status === 'draft');
  setGridViewItems(filteredSkills);
};

  return (
    (skills && skills.attributes.length > 0) ?
      <>
         {gridView === "list" ? (
         <Card title={
              <Row gutter={16} className="flex-between"
              style={{
                background: "#fff",
                borderRadius: "8px 8px 0 0",
                padding: "0.5rem",
              }}>
              <Col xs={24} sm={12} className="flex-center gap-8">
              <span>{draftStatus?.length} Competencies</span>
              <span className="flex-center gap-8"></span>
              </Col>
              <Col xs={24} sm={12} className="search__input-column">
              <div className="flex-center gap-16">
                <Input placeholder="Search by competency, SFIA level or status" onChange={(e)=> onSearch(e.target.value)} 
                    suffix={<SearchOutlined />}
                  />
                <div className="flex-center gap-8">
                  <Button
                      style={{ border: "none", color: gridView === "list" ? "#FF4405" : "inherit" }}
                      icon={<UnorderedListOutlined />}
                      onClick={() => dispatch(setSelectedGridView("list"))}
                    />
                    <Button
                      style={{ border: "none", color: (gridView as 'list' | 'grid') === "grid" ? "#FF4405" : "inherit" }}
                      icon={<AppstoreFilled />}
                      onClick={() => dispatch(setSelectedGridView("grid"))}
                    />
                </div>
              </div>
              </Col>
            </Row>
            }
            className="competency__wrapper-card"
            >
             <Table
              columns={competency_columns}
              dataSource={filteredData.length ? filteredData : draftStatus}
              scroll={{ x: 768 }}
              pagination={{
                onChange(current, pageSize) {
                  setPage(current);
                  setPaginationSize(pageSize)
                },
                defaultPageSize: 10,
                hideOnSinglePage: true,
                showSizeChanger: true
              }}
            className="skills-table"
          />
         </Card>
        ) :
          <Row gutter={[16, 16]} className="gridView__wrapper">
            <Card title={
              <Row gutter={16} className="flex-between"
              style={{
                background: "#fff",
                borderRadius: "8px 8px 0 0",
                padding: "0.5rem",
                width: "100%"
              }}
              >
              <Col xs={24} sm={14} className="flex-center gap-8">
              <span>{draftStatus?.length} Competencies</span>
              <span className="flex-center gap-8"></span>
              </Col>
              <Col xs={24} sm={10} className="search__input-column">
              <div className="flex-center gap-16">
                <Input placeholder="Search by competency, SFIA level or status" onChange={(e)=> onGridViewSearch(e.target.value)} 
                  suffix={<SearchOutlined />}
                 />
                 <div className="flex-center gap-8">
                  <Button
                      style={{ border: "none", color: (gridView as 'list' | 'grid') === "list" ? "#FF4405" : "inherit" }}
                      icon={<UnorderedListOutlined />}
                      onClick={() => dispatch(setSelectedGridView("list"))}
                    />
                    <Button
                      style={{ border: "none", color: (gridView as 'list' | 'grid') === "grid" ? "#FF4405" : "inherit" }}
                      icon={<AppstoreFilled />}
                      onClick={() => dispatch(setSelectedGridView("grid"))}
                    />
                </div>
                </div>
              </Col>
            </Row>
            }
            className="full-width skills__wrapper"
            >
              {(currentItems).map((skill, index) => (
                skill.display && (
                  <Col
                    xs={24}
                    md={12}
                    key={index}
                    className="skill-card-wrapper skills__card-column">
                    <Card
                      title={<div
                        className="d-flex-between"
                        style={getSfiaLevelStyle(skill.sfia_level)}>
                        <p>{skill.display}</p>
                        <div className="flex-center gap-8">
                          <EyeOutlined onClick={() => showEditSfiaLevelDrawer(skill)} />
                        </div>
                      </div>}
                      actions={[
                        <div
                          className="d-flex-between"
                          style={{
                            padding: "0 1rem",
                            cursor: "default",
                            color: "#222",
                            opacity: 0.5
                          }}
                        >
                          <div className="flex-center gap-8" />
                          <div className="flex-center gap-8">
                            Sfia level <span style={{ fontSize: "24px" }}>{skill.sfia_level}</span>
                          </div>
                        </div>
                      ]}
                      className="skill-body-container"
                      style={{marginBottom: "0.75rem"}}
                    >
                      {skill.skills.slice(0, 4).map((individualSkill, skillIndex) => (
                        <Tag
                          className="mt-8"
                          key={skillIndex}
                          style={{
                            marginBottom: '8px',
                            padding: "0.25rem 0.5rem",
                            height: "max-content",
                          }}
                        >
                          {individualSkill}
                        </Tag>
                      ))}
                      {skill.skills.length > 4 && (
                        <span
                          className="mt-8"
                          style={{
                            marginBottom: '8px',
                          }}
                        >
                          ...
                        </span>
                      )}
                    </Card>
                  </Col>
                )
              ))}

              {gridViewItems.length > 0 && (
                <Col xs={24} className="flex-end">
                  <Pagination
                    current={currentPage}
                    total={gridViewItems.length}
                    pageSize={itemsPerPage}
                    onChange={handlePageChange}
                    onShowSizeChange={(_, size) => handlePageSizeChange(size)}
                    showSizeChanger
                    pageSizeOptions={[10, 20, 50, 100]} 
                  />
                </Col>
              )}
            </Card>
          </Row>
        }
        <Drawer
          title={<div className="d-flex-between" style={{ marginRight: "1.5rem" }}>Competency Details
            <Button
              type='text'
              style={{ border: 'none' }}
              icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
              onClick={handleMaximize} />
          </div>}
          open={isDrawerVisible}
          onClose={closeDrawer}
          footer={null}
          width={width}
          className="staff-competency-details-drawer close-btn-position">
          <div className="dynamic-drawer-width" onMouseDown={onMouseDown} />
          <Col span={24} className="skills-expanded-container expanded-detail-skill-wrapper">
            <Card>
            <Form form={form} layout="vertical" onFinish={onFinish}>
              <Row gutter={16}>
                <Col xs={24} lg={12}>
                  <Form.Item
                    name="display"
                    label="Competency Name"
                    rules={[{ required: true, message: 'Please enter skill display name' }]}
                  >
                    <Input onChange={() => {
                      dispatch(setSkill({
                        ...skill,
                        display: skill.display
                      }))
                    }} />
                  </Form.Item>
                </Col>
                <Col xs={24} lg={12}>
                  <Form.Item
                    name="sfiaLevel"
                    label="Sfia Level"
                    rules={[{ required: true, message: 'Please enter sfia level' }]}
                  >
                    <Input placeholder="Sfia level" onChange={(e) => dispatch(setTraineeSifaLevel(e.target.value))} />
                  </Form.Item>
                </Col>
                <Col xs={24} lg={12}>
                  <Form.Item label="Competency Description" name="competency_description" className="mt-16">
                    <TextArea rows={4} onChange={(e) => dispatch(setCompetencyDescription(e.target.value))} />
                  </Form.Item>
              </Col>
                <Col xs={24} lg={12}>
                <Form.Item label="Rationale" name="competency_rationale" className="mt-16">
                  <TextArea rows={4} onChange={(e) => dispatch(setCompetencyRationale(e.target.value))} />
                </Form.Item>
              </Col>
              <Col span={24}>
                <Form.Item
                  name="individualSkills"
                  label="Individual Skills"
                  rules={[{ required: true, message: 'Please select individual skills' }]}
                >
                  <Select mode="tags" allowClear onChange={handleSkillsChange}>
                  </Select>
                </Form.Item>
              </Col>
              <Form.Item className="update-submit-button flex-center gap-16">
              <Popconfirm
                title="Are you sure you want to approve this competency?"
                onConfirm={() => onFinish()}
                onCancel={() => {
                  message.info("Competency approving cancelled");
                }}
                okText="Yes"
                cancelText="No">
                <Button className="dark-orange-bg white-color"
                  loading={loading}
                >
                  Approve
                </Button>
              </Popconfirm>
              <Button className="dark-orange-color white-bg"
                style={{marginLeft:"0.5rem"}}
                  loading={loading}
                  onClick={handleDecline}
                >
                  Decline
                </Button>
            </Form.Item>
            </Row>
            </Form>
              <Divider />
              <EvidenceTable
                columns={columns}
                setIsEvidenceUploadExpanded={setIsEvidenceEditOn}
                expandedRowId={expandedRowId ? expandedRowId.toString() : null}
                setExpandedRowId={setExpandedRowId}
                
                addKeyToEvidence={addKeyToEvidence}
              />
            </Card>
          </Col>
        </Drawer>
        <Modal
          title="Verify Evidence"
          open={isEvidenceEditOn}
          onCancel={closeModal}
          footer={null}
          width={800}
        >
          <ChangeEvidenceStatus uuid={selectedSkillUUID} setIsEvidenceEditOn={setIsEvidenceEditOn} />
        </Modal>
      </>
      : <EmptyJobHandler title="No Skills" description="No skills have been added yet" />
  )
}
