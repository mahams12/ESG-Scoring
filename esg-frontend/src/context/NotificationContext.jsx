// src/context/NotificationContext.jsx
import React, { createContext, useContext, useState, useCallback } from 'react';

const NotificationContext = createContext();

export const NotificationContextProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);

  const addNotification = useCallback((notification) => {
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      type: 'info',
      title: '',
      message: '',
      duration: 5000,
      ...notification
    };

    setNotifications(prev => [...prev, newNotification]);

    if (newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }

    return id;
  }, []);

  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const showSuccess = useCallback((message, title = 'Success') => {
    return addNotification({
      type: 'success',
      title,
      message
    });
  }, [addNotification]);

  const showError = useCallback((message, title = 'Error') => {
    return addNotification({
      type: 'error',
      title,
      message,
      duration: 8000
    });
  }, [addNotification]);

  const showInfo = useCallback((message, title = 'Info') => {
    return addNotification({
      type: 'info',
      title,
      message
    });
  }, [addNotification]);

  const showWarning = useCallback((message, title = 'Warning') => {
    return addNotification({
      type: 'warning',
      title,
      message
    });
  }, [addNotification]);

  const showNotification = useCallback((notification) => {
    if (typeof notification === 'string') {
      return addNotification({
        type: 'info',
        message: notification
      });
    }
    return addNotification(notification);
  }, [addNotification]);

  const value = {
    notifications,
    addNotification,
    removeNotification,
    clearAllNotifications,
    showSuccess,
    showError,
    showInfo,
    showWarning,
    showNotification
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotification = () => {
  const context = useContext(NotificationContext);
  
  if (!context) {
    console.warn('useNotification must be used within a NotificationContextProvider');
    return {
      notifications: [],
      addNotification: () => {},
      removeNotification: () => {},
      clearAllNotifications: () => {},
      showSuccess: () => {},
      showError: () => {},
      showInfo: () => {},
      showWarning: () => {},
      showNotification: () => {}
    };
  }
  
  return context;
};

export default NotificationContext;