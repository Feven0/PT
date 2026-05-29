import { PrinterOutlined } from '@ant-design/icons';
import { useRef } from "react";
import { Drawer, Button, Row, Col } from "antd"
import moment from "moment-timezone";   
import { Tabs } from 'antd';
import type { TabsProps } from 'antd';
import ReactToPrint from 'react-to-print';
import TableExtension from "../DataTables/TableExtension"
import { TableTypes } from "../../types/TableTypes";
import TagComponent from "../../components/commonComponents/Tag";
import PrintEmail from "./PrintEmail";
import { useAppSelector } from "../../redux/hooks/hooks";

type ReportType = {
    viewReport: boolean
    onCloseReport: () => void;    
    resendEmails: () => void;
}
export default function ShowReport({viewReport, onCloseReport, resendEmails}: ReportType) {
  const { failedReport, successReport } = useAppSelector((state) => state.tableExtension);
  const componentRef = useRef(null);

    const columns = [
        {
            title: 'Name',
            dataIndex: 'name',
            key: 'name',
        },
        {
            title: 'Email',
            dataIndex: 'email',
            key: 'email',
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => (
                <TagComponent text={status} type={status === 'Sent' ? 'high1' : 'info11'} />
            ),
        },
    ];

    const sentTableProp: TableTypes = {
        dataSource: successReport,
        columns: columns,
        allowEditColumn: false,
        scroll: { x: 768, y: 1000 },
        allowRowSelection: false,
        size: "small",
        counterName: "Sent Email",
        email: false,
        search: {
          searchPermission: true,
        },        
        pagination: {
          showSizeChanger: true,
        },
        download: {
            downloadPermission: true,
            fileName: `Sent Email Report ${moment().format('YYYY-MM-DD')}`,
            columnPicker: true,
            },
      };

      const notSentTableProp: TableTypes = {
        dataSource: failedReport,
        columns: columns,
        allowEditColumn: false,
        scroll: { x: 768, y: 1000 },
        allowRowSelection: false,
        size: "small",
        counterName: "Failed Email",
        email: false,
        search: {
          searchPermission: true,
        },
        pagination: {
          showSizeChanger: true,
        },
        download: {
            downloadPermission: true,
            columnPicker: true,
            fileName: `Failed Email Report ${moment().format('YYYY-MM-DD')}`
            },
      };

    const items: TabsProps['items'] = [
        {
          key: '1',
          label: 'Sent',
          children: <TableExtension  {...sentTableProp}/>,
        },
        {
          key: '2',
          label: 'Not Sent',
          children: (
            <>
            <Row className="data-table-header-row"  >
     
            { failedReport.length > 0 &&
                <Button 
                style={{ background: "#FF4405", color: "#FFF", marginRight: '10px'}}
                onClick={resendEmails}
                >Resend Email 
                </Button> 
            } 
            </Row>
                <TableExtension {...notSentTableProp}/>
            </>
          ),
        }
      ];

    return (
      <>    
        <Drawer
          title={
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span>Email Report</span>
              <span className="d-flex" style={{ gap: "0.5rem", alignItems: 'center' }}>
                <ReactToPrint
                  bodyClass="print-body"
                  trigger={() => <PrinterOutlined />}
                  content={() => componentRef.current}
                  documentTitle={`Email Report ${moment().format('YYYY-MM-DD')}`}
                />
              </span>
            </div>
          }
          width={720}
          onClose={onCloseReport}
          open={viewReport}
          styles={{
          body: {
              paddingBottom: 80,
          },
          }}
      >
      <Tabs defaultActiveKey="1" items={items} />    
      </Drawer>
      <Row style={{ display: "none" }}>
        <Col ref={componentRef} className="PrintSection">
            <PrintEmail />
        </Col>
      </Row>
    </>

  )
}
