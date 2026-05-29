import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { PrioritySettingType } from "../../../types/preferenceTypes";

type EducationState = {
  education: PrioritySettingType[];
  educationOptions: string[];
}

const initialState: EducationState = {
  education: [],
  educationOptions: ["Bachelor’s Degree", "Master’s Degree", "PhD", "High School Diploma", "Technical/Vocational Certificate"]
};

const educationPreferenceSlice = createSlice({
  name: "educationPreference",
  initialState,
  reducers: {
    setEducationPreference: (state, action: PayloadAction<PrioritySettingType[]>) => {
      state.education = action.payload
    },
    addEducationPreference: (state, action: PayloadAction<PrioritySettingType>) => {
      state.education.push(action.payload);
    },
    removeEducationPreference: (state, action: PayloadAction<string>) => {
      state.education = state.education.filter((role) => role.name !== action.payload);
    },
    updateEducationPriority: (
      state,
      action: PayloadAction<{ name: string; priority: "high" | "medium" | "low" }>
    ) => {
      state.education = state.education.map((role) =>
        role.name === action.payload.name
          ? { ...role, priority: action.payload.priority }
          : role
      );
    },
    updateEducationName: (
      state,
      action: PayloadAction<{ index: number; newName: string }>
    ) => {
      const { index, newName } = action.payload;
      const educationIndex = state.education.indexOf(state.education[index]);
      state.education[educationIndex].name = newName;
    },
    setEducationOptions: (state, action: PayloadAction<string[]>) => {
      state.educationOptions = action.payload;
    },
    removeEducationOption: (state, action: PayloadAction<string>) => {
      state.educationOptions = state.educationOptions.filter(size => size !== action.payload);
    }
  },
});

export const { 
  addEducationPreference,
  removeEducationPreference,
  updateEducationPriority,
  setEducationPreference,
  updateEducationName,
  setEducationOptions,
  removeEducationOption
 } = educationPreferenceSlice.actions;
export default educationPreferenceSlice.reducer;
