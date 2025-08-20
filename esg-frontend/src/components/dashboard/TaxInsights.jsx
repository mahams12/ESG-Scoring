import React from 'react';
import { LightBulbIcon, ArrowTrendingUpIcon } from '@heroicons/react/24/outline'; // Updated icon

const TaxInsights = () => {
  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-white mb-6">ESG Insights</h3>
      
      {/* Savings Insight */}
      <div className="bg-primary-600 rounded-lg p-4 mb-4">
        <div className="flex items-start space-x-3">
          <LightBulbIcon className="w-6 h-6 text-white flex-shrink-0 mt-1" />
          <div>
            <h4 className="font-medium text-white mb-2">Investment Opportunity</h4>
            <p className="text-sm text-primary-100">
              You could save up to $0.00 in taxes by optimizing your ESG investment portfolio.
            </p>
          </div>
        </div>
      </div>

      {/* Performance Insight */}
      <div className="bg-success-600 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <ArrowTrendingUpIcon className="w-6 h-6 text-white flex-shrink-0 mt-1" /> {/* Updated icon */}
          <div>
            <h4 className="font-medium text-white mb-2">Portfolio Performance</h4>
            <p className="text-sm text-success-100">
              Your ESG-focused investments have outperformed the market by 2.3% this quarter.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaxInsights;