// src/redux/slices/userProfileSlice.ts
import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import {
  Award,
  BasicAttribute,
  Education,
  Language,
  ProjectType,
  TAchievements,
  TCertifications,
  TCompetencies,
  TInterests,
  TProgrammingLanguages,
  TPublications,
  TReferences,
  Volunteer,
  WorkExperience,
} from "../../types/updated_profile";

// Define types for the state
export type userProfileTypes = {
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
};

// Define initial state
const initialState: userProfileTypes = {
  achievements: {
    attributes: [],
    code: "",
    description: "",
    display: "",
    name: "",
    profile_type: "",
    template: "",
  },
  awards: {
    code: "",
    description: "",
    display: "",
    name: "",
    profile_type: "",
    template: "",
    attributes: [],
  },
  certificates: {
    attributes: [],
    code: "",
    description: "",
    display: "",
    name: "",
    profile_type: "",
    template: "",
  },
  competencies: {
    attributes: [],
    code: "",
    description: "",
    display: "",
    name: "",
    profile_type: "",
    template: "",
  },
  basics: {
    attributes: [],
    name: "",
    profile_type: "",
    description: "",
    display: "",
    template: "",
    code: "",
  },
  education: {
    attributes: [],
    name: "",
    profile_type: "",
    description: "",
    display: "",
    template: "",
    code: "",
  },
  projects: {
    attributes: [],
    name: "",
    profile_type: "",
    description: "",
    display: "",
    template: "",
    code: "",
  },
  volunteer: {
    attributes: [],
    name: "",
    profile_type: "",
    description: "",
    display: "",
    template: "",
    code: "",
  },
  work_experience: {
    attributes: [],
    name: "",
    profile_type: "",
    description: "",
    display: "",
    template: "",
    code: "",
  },
  interests: {
    attributes: [],
    code: "",
    description: "",
    display: "",
    name: "",
    profile_type: "",
    template: "",
  },
  languages: {
    attributes: [],
    code: "",
    description: "",
    display: "",
    name: "",
    profile_type: "",
    template: "",
  },
  publications: {
    attributes: [],
    code: "",
    description: "",
    display: "",
    name: "",
    profile_type: "",
    template: "",
  },
  references: {
    attributes: [],
    code: "",
    description: "",
    display: "",
    name: "",
    profile_type: "",
    template: "",
  },
  programming_languages: {
    attributes: [],
    code: "",
    description: "",
    display: "",
    name: "",
    profile_type: "",
    template: "",
  },
};

// Create the slice
const userProfileSlice = createSlice({
  name: "userProfileData",
  initialState,
  reducers: {
    setAchievements: (state, action: PayloadAction<TAchievements>) => {
      state.achievements = action.payload;
    },
    setAwards: (state, action: PayloadAction<Award>) => {
      state.awards = action.payload;
    },
    setCertificates: (state, action: PayloadAction<TCertifications>) => {
      state.certificates = action.payload;
    },
    setCompetencies: (state, action: PayloadAction<TCompetencies>) => {
      state.competencies = action.payload;
    },
    setBasics: (state, action: PayloadAction<BasicAttribute>) => {
      state.basics = action.payload;
    },
    setEducation: (state, action: PayloadAction<Education>) => {
      state.education = action.payload;
    },
    setProjects: (state, action: PayloadAction<ProjectType>) => {
      state.projects = action.payload;
    },
    setVolunteer: (state, action: PayloadAction<Volunteer>) => {
      state.volunteer = action.payload;
    },
    setWorkExperience: (state, action: PayloadAction<WorkExperience>) => {
      state.work_experience = action.payload;
    },
    setInterests: (state, action: PayloadAction<TInterests>) => {
      state.interests = action.payload;
    },
    setLanguages: (state, action: PayloadAction<Language>) => {
      state.languages = action.payload;
    },
    setPublications: (state, action: PayloadAction<TPublications>) => {
      state.publications = action.payload;
    },
    setReferences: (state, action: PayloadAction<TReferences>) => {
      state.references = action.payload;
    },
    setProgrammingLanguages: (
      state,
      action: PayloadAction<TProgrammingLanguages>
    ) => {
      state.programming_languages = action.payload;
    },
  },
});

export const {
  setAchievements,
  setAwards,
  setCertificates,
  setCompetencies,
  setBasics,
  setEducation,
  setProjects,
  setVolunteer,
  setWorkExperience,
  setInterests,
  setLanguages,
  setPublications,
  setReferences,
  setProgrammingLanguages,
} = userProfileSlice.actions;

export default userProfileSlice.reducer;
