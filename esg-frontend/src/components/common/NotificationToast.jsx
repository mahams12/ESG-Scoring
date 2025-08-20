import React from 'react';
import { XMarkIcon, CheckCircleIcon, ExclamationTriangleIcon, InformationCircleIcon } from '@heroicons/react/24/outline';
import { useNotification } from '../../context/NotificationContext';

const NotificationToast = () => {
  const { notifications, removeNotification } = useNotification();

  const getIconAndColor = (type) => {
    switch (type) {
      case 'success':
        return { 
          icon: CheckCircleIcon, 
          color: 'bg-success-500 border-success-400',
          textColor: 'text-white'
        };
      case 'error':
        return { 
          icon: ExclamationTriangleIcon, 
          color: 'bg-danger-500 border-danger-400',
          textColor: 'text-white'
        };
      case 'warning':
        return { 
          icon: ExclamationTriangleIcon, 
          color: 'bg-warning-500 border-warning-400',
          textColor: 'text-white'
        };
      default:
        return { 
          icon: InformationCircleIcon, 
          color: 'bg-primary-500 border-primary-400',
          textColor: 'text-white'
        };
    }
  };

  if (!notifications || notifications.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {notifications.map((notification) => {
        const { icon: Icon, color, textColor } = getIconAndColor(notification.type);
        
        return (
          <div
            key={notification.id}
            className={`max-w-sm w-full ${color} border rounded-lg shadow-lg p-4 animate-slide-up`}
            style={{
              animation: 'slideUp 0.3s ease-out'
            }}
          >
            <div className="flex items-start">
              <Icon className={`w-5 h-5 ${textColor} flex-shrink-0 mt-0.5`} />
              <div className="ml-3 flex-1">
                <p className={`text-sm font-medium ${textColor}`}>
                  {notification.message}
                </p>
              </div>
              <button
                onClick={() => removeNotification(notification.id)}
                className={`ml-3 flex-shrink-0 ${textColor} hover:opacity-75 transition-opacity`}
              >
                <XMarkIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default NotificationToast;