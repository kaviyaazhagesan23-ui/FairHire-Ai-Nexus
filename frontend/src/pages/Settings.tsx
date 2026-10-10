import { API_BASE_URL } from '../api'
import { resetSettings, updateSettings, useSettings } from '../lib/settings'
import { useSpeech } from '../hooks/useSpeech'
import { ApiStatusPill, useApiHealth } from '../components/ApiStatus'
import { Emoji } from '../components/Emoji'

export default function SettingsPage() {
  const s = useSettings()
  const speech = useSpeech(s.voiceURI)
  const health = useApiHealth()
  const reduced = typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches

  return (
    <div className="stack" style={{ maxWidth: 760 }}>
      <div className="page-head"><h1>Settings <Emoji symbol="⚙️" anim="wiggle" size={26} /></h1></div>

      <div className="card stack">
        <div className="card-title">🔌 Data source</div>
        <label className="field">Candidate data for Overview, Candidates and Compare
          <select className="select" value={s.dataMode} onChange={(e) => updateSettings({ dataMode: e.target.value as 'demo' | 'live' })}>
            <option value="demo">Demo data (labeled sample records)</option>
            <option value="live">Live backend (real records)</option>
          </select>
        </label>
        <p className="muted small">Chat, explainability and resume screening always use the live backend.</p>
        <div className="row wrap"><span className="mono small">{API_BASE_URL}</span><ApiStatusPill state={health.state} onRefresh={health.check} />{health.model && <span className="small muted">Model: {health.model}</span>}</div>
        <p className="muted small">Change the URL via <code>VITE_API_BASE_URL</code> in <code>.env</code>, then restart the dev server.</p>
      </div>

      <div className="card stack">
        <div className="card-title">🎙️ Voice</div>
        <label className="row"><input type="checkbox" checked={s.muted} onChange={(e) => updateSettings({ muted: e.target.checked })} /> Mute spoken answers (text only)</label>
        <label className="row"><input type="checkbox" checked={s.autoplay} onChange={(e) => updateSettings({ autoplay: e.target.checked })} /> Read answers aloud automatically (off by default)</label>
        {speech.supported ? (
          <label className="field">Voice
            <select className="select" value={s.voiceURI} onChange={(e) => updateSettings({ voiceURI: e.target.value })}>
              <option value="">Browser default</option>
              {speech.voices.map((v) => <option key={v.voiceURI} value={v.voiceURI}>{v.name} ({v.lang})</option>)}
            </select>
          </label>
        ) : <p className="muted small">Speech synthesis isn't supported in this browser.</p>}
      </div>

      <div className="card stack">
        <div className="card-title">✨ Motion & storage</div>
        <p className="small">Reduced motion is {reduced ? <strong>on</strong> : 'off'} in your operating system. FairHire follows that setting automatically.</p>
        <p className="small muted">Only the preferences on this page are stored in your browser. Conversations are never stored.</p>
        <button className="btn btn-danger" style={{ alignSelf: 'flex-start' }} onClick={resetSettings}>Reset preferences</button>
      </div>

      <div className="card small muted">FairHire AI frontend v2.0.0 · decision support for human recruiters.</div>
    </div>
  )
}
