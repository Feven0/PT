import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export type T_Session = {
  name: string ;
  level: number | null;
};

export type TEvidence = {
  id?: string;
  sessions: {
    name: string;
    level: number | null;
  }[];
};


const initialState: TEvidence = {
  sessions: [
    {
      name: '',
      level: 0,
    },
  ],
};

const updateEvidenceSlice = createSlice({
  name: "updatedEvidenceForm",
  initialState,
  reducers: {
    setEvidenceForm: (
      state,
      action: PayloadAction<Partial<TEvidence>>
    ) => {
      return {
        ...state,
        ...action.payload,
      };
    },
    addSession: (state) => {
      return {
        ...state,
        sessions: [
          ...state.sessions,
          {
            name: '',
            level: 0,
          },
        ],
      };
    },
    resetEvidenceForm: () => {
      return initialState;
    },
    removeSession: (state, action: PayloadAction<number>) => {
      return {
        ...state,
        sessions: state.sessions.filter((_, index) => index !== action.payload),
      };
    },
  },
});

export const {
  setEvidenceForm,
  removeSession,
  addSession,
  resetEvidenceForm,
} = updateEvidenceSlice.actions;
export default updateEvidenceSlice.reducer;
