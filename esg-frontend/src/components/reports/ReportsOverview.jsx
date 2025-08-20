import React from 'react';
import FinancialCharts from './FinancialCharts';

const ReportsOverview = ({ period }) => {
  const reportCards = [
    {
      title: 'Profit & Loss Statement',
      description: 'Summary of revenues and expenses',
      icon: '📊',
      color: 'bg-blue-500'
    },
    {
      title: 'ESG Report',
      description: 'Ready-to-file ESG documents',
      icon: '📋',
      color: 'bg-green-500'
    },
    {
      title: 'Expense Analysis',
      description: 'Detailed breakdown by category',
      icon: '💰',
      color: 'bg-purple-500'
    },
    {
      title: 'Cash Flow Report',
      description: 'Track money in and out',
      icon: '💸',
      color: 'bg-orange-500'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Report Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reportCards.map((card, index) => (
          <div key={index} className="card p-6 hover:border-dark-600 transition-colors duration-200 cursor-pointer">
            <div className="flex items-center space-x-4">
              <div className={`w-12 h-12 ${card.color} rounded-lg flex items-center justify-center text-xl`}>
                {card.icon}
              </div>
              <div>
                <h4 className="font-semibold text-white">{card.title}</h4>
                <p className="text-sm text-dark-400 mt-1">{card.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <FinancialCharts period={period} />
    </div>
  );
};

export default ReportsOverview;