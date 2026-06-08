import { useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@apollo/client';
import { persistor } from "../redux/store";

import { reset } from "../redux/slices/userSlices";
import { log } from "../graphql/mutations/Log";
import { setSiderTab } from "../redux/slices/tabsSlice";

interface UseLogoutProps {
  strapiId: number;
}

const useLogout = ({ strapiId }: UseLogoutProps) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [createLog] = useMutation(log);

  const logout = useCallback(() => {
    createLog({ variables: { userId: strapiId, action: 'logout' } });
    dispatch(reset());
    sessionStorage.clear();
    localStorage.clear();
    persistor.pause();
    persistor.flush().then(() => {
      return persistor.purge();
    }).then(() => {
      persistor.persist();
    });
    dispatch(setSiderTab('1'));
    navigate('/login');
  }, [createLog, navigate, persistor, strapiId]);

  return logout;
};

export default useLogout;
