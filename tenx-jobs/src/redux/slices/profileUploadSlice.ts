import { createSlice } from "@reduxjs/toolkit";

type ProfileUploadState = {
profileJson: {
  key: number;
  id: string;
  type: string;
  profile: string;
  errorText: string;
  profileErrorText: string;
};
};

const initialState: ProfileUploadState = {
profileJson: {
  key: 0,
  id: "",
  type: "",
  profile: "",
  errorText: "",
  profileErrorText: "",
},
};

const profileUploadSlice = createSlice({
name: "profileUpload",
initialState,
reducers: {
  setProfileJson: (state, action) => {
    state.profileJson = action.payload;
  },
  resetProfileJson: (state) => {
    state.profileJson = initialState.profileJson;
  }
},
});

export const { setProfileJson, resetProfileJson } = profileUploadSlice.actions;
export default profileUploadSlice.reducer;