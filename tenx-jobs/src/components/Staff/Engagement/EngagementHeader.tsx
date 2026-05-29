import { Col,Flex, Card, Button, Select, Row } from 'antd';
import { ArrowLeftOutlined, ArrowRightOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { useAppSelector } from '../../../redux/hooks/hooks';
import EngagementStats from "../../Trainee/EngagementStats";

export default function EngagementHeader() {
    const navigate = useNavigate()
    const { user_profile_id, all_user_id } = useParams()
    const { engagement_list } = useAppSelector((state) => state.IdList);
    const { engagementStats } = useAppSelector((state) => state.userStats);

    const engagementIds = Object.keys(engagement_list);

    const currentIndex = engagementIds.findIndex((name) => {
      const engagement = engagement_list[name];
      return (
        engagement.all_user_id === all_user_id && engagement.user_profile_id === user_profile_id
      );
    });
    
    const handleNavigateBackward = () => {
        if (currentIndex > 0) {
          const prevId = engagementIds[currentIndex - 1];
          const prevEngagement = engagement_list[prevId]; 
          navigate(
            `/staff/trainee_engagements/${prevEngagement.all_user_id}/${prevEngagement.user_profile_id}`
          );
        }
      };
      
    
    const handleNavigateForward = () => {
      if (currentIndex < engagementIds.length - 1) {
        const nextId = engagementIds[currentIndex + 1];
        const nextEngagement = engagement_list[nextId];
        navigate(
          `/staff/trainee_engagements/${nextEngagement.all_user_id}/${nextEngagement.user_profile_id}`
        );
      }
    };
    
  
  return (
    <>
        <Col xs={24} lg={20} xxl={16}>
                <div style={{
                      padding:"0.5rem 1rem", 
                      background: "#FFF",
                      border: "2px solid D9D9D9", 
                      borderRadius: "0.5rem", 
                      marginBottom: "1rem",
                      display: "flex",
                      justifyContent: "space-between"
                      }}>
                    <div className="flex-center gap-8">
                      <ArrowLeftOutlined className="engagement-detail-icon .engagement-icon:hover" onClick={() => navigate("/staff")}/>
                      <p className='engagement-detail-title'>Engagement</p>
                    </div>
                </div>
        </Col>
        <Col xs={24} lg={20} xxl={16}>
            <Card className="trainee-container-column" style={{borderRadius: "8px 8px 0 0"}}>
                <Flex justify={'space-between'} gap={"1.5rem"}>
                  <Row gutter={16} style={{width:"100%"}}>
                    <Col xs={24} md={8}>
                      <Select
                      showSearch
                      style={{ width: "100%", marginTop:"0.5rem" }}
                      placeholder="Select an engagement"
                      optionFilterProp="children"
                      value={engagementIds[currentIndex]}
                      onChange={(value) => {
                        const engagement = engagement_list[value];
                        navigate(
                          `/staff/trainee_engagements/${engagement.all_user_id}/${engagement.user_profile_id}`
                        );
                      }}
                      filterOption={(input, option) => {
                        const name = option?.key;
                        return name ? name.toLowerCase().indexOf(input.toLowerCase()) >= 0 : false;
                      }}
                    >
                          {engagementIds.map((id) => {
                            return (
                              <Select.Option key={id} value={id}>
                                {id} 
                              </Select.Option>
                            );
                          })}
                          
                      </Select>  
                    </Col>
                    <Col xs={24} md={16} style={{
                      display: "flex",
                      justifyContent: "flex-end",
                      alignItems: "center"
                    }}>
                      <EngagementStats stats={engagementStats} />
                    </Col>
                  </Row>
                                  
                    <Flex gap={"1rem"} align='center'>
                        <Button 
                            className="engagement-detail-navigation"
                            disabled={currentIndex === 0}
                            onClick={() => handleNavigateBackward()}
                            icon={<ArrowLeftOutlined />}
                            />
                        <Button 
                            className="engagement-detail-navigation"
                            disabled={currentIndex === engagementIds.length - 1}
                            onClick={() => handleNavigateForward()}
                            icon={<ArrowRightOutlined />}
                        />
                    </Flex>
                </Flex>
            </Card> 
        </Col>
    </> 
    )
}

