export const validateTicker = (ticker) => {
    if (!ticker || typeof ticker !== 'string') {
      return { isValid: false, error: 'Ticker symbol is required' };
    }
    
    const cleanTicker = ticker.trim().toUpperCase();
    
    if (cleanTicker.length < 1 || cleanTicker.length > 5) {
      return { isValid: false, error: 'Ticker symbol must be 1-5 characters' };
    }
    
    if (!/^[A-Z]+$/.test(cleanTicker)) {
      return { isValid: false, error: 'Ticker symbol must contain only letters' };
    }
    
    return { isValid: true, ticker: cleanTicker };
  };
  
  export const validateCompanyName = (name) => {
    if (!name || typeof name !== 'string') {
      return { isValid: false, error: 'Company name is required' };
    }
    
    const cleanName = name.trim();
    
    if (cleanName.length < 2) {
      return { isValid: false, error: 'Company name must be at least 2 characters' };
    }
    
    if (cleanName.length > 100) {
      return { isValid: false, error: 'Company name must be less than 100 characters' };
    }
    
    return { isValid: true, name: cleanName };
  };
  
  export const validateESGScore = (score) => {
    if (typeof score !== 'number' || isNaN(score)) {
      return { isValid: false, error: 'ESG score must be a number' };
    }
    
    if (score < 0 || score > 100) {
      return { isValid: false, error: 'ESG score must be between 0 and 100' };
    }
    
    return { isValid: true, score };
  };
  
  export const validateEmail = (email) => {
    if (!email || typeof email !== 'string') {
      return { isValid: false, error: 'Email is required' };
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!emailRegex.test(email)) {
      return { isValid: false, error: 'Invalid email format' };
    }
    
    return { isValid: true, email: email.toLowerCase() };
  };
  
  export const validateDateRange = (startDate, endDate) => {
    if (!startDate || !endDate) {
      return { isValid: false, error: 'Both start and end dates are required' };
    }
    
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
      return { isValid: false, error: 'Invalid date format' };
    }
    
    if (start >= end) {
      return { isValid: false, error: 'Start date must be before end date' };
    }
    
    return { isValid: true, startDate: start, endDate: end };
  };
  