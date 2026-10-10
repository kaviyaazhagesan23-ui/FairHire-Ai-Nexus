import { animate, useMotionValue, useReducedMotion } from 'framer-motion'
import { useEffect, useRef, useState, type ReactNode } from 'react'

export function CountUp({ value, digits = 0, suffix = '' }: { value: number; digits?: number; suffix?: string }) {
  const reduce = useReducedMotion()
  const mv = useMotionValue(0)
  const [text, setText] = useState(reduce ? value.toFixed(digits) : (0).toFixed(digits))
  useEffect(() => {
    if (reduce) { setText(value.toFixed(digits)); return }
    const c = animate(mv, value, { duration: 0.9, ease: 'easeOut', onUpdate: (v) => setText(v.toFixed(digits)) })
    return () => c.stop()
  }, [value, digits, reduce, mv])
  return <span>{text}{suffix}</span>
}

export function ProgressRing({ value, size = 92, stroke = 9, label, display }: { value: number; size?: number; stroke?: number; label: string; display?: string }) {
  const clamped = Math.max(0, Math.min(1, value))
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const id = `ring-${size}-${label.replace(/\W/g, '')}`
  return (
    <div className="ring" style={{ width: size, height: size }} role="img" aria-label={`${label}: ${display ?? Math.round(clamped * 100) + '%'}`}>
      <svg width={size} height={size}>
        <defs>
          <linearGradient id={id} x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#4F46E5" /><stop offset="1" stopColor="#0EA5E9" /></linearGradient>
        </defs>
        <circle cx={size / 2} cy={size / 2} r={r} stroke="#E8ECFA" strokeWidth={stroke} fill="none" />
        <circle
          className="ring-arc" cx={size / 2} cy={size / 2} r={r} stroke={`url(#${id})`} strokeWidth={stroke} fill="none"
          strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c * (1 - clamped)} transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="ring-text">{display ?? `${Math.round(clamped * 100)}%`}</div>
    </div>
  )
}

export function MetricBar({ label, value, available = true, text }: { label: string; value?: number; available?: boolean; text?: string }) {
  const v = typeof value === 'number' ? Math.max(0, Math.min(1, value)) : 0
  return (
    <div className="metric">
      <div className="metric-head"><span>{label}</span><strong>{!available || typeof value !== 'number' ? 'Not available' : text ?? `${Math.round(v * 100)}%`}</strong></div>
      <div className="bar" role="presentation"><div className="bar-fill" style={{ width: available ? `${v * 100}%` : 0 }} /></div>
    </div>
  )
}

/** Gentle pointer-driven 3D tilt. Disabled for reduced motion and coarse pointers. */
export function TiltCard({ children, className = '' }: { children: ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null)
  const reduce = useReducedMotion()
  const onMove = (e: React.PointerEvent) => {
    if (reduce || e.pointerType !== 'mouse' || !ref.current) return
    const b = ref.current.getBoundingClientRect()
    const x = (e.clientX - b.left) / b.width - 0.5
    const y = (e.clientY - b.top) / b.height - 0.5
    ref.current.style.transform = `perspective(900px) rotateX(${(-y * 6).toFixed(2)}deg) rotateY(${(x * 8).toFixed(2)}deg) translateZ(0)`
  }
  const reset = () => { if (ref.current) ref.current.style.transform = '' }
  return <div ref={ref} className={`tilt ${className}`} onPointerMove={onMove} onPointerLeave={reset}>{children}</div>
}

export function Sparkles() {
  return (
    <div className="sparkles" aria-hidden="true">
      {[...Array(8)].map((_, i) => <span key={i} style={{ left: `${8 + i * 12}%`, top: `${(i * 37) % 80}%`, animationDelay: `${i * 0.45}s` }} />)}
    </div>
  )
}
