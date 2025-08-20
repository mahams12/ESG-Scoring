import React, { useState } from 'react';
import ReportsOverview from '../components/reports/ReportsOverview';
import FinancialCharts from '../components/reports/FinancialCharts';
import ExpenseBreakdown from '../components/reports/ExpenseBreakdown';
import ReportFilters from '../components/reports/ReportFilters';

const Reports = () => {
  const [selectedReport, setSelectedReport] = useState('overview');
  const [selectedPeriod, setSelectedPeriod] = useState('This Year');
  const [reportType, setReportType] = useState('Financial Summary');

  const handleFilterChange = (filters) => {
    setSelectedPeriod(filters.period);
    setReportType(filters.reportType);
  };

  const renderReportContent = () => {
    switch (selectedReport) {
      case 'overview':
        return <ReportsOverview period={selectedPeriod} />;
      case 'monthly':
        return <FinancialCharts period="monthly" />;
      case 'annual':
        return <FinancialCharts period="annual" />;
      case 'tax':
        return <ExpenseBreakdown />;
      default:
        return <ReportsOverview period={selectedPeriod} />;
    }
  };

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Reports & Analytics</h1>
          <p className="text-dark-300">Generate insights and reports for your business</p>
        </div>
        <div className="flex items-center space-x-4">
          <ReportFilters onFiltersChange={handleFilterChange} />
          <button className="btn-primary flex items-center space-x-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Report Navigation */}
      <div className="card p-1">
        <div className="flex space-x-1">
          {[
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'monthly', label: 'Monthly Reports', icon: '📅' },
            { id: 'annual', label: 'Annual Reports', icon: '📈' },
            { id: 'tax', label: 'Tax Estimation', icon: '💼' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedReport(tab.id)}
              className={`flex items-center space-x-2 px-4 py-3 rounded-lg font-medium transition-all duration-200 ${
                selectedReport === tab.id
                  ? 'bg-primary-600 text-white shadow-md'
                  : 'text-dark-300 hover:text-white hover:bg-dark-700'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Report Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2">
          {renderReportContent()}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <ExpenseBreakdown />
        </div>
      </div>
    </div>
  );
};

export default Reports;