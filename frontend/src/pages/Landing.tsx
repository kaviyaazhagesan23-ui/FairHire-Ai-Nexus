import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { ArrowRight, BarChart3, FileSearch, GitCompare, Sparkles, Brain } from 'lucide-react'
import { Emoji } from '../components/Emoji'
import { Sparkles as Sparks } from '../components/Visuals'
import { fadeUp, stagger } from '../lib/motion'

const features = [
  { icon: FileSearch, emoji: '📄', title: 'AI resume screening', text: 'Upload a PDF or DOCX resume and get a Strong/Weak Match prediction from the FairHire SVM pipeline.' },
  { icon: Brain, emoji: '🧠', title: 'Candidate intelligence', text: 'Skills, matched and missing requirements, experience and role compatibility in one clear profile.' },
  { icon: BarChart3, emoji: '📊', title: 'Explainable AI', text: 'SHAP and LIME views show which features pushed the model toward each prediction.' },
  { icon: GitCompare, emoji: '🏆', title: 'Candidate comparison', text: 'Side-by-side comparison with a transparent, weighted heuristic ranking score.' },
]

export default function Landing() {
  return (
    <div className="landing">
      <div className="bg-orbs" aria-hidden="true"><div className="orb a" /><div className="orb b" /><div className="orb c" /></div>
      <header className="l-nav">
        <div className="brand" style={{ padding: 0 }}>
          <span className="brand-mark"><Sparkles size={20} aria-hidden="true" /></span>
          <span>FairHire <b>AI</b></span>
        </div>
        <div className="row">
          <a className="btn btn-ghost btn-sm" href="#features">Capabilities</a>
          <Link className="btn btn-primary btn-sm" to="/app">Open dashboard</Link>
        </div>
      </header>

      <section className="hero">
        <motion.div variants={stagger} initial="hidden" animate="show">
          <motion.div variants={fadeUp} className="eyebrow"><Emoji symbol="✨" anim="sparkle" size={16} /> Explainable decision support for recruiters</motion.div>
          <motion.h1 variants={fadeUp}>Hire with <span className="grad-text">clarity</span>, not guesswork.</motion.h1>
          <motion.p variants={fadeUp} className="lead">
            FairHire AI screens resumes, surfaces candidate intelligence and explains every prediction, so human recruiters stay in control of the decision.
          </motion.p>
          <motion.div variants={fadeUp} className="row wrap">
            <Link className="btn btn-primary" to="/app">Open dashboard <ArrowRight size={16} /></Link>
            <a className="btn btn-ghost" href="#features">Explore capabilities</a>
            <Link className="btn btn-ghost" to="/app/recruiter"><Emoji symbol="🎙️" anim="pulse" size={16} /> Meet the AI recruiter</Link>
          </motion.div>
        </motion.div>

        <div className="stage" aria-label="Illustrative product preview (not real data)" role="img">
          <div className="plane">
            <div className="float-card f1">
              <div className="row spread"><strong>🎯 Role match</strong><span className="badge badge-success">Strong Match</span></div>
              <div className="metric" style={{ marginTop: 14 }}><div className="metric-head"><span>Skill coverage</span><span>7 / 7</span></div><div className="bar"><div className="bar-fill" style={{ width: '100%' }} /></div></div>
              <div className="metric"><div className="metric-head"><span>Experience fit</span><span>✓</span></div><div className="bar"><div className="bar-fill" style={{ width: '78%' }} /></div></div>
            </div>
            <div className="float-card f2">
              <strong>🏆 Ranking</strong>
              <div className="row" style={{ marginTop: 10 }}><span className="rank-badge rank-1">1</span><div><div style={{ fontWeight: 700 }}>Candidate A</div><div className="muted small">heuristic score</div></div></div>
              <div className="row" style={{ marginTop: 8 }}><span className="rank-badge">2</span><div><div style={{ fontWeight: 700 }}>Candidate B</div><div className="muted small">heuristic score</div></div></div>
            </div>
            <div className="float-card f3"><strong>💡 Why this prediction?</strong><p className="muted small" style={{ marginTop: 6 }}>SHAP highlights the top contributing features.</p></div>
            <span className="tag-float" style={{ top: 6, right: '8%' }}>Python</span>
            <span className="tag-float" style={{ top: 150, left: '-2%', animationDelay: '-1.5s' }}>Kubernetes</span>
            <span className="tag-float" style={{ bottom: 70, right: '4%', animationDelay: '-3s' }}>CI/CD</span>
          </div>
          <Emoji symbol="🤖" anim="float" size={54} className="" />
          <Sparks />
        </div>
      </section>

      <section id="features" className="section">
        <motion.h2 initial={{ opacity: 0, y: 14 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>Everything a recruiter needs, <span className="grad-text">explained</span></motion.h2>
        <p className="sub">Four capabilities built on the FairHire backend.</p>
        <motion.div className="grid g-4" variants={stagger} initial="hidden" whileInView="show" viewport={{ once: true, margin: '-60px' }}>
          {features.map(({ icon: Icon, emoji, title, text }) => (
            <motion.div key={title} variants={fadeUp} className="card hover">
              <div className="feature-icon"><Icon size={26} color="#4F46E5" aria-hidden="true" /></div>
              <h3 className="row" style={{ gap: 8 }}>{title} <Emoji symbol={emoji} anim="bounce" size={20} /></h3>
              <p className="muted" style={{ marginTop: 8 }}>{text}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      
    </div>
  )
}
