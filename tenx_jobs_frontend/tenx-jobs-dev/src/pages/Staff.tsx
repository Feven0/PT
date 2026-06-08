import { useMediaQuery } from "react-responsive";
import { createContext, Suspense, useEffect, useState } from "react";
import {  Drawer,App, Col, Image, Layout, Menu, Row, Tooltip, Modal, Divider } from 'antd';
import { useQuery } from "@apollo/client";
import { LogoutOutlined } from '@ant-design/icons';
import { Link, Outlet } from "react-router-dom";
import type { MenuProps } from 'antd';
import { TeamOutlined, CheckCircleOutlined, CaretDownOutlined, PieChartOutlined } from '@ant-design/icons';
import {BreadCrumb} from "../components/commonComponents/BreadCrumb";
//Components
import ServerError from "../components/commonComponents/ServerError";
import UserHeadline from "../components/commonComponents/UserHeadline";
import TeamNotification from "../components/Staff/TeamNotification";

//Queries
import { REVIEWER, STAFF_PERSONAL_SETTINGS } from "../graphql/queries/user";

//Redux and custom hooks
import { useAppDispatch, useAppSelector } from "../redux/hooks/hooks";
import { setAllUserId, setBatch, setGroups, setUserId } from "../redux/slices/userSlices";
import { setAllUserIdForLeap } from "../redux/slices/leapProfileIdSlice";
import { setContentCollapsed, setSiderTab } from "../redux/slices/tabsSlice";
import { resetReactionId } from "../redux/slices/staff/IdListsSlice";

//Type definitions
import { TReviewer } from "../types/userTypes";
import { BatchEntity, GroupEntity } from "../types/generated";

//Style and assets
import { layout, tenAcademy, tenAcademyLogoWithIcon } from "../assets";
import '../App.css';
import '../styles/staffDashboard.css'
import LoadingState from "../components/commonComponents/LoadingState";
import useLogout from "../hooks/useLogout";

type BatchData = {
  batchID: string;
  Batch?: string;
  Class_link?: string;
  Communication_link?: string;
}

export const TraineeSidebarContext = createContext(false)
const { Header, Content, Sider } = Layout;

