import { Row, Col, Tag, Drawer, Form, Input, Table, Select, Button, Popconfirm, message, Card, Pagination, Flex, Typography, InputNumber, Tooltip, List, Divider } from 'antd';
import { useEffect, useState } from "react"
import { DeleteOutlined, UnorderedListOutlined,ArrowLeftOutlined, AppstoreFilled,SearchOutlined, PlusOutlined, EditOutlined, EyeOutlined } from '@ant-design/icons';
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';
import { useMutation } from "@apollo/client";

//Components
import EmptyJobHandler from "../commonComponents/EmptyJobHandler"
import TagComponent from "../commonComponents/Tag";
import AddCompetency from "./AddCompetency";
import SkillsTags from "./Profile/Skills/SkillsTags";
import EvidenceTable from "./Profile/Skills/EvidenceTable";

//Redux and custom hooks
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import { setUserProfileSkillTitle } from "../../redux/slices/profileSkillSlice";
import { resetEvidence, resetSkill, setEvidence, setSkill } from "../../redux/slices/experienceSlice";
import { CREATE_NOTIFICATION } from "../../graphql/mutations/createNotification";
import useEvidenceForm from "../../hooks/useEvidenceForm";
import { addSession, removeSession, resetEvidenceForm } from "../../redux/slices/updateEvidenceSlice";
import useTagType from "../../hooks/useTags";
import useFetchUserProfile from "../../hooks/useFetchUserProfile";
import { T_TraineeCompetenciesAttributes, T_TraineeCompetencyEvidence } from "../../types/profileResponse";
import { addEvidenceUpdatingSession, removeSfiaDimensionRequested, resetEvidenceUpdateData, setEvidenceUpdate, updateSfiaDimensionRequested } from "../../redux/slices/evidenceUpdatingSlice";

//Utils
import { getSfiaLevelStyle } from "../../utils/getSfiaLevel";
import { setSelectedGridView } from "../../redux/slices/gridViewSlice";
import { setSelectedCompetency } from '../../redux/slices/staffCompetencySlice';
import { sources } from "../../utils/commonUtils";
import useAxiosRequest from "../../hooks/useAxiosRequest";
import { getRunStage } from "../../utils/getRunStage";
import { setSelectedSkillsUUID } from "../../redux/slices/selectedSkillsUUIDSlice";
import '../../styles/slidingCard.css'
import StaffDataLoader from "../commonComponents/StaffDataLoader";

const { TextArea } = Input;
const { Paragraph } = Typography
const run_stage = getRunStage();

type SkillsProps = {
  loading: boolean;
}

