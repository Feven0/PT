import { createSlice, PayloadAction } from "@reduxjs/toolkit";

type TSFIA_Level = {
  sfia_level: string | null;
  competency_description: string;
  competency_rationale: string;
}

const initialState: TSFIA_Level = {
  sfia_level: null,
  competency_description: "",
  competency_rationale: ""
}

const updatingTraineeSifaLevelSlice = createSlice({
  name: "updatingTraineeSifaLevel",
  initialState,
  reducers: {
    setTraineeSifaLevel: (state, action: PayloadAction<string>) => {
      state.sfia_level = action.payload;
    },

    setCompetencyDescription: (state, action: PayloadAction<string>) => {
      state.competency_description = action.payload;
    },
    setCompetencyRationale: (state, action: PayloadAction<string>) => {
      state.competency_rationale = action.payload;
    },

    resetTraineeSifaLevel: (state) => {
      state.sfia_level = initialState.sfia_level;
      state.competency_description = initialState.competency_description;
      state.competency_rationale = initialState.competency_rationale;
    }
  }
})

export const { setTraineeSifaLevel, setCompetencyDescription, setCompetencyRationale, resetTraineeSifaLevel } = updatingTraineeSifaLevelSlice.actions;
export default updatingTraineeSifaLevelSlice.reducer;