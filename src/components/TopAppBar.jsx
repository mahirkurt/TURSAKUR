import React from 'react'
import { useTheme } from '../contexts/ThemeContext'
import './TopAppBar.css'

function TopAppBar() {
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="top-app-bar">
      <div className="top-app-bar-content">
        {/* Logo */}
        <div className="top-app-bar-title-section">
          <img 
            src="/assets/logos/TURSAKUR-Color.png" 
            alt="TURSAKUR" 
            className="app-logo"
          />
        </div>

        {/* Navigasyon Linkleri */}
        <nav className="top-app-bar-navigation">
          <a href="/" className="nav-link">Ana Sayfa</a>
          <a href="/harita" className="nav-link">Harita</a>
          <a href="/hakkinda" className="nav-link">Hakkında</a>
        </nav>

        {/* Eylem Butonları */}
        <div className="top-app-bar-actions">
          {/* Tema Değiştirme Butonu */}
          <button 
            onClick={toggleTheme}
            className="icon-button theme-toggle"
            title={theme === 'light' ? 'Koyu temaya geç' : 'Açık temaya geç'}
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>

          {/* Menü Butonu (Mobil için) */}
          <button className="icon-button menu-button">
            ☰
          </button>
        </div>
      </div>
    </header>
  )
}

export default TopAppBar
