import { Drawer, Image, Layout, Menu, message, Row } from "antd";
import { createContext, Suspense, useEffect, useState } from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { LogoutOutlined } from '@ant-design/icons';
import { useQuery } from "@apollo/client";
import { useMediaQuery } from "react-responsive";
import { IoBriefcaseOutline } from "react-icons/io5";
import { PiUserCircleGear } from "react-icons/pi";
import { PiSlidersHorizontalLight } from "react-icons/pi";
import type { MenuProps } from 'antd';

//Components
import ServerError from "../components/commonComponents/ServerError";
import TraineeNotification from "../components/Trainee/TraineeNotification";
import UserHeadline from "../components/commonComponents/UserHeadline";
import LoadingState from "../components/commonComponents/LoadingState";

//Redux and custom hooks
import { useAppDispatch, useAppSelector } from "../redux/hooks/hooks";
import { setAllUserId, setBatch, setGroups, setTid, setUserId } from "../redux/slices/userSlices";
import { setAllUserIdForLeap, setBatchID, setTraineeId, setUserProfileId } from "../redux/slices/leapProfileIdSlice";
import { GET_TRAINEE_DETAILS } from "../graphql/queries/user";
import { setContentCollapsed, setSiderTab } from "../redux/slices/tabsSlice";
import useLogout from "../hooks/useLogout";

//Assets
import { tenlogo_small, leaplogo, layout, tenlogo } from "../assets";
import useFetchUserPreferenceID from "../hooks/useFetchUserPreferenceID";
import useAxiosRequest from "../hooks/useAxiosRequest";
import { getRunStage } from "../utils/getRunStage";
import '../styles/sidebar.css'

const { Header, Content, Sider } = Layout;

export const TraineeSidebarContext = createContext(false)
const run_stage = getRunStage();

