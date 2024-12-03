import { useState, useEffect, useRef } from 'react';
import { Table, Input, Select as AntSelect, Slider, Row, Col, Tag } from 'antd';
import Select from 'react-select'; 
import countries from 'world-countries'; 
const { Option } = AntSelect;

const AdminDashboard = ({ data = [] }) => {
  const [filters, setFilters] = useState<any>({
    name: '',
    batch: null,
    gender: '',
    nationality: '',
    role: '',
    scoreThreshold: null,
  });

  const [filteredDataCount, setFilteredDataCount] = useState<any>(data.length || 0); 
  const filteredDataRef = useRef<any>(data || []); 
  const [filteredData, setFilteredData] = useState<any>(data || []);

  const countryOptions = countries.map((country) => ({
    value: country?.cca2 || '', 
    label: country?.name?.common || '', 
  }));

  const applyFilters = (newFilters: any) => {
    // Ensure data is an array before proceeding
    let tempData = Array.isArray(data) ? [...data] : [];

    if (newFilters.name) {
      tempData = tempData.filter((item) =>
        item.name?.toLowerCase().includes(newFilters.name.toLowerCase())
      );
    }

    if (newFilters.batch) {
      tempData = tempData.filter((item) => item.batch === newFilters.batch);
    }

    if (newFilters.gender) {
      tempData = tempData.filter((item) => item.gender === newFilters.gender);
    }

    if (newFilters.nationality) {
      tempData = tempData.filter((item) =>
        item.nationality?.toLowerCase().includes(newFilters.nationality.toLowerCase())
      );
    }

    if (newFilters.role) {
      tempData = tempData.filter((item) => item.role === newFilters.role);
    }

    if (newFilters.scoreThreshold !== null) {
      tempData = tempData.filter((item) => item.score >= newFilters.scoreThreshold);
    }

    filteredDataRef.current = tempData;

    setFilteredData(tempData);
    setFilteredDataCount(tempData.length); 
  };

  const handleInputChange = (e: any) => {
    const { name, value } = e.target;
    setFilters((prevFilters: any) => {
      const newFilters = { ...prevFilters, [name]: value };
      applyFilters(newFilters); 
      return newFilters;
    });
  };

  const handleSelectChange = (name: any, value: any) => {
    setFilters((prevFilters: any) => {
      const newFilters = { ...prevFilters, [name]: value };

      Object.keys(newFilters).forEach((key) => {
        if (key !== name) {
          newFilters[key] = key === 'batch' ? null : ''; 
        }
      });

      applyFilters(newFilters); 
      return newFilters;
    });
  };

  const handleCountryChange = (selectedOption: any) => {
    setFilters((prevFilters: any) => {
      const newFilters = {
        ...prevFilters,
        nationality: selectedOption ? selectedOption.label : '',
      };

      Object.keys(newFilters).forEach((key) => {
        if (key !== 'nationality') {
          newFilters[key] = key === 'batch' ? null : ''; 
        }
      });

      applyFilters(newFilters); 
      return newFilters;
    });
  };

  const handleSliderChange = (value: any) => {
    setFilters((prevFilters: any) => {
      const newFilters = { ...prevFilters, scoreThreshold: value };

      Object.keys(newFilters).forEach((key) => {
        if (key !== 'scoreThreshold') {
          newFilters[key] = key === 'batch' ? null : ''; 
        }
      });

      applyFilters(newFilters);
      return newFilters;
    });
  };

  useEffect(() => {
    if (Array.isArray(data)) {
      applyFilters(filters); 
    } else {
      console.error('Expected data to be an array but got:', typeof data, data);
    }
  }, [data]); 

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Batch',
      dataIndex: 'batch',
      key: 'batch',
    },
    {
      title: 'Gender',
      dataIndex: 'gender',
      key: 'gender',
    },
    {
      title: 'Nationality',
      dataIndex: 'nationality',
      key: 'nationality',
    },
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
    },
    {
      title: 'Score',
      dataIndex: 'score',
      key: 'score',
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Input
            name="name"
            placeholder="Search by name"
            value={filters?.name || ''}
            onChange={handleInputChange}
          />
        </Col>
        <Col span={6}>
          <AntSelect
            placeholder="Select batch"
            value={filters?.batch || null}
            onChange={(value) => handleSelectChange('batch', value)}
            style={{ width: '100%' }}
          >
            {Array.from({ length: 10 }, (_, i) => (
              <Option key={i + 1} value={i + 1}>
                {i + 1}
              </Option>
            ))}
          </AntSelect>
        </Col>
        <Col span={6}>
          <AntSelect
            placeholder="Select gender"
            value={filters?.gender || null}
            onChange={(value) => handleSelectChange('gender', value)}
            style={{ width: '100%' }}
          >
            <Option value="Male">Male</Option>
            <Option value="Female">Female</Option>
          </AntSelect>
        </Col>
        <Col span={6}>
          <Select
            options={countryOptions || []}
            placeholder="Select nationality"
            onChange={handleCountryChange}
            isClearable
          />
        </Col>
      </Row>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <AntSelect
            placeholder="Select role"
            value={filters?.role || null}
            onChange={(value) => handleSelectChange('role', value)}
            style={{ width: '100%' }}
          >
            <Option value="applicant">Applicant</Option>
            <Option value="role">Role</Option>
          </AntSelect>
        </Col>
        <Col span={6}>
          <p>Score</p>
          <Slider
            min={0}
            max={100}
            onChange={handleSliderChange}
            value={filters?.scoreThreshold || 0}
            marks={{ 0: '0', 50: '50', 80: '80', 100: '100' }}
          />
        </Col>
      </Row>

      <div style={{ marginBottom: 16 }}>
        <Tag color="blue">{filteredDataCount} results</Tag>
      </div>

      <Table dataSource={filteredData || []} columns={columns} rowKey="jobId"  />
    </div>
  );
};

export default AdminDashboard;
