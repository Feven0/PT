import { Routes, Route, useLocation } from "react-router-dom";
import { Jobs, JobDetail } from '../pages/index';
import Navbar from "../components/Navbar";
import Trainee from '../pages/Trainee';
import AudioChat from "../components/AudioChat";

const AppRoutes = () => {
  const location = useLocation();

  return (
    <div className="App">
      {location.pathname !== '/' && <Navbar />}
      <Routes>
        <Route path="/" element={<Trainee />} />
        <Route path="/jobs/:userId" element={<Jobs />} />
        <Route path="/job_detail/:userId/:jobId" element={<JobDetail />} />
        <Route path="/audio" element={<AudioChat/>} />
      </Routes>
    </div>
  );
};

export default AppRoutes;