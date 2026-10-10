import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import Landing from './pages/Landing'
import Overview from './pages/Overview'
import Candidates from './pages/Candidates'
import Screening from './pages/Screening'
import Compare from './pages/Compare'
import Recruiter from './pages/Recruiter'
import Explainability from './pages/Explainability'
import SettingsPage from './pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/app" element={<AppShell />}>
        <Route index element={<Overview />} />
        <Route path="candidates" element={<Candidates />} />
        <Route path="screening" element={<Screening />} />
        <Route path="compare" element={<Compare />} />
        <Route path="recruiter" element={<Recruiter />} />
        <Route path="explainability" element={<Explainability />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
