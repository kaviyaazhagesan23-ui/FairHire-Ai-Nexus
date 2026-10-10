import { useCallback, useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Mic, MicOff, RotateCw, Send, Square, Trash2, Volume2, VolumeX } from 'lucide-react'
import { api, errorMessage } from '../api'
import { updateSettings, useSettings } from '../lib/settings'
import { useSpeech } from '../hooks/useSpeech'
import { useRecognition } from '../hooks/useRecognition'
import { Avatar, Waveform, stateLabel, type AiState } from '../components/Avatar'
import { Emoji } from '../components/Emoji'
import { Sparkles } from '../components/Visuals'
import { ModelNotice } from '../components/Badges'
import { cx } from '../lib/utils'

interface Msg { id: string; role: 'user' | 'ai'; text: string; ids?: string[]; intent?: string; error?: boolean; retry?: string }

const prompts = [
  { emoji: '🔍', text: 'Show Candidate 1562.' },
  { emoji: '🎯', text: 'What skills is Candidate 1728 missing?' },
  { emoji: '💡', text: 'What are the strengths of Candidate 1728?' },
  { emoji: '🏆', text: 'Compare Candidate 1562 with Candidate 1728.' },
]
const MAX = 1000 // backend limit for /api/chat
let seq = 0
const uid = () => `m${++seq}`

