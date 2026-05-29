import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { T_TraineeCompetencyEvidence } from "../../types/profileResponse";

type SfiaDimension = {
  name: string;
  level: number;
};

type Evidence = {
  key: string;
  remark: string;
  source: {
    link: string;
    name: string;
  };
  status: string;
  sentiment: string;
  verified_by: string;
  requested_by: string;
  confidence_degree: string;
  sfia_level_approved: string;
  sfia_level_requested: number | null;
  sfia_dimensions_approved: SfiaDimension[];
  sfia_dimensions_requested: SfiaDimension[];
};

type UserReactionIdsState = {
  verifiedData: Evidence[];
  requestedData: T_TraineeCompetencyEvidence;
  sfia_level: number | string | null | undefined;
  skills: string[] | undefined;
};

const initialState: UserReactionIdsState = {
  verifiedData: [],
  requestedData: {
    key: "",
    remark: "",
    source: {
      link: "",
      name: "",
    },
    status: "",
    sentiment: "neutral",
    verified_by: "",
    requested_by: "",
    confidence_degree: "medium",
    sfia_level_approved: "",
    sfia_level_requested: "",
    sfia_dimensions_approved: [],
    sfia_dimensions_requested: [],
  },
  sfia_level: "",
  skills: [],
};

const evidenceApprovalSlice = createSlice({
  name: "evidenceApproval",
  initialState,
  reducers: {
    setVerifiedData: (state, action: PayloadAction<Evidence[]>) => {
      state.verifiedData = action.payload;
    },
    setRequestedData: (
      state,
      action: PayloadAction<T_TraineeCompetencyEvidence>
    ) => {
      state.requestedData = action.payload;
    },
    setSfiaLevel: (state, action: PayloadAction<number | string | null>) => {
      state.sfia_level = action.payload;
    },

    setSkillOfSelectedEvidence: (state, action: PayloadAction<string[]>) => {
      state.skills = action.payload;
    },

    resetRequestedData: (state) => {
      state.requestedData = initialState.requestedData;
    },
    resetSfiaLevel: (state) => {
      state.sfia_level = initialState.sfia_level;
    },
    resetSkillOfSelectedEvidence: (state) => {
      state.skills = initialState.skills;
    },
  },
});

export const {
  setVerifiedData,
  setRequestedData,
  setSfiaLevel,
  resetRequestedData,
  resetSfiaLevel,
  resetSkillOfSelectedEvidence,
  setSkillOfSelectedEvidence,
} = evidenceApprovalSlice.actions;
export default evidenceApprovalSlice.reducer;
