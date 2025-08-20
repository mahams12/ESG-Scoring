// src/components/analysis/ESGReportDownload.jsx
import React, { useState } from 'react';
import { Download, FileText, FileSpreadsheet, FileBarChart, Check, X, AlertCircle } from 'lucide-react';
import { useReportDownload } from '../../hooks/useReportDownload';

const ESGReportDownload = ({ ticker, companyName, className = '' }) => {
  const [showFormats, setShowFormats] = useState(false);
  const { 
    downloadReport, 
    isDownloading, 
    downloadProgress, 
    lastDownload,
    availableFormats 
  } = useReportDownload();

  const handleDownload = async (format) => {
    setShowFormats(false);
    await downloadReport(ticker, format, {
      includeCharts: true,
      includeBenchmarks: true,
      includeNews: true
    });
  };

  const getFormatIcon = (format) => {
    switch (format) {
      case 'pdf': return <FileText className="w-4 h-4" />;
      case 'excel': return <FileSpreadsheet className="w-4 h-4" />;
      case 'csv': return <FileBarChart className="w-4 h-4" />;
      default: return <Download className="w-4 h-4" />;
    }
  };

  const getProgressIcon = () => {
    switch (downloadProgress?.status) {
      case 'completed': return <Check className="w-4 h-4 text-green-400" />;
      case 'error': return <X className="w-4 h-4 text-red-400" />;
      default: return <AlertCircle className="w-4 h-4 text-blue-400" />;
    }
  };

  return (
    <div className={`relative ${className}`}>
      {/* Main Download Button */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => setShowFormats(!showFormats)}
          disabled={isDownloading}
          className={`
            flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all
            ${isDownloading 
              ? 'bg-blue-600/50 text-blue-200 cursor-not-allowed' 
              : 'bg-blue-600 hover:bg-blue-700 text-white hover:shadow-lg'
            }
          `}
        >
          <Download className={`w-4 h-4 ${isDownloading ? 'animate-pulse' : ''}`} />
          <span>
            {isDownloading ? 'Generating...' : 'Download Report'}
          </span>
        </button>

        {/* Quick PDF Download */}
        {!showFormats && !isDownloading && (
          <button
            onClick={() => handleDownload('pdf')}
            className="p-2 bg-dark-700 hover:bg-dark-600 text-dark-300 hover:text-white rounded-lg transition-colors"
            title="Quick PDF Download"
          >
            <FileText className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Progress Indicator */}
      {downloadProgress && (
        <div className="absolute top-full mt-2 left-0 right-0 bg-dark-800 border border-dark-600 rounded-lg p-3 shadow-lg z-50">
          <div className="flex items-center space-x-2">
            {getProgressIcon()}
            <span className="text-sm text-dark-300">{downloadProgress.message}</span>
          </div>
          
          {downloadProgress.status !== 'completed' && downloadProgress.status !== 'error' && (
            <div className="mt-2 w-full bg-dark-700 rounded-full h-1">
              <div className="bg-blue-500 h-1 rounded-full animate-pulse" style={{ width: '60%' }}></div>
            </div>
          )}
        </div>
      )}

      {/* Format Selection Dropdown */}
      {showFormats && !isDownloading && (
        <div className="absolute top-full mt-2 left-0 bg-dark-800 border border-dark-600 rounded-lg shadow-lg z-50 min-w-64">
          <div className="p-3 border-b border-dark-600">
            <h3 className="font-medium text-white">Download ESG Report</h3>
            <p className="text-sm text-dark-400">{companyName} ({ticker})</p>
          </div>
          
          <div className="p-2">
            {availableFormats.map((format) => (
              <button
                key={format.value}
                onClick={() => handleDownload(format.value)}
                className="w-full flex items-center space-x-3 p-3 hover:bg-dark-700 rounded-lg transition-colors group"
              >
                <span className="text-lg">{format.icon}</span>
                <div className="flex-1 text-left">
                  <div className="font-medium text-white group-hover:text-blue-400">
                    {format.label}
                  </div>
                  <div className="text-sm text-dark-400">
                    {format.description}
                  </div>
                </div>
                {getFormatIcon(format.value)}
              </button>
            ))}
          </div>
          
          <div className="p-3 border-t border-dark-600 bg-dark-800/50">
            <p className="text-xs text-dark-500">
              Reports include ESG scores, AI insights, news analysis, and benchmarks
            </p>
          </div>
        </div>
      )}

      {/* Click outside to close */}
      {showFormats && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setShowFormats(false)}
        />
      )}

      {/* Last Download Info */}
      {lastDownload && !isDownloading && (
        <div className="mt-2 text-xs text-dark-500">
          Last downloaded: {lastDownload.filename}
        </div>
      )}
    </div>
  );
};

export default ESGReportDownload;