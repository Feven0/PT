import axios from 'axios' 

const Api = {
  uploadpdf: data => axios.post('http://0.0.0.0:5900/api/upload', data),
  audioUpload: data => axios.post('http://0.0.0.0:5900/api/audio_upload',data),
  sessionCreate: data => axios.post('http://0.0.0.0:5900/api/create_user_session', data),
  fetchSession: data => axios.post('http://0.0.0.0:5900/wv/fetch_user_session', data),
  fetchChatHistory: data => axios.post('http://0.0.0.0:5900/wv/fetch_chat_history', data),
  clarify: data => axios.post('http://0.0.0.0:5900/api/clarify', data),
  overallmetrics: data => axios.post('http://0.0.0.0:5900/api/calculate_overall_progress', data)
};


export default Api;