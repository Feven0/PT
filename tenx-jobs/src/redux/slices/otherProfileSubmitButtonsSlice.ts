import { createSlice, PayloadAction } from '@reduxjs/toolkit';

type TSubmitButton = {
  awardButtonEditing: boolean;
  certificateButtonEditing: boolean;
  languageButtonEditing: boolean;
  volunteerButtonEditing: boolean;
  achievementButtonEditing: boolean;
  programmingLanguageButtonEditing: boolean;
  publicationButtonEditing: boolean;
  referenceButtonEditing: boolean;
}

const initialState: TSubmitButton = {
  awardButtonEditing: false,
  certificateButtonEditing: false,
  languageButtonEditing: false,
  volunteerButtonEditing: false,
  achievementButtonEditing: false,
  programmingLanguageButtonEditing: false,
  publicationButtonEditing: false,
  referenceButtonEditing: false
}

const otherProfileSubmitButtonsSlice = createSlice({
  name: 'otherProfileSubmitButtons',
  initialState,
  reducers: {
    setAwardButtonEditing: (state, action: PayloadAction<boolean>) => {
      state.awardButtonEditing = action.payload;
    },
    setCertificateButtonEditing: (state, action: PayloadAction<boolean>) => {
      state.certificateButtonEditing = action.payload;
    },
    setLanguageButtonEditing: (state, action: PayloadAction<boolean>) => {
      state.languageButtonEditing = action.payload;
    },
    setVolunteerButtonEditing: (state, action: PayloadAction<boolean>) => {
      state.volunteerButtonEditing = action.payload;
    },
    setAchievementButtonEditing: (state, action: PayloadAction<boolean>) => {
      state.achievementButtonEditing = action.payload;
    },
    setProgrammingLanguageButtonEditing: (state, action: PayloadAction<boolean>) => {
      state.programmingLanguageButtonEditing = action.payload;
    },
    setPublicationButtonEditing: (state, action: PayloadAction<boolean>) => {
      state.publicationButtonEditing = action.payload;
    },
    setReferenceButtonEditing: (state, action: PayloadAction<boolean>) => {
      state.referenceButtonEditing = action.payload;
    }
  }
})

export const { setAwardButtonEditing, 
              setCertificateButtonEditing, 
              setLanguageButtonEditing, 
              setVolunteerButtonEditing,
              setAchievementButtonEditing,
              setProgrammingLanguageButtonEditing,
              setPublicationButtonEditing,
              setReferenceButtonEditing
            } = otherProfileSubmitButtonsSlice.actions;
export default otherProfileSubmitButtonsSlice.reducer;