export default function OrbBackground() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 overflow-hidden"
      style={{ zIndex: 0 }}
    >
      {/* Orb 1 — indigo / violet, top-left */}
      <div
        className="absolute animate-orb-float-1"
        style={{
          top: '-5%',
          left: '-5%',
          width: '65vw',
          height: '65vw',
          maxWidth: '800px',
          maxHeight: '800px',
          borderRadius: '50%',
          background:
            'radial-gradient(circle at 40% 40%, rgba(99,102,241,0.75) 0%, rgba(139,92,246,0.45) 40%, transparent 70%)',
          filter: 'blur(35px)',
          willChange: 'transform',
        }}
      />

      {/* Orb 2 — pink / fuchsia, bottom-right */}
      <div
        className="absolute animate-orb-float-2"
        style={{
          bottom: '-8%',
          right: '-8%',
          width: '60vw',
          height: '60vw',
          maxWidth: '750px',
          maxHeight: '750px',
          borderRadius: '50%',
          background:
            'radial-gradient(circle at 60% 60%, rgba(236,72,153,0.65) 0%, rgba(168,85,247,0.40) 40%, transparent 70%)',
          filter: 'blur(35px)',
          willChange: 'transform',
        }}
      />

      {/* Orb 3 — cyan accent, center */}
      <div
        className="absolute"
        style={{
          top: '30%',
          left: '35%',
          width: '40vw',
          height: '40vw',
          maxWidth: '500px',
          maxHeight: '500px',
          borderRadius: '50%',
          background:
            'radial-gradient(circle at 50% 50%, rgba(6,182,212,0.18) 0%, rgba(99,102,241,0.10) 50%, transparent 75%)',
          filter: 'blur(60px)',
        }}
      />

      {/* Mesh grid overlay */}
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `
            linear-gradient(rgba(99,102,241,0.07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99,102,241,0.07) 1px, transparent 1px)
          `,
          backgroundSize: '64px 64px',
          opacity: 0.4,
        }}
      />
    </div>
  )
}
