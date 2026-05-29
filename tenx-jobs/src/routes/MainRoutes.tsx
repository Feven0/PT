import { lazy } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import PublicRoutes from "./PublicRoutes";
import ProtectedRoutes from "./ProtectedRoutes";
import Login from "../pages/Auth/Login";
import Staff from '../pages/Staff';
import Trainee from "../pages/Trainee";

import Jobs from "../pages/TraineePage/Jobs";

const MatchDetail = lazy(()=>import("../pages/TraineePage/MatchDetail"));
const ExpandDetails = lazy(()=>import("../pages/TraineePage/ExpandDetails"));
const MyJobs = lazy(()=>import("../pages/TraineePage/MyJobs"));
const TraineeDetails = lazy(()=>import("../pages/Staff/TraineeDetails"));
const Preferences = lazy(()=>import("../pages/TraineePage/Preferences"));
const ExportableContent = lazy(()=>import("../pages/TraineePage/ExportableContent"));
const TraineeProfile = lazy(()=>import("../pages/TraineePage/TraineeProfile"));
const TraineeEngagements = lazy(()=>import("../pages/Staff/TraineeEngagements"));
const EngagementDetails = lazy(()=>import("../pages/Staff/EngagementDetails"));

import StaffHome from "../pages/Staff/StaffHome";
import CreateNewDirectAsset from "../pages/TraineePage/CreateNewDirectAsset";
import PageNotfound from "../components/commonComponents/PageNotfound";
import TraineeStats from "../pages/Staff/TraineeStats";

export default function MainRoutes() {

    return (
        <Routes>
            {/* PUBLIC ROUTES */}
            <Route
                path='/'
                element={<PublicRoutes />}>
                <Route
                    path="/"
                    element={<Navigate replace to="login" />} />
                <Route
                    path="/login"
                    element={<Login />}
                />

            </Route>
             <Route path="/trainee" element={<ProtectedRoutes roleRequired='Trainee' />}>
                <Route path="/trainee" element={<Trainee />} >
                    <Route path="/trainee/" element={<Jobs />} />
                    <Route path="/trainee/my-jobs/" element={<MyJobs />} />
                    <Route path="/trainee/match-detail/:id" element={<MatchDetail />} />
                    <Route path="/trainee/trainee_engagements/:all_user_id/:user_profile_id/:user_reaction_id" element={<ExpandDetails/>} />                       
                    <Route path="/trainee/export-profile" element={<ExportableContent />} />
                    <Route path="/trainee/trainee-profile" element={<TraineeProfile />} />
                    <Route path="/trainee/job/CreateNewAsset" element={<CreateNewDirectAsset />} />
                    <Route path="/trainee/preferences" element={<Preferences />} />
                </Route>
            </Route>
            {/*Staff Routes */}

            <Route path="/staff" element={<ProtectedRoutes roleRequired='Staff' />}>
                <Route element={<Staff />}>
                    <Route path="/staff/" element={<StaffHome />} />
                    <Route path="/staff/trainee-details/:id" element={<TraineeProfile />} />
                    <Route path="/staff/trainee_details/:allUserID/:trainee_id/:user_profile_id" element={<TraineeDetails />} />
                    <Route path="/staff/trainee_engagements/:all_user_id/:user_profile_id" element={<TraineeEngagements/>} />       
                    <Route path="/staff/trainee_engagements/:all_user_id/:user_profile_id/:user_reaction_id" element={<EngagementDetails/>} />
                    <Route path="/staff/trainee-stats" element={<TraineeStats />} />                   
                
                </Route>
            </Route>
            <Route path="*" element={<PageNotfound />} />
        </Routes>
    );
}

