import { cx } from '../lib/utils'

export type AiState = 'idle' | 'listening' | 'thinking' | 'speaking' | 'success' | 'error' | 'muted'

export const stateLabel: Record<AiState, string> = {
  idle: 'Ready',
  listening: 'Listening…',
  thinking: 'Thinking…',
  speaking: 'Speaking',
  success: 'Answer ready',
  error: 'Something went wrong',
  muted: 'Muted (text only)',
}

/** Layered SVG/CSS holographic recruiter orb. Visual behavior is driven by data-state. */
export function Avatar({ state, size = 260 }: { state: AiState; size?: number }) {
  return (
    <div className={cx('avatar')} data-state={state} style={{ width: size, height: size }} role="img" aria-label={`AI recruiter avatar. Status: ${stateLabel[state]}`}>
      <div className="av-ring av-ring-1" />
      <div className="av-ring av-ring-2" />
      <div className="av-ring av-ring-3" />
      <div className="av-pulse" />
      <div className="av-body">
        <svg viewBox="0 0 200 200" width="100%" height="100%">
          <defs>
            <radialGradient id="avOrb" cx="35%" cy="28%" r="80%">
              <stop offset="0" stopColor="#FFFFFF" />
              <stop offset="0.35" stopColor="#C7D2FE" />
              <stop offset="0.75" stopColor="#7C3AED" />
              <stop offset="1" stopColor="#3730A3" />
            </radialGradient>
            <radialGradient id="avGlass" cx="50%" cy="50%" r="60%">
              <stop offset="0" stopColor="#FFFFFF" stopOpacity="0.96" />
              <stop offset="1" stopColor="#E0E7FF" stopOpacity="0.9" />
            </radialGradient>
            <linearGradient id="avEye" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#0EA5E9" /><stop offset="1" stopColor="#4F46E5" /></linearGradient>
          </defs>
          <circle cx="100" cy="100" r="86" fill="url(#avOrb)" />
          <ellipse cx="72" cy="52" rx="34" ry="16" fill="#fff" opacity="0.35" />
          <rect x="45" y="64" width="110" height="78" rx="34" fill="url(#avGlass)" />
          <g className="av-eyes">
            <ellipse className="av-eye" cx="80" cy="97" rx="9" ry="12" fill="url(#avEye)" />
            <ellipse className="av-eye" cx="120" cy="97" rx="9" ry="12" fill="url(#avEye)" />
            <circle cx="83" cy="92" r="3" fill="#fff" />
            <circle cx="123" cy="92" r="3" fill="#fff" />
          </g>
          <path className="av-mouth" d="M84 124 Q100 134 116 124" fill="none" stroke="#4F46E5" strokeWidth="5" strokeLinecap="round" />
          <circle cx="100" cy="46" r="5" fill="#0EA5E9" className="av-antenna" />
          <line x1="100" y1="51" x2="100" y2="64" stroke="#C7D2FE" strokeWidth="3" />
          <g className="av-think" aria-hidden="true">
            <circle cx="62" cy="62" r="3" /><circle cx="100" cy="40" r="3" /><circle cx="138" cy="62" r="3" />
            <line x1="62" y1="62" x2="100" y2="40" /><line x1="100" y1="40" x2="138" y2="62" /><line x1="62" y1="62" x2="138" y2="62" />
          </g>
        </svg>
      </div>
      <div className="av-particles" aria-hidden="true">{[...Array(6)].map((_, i) => <i key={i} style={{ animationDelay: `${i * 0.3}s` }} />)}</div>
    </div>
  )
}

/** Equalizer bars: animate only while `active` (bound to real speech events by the caller). */
export function Waveform({ active, bars = 24 }: { active: boolean; bars?: number }) {
  return (
    <div className={cx('wave', active && 'wave-on')} aria-hidden="true">
      {Array.from({ length: bars }).map((_, i) => (
        <span key={i} style={{ animationDelay: `${(i % 8) * 0.09}s`, animationDuration: `${0.6 + ((i * 7) % 5) * 0.12}s` }} />
      ))}
    </div>
  )
}
