import React from 'react';

const LoadingSpinner = ({ size = 'medium', className = '', message = '' }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };

  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <div className={`spinner ${sizeClasses[size]} border-2 border-dark-600 border-t-primary-500`} />
      {message && (
        <p className="text-dark-400 text-sm mt-3 animate-pulse">{message}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;