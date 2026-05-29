export type Media ={
  icon: string;
  link: string;
  name: string;
}

export type History = {
  user:string,
  timestamp: Date,
  status:string,
  blob?: string
}

export type Location = {
  city: string;
  icon: string;
  region: string;
  address: string;
  country: string;
  postal_code: string;
}

export type TAwardAttributes = {
  date: string;
  uuid: string;
  title: string;
  status: string;
  awarder: string;
  history: History[];
  summary: string;
  url?: string;
}

export type Award = {
  code: string;
  description: string;
  display: string;
  name: string;
  profile_type: string;
  template: string;
  attributes: TAwardAttributes[];
}


export type BasicAttr = {
  role: string;
  uuid: string;
  email: string;
  image: string;
  media: Media[];
  phone: {
    name: string;
    value: string;
  }[];
  status: string;
  history: History[];
  location: Location;
  full_name: string;
  name_title: string;
  personal_statement: string;
}

export type BasicAttribute = {
  attributes: BasicAttr[]
  name: string;
  profile_type: string;
  description: string;
  display: string;
  template: string;
  code: string;
}


export type TProjectAttributes = {
  url: string;
  uuid: string;
  title: string;
  tools: string[];
  status: string;
  history: History[];
  summary: string;
  end_date: string;
  focus_area: string;
  highlights: string[];
  start_date: string;
}
export type ProjectType = {
  attributes: TProjectAttributes[];
  name: string;
  profile_type: string;
  description: string;
  display: string;
  template: string;
  code: string;
}


export type EducationAttributes = {
  uuid: string;
  score: string;
  remark: string;
  status: string;
  country: string;
  courses: string[];
  history: History[];
  end_date: string;
  start_date: string;
  study_area: string;
  study_type: string;
  institution_url: string;
  institution_name: string;
}

export type Education = {
  attributes: EducationAttributes[];
  name: string;
  profile_type: string;
  description: string;
  display: string;
  template: string;
  code: string;
}

export type TVolunteerAttributes = {
  url: string;
  uuid: string;
  status: string;
  history: History[];
  summary: string;
  end_date: string;
  position: string;
  highlights: string[];
  start_date: string;
  organization: string;
}

export type Volunteer ={
  attributes: TVolunteerAttributes[];
  name: string;
  profile_type: string;
  description: string;
  display: string;
  template: string;
  code: string;
}

export type WorkExperienceAttributes = {
  role: string;
  uuid: string;
  status: string;
  company: string;
  history: History[];
  summary: string;
  end_date: string;
  location: string;
  highlights: string[];
  start_date: string;
  company_url: string;
} 

export type WorkExperience = {
  attributes: WorkExperienceAttributes[];
  name: string;
  profile_type: string;
  description: string;
  display: string;
  template: string;
  code: string;
}

export type Section = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: any[];
  description: string;
  profile_type: string;
}

export type TReferences = {
  attributes: any[];
  code: string;
  description: string;
  display: string;
  name: string;
  profile_type: string;
  template: string;
}

export type TPublications = {
  attributes: any[];
  code: string;
  description: string;
  display: string;
  name: string;
  profile_type: string;
  template: string;
}

export type TEvidence = {
  key: string;
  remark: string;
  status: string,
  sentiment: string,
  verified_by: string,
  requested_by: string,
  confidence_degree: string,
  sfia_level_approved:string,
  sfia_level_requested: number | null,
  sfia_dimensions_approved: {name:string,level:number}[],
  sfia_dimensions_requested: {name:string,level:number}[]
  source: {
    name: string;
    link: string;
  };
}

export type TCompetenceAttributes = {
  abilities: string[];
  attitude: string[];
  credibility: string;
  description: string;
  display: string;
  history: History[];
  evidence: TEvidence[];
  knowledge: string[];
  name: string;
  others: string[];
  rationale: string;
  sfia_level: string;
  skills: string[];
  status: string;
  uuid: string;
  sfia_estimation_method: string;
  experience_level: string;

}
export type TCompetencies = {
  attributes:TCompetenceAttributes[];
  code: string;
  description: string;
  display: string;
  name: string;
  profile_type: string;
  template?: string;
}

export type TCertificateAttributes = {
  uuid: string;
  url: string;
  highlights: string[];
  status: string;
  date: string;
  name: string;
  history: History[];
  issuer: string;
}

export type TCertifications = {
  attributes: TCertificateAttributes[];
  code: string;
  description: string;
  display: string;
  name: string;
  profile_type: string;
  template: string;
}

export type TAchievements = {
  attributes: any[];
  code: string;
  description: string;
  display: string;
  name: string;
  profile_type: string;
  template: string;
}

export type TInterests = {
  attributes: any[];
  code: string;
  description: string;
  display: string;
  name: string;
  profile_type: string;
  template: string;
}

export type TLanguageAttributes = {
  fluency: string;
  history: History[];
  language: string;
  status: string;
  uuid: string
}

export type Language = {
  attributes: TLanguageAttributes[];
  code: string;
  description: string;
  display: string;
  name: string;
  profile_type: string;
  template: string;
}

export type TProgrammingLanguages = {
  attributes: any[];
  code: string;
  description: string;
  display: string;
  name: string;
  profile_type: string;
  template: string;
}

export type TUserProfileAttributes = {
  name: string;
  profile_type: string;
  description: string;
  display: string;
  achievements: TAchievements;
  awards: Award;
  certificates: TCertifications;
  competencies: TCompetencies;
  basics: BasicAttribute;
  education: Education;
  projects: ProjectType;
  volunteer: Volunteer;
  work_experience: WorkExperience;
  interests: TInterests;
  languages: Language;
  publications: TPublications;
  references: TReferences;
  programming_languages: TProgrammingLanguages;
}

export type TUserProfileData = {
  all_user_id: string;
  name: string;
  profile_type: string;
  description: string;
  display: string;
  achievements: TAchievements;
  awards: Award;
  certificates: TCertifications;
  competencies: TCompetencies;
  basics: BasicAttribute;
  education: Education;
  projects: ProjectType;
  volunteer: Volunteer;
  work_experience: WorkExperience;
  interests: TInterests;
  languages: Language;
  publications: TPublications;
  references: TReferences;
  programming_languages: TProgrammingLanguages;
  category: string;
  credibility: string;
  summary: string;
  user_profile_id: string;
  title: string;
  metadata: any;
  slug: string;
}

export type SegmentedOption = {
  label: string;
  value: string;
};