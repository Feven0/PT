import { createSlice, PayloadAction } from '@reduxjs/toolkit';

type MatchingPercentageState = {
  match: {
    preference_score_threshold: number;
    rating_score_threshold: number; 
    ujc_score_threshold: number;
  };
};

const initialState: MatchingPercentageState = {
  match: {
    ujc_score_threshold: 50,
    rating_score_threshold: 0,
    preference_score_threshold: 50
  },
};

const matchingPercentageSlice = createSlice({
  name: 'matchingPercentage',
  initialState,
  reducers: {
    setSliderValue: (
      state,
      action: PayloadAction<Partial<MatchingPercentageState['match']>>
    ) => {
      state.match = {
        ...state.match,
        ...action.payload,
      };
    },
  },
});

export const { setSliderValue } = matchingPercentageSlice.actions;
export default matchingPercentageSlice.reducer;
