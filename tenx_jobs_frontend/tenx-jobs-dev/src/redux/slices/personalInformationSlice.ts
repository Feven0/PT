import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export type TMedia = {
  icon: string;
  link: string;
  name: string;
}

export type TLocation = {
  address: string;
  city: string;
  country: string;
  postal_code: string;
  icon: string;
  region: string;
}

export type TPInfo= {
  info: {
    id: string;
    full_name: string;
    email: string;
    image: string;
    name_title: string;
    personal_statement: string;
    role: string;
    phone: string[];
    location: TLocation;
    media: TMedia[];
  }
}

const initialState: TPInfo = {
  info: {
    id: "",
    full_name: "",
    email: "",
    image: "",
    name_title: "",
    personal_statement: "",
    role: "",
    phone: [],
    location: {
      address: "",
      city: "",
      country: "",
      postal_code: "",
      icon: "",
      region: ""
    },
    media: []
  }
}

const personalInformationSlice = createSlice({
  name: "personalInformation",
  initialState,
  reducers: {
    setPersonalInformation: (state, action: PayloadAction<TPInfo>) => {
      state.info = action.payload.info;
    },
    resetPersonalInformation: (state) => {
      state.info = initialState.info;
    }
  }
});

export const { setPersonalInformation , resetPersonalInformation} = personalInformationSlice.actions;
export default personalInformationSlice.reducer;
