import { useCallback, useEffect, useRef, useState } from 'react'

const supported = typeof window !== 'undefined' && 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window

/** Text-to-speech. Speaking state is driven by real utterance events only. */
export function useSpeech(voiceURI: string) {
  const [speakingId, setSpeakingId] = useState<string | null>(null)
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([])
  const [error, setError] = useState<string | null>(null)
  const current = useRef<SpeechSynthesisUtterance | null>(null)

  useEffect(() => {
    if (!supported) return
    const load = () => setVoices(window.speechSynthesis.getVoices())
    load()
    window.speechSynthesis.addEventListener('voiceschanged', load)
    return () => window.speechSynthesis.removeEventListener('voiceschanged', load)
  }, [])

  const stop = useCallback(() => {
    if (!supported) return
    current.current = null // detach so the cancel-triggered error event is ignored
    window.speechSynthesis.cancel()
    setSpeakingId(null)
  }, [])

  const speak = useCallback((id: string, text: string) => {
    if (!supported) { setError('Speech synthesis is not supported in this browser.'); return }
    setError(null)
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text)
    const voice = window.speechSynthesis.getVoices().find((v) => v.voiceURI === voiceURI)
    if (voice) { u.voice = voice; u.lang = voice.lang }
    u.onstart = () => setSpeakingId(id)
    u.onend = () => { if (current.current === u) { current.current = null; setSpeakingId(null) } }
    u.onerror = () => {
      if (current.current === u) {
        current.current = null
        setSpeakingId(null)
        setError('Speech playback failed. Try another voice in Settings.')
      }
    }
    current.current = u
    window.speechSynthesis.speak(u)
  }, [voiceURI])

  // Cleanup on unmount (navigating away must silence the speaker).
  useEffect(() => () => { if (supported) window.speechSynthesis.cancel() }, [])

  return { supported, speakingId, voices, error, speak, stop }
}
