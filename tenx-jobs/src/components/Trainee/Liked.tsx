import { useEffect, useRef, useState } from "react";
import {  Avatar, Button, Card, Col, Divider, Form, Input, InputRef, Modal, Popconfirm, Row, Select, Space, Tooltip, Typography, message } from "antd";
import { PlusOutlined, ReloadOutlined, DownOutlined } from '@ant-design/icons';
import { FaExternalLinkAlt } from "react-icons/fa";

//Components
import ServerError from "../commonComponents/ServerError";
import StaffDataLoader from "../commonComponents/StaffDataLoader";

//Redux and Custom Hooks
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import { setMatchStatus } from "../../redux/slices/experienceSlice";
import { setUserReactionIds } from "../../redux/slices/userReactionIdsSlice";
import { setRecord } from "../../redux/slices/engagementRowSlice";
import useTraineeLikeRenderIcon from "../../hooks/useTraineeLikeRenderIcon";
import useFilterAndPagination from "../../hooks/userFilterAndPagination";
import { setEngagementsStats } from "../../redux/slices/userStatsSlice";
import { resetSelectedRows } from "../../redux/slices/tableExtension";
import useEngagementTableCellRender from "../../hooks/useEngagementTableCellRender";
import useAxiosRequest from "../../hooks/useAxiosRequest";

//Types
import { TableTypes } from "../../types/TableTypes";

//Utility Functions
import { rowClassName } from "../../utils/rowClassname";
import { ensureURLProtocol } from "../../utils/isUrl";
import { ApplicationStatusFilterOptions } from "../../utils/ApplicationStatusFilterOptions";
import { getSingularPluralString } from "../../utils/getSingularPluralString";
import { matchStatuses, reportStatus } from "../../utils/commonUtils";
import { TableParams } from "../Staff/Engagement/EngagedJobs";
import TableExtensionCursor from "../../libs/DataTables/TableExtensionCursor";
import { getRunStage } from "../../utils/getRunStage";

//Styles
import '../../styles/slidingCard.css'

const { Option } = Select;
const { TextArea } = Input;
const { Text } = Typography;

const run_stage = getRunStage();
export const DEFAULT_SINCE_DAYS = 7;

export default function Liked() {
  const [matchStatusFormVisible, setMatchStatusFormVisible] = useState(false);
  const [applyStatusFormVisible, setApplyStatusFormVisible] = useState(false);
  const [name, setName] = useState('');
  const [items, setItems] = useState(ApplicationStatusFilterOptions());
  const [description, setDescription] = useState('');
  const [selectedValue, setSelectedValue] = useState('Interested');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false)
  const [jobStatus, setJobStatus] = useState(reportStatus[0].value);
  const [otherReason, setOtherReason] = useState(""); 
  const [response, setResponse] = useState<any>(null);
  const [tableParams, setTableParams] = useState<TableParams>({
    pagination: {
      current: 1,
      pageSize: 10,
    },
  }); 
  
  //Redux States
  const {selectedRows} = useAppSelector((state) => state.tableExtension);
  const {match_status} = useAppSelector((state) => state.experience);
  const { allUserId, user_role, user_profile_id, trainee_id, batch } = useAppSelector((state) => state.leapProfileId);
  const {record: engagementRecord } = useAppSelector((state) => state.updateRecord);
  const {filter, days} = useAppSelector((state) => state.updateSince);
  
  const [form] = Form.useForm();
  const dispatch = useAppDispatch();
  const inputRef = useRef<InputRef>(null);
  const {renderTableCell} = useEngagementTableCellRender();
  const { makeRequest, loading: reportLoading, error } = useAxiosRequest();
  const { makeRequest:newRequest, loading, error:fetchErr } = useAxiosRequest();

