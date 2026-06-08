const backendUrl = import.meta.env.VITE_API_LEAP_JOB_BACKEND_URL;

export const getRunStage = (): string => {
  if (backendUrl.includes("dev-frog")) {
    return "dev";
  } else if (backendUrl.includes("frog")) {
    return "prod";
  }
  return "";
};
