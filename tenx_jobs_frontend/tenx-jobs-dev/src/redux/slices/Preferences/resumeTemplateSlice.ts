import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ResumeState {
  resume: {
    template_name: string;
    template_id: string;
    max_work_experience: number | null;
    max_projects: number | null;
    max_page: number  | null;
  };
  cover_letter: {
    max_page: number | null;
  }
}

const initialState: ResumeState = {
  resume: {
    template_name: '',
    template_id: '',
    max_work_experience: null,
    max_projects: null,
    max_page: null,
  },

  cover_letter: {
    max_page: null,
  },

};

const resumeTemplateSlice = createSlice({
  name: 'resumePreference',
  initialState,
  reducers: {
    setTemplateInfo(state, action: PayloadAction<ResumeState['resume']>) {
      state.resume = action.payload;
    },
    setCoverLetterInfo(state, action: PayloadAction<ResumeState['cover_letter']>) {
      state.cover_letter = action.payload;
    }
  },
});

export const { setTemplateInfo, setCoverLetterInfo } = resumeTemplateSlice.actions;
export default resumeTemplateSlice.reducer;
