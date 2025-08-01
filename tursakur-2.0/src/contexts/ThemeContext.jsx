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

  useLayoutEffect(() => {
    // <html> etiketine tema sınıfını uygula
    const html = document.documentElement
    
    // Önceki tema sınıflarını temizle
    html.classList.remove('light', 'dark')
    
    // Yeni tema sınıfını ekle
    html.classList.add(theme)
    
    // localStorage'a kaydet
    localStorage.setItem('tursakur-theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'))
  }

  const setLightTheme = () => setTheme('light')
  const setDarkTheme = () => setTheme('dark')

  const value = {
    theme,
    toggleTheme,
    setLightTheme,
    setDarkTheme,
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
