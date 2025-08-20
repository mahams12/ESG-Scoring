import React, { useState } from 'react';
import CompanySearch from '../components/analysis/CompanySearch';
import ESGScoreCard from '../components/analysis/ESGScoreCard';
import CompanyProfile from '../components/analysis/CompanyProfile';
import RiskAssessment from '../components/analysis/RiskAssessment';
import BenchmarkComparison from '../components/analysis/BenchmarkComparison';
import AIInsights from '../components/analysis/AIInsights';
import LoadingSpinner from '../components/common/LoadingSpinner';

const ESGAnalysis = () => {
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCompanySelect = async (company) => {
    setLoading(true);
    setError(null);
    setSelectedCompany(company);
    
    try {
      // Simulate API call - replace with actual service call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock analysis data
      const mockData = {
        company: {
          ticker: company.ticker,
          name: company.name,
          sector: 'Technology',
          marketCap: 3000000000000
        },
        esgScores: {
          environmental: 88.5,
          social: 82.1,
          governance: 84.8,
          overall: 85.1
        },
        riskLevel: 'Low-Medium',
        recommendation: 'BUY',
        aiInsights: 'Strong ESG profile with leadership in environmental initiatives and good governance practices.',
        benchmarkData: {
          industryAverage: 72.3,
          percentileRank: 92
        }
      };
      
      setAnalysisData(mockData);
    } catch (err) {
      setError('Failed to analyze company. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedCompany(null);
    setAnalysisData(null);
    setError(null);
  };

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">ESG Analysis</h1>
          <p className="text-dark-300">Analyze companies with AI-powered ESG insights</p>
        </div>
        {selectedCompany && (
          <button
            onClick={handleReset}
            className="btn-secondary"
          >
            New Analysis
          </button>
        )}
      </div>

      {/* Company Search */}
      <CompanySearch 
        onCompanySelect={handleCompanySelect}
        disabled={loading}
      />

      {/* Error State */}
      {error && (
        <div className="card p-6 border-danger-500 bg-danger-50">
          <p className="text-danger-600 font-medium">{error}</p>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="large" />
        </div>
      )}

      {/* Analysis Results */}
      {analysisData && !loading && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Main Analysis */}
          <div className="lg:col-span-2 space-y-6">
            <CompanyProfile company={analysisData.company} />
            <ESGScoreCard scores={analysisData.esgScores} />
            <AIInsights 
              insights={analysisData.aiInsights}
              recommendation={analysisData.recommendation}
              riskLevel={analysisData.riskLevel}
            />
          </div>

          {/* Right Column - Supporting Data */}
          <div className="space-y-6">
            <RiskAssessment 
              riskLevel={analysisData.riskLevel}
              scores={analysisData.esgScores}
            />
            <BenchmarkComparison 
              benchmarkData={analysisData.benchmarkData}
              companyScore={analysisData.esgScores.overall}
            />
          </div>
        </div>
      )}

      {/* Empty State */}
      {!selectedCompany && !loading && (
        <div className="text-center py-12">
          <div className="w-24 h-24 bg-dark-800 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-12 h-12 text-dark-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-white mb-2">Start Your ESG Analysis</h3>
          <p className="text-dark-400">Search for a company above to begin comprehensive ESG analysis</p>
        </div>
      )}
    </div>
  );
};

export default ESGAnalysis;