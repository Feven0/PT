import {PayloadAction, createSlice } from "@reduxjs/toolkit";

export type TEvidence = {
  evidence: {
  remark: string
  source: string[]
  link: string
  title: string
}
}

const initialState: TEvidence = {
  evidence: {
    remark: "",
    source: [],
    link: "",
    title: ""
  }
}

export const evidenceSlice = createSlice({
  name: "updateEvidence",
  initialState,
  reducers: {
    setEvidence: (state, action: PayloadAction<Partial<TEvidence['evidence']>>) => {
      state.evidence = {
        ...state.evidence,
        ...action.payload,
      };
    },
  },
});

export const { setEvidence } = evidenceSlice.actions;
export default evidenceSlice.reducer;
