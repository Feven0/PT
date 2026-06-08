import { useEffect, useState } from 'react'
import { Modal, Collapse, Button, Steps, Col, Row, Space, Typography, Dropdown, Form, message, Select, List, Tooltip, } from 'antd'
import { CaretRightOutlined, PlusOutlined, EllipsisOutlined, ExclamationCircleOutlined, LinkOutlined, MinusCircleOutlined, EditOutlined, PlusCircleOutlined } from "@ant-design/icons";
import { Link } from 'react-router-dom'
import { useMutation, useQuery } from '@apollo/client';
import Ajv from 'ajv';
import moment from 'moment-timezone';
import type { MenuProps } from 'antd';

//Components
import ServerError from "../commonComponents/ServerError";
import AddJobStatus from "./AddJobStatus";
import JobDetailFeedbackTrainee from "./JobDetailFeedbackTrainee";
import TraineeJobRubric from "./TraineeJobRubrics";
import CKEditorContent from "./CKEditorContent";
import EmptyJobHandler from "../commonComponents/EmptyJobHandler";

//Types
import { FormSchema, JobAssetType, JobContentType, jobRubricsQueryType, JobStatusType, JobTraineeQuery, JobTraineesType, schema } from '../../types/Jobs';

//Graphql
import { GET_JOB_DETAIL, JOB_RUBRICS_LIST } from "../../graphql/queries/CreateJobs";
import { JOB_TRAINEE_STATUS, JOB_TRAINEE_TAG } from "../../graphql/mutations/CreateJobs";

//Redux and Custom hooks
import { useAppSelector } from "../../redux/hooks/hooks";

//Styles
import '../../styles/jobs.css'
import StaffDataLoader from "../commonComponents/StaffDataLoader";

const { Text, } = Typography
const { Step } = Steps;
const { Option } = Select
const { Panel } = Collapse
const { confirm } = Modal;

export type JobDetailProps = {
    job_trainee_id: string;
}

