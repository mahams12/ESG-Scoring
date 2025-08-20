// src/components/analysis/CompanySearch.jsx
import React, { useState, useCallback } from 'react';
import { Search, Loader, TrendingUp, Building, CheckCircle, AlertTriangle } from 'lucide-react';
import { useNotification } from '../../context/NotificationContext';
import { useESGContext } from '../../context/ESGContext';
import api from '../../services/api';

const CompanySearch = ({ onAnalysisComplete, className = '' }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [lastAnalysis, setLastAnalysis] = useState(null);
  const { showSuccess, showError, showInfo } = useNotification();
  const { updateAnalysis, setIsAnalyzing: setGlobalAnalyzing } = useESGContext();

  const commonTickers = [
    { ticker: 'AAPL', name: 'Apple Inc.', sector: 'Technology' },
    { ticker: 'MSFT', name: 'Microsoft Corporation', sector: 'Technology' },
    { ticker: 'META', name: 'Meta Platforms Inc.', sector: 'Technology' },
    { ticker: 'GOOGL', name: 'Alphabet Inc.', sector: 'Technology' },
    { ticker: 'TSLA', name: 'Tesla Inc.', sector: 'Automotive' },
    { ticker: 'AMZN', name: 'Amazon.com Inc.', sector: 'E-commerce' },
    { ticker: 'NVDA', name: 'NVIDIA Corporation', sector: 'Technology' },
    { ticker: 'JPM', name: 'JPMorgan Chase & Co.', sector: 'Financial' },
    { ticker: 'JNJ', name: 'Johnson & Johnson', sector: 'Healthcare' },
    { ticker: 'V', name: 'Visa Inc.', sector: 'Financial' }
  ];

  // Test backend connectivity
  const testConnection = async () => {
    try {
      const response = await api.get('/api/v1/analysis/test', { timeout: 5000 });
      return response.data;
    } catch (error) {
      throw new Error(`Backend connection failed: ${error.message}`);
    }
  };

  // Perform ESG analysis
  const performAnalysis = async (ticker) => {
    try {
      setIsAnalyzing(true);
      setGlobalAnalyzing(true); // Update global state
      showInfo(`Starting ESG analysis for ${ticker}...`);

      // Test connection first
      try {
        await testConnection();
      } catch (error) {
        throw new Error('Cannot connect to backend. Make sure server is running on http://localhost:8000');
      }

      console.log('Calling ESG analysis endpoint...');
      
      // Call the simple analysis endpoint
      const response = await api.post('/api/v1/analysis/esg/simple', {
        ticker: ticker.toUpperCase()
      }, { 
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('Analysis response:', response.data);

      if (response.data?.status === 'success') {
        const analysisData = response.data.data;
        showSuccess(`ESG analysis completed for ${ticker}`);
        
        // Update global ESG context
        updateAnalysis(analysisData, ticker);
        
        setLastAnalysis({
          ticker,
          timestamp: new Date(),
          score: analysisData.esg_scores.overall_score
        });
        
        if (onAnalysisComplete) {
          onAnalysisComplete(analysisData, ticker);
        }
        return analysisData;
      } else {
        throw new Error(response.data?.message || 'Analysis failed');
      }

    } catch (error) {
      console.error('ESG analysis failed:', error);
      
      // Better error messages
      if (error.code === 'ECONNABORTED') {
        showError(`Analysis timeout for ${ticker}. Try again in a moment.`);
      } else if (error.response?.status === 404) {
        showError(`Endpoint not found. Check if backend is running on http://localhost:8000`);
      } else if (error.response?.status === 500) {
        showError(`Server error: ${error.response?.data?.detail || 'Internal server error'}`);
      } else if (error.message?.includes('Network Error') || error.message?.includes('ERR_NETWORK')) {
        showError(`Connection failed. Check if backend is running and CORS is configured.`);
      } else if (error.message?.includes('Cannot connect')) {
        showError(error.message);
      } else {
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to analyze company';
        showError(`Analysis failed: ${errorMessage}`);
      }
      throw error;
    } finally {
      setIsAnalyzing(false);
      setGlobalAnalyzing(false); // Update global state
    }
  };

  // Handle search input changes
  const handleSearchChange = useCallback((e) => {
    const value = e.target.value;
    setSearchTerm(value);

    if (value.length >= 1) {
      const filtered = commonTickers.filter(
        company => 
          company.ticker.toLowerCase().includes(value.toLowerCase()) ||
          company.name.toLowerCase().includes(value.toLowerCase())
      );
      setSuggestions(filtered.slice(0, 5));
      setShowSuggestions(true);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, []);

  // Handle search submission
  const handleSearch = useCallback(async (e) => {
    e.preventDefault();
    
    if (!searchTerm.trim()) {
      showError('Please enter a company ticker symbol');
      return;
    }

    const ticker = searchTerm.trim().toUpperCase();

    try {
      await performAnalysis(ticker);
    } catch (error) {
      // Error already handled in performAnalysis
    }
  }, [searchTerm, showError, onAnalysisComplete]);

  // Handle suggestion click
  const handleSuggestionClick = useCallback(async (suggestion) => {
    setSearchTerm(suggestion.ticker);
    setShowSuggestions(false);
    setSuggestions([]);
    
    // Auto-trigger analysis
    setTimeout(async () => {
      try {
        await performAnalysis(suggestion.ticker);
      } catch (error) {
        // Error already handled
      }
    }, 100);
  }, []);

  return (
    <div className={`relative ${className}`}>
      {/* Search Form */}
      <form onSubmit={handleSearch} className="relative">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {isAnalyzing ? (
              <Loader className="h-5 w-5 text-blue-400 animate-spin" />
            ) : (
              <Search className="h-5 w-5 text-dark-400" />
            )}
          </div>
          
          <input
            type="text"
            value={searchTerm}
            onChange={handleSearchChange}
            onFocus={() => {
              if (suggestions.length > 0) {
                setShowSuggestions(true);
              }
            }}
            onBlur={() => {
              setTimeout(() => setShowSuggestions(false), 200);
            }}
            placeholder="Enter company ticker (e.g., META, AAPL, TSLA)"
            disabled={isAnalyzing}
            className="
              block w-full pl-10 pr-12 py-3 text-lg
              bg-dark-800 border border-dark-600 rounded-xl
              text-white placeholder-dark-400
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200
            "
          />
          
          <div className="absolute inset-y-0 right-0 flex items-center">
            <button
              type="submit"
              disabled={isAnalyzing || !searchTerm.trim()}
              className="
                mr-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 
                disabled:bg-blue-600/50 disabled:cursor-not-allowed
                text-white font-medium rounded-lg transition-colors
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-dark-800
              "
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>
      </form>

      {/* Search Suggestions */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-dark-800 border border-dark-600 rounded-xl shadow-lg z-50 max-h-60 overflow-y-auto">
          {suggestions.map((suggestion) => (
            <button
              key={suggestion.ticker}
              type="button"
              onClick={() => handleSuggestionClick(suggestion)}
              className="
                w-full flex items-center space-x-3 px-4 py-3 text-left
                hover:bg-dark-700 transition-colors
                first:rounded-t-xl last:rounded-b-xl
                focus:outline-none focus:bg-dark-700
              "
            >
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-dark-700 rounded-lg flex items-center justify-center">
                  <Building className="w-5 h-5 text-blue-400" />
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-white">{suggestion.ticker}</span>
                  <span className="text-xs px-2 py-1 bg-dark-600 text-dark-300 rounded">
                    {suggestion.sector}
                  </span>
                </div>
                <p className="text-sm text-dark-400 truncate">{suggestion.name}</p>
              </div>
              <TrendingUp className="w-4 h-4 text-green-400 flex-shrink-0" />
            </button>
          ))}
        </div>
      )}

      {/* Analysis Status */}
      {isAnalyzing && (
        <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
          <div className="flex items-center space-x-3">
            <Loader className="w-5 h-5 text-blue-400 animate-spin" />
            <div>
              <p className="text-blue-400 font-medium">Running ESG Analysis...</p>
              <p className="text-sm text-blue-300">
                Analyzing ESG performance and generating insights
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Last Analysis Success */}
      {lastAnalysis && !isAnalyzing && (
        <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <div>
              <p className="text-green-400 font-medium">
                Last Analysis: {lastAnalysis.ticker} - Score: {lastAnalysis.score}/100
              </p>
              <p className="text-sm text-green-300">
                Completed {lastAnalysis.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Quick Start */}
      {!isAnalyzing && searchTerm === '' && (
        <div className="mt-6">
          <p className="text-sm text-dark-400 mb-3">Popular companies to analyze:</p>
          <div className="flex flex-wrap gap-2">
            {commonTickers.slice(0, 8).map((company) => (
              <button
                key={company.ticker}
                onClick={() => handleSuggestionClick(company)}
                className="
                  px-3 py-2 bg-dark-700 hover:bg-dark-600 
                  text-dark-300 hover:text-white rounded-lg
                  text-sm transition-colors
                  focus:outline-none focus:ring-2 focus:ring-blue-500
                "
              >
                {company.ticker}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Backend Status Indicator */}
      <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-yellow-400" />
          <p className="text-xs text-yellow-300">
            <strong>Live Data Mode:</strong> Backend running on http://localhost:8000 | 
            Using comprehensive ESG analysis with AI insights
          </p>
        </div>
      </div>
    </div>
  );
};

export default CompanySearch;