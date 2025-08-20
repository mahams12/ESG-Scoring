export const ESG_SCORE_RANGES = {
    EXCELLENT: { min: 85, max: 100, label: 'A', color: 'text-success-500' },
    GOOD: { min: 70, max: 84, label: 'B', color: 'text-success-600' },
    AVERAGE: { min: 50, max: 69, label: 'C', color: 'text-warning-500' },
    POOR: { min: 0, max: 49, label: 'D', color: 'text-danger-500' }
  };
  
  export const RISK_LEVELS = {
    LOW: { label: 'Low', color: 'text-success-500', bg: 'bg-success-500' },
    LOW_MEDIUM: { label: 'Low-Medium', color: 'text-warning-500', bg: 'bg-warning-500' },
    MEDIUM: { label: 'Medium', color: 'text-warning-500', bg: 'bg-warning-500' },
    MEDIUM_HIGH: { label: 'Medium-High', color: 'text-danger-500', bg: 'bg-danger-500' },
    HIGH: { label: 'High', color: 'text-danger-500', bg: 'bg-danger-500' }
  };
  
  export const SECTORS = [
    'Technology',
    'Healthcare',
    'Financial Services',
    'Energy',
    'Consumer Discretionary',
    'Consumer Staples',
    'Industrials',
    'Materials',
    'Utilities',
    'Real Estate',
    'Telecommunications'
  ];
  
  export const API_ENDPOINTS = {
    VALIDATE_COMPANY: '/api/company/{ticker}/exists',
    ANALYZE_COMPANY: '/api/analyze/{ticker}',
    LATEST_ANALYSIS: '/api/analysis/{ticker}/latest',
    COMPANY_PROFILE: '/api/company/{ticker}/profile',
    BENCHMARK_DATA: '/api/benchmark/{ticker}',
    GENERATE_REPORT: '/api/reports/generate',
    HEALTH_CHECK: '/api/health'
  };
  
  export const NOTIFICATION_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info'
  };
  
  export const CHART_COLORS = {
    PRIMARY: '#3b82f6',
    SUCCESS: '#22c55e',
    WARNING: '#eab308',
    DANGER: '#ef4444',
    PURPLE: '#8b5cf6',
    ORANGE: '#f97316'
  };