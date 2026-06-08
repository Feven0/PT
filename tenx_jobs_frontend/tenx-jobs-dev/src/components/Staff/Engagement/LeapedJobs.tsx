import { Col,Modal, Row, Space, Tooltip } from "antd";
import {useEffect, useState } from "react";
import { ReloadOutlined, DownOutlined } from "@ant-design/icons";
import type { GetProp, TableProps } from 'antd'; 
import { useParams } from "react-router-dom";
//Components
import ServerError from "../../commonComponents/ServerError";
import StaffDataLoader from "../../commonComponents/StaffDataLoader";
import ApplyStatusForm from "./ApplyStatusForm";

//Redux and custom hooks
import { useAppSelector } from "../../../redux/hooks/hooks";
import useRenderTableCell from "../../../hooks/useRenderTableCell";
import useRenderIcon from "../../../hooks/useRenderIcon";
import useFilterAndPagination from "../../../hooks/userFilterAndPagination";
import useAxiosRequest from "../../../hooks/useAxiosRequest";

//Utility functions
import { rowClassName } from "../../../utils/rowClassname";
import { TableTypes } from "../../../types/TableTypes";
import TableExtensionCursor from "../../../libs/DataTables/TableExtensionCursor";
import { DEFAULT_SINCE_DAYS } from "../../Trainee/Liked";
import { getRunStage } from "../../../utils/getRunStage";

type TablePaginationConfig = Exclude<GetProp<TableProps, 'pagination'>, boolean>;
interface TableParams {
  pagination?: TablePaginationConfig;

}

const run_stage = getRunStage();

export default function Leaped() {
  const { all_user_id, user_profile_id } = useParams()
  const [response, setResponse] = useState<any>(null);

  const [tableParams, setTableParams] = useState<TableParams>({
    pagination: {
      current: 1,
      pageSize: 10,
    },
  });    const {selectedRows} = useAppSelector((state) => state.tableExtension);
  const [applyStatusFormVisible, setApplyStatusFormVisible] = useState(false);
  const { user_role } = useAppSelector((state) => state.leapProfileId); 
  const {filter, days} = useAppSelector((state) => state.updateSince);
  const renderIcon = useRenderIcon();
  const renderTableCell = useRenderTableCell();
  const { makeRequest, loading, error } = useAxiosRequest();

  const sendResult = (since = days || DEFAULT_SINCE_DAYS) => {
  
    makeRequest({
      url: '/sjob/get-all-user-leaps',
      method: 'POST',
      data: {
        all_user_id: all_user_id,
        limit: response?.cursor?.total || 10,
        since: since,
        information_level: 'minimal',
        run_stage: run_stage,
        user_role: user_role,
        cursor: {
          page: tableParams?.pagination?.current || 1,
          pageSize: tableParams?.pagination?.pageSize|| 10,
          page_size: tableParams?.pagination?.pageSize || 10,
          page_count: tableParams?.pagination?.current || 1,
          total: totalPage || 0,
          filter: response?.cursor?.filter || {},
          query: response?.cursor?.query || {}          
        }
      },
      onSuccess: (response) => {
        if (response?.status===200) {
          setResponse(response.data);
        }
      },
      onError: () => {},
    });
  };

  useEffect(() => {
    sendResult();
  }, [tableParams.pagination?.current, tableParams.pagination?.pageSize, filter, days, all_user_id, user_profile_id]);

  const {
    handleTodayChange,
    handleLast7Change,
    handleFetchLast15Days,
    handleFetchLastMonth,
    handleFetchLast3Months,
  } = useFilterAndPagination(setTableParams, sendResult);

  if (error || response?.status === 400) return <ServerError />;

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
  }));

  const handleRefetch = () => {
    sendResult();
  }

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


  const totalPage = response?.cursor?.total

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

  const TableProp: TableTypes = {
    dataSource: dataSourceWithKeys,
    counterName: response?.leaps[0]?.counterName,
    columns: columns,
    onChange: handleTableChange,
    size: "small",
    bordered: false,
    loading: loading,
    scroll: { x: 768 },
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

  if(!response) return <StaffDataLoader/>

  return (
    <Row gutter={16} justify="center">
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
      applyStatusFormVisible && <ApplyStatusForm setVisible={setApplyStatusFormVisible} refetch={handleRefetch}/>
    }
    </Row>
  );
}
