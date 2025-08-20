import { ESG_SCORE_RANGES } from './constants';

export const formatESGScore = (score) => {
  if (typeof score !== 'number' || isNaN(score)) return 'N/A';
  return score.toFixed(1);
};

export const getESGGrade = (score) => {
  if (typeof score !== 'number' || isNaN(score)) return 'N/A';
  
  for (const [key, range] of Object.entries(ESG_SCORE_RANGES)) {
    if (score >= range.min && score <= range.max) {
      return range.label;
    }
  }
  return 'N/A';
};

export const getESGScoreColor = (score) => {
  if (typeof score !== 'number' || isNaN(score)) return 'text-dark-400';
  
  for (const [key, range] of Object.entries(ESG_SCORE_RANGES)) {
    if (score >= range.min && score <= range.max) {
      return range.color;
    }
  }
  return 'text-dark-400';
};

export const formatMarketCap = (value) => {
  if (typeof value !== 'number' || isNaN(value)) return 'N/A';
  
  if (value >= 1e12) return `${(value / 1e12).toFixed(1)}T`;
  if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`;
  if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
  return `${value.toLocaleString()}`;
};

export const formatEmployeeCount = (count) => {
  if (typeof count !== 'number' || isNaN(count)) return 'N/A';
  
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
  if (count >= 1000) return `${(count / 1000).toFixed(0)}K`;
  return count.toLocaleString();
};

export const formatRiskLevel = (riskLevel) => {
  if (!riskLevel) return 'Unknown';
  return riskLevel.split('-').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
  ).join('-');
};

export const formatChangePercentage = (current, previous) => {
  if (typeof current !== 'number' || typeof previous !== 'number') return 'N/A';
  if (previous === 0) return 'N/A';
  
  const change = ((current - previous) / previous) * 100;
  const sign = change >= 0 ? '+' : '';
  return `${sign}${change.toFixed(1)}%`;
};

export const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'Unknown';
  
  const date = new Date(timestamp);
  const now = new Date();
  const diffInMinutes = Math.floor((now - date) / (1000 * 60));
  
  if (diffInMinutes < 1) return 'Just now';
  if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;
  if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} hours ago`;
  if (diffInMinutes < 10080) return `${Math.floor(diffInMinutes / 1440)} days ago`;
  
  return date.toLocaleDateString();
};
