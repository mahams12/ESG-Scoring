import { useState, useCallback } from 'react';
import { esgService } from '../services/esgService';
import { useNotification } from './useNotification';

export const useESGAnalysis = () => {
  const [loading, setLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);
  const [error, setError] = useState(null);
  const { showNotification } = useNotification();

  const analyzeCompany = useCallback(async (ticker) => {
    setLoading(true);
    setError(null);
    
    try {
      // First validate company exists
      const validation = await esgService.validateCompany(ticker);
      if (!validation.success) {
        throw new Error(validation.error);
      }

      // Perform ESG analysis
      const result = await esgService.analyzeCompany(ticker);
      if (!result.success) {
        throw new Error(result.error);
      }

      setAnalysisData(result.data);
      showNotification(`ESG analysis completed for ${ticker}`, 'success');
      return { success: true, data: result.data };
      
    } catch (err) {
      const errorMessage = err.message || 'Analysis failed';
      setError(errorMessage);
      showNotification(errorMessage, 'error');
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  const getLatestAnalysis = useCallback(async (ticker) => {
    try {
      const result = await esgService.getLatestAnalysis(ticker);
      if (result.success) {
        setAnalysisData(result.data);
      }
      return result;
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch analysis';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  }, []);

  const clearAnalysis = useCallback(() => {
    setAnalysisData(null);
    setError(null);
  }, []);

  const mockAnalyze = useCallback(async (ticker) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockData = esgService.getMockAnalysis(ticker);
      setAnalysisData(mockData);
      showNotification(`ESG analysis completed for ${ticker}`, 'success');
      return { success: true, data: mockData };
      
    } catch (err) {
      const errorMessage = 'Mock analysis failed';
      setError(errorMessage);
      showNotification(errorMessage, 'error');
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  return {
    loading,
    analysisData,
    error,
    analyzeCompany,
    getLatestAnalysis,
    clearAnalysis,
    mockAnalyze
  };
};

export default useESGAnalysis;