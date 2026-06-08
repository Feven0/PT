import { useEffect } from "react"
import { useDispatch } from "react-redux"

import { Navigate, Outlet, useLocation } from "react-router-dom"
import { useAppSelector } from "../redux/hooks/hooks"
import { persistor } from "../redux/store"
import { getWithExpiry } from "../utils/BrowserFunction"
import { reset } from "../redux/slices/userSlices"
import Unauthorized from "../components/commonComponents/Unauthorized"

const useAuth = () => {
  const role = useAppSelector(state => state.user?.role)
  const checkToken = useAppSelector(state => state.user?.token) as string

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

type ProtectedRouteType = {
  roleRequired: "Staff" | "Trainee"
}

export default function ProtectedRoutes({ roleRequired }: ProtectedRouteType) {
  const dispatch = useDispatch()
  const location = useLocation()

  const { auth, role } = useAuth()
  useEffect(() => {
    if (!auth) {
      dispatch(reset())

      sessionStorage.clear()
      localStorage.clear()

      persistor.pause();
      persistor.flush().then(() => {
        return persistor.purge();
      });
      persistor.persist();

      window.location.reload()
    }
  }, [location.pathname])

  return auth ? (
    roleRequired === role ? (
      <Outlet />
    ) : (
      <Unauthorized />
    )
  ) : (
    <Navigate to="/login" />
  )
}