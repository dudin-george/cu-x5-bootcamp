import { useState, useEffect } from 'react'
import './App.css'

interface VersionInfo {
  version: string
  environment: string
}

function App() {
  const [versionInfo, setVersionInfo] = useState<VersionInfo | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/version')
      .then(res => res.json())
      .then(data => {
        setVersionInfo(data)
        setLoading(false)
      })
      .catch(() => {
        setVersionInfo({ version: 'unknown', environment: 'unknown' })
        setLoading(false)
      })
  }, [])

  return (
    <div className="app">
      <div className="grid-background"></div>
      
      <header className="header">
        <div className="logo">
          <span className="logo-x5">X5</span>
          <span className="logo-divider">/</span>
          <span className="logo-hiring">HIRING</span>
        </div>
        <div className="env-badge">
          {loading ? '...' : versionInfo?.environment.toUpperCase()}
        </div>
      </header>

      <main className="main">
        <div className="hero">
          <h1 className="title">
            <span className="title-line">Recruiter</span>
            <span className="title-line accent">Dashboard</span>
          </h1>
          <p className="subtitle">
            Платформа для управления наймом
          </p>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📋</div>
            <div className="stat-value">0</div>
            <div className="stat-label">Активных вакансий</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">👥</div>
            <div className="stat-value">0</div>
            <div className="stat-label">Кандидатов</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">💬</div>
            <div className="stat-value">0</div>
            <div className="stat-label">Интервью сегодня</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-value">0</div>
            <div className="stat-label">Офферов</div>
          </div>
        </div>

        <div className="status-section">
          <h2 className="section-title">Статус системы</h2>
          <div className="status-grid">
            <div className="status-item online">
              <span className="status-dot"></span>
              <span className="status-name">Core API</span>
            </div>
            <div className="status-item online">
              <span className="status-dot"></span>
              <span className="status-name">Candidate Bot</span>
            </div>
            <div className="status-item online">
              <span className="status-dot"></span>
              <span className="status-name">HM Bot</span>
            </div>
            <div className="status-item online">
              <span className="status-dot"></span>
              <span className="status-name">Worker</span>
            </div>
          </div>
        </div>
      </main>

      <footer className="footer">
        <div className="footer-content">
          <span>X5 Hiring Bootcamp</span>
          <span className="footer-divider">•</span>
          <span>v{loading ? '...' : versionInfo?.version}</span>
        </div>
      </footer>
    </div>
  )
}

export default App

