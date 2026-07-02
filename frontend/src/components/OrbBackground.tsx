import { useThemeStore } from '../store/theme'

export default function OrbBackground() {
  const { isDark } = useThemeStore()

  const orb1Opacity = isDark ? 0.75 : 0.18
  const orb2Opacity = isDark ? 0.65 : 0.15
  const orb1SecondaryOpacity = isDark ? 0.45 : 0.10
  const orb2SecondaryOpacity = isDark ? 0.40 : 0.08
  const blurAmount = isDark ? '35px' : '50px'

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 overflow-hidden"
      style={{ zIndex: 0 }}
    >
      {/* Orb 1 — blue, top-left */}
      <div
        className="absolute animate-orb-float-1"
        style={{
          top: '-5%', left: '-5%',
          width: '65vw', height: '65vw',
          maxWidth: '800px', maxHeight: '800px',
          borderRadius: '50%',
          background: `radial-gradient(circle at 40% 40%, rgba(59,130,246,${orb1Opacity}) 0%, rgba(37,99,235,${orb1SecondaryOpacity}) 40%, transparent 70%)`,
          filter: `blur(${blurAmount})`,
          willChange: 'transform',
        }}
      />

      {/* Orb 2 — cyan, bottom-right */}
      <div
        className="absolute animate-orb-float-2"
        style={{
          bottom: '-8%', right: '-8%',
          width: '60vw', height: '60vw',
          maxWidth: '750px', maxHeight: '750px',
          borderRadius: '50%',
          background: `radial-gradient(circle at 60% 60%, rgba(6,182,212,${orb2Opacity}) 0%, rgba(14,165,233,${orb2SecondaryOpacity}) 40%, transparent 70%)`,
          filter: `blur(${blurAmount})`,
          willChange: 'transform',
        }}
      />

      {/* Mesh grid overlay */}
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `
            linear-gradient(rgba(59,130,246,${isDark ? 0.07 : 0.04}) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59,130,246,${isDark ? 0.07 : 0.04}) 1px, transparent 1px)
          `,
          backgroundSize: '64px 64px',
          opacity: isDark ? 0.4 : 0.6,
        }}
      />
    </div>
  )
}
