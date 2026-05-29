import { message } from "antd";
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

type TraineeProfileProps = {
  user_profile_id: string | undefined;
  allUserID: string | undefined | number | null;
}

const useFetchTraineeProfileForStaff = ({ allUserID, user_profile_id }: TraineeProfileProps) => {
  const { user_role } = useAppSelector((state) => state.leapProfileId);
  const { info } = useAppSelector((state) => state.personalInformation);

  const dispatch = useAppDispatch();
  const { makeRequest } = useAxiosRequest();
  const fetchUserProfile = useCallback(() => {    
    const data = {
      user_role,
      run_stage,
      all_user_id: allUserID,
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
      onError: (error) => {
        message.error(`Error fetching user profile: ${error}`);
      }
    });
  }, [user_role, run_stage, allUserID, user_profile_id, dispatch]); 

  return fetchUserProfile;
};

export default useFetchTraineeProfileForStaff;
