import {PayloadAction, createSlice } from "@reduxjs/toolkit";

export type TRecord = {
  record: {
    company_name: string,
    job_id: string,
    job_profile_id: string,
    job_title: string,
    user_reaction_id: string,
    job_trainee_id: string
  }
}

const initialState: TRecord = {
  record: {
    company_name: "",
    job_id: "",
    job_profile_id: "",
    job_title: "",
    user_reaction_id: "",
    job_trainee_id: ""
  }
}

export const recordSlice = createSlice({
  name: "updateRecord",
  initialState,
  reducers: {
    setRecord: (state, action: PayloadAction<Partial<TRecord['record']>>) => {
      state.record = {
        ...state.record,
        ...action.payload,
      };
    },
  },
});

export const { setRecord } = recordSlice.actions;
export default recordSlice.reducer;
