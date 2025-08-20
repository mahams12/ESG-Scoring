import React, { useState, useRef, useEffect } from 'react';
import { MagnifyingGlassIcon, BuildingOfficeIcon } from '@heroicons/react/24/outline';

const CompanySearch = ({ onCompanySelect, disabled }) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loading, setLoading] = useState(false);
  const searchRef = useRef(null);

  // Mock company data
  const companies = [
    { ticker: 'AAPL', name: 'Apple Inc.', sector: 'Technology' },
    { ticker: 'MSFT', name: 'Microsoft Corporation', sector: 'Technology' },
    { ticker: 'GOOGL', name: 'Alphabet Inc.', sector: 'Technology' },
    { ticker: 'TSLA', name: 'Tesla, Inc.', sector: 'Automotive' },
    { ticker: 'AMZN', name: 'Amazon.com, Inc.', sector: 'E-commerce' },
    { ticker: 'META', name: 'Meta Platforms, Inc.', sector: 'Technology' },
    { ticker: 'NVDA', name: 'NVIDIA Corporation', sector: 'Technology' },
    { ticker: 'JPM', name: 'JPMorgan Chase & Co.', sector: 'Financial Services' },
    { ticker: 'JNJ', name: 'Johnson & Johnson', sector: 'Healthcare' },
    { ticker: 'V', name: 'Visa Inc.', sector: 'Financial Services' }
  ];

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = async (searchQuery) => {
    setQuery(searchQuery);
    
    if (searchQuery.length > 0) {
      setLoading(true);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const filtered = companies.filter(company =>
        company.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        company.ticker.toLowerCase().includes(searchQuery.toLowerCase())
      );
      
      setSuggestions(filtered);
      setShowSuggestions(true);
      setLoading(false);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const handleCompanySelect = (company) => {
    setQuery(`${company.ticker} - ${company.name}`);
    setShowSuggestions(false);
    onCompanySelect(company);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Try to find exact match
    const exactMatch = companies.find(company =>
      company.ticker.toLowerCase() === query.toLowerCase() ||
      company.name.toLowerCase() === query.toLowerCase()
    );
    
    if (exactMatch) {
      handleCompanySelect(exactMatch);
    } else if (suggestions.length > 0) {
      handleCompanySelect(suggestions[0]);
    }
  };

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Company Search</h3>
      
      <form onSubmit={handleSubmit} className="relative" ref={searchRef}>
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-400" />
          <input
            type="text"
            placeholder="Search by company name or ticker symbol (e.g., AAPL, Apple)"
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            disabled={disabled}
            className="w-full pl-10 pr-4 py-3 input-field text-lg"
          />
          {loading && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <div className="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}
        </div>

        {/* Suggestions Dropdown */}
        {showSuggestions && suggestions.length > 0 && (
          <div className="absolute z-10 w-full mt-2 bg-dark-800 border border-dark-600 rounded-lg shadow-lg max-h-60 overflow-y-auto">
            {suggestions.map((company, index) => (
              <button
                key={index}
                type="button"
                onClick={() => handleCompanySelect(company)}
                className="w-full px-4 py-3 text-left hover:bg-dark-700 transition-colors duration-200 flex items-center space-x-3"
              >
                <BuildingOfficeIcon className="w-5 h-5 text-dark-400" />
                <div>
                  <div className="font-medium text-white">
                    {company.ticker} - {company.name}
                  </div>
                  <div className="text-sm text-dark-400">{company.sector}</div>
                </div>
              </button>
            ))}
          </div>
        )}

        {/* No Results */}
        {showSuggestions && suggestions.length === 0 && query.length > 0 && !loading && (
          <div className="absolute z-10 w-full mt-2 bg-dark-800 border border-dark-600 rounded-lg shadow-lg p-4">
            <p className="text-dark-400 text-center">
              No companies found. Please check the ticker symbol or company name.
            </p>
          </div>
        )}

        <button
          type="submit"
          disabled={disabled || !query.trim()}
          className="btn-primary mt-4 w-full"
        >
          {disabled ? 'Analyzing...' : 'Analyze Company'}
        </button>
      </form>
    </div>
  );
};

export default CompanySearch;