export type TProjectAttributes = {
  to: string;
  from: string;
  link: string;
  name: string;
  type: string;
  tools:string;
  project_link: string;
  project_description: string[];
}

export type TProjects = {
  code: string;
  name: string;
  display: string;
  attributes: TProjectAttributes[];
  description: string;
  profile_type: string[];
}

export type TEducationAttributes = {
  to: string;
  from: string;
  code: string;
  name: string;
  degree: string;
  display: string;
  coursework: string[];
  university: string;
  description: string;
}

export type TEducation = {
  code: string;
  name: string;
  display: string;
  attributes: TEducationAttributes[];
  description: string;
  profile_type: string[];
}

export type TPreferenceAttributes = {
  role: any[];
  employment_type: string;
  experience_level: string;
  preferable_location: string;
}

export type TPreference = {
  code: string;
  name: string;
  display: string;
  attributes: TPreferenceAttributes;
  description: string;
  profile_type: string[];
}

export type TEvidenceAttributes = {
  remarks: string;
  source: string[];
  sentiment: string;
  reported_by: string;
  confidence_degree: string;
}

export type TSkillSectionAttributes = {
  code: string;
  name: string;
  others: string;
  skills: string[];
  ability: string;
  display: string;
  attitude: string;
  evidence: TEvidenceAttributes[];
  knowledge: string;
  rationale: string;
  sfia_level: string;
  credibility: string;
  description: string;
}

export type TSkillSection = {
  code: string;
  name: string;
  display: string;
  attributes: TSkillSectionAttributes[];
  description: string;
  profile_type: string[];
}

export type TWorkExperienceAttributes = {
  to: string;
  from: string;
  role: string;
  company: string;
  role_description: string;
}

export type TWorkExperience = {
  code: string;
  name: string;
  display: string;
  attributes: TWorkExperienceAttributes[];
  description: string;
  profile_type: string[];
}

export type TMediaAttributes = {
  github: string;
  kaggle: string;
  medium: string;
  dagshub: string;
  devpost: string;
  leetcode: string;
  linkedin: string;
  instagram: string;
}

export type TBasicInformationAttributes = {
  code: string;
  name: string;
  email: string;
  media: TMediaAttributes[];
  phone: string;
  display: string;
  username: string;
  description: string;
  profile_type:string[];
  Personal_statement:string;
}

export type TBasicInformation = {
  code:string;
  name: string;
  display: string;
  attributes: TBasicInformationAttributes[]
  description: string;
  profile_type: string
}

export type TProEducWorkExpAttr = {
  to: string;
  from: string;
  code?: string;
  name?: string;
  degree?: string;
  display?: string;
  coursework?: string[];
  university?: string;
  description?: string;
  link?: string;
  type?: string;
  tools?:string;
  project_link?: string;
  project_description?: string[];
  role?: string;
  company?: string;
  role_description?: string;
}

export type TProEducWorkExp = {
  code: string,
  name: string,
  display: string,
  attributes: TProEducWorkExpAttr[],
  description: string,
  profile_type: string[]
}