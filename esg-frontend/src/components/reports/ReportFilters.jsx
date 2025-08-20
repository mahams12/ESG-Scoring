import React, { useState } from 'react';
import { ChevronDownIcon } from '@heroicons/react/24/outline';

const ReportFilters = ({ onFiltersChange }) => {
  const [selectedPeriod, setSelectedPeriod] = useState('This Year');
  const [selectedReport, setSelectedReport] = useState('Financial Summary');
  const [showPeriodDropdown, setShowPeriodDropdown] = useState(false);
  const [showReportDropdown, setShowReportDropdown] = useState(false);

  const periods = ['This Month', 'Last Month', 'This Quarter', 'Last Quarter', 'This Year', 'Last Year'];
  const reportTypes = ['Financial Summary', 'ESG Analysis', 'Performance Report', 'Compliance Report'];

  const handlePeriodChange = (period) => {
    setSelectedPeriod(period);
    setShowPeriodDropdown(false);
    onFiltersChange?.({ period, reportType: selectedReport });
  };

  const handleReportChange = (reportType) => {
    setSelectedReport(reportType);
    setShowReportDropdown(false);
    onFiltersChange?.({ period: selectedPeriod, reportType });
  };

  return (
    <div className="flex items-center space-x-4">
      {/* Report Type Dropdown */}
      <div className="relative">
        <button
          onClick={() => setShowReportDropdown(!showReportDropdown)}
          className="flex items-center space-x-2 px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white hover:bg-dark-600 transition-colors"
        >
          <span>{selectedReport}</span>
          <ChevronDownIcon className="w-4 h-4" />
        </button>
        
        {showReportDropdown && (
          <div className="absolute right-0 mt-2 w-48 bg-dark-800 border border-dark-600 rounded-lg shadow-lg z-10">
            {reportTypes.map((type) => (
              <button
                key={type}
                onClick={() => handleReportChange(type)}
                className="w-full text-left px-4 py-2 text-white hover:bg-dark-700 first:rounded-t-lg last:rounded-b-lg"
              >
                {type}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Period Dropdown */}
      <div className="relative">
        <button
          onClick={() => setShowPeriodDropdown(!showPeriodDropdown)}
          className="flex items-center space-x-2 px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white hover:bg-dark-600 transition-colors"
        >
          <span>{selectedPeriod}</span>
          <ChevronDownIcon className="w-4 h-4" />
        </button>
        
        {showPeriodDropdown && (
          <div className="absolute right-0 mt-2 w-40 bg-dark-800 border border-dark-600 rounded-lg shadow-lg z-10">
            {periods.map((period) => (
              <button
                key={period}
                onClick={() => handlePeriodChange(period)}
                className="w-full text-left px-4 py-2 text-white hover:bg-dark-700 first:rounded-t-lg last:rounded-b-lg"
              >
                {period}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportFilters;