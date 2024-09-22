import { Routes, Route, Navigate } from "react-router-dom";
import { Jobs, JobDetail, UploadCV, PersonalActivity, EvaluationStatus } from '../pages/index';
import Navbar from "../components/Navbar";
import { MainActivity } from "../components/personal/index";
import Test from '../pages/Test'
import Trainee from '../pages/Trainee'


const AppRoutes = () => (
  <div className="App">
    <Navbar/>
    <Routes>
      <Route path="/upload" element={<UploadCV />} />
      <Route path="/" element={<Trainee />} />
      <Route path="/jobs/:userId" element={<Jobs />} />
      <Route path="/job_detail/:userId/:jobId" element={<JobDetail />} />
      <Route path="/personal_dashboard" element={<PersonalActivity/>}/>
      <Route path="/main_activity/:jbId/:sessionId" element={<MainActivity/>}/>
      <Route path="/evaluation_status/:bool" element={<EvaluationStatus/>}/>
      <Route path="/test" element={<Test/>}/>
    </Routes>
  </div>
);

export default AppRoutes;