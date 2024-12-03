import axios from 'axios' 

const Api = {
  audioUpload: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/audio_upload`,data),
  sessionCreate: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/create_user_session`, data),
  fetchSession: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/fetch_user_session`, data),
  fetchChatHistory: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/fetch_chat_history`, data),
  fetchSingleSession: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/fetch_single_session`, data),
  clarify: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/clarify`, data),
  UserAllSessionMetrics: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/calculate_allstat_progress`, data),
  OverallSesssionMetrics: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/calculate_session_overall_progress`, data),
  AnalyticsOverview: () => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/admin_overview_status`),
  ApplicationManager: () => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/admin_user_data`),
  UserStatus: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/engagement_jobs_status`, data)
};


export default Api;