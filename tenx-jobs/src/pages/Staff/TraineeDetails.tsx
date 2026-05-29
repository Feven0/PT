import { Avatar, Card, Col, Row, Tabs, Tooltip } from 'antd';
import type { TabsProps } from 'antd';
import { useEffect, useState } from "react";
import { MailOutlined, PhoneOutlined, LinkedinOutlined, EnvironmentOutlined, GithubOutlined, MediumOutlined, WhatsAppOutlined, SkypeOutlined } from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { FaTelegramPlane } from "react-icons/fa";

import TraineeProfileDetail from "../../components/Staff/Profile/TraineeProfileDetail";
import Skills from "../../components/Staff/Skills/Skills";
import StaffDataLoader from "../../components/commonComponents/StaffDataLoader";
import EmptyProfile from "../../components/commonComponents/EmptyProfile";

import { T_TraineeLocation } from "../../types/profileResponse";
import ServerError from "../../components/commonComponents/ServerError";
import JobLoading from "../../components/commonComponents/JobLoading";
import DraftCompetencies from "../../components/Staff/Skills/DraftCompetencies";
import useFetchTraineeProfileForStaff from "../../hooks/useFetchTraineeProfileForStaff";
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import { setStaffProfileTabsView } from "../../redux/slices/tabsSlice";
import useAxiosRequest from "../../hooks/useAxiosRequest";
import { getRunStage } from "../../utils/getRunStage";
import '../../styles/staff.css'

const run_stage = getRunStage();

