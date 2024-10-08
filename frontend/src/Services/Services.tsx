import axios from 'axios' 

const Api = {
  uploadpdf: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/upload`, data),
  audioUpload: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/audio_upload`,data),
  sessionCreate: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/create_user_session`, data),
  fetchSession: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/wv/fetch_user_session`, data),
  fetchChatHistory: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/wv/fetch_chat_history`, data),
  clarify: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/clarify`, data),
  overallmetrics: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/calculate_overall_progress`, data)
};


export default Api;