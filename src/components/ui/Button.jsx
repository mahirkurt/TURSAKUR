import React, { forwardRef } from 'react';
import PropTypes from 'prop-types';
import '../../styles/components/button.css';

/**
 * Material Design 3 Button Component
 * Tasarım rehberine göre hazırlanmış button bileşeni
 */
const Button = forwardRef(({
  children,
  variant = 'filled',
  size = 'medium',
  icon,
  iconPosition = 'start',
  disabled = false,
  className = '',
  onClick,
  type = 'button',
  ...props
}, ref) => {
  const baseClasses = 'md-button';
  const variantClass = `md-button--${variant}`;
  const sizeClass = size !== 'medium' ? `md-button--${size}` : '';
  
  const buttonClasses = [
    baseClasses,
    variantClass,
    sizeClass,
    className
  ].filter(Boolean).join(' ');

  const renderIcon = () => {
    if (!icon) return null;
    
    return (
      <span className="md-button__icon material-symbols-outlined">
        {icon}
      </span>
    );
  };

  const renderContent = () => {
    if (!icon) return children;
    
    if (iconPosition === 'end') {
      return (
        <>
          {children}
          {renderIcon()}
        </>
      );
    }
    
    return (
      <>
        {renderIcon()}
        {children}
      </>
    );
  };

  return (
    <button
      ref={ref}
      type={type}
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {renderContent()}
    </button>
  );
});

Button.displayName = 'Button';

Button.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['filled', 'outlined', 'text', 'elevated', 'filled-tonal']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  icon: PropTypes.string,
  iconPosition: PropTypes.oneOf(['start', 'end']),
  disabled: PropTypes.bool,
  className: PropTypes.string,
  onClick: PropTypes.func,
  type: PropTypes.oneOf(['button', 'submit', 'reset'])
};

export default Button;
