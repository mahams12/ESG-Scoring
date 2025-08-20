import React from 'react';
import { clsx } from 'clsx';

const Input = ({ 
  type = 'text',
  placeholder = '',
  value,
  onChange,
  disabled = false,
  error = '',
  label = '',
  icon: Icon,
  className = '',
  ...props 
}) => {
  const baseClasses = 'bg-dark-700 border border-dark-600 text-white placeholder-dark-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200';
  const errorClasses = error ? 'border-danger-500 focus:ring-danger-500' : '';
  const disabledClasses = disabled ? 'opacity-50 cursor-not-allowed' : '';
  const paddingClasses = Icon ? 'pl-10 pr-4 py-2' : 'px-3 py-2';

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-white mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <Icon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-400" />
        )}
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          disabled={disabled}
          className={clsx(
            baseClasses,
            paddingClasses,
            errorClasses,
            disabledClasses,
            className
          )}
          {...props}
        />
      </div>
      {error && (
        <p className="mt-1 text-sm text-danger-500">{error}</p>
      )}
    </div>
  );
};

export default Input;
