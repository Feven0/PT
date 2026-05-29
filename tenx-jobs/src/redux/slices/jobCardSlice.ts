import { createSlice } from "@reduxjs/toolkit";
import { TLeapJobCards } from "../../types/Jobs";

const initialState: TLeapJobCards = {
  user_profile_id: "",
  cards: [],
  match_attribute: {
    level: "",
    title: "",
    applyLink: "",
    match_algorithm:"",
    rationale: "",
    match_summary: "",
    match_detail: [],
    overall_match_degree: "",
    overall_match_score: ""
  },
  status: 0,
  message: "",
  redis_list_id: ""
};

const jobCardSlice = createSlice({
  name: "jobCard",
  initialState,
  reducers: {
    setCards: (state, { payload }) => {
      state.cards = payload;
    },

    setRedisListId: (state, { payload }) => {
      state.redis_list_id = payload;
    }
  },
});

export const { setCards, setRedisListId } = jobCardSlice.actions;
export default jobCardSlice.reducer;
