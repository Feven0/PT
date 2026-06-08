import { Button } from "antd";
import { Download } from "lucide-react";
import '../../../styles/stats.css'

interface CSVExportButtonProps<T extends Record<string, unknown>> {
  data: T[];
  filename?: string;
  title?: string;
  filterParams?: Record<string, string | number | boolean>;
}

function convertToCSV<T extends Record<string, unknown>>(
  objArray: T[],
  title?: string,
  filterParams?: Record<string, string | number | boolean>
): string {
  let str = "";

  if (title) {
    str += `${title}\r\n`;
  }

  if (filterParams) {
    for (const [key, value] of Object.entries(filterParams)) {
      str += `${key}: ${value}\r\n`;
    }
    str += "\r\n"; 
  }

  if (objArray.length === 0) {
    return str;
  }

  const headers = Object.keys(objArray[0]);
  str += headers.join(",") + "\r\n";

  for (let i = 0; i < objArray.length; i++) {
    let line = "";
    for (const index in objArray[i]) {
      if (line !== "") line += ",";
      const value = objArray[i][index];
      line +=
        value !== null && value !== undefined
          ? String(value).replace(/,/g, ";")
          : "";
    }
    str += line + "\r\n";
  }
  return str;
}

export default function CSVExportButton<T extends Record<string, unknown>>({
  data,
  filename = "export.csv",
  title,
  filterParams,
}: CSVExportButtonProps<T>): React.ReactElement {
  const downloadCSV = (): void => {
    const csvContent = convertToCSV(data, title, filterParams);
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute("href", url);
      link.setAttribute("download", filename);
      link.style.visibility = "hidden";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <Button onClick={downloadCSV} className="flex-center gap-8 csv__download-btn">
      <Download size={16} />
        Export CSV
    </Button>
  );
}
