import { useState, useContext } from 'react';
import { Input, Row, Col, Typography, Button } from 'antd';
import { MyJobCard } from './index';
import '../../styles/ProfileDetail/profiledetail.css';
import { ProviderContext } from '../../context/context';

const { Title } = Typography;

const ProfileDetail = () => {
    const { session } = useContext(ProviderContext);
    const [selectedCvId, setSelectedCvId] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [isCvListVisible, setIsCvListVisible] = useState(false); // State to toggle CV list

    const data = [
        { id: "8cbd6090-800e-4535-95bd-466d96ce97b8", name: "AI Engineering Role", company: "Wellfound" },
        { id: "d8936b36-eddb-4fb2-aaeb-33b7d7535f42", name: "Data Engineering Role", company: "Brainstorm" },
        { id: "8204d7df-5d15-4de6-968e-c49fde996000", name: "ML Engineering Role", company: "Indeed" },
        { id: "9290280c-fcd5-4360-949f-6d2645df7bb9", name: "Software Engineering Role", company: "Netflix" }
    ];

    const handleAnalyse = (cvId) => {
        setSelectedCvId(cvId);
        setSearchQuery('');
    };

    const toggleCvList = () => {
        setIsCvListVisible(!isCvListVisible); // Toggle visibility
    };

    return (
        <div className='profile-container'>
            <Row justify="space-between" align="middle">
                <Col>
                    <Button className='cv-button' onClick={toggleCvList}>
                        {isCvListVisible ? 'Hide CV List' : 'Show CV List'}
                    </Button>
                </Col>
            </Row>

            {isCvListVisible && (
                <Row gutter={[16, 16]} style={{ marginBottom: '20px', marginTop: '10px' }}>
                    <Col span={24}>
                        <div className='cv-dropdown'>
                            {session && session.length > 0 ? (
                                session.map((item, index) => (
                                    <Button 
                                        key={index} 
                                        className='cv-item-list' 
                                        onClick={() => handleAnalyse(item.sessionId)}
                                        block
                                    >
                                        {item.fileName}
                                    </Button>
                                ))
                            ) : (
                                <div className='p-2 text-gray-500'>No CVs available</div>
                            )}
                        </div>
                    </Col>
                </Row>
            )}

            <Row gutter={[16, 16]}>
                <Col span={24}>
                    <Input.Search
                        placeholder="Search jobs"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        enterButton
                        style={{ width: '100%', marginBottom: '20px' }}
                    />
                </Col>
                {data
                    .filter(item => item.name.toLowerCase().includes(searchQuery.toLowerCase()))
                    .map(item => (
                        <Col span={8} key={item.id}>
                            <MyJobCard item={item} selectedCvId={selectedCvId} />
                        </Col>
                    ))}
            </Row>
        </div>
    );
};

export default ProfileDetail;