import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export type CompanySizeType = {
  name: string;
  priority: "high" | "medium" | "low" | null;
}

type CompanySizeState = {
  company_size: CompanySizeType[];
  companySizeOptions: string[]; 
}

const initialState: CompanySizeState = {
  company_size: [],
  companySizeOptions: ["Small", "Medium", "Large", "Start Up"]
};

const companySizeSlice = createSlice({
  name: "companySizePreference",
  initialState,
  reducers: {
    setCompanySizePreference: (state, action: PayloadAction<CompanySizeType[]>) => {
      state.company_size = action.payload
    },
    addCompanySizePreference: (state, action: PayloadAction<CompanySizeType>) => {
      const existingCompanySize = state.company_size.find(
        (role) => role.name.toLowerCase() === action.payload.name.toLowerCase()
      );
      if (!existingCompanySize) {
        state.company_size.push(action.payload);
      } else {
        existingCompanySize.priority = action.payload.priority;
      }
    },
    removeCompanySizePreference: (state, action: PayloadAction<string>) => {
      state.company_size = state.company_size.filter((role) => role.name !== action.payload);
    },
    updateCompanySizePriority: (
      state,
      action: PayloadAction<{ name: string; priority: "high" | "medium" | "low" }>
    ) => {
      state.company_size = state.company_size.map((role) =>
        role.name === action.payload.name
          ? { ...role, priority: action.payload.priority }
          : role
      );
    },
   updateCompanyName: (
      state,
      action: PayloadAction<{ index: number; newName: string }>
    ) => {
      const { index, newName } = action.payload;
      const companyIndex = state.company_size.indexOf(state.company_size[index]);
      state.company_size[companyIndex].name = newName;
    },
    setCompanySizeOptions: (state, action: PayloadAction<string[]>) => {
      state.companySizeOptions = action.payload;
    },
    removeCompanySizeOption: (state, action: PayloadAction<string>) => { 
      state.companySizeOptions = state.companySizeOptions.filter(size => size !== action.payload);
    }
  },
});

export const { 
  addCompanySizePreference,
  removeCompanySizePreference,
  updateCompanySizePriority,
  updateCompanyName,
  setCompanySizePreference,
  setCompanySizeOptions,
  removeCompanySizeOption
 } = companySizeSlice.actions;
export default companySizeSlice.reducer;
