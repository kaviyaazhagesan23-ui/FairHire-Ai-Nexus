import { useSyncExternalStore } from 'react'

export type DataMode = 'demo' | 'live'

export interface Settings {
  dataMode: DataMode
  autoplay: boolean
  muted: boolean
  voiceURI: string
  sidebarCollapsed: boolean
}

const KEY = 'fairhire.prefs.v1'
const defaults: Settings = {
  dataMode: 'demo',
  autoplay: false, // spec: autoplay is off by default
  muted: false,
  voiceURI: '',
  sidebarCollapsed: false,
}

function load(): Settings {
  try {
    const raw = localStorage.getItem(KEY)
    if (raw) return { ...defaults, ...JSON.parse(raw) }
  } catch { /* storage unavailable: use defaults */ }
  return defaults
}

let state: Settings = load()
const listeners = new Set<() => void>()

export function getSettings(): Settings { return state }

export function updateSettings(patch: Partial<Settings>) {
  state = { ...state, ...patch }
  try { localStorage.setItem(KEY, JSON.stringify(state)) } catch { /* ignore */ }
  listeners.forEach((l) => l())
}

export function resetSettings() {
  try { localStorage.removeItem(KEY) } catch { /* ignore */ }
  state = defaults
  listeners.forEach((l) => l())
}

function subscribe(cb: () => void) {
  listeners.add(cb)
  return () => { listeners.delete(cb) }
}

export function useSettings(): Settings {
  return useSyncExternalStore(subscribe, getSettings, getSettings)
}
