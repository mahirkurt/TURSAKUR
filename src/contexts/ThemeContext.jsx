import React, { createContext, useState, useLayoutEffect, useContext } from 'react'

const ThemeContext = createContext()

export const ThemeProvider = ({ children }) => {
  // 'light' veya 'dark' - localStorage'dan al veya default 'light'
  const [theme, setTheme] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('tursakur-theme') || 'light'
    }
    return 'light'
  })
  
  // Kontrast seviyesi: 'standard', 'medium', 'high'
  const [contrast, setContrast] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('tursakur-contrast') || 'standard'
    }
    return 'standard'
  })

  useLayoutEffect(() => {
    // <html> etiketine tema sınıfını uygula
    const html = document.documentElement
    
    // Önceki sınıfları temizle
    html.classList.remove('light', 'dark', 'light-mc', 'light-hc', 'dark-mc', 'dark-hc')
    
    // Tema sınıfını ekle
    html.classList.add(theme)
    
    // Kontrast sınıfını ekle (sadece medium ve high için)
    if (contrast !== 'standard') {
      const contrastClass = `${theme}-${contrast === 'medium' ? 'mc' : 'hc'}`
      html.classList.add(contrastClass)
    }
    
    // localStorage'a kaydet
    localStorage.setItem('tursakur-theme', theme)
    localStorage.setItem('tursakur-contrast', contrast)
  }, [theme, contrast])

  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'))
  }

  const setLightTheme = () => setTheme('light')
  const setDarkTheme = () => setTheme('dark')
  
  const setContrastLevel = (level) => {
    setContrast(level)
  }

  // Sistem tema tercihini algıla
  const useSystemTheme = () => {
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    setTheme(systemTheme)
  }

  // Hareket azaltma tercihini algıla
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  const value = {
    theme,
    contrast,
    toggleTheme,
    setLightTheme,
    setDarkTheme,
    setContrastLevel,
    useSystemTheme,
    prefersReducedMotion,
    isLight: theme === 'light',
    isDark: theme === 'dark'
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