export default function Recruiter() {
  const { autoplay, muted, voiceURI } = useSettings()
  const speech = useSpeech(voiceURI)
  const [msgs, setMsgs] = useState<Msg[]>([])
  const [input, setInput] = useState('')
  const [pending, setPending] = useState(false)
  const [flash, setFlash] = useState(false)
  const [failed, setFailed] = useState(false)
  const logRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const rec = useRecognition((t) => setInput(t.slice(0, MAX))) // transcript lands in the input for review/edit

  // State is derived from real events: request in flight, mic active, utterance playing.
  const state: AiState = failed || rec.error ? 'error'
    : rec.listening ? 'listening'
    : pending ? 'thinking'
    : speech.speakingId ? 'speaking'
    : flash ? 'success'
    : muted ? 'muted' : 'idle'

  useEffect(() => { logRef.current?.scrollTo({ top: logRef.current.scrollHeight }) }, [msgs, pending])

  const flashSuccess = useCallback(() => { setFlash(true); window.setTimeout(() => setFlash(false), 1400) }, [])

  const send = useCallback(async (raw: string) => {
    const text = raw.trim()
    if (!text || pending) return
    if (text.length > MAX) { setMsgs((m) => [...m, { id: uid(), role: 'ai', text: `Messages are limited to ${MAX} characters.`, error: true }]); return }
    speech.stop()
    setFailed(false)
    setMsgs((m) => [...m, { id: uid(), role: 'user', text }])
    setInput('')
    setPending(true)
    try {
      const r = await api.chat(text)
      const id = uid()
      setMsgs((m) => [...m, { id, role: 'ai', text: r.answer, ids: r.candidate_ids, intent: r.intent }])
      flashSuccess()
      if (autoplay && !muted) speech.speak(id, r.answer)
    } catch (e) {
      setFailed(true)
      setMsgs((m) => [...m, { id: uid(), role: 'ai', text: errorMessage(e), error: true, retry: text }])
    } finally {
      setPending(false)
    }
  }, [pending, speech, autoplay, muted, flashSuccess])

  const clear = () => { speech.stop(); rec.stop(); setMsgs([]); setInput(''); setFailed(false) }

  return (
    <div className="stack">
      <div className="page-head">
        <h1>AI Recruiter <Emoji symbol="🤖" anim="float" size={28} /></h1>
        <p className="muted">Ask about candidates. Answers come from the FairHire AI; your browser can read them aloud.</p>
      </div>

      <div className="recruiter">
        <section className="card stage-card" aria-label="AI recruiter avatar" data-s={state}>
          <Sparkles />
          <Avatar state={state} size={260} />
          <div className="status-pill" role="status" aria-live="polite"><span className="status-dot" />{stateLabel[state]}</div>
          <Waveform active={state === 'speaking'} />
          <p className="muted small" style={{ minHeight: 34 }}>
            {state === 'speaking' && 'Speech animation follows playback events (approximate, not phoneme-accurate).'}
            {state === 'listening' && 'Speak now. The transcript appears in the box for you to review.'}
            {state === 'thinking' && 'Waiting for the backend…'}
            {state === 'error' && (rec.error ?? 'The last request failed. You can retry.')}
          </p>
          <div className="row wrap" style={{ justifyContent: 'center', marginTop: 8 }}>
            <button className="btn btn-ghost btn-sm" onClick={() => { updateSettings({ muted: !muted }); if (!muted) speech.stop() }} aria-pressed={muted}>
              {muted ? <VolumeX size={14} /> : <Volume2 size={14} />} {muted ? 'Unmute' : 'Mute'}
            </button>
            <label className="row small" style={{ gap: 6, cursor: 'pointer' }}>
              <input type="checkbox" checked={autoplay} onChange={(e) => updateSettings({ autoplay: e.target.checked })} /> Auto-read answers
            </label>
          </div>
          {!speech.supported && <p className="small muted" style={{ marginTop: 8 }}>Speech output isn't supported in this browser. Text chat still works.</p>}
          {speech.error && <p className="small" style={{ color: 'var(--error)' }} role="alert">{speech.error}</p>}
        </section>

        <section className="card chat" aria-label="Conversation">
          <div className="chat-log" ref={logRef} aria-live="polite">
            {msgs.length === 0 && (
              <div className="stack">
                <div className="msg msg-ai">Hi! I'm your FairHire recruiter assistant <Emoji symbol="✨" anim="sparkle" size={16} />. I can summarise a candidate, list missing skills or strengths, and compare candidates. Pick a prompt or type your own.</div>
                <div className="grid g-2">
                  {prompts.map((p) => (
                    <button key={p.text} className="prompt-card" onClick={() => void send(p.text)} disabled={pending}>
                      <Emoji symbol={p.emoji} anim="bounce" size={22} /> <span>{p.text}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
            <AnimatePresence initial={false}>
              {msgs.map((m) => (
                <motion.div key={m.id} className={cx('msg', m.role === 'user' ? 'msg-user' : 'msg-ai', m.error && 'msg-err')}
                  initial={{ opacity: 0, y: 10, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }}>
                  {m.text}
                  {m.role === 'ai' && (
                    <div className="msg-tools">
                      {m.ids && m.ids.map((id) => <Link key={id} className="chip chip-link" to={`/app/candidates?id=${id}`}>Candidate {id}</Link>)}
                      {!m.error && speech.supported && (speech.speakingId === m.id
                        ? <button className="btn btn-sm btn-ghost" onClick={speech.stop} aria-label="Stop speaking"><Square size={13} /> Stop</button>
                        : <button className="btn btn-sm btn-ghost" disabled={muted} onClick={() => speech.speak(m.id, m.text)} aria-label="Read this answer aloud"><Volume2 size={13} /> Listen</button>)}
                      {m.retry && <button className="btn btn-sm btn-ghost" onClick={() => void send(m.retry!)}><RotateCw size={13} /> Retry</button>}
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
            {pending && <div className="msg msg-ai" aria-label="Assistant is thinking"><span className="typing"><i /><i /><i /></span></div>}
          </div>

          <form className="composer" onSubmit={(e) => { e.preventDefault(); void send(input) }}>
            <label className="sr-only" htmlFor="chat-input">Message the AI recruiter</label>
            <textarea id="chat-input" ref={inputRef} className="input" rows={1} value={input} maxLength={MAX} placeholder={rec.listening ? 'Listening…' : 'Ask about a candidate…'}
              onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); void send(input) } }} />
            {rec.supported && (
              <button type="button" className={cx('btn btn-ghost btn-icon', rec.listening && 'mic-on')} onClick={rec.listening ? rec.stop : rec.start}
                aria-pressed={rec.listening} aria-label={rec.listening ? 'Stop listening' : 'Start voice input'} title="Voice input (asks for microphone permission)">
                {rec.listening ? <MicOff size={18} /> : <Mic size={18} />}
              </button>
            )}
            <button className="btn btn-primary" disabled={!input.trim() || pending} aria-label="Send message"><Send size={16} /> <span className="desktop-only">Send</span></button>
            <button type="button" className="btn btn-ghost btn-icon" onClick={clear} aria-label="Clear conversation" title="Clear conversation"><Trash2 size={16} /></button>
          </form>
          {!rec.supported && <p className="small muted" style={{ padding: '0 14px 12px' }}>Voice input isn't supported in this browser (try Chrome or Edge). Typing works normally.</p>}
        </section>
      </div>
      <ModelNotice />
    </div>
  )
}
