import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { PrioritySettingType } from "../../../types/preferenceTypes";

type RolesState = {
  roles: PrioritySettingType[];
}

const initialState: RolesState = {
  roles: []
};

const rolesSlice = createSlice({
  name: "rolesPreference",
  initialState,
  reducers: {
    setRolesPreference: (state, action: PayloadAction<PrioritySettingType[]>) => {
      state.roles = action.payload;
    },
    addRole: (state, action: PayloadAction<PrioritySettingType>) => {
      state.roles.push(action.payload);
    },
    removeRole: (state, action: PayloadAction<string>) => {
      state.roles = state.roles.filter((role) => role.name !== action.payload);
    },
    updateRolePriority: (
      state,
      action: PayloadAction<{ name: string; priority: "high" | "medium" | "low" }>
    ) => {
      state.roles = state.roles.map((role) =>
        role.name === action.payload.name
          ? { ...role, priority: action.payload.priority }
          : role
      );
    },
    updateRoleName: (
      state,
      action: PayloadAction<{ index: number; newName: string }>
    ) => {
      const { index, newName } = action.payload;
      const rolesIndex = state.roles.indexOf(state.roles[index]);
      state.roles[rolesIndex].name = newName;
    },
  },
});

export const { addRole, setRolesPreference, updateRoleName, removeRole,updateRolePriority } = rolesSlice.actions;
export default rolesSlice.reducer;
