import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { PrioritySettingType } from "../../../types/preferenceTypes";

type EmploymentState = {
  employment: PrioritySettingType[];
  employmentOptions: string[];
}

const initialState: EmploymentState = {
  employment: [],
  employmentOptions: ["Full-Time", "Part-Time", "Intern", "Contract"]
};

const toggleEmploymentType = createSlice({
  name: "employmentType",
  initialState,
  reducers: {
    setEmploymentTypePreference: (state, action: PayloadAction<PrioritySettingType[]>) => {
      state.employment = action.payload
    },
    addEmployment: (state, action: PayloadAction<PrioritySettingType>) => {
      const existingEmpType = state.employment.find(
        (role) => role.name.toLowerCase() === action.payload.name.toLowerCase()
      );
      if (!existingEmpType) {
        state.employment.push(action.payload);
      } else {
        existingEmpType.priority = action.payload.priority;
      }
    },
    removeEmployment: (state, action: PayloadAction<string>) => {
      state.employment = state.employment.filter((role) => role.name !== action.payload);
    },
    updateEmploymentPriority: (
      state,
      action: PayloadAction<{ name: string; priority: "high" | "medium" | "low" }>
    ) => {
      state.employment = state.employment.map((role) =>
        role.name === action.payload.name
          ? { ...role, priority: action.payload.priority }
          : role
      );
    },
    updateEmploymentTypeName: (
      state,
      action: PayloadAction<{ index: number; newName: string }>
    ) => {
      const { index, newName } = action.payload;
      const empTypeIndex = state.employment.indexOf(state.employment[index]);
      state.employment[empTypeIndex].name = newName;
    },
    removeEmploymentOption: (state, action: PayloadAction<string>) => {
      state.employmentOptions = state.employmentOptions.filter(size => size !== action.payload);
    },
    setEmploymentTypeOptions: (state, action: PayloadAction<string[]>) => {
      state.employmentOptions = action.payload;
    }
  },
});

export const { 
  addEmployment,
  removeEmployment,
  updateEmploymentPriority,
  setEmploymentTypePreference,
  updateEmploymentTypeName,
  removeEmploymentOption,
  setEmploymentTypeOptions
 } = toggleEmploymentType.actions;
export default toggleEmploymentType.reducer;
