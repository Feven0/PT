import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { TableSliceTypes, reportType } from "../../types/TableTypes";

const initialState: TableSliceTypes = {
  selectedRowKeys: [],
  selectedRows: [],
  emails: [],
  failedReport: [],
  successReport: [],
  printData: {
    to: "",
    cc: "",
    sender: "",
    subject: "",
    body: "",
    sentCount: 0,
    failedCount: 0,
  },
};

const TableExtensionSlice = createSlice({
  name: "tableExtension",
  initialState: initialState,
  reducers: {
    setTableExtension: (
      state,
      action: PayloadAction<Partial<TableSliceTypes>>
    ) => {
      return {
        ...state,
        ...action.payload,
      };
    },
    setEmails: (
      state,
      action: PayloadAction<{ name: string; email: string }[]>
    ) => {
      state.emails = action.payload.map((item) => ({
        name: item.name,
        email: item.email,
      }));
    },
    pushSuccessReport: (state, action: PayloadAction<reportType>) => {
      state.successReport.push(action.payload);
    },
    pushFailedReport: (state, action: PayloadAction<reportType>) => {
      state.failedReport.push(action.payload);
    },
    resetTableExtension: () => {
      return initialState;
    },
    resetSelectedRows: (state) => {
      state.selectedRowKeys = [];
      state.selectedRows = [];
    }
  },
});

export const {
  setTableExtension,
  pushSuccessReport,
  resetSelectedRows,
  setEmails,
  pushFailedReport,
  resetTableExtension,
} = TableExtensionSlice.actions;
export default TableExtensionSlice.reducer;
