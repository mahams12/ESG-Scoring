import React, { createContext, useContext, useState, useCallback } from 'react';

// Create the context
export const NotificationContext = createContext(undefined);

// Custom hook to use the notification context
export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationContextProvider');
  }
  return context;
};

// Notification context provider component
export const NotificationContextProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);

  // Function to show a notification
  const showNotification = useCallback((message, type = 'info', duration = 5000) => {
    const id = Date.now() + Math.random();
    const notification = {
      id,
      message,
      type,
      timestamp: new Date().toISOString()
    };

    setNotifications(prev => [...prev, notification]);

    // Auto remove notification after duration
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }

    return id;
  }, []);

  // Function to remove a specific notification
  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  // Function to clear all notifications
  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // Context value
  const value = {
    notifications,
    showNotification,
    removeNotification,
    clearAllNotifications
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

// Default export for convenience
export default NotificationContextProvider;