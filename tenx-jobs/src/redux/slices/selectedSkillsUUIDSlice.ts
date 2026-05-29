import {createSlice } from "@reduxjs/toolkit";

export type TSelectedSkillsUUID = {
  selectedSkillsUUID: string,
  rowId: string
}

const initialState: TSelectedSkillsUUID = {
  selectedSkillsUUID: "",
  rowId: ""
}

export const selectedSkillsUUIDSlice = createSlice({
  name: "selectedSkillsUUID",
  initialState,
  reducers: {
    setSelectedSkillsUUID: (state, action) => {
      state.selectedSkillsUUID = action.payload;
    },

    setRowId: (state, action) => {
      state.rowId = action.payload;
    }
  },
});

export const { setSelectedSkillsUUID, setRowId } = selectedSkillsUUIDSlice.actions;
export default selectedSkillsUUIDSlice.reducer;