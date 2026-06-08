import type { TabsProps } from 'antd';
import { Button, Card, Col, Divider, message, Popconfirm, Row, Tabs } from "antd";

import LocationPreference from "../../components/Trainee/TraineePreferences/LocationPreference";
import SalaryPreference from "../../components/Trainee/TraineePreferences/SalaryPreference";
import CVTemplate from "../../components/Trainee/TraineePreferences/CVTemplate";
import RolesPreference from "../../components/Trainee/TraineePreferences/RolesPreference";
import MatchingPercentage from "../../components/Trainee/TraineePreferences/MatchingPercentage";
import JobIndustryPreference from "../../components/Trainee/TraineePreferences/JobIndustryPreference";
import EmploymentType from "../../components/Trainee/TraineePreferences/EmploymentType";
import ExperienceLevel from "../../components/Trainee/TraineePreferences/ExperienceLevel";
import CompanySizePreference from "../../components/Trainee/TraineePreferences/CompanySizePreference";
import VisibilitySettings from "../../components/Trainee/TraineePreferences/VisibilitySettings";
import KeywordsToInclude from "../../components/Trainee/TraineePreferences/KeywordsToInclude";
import ServerError from "../../components/commonComponents/ServerError";
import NoFile from "../../components/commonComponents/NoFile";
import KeywordsToExclude from "../../components/Trainee/TraineePreferences/KeywordsToExclude";
import JobFilter from "../../components/Trainee/TraineePreferences/JobFilter";
import EducationPreference from "../../components/Trainee/TraineePreferences/EducationPreference";

import { useFetchUserPreferences } from "../../hooks/useGetUserPreferences";
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import { setPreferenceTab } from "../../redux/slices/tabsSlice";
import { setPreferenceControlTag } from "../../redux/slices/Preferences/preferenceControlSlice";
import useAxiosRequest from "../../hooks/useAxiosRequest";
import { getRunStage } from "../../utils/getRunStage";
import '../../styles/preference.css';

const run_stage = getRunStage();

export default function Preferences() {

  const { company_size } = useAppSelector((state) => state.companySizePreference);
  const { roles } = useAppSelector((state) => state.rolesPreference);
  const { experience_level } = useAppSelector((state) => state.experienceLevelPreference);
  const { employment } = useAppSelector((state) => state.employmentType);
  const { industry } = useAppSelector((state) => state.industryPreference);
  const { locations } = useAppSelector((state) => state.locationPreference);
  const { salary_range } = useAppSelector((state) => state.salaryPreference);
  const { education } = useAppSelector((state) => state.educationPreference);
  const { job_keywords_include } = useAppSelector((state) => state.jobKeywordsInclude);
  const { job_keywords_exclude } = useAppSelector((state) => state.jobKeywordsExclude);
  const { visibility } = useAppSelector((state) => state.visibility);
  const { match } = useAppSelector((state) => state.matchingPercentage);
  const { resume, cover_letter } = useAppSelector((state) => state.resumePreference);
  const { days_extracted } = useAppSelector((state) => state.jobFilter);
  const { allUserId, user_role, trainee_id, user_profile_id, trainee_preference_id } = useAppSelector((state) => state.leapProfileId);
  const {preferenceTab} = useAppSelector((state) => state.tabs);
  const {flag} = useAppSelector((state) => state.preferenceControl);

  const { response, error } = useFetchUserPreferences();
  const dispatch = useAppDispatch();
  const { makeRequest, loading } = useAxiosRequest();

  const handleSaveChanges = () => {
    const user_preference = {
      name: "preferences",
      display: "User Preferences",
      description: "Test User Preferences",
      profile_type: "preferences",
      jobs: {
        role: roles,
        match: {
          ujc_score_threshold: match.ujc_score_threshold,
          rating_score_threshold: match.rating_score_threshold,
          preference_score_threshold: match.preference_score_threshold,
        },
        industry: industry,
        keywords_include: job_keywords_include,
        keywords_exclude: job_keywords_exclude,
        location: locations,
        education: education,
        company_size: company_size,
        salary_range: salary_range,
        employment_type: employment,
        experience_level: experience_level,
        days_since_extracted: days_extracted,
        status: "",
      },
      assets: {
        resume: resume,
        status: "",
        cover_letter: {
          max_page: cover_letter.max_page,
        }
      },
      system: {
        visibility: visibility,
        status: ""
      },
      frequency: {
        status: "",
        fun_cards: "low",
        job_cards: "high",
        info_cards: "low",
        non_matches: "low"
      }
    }
    const data = {
      all_user_id: allUserId,
      user_role: user_role,
      run_stage: run_stage,
      user_profile_id: user_profile_id,
      user_preference_id: trainee_preference_id,
      user_preference: user_preference,
      trainee_id: trainee_id,
      status: ""
    }
    if (data) {
      makeRequest({
        url: '/sjob/post-preference-json-export',
        method: 'POST',
        data,
        onSuccess: (response) => {
          if (response.status === 200) {
            message.success('Preference added successfully');
            dispatch(setPreferenceControlTag(false));
          }
        },
        onError: () => {}
      });
    }
  };

  const items: TabsProps['items'] = [
    {
      key: '1',
      label: 'Job Filter',
      children: <>
        <RolesPreference />
        <Divider />
        <KeywordsToInclude />
        <KeywordsToExclude />
        <CompanySizePreference />
        <EmploymentType />
        <ExperienceLevel />
        <JobIndustryPreference />
        <Divider />
        <JobFilter />
        <EducationPreference />
        <Divider />
        <LocationPreference />
        <SalaryPreference />  
        <Divider />
        <MatchingPercentage />
      </>,
    },
    {
      key: '2',
      label: 'Assets',
      children: <CVTemplate />,
    },
    {
      key: '3',
      label: 'System',
      children: <VisibilitySettings />,
    },
  ];

  const onChange = (key: string) => dispatch(setPreferenceTab(key))

  if (error) return <ServerError />

  return (
    <Row gutter={16} justify="center" className="mt-16 preference-container mb-32">
      <Col xs={24} lg={16} xxl={12}>
        <Card className="full-width mb-16">
          {response ?
            <div className="preference__wrapper">
              <Tabs defaultActiveKey={preferenceTab} items={items} onChange={onChange} />
              <div className="save-preference-btn" style={{ justifyContent: "center" }}>
               {
                flag &&
                <Popconfirm
                title="Are you sure you want to add this preference?"
                onConfirm={() => handleSaveChanges()}
                onCancel={() => {
                  message.info("Preference adding cancelled");
                }}
                okText="Yes"
                cancelText="No">
                <Button className="dark-orange-bg white-color"
                  loading={loading}
                >
                  Apply Filter
                </Button>
              </Popconfirm>
               }
              </div>
            </div>
            : <NoFile />
          }
        </Card>
      </Col>
    </Row>
  );
}