/**
 * Animated gradient orb blobs that match the Streamlit dark-neon aesthetic.
 * Two blobs float independently using CSS keyframe animations.
 */
export default function OrbBackground() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 overflow-hidden"
      style={{ zIndex: 0 }}
    >
      {/* Orb 1 — indigo / violet, top-left area */}
      <div
        className="absolute animate-orb-float-1"
        style={{
          top: '-10%',
          left: '-8%',
          width: '55vw',
          height: '55vw',
          maxWidth: '700px',
          maxHeight: '700px',
          borderRadius: '50%',
          background:
            'radial-gradient(circle at 40% 40%, rgba(99,102,241,0.45) 0%, rgba(139,92,246,0.28) 45%, transparent 70%)',
          filter: 'blur(50px)',
          willChange: 'transform',
        }}
      />

      {/* Orb 2 — pink / fuchsia, bottom-right area */}
      <div
        className="absolute animate-orb-float-2"
        style={{
          bottom: '-12%',
          right: '-10%',
          width: '50vw',
          height: '50vw',
          maxWidth: '650px',
          maxHeight: '650px',
          borderRadius: '50%',
          background:
            'radial-gradient(circle at 60% 60%, rgba(236,72,153,0.38) 0%, rgba(244,114,182,0.22) 45%, transparent 70%)',
          filter: 'blur(55px)',
          willChange: 'transform',
        }}
      />

      {/* Subtle mesh overlay */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(rgba(99,102,241,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99,102,241,0.03) 1px, transparent 1px)
          `,
          backgroundSize: '64px 64px',
        }}
      />
    </div>
  )
}
