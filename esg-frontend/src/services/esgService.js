import { apiService } from './api';

export const esgService = {
  // Validate if company exists and is publicly traded
  validateCompany: async (ticker) => {
    try {
      const result = await apiService.validateCompany(ticker);
      return {
        success: true,
        data: result
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Company validation failed'
      };
    }
  },

  // Perform comprehensive ESG analysis
  analyzeCompany: async (ticker) => {
    try {
      const result = await apiService.analyzeCompany(ticker);
      return {
        success: true,
        data: result
      };
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'ESG analysis failed';
      
      // Handle specific error cases
      if (error.response?.status === 404) {
        return {
          success: false,
          error: 'Company not found or not publicly traded'
        };
      } else if (error.response?.status === 429) {
        return {
          success: false,
          error: 'Too many requests. Please try again later.'
        };
      } else if (error.response?.status >= 500) {
        return {
          success: false,
          error: 'Server error. Please try again later.'
        };
      }
      
      return {
        success: false,
        error: errorMessage
      };
    }
  },

  // Get latest analysis for a company
  getLatestAnalysis: async (ticker) => {
    try {
      const result = await apiService.getLatestAnalysis(ticker);
      return {
        success: true,
        data: result
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch analysis'
      };
    }
  },

  // Get company profile information
  getCompanyProfile: async (ticker) => {
    try {
      const result = await apiService.getCompanyProfile(ticker);
      return {
        success: true,
        data: result
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch company profile'
      };
    }
  },

  // Get benchmark comparison data
  getBenchmarkData: async (ticker, industry) => {
    try {
      const result = await apiService.getBenchmarkData(ticker, industry);
      return {
        success: true,
        data: result
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch benchmark data'
      };
    }
  },

  // Calculate ESG score color based on value
  getScoreColor: (score) => {
    if (score >= 85) return 'text-success-500';
    if (score >= 70) return 'text-success-600';
    if (score >= 50) return 'text-warning-500';
    return 'text-danger-500';
  },

  // Get ESG score grade
  getScoreGrade: (score) => {
    if (score >= 85) return 'A';
    if (score >= 75) return 'B';
    if (score >= 65) return 'C';
    if (score >= 50) return 'D';
    return 'F';
  },

  // Get risk level color
  getRiskColor: (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low':
        return 'text-success-500';
      case 'low-medium':
      case 'medium':
        return 'text-warning-500';
      case 'medium-high':
      case 'high':
        return 'text-danger-500';
      default:
        return 'text-dark-400';
    }
  },

  // Format ESG score for display
  formatScore: (score) => {
    if (typeof score !== 'number') return 'N/A';
    return score.toFixed(1);
  },

  // Mock data for development
  getMockAnalysis: (ticker) => {
    return {
      company: {
        ticker: ticker.toUpperCase(),
        name: `${ticker.toUpperCase()} Company`,
        sector: 'Technology',
        industry: 'Software',
        marketCap: 2500000000000,
        employees: 150000,
        founded: 1976,
        headquarters: 'Cupertino, CA'
      },
      esgScores: {
        environmental: 88.5,
        social: 82.1,
        governance: 84.8,
        overall: 85.1
      },
      riskAssessment: {
        level: 'Low-Medium',
        factors: [
          'Supply chain sustainability',
          'Data privacy concerns',
          'Regulatory compliance'
        ],
        opportunities: [
          'Renewable energy expansion',
          'ESG reporting improvement',
          'Stakeholder engagement'
        ]
      },
      aiAnalysis: {
        recommendation: 'BUY',
        confidence: 85,
        insights: 'Strong ESG profile with leadership in environmental initiatives. Company demonstrates commitment to sustainability with clear targets and transparent reporting.',
        keyStrengths: [
          'Carbon neutral operations',
          'Strong governance structure',
          'Employee diversity programs'
        ],
        areasForImprovement: [
          'Supply chain transparency',
          'Community engagement',
          'Water usage reduction'
        ]
      },
      benchmarkData: {
        industryAverage: 72.3,
        percentileRank: 92,
        peerComparison: [
          { name: 'Peer 1', score: 78.5 },
          { name: 'Peer 2', score: 81.2 },
          { name: 'Peer 3', score: 75.8 }
        ]
      },
      timestamp: new Date().toISOString(),
      dataFreshness: 'Real-time'
    };
  }
};

export default esgService;