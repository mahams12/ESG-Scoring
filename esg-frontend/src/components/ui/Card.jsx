import React from 'react';
import { clsx } from 'clsx';

const Card = ({ 
  children, 
  className = '',
  hover = false,
  padding = 'default',
  ...props 
}) => {
  const baseClasses = 'bg-dark-800 rounded-xl border border-dark-700 shadow-soft';
  
  const paddingClasses = {
    none: '',
    small: 'p-4',
    default: 'p-6',
    large: 'p-8'
  };

  const hoverClasses = hover ? 'hover:bg-dark-750 hover:shadow-medium hover:border-dark-600 transition-all duration-200 cursor-pointer' : '';

  return (
    <div
      className={clsx(
        baseClasses,
        paddingClasses[padding],
        hoverClasses,
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;