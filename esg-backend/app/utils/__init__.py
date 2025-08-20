# app/utils/__init__.py
"""
Utility modules for ESG Investment Research System
"""

from .helpers import generate_request_id, validate_ticker_format
from .constants import FEATURE_FLAGS

__all__ = [
    "generate_request_id",
    "validate_ticker_format", 
    "FEATURE_FLAGS"
]

# app/utils/helpers.py
"""
Helper functions for ESG Investment Research System
"""

import uuid
import re
from typing import Optional


def generate_request_id() -> str:
    """Generate a unique request ID"""
    return str(uuid.uuid4())


def validate_ticker_format(ticker: str) -> bool:
    """Validate ticker symbol format"""
    if not ticker:
        return False
    
    # Basic validation: 1-10 alphanumeric characters
    pattern = r'^[A-Z0-9]{1,10}$'
    return bool(re.match(pattern, ticker.upper()))


def sanitize_company_name(name: str) -> str:
    """Sanitize company name for search"""
    if not name:
        return ""
    
    # Remove special characters and normalize
    sanitized = re.sub(r'[^\w\s]', '', name)
    return sanitized.strip()


def calculate_percentage_change(old_value: float, new_value: float) -> Optional[float]:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return None
    
    return ((new_value - old_value) / old_value) * 100


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency"""
    if currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


# app/utils/constants.py
"""
Constants for ESG Investment Research System
"""

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_AI_ANALYSIS": True,
    "ENABLE_NEWS_ANALYSIS": True,
    "ENABLE_PEER_BENCHMARKING": True,
    "ENABLE_BENCHMARK_TRENDS": True,
    "ENABLE_WEB_SCRAPING": True,
    "ENABLE_CACHING": True,
    "ENABLE_BACKGROUND_TASKS": True
}

# ESG Rating mappings
ESG_GRADE_MAPPING = {
    "AAA": {"min_score": 90, "description": "Leader"},
    "AA": {"min_score": 80, "description": "Leader"},
    "A": {"min_score": 70, "description": "Average"},
    "BBB": {"min_score": 60, "description": "Average"},
    "BB": {"min_score": 50, "description": "Average"},
    "B": {"min_score": 40, "description": "Laggard"},
    "CCC": {"min_score": 0, "description": "Laggard"}
}

# Default user agents for web scraping
DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

# API rate limits
DEFAULT_RATE_LIMITS = {
    "requests_per_minute": 100,
    "requests_per_hour": 1000,
    "burst_limit": 10
}

# Cache TTL values (in seconds)
CACHE_TTL = {
    "company_validation": 3600,  # 1 hour
    "financial_data": 900,       # 15 minutes
    "esg_ratings": 1800,         # 30 minutes
    "news_data": 600,            # 10 minutes
    "analysis_results": 7200     # 2 hours
}

# Data source priorities
DATA_SOURCE_PRIORITIES = {
    "sustainalytics": 5,
    "msci_esg": 4,
    "cdp": 4,
    "esg_enterprise": 3,
    "epa_violations": 5,
    "osha_data": 5,
    "financial_modeling_prep": 5,
    "alpha_vantage": 4,
    "yahoo_finance": 3
}

# Investment recommendation thresholds
INVESTMENT_THRESHOLDS = {
    "STRONG_BUY": 85,
    "BUY": 75,
    "HOLD": 60,
    "SELL": 45,
    "STRONG_SELL": 0
}

# Risk level thresholds
RISK_LEVEL_THRESHOLDS = {
    "LOW": 80,
    "LOW_MEDIUM": 70,
    "MEDIUM": 60,
    "MEDIUM_HIGH": 50,
    "HIGH": 0
}

# ESG analysis depth configurations
ANALYSIS_DEPTH_CONFIG = {
    "basic": {
        "include_ai_insights": False,
        "include_benchmarks": False,
        "include_news": False,
        "max_data_sources": 2
    },
    "standard": {
        "include_ai_insights": True,
        "include_benchmarks": True,
        "include_news": False,
        "max_data_sources": 4
    },
    "comprehensive": {
        "include_ai_insights": True,
        "include_benchmarks": True,
        "include_news": True,
        "max_data_sources": 6
    }
}

# app/utils/exceptions.py
"""
Custom exceptions for ESG Investment Research System
"""


class ESGAnalysisError(Exception):
    """Base exception for ESG analysis errors"""
    pass


class CompanyNotFoundError(ESGAnalysisError):
    """Raised when company cannot be found or validated"""
    pass


class DataUnavailableError(ESGAnalysisError):
    """Raised when required data is unavailable"""
    pass


class RateLimitExceededError(ESGAnalysisError):
    """Raised when API rate limit is exceeded"""
    pass


class ExternalAPIError(ESGAnalysisError):
    """Raised when external API calls fail"""
    pass


class ValidationError(ESGAnalysisError):
    """Raised when input validation fails"""
    pass


class CacheError(ESGAnalysisError):
    """Raised when cache operations fail"""
    pass


class ScrapingError(ESGAnalysisError):
    """Raised when web scraping fails"""
    pass


class AIAnalysisError(ESGAnalysisError):
    """Raised when AI analysis fails"""
    pass