import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  skills: [],
  title: "",
};

const profileSkillSlice = createSlice({
  name: "userProfileSkill",
  initialState,
  reducers: {
    setUserProfileSkills: (state, { payload }) => {
      state.skills = payload;
    },

    setUserProfileSkillTitle: (state, { payload }) => {
      state.title = payload;
    },
  },
});

export const { setUserProfileSkills, setUserProfileSkillTitle } = profileSkillSlice.actions;
export default profileSkillSlice.reducer;