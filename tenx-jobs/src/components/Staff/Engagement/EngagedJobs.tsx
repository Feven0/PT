import { useEffect, useState } from 'react';
import { DownloadOutlined, ExpandAltOutlined, ReloadOutlined, DownOutlined } from '@ant-design/icons';
import { IoIosLink } from "react-icons/io";
import { Link, useParams } from 'react-router-dom';
import type { GetProp, TableProps } from 'antd';
import { Row, Col, Modal, Space, Avatar, Tooltip } from 'antd';

import ApplyStatusForm from './ApplyStatusForm';
import ServerError from '../../commonComponents/ServerError';
import { useAppSelector, useAppDispatch } from '../../../redux/hooks/hooks';
import { setReactionId } from '../../../redux/slices/staff/IdListsSlice';
import useEngagementTableCellRender from '../../../hooks/useEngagementTableCellRender';
import { TableTypes } from '../../../types/TableTypes';
import { rowClassName } from '../../../utils/rowClassname';
import TableExtensionCursor from '../../../libs/DataTables/TableExtensionCursor';
import { DEFAULT_SINCE_DAYS } from "../../Trainee/Liked";
import useFilterAndPagination from "../../../hooks/userFilterAndPagination";
import StaffDataLoader from "../../commonComponents/StaffDataLoader";
import { setEngagementsStats } from "../../../redux/slices/userStatsSlice";
import useAxiosRequest from "../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../utils/getRunStage";

type TablePaginationConfig = Exclude<GetProp<TableProps, 'pagination'>, boolean>;
export type TableParams= {
  pagination?: TablePaginationConfig;
}

export default function EngagedJobs() {
  const { all_user_id, user_profile_id } = useParams()
  const [applyStatusFormVisible, setApplyStatusFormVisible] = useState(false);
  const [response, setResponse] = useState<any>(null);

  const dispatch = useAppDispatch();
  const { selectedRows } = useAppSelector((state) => state.tableExtension);
  const [tableParams, setTableParams] = useState<TableParams>({
    pagination: {
      current: 1,
      pageSize: 10,
    },
  });

  const {user_role } = useAppSelector((state) => state.leapProfileId)
  const {filter, days} = useAppSelector((state) => state.updateSince);
  const { batch } = useAppSelector((state) => state.user)

  const { renderTableCell } = useEngagementTableCellRender();

  const { makeRequest, loading, error } = useAxiosRequest();
  const getTraineeEngagements = (since = days || DEFAULT_SINCE_DAYS) => {
    const data = {
      user_role: user_role,
      run_stage: getRunStage(),
      all_user_id: all_user_id,
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
  
    makeRequest({
      url: '/sjob/get-all-user-reactions',
      method: 'POST',
      data,
      onSuccess: (response) => {
        if (response.status === 200) {
          setResponse(response.data);
        }
      },
      onError: () => {},
    });
  };

  useEffect(() => {
    getTraineeEngagements()
  }, [tableParams.pagination?.current, tableParams.pagination?.pageSize, filter, days, batch, all_user_id, user_profile_id]);

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

  const {
    handleTodayChange,
    handleLast7Change,
    handleFetchLast15Days,
    handleFetchLastMonth,
    handleFetchLast3Months,
  } = useFilterAndPagination(setTableParams, getTraineeEngagements);

  const renderIcon = (icon: { type: string, source: string, icon: string }, data: string, record: any) => {
    const dataSource = record[icon.source];
    switch (icon.type) {
      case 'with_text':
        if (icon.icon === 'first-letter') {
          return <Avatar size="small">{data.charAt(0).toUpperCase()}</Avatar>;
        }
        return data;
      case 'icon_only':
        if (icon.icon === 'download') {
          return <DownloadOutlined />;
        }
        else if (icon.icon === 'expand') {
          const url = `/staff/trainee_engagements/${all_user_id}/${user_profile_id}/${dataSource}`;
          return (
            <Link to={url}>
              <ExpandAltOutlined />
            </Link>
          );
        }
        else if (icon.icon === 'link') {
          return (
            <a href={data} target='_blank' className='' rel='noopener' style={{ cursor: 'pointer' }}>
              <IoIosLink className="dark-orange-color " />
            </a>
          );
        }
        return data;
      default:
        return data;
    }
  };

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
      filters: column.has_filter ? column.filter.options.map((option: any) => ({
        text: option.name,
        value: option.value,
      })) : undefined,
      onFilter: column.has_filter ? (value: string, record: any) => {
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
  }));

  useEffect(() => {
    if (response) {
      const reaction_id = response.reactions[0]?.data.reduce((acc: any, curr: any) => {
        acc[curr.user_reaction_id] = curr.job_title;
        return acc;
      }, {});
      dispatch(setReactionId({ reaction_id }));
    }
  }, [response, dispatch]);

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

  const TableProp: TableTypes = {
    dataSource: dataSourceWithKeys,
    counterName: response?.reactions[0]?.counterName,
    columns: columns,
    loading: loading,
    size: "small",
    bordered: false,
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
          ],
        },
      },
      {
        autoFocus: false,
        placement: "bottom",
        name: <div className="flex-center gap-8"><p>{filter ? filter : "Last 7 days"}</p><DownOutlined/></div>,
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
    ],

    search: {
      searchPermission: true,
    },
    pagination: {
      showSizeChanger: true,
      current: tableParams?.pagination?.current,
      paginationSize: tableParams?.pagination?.pageSize,
      setPaginationSize: (pageSize: number) => {
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

  const handleRefetch = () =>  getTraineeEngagements();

  if(!response) return <StaffDataLoader/>

  if (error || response?.status === 400) {
    return <ServerError />
  }

  return (
    <Row gutter={[16, 16]}>
      {
        response && (
          <>
            <Col span={24} className="liked-jobs-container-column">
              <TableExtensionCursor {...TableProp} />
            </Col>
          </>
        )
      }
      {
        applyStatusFormVisible && <ApplyStatusForm setVisible={setApplyStatusFormVisible} refetch={handleRefetch} />
      }
    </Row>
  )
}