export default function TraineeJobDetail({ job_trainee_id} : JobDetailProps) {
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [isPriorityModalVisible, setIsPriorityModalVisible] = useState(false);
    const {trainee_id:Tid} = useAppSelector((state) => state.leapProfileId)
    const [form] = Form.useForm();

    const { error, loading, data, refetch } = useQuery<JobTraineeQuery>(GET_JOB_DETAIL, {
        variables: { traineeJobID: job_trainee_id, Tid: Tid },
        fetchPolicy: 'network-only',
    });

    const { data: dataRubrics } = useQuery<jobRubricsQueryType>(JOB_RUBRICS_LIST, {
        fetchPolicy: "network-only",
    });
    
    const [updateJobTraineeTag] = useMutation(JOB_TRAINEE_TAG);
    const [updateJobTraineeStatus] = useMutation(JOB_TRAINEE_STATUS);

    useEffect(() => {
        refetch()
    }, [])

    if (loading) return <StaffDataLoader />
    else if (error) return (<ServerError />);
    

    if (!data?.jobTrainees?.data[0]) {
        return (
            <EmptyJobHandler 
                title="No job details"
                 description="There are no job details at the moment. Please look back later!"  />
        )
    }


    const JobContent: JobContentType = {
        title: data?.jobTrainees?.data[0]?.attributes?.job?.data?.attributes?.title || "",
        companyName: data?.jobTrainees?.data[0]?.attributes?.job?.data?.attributes?.companyName || "",
        link: data?.jobTrainees?.data[0]?.attributes?.job?.data?.attributes?.link || "",
        description: data?.jobTrainees?.data[0]?.attributes?.job?.data?.attributes?.description || "",
        slug: data?.jobTrainees?.data[0]?.attributes?.job?.data?.attributes?.slug || "",
        Platform: data?.jobTrainees?.data[0]?.attributes?.job?.data?.attributes?.Platform || "",
        id: data?.jobTrainees?.data[0]?.attributes?.job?.data?.id || "",
        avatar: ""
    }

    const TraineeJobContent: JobTraineesType = {
        Tag: data?.jobTrainees?.data[0]?.attributes?.Tag || "",
        slug: data?.jobTrainees?.data[0]?.attributes?.slug || "",
        status: data?.jobTrainees?.data[0]?.attributes?.status || "",
        id: data?.jobTrainees?.data[0]?.id || ""
    }

    const loadStatusData = (): JobStatusType[] => {
        const tree_data: JobStatusType[] = []
        if (data?.jobTrainees?.data[0]?.attributes?.job_appliecation_statuses?.data && data?.jobTrainees?.data[0]?.attributes?.job_appliecation_statuses?.data.length > 0) {
            const stats = data?.jobTrainees?.data[0]?.attributes?.job_appliecation_statuses?.data
            for (let i = 0; i < stats.length; i++) {
                const item = stats[i]
                tree_data.push({
                    name: item.attributes?.Name || "",
                    date: item.attributes?.createdAt ? item.attributes?.createdAt.substring(0, item.attributes?.createdAt.indexOf('T')) : "",
                    description: item.attributes?.Description || "",
                    id: item.id || ""
                })
            }
        }
        return tree_data
    }

    const loadAssetData = (): JobAssetType[] => {
        const tree_data: JobAssetType[] = []
        if (data?.jobTrainees?.data[0]?.attributes?.job_assets?.data && data?.jobTrainees?.data[0]?.attributes?.job_assets?.data.length > 0) {
            const assets = data?.jobTrainees?.data[0]?.attributes?.job_assets?.data
            for (let i = 0; i < assets.length; i++) {
                const item = assets[i]
                tree_data.push({
                    name: item.attributes?.name || "",
                    type: item.attributes?.type ? (item.attributes?.type === 'File' ? item.attributes?.content.documentType : item.attributes?.type) : "",
                    id: item.id || "",
                    username: item.attributes?.content.username,
                    updatedAt: item.attributes?.updatedAt
                })
            }
        }
        return tree_data
    }
    
    const ajv = new Ajv()


    const rubricIsValid = (rub: any) => {
        const validate = ajv.compile(schema)
        const valid = validate(rub)
        return valid
    }

    const FormIsValid = (form: any) => {
        const validate = ajv.compile(FormSchema)
        const valid = validate(form)
        if (!valid) {
          //
        }
        return valid
    }

    const rubric = dataRubrics?.jobRubrics.data[0]
    const response = data?.jobTrainees?.data[0]?.attributes?.job_review_responses?.data[0]
    const rubric_content = rubric ? ((response && rubricIsValid(response?.attributes?.content)) ? response?.attributes?.content : rubric?.attributes?.content) : null
    const AdHoc_content = rubric ? ((response && FormIsValid(response?.attributes?.AdHoc)) ? response?.attributes?.AdHoc : rubric?.attributes?.AdHoc) : null
    
    const handleCancel = () => setIsModalVisible(false);
    const showModal = () => setIsModalVisible(true);

    const showArchiveConfirm = () => {
        confirm({
            title: 'Are you sure archive this Job?',
            icon: <ExclamationCircleOutlined />,
            content: '',
            okText: 'Yes',
            okType: 'danger',
            cancelText: 'No',
            onOk() {
                updateJobTraineeStatus({
                    variables: {
                        traineeJobID: job_trainee_id,
                        status: "Closed"
                    },
                    onCompleted(_data) {
                        refetch()
                    }
                })
            },
            onCancel() {
            },
        });
    };

    const showActivateConfirm = () => {
        confirm({
            title: 'Do you Want to activate these job?',
            icon: <ExclamationCircleOutlined />,
            content: '',
            onOk() {
                updateJobTraineeStatus({
                    variables: {
                        traineeJobID: job_trainee_id,
                        status: "Active"
                    },
                    onCompleted(_data) {
                        refetch()
                    }
                })
            },
            onCancel() {
            },
        });
    };

    const onFinish = (values: any) => {
        updateJobTraineeTag({
            variables: {
                traineeJobID: job_trainee_id,
                Tag: values.Tag
            },

            onCompleted(data) {
                if(data.updateJobTrainee.data.id) {
                    setIsPriorityModalVisible(false)
                    form.resetFields();
                    message.success('Job Priority updated Created!');
                    refetch()
                }
            }
        })
    }

    const handleCancelPriority = () => setIsPriorityModalVisible(false);

    const items: MenuProps['items'] = [
    {
      key: '1',
      label: (
        <div className="flex gap-8">
            <EditOutlined style={{ fontSize: "18px" }} />
            Change Priority
        </div>
      ),
      onClick: () => {
        setIsPriorityModalVisible(true);
      }
    },
    {
      key: '2',
      label: (
        TraineeJobContent.status === "Active" ? (
          <div className="flex gap-8">
            <MinusCircleOutlined style={{ fontSize: "18px" }} />
            Archive
          </div>
        ):null
      ),
        onClick: () => {
            showArchiveConfirm();
        }
    },
    {
      key: '3',
      label: (
        TraineeJobContent.status === "Closed" ? (
          <div className="flex gap-8">
            <PlusCircleOutlined style={{ fontSize: "18px" }} />
            Activate
          </div>
        ):null
      ),
        onClick: () => {
            showActivateConfirm();
        }
    },
  ];

    const JobReviewExtra = () => {
        if (rubric && ((response && rubricIsValid(response?.attributes?.content)))) {
            return <Space size={'small'}>
                <Text type="success">Reviewed </Text>
            </Space>
        }
        else {
            return <Space size={'small'}>
                <Text type="warning">Not Reviewed </Text>
            </Space>
        }
    }

    return (
        <>
            <Space direction='vertical' className="full-width job-details-container">
                <Space>
                    <Text className='JobView_company--text' >
                        {JobContent.companyName}
                    </Text>
                    <Text code>{JobContent.Platform}</Text>
                </Space>
                <Row gutter={[16, 16]} className="mt-16">
                    <Col xs={24} md={12}>
                        <Space className="full-width" direction='vertical' size={'large'}>
                            <Collapse defaultActiveKey={'1'} ghost
                                expandIcon={({ isActive }) => <CaretRightOutlined rotate={isActive ? 90 : 0} />}>
                                <Panel extra={<JobReviewExtra />}
                                    header={
                                        <Text className='Job_Detail_card_title--text'>
                                            Job Review
                                        </Text>
                                    } key='2'>
                                    <div style={{ 
                                            maxWidth: "800px", 
                                            padding: "10px 0px", 
                                            marginLeft: "auto", 
                                            marginRight: "auto" 
                                            }} >
                                        <Row justify='space-between' gutter={[8, 8]} style={{ marginBottom: "10px" }}>
                                            <Col span={22}>
                                                <TraineeJobRubric rubric={rubric_content} AdHoc={AdHoc_content} />
                                            </Col>
                                        </Row>
                                    </div>
                                </Panel>
                                <br />
                                <Panel key='1' extra={<>
                                        {
                                            TraineeJobContent.status === 'Active' && <Text type="success">Active</Text>
                                        }{
                                            TraineeJobContent.status === 'Closed' && <Text type="danger">Closed</Text>
                                        }
                                    </>}
                                    header={
                                        <Text className='Job_Detail_card_title--text'>
                                            Status
                                        </Text>
                                    }>
                                    <div style={{ 
                                                maxWidth: "800px", 
                                                padding: "10px 0px", 
                                                marginLeft: "auto", 
                                                marginRight: "auto" 
                                            }}>
                                        <Steps progressDot
                                            current={loadStatusData().length}
                                            direction="vertical">
                                            {
                                                loadStatusData().map(item => (
                                                    <>
                                                        <Step key={item.id} title={item.name} description={item.description} subTitle={item.date} />
                                                    </>
                                                ))
                                            }
                                        </Steps>
                                    </div>
                                    <div style={{ float: 'right' }}>
                                        <Button onClick={() => showModal()} type="text" color='danger' shape="round" >
                                            <Text className='JobView_addNewasset--text'>
                                                <PlusOutlined /> status
                                            </Text>
                                        </Button>
                                    </div>
                                </Panel>
                                <br />
                                <Panel key='3' extra={loadAssetData().length ? <Text>{loadAssetData().length}</Text> : null}
                                    header={
                                        <Text className='Job_Detail_card_title--text'>
                                            Submitted for Feedback
                                        </Text>
                                    }>
                                    <div style={{ maxWidth: "800px", padding: "10px 0px", marginLeft: "auto", marginRight: "auto" }} >
                                        <List>
                                            {
                                                loadAssetData().length > 0 && loadAssetData().map((item: JobAssetType) => (
                                                    <List.Item key={item.id}>
                                                        <Link to={`AssetDetail/${item.id}`}>
                                                            <Space direction='vertical' size={1}>
                                                                <Text className="job-detail-asset-title--text">
                                                                    {item.type}
                                                                    <br></br>
                                                                    {item.name}
                                                                </Text>
                                                                <Text className="job-detail-asset-title--text">
                                                                    {`Last updated `}
                                                                    <Tooltip title={moment().format("YYYY-MM-DD HH:mm:ss")}>
                                                                        <span>{moment(item.updatedAt).fromNow()}</span>
                                                                    </Tooltip>
                                                                    {` by ${item.username}`}

                                                                </Text>
                                                            </Space>
                                                        </Link>
                                                    </List.Item>
                                                ))
                                            }
                                        </List>
                                    </div>
                                    <div style={{ float: 'right' }}>
                                        <Button onClick={() => { }} type="text" color='danger' shape="round">
                                            <Link to={'/trainee/job/CreateNewAsset'}>
                                                <Text className='JobView_addNewasset--text'>
                                                    <PlusOutlined />    New
                                                </Text>
                                            </Link>
                                        </Button>
                                    </div>
                                </Panel>
                            </Collapse>
                            <JobDetailFeedbackTrainee jobTitle={JobContent.title} slug={JobContent.slug} job_trainee_id={job_trainee_id} />
                        </Space>
                    </Col>
                    <Col xs={24} md={12}>
                        <Space className="full-width" direction='vertical'>
                            <Collapse defaultActiveKey={'1'} ghost
                                expandIcon={({ isActive }) => <CaretRightOutlined rotate={isActive ? 90 : 0} />}>
                                <Panel key='1' 
                                        extra={<Dropdown menu={{ items }} placement="bottom">
                                                <Button icon={<EllipsisOutlined />}/>
                                            </Dropdown> 
                                        }
                                    header={
                                        <Text className='Job_Detail_card_title--text'>
                                            Detail{" "} <a rel="noreferrer" target="_blank" href={JobContent.link.trim()}><LinkOutlined /></a>
                                        </Text>
                                    }>
                                    <div style={{ maxWidth: "800px", padding: "10px 0px", marginLeft: "auto", marginRight: "auto" }} >
                                        <CKEditorContent content={JobContent.description} />
                                    </div>
                                </Panel>
                            </Collapse>
                        </Space>
                    </Col>
                </Row>
            </Space>

            <Modal
                width={368}
                title="Add New Status"
                centered
                open={isModalVisible}
                onCancel={handleCancel}
                footer={<></>}
                closable={false}
            >
                <AddJobStatus setIsModalVisible={setIsModalVisible} jobId={TraineeJobContent.id} />
            </Modal>
            <Modal
                width={368}
                title="Change Priority"
                centered
                open={isPriorityModalVisible}
                onCancel={handleCancelPriority}
                footer={<></>}
                closable={false}
            >
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={onFinish}
                    autoComplete="off">
                    <Form.Item
                        name="Tag"
                        initialValue={TraineeJobContent.Tag}
                        label={<Text className='job_label--element'>Status</Text>}
                        rules={[{ required: true }, { type: 'string', warningOnly: true }, { type: 'string', min: 2 }]}>
                        <Select>
                            <Option key={'High Priority'}>
                                High Priority
                            </Option>
                            <Option key={'Low Priority'}>
                                Low Priority
                            </Option>
                            <Option key={'Normal'}>
                                Normal
                            </Option>
                        </Select>
                    </Form.Item>
                    <Form.Item>
                        <Row gutter={[16, 16]}>
                            <Col>
                                <Space>
                                    <Button type="primary" htmlType="submit">
                                        Submit
                                    </Button>
                                    <Button type="text" style={{ color: "#F5222D" }} onClick={handleCancelPriority}>
                                        Cancel
                                    </Button>
                                </Space>
                            </Col>
                        </Row>
                    </Form.Item>
                </Form>
            </Modal>
        </>
    )
}
