import type { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import OrbBackground from './OrbBackground'

interface Props {
  children: ReactNode
}

/**
 * Shared page shell with the animated orb background and a slim top-right nav pill.
 * Shows:
 *   - On /chat  → "⚙️ Admin" link (admin users only) + logout
 *   - On /admin → "💬 Go to Chat" link + logout
 */
export default function Layout({ children }: Props) {
  const { user, logout } = useAuthStore()
  const location = useLocation()
  const isChat = location.pathname === '/chat'
  const isAdmin = location.pathname === '/admin'

  return (
    <div className="relative min-h-screen flex flex-col" style={{ backgroundColor: '#0a0a0a' }}>
      <OrbBackground />

      {/* Top bar */}
      <header
        className="relative z-10 flex items-center justify-between px-6 py-4"
        style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}
      >
        {/* Brand */}
        <div className="flex items-center gap-2.5">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-lg font-bold"
            style={{
              background: 'linear-gradient(135deg, #3b82f6, #06b6d4)',
              boxShadow: '0 0 16px rgba(59,130,246,0.5)',
            }}
          >
            A
          </div>
          <span className="font-semibold text-sm tracking-wide text-white/80">
            AI Docs Assistant
          </span>
        </div>

        {/* Right pill group */}
        <div className="flex items-center gap-2">
          {isChat && user?.role === 'admin' && (
            <Link to="/admin" className="ghost-btn text-xs">
              <span>⚙️</span>
              <span>Admin</span>
            </Link>
          )}

          {isAdmin && (
            <Link to="/chat" className="ghost-btn text-xs">
              <span>💬</span>
              <span>Go to Chat</span>
            </Link>
          )}

          {user && (
            <div className="flex items-center gap-2 ml-1">
              <span className="text-xs text-white/40 hidden sm:block">
                {user.username}
                {user.role === 'admin' && (
                  <span
                    className="ml-1.5 px-1.5 py-0.5 rounded-full text-[10px] font-medium"
                    style={{
                      background: 'rgba(6,182,212,0.2)',
                      border: '1px solid rgba(6,182,212,0.4)',
                      color: '#67e8f9',
                    }}
                  >
                    admin
                  </span>
                )}
              </span>
              <button
                onClick={logout}
                className="ghost-btn text-xs text-red-400/70 hover:text-red-300 border-red-500/20 hover:border-red-500/40 hover:bg-red-500/5"
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
