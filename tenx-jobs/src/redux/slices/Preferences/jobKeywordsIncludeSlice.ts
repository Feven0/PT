import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export type KeywordCategory = 'skills' | 'certificates' | 'tools' | 'knowledge' | 'abilities';

type JobKeywordsIncludeState = {
  job_keywords_include: {
    [key in KeywordCategory]: string[];
  };
};

const initialState: JobKeywordsIncludeState = {
  job_keywords_include: {
    skills: [],
    certificates: [],
    tools: [],
    knowledge: [],
    abilities: [],
  },
};

const jobKeywordsIncludeSlice = createSlice({
  name: "jobKeywordsInclude",
  initialState,
  reducers: {
    setJobKeywords_include: (
      state,
      action: PayloadAction<JobKeywordsIncludeState["job_keywords_include"]>
    ) => {
      state.job_keywords_include = action.payload;
    },
    addSkill: (state, action: PayloadAction<string>) => {
      if (!state.job_keywords_include.skills.includes(action.payload)) {
        state.job_keywords_include.skills.push(action.payload);
      }
    },
    removeSkill: (state, action: PayloadAction<string>) => {
      state.job_keywords_include.skills = state.job_keywords_include.skills.filter(
        (skill) => skill !== action.payload
      );
    },
    addCertificate: (state, action: PayloadAction<string>) => {
      if (!state.job_keywords_include.certificates.includes(action.payload)) {
        state.job_keywords_include.certificates.push(action.payload);
      }
    },
    removeCertificate: (state, action: PayloadAction<string>) => {
      state.job_keywords_include.certificates = state.job_keywords_include.certificates.filter(
        (cert) => cert !== action.payload
      );
    },
    addToolsPreference: (state, action: PayloadAction<string>) => {
      if (!state.job_keywords_include.tools.includes(action.payload)) {
        state.job_keywords_include.tools.push(action.payload);
      }
    },
    removeToolsPreference: (state, action: PayloadAction<string>) => {
      state.job_keywords_include.tools = state.job_keywords_include.tools.filter(
        (tool) => tool !== action.payload
      );
    },
    addKnowledgePreference: (state, action: PayloadAction<string>) => {
      if (!state.job_keywords_include.knowledge.includes(action.payload)) {
        state.job_keywords_include.knowledge.push(action.payload);
      }
    },
    removeKnowledgePreference: (state, action: PayloadAction<string>) => {
      state.job_keywords_include.knowledge = state.job_keywords_include.knowledge.filter(
        (knowledge) => knowledge !== action.payload
      );
    },
    addAbilitiesPreference: (state, action: PayloadAction<string>) => {
      if (!state.job_keywords_include.abilities.includes(action.payload)) {
        state.job_keywords_include.abilities.push(action.payload);
      }
    },
    removeAbilitiesPreference: (state, action: PayloadAction<string>) => {
      state.job_keywords_include.abilities = state.job_keywords_include.abilities.filter(
        (ability) => ability !== action.payload
      );
    },
  },
});

export const {
  addSkill,
  removeSkill,
  addCertificate,
  removeCertificate,
  addToolsPreference,
  removeToolsPreference,
  addKnowledgePreference,
  removeKnowledgePreference,
  addAbilitiesPreference,
  removeAbilitiesPreference,
  setJobKeywords_include,
} = jobKeywordsIncludeSlice.actions;

export default jobKeywordsIncludeSlice.reducer;
