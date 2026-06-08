import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface LeapProfileIdState {
  user_profile_id: string;
  allUserId: string | number | null | undefined;
  user_job_match_id: string;
  user_role: string;
  user_token: string;
  reloadCount: number;
  trainee_id: string;
  batch: string;
  batchID: string;
  trainee_preference_id: string;
}

const initialState: LeapProfileIdState = {
  user_profile_id: "",
  allUserId: "",
  user_job_match_id: "",
  user_role: "",
  user_token: "",
  reloadCount: 0,
  trainee_id: "",
  batch: "",
  batchID: "",
  trainee_preference_id: "",
};

const leapProfileIdSlice = createSlice({
  name: "leapProfileId",
  initialState,
  reducers: {
    setUserProfileId(state, action: PayloadAction<string>) {
      state.user_profile_id = action.payload;
    },
    setAllUserIdForLeap(
      state,
      action: PayloadAction<string | number | null | undefined>
    ) {
      state.allUserId = action.payload;
    },
    setUserJobMatchId(state, action: PayloadAction<string>) {
      state.user_job_match_id = action.payload;
    },
    setUserRole(state, action: PayloadAction<string>) {
      state.user_role = action.payload;
    },
    setUserToken(state, action: PayloadAction<string>) {
      state.user_token = action.payload;
    },
    setReloadCount(state, action: PayloadAction<number>) {
      state.reloadCount = action.payload;
    },

    setTraineeId(state, action: PayloadAction<string>) {
      state.trainee_id = action.payload;
    },

    setBatchID: (state, { payload }) => {
      state.batch = payload.batch;
      state.batchID = payload.batchID;
    },

    setTraineePreferenceId: (state, { payload }) => {
      state.trainee_preference_id = payload;
    },

    resetReloadCount(state) {
      state.reloadCount = 0;
    },
  },
});

export const {
  setUserProfileId,
  setReloadCount,
  setUserToken,
  setUserRole,
  setUserJobMatchId,
  resetReloadCount,
  setTraineeId,
  setBatchID,
  setAllUserIdForLeap,
  setTraineePreferenceId,
} = leapProfileIdSlice.actions;
export default leapProfileIdSlice.reducer;
