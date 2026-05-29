import { Navigate, Outlet } from 'react-router-dom'
import { useAppSelector } from "../redux/hooks/hooks"
import { getWithExpiry } from "../utils/BrowserFunction"


const useAuth = () => {
  const role = useAppSelector((state) => state.user?.role)
  const checkToken = useAppSelector((state) => state.user?.token ?? "");

  const token = getWithExpiry("token")
  const isTokenValid = token && token === checkToken ? true : false

  if (isTokenValid) {
    if (role === "Staff" || role === "Trainee") {
      return {
        auth: true,
        role: role,
      }
    } else {
      return {
        auth: true,
        role: null,
      }
    }
  } else {
    return {
      auth: false,
      role: null,
    }
  }
}


export default function PublicRoutes() {

  const { auth, role } = useAuth()

  if (auth && role) {
    const attemptedURL = sessionStorage.getItem("attemptedURL");
    if (role === "Staff") {
      return <Navigate to="/staff" />
    }
    else if (role === "Trainee" && attemptedURL) {
      return <Navigate to={attemptedURL} />
    }
    else if (role === "Trainee" && !attemptedURL) {
      return <Navigate to="/trainee" />
    }
  } else {
    return <Outlet />
  }
}
