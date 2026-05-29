import { createSlice, PayloadAction } from "@reduxjs/toolkit";

type TReactionId = {
  reaction_id: { [key: string]: string };
  engagement_list: {
    [key: string]: {
      all_user_id: string;
      user_profile_id: string;
      trainee_id: string;
    };
  };
  trainee_id: string | number | null;
};

const initialState: TReactionId = {
  reaction_id: {},
  engagement_list: {},
  trainee_id: "",
};

export const reactionIdSlice = createSlice({
  name: "updateIdLists",
  initialState,
  reducers: {
    setReactionId: (state, action: PayloadAction<Partial<TReactionId>>) => {
      if (action.payload.reaction_id) {
        state.reaction_id = action.payload.reaction_id; 
      }
      if (action.payload.engagement_list) {
        state.engagement_list = action.payload.engagement_list;
      }
    },
    
    setTraineeId: (state, action: PayloadAction<string | number>) => {
      state.trainee_id = action.payload;
    },

    resetReactionId: (state) => {
      state.reaction_id = {};
      state.engagement_list = {};
    },
  },
});

export const { setReactionId, resetReactionId, setTraineeId } = reactionIdSlice.actions;
export default reactionIdSlice.reducer;
