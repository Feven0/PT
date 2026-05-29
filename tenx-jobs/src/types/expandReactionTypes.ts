import { Stats } from "../redux/slices/userStatsSlice";

export type TJobHeaderPages = {
  company_header: any[];
  company_tags: any[];
  id: string | number;
};

export type TCompanyCardEx = {
  header: any[];
  pages: TJobHeaderPages[];
};

export type T_PageTagsValue = {
  name: string;
  score: number | string;
  type?:
    | "high1"
    | "high2"
    | "high3"
    | "mid4"
    | "mid5"
    | "mid6"
    | "low7"
    | "low8"
    | "low9"
    | "neutral10"
    | "info11";
};

export type T_PageTags = {
  name: string;
  description: string;
  title: string;
  value: T_PageTagsValue[];
};

export type TJopCardExpPages = {
  id: string | number;
  page_body: {
    name: string;
    description: string;
    title: string;
    value: string;
    type: string;
  };
  page_header: any[];
  page_tags: T_PageTags[];
};

export type T_ExpandHeader = {
  name: string;
  position: number;
  value: string;
  description: string;
};

export type TJobCardExp = {
  header: T_ExpandHeader[];
  pages: TJopCardExpPages[];
};

export type T_MatchedSkills = {
  score: string | number | null;
  skill_name: string;
  skill_match: string;
}

export type T_MatchDetails = {
  key: string;
  best_matched_user_competency: string;
  confidence: string;
  job_competency_name: string;
  job_sfia_level: string | number;
  matched_skills: T_MatchedSkills[];
  match_score: string;
  match_degree: string;
  missing_skills: any[];
  ujc_similarity_score: string;
  user_sfia_level: string | number;
};

export type TMatchAttributesExp = {
  applyLink: string;
  level: string;
  match_algorithm: string;
  match_summary: string;
  overall_match_score: string | number;
  overall_match_degree: string;
  rationale: string;
  title: string;
  user_job_match_id: string;
  match_detail: T_MatchDetails[];
};

export type T_JobCardExpandReaction = {
  version: string;
  company_name: string;
  job_card: TJobCardExp;
  company_card: TCompanyCardEx;
  job_profile_id: string;
  job_id: string;
  match_attributes: TMatchAttributesExp;
};

export type TProcessedJobCard = {
  cards: T_JobCardExpandReaction;
  stats: Stats;
};
