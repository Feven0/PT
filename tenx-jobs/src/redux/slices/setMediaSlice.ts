import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export type TMedia = {
  name: string;
  link: string | null;
  icon?: string;
};

export type TMediaForm = {
  id?: string;
  media: {
    name: string;
    link: string | null;
    icon?: string;
  }[];
};

const initialState: TMediaForm = {
  media: [
    {
      name: "",
      link: "",
      icon: "",
    },
  ],
};

const setMediaSlice = createSlice({
  name: "setMediaForm",
  initialState,
  reducers: {
    setMediaForm: (state, action: PayloadAction<Partial<TMediaForm>>) => {
      return {
        ...state,
        ...action.payload,
      };
    },
    addMediaSession: (state) => {
      return {
        ...state,
        media: [
          ...state.media,
          {
            name: "",
            link: "",
          },
        ],
      };
    },
    resetMediaForm: () => {
      return initialState;
    },
    removeMediaSession: (state, action: PayloadAction<number>) => {
      return {
        ...state,
        media: state.media.filter((_, index) => index !== action.payload),
      };
    },
  },
});

export const {
  setMediaForm,
  addMediaSession,
  resetMediaForm,
  removeMediaSession,
} = setMediaSlice.actions;
export default setMediaSlice.reducer;
