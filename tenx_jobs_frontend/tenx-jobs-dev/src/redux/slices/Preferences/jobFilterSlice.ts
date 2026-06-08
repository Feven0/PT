import { createSlice, PayloadAction } from "@reduxjs/toolkit";

 type days_extracted ={
  days_extracted: number | null | undefined;
 }

const initialState: days_extracted = {
  days_extracted: null,
};

const jobFilterSlice = createSlice({
  name: "jobFilter",
  initialState,
  reducers: {
    setDaysExtracted: (state, action: PayloadAction<number>) => {
      state.days_extracted = action.payload;
    },
  },
});

export const { setDaysExtracted } = jobFilterSlice.actions;
export default jobFilterSlice.reducer;