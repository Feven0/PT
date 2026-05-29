import { createSlice, PayloadAction } from "@reduxjs/toolkit";

type TTab = {
  jobsTab: string;
  siderOpen: boolean;
  siderDisplay: {
    title: string;
    content: string;
  };
  siderTab: string;
  contentCollapsed: boolean;
  profileTab: string;
  profileTabStaffView: string;
  staffProfileTab: string;
  staffEngagementTab: string;
  staffEngagementDetailsTab: string;
  engagementTabs: string;
  expandDetailsTabs: string;
  preferenceTab: string;
  reportJobTab: string;
};

const initialState: TTab = {
  jobsTab: "1",
  siderOpen: false,
  siderDisplay: {
    title: "",
    content: "",
  },
  siderTab: "1",
  contentCollapsed: false,
  profileTab: "1",
  profileTabStaffView: "1",
  staffProfileTab: "1",
  staffEngagementTab: "1",
  staffEngagementDetailsTab: "1",
  engagementTabs: "1",
  expandDetailsTabs: "1",
  preferenceTab: "1",
  reportJobTab: "1",
};

export const tabsSlice = createSlice({
  name: "tabs",
  initialState,
  reducers: {
    setJobsTab: (state, { payload }: PayloadAction<string>) => {
      state.jobsTab = payload;
    },
    setSiderOpen: (state, { payload }: PayloadAction<boolean>) => {
      state.siderOpen = payload;
    },
    setSiderDisplay: (
      state,
      { payload }: PayloadAction<{ title: string; content: string }>
    ) => {
      state.siderDisplay = payload;
    },
    setSiderTab: (state, { payload }: PayloadAction<string>) => {
      state.siderTab = payload;
    },
    setContentCollapsed: (state, { payload }: PayloadAction<boolean>) => {
      state.contentCollapsed = payload;
    },
    setProfileTabs: (state, { payload }: PayloadAction<string>) => {
      state.profileTab = payload;
    },
    setProfileTabsStaffView: (state, { payload }: PayloadAction<string>) => {
      state.profileTabStaffView = payload;
    },
    setStaffProfileTabsView: (state, { payload }: PayloadAction<string>) => {
      state.staffProfileTab = payload;
    },
    setEngagementTabs: (state, { payload }: PayloadAction<string>) => {
      state.engagementTabs = payload;
    },
    setExpandDetailsTabs: (state, { payload }: PayloadAction<string>) => {
      state.expandDetailsTabs = payload;
    },
    setPreferenceTab: (state, { payload }: PayloadAction<string>) => {
      state.preferenceTab = payload;
    },
    setReportJobTab: (state, { payload }: PayloadAction<string>) => {
      state.reportJobTab = payload;
    },
    setStaffEngagementTab: (state, { payload }: PayloadAction<string>) => {
      state.staffEngagementTab = payload;
    },
    setStaffEngagementDetailsTab: (
      state,
      { payload }: PayloadAction<string>
    ) => {
      state.staffEngagementDetailsTab = payload;
    },
  },
});

export const {
  setJobsTab,
  setStaffProfileTabsView,
  setProfileTabsStaffView,
  setSiderTab,
  setProfileTabs,
  setSiderOpen,
  setSiderDisplay,
  setEngagementTabs,
  setStaffEngagementTab,
  setExpandDetailsTabs,
  setStaffEngagementDetailsTab,
  setPreferenceTab,
  setReportJobTab,
  setContentCollapsed,
} = tabsSlice.actions;
export default tabsSlice.reducer;
