import type { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import { useThemeStore } from '../store/theme'
import OrbBackground from './OrbBackground'

interface Props {
  children: ReactNode
}

function SunIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M12 3v1m0 16v1m8.66-9H21M3 12H2m15.07-6.07l-.71.71M7.64 16.36l-.71.71M18.36 16.36l-.71.71M6.34 7.64l-.71-.71M12 5a7 7 0 100 14A7 7 0 0012 5z" />
    </svg>
  )
}

function MoonIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
    </svg>
  )
}

export default function Layout({ children }: Props) {
  const { user, logout } = useAuthStore()
  const { isDark, toggle } = useThemeStore()
  const location = useLocation()
  const isChat = location.pathname === '/chat'
  const isAdmin = location.pathname === '/admin'

  return (
    <div
      className="relative min-h-screen flex flex-col"
      style={{ backgroundColor: isDark ? '#0a0a0a' : '#ffffff' }}
    >
      <OrbBackground />

      {/* Top bar */}
      <header
        className="relative z-10 flex items-center justify-between px-6 py-4"
        style={{ borderBottom: isDark ? '1px solid rgba(255,255,255,0.05)' : '1px solid rgba(0,0,0,0.08)' }}
      >
        {/* Brand */}
        <div className="flex items-center gap-2.5">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-lg font-bold text-white"
            style={{
              background: 'linear-gradient(135deg, #3b82f6, #06b6d4)',
              boxShadow: '0 0 16px rgba(59,130,246,0.4)',
            }}
          >
            A
          </div>
          <span className={`font-semibold text-sm tracking-wide ${isDark ? 'text-white/80' : 'text-gray-700'}`}>
            AI Docs Assistant
          </span>
        </div>

        {/* Right pill group */}
        <div className="flex items-center gap-2">
          {isChat && user?.role === 'admin' && (
            <Link to="/admin" className="ghost-btn text-xs">
              <span>⚙️</span><span>Manage Docs</span>
            </Link>
          )}
          {isAdmin && (
            <Link to="/chat" className="ghost-btn text-xs">
              <span>💬</span><span>Go to Chat</span>
            </Link>
          )}

          {/* Theme toggle */}
          <button
            onClick={toggle}
            className="ghost-btn px-2.5 py-2"
            title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            aria-label="Toggle theme"
          >
            {isDark ? <SunIcon /> : <MoonIcon />}
          </button>

          {user && (
            <div className="flex items-center gap-2 ml-1">
              <span className={`text-xs hidden sm:block ${isDark ? 'text-white/40' : 'text-gray-500'}`}>
                {user.username}
              </span>
              <button
                onClick={logout}
                className={`ghost-btn text-xs border-red-200 hover:border-red-300 hover:bg-red-50
                  ${isDark ? 'text-red-400/70 hover:text-red-300 dark:border-red-500/20 dark:hover:border-red-500/40 dark:hover:bg-red-500/5' : 'text-red-500/80 hover:text-red-600'}`}
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Page content */}
      <main className="relative z-10 flex-1 flex flex-col min-h-0">{children}</main>
    </div>
  )
}
