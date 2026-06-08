import { Col, Modal, Checkbox, Button, Input, Typography } from 'antd';
import { useState } from 'react';
import { useMediaQuery } from "react-responsive";

const { Text } = Typography;
type ColumnEditModalProps = {
  visible: boolean;
  onCloseModal: () => void;
  columns: any[];
  onChangeColumns: (showColumns: string[]) => void;
};

type CheckboxValueType = string | number | boolean;

export default function ColumnEditModal({visible, onCloseModal, columns, onChangeColumns}: ColumnEditModalProps) {

  const isMobile = useMediaQuery({ query: '(max-width: 767px)' });
  const isTablet = useMediaQuery({ query: '(min-width: 768px) and (max-width: 1024px)' });
  const isDesktop = useMediaQuery({ query: '(min-width: 1025px)' });

  const initialCheckedValues = columns?.filter((column) => {
        if (isMobile) {
            return column.show.mobile;
        } else if (isTablet) {
            return column.show.tablet;
        } else if (isDesktop) {
            return column.show.desktop;
        }
        return false;
    })
    .map((column) => column.dataIndex);

  const [checkedValues, setCheckedValues] = useState<CheckboxValueType[]>(initialCheckedValues);
  const [searchValue, setSearchValue] = useState<string>('');
  const ellipsis = true;

  const filteredColumns = columns?.filter((column) =>
    column?.title?.toLowerCase().includes(searchValue?.toLowerCase())
  );

  const onChange = (newCheckedValues: CheckboxValueType[]) => {
    setCheckedValues((prevCheckedValues) => {
      const filteredColumnsForSearch = filteredColumns.map((column) => column.dataIndex);

      const newlyCheckedValues = newCheckedValues.filter(
        (value) => !prevCheckedValues.includes(value) && filteredColumnsForSearch.includes(value)
      );

      const newlyUncheckedValues = prevCheckedValues.filter(
        (value) => !newCheckedValues.includes(value) && filteredColumnsForSearch.includes(value)
      );

      const updatedCheckedValues = [
        ...prevCheckedValues.filter((value) => !newlyUncheckedValues.includes(value)),
        ...newlyCheckedValues,
      ];
      onChangeColumns(updatedCheckedValues.map(String));
      return updatedCheckedValues;
    });
  };

  return (
    <Modal
      title="Edit Columns"
      open={visible}
      onCancel={onCloseModal}
      width={800}
      footer={[
        <Button key="back" onClick={onCloseModal}>
          Cancel
        </Button>,
      ]}
    >
      <Input
        placeholder="Search columns..."
        value={searchValue}
        onChange={(e) => setSearchValue(e.target.value)}
        style={{ marginBottom: 16 }}
      />
      {filteredColumns?.length > 0 ? (
        <Checkbox.Group className="d-flex flex-direction-column" style={{ width: '100%' }} onChange={onChange} value={checkedValues}>
          {filteredColumns.map((column: any) => (
            <Col span={20} key={column.dataIndex} style={{ overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
              <Checkbox value={column.dataIndex}>
                <Text
                  style={ellipsis ? { width: "30vw" } : undefined}
                  ellipsis={ellipsis ? { tooltip: column.title } : false}
                >
                  {column.title}
                </Text>
              </Checkbox>
            </Col>
          ))}
        </Checkbox.Group>
      ) : (
        <Col>
          <p>No columns found</p>
        </Col>
      )}
    </Modal>
  );
}
