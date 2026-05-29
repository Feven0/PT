import { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from "../redux/hooks/hooks";
import { setLocationPreference } from "../redux/slices/Preferences/locationSlices";
import { setIndustryPreference } from "../redux/slices/Preferences/jobIndustrySlice";
import { setPreference } from "../redux/slices/Preferences/preferencesSlice";
import { setRolesPreference } from "../redux/slices/Preferences/rolesSlices";
import { setExperienceLevels } from "../redux/slices/Preferences/experienceLevelSlice";
import { setCompanySizePreference } from "../redux/slices/Preferences/companySizeSlice";
import { setEmploymentTypePreference } from "../redux/slices/Preferences/employmentTypeSlice";
import { setSalary } from "../redux/slices/Preferences/salarySlices";
import { setCoverLetterInfo, setTemplateInfo } from "../redux/slices/Preferences/resumeTemplateSlice";
import { setSystemVisibility } from "../redux/slices/Preferences/systemSlice";
import { setDaysExtracted } from "../redux/slices/Preferences/jobFilterSlice";
import { setSliderValue } from "../redux/slices/Preferences/matchingPercentageSlice";
import { setJobKeywords_include } from "../redux/slices/Preferences/jobKeywordsIncludeSlice";
import { setJobKeywords_exclude } from "../redux/slices/Preferences/jobKeywordsExcludeSlice";
import useAxiosRequest from "./useAxiosRequest";
import { getRunStage } from "../utils/getRunStage";
import { setEducationPreference } from "../redux/slices/Preferences/educationPreferenceSlice";

export function useFetchUserPreferences() {
  const [response, setResponse] = useState<any>(null);
  const dispatch = useAppDispatch();
  const { allUserId, user_role, user_profile_id } = useAppSelector((state) => state.leapProfileId);
  const { makeRequest, error } = useAxiosRequest()

  useEffect(() => {
    if (allUserId && user_profile_id) {
      makeRequest({
        url: '/sjob/get-user-preference',
        method: 'POST',
        data: {
          user_role,
          run_stage: getRunStage(),
          all_user_id: allUserId,
          user_profile_id: user_profile_id,
          user_preference_id: '',
          profile_type: 'user_preference',
          filter: {},
        },
        onSuccess: (response) => {
          if(response?.status === 200){
            setResponse(response.data);
          }
        },
        onError: () => {},
      });
    }
  }, [allUserId, user_profile_id]);

  useEffect(() => {
    if (response) {
      dispatch(setPreference(response));
      const locations = response?.user_preference?.jobs.location || [];
      const industry = response?.user_preference?.jobs?.industry || [];
      const keywords_include = response?.user_preference?.jobs.keywords_include || { skills: [], certificates: [], tools: [], knowledge: [], abilities: [] };
      const keywords_exclude = response?.user_preference?.jobs.keywords_exclude || { skills: [], certificates: [], tools: [], knowledge: [], abilities: [] };
      const roles = response?.user_preference?.jobs?.role || [];
      const companySize = response?.user_preference?.jobs?.company_size || [];
      const experience_level = response?.user_preference?.jobs?.experience_level || [];
      const employment_type = response?.user_preference?.jobs?.employment_type || [];
      const salary_range = response?.user_preference?.jobs?.salary_range || {};
      const resume = response?.user_preference?.assets?.resume || {};
      const visibility = response?.user_preference?.system?.visibility || {};
      const days_since_extracted = response?.user_preference?.jobs?.days_since_extracted || 5;
      const matches = response?.user_preference?.jobs?.match || {};
      const cover_letter = response?.user_preference?.assets?.cover_letter || {};
      const education = response?.user_preference?.jobs?.education || [];
      dispatch(setLocationPreference(locations));
      dispatch(setIndustryPreference(industry));
      dispatch(setJobKeywords_include(keywords_include))
      dispatch(setJobKeywords_exclude(keywords_exclude))
      dispatch(setRolesPreference(roles));
      dispatch(setExperienceLevels(experience_level));
      dispatch(setCompanySizePreference(companySize));
      dispatch(setEmploymentTypePreference(employment_type));
      dispatch(setSalary(salary_range));
      dispatch(setTemplateInfo(resume));
      dispatch(setSystemVisibility(visibility));
      dispatch(setDaysExtracted(days_since_extracted));
      dispatch(setSliderValue(matches))
      dispatch(setCoverLetterInfo(cover_letter));
      dispatch(setEducationPreference(education));
    }
  }, [response]);

  return { response, error };
}
