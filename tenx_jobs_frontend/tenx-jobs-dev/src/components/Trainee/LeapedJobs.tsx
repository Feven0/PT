import { Col, Row, Space, Tooltip } from "antd";
import {useEffect, useState } from "react";
import { ReloadOutlined, DownOutlined } from "@ant-design/icons";

//Components
import ServerError from "../commonComponents/ServerError";
import { TableParams } from "../Staff/Engagement/EngagedJobs";
import StaffDataLoader from "../commonComponents/StaffDataLoader";

//Redux and custom hooks
import { useAppSelector } from "../../redux/hooks/hooks";
import useRenderTableCell from "../../hooks/useRenderTableCell";
import useRenderIcon from "../../hooks/useRenderIcon";
import useFilterAndPagination from "../../hooks/userFilterAndPagination";
import useAxiosRequest from "../../hooks/useAxiosRequest";

//Utility functions
import { rowClassName } from "../../utils/rowClassname";
import { TableTypes } from "../../types/TableTypes";
import TableExtensionCursor from "../../libs/DataTables/TableExtensionCursor";
import { DEFAULT_SINCE_DAYS } from "./Liked";
import { getRunStage } from "../../utils/getRunStage";

const run_stage = getRunStage();

export default function LeapedJobs() {
  const [response, setResponse] = useState<any>(null);
  const [tableParams, setTableParams] = useState<TableParams>({
    pagination: {
      current: 1,
      pageSize: 10,
    },
  }); 
  const { allUserId, user_role, batch, user_profile_id } = useAppSelector((state) => state.leapProfileId); 
  const {filter, days} = useAppSelector((state) => state.updateSince);
  
  const { makeRequest, loading, error } = useAxiosRequest();
  const renderIcon = useRenderIcon();
  const renderTableCell = useRenderTableCell();

  const sendResult = (since = days || DEFAULT_SINCE_DAYS) => {
    const data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      limit: response?.cursor?.total || 10,
      since: since,
      information_level: "minimal",
      filters: {},
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
      url: '/sjob/get-all-user-leaps',
      method: 'POST',
      data,
      onSuccess: (response) => {
       if(response.status === 200){
        setResponse(response.data);
       }
      },
      onError: () => {},
    });
  };

  useEffect(() => {
    sendResult()
  }, [tableParams?.pagination?.current, tableParams?.pagination?.pageSize, filter, days, batch, allUserId, user_profile_id]);
  
  const {
    handleTodayChange,
    handleLast7Change,
    handleFetchLast15Days,
    handleFetchLastMonth,
    handleFetchLast3Months,
  } = useFilterAndPagination(setTableParams, sendResult);

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

  const columns = response?.leaps[0]?.columns
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
      value: option.value
    })) : undefined,
    onFilter: column.onFilter,
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

  const dataSourceWithKeys = response?.leaps[0]?.data.map((item: any, index: number) => ({
    ...item,
    key: index.toString(),
  }))

  const handleRefetch = () => sendResult();

  const TableProp: TableTypes = {
    dataSource: dataSourceWithKeys,
    counterName: response?.leaps[0]?.counterName,
    columns: columns,
    size: "small",
    bordered: false,
    scroll: { x: 768 },
    loading: loading,
    allowEditColumn: true,
    allowRowSelection: false,
    onChange: handleTableChange,
    rowClassName: rowClassName,
    dropDown: [
      {
        autoFocus: false,
        placement: "bottom",
        name: <div className="flex-center gap-8"><p>{filter ? filter : "Last 7 days"}</p><DownOutlined/></div>,
        menu: {
          items: [
            {
              key: "today",
              label: "Today",
              onClick: () => { handleTodayChange() },
            },
            {
              key: "last_7_days",
              label: "Last 7 days",
              onClick: () => { handleLast7Change() },
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
    search: {
      searchPermission: true,
    },
    buttons: [
      {
        type: "link",
        icon: <Tooltip title="Refetch"><ReloadOutlined /></Tooltip>,
        onClick: () => {
          handleRefetch();
        },
      },
    ],
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
  };

  if (error) return <ServerError />
  if(!response) return <StaffDataLoader/>

  return (
    <Row gutter={16} justify="center">
      {response?.leaps?.length > 0 && 
        <Col span={24} className="leaped-jobs-container-column">
            <TableExtensionCursor {...TableProp} />
        </Col>
        }
    </Row>
  );
}
