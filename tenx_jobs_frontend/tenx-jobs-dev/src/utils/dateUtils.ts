import { DateRange } from "react-day-picker";
import { startOfWeek, endOfWeek, format } from "date-fns";
import dayjs, { Dayjs } from 'dayjs';

export const getCurrentWeekRangeS = (): DateRange => {
  const today = new Date();
  return {
    from: startOfWeek(today, { weekStartsOn: 1 }),
    to: endOfWeek(today, { weekStartsOn: 1 }),
  };
};

export const convertToDayjsRange = (range: DateRange): [Dayjs | null, Dayjs | null] => {
  return [
    range.from ? dayjs(range.from) : null,
    range.to ? dayjs(range.to) : null,
  ];
};

export const formatToISO = (date: Date | undefined): string => {
  if (!date) {
    return "";
  }
  return date.toISOString().split(".")[0] + "Z";
};

export const formatDateRange = (range: DateRange | undefined): string => {
  if (!range || !range.from) {
    return "Select date range";
  }
  if (!range.to) {
    return format(range.from, "MMM d, yyyy");
  }
  return `${format(range.from, "MMM d")} - ${format(range.to, "MMM d, yyyy")}`;
};
