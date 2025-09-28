import { Routes, Route, useLocation } from "react-router-dom";
import { Jobs, JobDetail } from '../pages/index';
import Navbar from "../components/Navbar";
import Trainee from '../pages/Trainee';
import OpenAIRealtimeTest from "../components/OpenAIRealtimeTest";
import AssemblyAITest from '../pages/AssemblyAITest';

const AppRoutes = () => {
  const location = useLocation();

  return (
    <div className="App">
      {location.pathname !== '/' && <Navbar />}
      <Routes>
        <Route path="/" element={<Trainee />} />
        <Route path="/jobs/:userId" element={<Jobs />} />
        <Route path="/job_detail/:userId/:jobId" element={<JobDetail />} />
        <Route path="/dev/openai-realtime" element={<OpenAIRealtimeTest />} />
        <Route path="/dev/assemblyai-test" element={<AssemblyAITest />} />
      </Routes>
    </div>
  );
};

export default AppRoutes;