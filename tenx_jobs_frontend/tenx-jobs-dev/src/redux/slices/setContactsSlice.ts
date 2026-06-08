import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export type TContacts = {
  name: string;
  value: string | null;
  icon?: string;
};

export type TContactForms = {
  id?: string;
  phone: {
    name: string;
    value: string | null;
    icon?: string;
  }[];
};

const initialState: TContactForms = {
  phone: [
    {
      name: "",
      value: "",
      icon: "",
    },
  ],
};

const setContactsSlice = createSlice({
  name: "contactsForm",
  initialState,
  reducers: {
    setContactsForm: (state, action: PayloadAction<Partial<TContactForms>>) => {
      return {
        ...state,
        ...action.payload,
      };
    },
    addContactsSession: (state) => {
      return {
        ...state,
        phone: [
          ...state.phone,
          {
            name: "",
            value: "",
          },
        ],
      };
    },
    resetContactsForm: () => {
      return initialState;
    },
    removeContactsSession: (state, action: PayloadAction<number>) => {
      return {
        ...state,
        phone: state.phone.filter((_, index) => index !== action.payload),
      };
    },
  },
});

export const {
  setContactsForm,
  addContactsSession,
  resetContactsForm,
  removeContactsSession,
} = setContactsSlice.actions;
export default setContactsSlice.reducer;
