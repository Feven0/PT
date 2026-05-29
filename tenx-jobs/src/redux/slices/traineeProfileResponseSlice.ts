import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { T_TraineeProfileResponse } from "../../types/profileResponse";

const initialState: T_TraineeProfileResponse = {
  all_user_id: '',
  user_profile_id: '',
  user_profile: {
    name: '',
    display: '',
    description: '',
    profile_type: '',
    awards: {
      code: '',
      name: '',
      display: '',
      template: '',
      attributes: [],
      description: '',
      profile_type: ''
    },
    basics: {
      code: '',
      name: '',
      display: '',
      template: '',
      attributes: [],
      description: '',
      profile_type: ''
    },
    projects: {
      code: '',
      name: '',
      display: '',
      template: '',
      attributes: [],
      description: '',
      profile_type: ''
    },
    education: {
      code: '',
      name: '',
      display: '',
      template: '',
      attributes: [],
      description: '',
      profile_type: ''
    },
    work_experience: {
      code: '',
      name: '',
      display: '',
      template: '',
      attributes: [],
      description: '',
      profile_type: ''
    },
    competencies: {
      code: '',
      name: '',
      display: '',
      template: '',
      attributes: [],
      description: '',
      profile_type: ''
    },
    interests: {
      code: '',
      name: '',
      display: '',
      template: '',
      attributes: [],
      description: '',
      profile_type: ''
    },
    certificates: {
      code: '',
      name: '',
      display: '',
      template: '',
      attributes: [],
      description: '',
      profile_type: ''
    },
    languages: {
      code: '',
      name: '',
      display: '',
      template: '',
      attributes: [],
      description: '',
      profile_type: ''
    },
    volunteer: {
      code: '',
      name: '',
      display: '',
      template: '',
      attributes: [],
      description: '',
      profile_type: ''
    },
    references: {
      code: '',
      name: '',
      display: '',
      template: '',
      attributes: [],
      description: '',
      profile_type: ''
    },
    publications: {
      code: '',
      name: '',
      display: '',
      template: '',
      attributes: [],
      description: '',
      profile_type: ''
    },
    programing_languages: {
      code: '',
      name: '',
      display: '',
      template: '',
      attributes: [],
      description: '',
      profile_type: ''
    },
    achievements: {
      code: '',
      name: '',
      display: '',
      template: '',
      attributes: [],
      description: '',
      profile_type: ''
    }
  },
  status: 0,
  message: ''
};

const traineeProfileResponseSlice = createSlice({
  name: 'traineeProfileResponse',
  initialState,
  reducers: {
    setTraineeResponseProfile: (state, action: PayloadAction<T_TraineeProfileResponse>) => {
      state.all_user_id = action.payload.all_user_id;
      state.user_profile_id = action.payload.user_profile_id;
      state.user_profile = action.payload.user_profile;
      state.status = action.payload.status;
      state.message = action.payload.message;
    },

    setE: (state, action) => {
      const data = state.user_profile.competencies;
      const val = data?.attributes;
      const newData = JSON.parse(JSON.stringify(val));

      const { uuid, evidenceIndex, message } = action.payload;

      const foundEntry = newData?.find((entry:any) => entry.uuid === uuid);
      if (foundEntry) {
      const evidence = foundEntry.evidence;
      if (evidenceIndex >= 0 && evidenceIndex < evidence.length) {
        const foundEvidence = evidence[evidenceIndex];
        if (!foundEvidence.message) {
          foundEvidence.message = []; 
        }
        foundEvidence.message.push(message);
        }
      }
    },

    resetTraineeProfile: () => initialState,
  }
});

export const { setTraineeResponseProfile, resetTraineeProfile, setE } = traineeProfileResponseSlice.actions;
export default traineeProfileResponseSlice.reducer;
