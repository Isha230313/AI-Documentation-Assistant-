import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/auth'

interface Props {
  children: ReactNode
}

/**
 * Wraps routes that require both authentication and the "admin" role.
 * - No token → redirect to /login
 * - Token but non-admin role → redirect to /chat
 */
export default function AdminRoute({ children }: Props) {
  const token = useAuthStore((s) => s.token)
  const user = useAuthStore((s) => s.user)
  const location = useLocation()

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (user && user.role !== 'admin') {
    return <Navigate to="/chat" replace />
  }

  return <>{children}</>
}
