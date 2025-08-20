import React, { createContext, useContext, useReducer } from 'react';

const AppContext = createContext();

const initialState = {
  user: null,
  currentAnalysis: null,
  loading: false,
  error: null,
  theme: 'dark'
};

const appReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_CURRENT_ANALYSIS':
      return { ...state, currentAnalysis: action.payload };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
};

export const AppContextProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const setLoading = (loading) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  };

  const setError = (error) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const setCurrentAnalysis = (analysis) => {
    dispatch({ type: 'SET_CURRENT_ANALYSIS', payload: analysis });
  };

  const value = {
    ...state,
    setLoading,
    setError,
    clearError,
    setCurrentAnalysis
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppContextProvider');
  }
  return context;
};
