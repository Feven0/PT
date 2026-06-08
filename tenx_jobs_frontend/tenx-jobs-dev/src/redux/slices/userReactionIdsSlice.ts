import { createSlice, PayloadAction } from '@reduxjs/toolkit';

type UserReactionIdsState = {
  userReactionIds: { [key: string]: string };
  engagement_list: {
    [key: string]: {
      all_user_id: string;
      user_profile_id: string;
    };
  };
};

const initialState: UserReactionIdsState = {
  userReactionIds: {},
  engagement_list: {},

};

const userReactionIdsSlice = createSlice({
  name: 'userReactionIds',
  initialState,
  reducers: {
    setUserReactionIds: (state, action: PayloadAction<Partial<UserReactionIdsState>>) => {
      if (action.payload.userReactionIds) {
        state.userReactionIds = {
          ...state.userReactionIds,
          ...action.payload.userReactionIds,
        };
      }
      if (action.payload.engagement_list) {
        state.engagement_list = {
          ...state.engagement_list,
          ...action.payload.engagement_list,
        };
      }
    },
    resetReactionId: (state) => {
      state.userReactionIds = {};
      state.engagement_list = {};
    },
  },
});

export const { setUserReactionIds, resetReactionId } = userReactionIdsSlice.actions;
export default userReactionIdsSlice.reducer;