export default function Trainee() {
  const [collapsed, setCollapsed] = useState(true)
  const [visible, setVisible] = useState(false)
  const [response, setResponse] = useState<any>(null)

  const dispatch = useAppDispatch()
  const isMobile = useMediaQuery({ maxWidth: 768 });
  const isMedium = useMediaQuery({ maxWidth: 991 });

  const strapiId = useAppSelector((state: any) => state.user?.strapiId) as number
  const email = useAppSelector((state) => state.user.email)
  const { allUserId } = useAppSelector((state) => state.user)
  const { siderTab } = useAppSelector((state) => state.tabs)
  const fetchUserPreferenceID = useFetchUserPreferenceID();

  const navigate = useNavigate();
  const { makeRequest } = useAxiosRequest();

  const toggle = () => { setCollapsed(!collapsed) }
  const toggleMask = () => { setVisible((prev) => !prev) }
  const onClose = () => setVisible(false);

  useEffect(() => {
    dispatch(setContentCollapsed(collapsed))
  }, [collapsed])

  const logout = useLogout({ strapiId });

  const { loading: TraineeLoading, error: TraineeError, data: TraineeData } = useQuery(GET_TRAINEE_DETAILS, {
    fetchPolicy: "network-only",
    variables: {
      "email": email
    }
  })

  const sendResult = () => {
    if (allUserId) {
      makeRequest({
        url: '/sjob/get-user-profile-id',
        method: 'POST',
        data: {
          all_user_id: allUserId,
          profile_type: 'other',
          filter: {},
          run_stage: run_stage,
        },
        onSuccess: (response) => {
          if(response?.status === 200){
            setResponse(response.data);
          }
        },
        onError: (error) => {
          message.error(`Error fetching user profile: ${error}`);
        },
      });
    }
  }

  useEffect(() => {
    sendResult();
  }, [allUserId])

  useEffect(() => {
    if (response) {
      dispatch(setUserProfileId(response?.user_profile_id));
    }
  }, [response]);

  useEffect(() => {
    if (TraineeData) {
      dispatch(setBatch(
        {
          batch: TraineeData?.trainees?.data[0]?.attributes?.batch?.data?.attributes?.Batch,
          batchID: TraineeData?.trainees?.data[0]?.attributes?.batch?.data?.id
        }))

      dispatch(setBatchID(
        {
          batch: TraineeData?.trainees?.data[0]?.attributes?.batch?.data?.attributes?.Batch,
          batchID: TraineeData?.trainees?.data[0]?.attributes?.batch?.data?.id
        }))
      dispatch(setUserId(TraineeData?.trainees?.data[0]?.attributes?.trainee_id))
      dispatch(setAllUserId(TraineeData?.trainees?.data[0]?.attributes?.all_user?.data?.id))
      dispatch(setAllUserIdForLeap(TraineeData?.trainees?.data[0]?.attributes?.all_user?.data?.id))
      dispatch(setTid(TraineeData?.trainees?.data[0]?.id))
      dispatch(setTraineeId(TraineeData?.trainees?.data[0]?.id ?? ""))

      const groupids: string[] = []
      if (TraineeData.trainees?.data[0]?.attributes?.all_user.data.attributes.groups.data.length) {
        TraineeData.trainees?.data[0]?.attributes?.all_user.data.attributes.groups.data.forEach((group: any) => {
          groupids.push(group.id)
        })
      }
      dispatch(setGroups(groupids))
    }
  }, [TraineeData]);

  useEffect(() => {
    fetchUserPreferenceID();
  }, [allUserId])

  if (TraineeLoading) return <LoadingState />;
  if (TraineeError) return (<ServerError />);

  const handleMenuClick = (e: any) => {
    dispatch(setSiderTab(e.key));
    if (onClose) {
      onClose();
    }
  };

  const items: MenuProps['items'] = [
    {
      key: '1',
      label: (
        <Link to="/trainee" onClick={() => onClose()}>
          All Jobs
        </Link>
      ),
      icon: (
        <img
          src={siderTab === '1' ? tenlogo : leaplogo}
          alt={siderTab === '1' ? 'active-leap-logo' : 'leap-logo'}
          width={28}
        />
      ),
    },
    {
      key: '2',
      label: (
        <Link to="/trainee/my-jobs" onClick={() => onClose()}>
          My Jobs
        </Link>
      ),
      icon: <IoBriefcaseOutline style={{ fontSize: '22px' }} />,
    },
    {
      key: '3',
      label: (
        <Link to="/trainee/trainee-profile" onClick={() => onClose()}>
          Profile
        </Link>
      ),
      icon: <PiUserCircleGear style={{ fontSize: '22px' }} />,
    }
  ]

  if (isMedium) {
    items.push({
      key: '4',
      label: <span onClick={() => logout()}>Logout</span>,
      icon: <LogoutOutlined style={{ fontSize: '18px' }} />,
    });
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header className="home-page-header">
        <Row justify="space-between" className="header" wrap={false}>
          <div className={`d-flex-between head-line-container ${collapsed ? "headline-collapsed" : ""}`}>
            <Link to="/trainee">
              <div className="logo flex-center gap-8">
                <Image preview={false} width={28} src={tenlogo_small} />
                <h3 className={`dark-orange-color ${collapsed ? "logo-text" : ""}`}>Leap</h3>
              </div>
            </Link>
            <span className={`web-menu-icon ${collapsed ? "web-menu-icon-collapsed" : ""}`} >
              <img src={layout} alt="layout"
                className="cursor-pointer"
                onClick={toggle} />
            </span>
            <span className="mobile">
              <img src={layout} alt="layout"
                className="MenuOutlined-mobile cursor-pointer"
                onClick={toggleMask} />
              <Drawer title="Menu"
                placement={isMobile ? 'right' : 'left'}
                onClose={onClose}
                open={visible}
                width={300}
                className="sidebar-drawer">
                 <Menu
                  onClick={handleMenuClick}
                  defaultSelectedKeys={[siderTab]}
                  mode="inline"
                  className="sidebar"
                  items={items}
              />
              </Drawer>
            </span>
          </div>
          <div className="flex-center gap-16">
            <div className="trainee-preferences cursor-pointer" style={{height:"3rem"}}>
              <PiSlidersHorizontalLight className="font-24" style={{fontSize:"24px"}} onClick={
                () => navigate('/trainee/preferences')
              }/>
            </div>
            <div className="notificationTrainee cursor-pointer" style={{ height: "3.75rem" }}>
              <TraineeNotification />
            </div>
            <span className="notification-headline">
              <UserHeadline />
            </span>
          </div>
        </Row>
      </Header>
      <Layout className="home-page-layout">
        <Sider
          trigger={null}
          breakpoint={"lg"}
          theme="light"
          width={220}
          collapsible
          collapsed={collapsed}
          className="sidebar web sidebar-collapsible"
          style={{
            overflow: "hidden",
            position: 'fixed',
            left: 0,
            top: "64px",
            bottom: 0,
            background: "whitesmoke",
            height: `calc(100vh - 64px)`,
            transition: `width 0.5s ease-in-out`,
          }}>
          <Menu
              onClick={handleMenuClick}
              defaultSelectedKeys={[siderTab]}
              mode="inline"
              className="sidebar"
              items={items}
              />
        </Sider>
        <Content className={collapsed ? "collapsed-content" : "content"} >
          <TraineeSidebarContext.Provider value={collapsed}>
            <div style={{ overflowX: "hidden", height:"100vh" }}>
              <Suspense fallback={<LoadingState />}>
                <Outlet />
              </Suspense>
            </div>
          </TraineeSidebarContext.Provider>
        </Content>
      </Layout>
    </Layout >
  );
}
