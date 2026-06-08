import { Card, Col, Row, Tabs } from "antd";
import { setProfileTabsStaffView } from "../../redux/slices/tabsSlice";
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import type { TabsProps } from 'antd';
import AllUsersProfiles from "../../components/Staff/Profile/AllUsersProfiles";
import AllUsersEngagements from "../../components/Staff/Engagement/AllUsersEngagements";
import '../../styles/staff.css'

export default function StaffHome() {
  const dispatch = useAppDispatch();
  const { profileTabStaffView } = useAppSelector((state) => state.tabs);

  const onChange = (key: string) => dispatch(setProfileTabsStaffView(key));

  const items: TabsProps['items'] = [
    {
      key: '1',
      label: 'Profile',
      children: <AllUsersProfiles/>
    },
    {
      key: '2',
      label: 'Engagement',
      children: <AllUsersEngagements/>,
    },
  ];

  return (
    <Row gutter={16} style={{ marginTop: "3rem" }} justify="center">
      <Col xs={24} lg={20} xxl={16}>
        <Card>
          <Tabs
            className="staff__home__tabs"
            defaultActiveKey={profileTabStaffView}
            items={items}
            onChange={onChange}
          />
        </Card>
      </Col>
    </Row>
  )
}
