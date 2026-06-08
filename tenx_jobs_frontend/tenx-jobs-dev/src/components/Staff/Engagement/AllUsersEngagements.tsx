import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { IoIosLink } from "react-icons/io";
import { DownloadOutlined, ExpandAltOutlined } from "@ant-design/icons";
import { useAppSelector, useAppDispatch } from "../../../redux/hooks/hooks"
import { Avatar, Space } from "antd";
import type { GetProp, TableProps } from 'antd';

import ServerError from "../../commonComponents/ServerError";

//Redux and custom hooks
import { TableTypes } from "../../../types/TableTypes";
import { setTraineeInfo } from "../../../redux/slices/traineeInfoSetByStaffsSlice";
import useRenderTableCell from "../../../hooks/useRenderTableCell";
import { setReactionId, setTraineeId } from '../../../redux/slices/staff/IdListsSlice';

//Utils
import TableExtensionCursor from "../../../libs/DataTables/TableExtensionCursor";
import { rowClassName } from "../../../utils/rowClassname";
import { ensureURLProtocol } from "../../../utils/isUrl";
import StaffDataLoader from "../../commonComponents/StaffDataLoader";
import NoDetails from "../../commonComponents/NoDetails";
import useAxiosRequest from "../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../utils/getRunStage";

type TablePaginationConfig = Exclude<GetProp<TableProps, 'pagination'>, boolean>;
interface TableParams {
  pagination?: TablePaginationConfig;
}

export default function AllUsersEngagements() {
  const [tableParams, setTableParams] = useState<TableParams>({
    pagination: {
      current: 1,
      pageSize: 10,
    },
  });
  const [response, setResponse] = useState<any>(null);
  const { user_role } = useAppSelector((state) => state.leapProfileId)
  const { batch, allUserId } = useAppSelector((state) => state.user)
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const renderTableCell = useRenderTableCell();
  const { makeRequest, loading, error } = useAxiosRequest();

  const getAllUserEngagements = (prop: any = {}) => {
    if (batch) {
      makeRequest({
        url: '/sjob/get-admin-reaction-profiles',
        method: "POST",
        data: {
          user_role: user_role,
          run_stage: getRunStage(),
          all_user_id: allUserId,
          batch: batch,
          limit: 0,
          filter: {},
          cursor: {
            page: prop.page || 1,
            pageSize: prop.pageSize || 10,
            page_size: prop.page_size || 10,
            page_count: prop.page_count || 1,
            total: prop.total || 0,
            filter: prop.filter || {},
            query: prop.query || {}
          }
        },
        onSuccess: (response) => {
          if (response?.data) {
            setResponse(response.data);
          }
        },
        onError: () => {}
      });
    }
  };

  useEffect(() => {
    getAllUserEngagements()
  }, [batch])

  const handleRedirection = (record: any) => {
    dispatch(setTraineeId(record.trainee_id));
    dispatch(setTraineeInfo({
      name: record.name,
      email: record.email,
    }));
    const url = `/staff/trainee_engagements/${record.all_user_id}/${record.user_profile_id}`;
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

  const columns = response?.user_profiles[0]?.columns
    .filter((column: any) => {
      return !['user_profile_id', 'trainee_id', 'all_user_id', 'batch', 'created_at', 'updated_at'].includes(column.name);
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

  const totalPage = response?.cursor?.total

  const handleTableChange = (pagination: any) => {
    getAllUserEngagements({
      page: pagination.current,
      pageSize: pagination.pageSize,
      page_size: pagination.pageSize,
      limit: pagination.pageSize,
      page_count: pagination.current,
      total: totalPage,
      filter: response?.cursor?.filter,
      query: response?.cursor?.query
    });

    setTableParams((prevParams) => ({
      ...prevParams,
      pagination: {
        ...prevParams.pagination,
        current: pagination.current,
        pageSize: pagination.pageSize,
      },
    }));
  }

  useEffect(() => {
    if (response) {
      const engagement_list = response.user_profiles[0]?.data.reduce((acc: any, curr: any) => {
        acc[curr.name] = {
          all_user_id: curr.all_user_id,
          user_profile_id: curr.user_profile_id,
          trainee_id: curr.trainee_id,
        }
        return acc;
      }, {});
      dispatch(setReactionId({ engagement_list }));
    }
  }, [response, dispatch]);

  const TableProp: TableTypes = {
    dataSource: dataSourceWithKeys,
    counterName: response?.user_profiles[0]?.counterName,
    columns: columns,
    loading: loading,
    size: "small",
    onChange: handleTableChange,
    bordered: false,
    scroll: { x: 768 },
    allowEditColumn: true,
    allowRowSelection: true,
    rowClassName: rowClassName,
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
  };

  if (error) return <ServerError />
  if (!response) return <StaffDataLoader/>
  if(!batch) return <NoDetails title="No data" description="No batch is selected so far" />

  return (
    <>
      {
        response && <TableExtensionCursor {...TableProp} />
      }
    </>
  )
}
