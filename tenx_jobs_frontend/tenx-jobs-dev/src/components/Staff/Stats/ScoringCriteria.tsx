import { Badge, Collapse, Table } from "antd";
import { useState } from "react";
import { DownOutlined } from "@ant-design/icons";
import { scoringCriteria } from "../../../utils/scoringStats";

function formatBin(value: number) {
  return value === Infinity ? "∞" : value;
}

function CriterionTable({ data }: { data: any }) {
  const columns = [
    {
      title: 'Bins',
      dataIndex: 'bins',
      render: (text: number, _record: any, index: number) => {
        if (index === data.bins.length - 2) {
          return `≥ ${formatBin(text)}`;
        } else if (index === data.bins.length - 1) {
          return null; 
        } else {
          return `${formatBin(text)} - ${formatBin(data.bins[index + 1])}`;
        }
      },
    },
    {
      title: 'Weights',
      dataIndex: 'weights',
      render: (text: number) => <span>{text}</span>,
    },
  ];

  const filteredData = data.bins.slice(0, data.bins.length - 1).map((bin:any, index:number) => ({
    key: index,
    bins: bin,
    weights: data.weights[index],
  }));

  return (
    <Table
      dataSource={filteredData}
      columns={columns}
      pagination={false} 
      rowKey="key" 
    />
  );
}
function NestedCriterionTable({ data }: { data: any }) {
  return (
    <>
      {Object.entries(data).map(
        ([subTitle, subData]: [string, any]) =>
          subTitle !== "criterion_weight" && (
            <div key={subTitle} className="mb-4">
              <h4 className="mb-2 font-semibold text-left">{subTitle}</h4>
              <CriterionTable data={subData} />
            </div>
          )
      )}
    </>
  );
}

const { Panel } = Collapse;

export default function ScoringCriteria() {
  const [openItems, setOpenItems] = useState<string[]>([Object.keys(scoringCriteria)[0]]);

  const handleAccordionChange = (key: string | string[]) => {
    const valueArray = Array.isArray(key) ? key : [key];
    setOpenItems(valueArray); 
  };

  return (
    <div className="container p-4 mx-auto mb-2 bg-white rounded-lg">
        <Collapse 
          activeKey={openItems} 
          onChange={handleAccordionChange} 
          accordion
          expandIconPosition="start"
          expandIcon={({ isActive }) => (
            <DownOutlined style={{ transition: '0.3s', transform: isActive ? 'rotate(180deg)' : 'rotate(0deg)' }} />
          )}
          >
          {Object.entries(scoringCriteria).map(([title, data]) => (
            <Panel
              header={
                <div className="full-width d-flex-between">
                  <span>{title}</span>
                  <Badge>{`Weight: ${data.criterion_weight}`}</Badge>
                </div>
              }
              key={title}
            >
              {title === 'Change_2' ? (
                <NestedCriterionTable data={data} />
              ) : (
                <CriterionTable data={data} />
              )}
            </Panel>
          ))}
        </Collapse>
  </div>
  )
}
