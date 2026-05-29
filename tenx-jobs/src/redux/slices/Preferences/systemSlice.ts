import { createSlice, PayloadAction } from "@reduxjs/toolkit";

type VisibilityItem = {
  name: string;
  default: boolean;
  description: string;
};

type VisibilityState = {
  visibility: VisibilityItem[];
};

const initialState: VisibilityState = {
  visibility: [
    {
      name: "hide_action_bar",
      default: true,
      description: "Hide or Not the Floating Action Bar",
    },
    {
      name: "hide_bottom_navigation",
      default: true,
      description: "Hide or Not the Bottom Navigation Bar",
    }
  ]
};

const systemSlice = createSlice({
  name: "visibility",
  initialState,
  reducers: {
    setSystemVisibility: (state, action: PayloadAction<VisibilityItem[]>) => {
      if (action.payload.length === 1) {
        const item = action.payload[0];
        state.visibility = [{
          name: item.name || 'hide_action_bar',
          default: item.default,
          description: item.description || '', 
        }];
      } else {
        state.visibility = action.payload; 
      }
    },
    updateVisibility: (
      state,
      action: PayloadAction<{ name: string; value: boolean }>
    ) => {
      const index = state.visibility.findIndex(
        (item) => item.name === action.payload.name
      );

      if (index !== -1) {
        state.visibility[index].default = action.payload.value;
      } else {
        state.visibility.push(
          {
             name: action.payload.name, 
             default: action.payload.value, 
             description: "" 
            });
      }
    },
  },
});

export const { updateVisibility, setSystemVisibility } = systemSlice.actions;
export default systemSlice.reducer;