const getTraineeEngagements = async (since = days || DEFAULT_SINCE_DAYS) => {
  const postData = {
    user_role: user_role,
    run_stage: run_stage,
    all_user_id: allUserId,
    filter: {},
    since: since,
    limit: response?.cursor?.total || 10,
    reaction_type: "all",
    match_type: "all",
    information_level: "minimal",
    return_skip: false,
    cursor: {
      page: tableParams?.pagination?.current || 1,
      pageSize: tableParams?.pagination?.pageSize|| 10,
      page_size: tableParams?.pagination?.pageSize || 10,
      page_count: tableParams?.pagination?.current || 1,
      total: totalPage || 0,
      filter: response?.cursor?.filter || {},
      query: response?.cursor?.query || {}          
    }
  };
  newRequest({
      url: '/sjob/get-all-user-reactions',
      method: 'POST',
      data: postData,
      onSuccess: (response) => {
        setResponse(response.data);
      },
      onError: () => { }
    });
  };

  useEffect(() => {
    if (response) {
      const reaction_id = response.reactions[0]?.data.reduce((acc: any, curr: any) => {
        acc[curr.user_reaction_id] = curr.job_title;
        return acc;
      }, {});
      dispatch(setUserReactionIds({ userReactionIds: reaction_id }));
    }
  }, [response]);

  useEffect(() => {
    getTraineeEngagements();
  }, [tableParams?.pagination?.current, tableParams?.pagination?.pageSize, batch, filter, days, allUserId, user_profile_id]);


  useEffect(() => {
    dispatch(setEngagementsStats({
      Like: response?.stats?.Like,
      Skip: response?.stats?.Like,
      Super_Like: 0,
      credit_remaining: response?.stats?.credit_remaining,
      credit_used: response?.stats?.credit_used,
      dislike: response?.stats?.dislike,
      like: response?.stats?.like,
      max_credit: response?.stats?.max_credit,
      other: response?.stats?.other,
      superlike: response?.stats?.superlike,
    }))
  }, [response]);

  const addItem = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    setItems([...items, { value: name || `New item ${items.length + 1}`, text: name || `New item ${items.length + 1}` }]);
    setName('');
    setTimeout(() => {
        inputRef.current?.focus();
    }, 0);
  };

  const showModal = () => setIsModalVisible(true);
  const handleOk = () => setIsModalVisible(false);
  const handleCancel = () => setIsModalVisible(false);

  const handleClick = (url: string, record: any) => {
    dispatch(setRecord({
      company_name: record.company_name,
      job_id: record.job_id,
      job_profile_id: record.job_profile_id,
      job_title: record.job_title,
      user_reaction_id: record.user_reaction_id,
    }))
    if(record.apply_status === "Interested") {
      showModal();
    }
    setTimeout(() => {
      window.open(ensureURLProtocol(url), '_blank', 'noopener,noreferrer'); 
    }, 0);
  };

  const handleRefetch = () => getTraineeEngagements();
  const handleMatchStatusChange = (value:string) =>  dispatch(setMatchStatus(value));
  const handleReportingJobChange = (value: string) => setJobStatus(value);
  const { renderIcon } = useTraineeLikeRenderIcon(allUserId, user_profile_id, handleClick);

  const onNameChange = (e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value);
  const handleDescription = (event: React.ChangeEvent<HTMLTextAreaElement>) => setDescription(event.target.value);
  const handleSelectChange = (value: string) => setSelectedValue(value);

  const { handleTodayChange, handleLast7Change, handleFetchLast15Days, handleFetchLastMonth,handleFetchLast3Months,
  } = useFilterAndPagination(setTableParams, getTraineeEngagements);


  const handleAddStatus = () => {
    if (selectedRows.length === 0) {
      Modal.warning({
        title: 'No Rows Selected',
        content: 'Please select at least one row',
      });
      return;
    }
    setApplyStatusFormVisible(true);
  }

  const onApplyStatusFormFinish =  () => {
    const id_list = selectedRows.map((row: any) => ({
      user_reaction_id: row.user_reaction_id,
      job_trainee_id: row.job_trainee_id || "",
      job_id: row.job_id,
    }));
    const postData = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      trainee_id: trainee_id,
      id_list,
      application_status: selectedValue,
      description: description,
    } 
       makeRequest({
        url: '/sjob/put-job-application-status',
        method: 'POST',
        data: postData,
        onSuccess: (response) => {
          let successCount = 0;
          let failureCount = 0;
    
          response.data.feedback.forEach((feedback: any) => {
            if (feedback.status === 200) {
              successCount++;
            } else if (feedback.status === 400) {
              failureCount++;
          }
        });
  
        if (successCount > 0) {
          message.success(`${successCount} out of ${selectedRows.length} records updated successfully`);
        }
        if (failureCount > 0) {
          message.error(`${failureCount} out of ${selectedRows.length} records failed to update`);
        }
        getTraineeEngagements();
        setApplyStatusFormVisible(false);
        dispatch(resetSelectedRows());
        form.resetFields();
      },
      onError: () => {
        setApplyStatusFormVisible(false);
        dispatch(resetSelectedRows());
      },
    });
    
  }

  const handleMatchStatus = () => {
    if (selectedRows.length === 0) {
      Modal.warning({
        title: 'No Rows Selected',
        content: 'Please select at least one row',
      });
      return;
    }
    
    setMatchStatusFormVisible(true);
    const initialValues = {
      rows: selectedRows.map((row:any, index:number) => ({
        match_status: index === 0 ? row.match_status : "", 
        job_title: row.job_title,
      }))
    };
    form.setFieldsValue(initialValues);
  };

  const handleReportJob = () => {
    if (selectedRows.length === 0) {
      Modal.warning({
        title: 'No Rows Selected',
        content: 'Please select at least one row',
      });
      return;
    }
    setIsReportModalOpen(true)
  }

  const handleSendJobToLeap = () => {
    if (selectedRows.length === 0) {
      Modal.warning({
        title: 'No Rows Selected',
        content: 'Please select at least one row',
      });
      return;
    }
    
    else {
      const user_reaction_ids = selectedRows.map((row:any) => row.user_reaction_id);
      const postData = {
        user_role: user_role,
        run_stage: run_stage,
        all_user_id: allUserId,
        user_reaction_ids: user_reaction_ids,
        template_id: "1",
        overwrite: false
      }    

       makeRequest({
        url: '/sjob/put-reaction-to-leap',
        method: 'POST',
        data: postData,
        onSuccess: (response) => {
          if(response.status === 200) {
            getTraineeEngagements();
            dispatch(resetSelectedRows());
          }
        },
        onError: () => {
          dispatch(resetSelectedRows());
        },
      });
    }
  }

  const onFinish =  () => {
    const user_reaction_ids = selectedRows.map((row:any) => row.user_reaction_id);
    const postData = {
      user_role: user_role,
      all_user_id: allUserId,
      user_reaction_ids: user_reaction_ids,
      reaction_type: match_status,
      run_stage: run_stage,
    }
      makeRequest({
        url: '/sjob/put-user-reaction-types',
        method: 'POST',
        data: postData,
        onSuccess: (resp) => {
          if (resp.data.feedback) {
            let successCount = 0;
            let failureCount = 0;
            resp.data.feedback.forEach((feedback: any) => {
              if (feedback.status === 200) {
                successCount++;
              } else if (feedback.status === 400) {
                failureCount++;
              }
            });
    
            if (successCount > 0) {
              message.success(`${successCount} records updated successfully`);
            }
            if (failureCount > 0) {
              message.error(`${failureCount} rows were not updated`);
            }
            getTraineeEngagements();
            dispatch(resetSelectedRows());
          }
          setMatchStatusFormVisible(false);
          form.resetFields();
          dispatch(resetSelectedRows());
        },
        onError: () => {
          dispatch(resetSelectedRows());
        },
      });
  };

  const onReportFinish = () => {
    const reason = jobStatus === 'other' ? otherReason : jobStatus;
    const jobProfileIds = selectedRows.map((row: any) => row.job_profile_id);
    const data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      job_profile_id:jobProfileIds,
      reason: reason,
    }
      makeRequest({
        url: '/sjob/post-report-invalid-job',
        method: 'POST',
        data,
        onSuccess: () => {
          setIsReportModalOpen(false);
          getTraineeEngagements();
          dispatch(resetSelectedRows());
        },
        onError: () => {
          setIsReportModalOpen(false);
          dispatch(resetSelectedRows());
        },
      });
  }

  const totalPage = response?.cursor?.total || 10;
    const handleTableChange = (pagination: any) => {
  
      setTableParams((prevParams) => ({
        ...prevParams,
        pagination: {
          ...prevParams.pagination,
          current: pagination.current,
          pageSize: pagination.pageSize,
        },
      }));
    }

  const columns = response?.reactions[0]?.columns
    .filter((column: any) => {
      if (column.name === 'expand_reaction') {
        return true;
      }
     
      return !['user_profile_id', 'job_profile_id', 'all_user'].includes(column.name);
    })
    .map((column: any) => ({
      title: column.label.charAt(0).toUpperCase() + column.label.slice(1),
      dataIndex: column.name,
      key: column.key,
      type: column.type,
      show: column.show,
      sorter: column.sorting ? (a: any, b: any) => {
        const valueA = a[column.name];
        const valueB = b[column.name];
        if (!isNaN(valueA) && !isNaN(valueB)) {
          return valueA - valueB;
        }
        if (valueA < valueB) return -1;
        if (valueA > valueB) return 1;
        return 0;
      } : undefined,
      filters: column.has_filter ? column.filter.options.map((option:any) => ({
        text: option.name,
        value: option.value,
    })) : undefined,
      onFilter: column.has_filter ? (value:string, record:any) => {
        const recordValue = record[column.name];
        if (typeof recordValue === 'string' && typeof value === 'string') {
            return recordValue.toLowerCase() === value.toLowerCase();
        }
        return recordValue === value;
    } : undefined,
  
      render: (_text: string, record: any) => {
        if (column.has_icon) {
          return (
            <Space>
              {renderIcon(column.icon, record[column.name], record)}
            </Space>
          );
        }
        return renderTableCell(column.type, record[column.name]);
      }
    }));
  
    const dataSourceWithKeys = response?.reactions[0]?.data.map((item: any, index: number) => ({
      ...item,
      key: index.toString(), 
    }))

  const TableProp: TableTypes = {
    dataSource: dataSourceWithKeys,
    counterName: response?.reactions[0]?.counterName,
    columns: columns,
    size: "small",
    bordered: false,
    loading: loading,
    scroll: { x: 768 },
    onChange: handleTableChange,
    allowEditColumn: true,
    allowRowSelection: true,
    rowClassName: rowClassName,
    dropDown: [
      {
        autoFocus: false,
        placement: "bottom",
        name: "Change",
        menu: {
          items: [
            {
              key: "change-apply-status",
              label: "Apply Status",
              onClick: () => { handleAddStatus() }
            },
            {
              key: "change-match-status",
              label: "Match Status",
              onClick: () => { handleMatchStatus() },
            },
            {
              key:"report_job",
              label: "Report Job",
              onClick: () => {handleReportJob()}
            }
          ],
        },
      },
      {
        autoFocus: false,
        placement: "bottom",
        name: <div className="flex-center gap-8"><p>{filter ? filter : "Last 7 days" }</p><DownOutlined/></div>,
        menu: {
          items: [
            {
              key: "today",
              label: "Today",
              onClick: () => {handleTodayChange() },
            },
            {
              key: "last_7_days",
              label: "Last 7 days",
              onClick: () => {handleLast7Change() },
            },
            {
              key: "last_15_days",
              label: "Last 15 days",
              onClick: () => { handleFetchLast15Days() }
            },
            {
              key: "last_30_days",
              label: "Last 30 days",
              onClick: () => { handleFetchLastMonth() },
            },
            {
              key:"last_90_days",
              label: "Last 90 days",
              onClick: () => {handleFetchLast3Months()}
            }
          ],
        },
      }
    ],
    buttons: [
      {
        type: "link",
        icon: <Tooltip title="Refetch"><ReloadOutlined /></Tooltip>,
        onClick: () => {
          handleRefetch();
        },
      },
      {
        name: <Tooltip title="Send to leap"><div className="flex-center gap-8 send-to-leap-btn"><span>Generate</span><FaExternalLinkAlt /></div></Tooltip>,
        type: "link",
        onClick: () => {
          handleSendJobToLeap();
        },
      },
    ],

    search: {
      searchPermission: true,
    },
    pagination: {
      showSizeChanger: true,
      current: tableParams?.pagination?.current,
      paginationSize: tableParams?.pagination?.pageSize,
      setPaginationSize:  (pageSize: number) => {
        setTableParams((prevParams) => ({
          ...prevParams,
          pagination: {
            ...prevParams.pagination,
            pageSize: pageSize,
          },
        }));
      },
      total: totalPage,    
    },
  }

  const handleCreateCancel = () => {
    setApplyStatusFormVisible(false)
    form.resetFields();
  };

  const handleStatusSubmission = () => {
    const id_list = [engagementRecord.user_reaction_id, engagementRecord.job_trainee_id,  engagementRecord.job_id];
    const sanitized_id_list = [{
      user_reaction_id: id_list[0] !== undefined && id_list[0] !== null && id_list[0] !== 'na' ? id_list[0] : "",
      job_trainee_id: id_list[1] !== undefined && id_list[1] !== null && id_list[1] !== 'na' ? id_list[1] : "",
      job_id: id_list[2] !== undefined && id_list[2] !== null && id_list[2] !== 'na' ? id_list[2] : ""
    }];

    const postData = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      trainee_id: trainee_id,
      id_list:sanitized_id_list,
      application_status: 'Applied',
      description: ""
    }
    makeRequest({
      url: '/sjob/put-job-application-status',
      method: 'POST',
      data: postData,
      onSuccess: (response) => {
        if (response.status === 200) {
          getTraineeEngagements();
          setIsModalVisible(false);
        }else {
          setIsModalVisible(false);
        }
      },
      onError: () => {
        setIsModalVisible(false);
      },
    });
  }

  if(!response) return <StaffDataLoader/>
  if (error || fetchErr) return <ServerError />;

  return (
    <Row gutter={16} justify="center" className="mobile-liked-jobs-wrapper">
      {response && (
        <Col span={24} className="liked-jobs-container-column">
          <TableExtensionCursor {...TableProp} />
        </Col>
      )}

      <Modal
        title={
          <div className="d-flex-between mb-8" style={{borderBottom:"1px solid whitesmoke"}}>
            <span>Update Match Status</span>
          </div>
        }
        open={matchStatusFormVisible}
        onCancel={() => setMatchStatusFormVisible(false)}
        footer={null}>
          <Form form={form} layout="vertical" className="mt-16">
           <span style={{
            fontSize: "1rem",
           }}>You have selected {getSingularPluralString(selectedRows.length, 'row')}</span>

            {selectedRows.length > 0 && (<>
              <Form.Item
                className="mt-16"
                name="match_status"
                label="Match Status"
                rules={[{ required: true, message: 'Please select match status' }]}
                initialValue={match_status}
              >
                 <Select placeholder="Select Match Status" onChange={handleMatchStatusChange}>
                    {matchStatuses.map((status) => (
                        <Option key={status.value} value={status.value}>
                            {status.display}
                        </Option>
                    ))}
                </Select>
              </Form.Item>

              <Form.Item>
                <Popconfirm
                  title="Are you sure you want to update this match status?"
                  onConfirm={onFinish}
                  onCancel={() => {
                    message.info("Match status updating cancelled");
                  }}
                  okText="Yes"
                  cancelText="No"
                >
                  <Button
                    className="dark-orange-bg white-color"
                    loading={reportLoading}
                  >
                    Update
                  </Button>
                </Popconfirm>
              </Form.Item>
            </>
          )}
        </Form>
        </Modal>
        <Modal
          title="Apply Status"
          open={applyStatusFormVisible}
          onCancel={() => setApplyStatusFormVisible(false)}
          footer={null}>
             <Form
              form={form}
              layout="vertical"
              onFinish={onApplyStatusFormFinish}
              autoComplete="off">
                 <span style={{
                  fontSize: "1rem",
                  marginBottom: "1rem",
              }}>You have selected {getSingularPluralString(selectedRows.length, 'row')}</span>
            <Form.Item
                name="applicationStatus"
                tooltip='Your current application status'
                initialValue={'Interested'}
                label={<Text className='job_label--element'>Status</Text>}
                rules={[{ required: true }, 
                        { type: 'string', warningOnly: true }, 
                        { type: 'string', min: 2 }]}>
                <Select
                    value={selectedValue}
                    onChange={handleSelectChange}
                    placeholder="select"
                    dropdownRender={menu => (
                        <>
                            {menu}
                            <Divider style={{ margin: '8px 0' }} />
                            <Space style={{ padding: '0 8px 4px' }}>
                                <Input
                                    placeholder="Add new Status"
                                    ref={inputRef}
                                    value={name}
                                    onChange={onNameChange} />
                                  <Button className="dark-orange-bg white-color" type="text" icon={<PlusOutlined />} onClick={addItem}>
                                      Add
                                  </Button>
                            </Space>
                        </>
                    )}>
                   {items.map(item => (
                    <Option key={item.value} value={item.value}>
                      {item.text}
                    </Option>
                  ))}
                </Select>
            </Form.Item>
            <Form.Item
                name="description"
                tooltip="Add short description for the job status update"
                label={<Text className='job_label--element'>Status Description</Text>}
                rules={[{ type: 'string', warningOnly: true }, { type: 'string', min: 2 }]}>
                <TextArea onChange={handleDescription} placeholder="Add description for the status(optional)" maxLength={250} />
            </Form.Item>
            <Form.Item>
                <Row gutter={[16, 16]}>
                    <Col span={24}>
                        <Space>
                            <Popconfirm
                              title="Are you sure you want to update this apply status?"
                              onConfirm={onApplyStatusFormFinish}
                              onCancel={() => {
                                message.info("Apply status updating cancelled");
                              }}
                              okText="Yes"
                              cancelText="No"
                            >
                              <Button
                                className="dark-orange-bg white-color"
                                loading={reportLoading}
                              >
                                Update
                              </Button>
                            </Popconfirm>
                            <Button type="text" style={{ color: "#F5222D" }} onClick={handleCreateCancel}>
                                Cancel
                            </Button>
                        </Space>
                    </Col>
                </Row>
            </Form.Item>
        </Form>
      </Modal>

      <Modal 
          open={isModalVisible} 
          onOk={handleOk} 
          onCancel={handleCancel}
          footer={null}
          title={<div className="dark-orange-color"><h3>Have you applied for this job?</h3></div>}
          >
            <Row gutter={16} justify="center">
                <Col span={24}>
                    <Card className="mt-16" style={{
                      background:"#F5F5F5"
                    }}>
                       <h4>{engagementRecord.job_title}</h4>
                       <div className="flex-center gap-8 mt-16">
                       <Avatar shape="square" size="small" className="work-experience-logo">
                          {engagementRecord.company_name.charAt(0).toUpperCase()}
                        </Avatar>
                        <p>{engagementRecord.company_name}</p>
                       </div>
                    </Card>
                    <div className="mt-16 flex-center gap-16">
                    <Button 
                        onClick={handleStatusSubmission}
                        loading={reportLoading}
                        className="dark-orange-bg white-color">
                        Yes I did
                      </Button>
                      <Button 
                        onClick={handleCancel}
                        className="white-bg dark-color">
                          No
                      </Button>
                    </div>
                </Col>
            </Row>
      </Modal>
        <Modal
          open={isReportModalOpen}
          onOk={()=>setIsReportModalOpen(false)}
          onCancel={()=>setIsReportModalOpen(false)}
          footer={null}
          title={<div className="dark-orange-color"><h3>Report Job</h3></div>}
          >
            <Row gutter={16}>
              <Col span={24}>
                <Form form={form} 
                  layout="vertical" 
                  initialValues={{
                    job_status: reportStatus[0].value, 
                  }}
                  className="mt-16">
                  <Form.Item
                        className="mt-16"
                        name="job_status"
                        label="Reason for Reporting"
                        rules={[{ required: true, message: 'Please select match status' }]}
                      >
                        <Select
                              placeholder="Select reason" 
                              defaultActiveFirstOption={true}
                              onChange={handleReportingJobChange}>
                            {reportStatus.map((status) => (
                                <Select.Option key={status.value} value={status.value}>
                                    {status.display}
                                </Select.Option>
                            ))}
                        </Select>
                      </Form.Item>
                      {jobStatus === 'other' && (
                        <Form.Item
                          name="other_reason"
                          label="Please specify"
                          rules={[{ required: true, message: 'Please provide details for the "Other" reason' }]}
                        >
                          <Input
                            placeholder="Enter your reason"
                            value={otherReason}
                            onChange={(e) => setOtherReason(e.target.value)}
                          />
                        </Form.Item>
                      )}
                      <Form.Item
                        className="flex-center gap-16"
                      >
                        <Popconfirm
                          title="Are you sure you want to report this job?"
                          onConfirm={onReportFinish}
                          onCancel={() => {
                            message.info("Reporting cancelled");
                          }}
                          okText="Yes"
                          cancelText="No"
                          className="flex-center gap-16"
                        >
                          <Button
                            className="dark-orange-bg white-color"
                            loading={reportLoading}
                          >
                            Report
                          </Button>
                        </Popconfirm>
                      </Form.Item>
                </Form>
              </Col>
            </Row>
        </Modal>
    </Row>
  );
}
