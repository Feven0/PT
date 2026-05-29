import {createSlice } from "@reduxjs/toolkit";
import { TUser } from "../../types/userTypes";

const initialState : TUser = {
  token: "",
  username: "",
  email: "",
  role: "",
  userId: "",
  strapiId: "",
  batch: "",
  allUserId: "",
  groups: "",
  Tid: "",
  Rid: "",
  batchID: "",
  user_profile_id: "",
};

const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    setToken: (state, { payload }) => {
      state.token = payload.token;
    },
    setUsername: (state, { payload }) => {
      state.username = payload.username;
    },
    setEmail: (state, { payload }) => {
      state.email = payload.email;
    },
    setRole: (state, { payload }) => {
      state.role = payload.role;
    },
    setUserId: (state, { payload }) => {
      state.userId = payload;
    },
    setStrapiId: (state, { payload }) => {
      state.strapiId = payload;
    },
    setBatch: (state, { payload }) => {
      state.batch = payload.batch;
      state.batchID = payload.batchID;
    },
    setAllUserId: (state, { payload }) => {
      state.allUserId = payload;
    },
    setGroups: (state, { payload }) => {
      state.groups = payload;
    },
    setTid: (state, { payload }) => {
      state.Tid = payload;
    },
    setRid: (state, { payload }) => {
      state.Rid = payload;
    },
    setUserProfileId: (state, { payload }) => {
      state.user_profile_id = payload;
    },
    reset: () => {
      return initialState
    },
  },
});

export const {
  setToken,
  setRid,
  setTid,
  setUsername,
  setEmail,
  setRole,
  setUserId,
  setStrapiId,
  setAllUserId,
  setGroups,
  setBatch,
  setUserProfileId,
  reset,
} = userSlice.actions;

export default userSlice.reducer;
