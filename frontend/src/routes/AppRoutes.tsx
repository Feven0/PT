import { Routes, Route } from "react-router-dom";
import { Jobs, JobDetail } from '../pages/index';
import Navbar from "../components/Navbar";
import Trainee from '../pages/Trainee'


const AppRoutes = () => (
  <div className="App">
    <Navbar/>
    <Routes>
      <Route path="/" element={<Trainee />} />
      <Route path="/jobs/:userId" element={<Jobs />} />
      <Route path="/job_detail/:userId/:jobId" element={<JobDetail />} />
    </Routes>
  </div>
);

export default AppRoutes;