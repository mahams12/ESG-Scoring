import { apiService } from './api';

export const reportsService = {
  // Generate report
  generateReport: async (reportType, filters = {}) => {
    try {
      const result = await apiService.post('/api/reports/generate', {
        type: reportType,
        filters
      });
      return {
        success: true,
        data: result.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Report generation failed'
      };
    }
  },

  // Get reports list
  getReports: async (filters = {}) => {
    try {
      const result = await apiService.get('/api/reports', { params: filters });
      return {
        success: true,
        data: result.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch reports'
      };
    }
  },

  // Download report
  downloadReport: async (reportId, format = 'pdf') => {
    try {
      const result = await apiService.get(`/api/reports/${reportId}/download?format=${format}`, {
        responseType: 'blob'
      });
      return {
        success: true,
        data: result.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Download failed'
      };
    }
  },

  // Get report analytics
  getReportAnalytics: async (dateRange = '30d') => {
    try {
      const result = await apiService.get(`/api/reports/analytics?range=${dateRange}`);
      return {
        success: true,
        data: result.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch analytics'
      };
    }
  },

  // Mock data for development
  getMockFinancialData: () => {
    return {
      income: [15000, 16000, 17500, 18000, 19750, 19750, 18500, 17000, 16500, 18000, 19000, 20000],
      expenses: [12000, 13000, 13650, 14000, 13650, 13650, 14500, 15000, 14000, 13500, 13000, 12500],
      profit: [3000, 3000, 3850, 4000, 6100, 6100, 4000, 2000, 2500, 4500, 6000, 7500],
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    };
  },

  getMockExpenseBreakdown: () => {
    return [
      { category: 'Marketing', amount: 2500, percentage: 17.8, color: 'bg-red-500' },
      { category: 'Operations', amount: 2950, percentage: 21.0, color: 'bg-orange-500' },
      { category: 'R&D', amount: 1200, percentage: 8.5, color: 'bg-yellow-500' },
      { category: 'Sales', amount: 1650, percentage: 11.8, color: 'bg-green-500' },
      { category: 'Admin', amount: 2025, percentage: 14.4, color: 'bg-blue-500' },
      { category: 'Other', amount: 1500, percentage: 10.7, color: 'bg-purple-500' },
    ];
  }
};

export default reportsService;
