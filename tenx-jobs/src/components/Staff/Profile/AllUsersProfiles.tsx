import { Avatar, Space } from "antd";
import { IoIosLink } from 'react-icons/io';
import { DownloadOutlined, ExpandAltOutlined } from "@ant-design/icons";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import ServerError from "../../../components/commonComponents/ServerError";

//Redux and custom hooks
import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { TableTypes } from "../../../types/TableTypes";
import { setTraineeInfo } from "../../../redux/slices/traineeInfoSetByStaffsSlice";
import useRenderTableCell from "../../../hooks/useRenderTableCell";

//Utils
import { rowClassName } from "../../../utils/rowClassname";
import { ensureURLProtocol } from "../../../utils/isUrl";
import StaffDataLoader from "../../commonComponents/StaffDataLoader";
import useAxiosRequest from "../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../utils/getRunStage";
import { TableParams } from "../Engagement/EngagedJobs";
import TableExtensionCursor from "../../../libs/DataTables/TableExtensionCursor";

const run_stage = getRunStage();

export default function AllUsersProfiles() {
  const [response, setResponse] = useState<any>(null);
  const [tableParams, setTableParams] = useState<TableParams>({
    pagination: {
      current: 1,
      pageSize: 10,
    },
  });

  const { allUserId, user_role } = useAppSelector((state) => state.leapProfileId)
  const { batch } = useAppSelector((state) => state.user)

  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { makeRequest, error, loading } = useAxiosRequest(); 
  const renderTableCell = useRenderTableCell();

  const getUserProfile = () => {
    makeRequest({
      url: '/sjob/get-all-user-profiles',
      method: "POST",
      data: {
        user_role: user_role,
        run_stage: run_stage,
        all_user_id: allUserId,
        batch: batch,
        limit: response?.cursor?.total || 10,
        filter: {},
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
        if (response?.data) {
          setResponse(response.data);
        }
      },
      onError: () => {}
    });
  };
  
  useEffect(() => {
    getUserProfile()
  }, [tableParams.pagination?.current, tableParams.pagination?.pageSize, batch])

  const handleRedirection = (record: any) => {
    dispatch(setTraineeInfo({
      name: record.name,
      email: record.email,
    }));
    const url = `/staff/trainee_details/${record.all_user_id}/${record.trainee_id}/${record.user_profile_id}`;
    navigate(url)
  }

  const renderIcon = (icon: { type: string, source: string, icon: string }, data: string, record: any) => {
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
          return (
            <span className="dark-orange-color cursor-pointer" onClick={() => handleRedirection(record)}>
              <ExpandAltOutlined />
            </span>
          );
        }
        else if (icon.icon === 'link') {
          return (
            <a href={ensureURLProtocol(data)} rel="noreferrer" target="_blank">
              <IoIosLink />
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

  const columns = response?.user_profiles[0]?.columns
    .filter((column: any) => {
      return !['user_profile_id', 'job_profile_id', 'all_user_id'].includes(column.name);
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

  const dataSourceWithKeys = response?.user_profiles[0]?.data.map((item: any, index: number) => ({
    ...item,
    key: index.toString(),
  }));


  const TableProp: TableTypes = {
    dataSource: dataSourceWithKeys,
    counterName: response?.user_profiles[0]?.counterName,
    columns: columns,
    size: "small",
    bordered: false,
    scroll: { x: 768 },
    allowEditColumn: true,
    onChange: handleTableChange,
    loading: loading,
    allowRowSelection: true,
    rowClassName: rowClassName,
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
  };

  if (error) return <ServerError />
  if (!response) return <StaffDataLoader/>

  return (
    <>
        { 
            response &&  <TableExtensionCursor {...TableProp} />
 
        }
    </>
  )
}