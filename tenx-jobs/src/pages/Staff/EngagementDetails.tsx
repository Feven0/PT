import { useEffect, useState } from 'react';
import { setStaffEngagementDetailsTab } from "../../redux/slices/tabsSlice";
import { Row, Col, Card, TabsProps, Tabs } from 'antd';
import { useAppSelector, useAppDispatch } from '../../redux/hooks/hooks';
import EngagementDetailsHeader from '../../components/Staff/Engagement/EngagementDetailHeader';
import EngagementDetailData from '../../components/Staff/Engagement/EngagementDetailData';
import { useParams } from 'react-router-dom';
import ServerError from '../../components/commonComponents/ServerError';
import Assets from '../../components/Trainee/MatchDetails/Assets';
import StaffDataLoader from '../../components/commonComponents/StaffDataLoader';
import TraineeMatchDetails from "../../components/Trainee/TraineeMatchDetails";
import { Stats } from "../../redux/slices/userStatsSlice";
import { T_JobCardExpandReaction, T_MatchDetails, TProcessedJobCard } from "../../types/expandReactionTypes";
import useAxiosRequest from "../../hooks/useAxiosRequest";
import { getRunStage } from "../../utils/getRunStage";

const run_stage = getRunStage();

export default function EngagementDetails() {
  const dispatch = useAppDispatch();
  const [response, setResponse] = useState<any>(null)
    const { user_reaction_id,all_user_id } = useParams()
    const { staffEngagementDetailsTab } = useAppSelector((state) => state.tabs);
    const { user_role } = useAppSelector((state) => state.leapProfileId)
    const asset = response?.infocards?.leap_profile_card
    const { makeRequest, loading, error } = useAxiosRequest();
    const isExpansions = true;

    const onChange = (key: string) => dispatch(setStaffEngagementDetailsTab(key));

    const getEngagementDetail = () => {
      const data = {
        user_role: user_role,
        run_stage: run_stage,
        all_user_id: all_user_id,
        user_reaction_id: user_reaction_id,
        information_level: "minimal",
      };
  
      makeRequest({
        url: '/sjob/get-expanded-reaction',
        method: 'POST',
        data,
        onSuccess: (response) => {
          if(response.status === 200) {
          setResponse(response.data)
          }
        },
        onError: () => { },
      });
    };
  
    useEffect(() => {
        getEngagementDetail()
    }, [user_reaction_id])

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
            match_detail: response?.infocards?.job_profile_card?.match_attributes?.match_detail?.map((detail:T_MatchDetails, index:number) => ({
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
            label: 'Engagement Data',
            children: <EngagementDetailData response={response} refetch={getEngagementDetail}/>,
        },
        {
            key: '2',
            label: 'Match Details',
            children: response? <TraineeMatchDetails
            isExpansion={isExpansions} 
            transformedMatchDetail={processedJobCard.cards.match_attributes} 
            columns={columns} />
            : <StaffDataLoader />
        },
        {
            key: '3',
            label: 'Asset',
            children:  <Assets file={asset}/>
        }
    ];
    
    if (error || response?.status === 400)  return <ServerError />

  return (
    <Row gutter={16} style={{ marginTop: "3rem" }} justify="center">
        <EngagementDetailsHeader />
        <Col xs={24} lg={20} xxl={16}>
            <Card className="engagement-card-container">
                {
                    loading || !response ? (
                        <StaffDataLoader  />
                    ) :
                    <Tabs
                        defaultActiveKey={staffEngagementDetailsTab}
                        items={items}
                        onChange={onChange} 
                    />
                }
            </Card>
        </Col>
    </Row>
  )
}
