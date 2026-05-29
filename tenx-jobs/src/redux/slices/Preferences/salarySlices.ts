import { createSlice, PayloadAction } from '@reduxjs/toolkit';

type SalaryRangeState = {
  salary_range: {
    minimum_salary: number;
    maximum_salary: number | undefined;
    unit: string;
    currency: string;
  };
  noMaxLimit: boolean;
}

const initialState: SalaryRangeState = {
  salary_range: {
    minimum_salary: 500,
    maximum_salary: 100000,
    unit: "year",
    currency: "USD",
  },
  noMaxLimit: false,
};

const salarySlice = createSlice({
  name: 'salaryPreference',
  initialState,
  reducers: {
    setSalary: (state, action: PayloadAction<SalaryRangeState['salary_range']>) => {
      state.salary_range = action.payload;
    },
    setMinimumSalary: (state, action: PayloadAction<number>) => {
      state.salary_range.minimum_salary = action.payload;
    },
    setMaximumSalary: (state, action: PayloadAction<number | undefined>) => {
      state.salary_range.maximum_salary = action.payload;
    },
    setUnit: (state, action: PayloadAction<string>) => {
      state.salary_range.unit = action.payload;
    },
    setCurrency: (state, action: PayloadAction<string>) => {
      state.salary_range.currency = action.payload;
    },
    setNoMaxLimit: (state, action: PayloadAction<boolean>) => {
      state.noMaxLimit = action.payload;
      if (action.payload) {
        state.salary_range.maximum_salary = undefined;
      } else {
        state.salary_range.maximum_salary = Math.max(
          state.salary_range.minimum_salary,
          state.salary_range.maximum_salary || 80000
        );
      }
    },
  },
});

export const { 
    setMinimumSalary, 
    setMaximumSalary, 
    setUnit, 
    setCurrency,
    setNoMaxLimit,
    setSalary
  } = salarySlice.actions;
export default salarySlice.reducer;
