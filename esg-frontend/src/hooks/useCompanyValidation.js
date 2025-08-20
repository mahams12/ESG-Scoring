import { useState, useCallback } from 'react';
import { companyService } from '../services/companyService';

export const useCompanyValidation = () => {
  const [loading, setLoading] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [error, setError] = useState(null);

  const validateCompany = useCallback(async (ticker) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await companyService.validateTicker(ticker);
      setValidationResult(result);
      return result;
    } catch (err) {
      const errorMessage = err.message || 'Validation failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  const searchCompanies = useCallback(async (query) => {
    if (!query || query.length < 1) {
      return { success: true, data: [] };
    }

    setLoading(true);
    
    try {
      // Use mock search for development
      const companies = companyService.mockSearch(query);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 300));
      
      return { success: true, data: companies };
    } catch (err) {
      const errorMessage = err.message || 'Search failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  const clearValidation = useCallback(() => {
    setValidationResult(null);
    setError(null);
  }, []);

  return {
    loading,
    validationResult,
    error,
    validateCompany,
    searchCompanies,
    clearValidation
  };
};

export default useCompanyValidation;