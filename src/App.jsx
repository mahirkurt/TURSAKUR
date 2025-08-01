import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import HomePage from './pages/HomePage'
import InstitutionDetail from './pages/InstitutionDetail'
import MapPage from './pages/MapPage'
import AboutPage from './pages/AboutPage'
import './App.css'

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="app">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/kurum/:id" element={<InstitutionDetail />} />
            <Route path="/harita" element={<MapPage />} />
            <Route path="/hakkinda" element={<AboutPage />} />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  )
}

export default App
