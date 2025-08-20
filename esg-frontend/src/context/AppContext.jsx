// src/context/AppContext.jsx
import React, { createContext, useContext, useState, useCallback } from 'react';

// Create the context
const AppContext = createContext();

// App provider component
export const AppContextProvider = ({ children }) => {
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentCompany, setCurrentCompany] = useState(null);
  const [recentAnalyses, setRecentAnalyses] = useState([]);

  // Loading state management
  const startLoading = useCallback(() => setLoading(true), []);
  const stopLoading = useCallback(() => setLoading(false), []);

  // Sidebar state management
  const toggleSidebar = useCallback(() => setSidebarOpen(prev => !prev), []);

  // Company state management
  const updateCurrentCompany = useCallback((company) => {
    setCurrentCompany(company);
    
    // Add to recent analyses if it's a new analysis
    if (company && company.ticker) {
      setRecentAnalyses(prev => {
        const filtered = prev.filter(item => item.ticker !== company.ticker);
        return [company, ...filtered].slice(0, 10); // Keep last 10
      });
    }
  }, []);

  // Clear current analysis
  const clearCurrentCompany = useCallback(() => {
    setCurrentCompany(null);
  }, []);

  const value = {
    // State
    loading,
    user,
    sidebarOpen,
    currentCompany,
    recentAnalyses,
    
    // Actions
    startLoading,
    stopLoading,
    setUser,
    toggleSidebar,
    setSidebarOpen,
    updateCurrentCompany,
    clearCurrentCompany,
    setRecentAnalyses
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

// Hook to use the app context
export const useApp = () => {
  const context = useContext(AppContext);
  
  if (!context) {
    // Return a no-op implementation if context is not available
    console.warn('useApp must be used within an AppContextProvider');
    return {
      loading: false,
      user: null,
      sidebarOpen: true,
      currentCompany: null,
      recentAnalyses: [],
      startLoading: () => {},
      stopLoading: () => {},
      setUser: () => {},
      toggleSidebar: () => {},
      setSidebarOpen: () => {},
      updateCurrentCompany: () => {},
      clearCurrentCompany: () => {},
      setRecentAnalyses: () => {}
    };
  }
  
  return context;
};

export default AppContext;