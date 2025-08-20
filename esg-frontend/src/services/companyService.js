import { apiService } from './api';

export const companyService = {
  // Search companies
  searchCompanies: async (query) => {
    try {
      const result = await apiService.get(`/api/companies/search?q=${encodeURIComponent(query)}`);
      return {
        success: true,
        data: result.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Search failed'
      };
    }
  },

  // Get company details
  getCompanyDetails: async (ticker) => {
    try {
      const result = await apiService.get(`/api/companies/${ticker}`);
      return {
        success: true,
        data: result.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch company details'
      };
    }
  },

  // Validate company ticker
  validateTicker: async (ticker) => {
    try {
      const result = await apiService.get(`/api/companies/${ticker}/validate`);
      return {
        success: true,
        data: result.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Invalid ticker symbol'
      };
    }
  },

  // Mock search for development
  mockSearch: (query) => {
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

    return companies.filter(company =>
      company.name.toLowerCase().includes(query.toLowerCase()) ||
      company.ticker.toLowerCase().includes(query.toLowerCase())
    );
  }
};

export default companyService;
