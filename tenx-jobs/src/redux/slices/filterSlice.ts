import { PayloadAction, createSlice } from "@reduxjs/toolkit";

export type TFilter = {
  move_to: string[];
  move_from: string[];
  job_link: string;
  application_status: string;
  show_others: boolean;
};

const initialState: TFilter = {
  move_to: [],
  move_from: [],
  job_link: "",
  application_status: "",
  show_others: true,
};

export const filterSlice = createSlice({
  name: "updateFilter",
  initialState,
  reducers: {
    setMoveToFilter: (state, action: PayloadAction<string[]>) => {
      state.move_to = action.payload;
    },
    setMoveFromFilter: (state, action: PayloadAction<string[]>) => {
      state.move_from = action.payload;
    },
    setJobLink: (state, action: PayloadAction<string>) => {
      state.job_link = action.payload;
    },
    setJobApplicationStatus: (state, action: PayloadAction<string>) => {
      state.application_status = action.payload;
    },
    setShowOters: (state, action: PayloadAction<boolean>) => {
      state.show_others = action.payload;
    },
  },
});

export const {
  setMoveToFilter,
  setJobLink,
  setMoveFromFilter,
  setJobApplicationStatus,
  setShowOters,
} = filterSlice.actions;
export default filterSlice.reducer;
