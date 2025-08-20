// src/services/reportDownloadService.js
import api from './api';

export const reportDownloadService = {
  /**
   * Download ESG report for a company
   * @param {string} ticker - Company ticker symbol
   * @param {string} format - Report format (pdf, excel, csv)
   * @param {Object} options - Additional options
   */
  async downloadESGReport(ticker, format = 'pdf', options = {}) {
    try {
      const params = new URLSearchParams({
        format,
        include_charts: options.includeCharts || true,
        include_benchmarks: options.includeBenchmarks || true,
        include_news: options.includeNews || true,
        include_raw_data: options.includeRawData || false
      });

      const response = await api.get(`/analysis/${ticker}/download?${params}`, {
        responseType: 'blob',
        timeout: 30000 // 30 second timeout for file generation
      });

      // Create download link
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Set filename based on format and ticker
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `${ticker}_ESG_Report_${timestamp}.${format === 'excel' ? 'xlsx' : format}`;
      link.download = filename;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      return {
        success: true,
        filename,
        message: `ESG report downloaded successfully`
      };
    } catch (error) {
      console.error('Report download failed:', error);
      
      let message = 'Failed to download report';
      if (error.response?.status === 404) {
        message = 'Company ESG data not found';
      } else if (error.response?.status === 429) {
        message = 'Too many requests. Please try again later.';
      } else if (error.code === 'ECONNABORTED') {
        message = 'Download timeout. Report generation is taking longer than expected.';
      }

      return {
        success: false,
        error: message
      };
    }
  },

  /**
   * Get available report formats
   */
  getAvailableFormats() {
    return [
      { value: 'pdf', label: 'PDF Report', icon: '📄', description: 'Comprehensive visual report' },
      { value: 'excel', label: 'Excel Spreadsheet', icon: '📊', description: 'Data for analysis' },
      { value: 'csv', label: 'CSV Data', icon: '📋', description: 'Raw data export' }
    ];
  },

  /**
   * Generate report preview URL
   */
  getPreviewUrl(ticker) {
    return `/analysis/${ticker}/preview`;
  },

  /**
   * Get report preview data
   */
  async getReportPreview(ticker) {
    try {
      const response = await api.get(`/analysis/${ticker}/preview`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Preview fetch failed:', error);
      return {
        success: false,
        error: 'Failed to fetch report preview'
      };
    }
  }
};