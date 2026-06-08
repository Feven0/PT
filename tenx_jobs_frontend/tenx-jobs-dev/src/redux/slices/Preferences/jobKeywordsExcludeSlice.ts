import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export type KeywordCategory = 'skills' | 'certificates' | 'tools' | 'knowledge' | 'abilities';

type JobKeywordsExcludeState = {
  job_keywords_exclude: {
    [key in KeywordCategory]: string[];
  };
};

const initialState: JobKeywordsExcludeState = {
  job_keywords_exclude: {
    skills: [],
    certificates: [],
    tools: [],
    knowledge: [],
    abilities: [],
  },
};

const jobKeywordsExcludeSlice = createSlice({
  name: "jobKeywordsExclude",
  initialState,
  reducers: {
    setJobKeywords_exclude: (
      state,
      action: PayloadAction<JobKeywordsExcludeState["job_keywords_exclude"]>
    ) => {
      state.job_keywords_exclude = action.payload;
    },
    addSkillExclude: (state, action: PayloadAction<string>) => {
      if (!state.job_keywords_exclude.skills.includes(action.payload)) {
        state.job_keywords_exclude.skills.push(action.payload);
      }
    },
    removeSkillExclude: (state, action: PayloadAction<string>) => {
      state.job_keywords_exclude.skills = state.job_keywords_exclude.skills.filter(
        (skill) => skill !== action.payload
      );
    },
    addCertificateExclude: (state, action: PayloadAction<string>) => {
      if (!state.job_keywords_exclude.certificates.includes(action.payload)) {
        state.job_keywords_exclude.certificates.push(action.payload);
      }
    },
    removeCertificateExclude: (state, action: PayloadAction<string>) => {
      state.job_keywords_exclude.certificates = state.job_keywords_exclude.certificates.filter(
        (cert) => cert !== action.payload
      );
    },
    addToolsPreferenceExclude: (state, action: PayloadAction<string>) => {
      if (!state.job_keywords_exclude.tools.includes(action.payload)) {
        state.job_keywords_exclude.tools.push(action.payload);
      }
    },
    removeToolsPreferenceExclude: (state, action: PayloadAction<string>) => {
      state.job_keywords_exclude.tools = state.job_keywords_exclude.tools.filter(
        (tool) => tool !== action.payload
      );
    },
    addKnowledgePreferenceExclude: (state, action: PayloadAction<string>) => {
      if (!state.job_keywords_exclude.knowledge.includes(action.payload)) {
        state.job_keywords_exclude.knowledge.push(action.payload);
      }
    },
    removeKnowledgePreferenceExclude: (state, action: PayloadAction<string>) => {
      state.job_keywords_exclude.knowledge = state.job_keywords_exclude.knowledge.filter(
        (knowledge) => knowledge !== action.payload
      );
    },
    addAbilitiesPreferenceExclude: (state, action: PayloadAction<string>) => {
      if (!state.job_keywords_exclude.abilities.includes(action.payload)) {
        state.job_keywords_exclude.abilities.push(action.payload);
      }
    },
    removeAbilitiesPreferenceExclude: (state, action: PayloadAction<string>) => {
      state.job_keywords_exclude.abilities = state.job_keywords_exclude.abilities.filter(
        (ability) => ability !== action.payload
      );
    },
  },
});

export const {
  addSkillExclude,
  removeSkillExclude,
  addCertificateExclude,
  removeCertificateExclude,
  addToolsPreferenceExclude,
  removeToolsPreferenceExclude,
  addKnowledgePreferenceExclude,
  removeKnowledgePreferenceExclude,
  addAbilitiesPreferenceExclude,
  removeAbilitiesPreferenceExclude,
  setJobKeywords_exclude,
} = jobKeywordsExcludeSlice.actions;

export default jobKeywordsExcludeSlice.reducer;
