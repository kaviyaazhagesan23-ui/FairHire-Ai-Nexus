import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { BarChart3, Bot, FileUp, GitCompare, LayoutDashboard, Menu, PanelLeftClose, PanelLeftOpen, Search, Settings, Sparkles, Users, X } from 'lucide-react'
import { pageTransition } from '../lib/motion'
import { updateSettings, useSettings } from '../lib/settings'
import { ApiStatusPill, useApiHealth } from './ApiStatus'
import { DemoBadge } from './Badges'
import { cx } from '../lib/utils'

const nav = [
  { to: '/app', end: true, label: 'Overview', icon: LayoutDashboard, title: 'Overview' },
  { to: '/app/candidates', label: 'Candidates', icon: Users, title: 'Candidates' },
  { to: '/app/screening', label: 'Resume Screening', icon: FileUp, title: 'Resume Screening' },
  { to: '/app/compare', label: 'Compare Candidates', icon: GitCompare, title: 'Compare Candidates' },
  { to: '/app/recruiter', label: 'AI Recruiter', icon: Bot, title: 'AI Recruiter' },
  { to: '/app/explainability', label: 'Explainability', icon: BarChart3, title: 'Explainability' },
  { to: '/app/settings', label: 'Settings', icon: Settings, title: 'Settings' },
]

export function AppShell() {
  const { sidebarCollapsed, dataMode } = useSettings()
  const [open, setOpen] = useState(false)
  const loc = useLocation()
  const health = useApiHealth()
  const current = nav.find((n) => (n.end ? loc.pathname === n.to : loc.pathname.startsWith(n.to)))

  useEffect(() => { setOpen(false) }, [loc.pathname])

  return (
    <div className="shell">
      <div className={cx('scrim', open && 'show')} onClick={() => setOpen(false)} aria-hidden="true" />
      <aside className={cx('sidebar', sidebarCollapsed && 'collapsed', open && 'open')} aria-label="Primary">
        <Link to="/" className="brand" aria-label="FairHire AI home">
          <span className="brand-mark"><Sparkles size={20} aria-hidden="true" /></span>
          <span className="label">FairHire <b>AI</b></span>
        </Link>
        <nav className="stack" style={{ gap: 4 }}>
          {nav.map(({ to, end, label, icon: Icon }) => (
            <NavLink key={to} to={to} end={end} className={({ isActive }) => cx('nav-link', isActive && 'active')} title={label}>
              <Icon size={19} aria-hidden="true" /><span className="label">{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-foot">
          <button className="btn btn-ghost btn-sm desktop-only" onClick={() => updateSettings({ sidebarCollapsed: !sidebarCollapsed })} aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
            {sidebarCollapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}<span className="label">Collapse</span>
          </button>
        </div>
      </aside>

      <div className="main">
        <div className="bg-orbs" aria-hidden="true"><div className="orb a" /><div className="orb b" /><div className="orb c" /></div>
        <header className="topbar">
          <button className="btn btn-ghost btn-icon mobile-only" onClick={() => setOpen((o) => !o)} aria-label={open ? 'Close menu' : 'Open menu'}>
            {open ? <X size={18} /> : <Menu size={18} />}
          </button>
          <div style={{ minWidth: 0 }}>
            <div className="crumbs"><Link to="/" style={{ color: 'inherit' }}>FairHire</Link> / {current?.title ?? 'Page'}</div>
            <strong style={{ fontSize: '1.05rem' }}>{current?.title ?? 'FairHire AI'}</strong>
          </div>
          <div style={{ flex: 1 }} />
          {dataMode === 'demo' && <DemoBadge />}
          <ApiStatusPill state={health.state} onRefresh={health.check} />
          <Link to="/app/candidates" className="btn btn-ghost btn-icon desktop-only" aria-label="Search candidates"><Search size={16} /></Link>
        </header>
        <AnimatePresence mode="wait">
          <motion.main key={loc.pathname} className="page" {...pageTransition}>
            <Outlet context={health} />
          </motion.main>
        </AnimatePresence>
      </div>
    </div>
  )
}
