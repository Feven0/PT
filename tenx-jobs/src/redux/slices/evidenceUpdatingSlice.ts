import { createSlice, PayloadAction } from '@reduxjs/toolkit';

type SfiaDimension = {
  name: string;
  level: number;
};

type Evidence = {
  key?: string;
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
  sfia_level_approved: number | string | null;
  sfia_level_requested: number | null | string;
  sfia_dimensions_approved: SfiaDimension[];
  sfia_dimensions_requested: SfiaDimension[];
};

type UpdateEvidenceProp = {
  evidenceDataToBeUpdated: Evidence;
};

const initialState: UpdateEvidenceProp = {
  evidenceDataToBeUpdated: {
    key: '',
    remark: '',
    source: {
      link: '',
      name: '',
    },
    status: '',
    sentiment: '',
    verified_by: '',
    requested_by: '',
    confidence_degree: '',
    sfia_level_approved: '',
    sfia_level_requested: null,
    sfia_dimensions_approved: [],
    sfia_dimensions_requested: [],
  },
};

const evidenceUpdatingSlice = createSlice({
  name: 'updateCompetencyEvidence',
  initialState,
  reducers: {

    setEvidenceUpdate: (state, action: PayloadAction<Evidence>) => {
      state.evidenceDataToBeUpdated = action.payload;
    },
    resetEvidenceUpdateData: (state) => {
      state.evidenceDataToBeUpdated = initialState.evidenceDataToBeUpdated;
    },

    updateSfiaDimensionRequested: (state, action: PayloadAction<{ index: number; name: string; level: number | null }>) => {
      const { index, name, level } = action.payload;
      if (state.evidenceDataToBeUpdated.sfia_dimensions_requested[index]) {
        state.evidenceDataToBeUpdated.sfia_dimensions_requested[index] = { name, level: level || 0 };
      } else {
        state.evidenceDataToBeUpdated.sfia_dimensions_requested.push({ name, level: level || 0 });
      }
    },
    removeSfiaDimensionRequested: (state, action: PayloadAction<number>) => {
      const index = action.payload;
      if (index > -1 && index < state.evidenceDataToBeUpdated.sfia_dimensions_requested.length) {
        state.evidenceDataToBeUpdated.sfia_dimensions_requested.splice(index, 1);
      }
    },
    addEvidenceUpdatingSession: (state) => {
      state.evidenceDataToBeUpdated.sfia_dimensions_requested.push({ name: "", level: 0 });
    },
}});

export const { 
  setEvidenceUpdate,
  updateSfiaDimensionRequested,
  resetEvidenceUpdateData,
  removeSfiaDimensionRequested,
  addEvidenceUpdatingSession
 } = evidenceUpdatingSlice.actions;
export default evidenceUpdatingSlice.reducer;
