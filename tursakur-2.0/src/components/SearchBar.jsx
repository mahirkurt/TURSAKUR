import React, { useState, useRef, useEffect } from 'react'
import './SearchBar.css'

function SearchBar({ value, onChange, placeholder = "Arama yapın...", className = "" }) {
  const [isFocused, setIsFocused] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [selectedSuggestion, setSelectedSuggestion] = useState(-1)
  const inputRef = useRef(null)
  const suggestionsRef = useRef(null)

  // Debounced suggestions (mock data for now)
  useEffect(() => {
    if (value.length > 2) {
      // Mock suggestions - gerçek uygulamada Supabase'den gelecek
      const mockSuggestions = [
        { type: 'hospital', text: `${value} Hastanesi`, count: 5 },
        { type: 'province', text: value, count: 23 },
        { type: 'district', text: `${value} ilçesi`, count: 8 },
      ].filter(s => s.text.toLowerCase().includes(value.toLowerCase()))
      
      setSuggestions(mockSuggestions)
    } else {
      setSuggestions([])
    }
  }, [value])

  const handleInputChange = (e) => {
    onChange(e.target.value)
    setSelectedSuggestion(-1)
  }

  const handleKeyDown = (e) => {
    if (suggestions.length === 0) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedSuggestion(prev => 
          prev < suggestions.length - 1 ? prev + 1 : 0
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedSuggestion(prev => 
          prev > 0 ? prev - 1 : suggestions.length - 1
        )
        break
      case 'Enter':
        e.preventDefault()
        if (selectedSuggestion >= 0) {
          onChange(suggestions[selectedSuggestion].text)
          setSuggestions([])
          setSelectedSuggestion(-1)
        }
        break
      case 'Escape':
        setSuggestions([])
        setSelectedSuggestion(-1)
        inputRef.current?.blur()
        break
    }
  }

  const handleSuggestionClick = (suggestion) => {
    onChange(suggestion.text)
    setSuggestions([])
    setSelectedSuggestion(-1)
    inputRef.current?.focus()
  }

  const clearSearch = () => {
    onChange('')
    setSuggestions([])
    setSelectedSuggestion(-1)
    inputRef.current?.focus()
  }

  return (
    <div className={`search-bar ${className} ${isFocused ? 'focused' : ''}`}>
      <div className="search-input-container">
        <div className="search-icon">🔍</div>
        
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => {
            // Suggestions'a tıklama için kısa bir gecikme
            setTimeout(() => {
              setIsFocused(false)
              setSuggestions([])
              setSelectedSuggestion(-1)
            }, 200)
          }}
          placeholder={placeholder}
          className="search-input body-large"
          aria-label="Sağlık kuruluşu arama"
          aria-autocomplete="list"
          aria-expanded={suggestions.length > 0}
          role="combobox"
        />

        {value && (
          <button
            onClick={clearSearch}
            className="clear-button"
            title="Aramayı temizle"
            aria-label="Aramayı temizle"
          >
            ✕
          </button>
        )}
      </div>

      {/* Suggestions Dropdown */}
      {suggestions.length > 0 && isFocused && (
        <div 
          ref={suggestionsRef}
          className="suggestions-dropdown"
          role="listbox"
        >
          {suggestions.map((suggestion, index) => (
            <button
              key={`${suggestion.type}-${index}`}
              onClick={() => handleSuggestionClick(suggestion)}
              className={`suggestion-item ${index === selectedSuggestion ? 'selected' : ''}`}
              role="option"
              aria-selected={index === selectedSuggestion}
            >
              <div className="suggestion-content">
                <span className="suggestion-text body-medium">
                  {suggestion.text}
                </span>
                <span className="suggestion-count label-small">
                  {suggestion.count} sonuç
                </span>
              </div>
              <div className="suggestion-type label-small">
                {suggestion.type === 'hospital' && '🏥'}
                {suggestion.type === 'province' && '📍'}
                {suggestion.type === 'district' && '🗺️'}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default SearchBar
