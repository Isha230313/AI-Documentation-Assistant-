import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/auth'

interface Props {
  children: ReactNode
}

/**
 * Wraps any route that requires a valid JWT.
 * Unauthenticated users are redirected to /login, with the intended path saved
 * in location state so they can be bounced back after a successful login.
 */
export default function ProtectedRoute({ children }: Props) {
  const token = useAuthStore((s) => s.token)
  const location = useLocation()

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}
