import { useEffect, useState } from "react";
import { Card, Col, Row } from "antd";

// Components
import AllJobs from "../../components/Trainee/AllJobs";
import ServerError from "../../components/commonComponents/ServerError";

// Redux and custom hooks
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import { setCards, setRedisListId } from "../../redux/slices/jobCardSlice";
import { setUserState } from "../../redux/slices/userStatsSlice";
import { setUserProfileId } from "../../redux/slices/leapProfileIdSlice";
import useAxiosRequest from "../../hooks/useAxiosRequest";

// Styles
import { getRunStage } from "../../utils/getRunStage";
import '../../styles/slidingCard.css'

const run_stage = getRunStage();

export default function Jobs() {
  const [response, setResponse] = useState<any>(null);
  const { cards } = useAppSelector((state) => state.jobCard);
  const { user_profile_id, allUserId, user_role } = useAppSelector((state) => state.leapProfileId);
  const { days } = useAppSelector((state) => state.updateSince);
  const { contentCollapsed } = useAppSelector((state) => state.tabs);

  const dispatch = useAppDispatch();
  const { makeRequest, error } = useAxiosRequest();

  const getUserProfileID = () => {
    if (allUserId) {
      makeRequest({
        url: '/sjob/get-user-profile-id',
        method: 'POST',
        data: {
          user_role: user_role,
          all_user_id: allUserId,
          profile_type: "other",
          filter: {},
          run_stage: run_stage,
        },
        onSuccess: (response) => {
          if (response?.data) {
            setResponse(response.data);
          }
        },
        onError: () => { },
      });
    }
  };
  

  useEffect(() => {
    getUserProfileID();
  }, [])

  useEffect(() => {
    if (response) {
      dispatch(setUserProfileId(response?.user_profile_id));
    }
  }, [response]);

  useEffect(() => {
    const fetchCardData = async() => {
      const data = {
        all_user_id: allUserId,
        user_role: user_role,
        user_profile_id: user_profile_id,
        session_id: "",
        topic_type: "job",
        resend: false,
        since: days,
        filter: {},
        run_stage: run_stage,
      };

      makeRequest({
        url: '/sjob/get-job-cards',
        method: 'POST',
        data,
        onSuccess: (response) => {
          if (response?.data?.cards) {
            dispatch(setCards(response.data.cards));
            dispatch(setUserState(response.data.stats));
            dispatch(setRedisListId(response.data.redis_id_list[0]));
          }
        },
        onError: () => {},
      });
    };

    if (user_profile_id !== '0') {
      if (cards.length === 0) {
        user_profile_id && fetchCardData();
      }
    } else {
      getUserProfileID();
    }
  }, [user_profile_id, days]);


  if (error) return <ServerError />

  return (
    <Row gutter={[16, 16]} justify="center">
      <Col xs={24} lg={20} xxl={contentCollapsed ? 16 : 18} style={{ background: "whitesmoke" }}>
        <Card className="tinder-container-card">
          <AllJobs />
        </Card>
      </Col>
    </Row>
  );

}
