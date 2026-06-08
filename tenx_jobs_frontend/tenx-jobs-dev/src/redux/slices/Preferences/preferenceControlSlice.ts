import { createSlice, PayloadAction } from "@reduxjs/toolkit";

type tagType = {
  flag: boolean;
}

const initialState: tagType = {
  flag: false
};

const tagSlice = createSlice({
  name: "preferenceControl",
  initialState,
  reducers: {
    setPreferenceControlTag: (state, action: PayloadAction<boolean>) => {
      state.flag = action.payload
    },
  },
});

export const { setPreferenceControlTag } = tagSlice.actions;
export default tagSlice.reducer;