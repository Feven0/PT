export type UserStats = {
  all_user_id: string;
  Name: string;
  Gender: string;
  Intensive_Training_Performance: string;
  Cummulative_Intensive_Training_Score: number;
  Interested: number;
  Applied: number;
  Rejections: number;
  Interviews: number;
  Offers: number;
  Challenges_Completed: number;
  Standup_Attendance: number;
  Total_Score: number;
  Max_Score: number;
  Success_Probability: string;
};

export type ApiResponse = {
  all_user_id: number;
  stats: UserStats[];
  batches: number[];
  weeks: string[];
  num_of_assignments: number;
  status: number;
  message: string;
};

export type AggregatedStats = {
  successProbability: number;
  interested: number;
  applied: number;
  rejections: number;
  interviews: number;
  offers: number;
  challengesCompleted: number;
  standupAttendance: number;
  count: number;
};

export type AggregatedData = {
  gender: { [key: string]: AggregatedStats };
  performance: { [key: string]: AggregatedStats };
};

export type EngagementStat = {
  name: string;
  "Challenges Completed(%)": number;
  "Standup Attendance(%)": number;
};

export type ApplicationStat = {
  name: string;
  Interested: number;
  Applied: number;
  Rejections: number;
  Interviews: number;
  Offers: number;
};

export type GeneralAggregateCountStats = {
  maleCount: number;
  femaleCount: number;
  excellentPerformers: number;
  goodPerformers: number;
  poorPerformers: number;
};
