import { Button, Collapse, Form, Input, Select, Switch, Typography, message } from 'antd';
import { useState } from 'react'
import { useAppSelector } from '../../redux/hooks/hooks';
import useAxiosRequest from "../../hooks/useAxiosRequest";
import { newJobApplication } from "../../utils/commonUtils";
import { getRunStage } from "../../utils/getRunStage";

import '../../styles/slidingCard.css'
import '../../App.css'

const { Text } = Typography;
const { Option } = Select;

const run_stage = getRunStage();

export default function AddNewJob() {
    const [applicationStatus, setApplicationStatus] = useState('Interested');
    const [showOthers, setShowOthers] = useState(true);
    const [generateAssets, setGenerateAssets] = useState(false);
    
    const { user_profile_id, allUserId, user_role } = useAppSelector((state) => state.leapProfileId);
    const [form] = Form.useForm();
    const { makeRequest, loading } = useAxiosRequest();

    const onFinish = () => {
        form.validateFields().then(() => {
            if (form.getFieldValue('jobLink').trim() === "") {
                message.error("Please enter job link");
                return;
            }
            const payload = {
                user_role: user_role,
                run_stage: run_stage,
                all_user_id: allUserId,
                user_profile_id: user_profile_id,
                job_url: form.getFieldValue('jobLink'),
                application_status: applicationStatus,
                show_others: showOthers,
                generate_assets: generateAssets,
                template_id: 1
            }
            makeRequest({
            url: '/sjob/post-job-contribution',
            method: 'POST',
            data: payload,
            onSuccess: (response) => {
              if (response.status === 200) {
                message.success('Job contribution posted successfully');
                form.resetFields();
                setGenerateAssets(false);
              }
            },
            onError: () => { },
          });
        })
        .catch(() => {});
    }

    const items = [
        {
            key: '1',
            label: (
                <div className="flex gap-8 match-text-title"> Add New Jobs</div>
            ),
            children: (
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={onFinish}
                    autoComplete="off"
                >
                    <Form.Item
                        className="mt-16"
                        name="applicationStatus"
                        label={<Text>Status</Text>}
                        tooltip='Your current application status'
                        initialValue={applicationStatus}
                        rules={[{ required: true, message: 'Please select Application status' }]}
                    >
                        <Select placeholder="Select Match Status" onChange={(value) => setApplicationStatus(value)}>
                            {newJobApplication.map((status) => (
                                <Option key={status} value={status}>
                                    {status}
                                </Option>
                            ))}
                        </Select>
                    </Form.Item>
                    <Form.Item
                        className="mt-16"
                        name="jobLink"
                        label={<Text>Job Link</Text>}
                        tooltip='Link to the job posting'
                        rules={[{ required: true }, { type: 'url', warningOnly: true }, { type: 'string', min: 6 }]}
                    >
                        <Input placeholder="Enter Job Link" />
                    </Form.Item>
                    <div className="d-flex-between">
                        <Form.Item label="Show others" initialValue={showOthers}>
                            <Switch
                                defaultChecked
                                onChange={(value) => setShowOthers(value)}
                            />
                        </Form.Item>
                        <Form.Item label="Generate Assets" initialValue={generateAssets}>
                            <Switch
                                defaultChecked={false}
                                onChange={(value) => setGenerateAssets(value)}
                            />
                        </Form.Item>
                    </div>
                    <Form.Item>
                        <Button htmlType="submit" className="dark-orange-bg white-color" loading={loading}>
                            Submit
                        </Button>
                    </Form.Item>
                </Form>
            ),
        },
    ];

    return (
        <Collapse items={items}  />
    )
}
