import { useState, type FormEvent } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import { login } from '../api/auth'
import { apiClient } from '../api/client'
import { useAuthStore } from '../store/auth'
import OrbBackground from '../components/OrbBackground'
import Spinner from '../components/Spinner'
import type { ApiErrorDetail, User } from '../types'

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { setAuth } = useAuthStore()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname ?? '/chat'

  const loginMutation = useMutation({
    mutationFn: () => login(username, password),
    onSuccess: async (tokenData) => {
      try {
        const meRes = await apiClient.get<User>('/auth/me', {
          headers: { Authorization: `Bearer ${tokenData.access_token}` },
        })
        setAuth(tokenData.access_token, meRes.data)
      } catch {
        setAuth(tokenData.access_token, { username, role: 'user', is_active: true })
      }
      navigate(from, { replace: true })
    },
    onError: (error: unknown) => {
      if (error instanceof AxiosError) {
        const detail = (error.response?.data as ApiErrorDetail)?.detail
        setErrorMsg(detail ?? 'Invalid credentials. Please try again.')
      } else {
        setErrorMsg('An unexpected error occurred. Please try again.')
      }
    },
  })

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    setErrorMsg(null)
    if (!username.trim() || !password) {
      setErrorMsg('Please enter both username and password.')
      return
    }
    loginMutation.mutate()
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4" style={{ backgroundColor: '#0a0a0a' }}>
      <OrbBackground />

      <div className="relative z-10 w-full max-w-md animate-slide-up">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl font-extrabold text-white"
              style={{ background: 'linear-gradient(135deg, #3b82f6, #06b6d4)', boxShadow: '0 0 32px rgba(59,130,246,0.5)' }}
            >
              A
            </div>
          </div>
          <h1 className="text-3xl font-bold text-white mb-1">Welcome back</h1>
          <p className="text-white/40 text-sm">Sign in to your Documentation Assistant</p>
        </div>

        <div className="glass-card p-8" style={{ boxShadow: '0 0 40px rgba(59,130,246,0.08), 0 24px 64px rgba(0,0,0,0.5)' }}>
          <form onSubmit={handleSubmit} noValidate className="space-y-5">
            {errorMsg && (
              <div className="error-banner" role="alert">
                <span>{errorMsg}</span>
              </div>
            )}

            <div className="space-y-1.5">
              <label htmlFor="username" className="block text-sm font-medium text-white/70">Username</label>
              <input
                id="username"
                type="text"
                autoComplete="username"
                autoFocus
                className="input-field"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={loginMutation.isPending}
              />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="password" className="block text-sm font-medium text-white/70">Password</label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                className="input-field"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loginMutation.isPending}
              />
            </div>

            <button
              type="submit"
              disabled={loginMutation.isPending}
              className="neon-btn w-full justify-center py-3 text-base mt-2 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loginMutation.isPending ? <><Spinner /><span>Signing in…</span></> : 'Sign in'}
            </button>
          </form>
        </div>

        <p className="text-center text-white/20 text-xs mt-6">
          AI Documentation Assistant &copy; {new Date().getFullYear()}
        </p>
      </div>
    </div>
  )
}
