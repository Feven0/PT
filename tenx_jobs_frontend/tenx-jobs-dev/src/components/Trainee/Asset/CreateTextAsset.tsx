import { useMutation } from '@apollo/client';
import { Button, Col, Divider, Form, Input, InputRef, message, Row, Select, Space, Typography } from 'antd'
import { PlusOutlined, } from "@ant-design/icons";
import React, { useRef, useState } from 'react'
import moment from 'moment-timezone';
import { useNavigate, useParams } from 'react-router-dom';

//GraphQL queries and mutations
import { CREATE_JOB_ASSET } from "../../../graphql/mutations/CreateJobs";
import { useAppSelector } from "../../../redux/hooks/hooks";
import { CREATE_NOTIFICATION } from "../../../graphql/mutations/createNotification";
import CkEditor from "../../commonComponents/CKEditor";

const { Text } = Typography
const { Option } = Select

type JobAssetTextContentType = {
    name: string,
    content: {
        data: string,
        username: string,
        timestamp: string,
    }
    slug: string,
    jobTrainee: [string],
    traineeId: string,
    type: string,
}
let indexSelect = 0

export default function CreateTextAsset() {
    const navigate = useNavigate();
    const [form] = Form.useForm();
    const params = useParams()
    const [EditorContent, setEditorContent] = useState<string>("")
    const traineeJobID = params.id as string
    const username = useAppSelector((state) => state.user?.username)
    const {allUserId, batch,trainee_id:id } = useAppSelector((state) => state?.leapProfileId)
    const [createNotification] = useMutation(CREATE_NOTIFICATION);
    const [createJobAsset] = useMutation(CREATE_JOB_ASSET);
    const inputRef = useRef<InputRef>(null);
    const [name, setName] = useState('');

    const onNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setName(event.target.value);
    };

    const addItem = (e: React.MouseEvent<HTMLAnchorElement>) => {
        e.preventDefault();
        setItems([...items, name || `New item ${indexSelect++}`]);
        setName('');
        setTimeout(() => {
            inputRef.current?.focus();
        }, 0);
    };

    const [items, setItems] = useState([
        'Email',
        'Cover Letter',
        'QA',
    ]);

    const handleCreateCancel = () => {
        form.resetFields();
        navigate(-1)
    };

    const handleDataChange = (data: string) => {
        setEditorContent(data);
    }

    const onFinish = (values: any) => {
        const JobAssetTextContent: JobAssetTextContentType = {
            name: values.name,
            content: {
                data: EditorContent,
                username: username,
                timestamp: moment().toISOString()
            },
            traineeId: id,
            jobTrainee: [traineeJobID],
            slug: `${values.name}-${id}-${(Date.now()).toString(36)}`,
            type: values.type
        }
        createJobAsset({
            variables: {
                name: JobAssetTextContent.name,
                slug: JobAssetTextContent.slug,
                type: JobAssetTextContent.type,
                jobTrainees: JobAssetTextContent.jobTrainee,
                traineeID: JobAssetTextContent.traineeId,
                content: JobAssetTextContent.content
            },
            onCompleted(data) {
                const assetID = data.createJobAsset.data.id
                createNotification({
                    variables: {
                        sender: allUserId,
                        group: 1,
                        detail: {
                            traineeId: id,
                            notificationMessageTeam: `${username} Created a new job application material. Title:${JobAssetTextContent.name} Type:${JobAssetTextContent.type} `,
                            notificationMessageTrainee: ``,
                            where: `${JobAssetTextContent.name}`,
                            traineeLink: `/trainee/job/${traineeJobID}/AssetDetail/${assetID}`,
                            staffLink: `/staff`,
                            origin: "leap"
                        },
                        batch: batch
                    },
                    onCompleted(_data) {
                        setEditorContent("")
                        form.resetFields();
                        message.success('Application material Created!');
                    }
                })

            }
        })
    }

    return (
        <>
            <Form
                form={form}
                layout="vertical"
                onFinish={onFinish}
                autoComplete="off">
                  <Row gutter={[16, 16]}>
                    <Col xs={24} lg={12}>
                        <Form.Item
                        name="name"
                        label={<Text className='job_label--element'>Title</Text>}
                        rules={[{ required: true }, { type: 'string', warningOnly: true }, { type: 'string', min: 2 }]}
                    >
                        <Input placeholder="title" />
                    </Form.Item>
                    </Col>
                    <Col xs={24} lg={12}>
                    <Form.Item
                    name="type"
                    tooltip='Type of text content you are going to create'
                    initialValue={'Email'}
                    label={<Text className='job_label--element'>Type</Text>}
                    rules={[{ required: true }, { type: 'string', warningOnly: true }, { type: 'string', min: 2 }]}>
                    <Select
                        defaultValue={'Email'}
                        placeholder="select type of text"
                        dropdownRender={menu => (
                            <>
                                {menu}
                                <Divider style={{ margin: '8px 0' }} />
                                <Space style={{ padding: '0 8px 4px' }}>
                                    <Input
                                        placeholder="Add new Type"
                                        ref={inputRef}
                                        value={name}
                                        onChange={onNameChange} />
                                    <Button type="text" icon={<PlusOutlined />} onClick={addItem}>
                                        Add
                                    </Button>
                                </Space>
                            </>
                        )}>
                        {items.map(item => (
                            <Option key={item}>{item}</Option>
                        ))}
                    </Select>
                </Form.Item>
                    </Col>
                  </Row>
               
               
                <Divider orientation='left'>
                    {<Text className='challenge_label--element'>Content</Text>}
                </Divider>
                <Form.Item name="content">
                    <CkEditor value={EditorContent} onDataChange={handleDataChange}/>
                </Form.Item>
                <Form.Item>
                    <Row gutter={[16, 16]}>
                        <Col>
                            <Space>
                                <Button className="dark-orange-bg white-color" htmlType="submit">
                                    Publish
                                </Button>
                                <Button type="text" style={{ color: "#F5222D" }} onClick={handleCreateCancel}>
                                    Cancel
                                </Button>
                            </Space>
                        </Col>
                    </Row>
                </Form.Item>
            </Form>
        </>
    )
}
