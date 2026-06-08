import { useMutation } from "@apollo/client";
import { Avatar, Button, Card, Col, message, Modal, Row, Tabs } from "antd";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import type { TabsProps } from 'antd';

// Components
import ServerError from "../../components/commonComponents/ServerError";
import TraineeMatchDetails from "../../components/Trainee/TraineeMatchDetails";
import Assets from "../../components/Trainee/MatchDetails/Assets";
import StaffDataLoader from "../../components/commonComponents/StaffDataLoader";
import EngagementDetailData from "../../components/Staff/Engagement/EngagementDetailData";
import TraineeExpandDetailHeader from "../../components/Trainee/TraineeExpandDetailHeader";
import NoFile from "../../components/commonComponents/NoFile";

// Redux and custom hooks
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import { Stats } from "../../redux/slices/userStatsSlice";

import { CREATE_NOTIFICATION } from "../../graphql/mutations/createNotification";
import { T_ExpandHeader, T_JobCardExpandReaction, T_MatchDetails, TProcessedJobCard } from "../../types/expandReactionTypes";
import useAxiosRequest from "../../hooks/useAxiosRequest";
import { setExpandDetailsTabs } from "../../redux/slices/tabsSlice";
import { getRunStage } from "../../utils/getRunStage";

// Styles
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import '../../styles/slidingCard.css'
import '../../App.css'

const run_stage = getRunStage();

