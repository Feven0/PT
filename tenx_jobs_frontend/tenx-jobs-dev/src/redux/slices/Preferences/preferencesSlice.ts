import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { T_Preference } from "../../../types/preferenceTypes";

const initialState: T_Preference = {
  all_user_id: "",
  user_preference_id: "",
  user_preference: {
    name: "",
    display: "",
    description: "",
    profile_type: "",
    jobs: {
      uuid: "",
      status: "",
      days_since_extracted: 0,
      role: [],
      match: {
        ujc_score_threshold: 0,
        rating_score_threshold: 0,
        preference_score_threshold: 0,
      },
      history: [],
      industry: [],
      keywords_include: {
        tools: [],
        skills: [],
        abilities: [],
        knowledge: [],
        certificates: [],
      },
      keywords_exclude: {
        tools: [],
        skills: [],
        abilities: [],
        knowledge: [],
        certificates: [],
      },
      locations: [],
      education: [],
      company_size: [],
      salary_range: {
        unit: "",
        currency: "",
        maximum_salary: "",
        minimum_salary: "",
      },
      employment_type: [],
      experience_level: [],
    },
    assets: {
      uuid: "",
      resume: {
        max_page: "",
        template_id: "",
        max_projects: "",
        template_name: "",
        max_work_experience: "",
      },
      status: "",
      history: [],
      cover_letter: {
        max_page: "",
      },
    },
    system: {
      uuid: "",
      status: "",
      history: [],
      visibility: [],
    },
    frequency: {
      uuid: "",
      status: "",
      history: [],
      fun_cards: "low",
      job_cards: "low",
      info_cards: "low",
      non_matches: "low",
    },
  },
  status: "",
  message: "",
};

const preferenceSlice = createSlice({
  name: "preferences",
  initialState,
  reducers: {
    setPreference(state, action: PayloadAction<T_Preference>) {
      return { ...state, ...action.payload };
    },
    clearPreference() {
      return initialState;
    },
  },
});

export const { setPreference, clearPreference } = preferenceSlice.actions;
export default preferenceSlice.reducer;
