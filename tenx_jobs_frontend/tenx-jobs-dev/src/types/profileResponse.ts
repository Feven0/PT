export type T_History = {
  timestamp: string;
  user: string;
  status: string;
  blob: string;
};

export type T_TraineeAwardAttributes = {
  uuid: string;
  url?: string;
  title: string;
  awarder: string;
  history: T_History[];
  summary: string;
  verified_by: string;
  requested_by: string;
  date: string;
  status: string;
};

export type T_TraineeAward = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: T_TraineeAwardAttributes[];
  description: string;
  profile_type: string;
};

export type T_TraineeLocation = {
  country: string;
  address: string;
  city: string;
  region: string;
  postal_code: string;
  icon?: string;
};

export type T_TraineePhone = {
  name: string;
  value: string;
  icon?: string;
};
export type T_TraineeMedia = {
  name: string;
  link: string;
  icon?: string;
};

export type T_TraineeBasicsAttributes = {
  uuid: string;
  full_name: string;
  email: string;
  role: string;
  personal_statement: string;
  verified_by: string;
  requested_by: string;
  status: string;
  name_title: string;
  image: string;
  phone: T_TraineePhone[];
  location: T_TraineeLocation;
  media: T_TraineeMedia[];
  history: T_History[];
};

export type T_TraineeBasics = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: T_TraineeBasicsAttributes[];
  description: string;
  profile_type: string;
};

//Projects
export type T_TraineeProjectsAttributes = {
  uuid: string;
  title: string;
  url?: string;
  status: string;
  summary: string;
  start_date: string;
  end_date: string;
  focus_area: string;
  highlights: string[];
  verified_by: string;
  requested_by: string;
  tools: string[];
  history: T_History[];
};

export type T_TraineeProjects = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: T_TraineeProjectsAttributes[];
  description: string;
  profile_type: string;
};

//Education

export type T_TraineeEducationAttributes = {
  uuid: string;
  score: string;
  remark: string;
  status: string;
  country: string;
  courses: string[];
  end_date: string;
  start_date: string;
  study_area: string;
  study_type: string;
  verified_by: string;
  requested_by: string;
  institution_url: string;
  institution_name: string;
  history: T_History[];
};

export type T_TraineeEducation = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: T_TraineeEducationAttributes[];
  description: string;
  profile_type: string;
};

//Work Experience
export type T_TraineeWorkExperienceAttributes = {
  role: string;
  uuid: string;
  status: string;
  company: string;
  history: T_History[];
  summary: string;
  end_date: string;
  location: string;
  highlights: string[];
  start_date: string;
  company_url: string;
  verified_by: string;
  requested_by: string;
};

export type T_TraineeWorkExperience = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: T_TraineeWorkExperienceAttributes[];
  description: string;
  profile_type: string;
};

//Competencies
export type T_TraineeSfia_dimension = {
  name: string;
  level: number;
};

export type T_TraineeCompetencyEvidenceSource = {
  name: string;
  link?: string;
};

export type T_EvidenceMessage = {
  content: string;
  role: string;
  timestamp: string;
};

export type T_TraineeCompetencyEvidence = {
  key?: string;
  remark: string;
  source: T_TraineeCompetencyEvidenceSource;
  status: string;
  sentiment: string;
  verified_by: string;
  requested_by: string;
  confidence_degree: string;
  sfia_level_approved: number | string | null;
  sfia_level_requested: number | string | null;
  sfia_dimensions_approved: T_TraineeSfia_dimension[];
  sfia_dimensions_requested: T_TraineeSfia_dimension[];
  message?: T_EvidenceMessage[];
};

export type T_TraineeCompetenciesAttributes = {
  uuid: string;
  name: string;
  others: string[];
  skills: string[];
  status: string;
  attitude: string[];
  display: string;
  history: T_History[];
  evidence: T_TraineeCompetencyEvidence[];
  abilities: string[];
  knowledge: string[];
  rationale: string;
  sfia_level: string;
  description: string;
  verified_by: string;
  requested_by: string;
  experience_level: string;
  sfia_estimation_method: string;
  credibility: string;
};

