import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // Handle common errors
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login or refresh token
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    } else if (error.response?.status === 404) {
      // Not found
      console.error('Resource not found');
    } else if (error.response?.status >= 500) {
      // Server error
      console.error('Server error occurred');
    }
    
    return Promise.reject(error);
  }
);

// API methods
export const apiService = {
  // Company validation
  validateCompany: async (ticker) => {
    const response = await api.get(`/api/company/${ticker}/exists`);
    return response.data;
  },

  // ESG Analysis
  analyzeCompany: async (ticker) => {
    const response = await api.post(`/api/analyze/${ticker}`);
    return response.data;
  },

  getLatestAnalysis: async (ticker) => {
    const response = await api.get(`/api/analysis/${ticker}/latest`);
    return response.data;
  },

  // Company data
  getCompanyProfile: async (ticker) => {
    const response = await api.get(`/api/company/${ticker}/profile`);
    return response.data;
  },

  // Benchmarking
  getBenchmarkData: async (ticker, industry) => {
    const response = await api.get(`/api/benchmark/${ticker}?industry=${industry}`);
    return response.data;
  },

  // Reports
  generateReport: async (reportType, filters) => {
    const response = await api.post('/api/reports/generate', {
      type: reportType,
      filters
    });
    return response.data;
  },

  getReports: async (filters = {}) => {
    const response = await api.get('/api/reports', { params: filters });
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },

  // Generic methods
  get: (url, config) => api.get(url, config),
  post: (url, data, config) => api.post(url, data, config),
  put: (url, data, config) => api.put(url, data, config),
  delete: (url, config) => api.delete(url, config),
};

export default api;