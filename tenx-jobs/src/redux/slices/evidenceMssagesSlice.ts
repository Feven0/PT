import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { T_EvidenceMessage, T_TraineeCompetencyEvidenceSource, T_TraineeSfia_dimension } from "../../types/profileResponse";

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

type TraineeCompetencyEvidenceState = {
  evidence: T_TraineeCompetencyEvidence | null; 
};

const initialState: TraineeCompetencyEvidenceState = {
  evidence: null,
};

const traineeCompetencyEvidenceSlice = createSlice({
  name: 'traineeCompetencyEvidence',
  initialState,
  reducers: {
    setEvidences: (state, action: PayloadAction<T_TraineeCompetencyEvidence>) => {
      state.evidence = action.payload;
    },
    updateRemark: (state, action: PayloadAction<string>) => {
      if (state.evidence) {
        state.evidence.remark = action.payload;
      }
    },
    updateSource: (state, action: PayloadAction<T_TraineeCompetencyEvidenceSource>) => {
      if (state.evidence) {
        state.evidence.source = action.payload;
      }
    },
    updateStatus: (state, action: PayloadAction<string>) => {
      if (state.evidence) {
        state.evidence.status = action.payload;
      }
    },
    updateSentiment: (state, action: PayloadAction<string>) => {
      if (state.evidence) {
        state.evidence.sentiment = action.payload;
      }
    },
    updateVerifiedBy: (state, action: PayloadAction<string>) => {
      if (state.evidence) {
        state.evidence.verified_by = action.payload;
      }
    },
    updateRequestedBy: (state, action: PayloadAction<string>) => {
      if (state.evidence) {
        state.evidence.requested_by = action.payload;
      }
    },
    updateConfidenceDegree: (state, action: PayloadAction<string>) => {
      if (state.evidence) {
        state.evidence.confidence_degree = action.payload;
      }
    },
    updateSfialLevelApproved: (state, action: PayloadAction<number | string | null>) => {
      if (state.evidence) {
        state.evidence.sfia_level_approved = action.payload;
      }
    },
    updateSfialLevelRequested: (state, action: PayloadAction<number | string | null>) => {
      if (state.evidence) {
        state.evidence.sfia_level_requested = action.payload;
      }
    },
    updateSfialDimensionsApproved: (state, action: PayloadAction<T_TraineeSfia_dimension[]>) => {
      if (state.evidence) {
        state.evidence.sfia_dimensions_approved = action.payload;
      }
    },
    updateSfialDimensionsRequested: (state, action: PayloadAction<T_TraineeSfia_dimension[]>) => {
      if (state.evidence) {
        state.evidence.sfia_dimensions_requested = action.payload;
      }
    },
    updateMessage: (state, action: PayloadAction<T_EvidenceMessage>) => {
      if (state.evidence) {
        if (!state.evidence.message) {
          state.evidence.message = [];
        }
        state.evidence.message.push(action.payload);
      }
    },
    
    clearEvidence: (state) => {
      state.evidence = null;
    },
  },
});

export const {
  setEvidences,
  updateRemark,
  updateSource,
  updateStatus,
  updateSentiment,
  updateVerifiedBy,
  updateRequestedBy,
  updateConfidenceDegree,
  updateSfialLevelApproved,
  updateSfialLevelRequested,
  updateSfialDimensionsApproved,
  updateSfialDimensionsRequested,
  updateMessage,
  clearEvidence,
} = traineeCompetencyEvidenceSlice.actions;

// Export the reducer
export default traineeCompetencyEvidenceSlice.reducer;
