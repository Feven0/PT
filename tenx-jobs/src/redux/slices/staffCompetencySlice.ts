import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { T_EvidenceMessage, T_TraineeCompetenciesAttributes } from "../../types/profileResponse";

type TCompetenceState = {
  selectedCompetency: T_TraineeCompetenciesAttributes;
};

const initialState: TCompetenceState = {
  selectedCompetency: {
    uuid: "",
    name: "",
    display: "",
    others: [],
    description: "",
    evidence: [],
    abilities: [],
    skills: [],
    knowledge: [],
    status: "",
    attitude: [],
    history: [],
    sfia_level: "",
    verified_by: "",
    requested_by: "",
    experience_level: "",
    sfia_estimation_method: "",
    credibility: "",
    rationale: "",
  },
};

const competenceSlice = createSlice({
  name: "competencyApproval",
  initialState,
  reducers: {
    setSelectedCompetency(
      state,
      action: PayloadAction<T_TraineeCompetenciesAttributes>
    ) {
      state.selectedCompetency = action.payload;
    },

    setFilteredCompetencies(state, action: PayloadAction<T_TraineeCompetenciesAttributes[]>) {
      if (action.payload.length > 0) {
        state.selectedCompetency = action.payload[0];
      }
    },

    updateEvidence(
      state,
      action: PayloadAction<{
        index: number;
        updatedFields: Partial<T_TraineeCompetenciesAttributes>;
      }>
    ) {
      const { index, updatedFields } = action.payload;

      if (state.selectedCompetency && state.selectedCompetency.evidence) {
        state.selectedCompetency.evidence[index] = {
          ...state.selectedCompetency.evidence[index],
          ...updatedFields,
        };
      }
    },

    appendMessageToEvidence(state, action: PayloadAction<{ index: number; newMessage: T_EvidenceMessage }>) {
      const { index, newMessage } = action.payload;
      
      if (state.selectedCompetency?.evidence && state.selectedCompetency.evidence[index]) {
        const evidence = state.selectedCompetency.evidence[index];        
        const existingMessages = evidence.message || [];
        const updatedMessages = [...existingMessages, newMessage];
        
        state.selectedCompetency.evidence[index] = {
          ...evidence,
          message: updatedMessages,
        };
      }
    }
  },
});

export const { setSelectedCompetency, setFilteredCompetencies, appendMessageToEvidence, updateEvidence } =
  competenceSlice.actions;
export default competenceSlice.reducer;
