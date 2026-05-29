import { Row,Tabs, Col, Card, TabsProps } from 'antd';
import { useAppDispatch, useAppSelector } from '../../redux/hooks/hooks';
import { setStaffEngagementTab } from '../../redux/slices/tabsSlice';
import EngagedJobs from '../../components/Staff/Engagement/EngagedJobs';
import LeapedJobs from '../../components/Staff/Engagement/LeapedJobs';
import EngagementHeader from '../../components/Staff/Engagement/EngagementHeader';

export default function TraineeEngagements() {
    const dispatch = useAppDispatch();
    const { staffEngagementTab } = useAppSelector((state) => state.tabs);

    const onChange = (key: string) => dispatch(setStaffEngagementTab(key));
    
    const items: TabsProps['items'] = [
        {
            key: '1',
            label: 'Engaged',
            children: <EngagedJobs/>,
        },
        {
            key: '2',
            label: 'Leaped',
            children: <LeapedJobs/>,
        }
        ];

  return (
    <Row gutter={16} style={{ marginTop: "3rem" }} justify="center">
        <EngagementHeader />
        <Col xs={24} lg={20} xxl={16}>
        <Card>
            <Tabs
                defaultActiveKey={staffEngagementTab}
                items={items}
                onChange={onChange} 
            />
        </Card>
        </Col>
    </Row>
  )
}
