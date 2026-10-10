import { useCallback, useEffect, useRef, useState } from 'react'

interface RecognitionResultLike { 0: { transcript: string }; isFinal: boolean }
interface RecognitionEventLike { results: ArrayLike<RecognitionResultLike> }
interface RecognitionLike {
  lang: string
  interimResults: boolean
  continuous: boolean
  onresult: ((e: RecognitionEventLike) => void) | null
  onerror: ((e: { error: string }) => void) | null
  onend: (() => void) | null
  start(): void
  stop(): void
  abort(): void
}
type RecognitionCtor = new () => RecognitionLike

const Ctor: RecognitionCtor | undefined =
  typeof window !== 'undefined'
    ? ((window as unknown as { SpeechRecognition?: RecognitionCtor; webkitSpeechRecognition?: RecognitionCtor }).SpeechRecognition ??
       (window as unknown as { webkitSpeechRecognition?: RecognitionCtor }).webkitSpeechRecognition)
    : undefined

const friendly: Record<string, string> = {
  'not-allowed': 'Microphone permission was denied. Allow it in your browser, or keep typing.',
  'service-not-allowed': 'Speech recognition is blocked in this browser context.',
  'no-speech': 'No speech was detected. Try again.',
  'audio-capture': 'No microphone was found.',
  network: 'Speech recognition needs a network connection in this browser.',
}

/** Voice input. The microphone starts ONLY from an explicit start() call. */
export function useRecognition(onTranscript: (text: string) => void) {
  const [listening, setListening] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const ref = useRef<RecognitionLike | null>(null)
  const cb = useRef(onTranscript)
  cb.current = onTranscript

  const stop = useCallback(() => { ref.current?.stop() }, [])

  const start = useCallback(() => {
    if (!Ctor) return
    setError(null)
    const r = new Ctor()
    r.lang = navigator.language || 'en-US'
    r.interimResults = true
    r.continuous = false
    r.onresult = (e) => {
      let text = ''
      for (let i = 0; i < e.results.length; i++) text += e.results[i][0].transcript
      cb.current(text)
    }
    r.onerror = (e) => { if (e.error !== 'aborted') setError(friendly[e.error] ?? 'Speech recognition failed.') }
    r.onend = () => { setListening(false); ref.current = null }
    ref.current = r
    try { r.start(); setListening(true) } catch { setError('Could not start the microphone.'); ref.current = null }
  }, [])

  useEffect(() => () => { ref.current?.abort(); ref.current = null }, [])

  return { supported: Boolean(Ctor), listening, error, start, stop }
}
