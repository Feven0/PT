import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface GridView {
  selectedTab: 'list' | 'grid';
}

const initialState: GridView = {
  selectedTab: 'list',
};

const gridViewSlice = createSlice({
  name: 'gridView',
  initialState,
  reducers: {
    setSelectedGridView: (state, action: PayloadAction<'list' | 'grid'>) => {
      state.selectedTab = action.payload;
    },
  },
});

export const { setSelectedGridView } = gridViewSlice.actions;
export default gridViewSlice.reducer;
