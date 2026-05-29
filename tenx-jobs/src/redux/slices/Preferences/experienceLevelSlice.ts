import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { PrioritySettingType } from "../../../types/preferenceTypes";
import { normalizeType } from "../../../utils/commonUtils";

type ExpeLevelState = {
  experience_level: PrioritySettingType[];
  experienceLevelOptions: string[];
};

const initialState: ExpeLevelState = {
  experience_level: [],
  experienceLevelOptions: ["Entry", "Mid", "Senior", "Associate", "Executive"],
};

const toggleEmploymentType = createSlice({
  name: "experienceLevelPreference",
  initialState,
  reducers: {
    setExperienceLevels: (
      state,
      action: PayloadAction<PrioritySettingType[]>
    ) => {
      state.experience_level = action.payload;
    },
    addExperienceLevelPreference: (
      state,
      action: PayloadAction<PrioritySettingType>
    ) => {
      const normalizedName = normalizeType(action.payload.name);
      const existingExpLevel = state.experience_level.find(
        (role) => normalizeType(role.name) === normalizedName
      );
      if (!existingExpLevel) {
        state.experience_level.push(action.payload);
      } else {
        existingExpLevel.priority = action.payload.priority;
      }
    },
    removeExperienceLevelPreference: (state, action: PayloadAction<string>) => {
      state.experience_level = state.experience_level.filter(
        (role) => role.name !== action.payload
      );
    },
    updateExperienceLevelPreferencePriority: (
      state,
      action: PayloadAction<{
        name: string;
        priority: "high" | "medium" | "low";
      }>
    ) => {
      const normalizedName = normalizeType(action.payload.name);
      state.experience_level = state.experience_level.map((role) =>
        normalizeType(role.name) === normalizedName
          ? { ...role, priority: action.payload.priority }
          : role
      );
    },
    setExperienceLevelOptions: (state, action: PayloadAction<string[]>) => {
      state.experienceLevelOptions = action.payload;
    },
    removeExperienceLevelOption: (state, action: PayloadAction<string>) => {
      const normalizedName = normalizeType(action.payload);
      state.experienceLevelOptions = state.experienceLevelOptions.filter(
        (size) => normalizeType(size) !== normalizedName
      );
    },
  },
});

export const {
  addExperienceLevelPreference,
  removeExperienceLevelPreference,
  updateExperienceLevelPreferencePriority,
  setExperienceLevels,
  setExperienceLevelOptions,
  removeExperienceLevelOption,
} = toggleEmploymentType.actions;
export default toggleEmploymentType.reducer;
