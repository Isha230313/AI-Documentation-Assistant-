export default function Spinner({ size = 4 }: { size?: number }) {
  return (
    <span
      className={`inline-block w-${size} h-${size} rounded-full border-2 border-white/20 border-t-indigo-400 animate-spin-slow`}
      role="status"
      aria-label="Loading"
    />
  )
}
