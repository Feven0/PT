import { useMutation } from '@apollo/client';
import { Button, Col, Divider, Form, Input, InputRef, message, Row, Select, Space, Typography, } from 'antd'
import { PlusOutlined, } from "@ant-design/icons";
import React, { useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom';
import moment from 'moment-timezone';

//GraphQL queries and mutations
import { useAppSelector } from "../../../redux/hooks/hooks";
import { CREATE_JOB_ASSET } from "../../../graphql/mutations/CreateJobs";
import { CREATE_NOTIFICATION } from "../../../graphql/mutations/createNotification";

const { Text } = Typography
const { Option } = Select


type JobAssetTextContentType = {
    name: string,
    content: {
        data: string,
        documentType: string
        username: string,
        timestamp: string

    }
    slug: string,
    jobTrainee: [string],
    traineeId: string,
    type: string,
}

let indexSelect = 0
export default function CreateFileAsset() {
    const navigate = useNavigate();
    const [form] = Form.useForm();
    const params = useParams()
    const traineeJobID = params.id as string
    const username = useAppSelector((state) => state.user?.username)
    const {allUserId, batch, trainee_id: id} = useAppSelector((state) => state?.leapProfileId)

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
        'CV',
        'Portfolio',
    ]);


    const handleCreateCancel = () => {
        form.resetFields();
        navigate(-1)
    };

    const onFinish = (values: any) => {
        const JobAssetTextContent: JobAssetTextContentType = {
            name: values.name,
            content: {
                data: values.content,
                documentType: values.type,
                username: username,
                timestamp: moment().toISOString()

            },
            traineeId: id,
            jobTrainee: [traineeJobID],
            slug: `${values.name}-${id}-${(Date.now()).toString(36)}`,
            type: "File"
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
                            notificationMessageTeam: `${username} Created a new job application material! Title:${JobAssetTextContent.name} Type:${values.type} `,
                            notificationMessageTrainee: ``,
                            where: `${JobAssetTextContent.name}`,
                            traineeLink: `/trainee/job/${traineeJobID}/AssetDetail/${assetID}`,
                            staffLink: `/staff`
                        },
                        batch: batch
                    },
                    onCompleted(_data) {
                        form.resetFields();
                        message.success(`Application material Created!`);
                    }
                })

            }
        })
    }


    return (
        <div style={{ maxWidth: "800px", marginLeft: "auto", marginRight: "auto" }} >
            <Form
                form={form}
                layout="vertical"
                onFinish={onFinish}
                autoComplete="off">
                <Form.Item
                    name="name"
                    label={<Text className='job_label--element'>Title</Text>}
                    rules={[{ required: true }, { type: 'string', warningOnly: true }, { type: 'string', min: 2 }]}
                >
                    <Input style={{ maxWidth: "300px", minWidth: "300px" }} placeholder="title" />
                </Form.Item>
                <Form.Item
                    name="type"
                    tooltip='Type of text content you are going to create'
                    initialValue={'CV'}
                    label={<Text className='job_label--element'>Document Type</Text>}
                    rules={[{ required: true }, { type: 'string', warningOnly: true }, { type: 'string', min: 2 }]}>
                    <Select
                        defaultValue={'CV'}
                        style={{ maxWidth: "300px", minWidth: "300px" }}
                        placeholder="select type of document"
                        dropdownRender={menu => (
                            <>
                                {menu}
                                <Divider style={{ margin: '8px 0' }} />
                                <Space style={{ padding: '0 8px 4px' }}>
                                    <Input
                                        style={{ maxWidth: "200px", minWidth: "200px" }}
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
                <Form.Item
                    name="content"
                    label={<Text className='job_label--element'>File Link</Text>}
                    rules={[{ required: true }, { type: 'string', warningOnly: true }, { type: 'string', min: 2 }]}
                >
                    <Input type={'url'} style={{ maxWidth: "300px", minWidth: "300px" }} placeholder="link to the file" />
                </Form.Item>
                <Form.Item>
                    <Row gutter={[16, 16]}>
                        <Col>
                            <Space>
                                <Button type="primary" htmlType="submit">
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
        </div>
    )
}
