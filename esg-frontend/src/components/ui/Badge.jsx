import React from 'react';
import { clsx } from 'clsx';

const Badge = ({ 
  children, 
  variant = 'default',
  size = 'medium',
  className = '' 
}) => {
  const baseClasses = 'inline-flex items-center font-medium rounded-full';

  const variants = {
    default: 'bg-dark-700 text-dark-300 border border-dark-600',
    primary: 'bg-primary-600 text-white',
    success: 'bg-success-600 text-white',
    warning: 'bg-warning-600 text-white',
    danger: 'bg-danger-600 text-white',
    outline: 'border border-current text-current bg-transparent'
  };

  const sizes = {
    small: 'px-2 py-1 text-xs',
    medium: 'px-3 py-1 text-sm',
    large: 'px-4 py-2'
  };

  return (
    <span
      className={clsx(
        baseClasses,
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </span>
  );
};

export default Badge;