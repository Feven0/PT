import { useEffect, useState } from 'react';
import { useAppSelector } from "../redux/hooks/hooks";
import useAxiosRequest from "./useAxiosRequest";
import { getRunStage } from "../utils/getRunStage";

export type CursorType = {
  query?: string;
  filter?: string;
  page?: number;
  page_size?: number;
  total?: number;
  page_count?: number;
};

export type sendResultType = {
  cursor?: CursorType;
  pageSize?: number;
  limit: number;
}

const useUserReactions = () => {
  const [response, setResponse] = useState<any>(null);
  const { allUserId, user_role } = useAppSelector((state) => state.leapProfileId);
  const { makeRequest, loading, error } = useAxiosRequest();

  const sendResult = (limit: number = 30) => {
    makeRequest({
      url: '/sjob/get-all-user-reactions',
      method: 'POST',
      data: {
        all_user_id: allUserId,
        limit: limit,
        since: 0,
        reaction_type: 'all',
        match_type: 'all',
        information_level: 'minimal',
        filter: {},
        run_stage: getRunStage(),
        user_role: user_role,
        cursor: {},
      },
      onSuccess: (response) => {
        if (response?.status === 200) {
          setResponse(response.data);
        }
      },
      onError: () => {},
    });
  };

  useEffect(() => {
    sendResult();
  }, [allUserId, user_role]);

  return {
    loading,
    error,
    response,
    sendResult
  };
};

export default useUserReactions;
