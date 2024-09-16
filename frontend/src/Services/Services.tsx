import axios from 'axios' 

// const Api = {
//   uploadpdf: data => axios.post('http://0.0.0.0:8000/api/upload', data),
//   analyse: data => axios.post('http://0.0.0.0:8000/analyse/',data),
//   interview: data => axios.post('http://0.0.0.0:8000/interview/',data),
//   audioUpload: data => axios.post('http://0.0.0.0:8000/api/audio_upload',data),
//   analyseDoc: data => axios.post('http://0.0.0.0:8000/api/analyse_cv', data),
//   fetchSession: data => axios.post('http://0.0.0.0:8000/api/fetch_user_session', data),
//   fetchSessionJob: data => axios.post('http://0.0.0.0:8000/api/fetch_session_job', data),
// };


const Api = {
  uploadpdf: data => axios.post('http://0.0.0.0:5500/api/upload', data),
  analyse: data => axios.post('http://0.0.0.0:5500/analyse/',data),
  interview: data => axios.post('http://0.0.0.0:5500/interview/',data),
  audioUpload: data => axios.post('http://0.0.0.0:5500/api/audio_upload',data),
  analyseDoc: data => axios.post('http://0.0.0.0:5500/api/analyse_cv', data),
  fetchSession: data => axios.post('http://0.0.0.0:5500/wv/fetch_user_session', data),
  fetchSessionJob: data => axios.post('http://0.0.0.0:5500/wv/fetch_session_job', data),
};


export default Api;