export default function TraineeDetails() {
  const [count, setCount] = useState(5)
  const [error, setError] = useState<any>(null)
  const [response, setResponse] = useState<any>(null)
  const { allUserID } = useParams()
  const { user_profile_id } = useParams()
  const { name, email } = useAppSelector((state) => state.updateTraineeInfo)
  const { staffProfileTab } = useAppSelector((state) => state.tabs)
  const { user_role } = useAppSelector((state) => state.leapProfileId)
  const { awards, basics, education, volunteer, languages, competencies, projects, work_experience, certificates } = useAppSelector((state) => state.traineeProfileResponse.user_profile)

  const fetchUserProfile = useFetchTraineeProfileForStaff({ allUserID, user_profile_id })
  const dispatch = useAppDispatch()
  const { makeRequest } = useAxiosRequest(); 
  const getUserProfile = () => {  
    const data = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserID,
      user_profile_id: user_profile_id,
      profile_type: 'user_profile',
      filter: {},
    };
  
    makeRequest({
      url: '/sjob/get-user-profile',
      method: 'POST',
      data,
      onSuccess: (response) => {
        if (response?.data) {
          setResponse(response.data);
        } else {
          setError(`Error fetching user profile: ${response?.message}`);
        }
      },
      onError: (error) => {
        setError(`Error fetching user profile: ${error}`);
      },
    });
  };
  useEffect(() => {
    getUserProfile()
  }, [])

  useEffect(() => {
    fetchUserProfile()
  }, [])

  const onChange = (key: string) => dispatch(setStaffProfileTabsView(key))

  const items: TabsProps['items'] = [
    {
      key: '1',
      label: 'Competencies',
      children: competencies ? <Skills /> :
                        <EmptyProfile title="No Competencies" 
                        description="You currently don't have a profile. Please upload a profile by exporting it from your LinkedIn account." />
    },
    {
      key: '2',
      label: 'Profile',
      children: (basics && work_experience && projects && education) ? (
        <TraineeProfileDetail
          bio={basics}
          projects={projects}
          education={education}
          experience={work_experience}
          volunteer={volunteer}
          awards={awards}
          certificates={certificates}
          languages={languages}
        />
      ) : <StaffDataLoader />
    },
    {
      key: '3',
      label: 'Drafts',
      children: competencies ? <DraftCompetencies /> :
                        <EmptyProfile title="No Competencies" 
                        description="You currently don't have a profile. Please upload a profile by exporting it from your LinkedIn account." />
    },
  ];

  const displayName = basics?.attributes[0]?.full_name || name;
  const location = basics?.attributes[0]?.location;
  const initials = displayName
    .split(' ')
    .filter(part => part.length > 0)
    .slice(0, 2)
    .map(part => part[0].toUpperCase())
    .join('');

  const isLocationValid = (location: T_TraineeLocation) => {
    return Object.values(location).every(
      (value) => typeof value === 'string' && value.trim() !== ''
    );
  };

  const truncateText = (text: string, wordLimit: number): string => {
    const words = text.split(' ');
    if (words.length > wordLimit) {
      return words.slice(0, wordLimit).join(' ') + '...';
    }
    return text;
  };

  const role = basics?.attributes[0]?.role || '';
  const truncatedRole = truncateText(role, 6);

  const getIconByName = (name: string) => {
    switch (name.toLowerCase()) {
      case 'main':
        return <PhoneOutlined />;
      case 'whatsapp':
        return <WhatsAppOutlined />;
      case 'telegram':
        return <FaTelegramPlane />;
      case 'skype':
        return <SkypeOutlined />;
      default:
        return <PhoneOutlined />;
    }
  };

  if (error) return <ServerError />


  return (
    !response ?
      <Row gutter={16} justify="center" style={{ marginTop: "3rem" }}>
        <Col xs={24} lg={20} xxl={16} className="mobile-skills-header">
          <JobLoading count={count} setCount={setCount} />
        </Col>
      </Row> :
      <Row gutter={16} style={{ marginTop: "3rem", marginBottom: "2rem", marginLeft:"4rem" }} justify="center">
        <Col xs={24} lg={22} xxl={20}>
          <Row gutter={16} justify="center" className="staff-profile-wrapper">
            <Col xs={24} lg={16}>
              <Card className="full-width white-bg trainee__profile__card">
                <Tabs
                  defaultActiveKey={staffProfileTab}
                  items={items} onChange={onChange}
                />
                </Card>
            </Col>
            {basics?.attributes.length > 0 && (
              <Col xs={24} lg={8} className="user-info-wrapper">
                <Card
                  className="white-bg"
                  title={
                    <div className="flex-center gap-8" style={{ padding: "0.5rem 0" }}>
                    
                      <Avatar shape="square" size={50}>
                        {initials}
                      </Avatar>
                   
                      <div className="flex" style={{ flexDirection: "column" }}>
                        <span className="user-name-text">{displayName}</span>
                        {/* <p className="user-name-sub-text" style={{ wordBreak: 'break-word', whiteSpace: 'normal' }}>{basic_info?.attributes[0]?.role}</p> */}
                        <Tooltip title={role}>
                          <p className="user-name-sub-text" style={{ wordBreak: 'break-word', whiteSpace: 'normal' }}>
                            {truncatedRole}
                          </p>
                        </Tooltip>
                      </div>
                    </div>
                  }
                >
                  <div>
                    {(basics?.attributes[0]?.email || email) && (
                      <span className="flex gap-8">
                        <MailOutlined /> <p>{basics?.attributes[0]?.email || email}</p>
                      </span>
                    )}
                    {basics?.attributes[0]?.phone.length > 0 && (
                      <div className="mt-8">
                        {basics.attributes[0].phone.map((phoneEntry, index) => (
                          <span key={index} className="flex-center gap-8">
                            {getIconByName(phoneEntry.name)}
                            <p>{phoneEntry.value}</p>
                          </span>
                        ))}
                      </div>
                    )}
                    {basics?.attributes[0].media &&
                      basics?.attributes[0].media.map((me) => {
                        let icon;
                        switch (me.name.toLowerCase()) {
                          case 'linkedin':
                            icon = <LinkedinOutlined />;
                            break;
                          case 'github':
                            icon = <GithubOutlined />;
                            break;
                          case 'medium':
                            icon = <MediumOutlined />;
                            break;
                          default:
                            icon = null;
                        }

                        return (
                          <span className="flex gap-8 mt-8" key={me.link}>
                            {icon}
                            <a href={me.link} target="_blank" rel="noopener noreferrer">
                              {me.name}
                            </a>
                          </span>
                        );
                      })}
                    {location && isLocationValid(location) && (
                      <span className="flex gap-8 mt-8">
                        <EnvironmentOutlined /><p>{location.address}</p>
                      </span>
                    )}
                  </div>
                </Card>
              </Col>
            )}
          </Row>
        </Col>
      </Row>
  )
}