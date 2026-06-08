import { Card, Col, Row, Tabs } from 'antd';
import type { TabsProps } from 'antd';
import LeapedJobs from "../../components/Trainee/LeapedJobs";
import Liked from "../../components/Trainee/Liked";
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import { setEngagementTabs } from "../../redux/slices/tabsSlice";
import EngagementStats from "../../components/Trainee/EngagementStats";

export default function MyJobs() {
  const { engagementStats } = useAppSelector((state) => state.userStats);
  const {engagementTabs} = useAppSelector((state) => state.tabs);
  const dispatch = useAppDispatch();

  const items: TabsProps['items'] = [
    {
      key: '1',
      label: 'Engagements',
      children: <Liked/>,
    },
    {
      key: '2',
      label: 'Leaped',
      children: <LeapedJobs/>,
    }
  ];

  const onChange = (key: string) => dispatch(setEngagementTabs(key))

  return (
    <Row gutter={16} justify="center" style={{marginBottom:"2rem"}}>
      <EngagementStats stats={engagementStats} source="trainee" />
      <Col xs={24} lg={22} xxl={18} className="mt-16">
        <Card className="myJobs__tab">
            <Tabs 
              defaultActiveKey={engagementTabs} 
              items={items} 
              onChange={onChange} 
              />
        </Card>
      </Col>
    </Row>
  )
}
