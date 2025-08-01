import React from 'react';
import PropTypes from 'prop-types';
import '../../styles/components/card.css';

/**
 * Material Design 3 Card Component
 * Tasarım rehberine göre hazırlanmış card bileşeni
 */
const Card = ({
  children,
  variant = 'elevated',
  size = 'standard',
  interactive = false,
  className = '',
  onClick,
  ...props
}) => {
  const baseClasses = 'md-card';
  const variantClass = `md-card--${variant}`;
  const sizeClass = size !== 'standard' ? `md-card--${size}` : '';
  const interactiveClass = interactive ? 'md-card--interactive' : '';
  
  const cardClasses = [
    baseClasses,
    variantClass,
    sizeClass,
    interactiveClass,
    className
  ].filter(Boolean).join(' ');

  const cardProps = {
    className: cardClasses,
    ...props
  };

  if (interactive && onClick) {
    cardProps.onClick = onClick;
    cardProps.role = 'button';
    cardProps.tabIndex = 0;
    cardProps.onKeyDown = (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onClick(e);
      }
    };
  }

  return (
    <div {...cardProps}>
      {children}
    </div>
  );
};

/**
 * Card Media Component - görsel içerik için
 */
const CardMedia = ({ children, className = '', ...props }) => (
  <div className={`md-card__media ${className}`} {...props}>
    {children}
  </div>
);

/**
 * Card Content Component - ana içerik için
 */
const CardContent = ({ children, className = '', ...props }) => (
  <div className={`md-card__content ${className}`} {...props}>
    {children}
  </div>
);

/**
 * Card Header Component - başlık alanı için
 */
const CardHeader = ({ title, subtitle, className = '', ...props }) => (
  <div className={`md-card__header ${className}`} {...props}>
    {title && <h3 className="md-card__title">{title}</h3>}
    {subtitle && <p className="md-card__subtitle">{subtitle}</p>}
  </div>
);

/**
 * Card Actions Component - buton alanı için
 */
const CardActions = ({ children, alignment = 'start', className = '', ...props }) => {
  const alignmentClass = alignment !== 'start' ? `md-card__actions--${alignment}` : '';
  const actionsClasses = `md-card__actions ${alignmentClass} ${className}`.trim();
  
  return (
    <div className={actionsClasses} {...props}>
      {children}
    </div>
  );
};

/**
 * Card Metadata Component - ek bilgiler için
 */
const CardMetadata = ({ items = [], className = '', ...props }) => (
  <div className={`md-card__metadata ${className}`} {...props}>
    {items.map((item, index) => (
      <div key={index} className="md-card__metadata-item">
        {item.icon && (
          <span className="md-card__metadata-icon material-symbols-outlined">
            {item.icon}
          </span>
        )}
        <span>{item.text}</span>
      </div>
    ))}
  </div>
);

/**
 * Card Badge Component - etiket için
 */
const CardBadge = ({ children, className = '', ...props }) => (
  <div className={`md-card__badge ${className}`} {...props}>
    {children}
  </div>
);

// PropTypes
Card.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['elevated', 'filled', 'outlined']),
  size: PropTypes.oneOf(['compact', 'standard', 'tall']),
  interactive: PropTypes.bool,
  className: PropTypes.string,
  onClick: PropTypes.func
};

CardMedia.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string
};

CardContent.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string
};

CardHeader.propTypes = {
  title: PropTypes.string,
  subtitle: PropTypes.string,
  className: PropTypes.string
};

CardActions.propTypes = {
  children: PropTypes.node.isRequired,
  alignment: PropTypes.oneOf(['start', 'end', 'between']),
  className: PropTypes.string
};

CardMetadata.propTypes = {
  items: PropTypes.arrayOf(PropTypes.shape({
    icon: PropTypes.string,
    text: PropTypes.string.isRequired
  })),
  className: PropTypes.string
};

CardBadge.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string
};

// Export all components
export default Card;
export { CardMedia, CardContent, CardHeader, CardActions, CardMetadata, CardBadge };
