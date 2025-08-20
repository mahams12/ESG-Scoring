// src/context/ESGContext.jsx
import React, { createContext, useContext, useState, useCallback } from 'react';

const ESGContext = createContext();

export const ESGContextProvider = ({ children }) => {
  const [latestAnalysis, setLatestAnalysis] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Update latest analysis and add to history
  const updateAnalysis = useCallback((analysisData, ticker) => {
    const analysisWithMeta = {
      ...analysisData,
      ticker: ticker,
      timestamp: new Date().toISOString(),
      id: Date.now()
    };

    setLatestAnalysis(analysisWithMeta);
    
    // Add to history (keep last 10)
    setAnalysisHistory(prev => {
      const filtered = prev.filter(item => item.ticker !== ticker);
      return [analysisWithMeta, ...filtered].slice(0, 10);
    });
  }, []);

  // Clear current analysis
  const clearAnalysis = useCallback(() => {
    setLatestAnalysis(null);
  }, []);

  // Get analysis by ticker
  const getAnalysisByTicker = useCallback((ticker) => {
    return analysisHistory.find(item => 
      item.ticker?.toLowerCase() === ticker?.toLowerCase()
    );
  }, [analysisHistory]);

  // Get portfolio summary (average scores)
  const getPortfolioSummary = useCallback(() => {
    if (analysisHistory.length === 0) return null;

    const totalScores = analysisHistory.reduce((acc, analysis) => {
      const scores = analysis.esg_scores || {};
      return {
        environmental: acc.environmental + (scores.environmental_score || 0),
        social: acc.social + (scores.social_score || 0),
        governance: acc.governance + (scores.governance_score || 0),
        overall: acc.overall + (scores.overall_score || 0)
      };
    }, { environmental: 0, social: 0, governance: 0, overall: 0 });

    const count = analysisHistory.length;
    return {
      environmental: totalScores.environmental / count,
      social: totalScores.social / count,
      governance: totalScores.governance / count,
      overall: totalScores.overall / count,
      companiesAnalyzed: count
    };
  }, [analysisHistory]);

  const value = {
    // State
    latestAnalysis,
    analysisHistory,
    isAnalyzing,
    
    // Actions
    updateAnalysis,
    clearAnalysis,
    setIsAnalyzing,
    getAnalysisByTicker,
    getPortfolioSummary
  };

  return (
    <ESGContext.Provider value={value}>
      {children}
    </ESGContext.Provider>
  );
};

export const useESGContext = () => {
  const context = useContext(ESGContext);
  
  if (!context) {
    console.warn('useESGContext must be used within an ESGContextProvider');
    return {
      latestAnalysis: null,
      analysisHistory: [],
      isAnalyzing: false,
      updateAnalysis: () => {},
      clearAnalysis: () => {},
      setIsAnalyzing: () => {},
      getAnalysisByTicker: () => null,
      getPortfolioSummary: () => null
    };
  }
  
  return context;
};

export default ESGContext;