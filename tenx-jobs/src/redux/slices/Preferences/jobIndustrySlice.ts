import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { PrioritySettingType } from "../../../types/preferenceTypes";

type IndustryState = {
  industry: PrioritySettingType[];
}

const initialState: IndustryState = {
  industry: [],
};

const jobIndustrySlice = createSlice({
  name: "industryPreference",
  initialState,
  reducers: {
    setIndustryPreference: (state, action: PayloadAction<PrioritySettingType[]>) => {
      state.industry = action.payload
    },
    addJobIndustry: (state, action: PayloadAction<PrioritySettingType>) => {
      state.industry.push(action.payload);
    },
    removeJobIndustry: (state, action: PayloadAction<string>) => {
      state.industry = state.industry.filter((role) => role.name !== action.payload);
    },
    updateJobIndustryPriority: (
      state,
      action: PayloadAction<{ name: string; priority: "high" | "medium" | "low" }>
    ) => {
      state.industry = state.industry.map((role) =>
        role.name === action.payload.name
          ? { ...role, priority: action.payload.priority }
          : role
      );
    },
    updateIndustryName: (
      state,
      action: PayloadAction<{ index: number; newName: string }>
    ) => {
      const { index, newName } = action.payload;
      const industryIndex = state.industry.indexOf(state.industry[index]);
      state.industry[industryIndex].name = newName;
    },
  },
});

export const { 
  addJobIndustry,
  removeJobIndustry,
  updateJobIndustryPriority,
  setIndustryPreference,
  updateIndustryName
 } = jobIndustrySlice.actions;
export default jobIndustrySlice.reducer;
