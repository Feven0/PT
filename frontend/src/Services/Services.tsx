import axios from 'axios' 

const Api = {
  uploadpdf: data => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/upload`, data),
  audioUpload: data => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/audio_upload`,data),
  audUpload: data => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/transcribe`,data),
  txtspeech: data => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/synthesize`,data),
  sessionCreate: data => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/create_user_session`, data),
  fetchSession: data => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/wv/fetch_user_session`, data),
  fetchChatHistory: data => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/wv/fetch_chat_history`, data),
  fetchChatObserver: data => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/wv/fetch_chat_observer`, data),
  clarify: data => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/clarify`, data),
  overallmetrics: data => axios.post(`${import.meta.env.VITE_REACT_APP_BACKEND_URL}/api/calculate_overall_progress`, data)
};


export default Api;