export default function ExpandDetails() {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const {userReactionIds} = useAppSelector((state) => state.userReactionIds);
  const { allUserId, user_role, user_profile_id, trainee_id} = useAppSelector((state) => state.leapProfileId);
  const {expandDetailsTabs} = useAppSelector((state) => state.tabs);
  const reactionIds = Object.keys(userReactionIds);
  const { user_reaction_id, all_user_id } = useParams()
  const currentIndex = reactionIds.findIndex(id => id === user_reaction_id);
  const { makeRequest, loading } = useAxiosRequest();
  const { makeRequest: newRequest, loading: dataLoading, error } = useAxiosRequest();

  const [createNotification] = useMutation(CREATE_NOTIFICATION);
  const dispatch = useAppDispatch();

  const isExpansions = true;

  const getExpandedData = () => {
    newRequest({
      url: '/sjob/get-expanded-reaction',
      method: 'POST',
      data: {
        user_role: user_role,
        all_user_id: all_user_id,
        user_reaction_id: user_reaction_id,
        information_level: 'minimal',
        run_stage: run_stage
      },
      onSuccess: (response) => {
        if (response.status === 200) {
          setResponse(response.data);
        }
      },
      onError: () => {}
    });
  };

useEffect(() => {
  getExpandedData()
}, [user_reaction_id, all_user_id])

const leap_card =  response?.infocards?.leap_profile_card;

function getProcessedJobCard(): TProcessedJobCard {
  const jobCard: T_JobCardExpandReaction = {
    version: response?.infocards?.job_profile_card?.version,
    company_name: response?.infocards?.job_profile_card?.company_name,
    job_card: response?.infocards?.job_profile_card?.job_card,
    company_card: response?.infocards?.job_profile_card?.company_card,
    job_profile_id: response?.infocards?.job_profile_card?.job_profile_id,
    job_id: response?.infocards?.job_profile_card?.job_id,
    match_attributes: {
      ...response?.infocards?.job_profile_card?.match_attributes,
      match_detail: response?.infocards?.job_profile_card?.match_attributes?.match_detail.map((detail:T_MatchDetails, index:number) => ({
        ...detail,
        key: index.toString(),
      }))
    }
  };

  const stats: Stats = response?.infocards?.stats;
  return {
    cards: jobCard,
    stats
  };
}

const processedJobCard = getProcessedJobCard();
const jobTitle = processedJobCard.cards?.job_card?.header.find((header: T_ExpandHeader) => header.position === 1)?.value || "";
const leapProfileCard = leap_card;

const columns = [
  {
    title: 'Competency Name',
    dataIndex: 'job_competency_name',
    key: 'job_competency_name',
  },
  {
    title: 'Best Matched User Competency',
    dataIndex: 'best_matched_user_competency',
    key: 'best_matched_user_competency',
  },
  
  {
    title: 'Match Score',
    dataIndex: 'match_score',
    key: 'match_score',
  },
  {
    title: 'Matched Skills',
    dataIndex: 'matched_skills',
    key: 'matched_skills',
    render: (_text: string, record: T_MatchDetails) => (
      <span>{record.matched_skills.length}</span>
    ),
  },
  {
    title: 'Missing Skills',
    dataIndex: 'missing_skills',
    key: 'missing_skills',
    render: (_text: string, record: T_MatchDetails) => (
      <span>{record.missing_skills.length}</span>
    ),
  },
  {
    title: 'Confidence',
    dataIndex: 'confidence',
    key: 'confidence',
  },
];

const items: TabsProps['items'] = [
  {
    key: '1',
    label: 'Jobs',
    children: <EngagementDetailData response={response} refetch={getExpandedData}/>
  },
  {
    key: '2',
    label: 'Match Details',
    children: response && <TraineeMatchDetails 
              isExpansion={isExpansions} 
              transformedMatchDetail={processedJobCard.cards.match_attributes} 
              columns={columns} />
  },
  {
    key: '4',
    label:"Assets",
    children: <Assets file={leapProfileCard} />
  }
];

  const handleOk = () => setIsModalVisible(false)
  const handleCancel = () => setIsModalVisible(false);

  const handleStatusSubmission = async () => {
    let newId = '';
    if (currentIndex > 0) {
      const newIndex = currentIndex - 1;
       newId = userReactionIds[newIndex];
    }

    const sanitized_id_list= [{
      user_reaction_id: newId || user_reaction_id,
      job_trainee_id: response?.infocards?.reaction_profile_card?.job_trainee_id || "",
      job_id: processedJobCard.cards?.job_id || "",
    }]

    const postData = {
      user_role: user_role,
      run_stage: run_stage,
      all_user_id: allUserId,
      trainee_id: trainee_id,
      id_list:sanitized_id_list,
      application_status: 'Applied',
      description: ""
    };

    makeRequest({
      url: '/sjob/put-job-application-status',
      method: 'POST',
      data: postData,
      onSuccess: (response) => {
        if (response.status === 200) {
          message.success("Job status updated successfully");
          createNotification({
            variables: {
              sender: allUserId,
              group: 1,
              details: {
                traineeId: trainee_id,
                notificationMessageTeam: "Added job status",
                notificationMessageTrainee: "Updated job status",
                where: "Expanded Reaction",
                traineeLink: `/trainee/trainee_engagements/${allUserId}/${user_profile_id}/${newId}`,
                staffLink: `/staff/trainee_engagements/${allUserId}/${user_profile_id}/${newId}`
              }
            },
            onCompleted(data) {
              if (data?.createNotification?.data.id) {
                message.success("Notification Created Successfully");
              }
            }
          });
        }
        setIsModalVisible(false);
      },
      onError: () => {
        setIsModalVisible(false);
      }
    });
  }

  if(error) return <ServerError />
  if(!processedJobCard) return <NoFile />

  return (
    <Row gutter={16} className="mt-32" justify="center">
      <TraineeExpandDetailHeader/>
        <Col xs={24} lg={20} xxl={16} className="expand-details-container">
          {
            loading || dataLoading ? <StaffDataLoader />:
            <Tabs 
              className="expand-details-container-tab"
              defaultActiveKey={expandDetailsTabs}
              items={items}
              tabPosition="top"
              onChange={(key) => dispatch(setExpandDetailsTabs(key))}
              style={{ background: "white" }}
            />
            }
      </Col>
     
      <Modal
        title={<div className="dark-orange-color"><h3>Have you applied for this job?</h3></div>}
        open={isModalVisible}
        onOk={handleOk}
        onCancel={handleCancel}
        footer={null}>
         {processedJobCard ?
          <Row gutter={16} justify="center">
            <Col span={24}>
                <Card className="mt-16" style={{background:"#F5F5F5"}}>
                    <h4>{ processedJobCard.cards.match_attributes?.title &&  processedJobCard.cards.match_attributes?.title}</h4>
                       <div className="flex-center gap-8 mt-16">
                       <Avatar shape="square" size="small" className="work-experience-logo">
                          {jobTitle?.charAt(0).toUpperCase()}
                        </Avatar>
                        <p>{processedJobCard.cards?.company_name}</p>
                       </div>
                    </Card>
                    <div className="mt-16 flex-center gap-16">
                    <Button 
                        onClick={handleStatusSubmission}
                        loading={loading}
                        className="dark-orange-bg white-color">
                        Yes I did
                      </Button>
                      <Button 
                        onClick={handleCancel}
                        className="white-bg dark-color">
                          No
                      </Button>
                    </div>
                </Col>
          </Row>
          : null
        }
      </Modal>
    </Row>
  )
  
}
