import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export type Stats = {
  credit_remaining: number;
  credit_used: number;
  max_credit: number;
  supermatch: number;
  match: number;
  negmatch: number;
  mismatch: number;
  superlike: number;
  like: number;
  dislike: number;
  superdislike: number;
  other: number;
  unknown?: number;
};

export type engagementStats = {
 Like: number;
 Skip: number;
 Super_Like: number;
 credit_remaining: number;
 credit_used: number;
 dislike: number;
 like: number
 max_credit: number
 other: number
 superlike: number
}

export type UserState = {
  stats: Stats;
  engagementStats?: engagementStats;
};

const initialState: UserState = {
  stats: {
    credit_used: 0,
    max_credit: 0,
    supermatch: 0,
    match: 0,
    negmatch: 0,
    mismatch: 0,
    superlike: 0,
    like: 0,
    dislike: 0,
    superdislike: 0,
    other: 0,
    credit_remaining: 0,
    unknown: 0,
  },
  engagementStats: {
    Like: 0,
    Skip: 0,
    Super_Like: 0,
    credit_remaining: 0,
    credit_used: 0,
    dislike: 0,
    like: 0,
    max_credit: 0,
    other: 0,
    superlike: 0,
  }
};

const userStatsSlice = createSlice({
  name: 'userStats',
  initialState,
  reducers: {
    setUserState(state, action: PayloadAction<Stats>) {
      state.stats = action.payload;
    },
    setEngagementsStats(state, action: PayloadAction<engagementStats>) {
      state.engagementStats = action.payload;
    },
    updateStats(state, action: PayloadAction<Partial<Stats>>) {
      state.stats = { ...state.stats, ...action.payload };
    },
  },
});

export const { setUserState, updateStats, setEngagementsStats } = userStatsSlice.actions;
export default userStatsSlice.reducer;


