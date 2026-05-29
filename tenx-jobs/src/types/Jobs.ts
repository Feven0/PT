import { TMatchAttributesExp } from "./expandReactionTypes";
import { TinderJobProfileEntityResponseCollection } from "./generated";
import {
  JobRubricEntityResponseCollection,
  JobTraineeEntityResponseCollection,
} from "./generated";

import { JSONSchemaType } from "ajv";

export type TJob = {
  tinderJobProfiles: TinderJobProfileEntityResponseCollection;
};

export type JobHeader = {
  position: string;
  name: string;
  value: string;
  description: string;
  endDate?: string;
};

export type TReactionAttribute = {
  section: string;
  user_reaction: string;
};

export type PageHeader = {
  name: string;
  value: string;
  description: string;
  endDate?: string;
};

export type PageBody = {
  type: string;
  title?: string;
  value: string;
  description: string;
  score: string;
  name?: string;
};

export type TagValue = {
  name: string;
  score: number;
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

export type PageTag = {
  name: string;
  title: string;
  value: TagValue[];
  description: string;
};

export type Page = {
  id: number;
  page_header: PageHeader[];
  page_body: PageBody;
  page_tags: PageTag[];
};

export type CompanyDetail = {
  id: number | string;
  companyName: string;
  title: string;
  link: string;
  description: string;
};

export type JobCard = {
  header: JobHeader[];
  pages: Page[];
  companyDetail: CompanyDetail[];
};

export type CompanyBody = {
  name: string;
  value: string;
  description: string;
  link?: string;
};

export type Company = {
  company_header: string;
  company_body: CompanyBody[];
  company_tags: string[];
};

export type CompanyCard = {
  common_header: string[];
  company: Company[];
};

export type CompanyPage = {
  company_header: string;
  company_body: {
    name: string;
    value: string;
    description: string;
    link?: string;
  };
  company_tags: string[];
};

export type Data = {
  id: number | string;
  version: number;
  "company name": string;
  job_card: JobCard;
  company_card: CompanyCard;
};

export type TPageHeader = {
  name: string;
  value: string;
  position: number;
  description: string;
};

export type TTagValue = {
  name: string;
  score: number;
};

export type TPageTags = {
  name: string;
  title: string;
  value: TTagValue[];
  description: string;
};

export type TPageBody = {
  name: string;
  type: string;
  score: string;
  title: string;
  value: string;
  description: string;
};

export type TJobPage = {
  id: number;
  page_body: TPageBody;
  page_tags: TPageTags[];
  page_header: TPageHeader[];
};

export type TCompanyBody = {
  name: string;
  value: string;
  description: string;
};

export type TCompanyPage = {
  id: number;
  company_body: TCompanyBody;
  company_tags: any[];
  company_header: any[];
};

export type TJobCardHeader = {
  name: string;
  value: string;
  position: number;
  description: string;
};

export type TJobCard = {
  pages: TJobPage[];
  header: TJobCardHeader[];
};

export type TCompanyCardHeader = {
  header: string[];
};

export type TCompanyCardPages = {
  company_body: TCompanyBody[];
  company_tags: string[];
  company_header: string[];
  id: number;
};

export type TCompanyCard = {
  header: TCompanyCardHeader;
  pages: TCompanyCardPages;
};

export type TMatchDetail = {
  confidence: string;
  match_score: string;
  matched_skills: string[];
  missing_skills: string[];
  job_competency_name: string;
  best_matched_user_competency: string;
  job_sfia_level?: string;
  match_degree?: string;
  user_sfia_level?: string;
  ujc_similarity_score?: string;
};

export type TMatchAttrib = {
  level: string;
  title: string;
  applyLink: string;
  rationale: string;
  match_algorithm: string;
  match_summary: string;
  match_detail: TMatchDetail[];
  overall_match_degree: string;
  overall_match_score: string;
  user_job_match_id?: string;
  job_sfia_level?: string;
  user_sfia_level?: string;
  ujc_similarity_score?: string;
};

export type TCards = {
  version: number;
  job_card: TJobCard;
  company_card: TCompanyCard[];
  company_name: string;
  match_attributes: TMatchAttributesExp;
  job_profile_id: string;
};

export type TMatchAttribute = {
  key: string;
  best_matched_user_competency: string;
  confidence: string;
  match_score: string;
  job_competency_name: string;
  matched_skills: string[];
  missing_skills: string[];
  match_summary: string;
  overall_match_score: string;
  overall_match_degree: string;
  rationale: string;
  title: string;
  applyLink: string;
  job_sfia_level?: string;
  user_sfia_level?: string;
  ujc_similarity_score?: string;
};

export type TLeapJobCards = {
  user_profile_id: string;
  cards: TCards[];
  match_attribute: TMatchAttrib;
  status: number;
  message: string;
  redis_list_id: string;
};

export interface CriteriaInterface {
  title: string;
  description?: string | null;
  points: {
    title: string;
    description: string;
    point: number;
  }[];
  value: number;
  total: number;
}

export interface FormCriteriaInterface {
  name: string;
  description?: string | null;
  options?: {
    name: string;
    value: string;
  }[];
  label: string;
  component: string;
  value?: number | string | null | boolean;
}

export type JobContentType = {
  companyName: string;
  link: string;
  description: string;
  Platform: string;
  title: string;
  slug: string;
  id: string;
  avatar: string;
};
export type JobTraineesType = {
  status: string;
  Tag: string;
  slug: string;
  id: string;
};

export type JobTraineeQuery = {
  jobTrainees: JobTraineeEntityResponseCollection;
};
export type JobIDListQuery = {
  jobTrainees: JobTraineeEntityResponseCollection;
};
export type JobStatusType = {
  name: string;
  description: string;
  date: string;
  id: string;
};
export type JobAssetType = {
  name: string;
  type: string;
  id: string;
  username: string;
  updatedAt: string;
};
export type jobRubricsQueryType = {
  jobRubrics: JobRubricEntityResponseCollection;
};
export interface CriteriaInterface {
  title: string;
  description?: string | null;
  points: {
    title: string;
    description: string;
    point: number;
  }[];
  value: number;
  total: number;
}

export const schema: JSONSchemaType<CriteriaInterface[]> = {
  type: "array",
  items: {
    type: "object",
    properties: {
      title: {
        type: "string",
      },
      description: {
        type: "string",
        nullable: true,
      },
      points: {
        type: "array",
        items: {
          type: "object",
          properties: {
            title: {
              type: "string",
            },
            description: {
              type: "string",
            },
            point: {
              type: "integer",
              minimum: 0,
            },
          },
          required: ["title", "description", "point"],
          additionalProperties: false,
        },
      },
      value: {
        type: "integer",
        minimum: -1,
      },
      total: {
        type: "integer",
        minimum: 0,
      },
    },
    required: ["title", "points", "value", "total"],
    additionalProperties: false,
  },
};
export interface FormCriteriaInterface {
  name: string;
  description?: string | null;
  options?: {
    name: string;
    value: string;
  }[];
  label: string;
  component: string;
  value?: number | string | null | boolean;
}
export const FormSchema: JSONSchemaType<FormCriteriaInterface[]> = {
  type: "array",
  items: {
    type: "object",
    properties: {
      name: {
        type: "string",
      },
      description: {
        type: "string",
        nullable: true,
      },
      value: {
        type: ["string", "number", "boolean"],
        nullable: true,
      },
      options: {
        type: "array",
        nullable: true,
        items: {
          type: "object",
          properties: {
            name: {
              type: "string",
            },
            value: {
              type: "string",
            },
          },
          required: ["name", "value"],
          additionalProperties: false,
        },
      },
      label: {
        type: "string",
      },
      component: {
        type: "string",
      },
    },

    required: ["name", "component", "label"],
    additionalProperties: false,
  },
};

export type TLeapProfileCard = {
  "Application Link": string;
  "Generated CV Link": string;
  "Generated Cover Letter Link": string;
  "Google Drive Folder Link": string;
};
