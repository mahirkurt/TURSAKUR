import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import '../styles/components/textfield.css';

/**
 * Material Design 3 TextField Component
 */
const TextField = ({
  label,
  placeholder,
  value,
  onChange,
  variant = 'filled',
  leadingIcon,
  trailingIcon,
  onTrailingIconClick,
  supportingText,
  error = false,
  disabled = false,
  className = '',
  type = 'text',
  ...props
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [hasValue, setHasValue] = useState(!!value);
  const inputRef = useRef(null);

  useEffect(() => {
    setHasValue(!!value);
  }, [value]);

  const handleFocus = () => {
    setIsFocused(true);
  };

  const handleBlur = () => {
    setIsFocused(false);
  };

  const handleChange = (e) => {
    const newValue = e.target.value;
    setHasValue(!!newValue);
    if (onChange) {
      onChange(e);
    }
  };

  const handleLabelClick = () => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const baseClasses = 'md-textfield';
  const variantClass = `md-textfield--${variant}`;
  const errorClass = error ? 'md-textfield--error' : '';
  const disabledClass = disabled ? 'md-textfield--disabled' : '';
  
  const textfieldClasses = [
    baseClasses,
    variantClass,
    errorClass,
    disabledClass,
    className
  ].filter(Boolean).join(' ');

  const labelFloating = isFocused || hasValue || placeholder;

  return (
    <div className={textfieldClasses}>
      <div className="md-textfield__container">
        {leadingIcon && (
          <span className="md-textfield__icon md-textfield__icon--leading material-symbols-outlined">
            {leadingIcon}
          </span>
        )}
        
        <input
          ref={inputRef}
          type={type}
          className="md-textfield__input"
          value={value}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={labelFloating ? placeholder : ''}
          disabled={disabled}
          {...props}
        />
        
        {label && (
          <label
            className={`md-textfield__label ${labelFloating ? 'md-textfield__label--floating' : ''}`}
            onClick={handleLabelClick}
          >
            {label}
          </label>
        )}
        
        {trailingIcon && (
          <span
            className="md-textfield__icon md-textfield__icon--trailing material-symbols-outlined"
            onClick={onTrailingIconClick}
          >
            {trailingIcon}
          </span>
        )}
      </div>
      
      {supportingText && (
        <div className="md-textfield__supporting-text">
          <span>{supportingText}</span>
        </div>
      )}
    </div>
  );
};

TextField.propTypes = {
  label: PropTypes.string,
  placeholder: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func,
  variant: PropTypes.oneOf(['filled', 'outlined']),
  leadingIcon: PropTypes.string,
  trailingIcon: PropTypes.string,
  onTrailingIconClick: PropTypes.func,
  supportingText: PropTypes.string,
  error: PropTypes.bool,
  disabled: PropTypes.bool,
  className: PropTypes.string,
  type: PropTypes.string
};

export default TextField;
