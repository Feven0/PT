import React, { useState } from 'react';
import { Input, Row, Col } from "antd";
import { JobCard } from '../components/index';
import '../styles/jobs/jobs.css';

const Jobs = () => {
  const data = [
    { id: "8cbd6090-800e-4535-95bd-466d96ce97b8", name: "AI Engineering Role", company: "wellfound" },
    { id: "d8936b36-eddb-4fb2-aaeb-33b7d7535f42", name: "Data Engineering Role", company: "brainstorm"  },
    { id: "8204d7df-5d15-4de6-968e-c49fde996000", name: "ML Engineering Role", company: "indeed"  },
    { id: "9290280c-fcd5-4360-949f-6d2645df7bb9", name: "Software Engineering Role", company: "netflix"  }
  ];

  const [searchQuery, setSearchQuery] = useState('');

  const filteredData = data.filter(item =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const { Search } = Input;

  const onSearch = (value) => {
    console.log(value);
    setSearchQuery(value); // Update search query state
  };

  return (
    <>
      <Row justify="end" className='search' style={{marginTop: '50px'}}>
        <Col>
          <Search 
            placeholder="input search text" 
            // onSearch={onSearch} 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            enterButton 
            style={{width: '30rem'}}
          />
        </Col>
      </Row>
      <Row gutter={16} style={{margin: '40px'}}>
        {filteredData.map(item => (
          <Col span={6} key={item.id}>
            <JobCard item={item} />
          </Col>
        ))}
      </Row>
    </>
  );
};

export default Jobs;