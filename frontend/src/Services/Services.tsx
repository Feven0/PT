import axios from 'axios' 

const Api = {
  uploadpdf: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/upload`, data),
  audioUpload: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/audio_upload`,data),
  audUpload: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/transcribe`,data),
  txtspeech: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/synthesize`,data),
  sessionCreate: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/create_user_session`, data),
  fetchSession: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/wv/fetch_user_session`, data),
  fetchChatHistory: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/wv/fetch_chat_history`, data),
  fetchSingleSession: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/wv/fetch_single_session`, data),
  clarify: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/clarify`, data),
  UserAllSessionMetrics: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/calculate_allstat_progress`, data),
  OverallSesssionMetrics: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/calculate_session_overall_progress`, data),
  audio: (data: any) => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/synthesize-audio/`, data),

};


export default Api;