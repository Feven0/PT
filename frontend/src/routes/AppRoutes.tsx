import { Routes, Route, Navigate } from "react-router-dom";
import { Jobs, JobDetail } from '../pages/index';

const AppRoutes = () => (
  <div className="App">
    <Routes>
      <Route path="/" element={<Jobs />} />
      <Route path="/job_detail/:id" element={<JobDetail />} />
    </Routes>
  </div>
);

export default AppRoutes;