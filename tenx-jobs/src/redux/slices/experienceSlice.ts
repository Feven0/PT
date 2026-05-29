import {PayloadAction, createSlice } from "@reduxjs/toolkit";

type WorkExperience = {
  id: string
  role: string
  company: string
  duration: [string, string | null]
  description: string
  location?: string
}

export type TEducation = {
  id:string
  school: string
  duration: [string, string | null]
  coursework: string[]
  description: string
  institution_url?: string
  study_area: string
  study_type: string
  country: string
  degree?: string
  score?: string
}

export type TEvidence = {
  remark: string;
  source: string[];
  sentiment: string;
  reported_by: string;
  confidence_degree: string;
  sfia_level_requested: number | null | string
}

export type TProject = {
  id: string,
  duration: [string, string | null],
  link: string,
  name: string,
  type: string,
  tools: string[],
  project_link: string,
  project_description: string[],
  description?: string,
  focus_area?: string,
  title?: string,
  url?: string,
}

export type TSkill = {
  display: string;
  individualSkills: string[];
};

export type TProfile ={
  experience: WorkExperience
  education: TEducation
  feedbackText: string
  checkedValue: string
  userBio: string,
  project: TProject,
  skill: TSkill;
  evidence: TEvidence;
  match_status: string,
}

const initialState: TProfile = {
  experience: {
    id: "",
    role: "",
    company: "",
    duration: ["", ""],
    description: "",
    location: "",
  },
  education: {
    id:"",
    school: "",
    degree: "",
    duration: ["", ""],
    coursework: [],
    description: "",
    institution_url: "",
    study_area: "",
    study_type: "",
    country: "",
  },

  project: {
    id: "",
    duration: ["", ""],
    link: "",
    name: "",
    type: "",
    tools: [],
    project_link: "",
    project_description: [],
    description: ""
  },

  skill: {
    display: "",
    individualSkills: [],
  },

  evidence: {  
    remark: "",
    source: [],
    sentiment: "",
    reported_by: "",
    confidence_degree: "",
    sfia_level_requested: 1
  },

  feedbackText: "",
  checkedValue: "not_interested",
  userBio: "",
  match_status: "like",
}

export const experienceSlice = createSlice({
  name: "experience",
  initialState,
  reducers: {
    setExperience: (state, action: PayloadAction<Partial<TProfile['experience']>>) => {
      state.experience = {
        ...state.experience,
        ...action.payload,
      };
    },
    setEducation: (state, action: PayloadAction<Partial<TProfile['education']>>) => {
      state.education = {
        ...state.education,
        ...action.payload,
      };
    },

    setProject: (state, action: PayloadAction<Partial<TProfile['project']>>) => {
      state.project = {
        ...state.project,
        ...action.payload,
      };
    },

    setSkill: (state, action: PayloadAction<Partial<TProfile["skill"]>>) => {
      state.skill = {
        ...state.skill,
        ...action.payload,
      };
    },

    setEvidence: (state, action: PayloadAction<Partial<TProfile["evidence"]>>) => {
      state.evidence = {
        ...state.evidence,
        ...action.payload,
      };
    },

    setFeedbackText: (state, action: PayloadAction<string>) => {
      state.feedbackText = action.payload
    },
    setCheckedValue: (state, action: PayloadAction<string | undefined>) => {
      state.checkedValue = action.payload ?? "not_interested";
    },

    setUserBio: (state, action: PayloadAction<string>) => {
      state.userBio = action.payload
    },

    setMatchStatus: (state, action) => {
      state.match_status = action.payload;
    },
    clearMatchStatus: (state) => {
      state.match_status = '';
    },

    resetCheckedValue: (state) => {
      state.checkedValue = "not_interested";
    },

    resetExperience: (state) => {
      state.experience = {
        id: "",
        role: "",
        company: "",
        duration: ["", ""],
        description: "",
        location: "",
      }
    },
    resetEducation: (state) => {
      state.education = {
        id: "",
        school: "",
        degree: "",
        duration: ["", ""],
        coursework: [],
        description: "",
        institution_url: "",
        study_area: "",
        study_type: "",
        country: "",
      }
  },

  resetProject: (state) => {
    state.project = {
      id: "",
      duration: ["", ""],
      link: "",
      name: "",
      type: "",
      tools: [],
      project_link: "",
      project_description: [],
      description: ""
    }
  },

  resetSkill: (state) => {
    state.skill = {
      display: "",
      individualSkills: [],
    };
  },

  resetEvidence: (state) => {
    state.evidence = {
      remark: "",
      source: [],
      sentiment: "",
      reported_by: "",
      confidence_degree: "",
      sfia_level_requested: 1
    };
  },

  resetBio: (state)=> {
    state.userBio = ""
  },
  }
})

export const { 
            setExperience, 
            resetBio, 
            setUserBio, 
            resetCheckedValue, 
            setCheckedValue, 
            setEducation, 
            setProject,
            setFeedbackText, 
            resetProject,
            resetSkill,
            resetEducation, 
            resetExperience,
            setEvidence,
            resetEvidence,
            setSkill,
            setMatchStatus
          } = experienceSlice.actions
export default experienceSlice.reducer