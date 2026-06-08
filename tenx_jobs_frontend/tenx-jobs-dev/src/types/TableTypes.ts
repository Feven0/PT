import type { ColumnsType } from "antd/es/table";
import React from "react";
import type { MenuProps } from "antd";

export type download = {
  downloadPermission?: boolean;
  fileName?: string;
  columnPicker?: boolean;
};

export type Filter = {
  items: MenuProps;
  placement:
    | "bottomLeft"
    | "bottomCenter"
    | "bottomRight"
    | "topLeft"
    | "topCenter"
    | "topRight";
  overlayClassName?: string;
  overlayStyle?: React.CSSProperties;
  trigger?: ("click" | "hover")[];
  open?: boolean;
  onVisibleChange?: (visible: boolean) => void;
  disabled?: boolean;
  align?: object;
  getPopupContainer?: (triggerNode: HTMLElement) => HTMLElement;
  arrow?: boolean;
  onOpenChange?: (open: boolean) => void;
  name: string;
  icon?: React.ReactNode;
  autoFocus?: boolean;
};

export type button = {
  name?: string | JSX.Element | React.ReactNode;
  icon?: React.ReactNode;
  type?: string;
  onClick: (...args: any[]) => void;
  disabled?: boolean;
  loading?: boolean;
  style?: object;
  className?: string;
  danger?: boolean;
  ghost?: boolean;
  size?: "small" | "middle" | "large";
  block?: boolean;
  htmlType?: "button" | "submit" | "reset";
  href?: string;
  target?: string;
  shape?: "circle" | "round";
};

export type dropDown = {
  arrow?: boolean;
  autoAdjustOverflow?: boolean;
  autoFocus: boolean;
  disabled?: boolean;
  destroyPopupOnHide?: boolean;
  getPopupContainer?: (triggerNode: HTMLElement) => HTMLElement;
  dropdownRender?: (menu: React.ReactNode) => React.ReactNode;
  menu: MenuProps;
  overlayClassName?: string;
  overlayStyle?: React.CSSProperties;
  placement:
    | "bottomLeft"
    | "bottomCenter"
    | "bottomRight"
    | "topLeft"
    | "topCenter"
    | "bottom"
    | "topRight";
  trigger?: ("click" | "hover")[];
  onOpenChange?: (open: boolean) => void;
  icon?: React.ReactNode;
  name: string | JSX.Element | React.ReactNode;
};

export type pagination = {
  paginationSize?: number; // we need it
  setPaginationSize?: (size: number) => void; // we need it
  showSizeChanger?: boolean;
  pagination?: number; //unused we don't need it
  current?: number; // we need it
  total?: number; // we need it
  onChange?: (page: number, pageSize?: number) => void; // we don't need it
};

export type search = {
  searchPermission: boolean;
};

export type Switch = {
  autoFocus?: boolean;
  loading?: boolean;
  disabled?: boolean;
  checked: boolean;
  className?: string;
  defaultChecked?: boolean;
  size?: "default" | "small";
  value?: boolean;
  style?: object;
  unCheckedChildren?: React.ReactNode;
  checkedChildren?: React.ReactNode;
  onChange: (...args: unknown[]) => void;
  onClick?: (...args: unknown[]) => void;
};

export type tableProps = {
  dataSource: object[];
  columns: ColumnsType<object>;
  size?: "small" | "middle" | "large";
  counterName: string;
  allowEditColumn: boolean;
  allowRowSelection: boolean;
  rowSelectionTypeRadio?: boolean;
  onChange?: (...args: any[]) => void;
  buttons?: button[];
  dropDown?: dropDown[];
  bordered?: boolean;
  switchComp?: Switch;
  expandable?: object;
  pagination: pagination;
  email?: boolean;
  filter?: Filter;
  setSelectedParentRows?: (selectedRows: object[]) => void;
  scroll?: object;
  onRow?: (
    record: unknown,
    index?: number
  ) => React.HTMLAttributes<HTMLElement>;
  rowClassName?: (record: any, index: any) => string;
};

export type TableTypes = {
  download?: download;
  search: search;
  loading?: boolean;
} & tableProps;

export type emailsType = {
  name: string;
  email: string;
};

export type TableSliceTypes = {
  selectedRowKeys: string[];
  selectedRows: any[];
  emails: { name: string; email: string }[];
  failedReport: { name: string; email: string; status: string }[];
  successReport: { name: string; email: string; status: string }[];
  printData: {
    to: string;
    cc: string;
    sender: string;
    subject: string;
    body: string;
    sentCount: number;
    failedCount: number;
  };
};

export type reportType = {
  name: string;
  email: string;
  status: string;
};

export type ColumnDisplayOption = {
  device: string;
  show: boolean;
};

export type FilterOption = {
  name: string;
  value: string;
};

export type TFilter = {
  options: FilterOption[];
};

export type Icon = {
  type: string;
  source?: string;
  icon?: string;
};

export type TColumn = {
  name: string;
  key: string;
  title: string;
  sorting?: boolean;
  has_filter?: boolean;
  has_icon?: boolean;
  dataIndex: string;
  icon?: Icon;
  type: {
    name: string;
    format?: string;
    source?: string;
  };
  show: ColumnDisplayOption;
  filter?: TFilter;
  render?: (value: any, record: any) => React.ReactNode;
};