export default function Staff() {
  const { email,batch }  = useAppSelector((state) => state.user)
  const [isModalVisible, setIsModalVisible] = useState(false);
  const { message } = App.useApp();
  const {siderTab} = useAppSelector((state) => state.tabs)
  const isMobile = useMediaQuery({maxWidth: 768});
  const isMedium = useMediaQuery({ maxWidth: 991 });
  const [collapsed, setCollapsed] = useState(true)
  const [visible, setVisible] = useState(false)
  const strapiId = useAppSelector((state: any) => state.user?.strapiId) as number

  const dispatch = useAppDispatch()

  const { data: personalData, loading: preferenceLoading } = useQuery(STAFF_PERSONAL_SETTINGS, {
      fetchPolicy: "network-only",
      variables: { "email": email }
    });
  
    useEffect(() => {
      if (email && !batch) {
        const timeoutId = setTimeout(() => {
          const b = personalData?.preferences?.data?.[0]?.attributes?.defaultSettings?.batch;
          const batchID = personalData?.preferences?.data?.[0]?.attributes?.defaultSettings?.batchID;
    
          if (b && batchID) {
            dispatch(setBatch({ batch: b, batchID: batchID }));
          } else {
            dispatch(setBatch({ batch: 6, batchID: 3 }));
          }
        }, 1000); 
    
        return () => clearTimeout(timeoutId); 
      }
    }, [personalData, email, batch]);
    

  const { loading, error, data } = useQuery<TReviewer>(REVIEWER, {
    fetchPolicy: "network-only",
    variables: {
      "email": email
    },
  })

  const toggleMask = () => { setVisible((prev) => !prev) }
  const onClose = () => setVisible(false);

  useEffect(() => {
    dispatch(setContentCollapsed(collapsed))
  }, [collapsed])

  
  const Batches: BatchData[] = [];
  const groupids: string[] = [];
  data?.reviewers?.data[0]?.attributes?.batches?.data?.forEach((batch: BatchEntity) => {
    Batches.push({
      batchID: batch?.id ?? "",
      Batch: typeof batch?.attributes?.Batch === 'number' 
              ? batch.attributes.Batch.toString() 
              : batch?.attributes?.Batch ?? "",  
      Class_link: batch?.attributes?.Class_link ?? "",
      Communication_link: batch?.attributes?.Communication_link ?? "",
    });
  });

  useEffect(() => {
    dispatch(setUserId(data?.reviewers?.data[0]?.id))
    dispatch(setAllUserId(data?.reviewers?.data[0]?.attributes?.all_user?.data?.id))
    dispatch(setAllUserIdForLeap(data?.reviewers?.data[0]?.attributes?.all_user?.data?.id))
    if (data?.reviewers?.data[0]?.attributes?.all_user?.data?.attributes?.groups?.data?.length) {
      data?.reviewers?.data[0]?.attributes?.all_user?.data?.attributes?.groups?.data?.forEach((group: GroupEntity) => {
        if (group?.id) {
          groupids.push(group.id);
        }
      });
    }
    dispatch(setGroups(groupids));
  
  } , [data])

  const handleMenuClick = (e: any) => {
    dispatch(setSiderTab(e.key));
    if (onClose) {
      onClose();
    }
  };

  const logout = useLogout({ strapiId });

  if (loading || preferenceLoading) return <LoadingState/>;
  if (error) return  <ServerError />

  const items: MenuProps['items'] = [
    {
      key: '1',
      label: (
        <Link to="/staff" onClick={() => onClose()}>
          Trainee
        </Link>
      ),
      icon:<TeamOutlined />
    },
    {
      key: '2',
      label: (
        <Link to="/staff/trainee-stats" onClick={() => onClose()}>
          Stats
        </Link>
      ),
      icon: <PieChartOutlined />,
    },
  ]

  if (isMedium) {
    items.push({
      key: '4',
      label: <span onClick={() => logout()}>Logout</span>,
      icon: <LogoutOutlined style={{ fontSize: '18px' }} />,
    });
  }

  
  return (
    <Layout className="overflow-y" style={{ overflowX: 'hidden', height: '100vh' }}>
            <Row gutter={[4, 8]} className="staff__pages" style={{ background: "whitesmoke" }}>
                <Col xs={0} lg={1} className="cohort-switcher-wrapper-web" >
                    <div className="flex flex-column staff-cohort-switcher-icon" style={{ height: "2rem", marginTop: "0.25rem"}}>
                        <Image src={tenAcademy} preview={false} style={{ width: "1.9rem", height: "1.9rem" }} />
                        <Tooltip title="Select Batch">
                            <CaretDownOutlined 
                              style={{ color: "red",width: "1.9rem", cursor: "pointer",justifyContent: "center" }} 
                              onClick={() => setIsModalVisible(true)}
                            />
                        </Tooltip>
                    </div>
                </Col>
                <Col xs={24} lg={23}>
                    <Header className="home-page-header-mobile">
                      <div className="header-logo">
                            <div className="d-flex align-items-center flex-column flex-justify-content-center staff-cohort-switcher-icon-mobile" style={{ height: "2rem" }}>
                                <Image src={tenAcademyLogoWithIcon} preview={false} style={{ width: "1.8rem", height: "2.2rem", cursor: "pointer", paddingRight: "0.25rem" }}  onClick={() => setIsModalVisible(true)}/>
                            </div> 
                            <div className={`d-flex-between cohort-title-mobile ${collapsed ? "collapsed-cohort-switcher" : ""}`}>
                                <div>
                                  <h2 className={`batch-text ${collapsed ? 'collapsed-batch-text' : ''} ${!collapsed ? 'desktop-expanded' : ''}`}>
                                    {`Batch ${batch}`}
                                  </h2>
                                 </div>
                                <div style={{ padding: "0.5rem", marginRight: collapsed ? "0.75rem" : "0" }} className="menu-outlined-web">
                                  {
                                  collapsed ? (<img src={layout} style={{width:"1.5rem", cursor:"pointer"}} alt="layout"  onClick={() => setCollapsed(!collapsed)} />
                                  ) : (<img src={layout} style={{width:"1.5rem", cursor:"pointer"}} alt="layout" onClick={() => setCollapsed(!collapsed)} />
                                  )}
                                </div>
                              </div>
                            <div className="header-left d-flex bread-crumb-container" style={{ textAlign: "left" }}>
                                <span className="font-16"><BreadCrumb /></span>
                            </div>
                            <div className="mobile">
                            <img src={layout} alt="layout" style={{ fontSize: "22px", marginRight: "6px", width:"1.5rem", cursor:"pointer" }} className="MenuOutlined-mobile-staff" onClick={toggleMask} />
                                <Drawer 
                                  title="" 
                                  placement={isMobile ? 'right' : 'left'} 
                                  onClose={onClose} 
                                  open={visible} 
                                  width={425} 
                                  className="drawer-menu-mobile">
                                    <Menu
                                      onClick={handleMenuClick}
                                      defaultSelectedKeys={[siderTab]}
                                      mode="inline"
                                      className="sidebar"
                                      items={items}
                                  />
                                    <div className="flex flex-column align-items-center mobile-loggedin">
                                        <UserHeadline />
                                    </div>
                                </Drawer>
                            </div>
                        </div>
                        <div className="notificationTrainee" style={{height:"3.75rem", marginRight: "1rem"}}>
                          <TeamNotification />
                        </div>
                      <div className="flex align-items-center web-loggedin" style={{ gap: "0.25rem" }}>
                          <UserHeadline />
                      </div>
                    </Header>
                    <Layout>
                      <Sider
                        width={220}
                        trigger={null}
                        theme="light"
                        collapsible
                        breakpoint={"lg"}
                        collapsed={collapsed}
                        className="sidebar web collapsed-sidebar-staff">

                        <Divider style={{ margin: "0rem 0" }} />
                        <Menu
                          onClick={handleMenuClick}
                          defaultSelectedKeys={[siderTab]}
                          mode="inline"
                          className="sidebar"
                          items={items}
                        />
                      </Sider>
                      <Content className={collapsed ? "collapsed-content" : "content"} style={{padding: "0 0.5rem"}}>
                          <div style={{overflowX:"hidden"}}>
                            <Suspense fallback={<LoadingState />}>
                              <Outlet />
                            </Suspense>
                          </div>
                      </Content>
                    </Layout>
                </Col>
                {
                    isModalVisible && (
                      <Modal
                        title="Switch Batch"
                        width={250}
                        open={isModalVisible}
                        onOk={() => setIsModalVisible(false)}
                        onCancel={() => setIsModalVisible(false)}
                        footer={null}
                        className="applicant-cohort-switcher-modal"
                      >
                        <div>
                          {Batches.map((cohort, index) => (
                            <div key={cohort.batchID} className="this">
                              <div
                                className="switch-cohort-hover"
                                onClick={() => {
                                  message.success(`Batch ${cohort.Batch} is selected`);
                                  dispatch(setBatch({ batch: cohort.Batch, batchID: cohort.batchID }));
                                  dispatch(resetReactionId());
                                  setIsModalVisible(false);
                                }}
                                style={{ cursor: "pointer" }}
                              >
                                <div className="d-flex-items-center" style={{ padding: "0.5rem 1rem" }}>
                                  <div className="d-flex d-flex-between">
                                    <span>{`Batch ${cohort.Batch}`}</span>
                                    {cohort.Batch === batch.toString() && (
                                      <span style={{ color: "green" }}>
                                        <CheckCircleOutlined />
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </div>
                              {index !== Batches.length - 1 && <Divider style={{ margin: 0, padding: 0 }} />}
                            </div>
                          ))}
                        </div>
                      </Modal>
                    )
                  }

            </Row>
    </Layout>  
  )
}
