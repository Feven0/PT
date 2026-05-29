import { createSlice, PayloadAction } from "@reduxjs/toolkit";
export type PreferenceLocation = {
  country: string;
  state: string;
  city: string;
  priority: "high" | "medium" | "low" | null;
}

type LocationState = {
  locations: PreferenceLocation[];
}

const initialState: LocationState = {
  locations: [], 
};

export const locationSlice = createSlice({
  name: "locationPreference",
  initialState,
  reducers: {
    setLocationPreference: (state, action: PayloadAction<PreferenceLocation[]>) => {
      state.locations = action.payload;
    },
    addLocation: (state, action: PayloadAction<PreferenceLocation>) => {
      state.locations.push(action.payload);
    },
    removeLocation: (state, action: PayloadAction<string>) => {
      state.locations = state.locations.filter(
        (location) => location.country !== action.payload
      );
    },
    updateLocationPriority: (state, action: PayloadAction<{ country: string; priority: "high" | "medium" | "low" | null }>) => {
      const { country, priority } = action.payload;
      const location = state.locations.find((loc) => loc.country === country);
      if (location) {
        location.priority = priority;
      }
    },
  },
});

export const { addLocation, updateLocationPriority, setLocationPreference, removeLocation } = locationSlice.actions;
export default locationSlice.reducer;
