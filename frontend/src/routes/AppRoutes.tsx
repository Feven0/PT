import { Routes, Route, Navigate } from "react-router-dom";
import { Jobs, JobDetail, UploadCV, PersonalActivity } from '../pages/index';
import Navbar from "../components/Navbar";
import { MainActivity } from "../components/personal/index";


const AppRoutes = () => (
  <div className="App">
    <Navbar/>
    <Routes>
      <Route path="/" element={<UploadCV />} />
      <Route path="/jobs" element={<Jobs />} />
      <Route path="/job_detail/:id" element={<JobDetail />} />
      <Route path="/personal_dashboard" element={<PersonalActivity/>}/>
      <Route path="/main_activity/:jbId/:sessionId" element={<MainActivity/>}/>
    </Routes>
  </div>
);

export default AppRoutes;