export default function Skills({ loading: dataLoading }: SkillsProps) {
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [isSkillExpanded, setIsSkillExpanded] = useState<boolean>(false);
  const [selectedSkill, setSelectedSkill] = useState<T_TraineeCompetenciesAttributes | null>(null);
  const [expandedRowId, setExpandedRowId] = useState<React.Key | null>(null);
  const [isEvidenceUploadExpanded, setIsEvidenceUploadExpanded] = useState<boolean>(false)
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [page, setPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [paginationSize, setPaginationSize] = useState(10);
  const [sourceLinkMap, setSourceLinkMap] = useState<{ name: string; link: string }>({
    name: '',
    link: '',
  });
  const [width, setWidth] = useState(800);
  const [isResizing, setIsResizing] = useState(false);
  const [selectSkillUUID, setSelectSkillUUID] = useState<string>("");
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingRecord, setEditingRecord] = useState<T_TraineeCompetencyEvidence | null>(null);
  const [isAddCompetenceDrawerVisible, setIsAddCompetenceDrawerVisible] = useState(false);
  const [filteredData, setFilteredData] = useState<T_TraineeCompetenciesAttributes[]>([]);
  const [gridViewItems, setGridViewItems] = useState<T_TraineeCompetenciesAttributes[]>([]);

  const { competencies: skills } = useAppSelector((state) => state.traineeProfileResponse.user_profile)
  const { skill, evidence } = useAppSelector((state) => state.experience)
  const { allUserId, user_profile_id, user_role, trainee_id, batch } = useAppSelector(state => state.leapProfileId)
  const { sessions } = useAppSelector((state) => state.updatedEvidenceForm)
  const { evidenceDataToBeUpdated } = useAppSelector((state) => state.updateCompetencyEvidence)
  const gridView = useAppSelector((state) => state.gridView.selectedTab)

  const { handleSelectChange, handleMaxSectionChange, capitalizedOptions } = useEvidenceForm();
  const { getType } = useTagType();
  const {fetchUserProfile} = useFetchUserProfile();
  const [createNotification] = useMutation(CREATE_NOTIFICATION);

  // const itemsPerPage = 10;
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = gridViewItems.slice(indexOfFirstItem, indexOfLastItem);
  
  const handlePageChange = (page: number) => setCurrentPage(page);
  const handlePageSizeChange = (size: number) => setItemsPerPage(size);
  const { makeRequest, loading } = useAxiosRequest();

  const [form] = Form.useForm();
  const dispatch = useAppDispatch()

  const handleEditClick = (skill: T_TraineeCompetenciesAttributes) => {
    dispatch(setSelectedCompetency(skill))
    dispatch(setSelectedSkillsUUID(skill.uuid))
    setSelectSkillUUID(skill.uuid);
    setIsSkillExpanded(true);
    setSelectedSkill(skill);
  };

  const handleSkillEdit = (skill: T_TraineeCompetenciesAttributes) => {
    dispatch(setSelectedSkillsUUID(skill.uuid))
    setSelectSkillUUID(skill.uuid);
    setDrawerVisible(true);
    form.setFieldsValue({
      display: skill.display,
      individualSkills: skill.skills,
    });
    dispatch(setUserProfileSkillTitle(skill.display));
  }

  const closeDrawer = () => {
    setDrawerVisible(false);
    form.resetFields();
  };

  const handleSkillsChange = (selectedSkills: string[]) => {
    dispatch(
      setSkill({
        ...skill,
        individualSkills: selectedSkills,
      })
    );
  };

  useEffect(() => {
    const onMouseMoveHandler = (e: MouseEvent) => {
      if (isResizing) {
        const offsetRight =
          document.body.offsetWidth - (e.clientX - document.body.offsetLeft);
        const minWidth = 540;
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
    setFilteredData(extractData());
    setGridViewItems(skills.attributes);
  }, [skills]);

  const handleMaximize = () => {
    const newWidth = width === 2000 ? 540 : 2000;
    setWidth(newWidth);
  };

  const onMouseDown = () => setIsResizing(true);
  const onMouseUp = () => setIsResizing(false);

  const handleEdit = (record: T_TraineeCompetencyEvidence) => {
    setEditingRecord(record);
    setIsModalVisible(true);
    dispatch(setEvidenceUpdate({
      key: record.key || "",
      remark: record.remark,
      source: {
        link: record.source.link || "",
        name: record.source.name,
      },
      status: record.status,
      sentiment: record.sentiment,
      verified_by: record.verified_by,
      requested_by: record.requested_by,
      confidence_degree: record.confidence_degree,
      sfia_level_approved: record.sfia_level_approved,
      sfia_level_requested: Number(record.sfia_level_requested),
      sfia_dimensions_approved: record.sfia_dimensions_approved,
      sfia_dimensions_requested: record.sfia_dimensions_requested,
    }))
    form.setFieldsValue({
      sessions_edit: record.sfia_dimensions_requested,
      source_edit: record.source.name,
      sfia_level_requested_edit: Number(record.sfia_level_requested),
      link_edit: record.source.link,
      remark_edit: record.remark
    })
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    setEditingRecord(null);
  };

  const handleEditSelectChange = (value: string, index: number) => {
    dispatch(updateSfiaDimensionRequested({ index, name: value, level: null }));
  };

  const handleEditMaxSectionChange = (value: number, index: number) => {
    const existingDimension = evidenceDataToBeUpdated.sfia_dimensions_requested[index];
    const name = existingDimension?.name || '';
    dispatch(updateSfiaDimensionRequested({ index, name, level: value }));
  };

  const extractData = (): T_TraineeCompetenciesAttributes[] => {
    return skills.attributes
      .filter((attr: T_TraineeCompetenciesAttributes) => attr.name !== "")
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
  };

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
          <TagComponent text={record.status} type={getType(record.status)} />
        )
      }
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
          onClick={() => handleEditClick(record)}
        />
      ),
    },
  ];

  const columns: any = [
    {
      title: "SFIA level requested",
      dataIndex: "sfia_level_requested",
      key: "sfia_level_requested",
      render: (_text: string, record: T_TraineeCompetencyEvidence) => {
        return (
          record.sfia_level_requested ?
            <span>{record.sfia_level_requested}</span>
            : <span>--</span>
        )
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
          <TagComponent text={record.status} type={getType(record.status)} />
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
      title: "Edit",
      key: "edit",
      render: (_text: string, record: T_TraineeCompetencyEvidence) => {
        if (record.status !== "verified" && record.status !== "approved") {
          return (
            <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          );
        }
        return null;
      },
    },
  ]

  const addKeyToEvidence = (evidence: T_TraineeCompetencyEvidence[]): T_TraineeCompetencyEvidence[] => {
    return evidence.map((ev, index) => ({
      ...ev,
      key: `${index}`
    }));
  };

  const handleSourceChange = (value: string) => {
    setSourceLinkMap((prevState) => ({
      ...prevState,
      name: value,
    }));
  };

  const handleLinkChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSourceLinkMap((prevState) => ({
      ...prevState,
      link: e.target.value,
    }));
  };

  const onFinish = async () => {
    const selectedSkills = skills.attributes.find((skill:T_TraineeCompetenciesAttributes) => skill.uuid === selectSkillUUID);
    const data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "competencies",
          uuid: selectSkillUUID,
          data: {
            abilities: selectedSkills?.abilities,
            attitude: selectedSkills?.attitude,
            description: selectedSkills?.description,
            display: selectedSkills?.display,
            evidence: selectedSkills?.evidence,
            knowledge: selectedSkills?.knowledge,
            name: selectedSkills?.name,
            others: selectedSkills?.others,
            rationale: selectedSkills?.rationale,
            sfia_level: selectedSkills?.sfia_level,
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
      notificationMessageTeam: `Updated skills! `,
      notificationMessageTrainee: `Updated skills!`,
      where: "Competencies",
      traineeLink: `/trainee/trainee-profile`,
      staffLink: `/staff/trainee_details/${allUserId}/${trainee_id}/${user_profile_id}`,
    }

      await form.validateFields();    
      makeRequest({
        url: '/sjob/put-user-profile',
        method: 'POST',
        data,
        onSuccess: (response) => {
          if (response.status === 200) {
            createNotification({
              variables: {
                sender: allUserId,
                group: 1,
                detail: details,
                origin: "leap",
                batch,
              },
              onCompleted: (data) => {
                if (data?.createNotification?.data.id) {
                  message.success("Notification created successfully");
                } else {
                  console.error("Notification creation failed");
                }
              },
            });
            message.success("Skills updated successfully");
            dispatch(resetSkill());
            setDrawerVisible(false);
            fetchUserProfile();
            form.resetFields();
          }
        },
        onError: () => {
        },
      });
   
  };


  const onEvidenceFinish = async() => {
    const selectedSkills = skills.attributes.find(skill => skill.uuid === selectSkillUUID);
    const evidenceData = {
      source: sourceLinkMap,
      remark: evidence?.remark,
      sentiment: "",
      confidence_degree: "",
      sfia_level_requested: evidence.sfia_level_requested,
      sfia_level_approved: "",
      sfia_dimensions_approved: [],
      verified_by: "",
      sfia_dimensions_requested: (sessions && sessions.length > 0 &&
        sessions.every(session => session.name !== "" && session.level !== null))
        ? sessions.map(session => ({
          name: session.name,
          level: session.level
        }))
        : [],
      status: "Request for approval",
      overall_sfia: 1
    };
    const updatedEvidence = [
      ...(selectedSkills?.evidence || []),
      evidenceData
    ];

    const data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "competencies",
          uuid: selectSkillUUID,
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
            skills: selectedSkills?.skills,
          }
        }
      ],
      status: "approved",
    }

    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Updated evidence! `,
      notificationMessageTrainee: `Updated evidence!`,
      where: "Competencies",
      traineeLink: `/trainee/trainee-profile`,
      staffLink: `/staff/trainee_details/${allUserId}/${trainee_id}/${user_profile_id}`,
    }

      makeRequest({
        url: '/sjob/put-user-profile',
        method: 'POST',
        data,
        onSuccess: (response) => {
          if (response.status === 200) {
            createNotification({
              variables: {
                sender: allUserId,
                group: 1,
                detail: details,
                origin: "leap",
                batch,
              },
              onCompleted: (data) => {
                if (data?.createNotification?.data.id) {
                  message.success("Notification created successfully");
                } else {
                  console.error("Notification creation failed");
                }
              },
            });
            message.success("Evidence added successfully");
            dispatch(resetEvidence());
            setIsEvidenceUploadExpanded(false);
            dispatch(resetEvidenceForm());
            fetchUserProfile();
            form.resetFields();
          }
        },
        onError: () => {},
      });
  }

  const onFinishEdit = async() => {
    const updatedEvidence = selectedSkill?.evidence.map((evidence, index) => {
      if (index.toString() === evidenceDataToBeUpdated.key) {
        const updatedData = { ...evidenceDataToBeUpdated };
        delete updatedData.key;
        return {
          ...evidence,
          ...updatedData,
        };
      }
      return evidence;
    });
    const data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      user_profile_id: user_profile_id,
      user_profile: [
        {
          code: "competencies",
          uuid: selectSkillUUID,
          data: {
            abilities: selectedSkill?.abilities,
            attitude: selectedSkill?.attitude,
            description: selectedSkill?.description,
            display: selectedSkill?.display,
            evidence: updatedEvidence,
            knowledge: selectedSkill?.knowledge,
            name: selectedSkill?.name,
            others: selectedSkill?.others,
            rationale: selectedSkill?.rationale,
            sfia_level: selectedSkill?.sfia_level,
            sfia_estimation_method: selectedSkill?.sfia_estimation_method,
            experience_level: selectedSkill?.experience_level,
            skills: selectedSkill?.skills,
          }
        }
      ],
      status: "approved",
    }

    const details = {
      traineeId: trainee_id,
      notificationMessageTeam: `Updated evidence! `,
      notificationMessageTrainee: `Updated evidence!`,
      where: "Competencies",
      traineeLink: `/trainee/trainee-profile`,
      staffLink: `/staff/trainee_details/${allUserId}/${trainee_id}/${user_profile_id}`,
    }
    makeRequest({
      url: '/sjob/put-user-profile',
      method: 'POST',
      data,
      onSuccess: (response) => {
        if (response.status === 200) {
          createNotification({
            variables: {
              sender: allUserId,
              group: 1,
              detail: details,
              origin: "leap",
              batch,
            },
            onCompleted: (data) => {
              if (data?.createNotification?.data.id) {
                message.success("Notification created successfully");
              } else {
                message.error("Notification creation failed");
              }
            },
          });
          message.success("Evidence updated successfully");
          setIsModalVisible(true);
          dispatch(resetEvidenceUpdateData());
          fetchUserProfile();
          handleCancel();
          form.resetFields();
        }
      },
      onError: () => {
        handleCancel();
      },
    });
    } 

   const onSearch = (value: string) => {
    const fil = extractData().filter((item) => {
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
        )});    
      return setGridViewItems(cur);
    }
    setGridViewItems(skills.attributes);
  };

  if(dataLoading) return <StaffDataLoader/>

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
              <span>{extractData().length} Competencies</span>
              <span className="flex-center gap-8">
                <Button className="dark-orange-bg white-color"
                  icon={<PlusOutlined />}
                  onClick={()=> setIsAddCompetenceDrawerVisible(true)}
                >
                  New
                </Button>
               
              </span>
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
              dataSource={filteredData.length ? filteredData : extractData()}
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
              <span>{extractData().length} Competencies</span>
              <span className="flex-center gap-8">
                <Button className="dark-orange-bg white-color"
                  icon={<PlusOutlined />}
                  onClick={()=> setIsAddCompetenceDrawerVisible(true)}
                >
                  New
                </Button>
              </span>
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
                          <EyeOutlined onClick={() => handleEditClick(skill)} />
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
          title={<div className="d-flex-between" style={{ marginRight: "1.25rem" }}>Edit Skill
            <Button
              type='text'
              style={{ border: 'none' }}
              icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
              onClick={handleMaximize} />
          </div>}
          placement="right"
          onClose={closeDrawer}
          width={width}
          open={drawerVisible}
          className="close-btn-position"
        >
          <div className="dynamic-drawer-width" onMouseDown={onMouseDown} />
          <Form form={form} layout="vertical" onFinish={onFinish}>
            <Form.Item
              name="display"
              label="Competency"
              rules={[{ required: true, message: 'Please enter skill display name' }]}
            >
              <Input readOnly onChange={() => {
                dispatch(setSkill({
                  ...skill,
                  display: skill.display
                }))
              }} />
            </Form.Item>
            <Form.Item
              name="individualSkills"
              label="Individual Skills"
              rules={[{ required: true, message: 'Please select individual skills' }]}
            >
              <Select mode="tags" allowClear onChange={handleSkillsChange}>
              </Select>
            </Form.Item>
            <Form.Item className="update-submit-button">
              <Popconfirm
                title="Are you sure you want to update this skill?"
                onConfirm={() => onFinish()}
                onCancel={() => {
                  message.info("Skill updating cancelled");
                }}
                okText="Yes"
                cancelText="No">
                <Button className="dark-orange-bg white-color"
                  loading={loading}>
                  Update
                </Button>
              </Popconfirm>
            </Form.Item>
          </Form>
        </Drawer>
        <Drawer
          title={<div className="d-flex-between" style={{ marginRight: "1.25rem" }}>Add Evidence
            <Button
              type='text'
              style={{ border: 'none' }}
              icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
              onClick={handleMaximize} />
          </div>}
          placement="right"
          onClose={() => setIsEvidenceUploadExpanded(false)}
          open={isEvidenceUploadExpanded}
          className="close-btn-position"
          width={width}>
          <div className="dynamic-drawer-width" onMouseDown={onMouseDown} />
          <Form
            layout="vertical"
            form={form}
            onFinish={onEvidenceFinish}
            initialValues={{}}>
            <Form.Item name="source"
              rules={[{ required: true, message: 'Please select source!' }]}
              label="Source">
              <Select onChange={handleSourceChange}>
                {sources.map((source) => (
                  <Select.Option key={source} value={source}>
                    {source}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="link" label="Link">
              <Input onChange={handleLinkChange} />
            </Form.Item>
            <Paragraph className="mt-16">SFIA Dimension </Paragraph>
            <Form.List
              name="sessions"
              initialValue={sessions}
              rules={[]}
            >
              {(sessions, { add, remove }) => (
                <div style={{ display: 'flex', rowGap: 16, flexDirection: 'column' }}>
                  {sessions.map((field) => {
                    return (
                      <Card
                        size="small"
                        title={
                          <div className="d-flex-between">
                            <span>{`SFIA Dimension-${field.name + 1}`}</span>
                            {sessions.length > 0 && (
                              <Flex justify='flex-end'>
                                <Button
                                  style={{ background: "#FF4405", color: "#FFF" }}
                                  icon={<DeleteOutlined />}
                                  onClick={() => {
                                    dispatch(removeSession(field.name));
                                    remove(field.name)
                                  }}
                                />
                              </Flex>
                            )}
                          </div>
                        }
                        key={field.key}
                      >
                        <Row gutter={[16, 16]}>
                          <Col span={12}>
                            <Form.Item
                              label="Name"
                              name={[field.name, 'name']}
                              rules={[{ required: false, message: 'Please select SFIA Dimension name!' }]}
                              tooltip="Select SFIA Dimension"
                            >
                              <Select
                                options={capitalizedOptions}
                                placeholder="Select name"
                                onChange={(value) => handleSelectChange(value, field.name)}
                                value={field.name.toString()}
                              />
                            </Form.Item>
                          </Col>
                          <Col span={12}>
                            <Form.Item
                              label="Level"
                              name={[field.name, 'level']}
                              rules={[{ required: false, message: 'Please input level!' }]}
                              tooltip="SFIA Level starting from 1 to 5"
                            >
                              <InputNumber
                                placeholder='Level'
                                style={{ width: "100%" }}
                                min={1}
                                max={5}
                                value={field.name}
                                onChange={(value) => handleMaxSectionChange(value, field.name)}
                              />
                            </Form.Item>
                          </Col>

                        </Row>
                      </Card>
                    )
                  })}

                  {sessions.length < 5 && (
                    <Button type="dashed"
                      onClick={() => {
                        dispatch(addSession());
                        add();
                      }}
                      block
                      icon={<PlusOutlined />}
                    >
                      Add Item
                    </Button>
                  )}
                </div>
              )}
            </Form.List>
            <Form.Item
              label="SFIA level requested"
              rules={[{ required: true, message: 'Please input level!' }]}
              name="sfia_level_requested" className="mt-16">
              <InputNumber
                min={1}
                max={7}
                style={{ width: "100%" }}
                value={evidence.sfia_level_requested}
                onChange={(value) => dispatch(setEvidence({
                  ...evidence,
                  sfia_level_requested: value
                }))}
              />
            </Form.Item>

            <Form.Item label="Remark" name="remark" className="mt-16">
              <TextArea rows={4} onChange={(e) => dispatch(setEvidence({
                ...evidence,
                remark: e.target.value
              }))} />
            </Form.Item>
            <Form.Item className="update-submit-button">
              <Popconfirm
                title="Are you sure you want to update this evidence?"
                onConfirm={() => onEvidenceFinish()}
                onCancel={() => {
                  message.info("Evidence updating cancelled");
                }}
                okText="Yes"
                cancelText="No">
                <Button className="dark-orange-bg white-color"
                  loading={loading}
                >
                  Update
                </Button>
              </Popconfirm>
            </Form.Item>
          </Form>
        </Drawer>
        <Drawer title={<div className="d-flex-between" style={{ marginRight: "1.25rem" }}>Edit Evidence
          <Button
            type='text'
            style={{ border: 'none' }}
            icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
            onClick={handleMaximize} />
        </div>}
          open={isModalVisible} onClose={handleCancel} footer={null}
          className="close-btn-position"
          width={width}>
          <div className="dynamic-drawer-width" onMouseDown={onMouseDown} />
          <Form
            onFinish={onFinishEdit}
            initialValues={{
              link_edit: editingRecord?.source.link,
              sfia_level_requested_edit: editingRecord?.sfia_level_requested,
              sessions_edit: editingRecord?.sfia_dimensions_requested,
              source_edit: editingRecord?.source.name,
              remark_edit: editingRecord?.remark
            }}
            layout="vertical">
            <Form.Item name="source_edit" label="Source">
              <Select onChange={
                (value) => dispatch(
                  setEvidenceUpdate({
                    ...evidenceDataToBeUpdated,
                    source: {
                      link: evidenceDataToBeUpdated.source.link,
                      name: value
                    }
                  })
                )
              } value={editingRecord?.source.name}>
                {sources.map((source) => (
                  <Select.Option key={source} value={source}>
                    {source}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="link_edit" label="Link">
              <Input onChange={(value) =>
                dispatch(setEvidenceUpdate({
                  ...evidenceDataToBeUpdated,
                  source: {
                    link: value.target.value,
                    name: evidenceDataToBeUpdated.source.name || ""
                  }
                }))
              } value={editingRecord?.source.link} />
            </Form.Item>
            <Paragraph>SFIA Dimensions Requested</Paragraph>
            <Form.List
              name="sessions_edit"
              rules={[]}
            >
              {(sessions, { remove, add }) => (
                <div style={{ display: 'flex', rowGap: 16, flexDirection: 'column' }}>
                  {sessions.map((field, index) => {
                    return (
                      <Card
                        size="small"
                        title={
                          <div className="d-flex-between">
                            <span>{`SFIA Dimension-${field.name + 1}`}</span>
                            {sessions.length > 1 && (
                              <Flex justify='flex-end'>
                                <Button
                                  style={{ background: "#FF4405", color: "#FFF" }}
                                  icon={<DeleteOutlined />}
                                  onClick={() => {
                                    dispatch(removeSfiaDimensionRequested(field.name));
                                    remove(field.name)
                                  }}
                                />
                              </Flex>
                            )}
                          </div>
                        }
                        key={field.key}
                      >
                        <Row gutter={[16, 16]}>
                          <Col span={12}>
                            <Form.Item
                              label="Name"
                              name={[field.name, 'name']}
                              rules={[{ required: true, message: 'Please select SFIA_Dimension name!' }]}
                              tooltip="Select SFIA_Dimension"
                            >
                              <Select
                                options={capitalizedOptions}
                                placeholder="Select name"
                                onChange={(value) => handleEditSelectChange(value, index)}
                                value={field.name.toString()}
                              />
                            </Form.Item>
                          </Col>
                          <Col span={12}>
                            <Form.Item
                              label="Level"
                              name={[field.name, 'level']}
                              rules={[{ required: true, message: 'Please input level!' }]}
                              tooltip="SFIA Level starting from 1 to 4"
                            >
                              <InputNumber
                                placeholder='Level'
                                style={{ width: "100%" }}
                                min={1}
                                max={5}
                                value={field.name}
                                onChange={(value) => handleEditMaxSectionChange(value as number, index)}
                              />
                            </Form.Item>
                          </Col>
                        </Row>
                      </Card>
                    )
                  })}
                  {sessions.length < 5 && (
                    <Button type="dashed"
                      onClick={() => {
                        dispatch(addEvidenceUpdatingSession());
                        add();
                      }}
                      block
                      icon={<PlusOutlined />}
                    >
                      Add Item
                    </Button>
                  )}
                </div>
              )}
            </Form.List>
            <Form.Item
              label="SFIA level requested"
              name="sfia_level_requested_edit"
              className="mt-16">
              <InputNumber
                min={1}
                max={7}
                style={{ width: "100%" }}
                onChange={(value) => dispatch(setEvidenceUpdate({
                  ...evidenceDataToBeUpdated,
                  sfia_level_requested: value
                }))}
              />
            </Form.Item>
            <Form.Item label="Remark" name="remark_edit" className="mt-16">
              <TextArea rows={4} onChange={(e) => dispatch(setEvidenceUpdate({
                ...evidenceDataToBeUpdated,
                remark: e.target.value
              }))} />
            </Form.Item>
            <Form.Item className="update-submit-button">
              <Popconfirm okText="Yes" cancelText="No"
                title="Are you sure you want to upload this award?"
                onConfirm={() => onFinishEdit()}
                onCancel={() => { message.info("Profile creation cancelled") }}>
                <Button className="dark-orange-bg white-color" loading={loading} >
                  Update
                </Button>
              </Popconfirm>
            </Form.Item>
          </Form>
        </Drawer>
        <Drawer
          title={<div className="d-flex-between" style={{ marginRight: "1.25rem" }}>Competency Details
            <Button
              type='text'
              style={{ border: 'none' }}
              icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
              onClick={handleMaximize} />
          </div>}
          placement="right"
          onClose={() => setIsSkillExpanded(false)}
          open={isSkillExpanded}
          width={width}
          className="close-btn-position"
        >
          <div className="dynamic-drawer-width" onMouseDown={onMouseDown} />
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
              <SkillsTags handleSkillEdit={handleSkillEdit} />
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
        </Drawer>
        <Drawer
          title={<div className="d-flex-between" style={{ marginRight: "1.25rem" }}>Add Competency
          <Button
            type='text'
            style={{ border: 'none' }}
            icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
            onClick={handleMaximize} />
        </div>}
          placement="right"
          onClose={() => setIsAddCompetenceDrawerVisible(false)}
          open={isAddCompetenceDrawerVisible}
          width={width}
          className="close-btn-position"
        >
          <div className="dynamic-drawer-width" onMouseDown={onMouseDown} />
            <AddCompetency setIsAddCompetenceDrawerVisible={setIsAddCompetenceDrawerVisible}/>
        </Drawer>
      </>
      : <EmptyJobHandler title="No Skills" description="No skills have been added yet" />
  )
}
