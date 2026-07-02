import { useEffect, type ReactNode } from 'react'
import { useThemeStore } from '../store/theme'

export default function ThemeProvider({ children }: { children: ReactNode }) {
  const { isDark } = useThemeStore()

  useEffect(() => {
    const root = document.documentElement
    if (isDark) {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }, [isDark])

  return <>{children}</>
}
