import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from "../redux/hooks/hooks";
import { setTraineeResponseProfile } from "../redux/slices/traineeProfileResponseSlice";
import { setEducation } from "../redux/slices/experienceSlice";
import { setPersonalInformation } from "../redux/slices/personalInformationSlice";
import { setMediaForm } from "../redux/slices/setMediaSlice";
import { setContactsForm } from "../redux/slices/setContactsSlice";
import useAxiosRequest from "./useAxiosRequest";
import { getRunStage } from "../utils/getRunStage";

const run_stage = getRunStage();

const useFetchUserProfile = () => {
  const { user_profile_id, allUserId, user_role } = useAppSelector((state) => state.leapProfileId);
  const { info } = useAppSelector((state) => state.personalInformation);
  const { makeRequest, loading, error } = useAxiosRequest();
  const dispatch = useAppDispatch();

  const fetchUserProfile = useCallback(() => {
    const data = {
      user_role,
      run_stage,
      all_user_id: allUserId,
      user_profile_id,
      profile_type: "user_profile",
      filter: {},
    };

    makeRequest({
      url: '/sjob/get-user-profile',
      method: 'POST',
      data,
      onSuccess: (response) => {
        dispatch(setTraineeResponseProfile(response.data));
        dispatch(setEducation(response.data.user_profile.education));

        const personalAttributes = response.data.user_profile.basics.attributes[0];
        dispatch(
          setPersonalInformation({
            info: {
              ...info,
              personal_statement: personalAttributes.personal_statement,
              image: personalAttributes.image,
              id: personalAttributes.uuid,
              full_name: personalAttributes.full_name,
              email: personalAttributes.email,
              role: personalAttributes.role,
              phone: personalAttributes.phone,
              location: personalAttributes.location,
              media: personalAttributes.media,
              name_title: personalAttributes.name_title,
            },
          })
        );

        dispatch(setMediaForm({ media: personalAttributes.media }));
        dispatch(setContactsForm({ phone: personalAttributes.phone }));
      },
      onError: () => {},
    });
  }, [user_role, allUserId, user_profile_id, info]);

  return {fetchUserProfile, loading, error };
};

export default useFetchUserProfile;
