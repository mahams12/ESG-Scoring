import React from 'react';
import { SparklesIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const AIInsights = ({ insights, recommendation, riskLevel }) => {
  const getRecommendationColor = (rec) => {
    switch (rec?.toUpperCase()) {
      case 'BUY':
        return 'text-success-500 bg-success-500/10 border-success-500/20';
      case 'HOLD':
        return 'text-warning-500 bg-warning-500/10 border-warning-500/20';
      case 'SELL':
        return 'text-danger-500 bg-danger-500/10 border-danger-500/20';
      default:
        return 'text-primary-500 bg-primary-500/10 border-primary-500/20';
    }
  };

  const keyStrengths = [
    'Carbon neutral operations achieved ahead of schedule',
    'Strong board independence and diversity',
    'Comprehensive employee development programs',
    'Transparent ESG reporting and stakeholder engagement'
  ];

  const improvementAreas = [
    'Supply chain sustainability tracking',
    'Water usage reduction initiatives',
    'Community investment programs',
    'Waste reduction in manufacturing'
  ];

  return (
    <div className="card p-6">
      <div className="flex items-center space-x-3 mb-6">
        <SparklesIcon className="w-6 h-6 text-primary-400" />
        <h3 className="text-lg font-semibold text-white">AI-Powered Insights</h3>
      </div>

      {/* Investment Recommendation */}
      <div className={`p-4 rounded-lg border mb-6 ${getRecommendationColor(recommendation)}`}>
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-semibold text-white">Investment Recommendation</h4>
          <span className={`px-3 py-1 rounded-full font-bold ${getRecommendationColor(recommendation)}`}>
            {recommendation}
          </span>
        </div>
        <p className="text-sm text-dark-300">{insights}</p>
      </div>

      {/* Key Strengths */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-4">
          <CheckCircleIcon className="w-5 h-5 text-success-400" />
          <h5 className="font-medium text-white">Key Strengths</h5>
        </div>
        <div className="space-y-2">
          {keyStrengths.map((strength, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-success-500/5 border border-success-500/10 rounded-lg">
              <CheckCircleIcon className="w-4 h-4 text-success-400 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-dark-300">{strength}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Areas for Improvement */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-4">
          <ExclamationTriangleIcon className="w-5 h-5 text-warning-400" />
          <h5 className="font-medium text-white">Areas for Improvement</h5>
        </div>
        <div className="space-y-2">
          {improvementAreas.map((area, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-warning-500/5 border border-warning-500/10 rounded-lg">
              <ExclamationTriangleIcon className="w-4 h-4 text-warning-400 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-dark-300">{area}</p>
            </div>
          ))}
        </div>
      </div>

      {/* AI Confidence Score */}
      <div className="p-4 bg-dark-900 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-white">AI Confidence Level</span>
          <span className="text-sm font-bold text-primary-400">85%</span>
        </div>
        <div className="w-full bg-dark-700 rounded-full h-2">
          <div 
            className="h-2 bg-primary-500 rounded-full transition-all duration-1000"
            style={{ width: '85%' }}
          />
        </div>
        <p className="text-xs text-dark-400 mt-2">
          High confidence based on comprehensive data analysis and market trends
        </p>
      </div>
    </div>
  );
};

export default AIInsights;