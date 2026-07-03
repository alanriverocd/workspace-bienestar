import React from 'react'
import Dashboard from './components/Dashboard'
import './styles.css'

export default function App(){
  return (
    <div className="app-root">
      <header className="topbar">
        <div className="brand">
          <div className="brand-logo" aria-hidden="true">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="48" height="48" rx="8" fill="#0b66ff" />
              <path d="M12 30C14.5 26 20 20 28 18" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
              <circle cx="32" cy="14" r="3" fill="white" />
            </svg>
          </div>
          <div>
            <h1 className="title">Control de Fallas</h1>
            <p className="subtitle">Plataforma de supervisión y sincronización</p>
          </div>
        </div>
      </header>

      <main className="container">
        <Dashboard />
      </main>

      <footer className="footer">© {new Date().getFullYear()} Alan Rivero — Workspace Bienestar</footer>
    </div>
  )
}
