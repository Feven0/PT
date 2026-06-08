import { useMediaQuery } from "react-responsive";
import { Dropdown } from 'antd';
import { Table } from 'ant-table-extensions';
import React, { useState, useEffect } from 'react'
import type { ColumnsType, TableProps } from 'antd/es/table';
import { Button, Switch , Row, Typography} from 'antd';
import { EditOutlined, MailOutlined,SearchOutlined,DownOutlined,  DownloadOutlined } from '@ant-design/icons';
import { download, emailsType, search, tableProps } from '../../types/TableTypes'
import { getSingularPluralString } from '../../utils/getSingularPluralString';
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import ColumnEditModal from "./ColumnEditModal";
import { resetTableExtension, setEmails, setTableExtension } from "../../redux/slices/tableExtension";
import Email from "../Email/Email";

import '../../App.css';
const { Paragraph } = Typography;

type CustomColumnType<T> = ColumnsType<T> & {
  show?: {
      mobile?: boolean;
      tablet?: boolean;
      desktop?: boolean;
  } | undefined;
};

type AntdTableProps<T> = TableProps<T> & {
  columns: ColumnsType<T>;
  download?: download;
  search: search; 
  pages?: number;
  loading?: boolean;    
} & tableProps;
Table

  export default function TableExtensionCursor<T extends object>(props: AntdTableProps<T>) {
    const dispatch = useAppDispatch();

    const { dataSource, columns, expandable, allowEditColumn, onChange,
            onRow, allowRowSelection,rowSelectionTypeRadio, bordered, counterName,filter, 
            buttons, dropDown, switchComp, email, scroll, rowClassName, setSelectedParentRows, loading
        } = props;
    const { downloadPermission, fileName, columnPicker } = props.download ?? {};
    const { showSizeChanger, paginationSize, total, current } = props.pagination;
    const { searchPermission } = props.search;
    const { selectedRows, selectedRowKeys } = useAppSelector((state) => state.tableExtension);
    const [searchedDataLength, setSearchedDataLength] = useState<number>(0);
    const [visibleModal, setVisibleModal] = useState<boolean>(false);
    const [filterColumns, setFilterColumns] = useState<CustomColumnType<T>>(columns);
    const [visible, setVisible] = useState(false);

    const isMobile = useMediaQuery({ query: '(max-width: 767px)' });
    const isTablet = useMediaQuery({ query: '(min-width: 768px) and (max-width: 991px)' });
    const isDesktop = useMediaQuery({ query: '(min-width: 992px)' });

    useEffect(() => {
      dispatch(setTableExtension({ selectedRowKeys: [], selectedRows: []}));
    },[]);

    const showDrawer = () => {
      const uniqueEmailsSet = new Set(selectedRows.map((row: emailsType) => ({ name: row.name, email: row.email })));      
      const uniqueEmailsArray: emailsType[] = Array.from(uniqueEmailsSet) as emailsType[];
      dispatch(setEmails(uniqueEmailsArray));    
      dispatch(setTableExtension({ failedReport: [], successReport:[] }));
      setVisible(true);
    };
  
    const onClose = () => setVisible(false);
    const showModal = () => setVisibleModal(true);

    const onSelectChange = (selectedKeys: React.Key[]) => {
      const updatedSelectedRows = (dataSource as { key: string }[]).filter((row) => selectedKeys.includes(row.key));
      dispatch(setTableExtension({ selectedRowKeys: selectedKeys as string[], selectedRows: updatedSelectedRows }))
      setSelectedParentRows && setSelectedParentRows(updatedSelectedRows);
    };

    const handleSearchFunction = (data: any[], searchText: string) => {
      const lowerCasedSearchText = searchText.toLowerCase().trim();
      
      const filteredData = data.filter((item: any) => {
          return Object.values(item).some((columnValue: any) =>
              columnValue && columnValue.toString().toLowerCase().includes(lowerCasedSearchText)
          );
      });
  
      setSearchedDataLength(filteredData.length);
      return filteredData;
  };
   
  const handleColumnsShowChange = (showColumns: string[]): void => {
    setFilterColumns((prevColumns) =>
        prevColumns.map((column:any) => {
            if ('dataIndex' in column && typeof column.dataIndex === 'string') {
                return {
                    ...column,
                    show: {
                        ...column.show,
                        mobile: showColumns.includes(column.dataIndex),
                        tablet: showColumns.includes(column.dataIndex),
                        desktop: showColumns.includes(column.dataIndex),
                    },
                };
            }
            return column;
        })
    );
  };

    const rowSelection = {
      columnWidth: '5%',
      selectedRowKeys,
      onChange: onSelectChange,
      type: rowSelectionTypeRadio ? "radio" : "checkbox",
      selections: [
        {
          key: 'all-data',
          text: 'Select All Data',
          onSelect: () => {
            dispatch(setTableExtension({ selectedRowKeys: dataSource?.map((row) => (row as any).key), selectedRows: dataSource }));
            setSelectedParentRows && setSelectedParentRows(dataSource);
          },
        },
        {
          key: 'clear',
          text: 'Clear All',
          onSelect: () => {
            dispatch(resetTableExtension());
            setSelectedParentRows && setSelectedParentRows([]);
          },
        },
      ],
    };

    const handleEmailButtonClick = () => showDrawer();

    const filteredColumns = (filterColumns ?? []).filter(column => { 
      const showConfig = (column as CustomColumnType<T>).show;
      if (isMobile && showConfig?.mobile === false) return false;
      if (isTablet && showConfig?.tablet === false) return false;
      if (isDesktop && showConfig?.desktop === false) return false;
      return true;
  });

    const tableProps = {
      dataSource: dataSource,
      columns: [
        {
          title: '#',
          key: 'index',
          width: "7%",
          render: (_text: string, _record: any, index: number) => {
            return (((current ?? 1) - 1) * (paginationSize ?? 10)) + index + 1;
          },
        },      
      ...filteredColumns
      ],
      rowSelection: allowRowSelection && rowSelection,
      expandable: expandable,
      bordered: bordered || false,
      rowClassName: rowClassName,
      onChange: onChange,
      loading: loading,
      onRow:onRow,
      scroll: scroll, 
      pagination: {
        defaultPageSize: paginationSize || 10,
        hideOnSinglePage: true,
        total: total,
        current: current,
        showSizeChanger: showSizeChanger,
      },      
      ...(searchPermission && {
        searchable: true,
        searchableProps: {
          inputProps: {
            placeholder: 'Search here',
            suffix: <SearchOutlined/>,
            style: {
              width: '25%',
            }
          },
          searchFunction: handleSearchFunction,

        },
      }),
      ...(downloadPermission && {
        exportable: true,
        exportableProps: {
          dataSource: dataSource,
          fileName: fileName,
          showColumnPicker: columnPicker,
          children: '',
          btnProps: {
            icon: <DownloadOutlined />,
            
            style: {
              border: 'none',
            }
          },
         
        },
      }),
    };

    return (
      <>
      <Row className="data-table-header-row">
        <Paragraph style={{ marginRight: '10px', marginTop: "0.1rem"}}>
          {
            (selectedRowKeys.length > 0
              ? getSingularPluralString(selectedRowKeys.length, counterName)
              : searchedDataLength > 0 ? getSingularPluralString(searchedDataLength, counterName)
              : getSingularPluralString(total ?? 0, counterName))
            }
        </Paragraph>
     
      { email &&
        <Button 
          type="text" 
          icon={<MailOutlined />} 
          onClick={handleEmailButtonClick }
        /> 
      } 
      {
        allowEditColumn && (
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={showModal}
          />
        )
      }
      <div style={{display: "flex", gap: "0.5rem"}}>
        {
          buttons && buttons.map((button, index) => {
            return (
              <Button 
                key={index} 
                icon={button.icon && button.icon}
                onClick={button.onClick && button.onClick}
                disabled= {button.disabled && button.disabled}
                loading= {button.loading && button.loading}
                style={button.style ? { ...button.style, border: 'none' } : { border: 'none' }}
                className= {button.className && button.className}
                danger= {button.danger && button.danger}
                ghost= {button.ghost && button.ghost}
                size= {button.size && button.size}
                block= {button.block && button.block}
                htmlType= {button.htmlType && button.htmlType}
                href= {button.href && button.href}
                target= {button.target && button.target}
                shape= {button.shape && button.shape}
              >
                {button.name && button.name}
              </Button>
            )
          })
        }
        {
          dropDown && dropDown.map((dropDown, index) => {
            return (
              <Dropdown
                key={index}
                arrow={dropDown.arrow && dropDown.arrow}
                autoAdjustOverflow={dropDown.autoAdjustOverflow && dropDown.autoAdjustOverflow}
                autoFocus={dropDown.autoFocus && dropDown.autoFocus}
                disabled={dropDown.disabled && dropDown.disabled}
                destroyPopupOnHide={dropDown.destroyPopupOnHide && dropDown.destroyPopupOnHide}
                getPopupContainer={dropDown.getPopupContainer && dropDown.getPopupContainer}
                dropdownRender={dropDown.dropdownRender && dropDown.dropdownRender}
                menu={dropDown.menu}
                overlayClassName={dropDown.overlayClassName && dropDown.overlayClassName}
                overlayStyle={dropDown.overlayStyle && dropDown.overlayStyle}
                placement={dropDown.placement && dropDown.placement}
                trigger={dropDown.trigger && dropDown.trigger}
                onOpenChange={dropDown.onOpenChange && dropDown.onOpenChange}
              >
                <Button
                  type="text"
                  icon={dropDown.icon && dropDown.icon}
                  style={{ border: 'none' }}
                >
                  {dropDown.name && dropDown.name}
                </Button>
              </Dropdown>
            )
          })
        }
        {
          switchComp && (
            <Switch 
              autoFocus={ switchComp.autoFocus && switchComp.autoFocus}
              loading={switchComp.loading && switchComp.loading}
              disabled={switchComp.disabled && switchComp.disabled}
              checked={switchComp.checked}
              className={switchComp.className && switchComp.className}
              defaultChecked={switchComp.defaultChecked && switchComp.defaultChecked}
              size={switchComp.size && switchComp.size}
              value={switchComp.value && switchComp.value}
              unCheckedChildren={switchComp.unCheckedChildren}
              checkedChildren={switchComp.checkedChildren}
              style={switchComp.style && switchComp.style}
              onChange={switchComp.onChange}
              onClick={switchComp.onClick && switchComp.onClick}
            />
          )
        }
        </div>

      </Row>
      <Row style={{float: 'right', marginLeft: "0.5rem"}}>
        {
          filter && (
            <Dropdown 
              menu={filter?.items} trigger={filter?.trigger}>
              <a onClick={(e) => e.preventDefault()}>
                <div style={{
                      display: "flex",
                      gap: "0.3rem", 
                      marginLeft:"0.5rem", 
                      width:"8%", 
                      fontSize: "0.9rem", 
                      color: "rgba(0, 0, 0, 0.88))"}}>
                  Filter
                  <DownOutlined />
                </div>
              </a>
            </Dropdown>
          )
        }
      
      </Row>
      { allowEditColumn && (
        <ColumnEditModal
          visible={visibleModal}
          onCloseModal={() => setVisibleModal(false)}
          columns={columns}
          onChangeColumns={handleColumnsShowChange}
        />
      )}

        <Email
          onSelectChange={onSelectChange} 
          visible={visible} 
          onClose={onClose} 
        />
        
      <Table {...tableProps} />
      </>
    );
  }
