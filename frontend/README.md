# FairHire AI — Frontend

Premium light-theme React + Vite + TypeScript frontend for the FairHire AI FastAPI backend.
It is decision-support software for human recruiters; it never makes hiring decisions.

## Quick start (Windows / PowerShell)

```powershell
# 1) Backend (leave running in its own terminal) — this frontend does not modify it
cd "C:\Users\kaviy\FairHire-AI\FairHire-AI\backend"
.\venv\Scripts\python.exe -m uvicorn app.main:app --port 8000

# 2) Frontend (second terminal)
cd "C:\Users\kaviy\FairHire-AI\FairHire-AI\frontend"
# unzip this package into that folder first (back up anything already there)
node -v            # Node 18+ required
copy .env.example .env
npm install
npm run dev        # http://localhost:5173
npm run build      # type-check + production build into dist/
```

`VITE_API_BASE_URL` (in `.env`) defaults to `http://127.0.0.1:8000`.

## What is wired to the real backend

Contract taken from `backend/app/main.py` and the service files.

| Screen | Endpoint(s) | Notes |
|---|---|---|
| AI Recruiter | `POST /api/chat` | Always live. Shows the real `answer`, `candidate_ids`, `intent`. |
| Candidates (live mode) | `GET /api/candidate/{id}` | Lookup by ID only (see gaps). |
| Compare | `POST /api/compare` | Ranking, `ranking_score` and `score_explanation` exactly as returned. |
| Explainability | `GET /api/explain/shap/global`, `/structured`, `/shap/{id}`, `/lime/{id}` | Always live. |
| Resume Screening | `POST /api/upload/predict` (multipart) | Always live. PDF/DOCX only. |
| API status | `GET /api/health` | Shown in the top bar and Settings. |

## Demo data vs live data

Settings → **Data source**. Default is **Demo**: 12 invented candidates (IDs 101–112) so the UI works before
the backend is connected. Every demo screen shows a **Demo data** badge. Demo mode applies only to Overview,
Candidates and Compare. Chat, explainability and uploads never use mock data, and live mode never falls back to demo data.

## Known gaps (honest list)

1. **No candidate list endpoint.** The backend only has `GET /api/candidate/{id}`, so in live mode Candidates is a
   lookup-by-ID screen and Overview shows no KPIs (nothing is estimated). Smallest backend addition that would
   unlock browsing, filters and totals (**not applied**, proposal only):
   ```python
   # backend/app/main.py
   from app.services.candidate_service import CANDIDATES
   @app.get("/api/candidates")
   def list_candidates(limit: int = 50, offset: int = 0):
       return {"total": len(CANDIDATES), "items": CANDIDATES[offset:offset + limit]}
   ```
2. **Candidate JSON schema.** `candidate_intelligence_v2.json` wasn't in the bundle, so fields are typed as optional
   from how the services read them (`candidate_skills`, `matched_skills`, `experience.candidate_experience_years`, …).
   Missing fields display "Not available". If `required_experience_years` or other keys are named differently, adjust `src/types/api.ts`.
3. **SHAP/LIME CSV columns** (global, structured, per-candidate) weren't visible. The UI auto-detects a text
   label column and a numeric value column and falls back to a raw table, so nothing is invented.
4. **Upload progress** isn't reported by the backend; the scan animation is indeterminate. The 5 MB limit is a
   client-side guard (the backend sets none). `/api/upload/predict` returns raw `str(exc)` on 500s; the frontend
   deliberately shows a generic message for 5xx.
5. **3D approach.** The avatar and hero are layered SVG/CSS (perspective transforms), not WebGL, so there is no
   Three.js dependency and no empty-canvas failure mode.
6. **Speech animation** is bound to real `SpeechSynthesisUtterance` start/end/error events, but the equalizer bars
   and mouth motion are an approximation. Browsers don't expose audio amplitude or phonemes for TTS.
7. Styling uses plain CSS design tokens (`src/styles`) instead of Tailwind to avoid unverified build config.

## Browser voice support

- **Text-to-speech** (`speechSynthesis`): Chrome, Edge, Safari, Firefox. Voices vary by OS; pick one in Settings.
- **Voice input** (`SpeechRecognition`): Chrome and Edge (Chrome sends audio to Google's service). Hidden when
  unsupported. The microphone starts only when you click the mic button; the transcript is placed in the
  input box for review before sending.
- Autoplay of spoken answers is **off** by default.

## Structure

```
src/api/        client.ts (typed fetch, timeouts, errors) · mock.ts (demo only) · index.ts (mode switch)
src/components/ AppShell, Avatar/Waveform, Emoji, Visuals (rings, counters, tilt), States, Badges, charts
src/hooks/      useSpeech, useRecognition
src/lib/        settings store, motion variants, utils
src/pages/      Landing, Overview, Candidates, Compare, Recruiter, Explainability, Screening, Settings
src/styles/     tokens.css, global.css
```

## Deployment

`npm run build` outputs static files in `dist/`. Host on any static host, set `VITE_API_BASE_URL` at build time to
your deployed API, and restrict `allow_origins` in the backend CORS config (currently `*`) to your frontend origin.

## Status of this package

Written against your backend source. In the authoring environment `npm install`/`build` could not be run (no
network), so only a parse check was done. **Run `npm install && npm run build` first** and fix any type error it
reports; none of the runtime flows have been exercised in a browser yet.
