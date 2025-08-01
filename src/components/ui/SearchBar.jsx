import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import TextField from './TextField';

/**
 * Material Design 3 Search Bar Component
 * Gelişmiş arama özelikleri ile
 */
const SearchBar = ({
  value,
  onChange,
  onSearch,
  onSuggestionSelect,
  suggestions = [],
  placeholder = "Hastane, şehir veya sağlık kuruluşu ara...",
  loading = false,
  className = '',
  ...props
}) => {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
  const searchRef = useRef(null);
  const suggestionsRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSuggestions(false);
        setSelectedSuggestionIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleInputChange = (e) => {
    const newValue = e.target.value;
    onChange(newValue);
    setShowSuggestions(newValue.length > 0 && suggestions.length > 0);
    setSelectedSuggestionIndex(-1);
  };

  const handleInputFocus = () => {
    if (value.length > 0 && suggestions.length > 0) {
      setShowSuggestions(true);
    }
  };

  const handleKeyDown = (e) => {
    if (!showSuggestions) {
      if (e.key === 'Enter') {
        handleSearch();
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedSuggestionIndex >= 0) {
          handleSuggestionClick(suggestions[selectedSuggestionIndex]);
        } else {
          handleSearch();
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedSuggestionIndex(-1);
        break;
      default:
        break;
    }
  };

  const handleSearch = () => {
    if (onSearch) {
      onSearch(value);
    }
    setShowSuggestions(false);
    setSelectedSuggestionIndex(-1);
  };

  const handleSuggestionClick = (suggestion) => {
    if (onSuggestionSelect) {
      onSuggestionSelect(suggestion);
    }
    setShowSuggestions(false);
    setSelectedSuggestionIndex(-1);
  };

  const handleClear = () => {
    onChange('');
    setShowSuggestions(false);
    setSelectedSuggestionIndex(-1);
    if (searchRef.current) {
      const input = searchRef.current.querySelector('input');
      if (input) {
        input.focus();
      }
    }
  };

  const getTrailingIcon = () => {
    if (loading) {
      return 'progress_activity'; // Loading spinner icon
    }
    if (value.length > 0) {
      return 'clear';
    }
    return 'search';
  };

  const handleTrailingIconClick = () => {
    if (loading) return;
    
    if (value.length > 0) {
      handleClear();
    } else {
      handleSearch();
    }
  };

  return (
    <div ref={searchRef} className={`md-search-field ${className}`}>
      <TextField
        variant="filled"
        placeholder={placeholder}
        value={value}
        onChange={handleInputChange}
        onFocus={handleInputFocus}
        onKeyDown={handleKeyDown}
        leadingIcon="search"
        trailingIcon={getTrailingIcon()}
        onTrailingIconClick={handleTrailingIconClick}
        className="md-search-field__input"
        {...props}
      />
      
      {showSuggestions && suggestions.length > 0 && (
        <div ref={suggestionsRef} className="md-search-suggestions">
          {suggestions.map((suggestion, index) => (
            <div
              key={suggestion.id || index}
              className={`md-search-suggestion ${
                index === selectedSuggestionIndex ? 'md-search-suggestion--selected' : ''
              }`}
              onClick={() => handleSuggestionClick(suggestion)}
              onMouseEnter={() => setSelectedSuggestionIndex(index)}
            >
              <span className="md-search-suggestion__icon material-symbols-outlined">
                {suggestion.type === 'location' ? 'location_on' : 
                 suggestion.type === 'hospital' ? 'local_hospital' : 
                 suggestion.type === 'recent' ? 'history' : 'search'}
              </span>
              <div className="md-search-suggestion__content">
                <div className="md-search-suggestion__text">
                  {suggestion.title || suggestion.name}
                </div>
                {suggestion.subtitle && (
                  <div className="md-search-suggestion__secondary">
                    {suggestion.subtitle}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

SearchBar.propTypes = {
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  onSearch: PropTypes.func,
  onSuggestionSelect: PropTypes.func,
  suggestions: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    title: PropTypes.string,
    name: PropTypes.string,
    subtitle: PropTypes.string,
    type: PropTypes.oneOf(['location', 'hospital', 'recent', 'suggestion'])
  })),
  placeholder: PropTypes.string,
  loading: PropTypes.bool,
  className: PropTypes.string
};

export default SearchBar;
