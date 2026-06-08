import { Col,Flex, Card, Button } from 'antd';
import { ArrowLeftOutlined, ArrowRightOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { useAppSelector } from '../../../redux/hooks/hooks';

export default function EngagementDetailHeader() {
    const navigate = useNavigate()
    const { user_reaction_id,user_profile_id, all_user_id } = useParams()
    const { reaction_id } = useAppSelector((state) => state.IdList);

    const reactionIds = Object.keys(reaction_id);

    const currentIndex = reactionIds.findIndex(id => id === user_reaction_id);
  
    const handleNavigateBackward = () => {
      if (currentIndex > 0) {
        const prevId = reactionIds[currentIndex - 1];
        navigate(`/staff/trainee_engagements/${all_user_id}/${user_profile_id}/${prevId}`);
        
      }
    };
  
    const handleNavigateForward = () => {
      if (currentIndex < reactionIds.length - 1) {
        const nextId = reactionIds[currentIndex + 1];
        navigate(`/staff/trainee_engagements/${all_user_id}/${user_profile_id}/${nextId}`);    }
    };
  
  return (
    <>
        <Col xs={24} lg={20} xxl={16}>
                <Flex gap={"0.5rem"} style={{padding:"0.5rem 1rem", background: "#FFF",border: "2px solid D9D9D9", borderRadius: "0.5rem", marginBottom: "1rem"}}>
                    <ArrowLeftOutlined className="engagement-detail-icon .engagement-icon:hover" onClick={() => navigate(`/staff/trainee_engagements/${all_user_id}/${user_profile_id}`)}/>
                    <p className='engagement-detail-title'>Engagement Detail</p>
                </Flex>
        </Col>
        <Col xs={24} lg={20} xxl={16}>
            <Card className="trainee-container-column" style={{borderRadius: "8px 8px 0 0"}}>
                <Flex justify={'space-between'} gap={"1.5rem"}>
                    <p className="engagement-detail-navigation" style={{ width: "100%" }}>
                        {user_reaction_id ? reaction_id[user_reaction_id] : "No reaction selected"}
                    </p>
                    <Flex gap={"1rem"} align='center'>
                        <Button 
                            className="engagement-detail-navigation"
                            onClick={() => handleNavigateForward()}
                            disabled={currentIndex === reactionIds.length - 1}
                            icon={<ArrowLeftOutlined />}
                            />
                        <Button 
                            className="engagement-detail-navigation"
                            disabled={currentIndex === 0}
                            onClick={() => handleNavigateBackward()}
                            icon={<ArrowRightOutlined />}
                        />
                    </Flex>
                </Flex>
            </Card> 
        </Col>
    </> 
    )
}

