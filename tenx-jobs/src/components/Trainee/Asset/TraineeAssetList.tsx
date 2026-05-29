import { useMutation, useQuery } from '@apollo/client';
import { Button, List, Space, Spin, Table, Tooltip, Typography } from 'antd';
import React, { useState } from 'react'
import { useParams } from 'react-router-dom';
import moment from 'moment';

//Components
import Unauthorized from "../../commonComponents/Unauthorized";
import ServerError from "../../commonComponents/ServerError";

//Redux and Custom hooks
import { useAppSelector } from "../../../redux/hooks/hooks";

//Graphql queries and mutations
import { JOB_APPLICATION_MATERIALS } from "../../../graphql/queries/CreateJobs";
import { EDIT_JOB_ASSET } from "../../../graphql/mutations/CreateJobs";

//Types
import { JobAssetEntityResponseCollection, JobTraineeEntity } from "../../../types/generated";

//Utilities
import { tableColumnTextFilterConfig } from "../../../utils/tableColumnTextFilterConfig";
import StaffDataLoader from "../../commonComponents/StaffDataLoader";

const { Text } = Typography
type JobAssetType = {
    name: string,
    type: string,
    id: string,
    username: string,
    updatedAt: string,
    key: string,
    JobTrainee: string[]
}
type JobAssetQueryType = {
    jobAssets: JobAssetEntityResponseCollection
}

export default function TraineeAssetList() {
    const {trainee_id: Tid } = useAppSelector((state) => state?.leapProfileId)
    const params = useParams()
    const traineeJobID = params.id as string

    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
    const [selectedRows, setselectedRows] = useState<JobAssetType[]>([])
    const [page, setPage] = useState(1);
    const [paginationSize, setPaginationSize] = useState(25);

    const { loading, error, data } = useQuery<JobAssetQueryType>(JOB_APPLICATION_MATERIALS, {
        variables: { "traineeID": Tid },
        fetchPolicy: "network-only",
    });
    const [editJobAsset]  = useMutation(EDIT_JOB_ASSET);

    if (loading)  return <StaffDataLoader />
    
    if (error) {
        if (error?.graphQLErrors[0]?.message === "Forbidden access") {
            return <Unauthorized />
        } else {
            return <ServerError />
        }
    }

    const loadAssetData = (): JobAssetType[] => {
        const tree_data: JobAssetType[] = []
        if (data?.jobAssets.data) {
            const assets = data.jobAssets.data
            for (let i = 0; i < assets.length; i++) {
                const item = assets[i]
                const jobTrainee: string[] = []
                item.attributes?.job_trainees?.data && item.attributes.job_trainees.data.forEach((job: JobTraineeEntity) => {
                    job.id && jobTrainee.push(job.id)
                })
                tree_data.push({
                    name: item.attributes?.name || "",
                    type: item.attributes?.type ? (item.attributes?.type === 'File' ? item.attributes?.content.documentType : item.attributes?.type) : "",
                    id: item.id || "",
                    username: item.attributes?.content.username,
                    updatedAt: item.attributes?.updatedAt,
                    key: item.id || "",
                    JobTrainee: jobTrainee
                })
            }
        }
        return tree_data
    }
    const AssetColumns = [
        {
            title: '#',
            key: 'index',
            width: "7%",
            render: (_text: string, _record: any, index: number) => (page - 1) * paginationSize + index + 1,
        },
        {
            title: 'Materials',
            key: 'slug',
            dataIndex: 'content',
            render: (_value: any, record: any) => (
                <List.Item key={record.id}>
                    <Space direction='vertical' size={1}>
                        <Text
                            style={{
                                fontSize: "16px",
                                fontWeight: "400",
                                fontStyle: "normal",
                                lineHeight: "24px",
                                color: "#262626"
                            }}
                        >
                            {record.type}
                            <br></br>
                            {record.name}
                        </Text>
                        <Text
                            style={{
                                fontSize: "12px",
                                fontWeight: "300",
                                fontStyle: "normal",
                                lineHeight: "18px",
                                color: "#262626"
                            }}
                        >
                            {`Last updated `}
                            <Tooltip title={moment().format("YYYY-MM-DD HH:mm:ss")}>
                                <span>{moment(record.updatedAt).fromNow()}</span>
                            </Tooltip>
                            {` by ${record.username}`}

                        </Text>
                    </Space>
                </List.Item>
            ),
            ...tableColumnTextFilterConfig<any>(),
            onFilter: (value: any, record: any) => record.content[record.content.length - 1].title.toLowerCase().indexOf(value.toLowerCase()) !== -1,
        },
    ]

    const onSelectChange = (newSelectedRowKeys: React.Key[], newSelectedRows: JobAssetType[]) => {
        setSelectedRowKeys(newSelectedRowKeys);
        setselectedRows(newSelectedRows)
    };

    const rowSelection = {
        selectedRowKeys,
        onChange: onSelectChange,
    };

    const start = () => {
        if (selectedRows.length > 0) {
            selectedRows.forEach((item: JobAssetType) => {
                if (item.JobTrainee.indexOf(traineeJobID) === -1) {
                    item.JobTrainee.push(traineeJobID);
                    editJobAsset({
                        variables: {
                            id: item.id,
                            jobTrainees: item.JobTrainee
                        },

                    })
                }
            })
            setSelectedRowKeys([])
            setselectedRows([])
        }
    };

    const hasSelected = selectedRowKeys.length > 0;

    return (
        <Spin spinning={loading} >
            {hasSelected && <div style={{ marginBottom: 16 }}>
                <Button type="primary" onClick={start} disabled={!hasSelected} >
                    Add
                </Button>
                <span style={{ marginLeft: 8 }}>
                    {hasSelected ? ` ${selectedRowKeys.length} job application materials to this job ` : ''}
                </span>
            </div>}
            <Table
                rowSelection={{
                    ...rowSelection,
                }}
                pagination={{
                    onChange(current, pageSize) {
                        setPage(current);
                        setPaginationSize(pageSize)
                    },
                    defaultPageSize: 25, hideOnSinglePage: true, showSizeChanger: true
                }}
                columns={AssetColumns} dataSource={loadAssetData()}
            />
        </Spin>
    )
}
