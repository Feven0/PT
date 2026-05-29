export const ApplicationStates = [
  "Interested",
  "Applied",
  "Interview scheduled",
  "Technical challenge completed",
  "Rejection letter received (from application)",
  "Rejection letter received (from interview)",
  "Offer received",
  "No response received - archived",
];
export const newJobApplication = ["Applied", "Ready to apply", "Interested"];
export const NewJobApplicationFilterOptions = (): {
  value: string;
  text: string;
}[] => {
  return newJobApplication.map((item) => ({
    value: item,
    text: item,
  }));
};

export const ApplicationStatusFilterOptions = (): {
  value: string;
  text: string;
}[] => {
  return ApplicationStates.map((item) => ({
    value: item,
    text: item,
  }));
};
