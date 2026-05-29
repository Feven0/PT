import moment from 'moment';

export const calculateDuration = (startDate: string, endDate: string | null | undefined): string => {
  const start = moment(startDate);
  const end = endDate ? moment(endDate) : moment();

  const years = end.diff(start, 'years');
  start.add(years, 'years');

  const months = end.diff(start, 'months');
  
  let duration = '';
  if (years > 0) {
    duration += `${years}yr${years > 1 ? 's' : ''}`;
  }
  if (months > 0) {
    if (duration) duration += ' ';
    duration += `${months}month${months > 1 ? 's' : ''}`;
  }
  
  return duration || 'less than a month';
};
