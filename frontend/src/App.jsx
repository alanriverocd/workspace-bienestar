import React from 'react'
import Dashboard from './components/Dashboard'
import './styles.css'

export default function App(){
  return (
    <div className="app-root">
      <header className="topbar">
        <div className="brand">
          <img src="/assets/logo192.png" alt="logo" className="brand-logo" onError={(e)=> e.target.style.display='none'} />
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