export type T_TraineeCompetencies = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: T_TraineeCompetenciesAttributes[];
  description: string;
  profile_type: string;
};

//Interests
export type T_TraineeInterests = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: any[];
  description: string;
  profile_type: string;
};

//Certificates
export type T_TraineeCertificatesAttributes = {
  uuid: string;
  date: string;
  name: string;
  issuer: string;
  status: string;
  history: T_History[];
  verified_by: string;
  requested_by: string;
  url?: string;
};

export type T_TraineeCertificates = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: T_TraineeCertificatesAttributes[];
  description: string;
  profile_type: string;
};

//Languages
export type T_TraineeLanguagesAttributes = {
  uuid: string;
  status: string;
  fluency: string;
  history: T_History[];
  language: string;
  verified_by: string;
  requested_by: string;
};

export type T_TraineeLanguages = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: T_TraineeLanguagesAttributes[];
  description: string;
  profile_type: string;
};

//Volunteer
export type T_TraineeVolunteerAttributes = {
  uuid: string;
  url?: string;
  status: string;
  history: T_History[];
  summary: string;
  end_date: string;
  position: string;
  highlights: string[];
  start_date: string;
  verified_by: string;
  organization: string;
  requested_by: string;
};
export type T_TraineeVolunteer = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: T_TraineeVolunteerAttributes[];
  description: string;
  profile_type: string;
};

//References
export type T_TraineeReferenceContact = {
  full_name: string;
  email: string;
  relationship: string;
  phone: string[];
  remark: string[];
};
export type T_ReferenceAttributes = {
  uuid: string;
  priority: number;
  reference_text: string;
  contact: T_TraineeReferenceContact[];
};
export type T_TraineeReferences = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: T_ReferenceAttributes[];
  description: string;
  profile_type: string;
};

//Publications
export type T_TraineePublicationsAttributes = {
  uuid: string;
  name: string;
  publisher: string;
  release_date: string;
  summary: string;
  url: string;
  history: T_History[];
};

export type T_TraineePublications = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: T_TraineePublicationsAttributes[];
  description: string;
  profile_type: string;
};

//Achievements
export type T_TraineeAchievementsAttributes = {
  uuid: string;
  title: string;
  summary: string;
  date: string;
  history: T_History[];
};

export type T_TraineeAchievements = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: T_TraineeAchievementsAttributes[];
  description: string;
  profile_type: string;
};

//Programming Languages
export type T_TraineeProgrammingLanguagesAttributes = {
  uuid: string;
  name: string;
  level: string;
  history: T_History[];
};
export type T_TraineeProgrammingLanguages = {
  code: string;
  name: string;
  display: string;
  template: string;
  attributes: T_TraineeProgrammingLanguagesAttributes[];
  description: string;
  profile_type: string;
};

export type T_TraineeProfile = {
  name: string;
  display: string;
  description: string;
  profile_type: string;
  awards: T_TraineeAward;
  basics: T_TraineeBasics;
  projects: T_TraineeProjects;
  education: T_TraineeEducation;
  work_experience: T_TraineeWorkExperience;
  competencies: T_TraineeCompetencies;
  interests: T_TraineeInterests;
  certificates: T_TraineeCertificates;
  languages: T_TraineeLanguages;
  volunteer: T_TraineeVolunteer;
  references: T_TraineeReferences;
  publications: T_TraineePublications;
  programing_languages: T_TraineeProgrammingLanguages;
  achievements: T_TraineeAchievements;
};

export type T_TraineeProfileResponse = {
  all_user_id: string;
  user_profile_id: string;
  user_profile: T_TraineeProfile;
  status: number;
  message: string;
};
