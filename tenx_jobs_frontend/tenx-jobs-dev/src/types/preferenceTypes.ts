import { History } from "./updated_profile";

export type Priorities = "low" | "high" | "medium";

export type T_TagsAndPriority = {
  name: string;
  priority: "high" | "medium" | "low";
};

export type T__Match = {
  ujc_score_threshold: number | string;
  rating_score_threshold: number | string;
  preference_score_threshold: number | string;
};

export type T_KeywordsItems = {
  tools: string[];
  skills: string[];
  abilities: string[];
  knowledge: string[];
  certificates: string[];
};

export type T_LocationPreference = {
  city: string;
  state: string;
  country: string;
  priority: string;
};

export type T_SalaryRangePreference = {
  unit: string;
  currency: string;
  maximum_salary: string | number;
  minimum_salary: string | number;
};

export type T_UserPrefJobs = {
  uuid: string;
  status: string;
  days_since_extracted: number;
  role: T_TagsAndPriority[];
  match: T__Match;
  history: History[];
  industry: T_TagsAndPriority[];
  keywords_include: T_KeywordsItems;
  keywords_exclude: T_KeywordsItems;
  locations: T_LocationPreference[];
  education: T_TagsAndPriority[];
  company_size: T_TagsAndPriority[];
  salary_range: T_SalaryRangePreference;
  employment_type: T_TagsAndPriority[];
  experience_level: T_TagsAndPriority[];
};

export type T_ResumePref = {
  max_page: string;
  template_id: string;
  max_projects: string;
  template_name: string;
  max_work_experience: string;
};

export type T_CoverLetter = {
  max_page: string | number;
};

export type T_UserPrefAssets = {
  uuid: string;
  resume: T_ResumePref;
  status: string;
  history: History[];
  cover_letter: T_CoverLetter;
};

export type T_VisibilityPref = {
  name: string;
  default: boolean;
  description: string;
};

export type T_UserSystemPref = {
  uuid: string;
  status: string;
  history: History[];
  visibility: T_VisibilityPref[];
};

export type T_Frequency = {
  uuid: string;
  status: string;
  history: History[];
  fun_cards: Priorities;
  job_cards: Priorities;
  info_cards: Priorities;
  non_matches: Priorities;
};

export type T_UserPreferenceAttrib = {
  name: string;
  display: string;
  description: string;
  profile_type: string;
  jobs: T_UserPrefJobs;
  assets: T_UserPrefAssets;
  system: T_UserSystemPref;
  frequency: T_Frequency;
};

export type T_UserPreference = {
  name: string;
  display: string;
  description: string;
  profile_type: string;
  jobs: T_UserPrefJobs;
  assets: T_UserPrefAssets;
  system: T_UserSystemPref;
  frequency: T_Frequency;
};

export type T_Preference = {
  all_user_id: string;
  user_preference_id: string;
  user_preference: T_UserPreference;
  status: string;
  message: string;
};

export type PrioritySettingType = {
  name: string;
  priority: "high" | "medium" | "low" | null;
};


export type KeywordObject = {
  tools: string[];
  skills: string[];
  abilities: string[];
  knowledge: string[];
  certificates: string[];
}

export type CombinedKeyword = {
  category: keyof KeywordObject;
  item: string;
  type?: 'include' | 'exclude';
}
