import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export type TraineeInfo = {
  name: string;
  email: string;
};

const initialState: TraineeInfo = {
  name: '',
  email: '',
};

export const traineeInfoSetByStaffsSlice = createSlice({
  name: 'updateTraineeInfo',
  initialState,
  reducers: {
    setTraineeInfo: (state, action: PayloadAction<Partial<TraineeInfo>>) => {
      state.name = action.payload.name || state.name;
      state.email = action.payload.email || state.email;
    },
  },
});

export const { setTraineeInfo } = traineeInfoSetByStaffsSlice.actions;
export default traineeInfoSetByStaffsSlice.reducer;
