import { useCallback } from 'react';
import { message } from "antd";
import { useAppDispatch, useAppSelector } from "../redux/hooks/hooks";
import { setTraineePreferenceId } from "../redux/slices/leapProfileIdSlice";
import useAxiosRequest from "./useAxiosRequest";
import { getRunStage } from "../utils/getRunStage";

const useFetchUserPreferenceID = () => {
  const { allUserId, user_role } = useAppSelector((state) => state.leapProfileId);
  const { makeRequest } = useAxiosRequest();
  const dispatch = useAppDispatch();

  const fetchUserPreferenceID = useCallback(() => {
    const data = {
      user_role,
      run_stage: getRunStage(),
      all_user_id: allUserId,
      profile_type: "user_preference",
      filter: {},
    };

    makeRequest({
      url: '/sjob/get-user-preference-id',
      method: 'POST',
      data,
      onSuccess: (response) => {
        dispatch(setTraineePreferenceId(response.data.user_preference_id));
      },
      onError: (error) => {
        message.error(`Error fetching user preference ID: ${error}`);
      },
    });
  }, [user_role, allUserId, dispatch]);

return fetchUserPreferenceID;
};

export default useFetchUserPreferenceID;
