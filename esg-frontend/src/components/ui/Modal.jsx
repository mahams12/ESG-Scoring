import React from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

const Modal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  size = 'medium',
  showCloseButton = true 
}) => {
  const sizes = {
    small: 'max-w-md',
    medium: 'max-w-lg',
    large: 'max-w-4xl',
    xl: 'max-w-6xl'
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div 
          className="fixed inset-0 transition-opacity bg-dark-900 bg-opacity-75"
          onClick={onClose}
        />

        {/* Modal panel */}
        <div className={`inline-block w-full ${sizes[size]} p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-dark-800 border border-dark-700 shadow-xl rounded-xl`}>
          {/* Header */}
          {(title || showCloseButton) && (
            <div className="flex items-center justify-between mb-6">
              {title && (
                <h3 className="text-lg font-semibold text-white">{title}</h3>
              )}
              {showCloseButton && (
                <button
                  onClick={onClose}
                  className="text-dark-400 hover:text-white transition-colors"
                >
                  <XMarkIcon className="w-6 h-6" />
                </button>
              )}
            </div>
          )}

          {/* Content */}
          <div className="text-white">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Modal;
