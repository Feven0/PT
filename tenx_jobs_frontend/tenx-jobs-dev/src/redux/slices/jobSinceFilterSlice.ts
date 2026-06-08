import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface JobSinceFilterState {
  days: number;
  filter: string;
}

const initialState: JobSinceFilterState = {
  days: 7, 
  filter: 'Last 7 days',
};

const jobSinceFilterSlice = createSlice({
  name: 'updateSince',
  initialState,
  reducers: {
    setSince: (state, action: PayloadAction<{ days: number, filter: string }>) => {
      state.days = action.payload.days;
      state.filter = action.payload.filter;
    },
  },
});

export const { setSince } = jobSinceFilterSlice.actions;
export default jobSinceFilterSlice.reducer;
