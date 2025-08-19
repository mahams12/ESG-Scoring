"""
Constants and configuration values for ESG Investment Research System
"""

from enum import Enum
from typing import Dict, List, Tuple


# ESG Score Ranges and Classifications
ESG_SCORE_RANGES = {
    "EXCELLENT": (90, 100),
    "GOOD": (75, 89),
    "AVERAGE": (50, 74),
    "BELOW_AVERAGE": (25, 49),
    "POOR": (0, 24)
}

# Investment Recommendation Mapping
INVESTMENT_RECOMMENDATION_MAPPING = {
    "STRONG_BUY": {"min_score": 85, "description": "Exceptional ESG performance"},
    "BUY": {"min_score": 75, "description": "Strong ESG performance"},
    "HOLD": {"min_score": 60, "description": "Adequate ESG performance"},
    "SELL": {"min_score": 45, "description": "Weak ESG performance"},
    "STRONG_SELL": {"min_score": 0, "description": "Poor ESG performance"}
}

# Risk Level Mapping
RISK_LEVEL_MAPPING = {
    "LOW": {"max_score": 80, "color": "#28a745", "description": "Minimal ESG risks"},
    "LOW_MEDIUM": {"max_score": 70, "color": "#6c757d", "description": "Limited ESG risks"},
    "MEDIUM": {"max_score": 60, "color": "#ffc107", "description": "Moderate ESG risks"},
    "MEDIUM_HIGH": {"max_score": 50, "color": "#fd7e14", "description": "Elevated ESG risks"},
    "HIGH": {"max_score": 0, "color": "#dc3545", "description": "Significant ESG risks"}
}

# Data Quality Thresholds
DATA_QUALITY_THRESHOLDS = {
    "EXCELLENT": 0.9,
    "GOOD": 0.7,
    "FAIR": 0.5,
    "POOR": 0.3,
    "INSUFFICIENT": 0.0
}

# Sector Mapping and Classifications
SECTOR_MAPPING = {
    "TECHNOLOGY": {
        "keywords": ["software", "hardware", "tech", "internet", "digital"],
        "esg_focus": ["data_privacy", "cybersecurity", "electronic_waste"],
        "typical_risks": ["data_breaches", "labor_practices", "supply_chain"]
    },
    "HEALTHCARE": {
        "keywords": ["pharmaceutical", "biotech", "medical", "health"],
        "esg_focus": ["product_safety", "access_to_medicine", "clinical_trials"],
        "typical_risks": ["drug_pricing", "clinical_trial_ethics", "product_liability"]
    },
    "FINANCIALS": {
        "keywords": ["bank", "insurance", "investment", "finance"],
        "esg_focus": ["responsible_lending", "financial_inclusion", "governance"],
        "typical_risks": ["lending_practices", "executive_compensation", "risk_management"]
    },
    "ENERGY": {
        "keywords": ["oil", "gas", "renewable", "utility", "power"],
        "esg_focus": ["carbon_emissions", "renewable_transition", "environmental_impact"],
        "typical_risks": ["climate_change", "environmental_violations", "stranded_assets"]
    },
    "CONSUMER_DISCRETIONARY": {
        "keywords": ["retail", "automotive", "entertainment", "luxury"],
        "esg_focus": ["supply_chain", "labor_practices", "product_quality"],
        "typical_risks": ["labor_violations", "supply_chain_disruption", "brand_reputation"]
    },
    "CONSUMER_STAPLES": {
        "keywords": ["food", "beverage", "household", "personal_care"],
        "esg_focus": ["sustainable_sourcing", "nutrition", "packaging"],
        "typical_risks": ["supply_chain_sustainability", "health_claims", "water_usage"]
    },
    "INDUSTRIALS": {
        "keywords": ["manufacturing", "aerospace", "defense", "construction"],
        "esg_focus": ["workplace_safety", "environmental_compliance", "innovation"],
        "typical_risks": ["workplace_accidents", "environmental_violations", "supply_chain"]
    },
    "MATERIALS": {
        "keywords": ["mining", "chemicals", "metals", "paper"],
        "esg_focus": ["environmental_impact", "resource_efficiency", "waste_management"],
        "typical_risks": ["environmental_damage", "worker_safety", "community_impact"]
    },
    "UTILITIES": {
        "keywords": ["electric", "water", "gas", "renewable"],
        "esg_focus": ["grid_modernization", "renewable_energy", "rate_affordability"],
        "typical_risks": ["infrastructure_aging", "regulatory_changes", "environmental_compliance"]
    },
    "REAL_ESTATE": {
        "keywords": ["reit", "property", "development", "real_estate"],
        "esg_focus": ["energy_efficiency", "sustainable_building", "community_development"],
        "typical_risks": ["climate_resilience", "tenant_relations", "urban_planning"]
    },
    "COMMUNICATION_SERVICES": {
        "keywords": ["telecom", "media", "entertainment", "social_media"],
        "esg_focus": ["content_responsibility", "data_privacy", "digital_divide"],
        "typical_risks": ["content_moderation", "data_breaches", "regulatory_scrutiny"]
    }
}

# Market Cap Categories (in USD)
MARKET_CAP_CATEGORIES = {
    "MEGA_CAP": {"min": 200_000_000_000, "description": "Mega-cap (>$200B)"},
    "LARGE_CAP": {"min": 10_000_000_000, "description": "Large-cap ($10B-$200B)"},
    "MID_CAP": {"min": 2_000_000_000, "description": "Mid-cap ($2B-$10B)"},
    "SMALL_CAP": {"min": 300_000_000, "description": "Small-cap ($300M-$2B)"},
    "MICRO_CAP": {"min": 50_000_000, "description": "Micro-cap ($50M-$300M)"},
    "NANO_CAP": {"min": 0, "description": "Nano-cap (<$50M)"}
}

# API Timeout Settings (in seconds)
API_TIMEOUT_SETTINGS = {
    "FINANCIAL_MODELING_PREP": 30,
    "YAHOO_FINANCE": 15,
    "IEX_CLOUD": 20,
    "OPENAI": 60,
    "NEWS_API": 15,
    "WEB_SCRAPING": 30,
    "DATABASE": 10
}

# Cache TTL Settings (in seconds)
CACHE_TTL_SETTINGS = {
    "COMPANY_VALIDATION": 3600,      # 1 hour
    "FINANCIAL_DATA": 900,           # 15 minutes
    "ESG_RATINGS": 1800,             # 30 minutes
    "NEWS_DATA": 600,                # 10 minutes
    "ANALYSIS_RESULTS": 7200,        # 2 hours
    "BENCHMARK_DATA": 86400,         # 24 hours
    "MARKET_DATA": 300               # 5 minutes
}

# ESG Metrics Categories
ESG_METRICS_CATEGORIES = {
    "ENVIRONMENTAL": [
        "carbon_emissions",
        "renewable_energy_percentage",
        "water_usage",
        "waste_generated",
        "environmental_violations",
        "biodiversity_impact_score",
        "energy_consumption"
    ],
    "SOCIAL": [
        "employee_satisfaction_score",
        "diversity_percentage",
        "workplace_safety_incidents",
        "community_investment",
        "customer_satisfaction_score",
        "data_privacy_score",
        "human_rights_score"
    ],
    "GOVERNANCE": [
        "board_independence_percentage",
        "executive_compensation_ratio",
        "audit_quality_score",
        "transparency_score",
        "ethics_violations",
        "cybersecurity_score",
        "anti_corruption_score"
    ]
}

# Data Source Reliability Scores
DATA_SOURCE_RELIABILITY = {
    "FINANCIAL_MODELING_PREP": 0.9,
    "YAHOO_FINANCE": 0.85,
    "IEX_CLOUD": 0.8,
    "SUSTAINALYTICS": 0.95,
    "CDP": 0.9,
    "MSCI_ESG": 0.95,
    "EPA_VIOLATIONS": 0.95,
    "OSHA_DATA": 0.9,
    "NEWS_API": 0.7,
    "REDDIT": 0.5,
    "WEB_SCRAPING": 0.6
}

# Analysis Prompt Templates
AI_PROMPT_TEMPLATES = {
    "BASIC_ANALYSIS": """
    Analyze the ESG performance of {company_name} ({ticker}) in the {sector} sector.
    Provide scores (0-100) for Environmental, Social, and Governance dimensions.
    """,
    
    "COMPREHENSIVE_ANALYSIS": """
    Perform a comprehensive ESG analysis of {company_name} ({ticker}) considering:
    - Financial performance and context
    - Industry benchmarks and peer comparison
    - Recent news and sentiment analysis
    - Regulatory compliance and violations
    - Long-term sustainability trends
    """,
    
    "PEER_COMPARISON": """
    Compare {company_name} ({ticker}) against industry peers:
    {peer_companies}
    Focus on relative ESG performance and competitive positioning.
    """,
    
    "TREND_ANALYSIS": """
    Analyze ESG trends for {company_name} ({ticker}) over the past {time_period}.
    Identify improvement areas and forecast future performance.
    """
}

# HTTP Status Code Mappings
HTTP_STATUS_MAPPINGS = {
    "COMPANY_NOT_FOUND": 404,
    "VALIDATION_ERROR": 422,
    "RATE_LIMIT_EXCEEDED": 429,
    "INTERNAL_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503,
    "TIMEOUT": 504
}

# Regular Expressions for Data Validation
VALIDATION_PATTERNS = {
    "TICKER": r"^[A-Z0-9.-]{1,10}$",
    "EMAIL": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "URL": r"^https?://[^\s/$.?#].[^\s]*$",
    "PHONE": r"^\+?1?[0-9]{10,15}$",
    "DATE_ISO": r"^\d{4}-\d{2}-\d{2}$",
    "CURRENCY": r"^\$?[0-9,]+\.?[0-9]*$"
}

# Default Configuration Values
DEFAULT_VALUES = {
    "ESG_SCORE": 50.0,
    "CONFIDENCE_LEVEL": 0.5,
    "ANALYSIS_TIMEOUT": 60,
    "MAX_RETRIES": 3,
    "BATCH_SIZE": 10,
    "PAGE_SIZE": 20,
    "MAX_PAGE_SIZE": 100
}

# Error Message Templates
ERROR_MESSAGES = {
    "COMPANY_NOT_FOUND": "Company '{ticker}' does not exist or is not publicly traded. Please check the ticker symbol and try again.",
    "INVALID_TICKER": "Invalid ticker format. Ticker symbols should be 1-10 alphanumeric characters.",
    "DATA_UNAVAILABLE": "ESG data is not available for '{ticker}' at this time. Please try again later.",
    "API_LIMIT_EXCEEDED": "API request limit exceeded. Please try again later or upgrade your plan.",
    "TIMEOUT": "Request timed out. The analysis is taking longer than expected. Please try again.",
    "INSUFFICIENT_DATA": "Insufficient data available for comprehensive ESG analysis of '{ticker}'.",
    "ANALYSIS_FAILED": "ESG analysis failed due to technical issues. Please try again later."
}

# Success Message Templates
SUCCESS_MESSAGES = {
    "COMPANY_VALIDATED": "Company validation completed successfully.",
    "ANALYSIS_COMPLETED": "ESG analysis completed successfully.",
    "DATA_UPDATED": "Company data updated successfully.",
    "CACHE_REFRESHED": "Data cache refreshed successfully."
}

# Feature Flags
FEATURE_FLAGS = {
    "ENABLE_AI_ANALYSIS": True,
    "ENABLE_WEB_SCRAPING": True,
    "ENABLE_CACHING": True,
    "ENABLE_BACKGROUND_TASKS": True,
    "ENABLE_RATE_LIMITING": True,
    "ENABLE_DETAILED_LOGGING": True,
    "ENABLE_PEER_COMPARISON": True,
    "ENABLE_NEWS_ANALYSIS": True,
    "ENABLE_REAL_TIME_UPDATES": True,
    "ENABLE_BENCHMARK_TRENDS": True
}

# Logging Configuration
LOGGING_CONFIG = {
    "LEVELS": {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50
    },
    "FORMATS": {
        "DETAILED": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        "SIMPLE": "{time:HH:mm:ss} | {level} | {message}",
        "JSON": '{"timestamp": "{time:YYYY-MM-DD HH:mm:ss}", "level": "{level}", "message": "{message}"}'
    },
    "FILES": {
        "MAIN": "logs/esg_system.log",
        "ERROR": "logs/errors.log",
        "ACCESS": "logs/access.log",
        "ANALYSIS": "logs/analysis.log"
    }
}

# Rate Limiting Configuration
RATE_LIMITS = {
    "API_ENDPOINTS": {
        "COMPANY_VALIDATION": {"per_minute": 60, "per_hour": 500},
        "ESG_ANALYSIS": {"per_minute": 30, "per_hour": 200},
        "BULK_OPERATIONS": {"per_minute": 5, "per_hour": 50},
        "HEALTH_CHECK": {"per_minute": 120, "per_hour": 1000}
    },
    "EXTERNAL_APIS": {
        "FINANCIAL_MODELING_PREP": {"per_minute": 300, "per_hour": 5000},
        "OPENAI": {"per_minute": 60, "per_hour": 1000},
        "NEWS_API": {"per_minute": 100, "per_hour": 1000},
        "WEB_SCRAPING": {"per_minute": 30, "per_hour": 500}
    }
}

# Performance Benchmarks
PERFORMANCE_BENCHMARKS = {
    "COMPANY_VALIDATION": {
        "TARGET_RESPONSE_TIME": 2.0,  # seconds
        "MAX_RESPONSE_TIME": 5.0,
        "SUCCESS_RATE_TARGET": 0.99
    },
    "ESG_ANALYSIS": {
        "TARGET_RESPONSE_TIME": 15.0,  # seconds
        "MAX_RESPONSE_TIME": 45.0,
        "SUCCESS_RATE_TARGET": 0.95
    },
    "DATA_COLLECTION": {
        "TARGET_RESPONSE_TIME": 5.0,  # seconds
        "MAX_RESPONSE_TIME": 15.0,
        "SUCCESS_RATE_TARGET": 0.98
    },
    "AI_ANALYSIS": {
        "TARGET_RESPONSE_TIME": 10.0,  # seconds
        "MAX_RESPONSE_TIME": 30.0,
        "SUCCESS_RATE_TARGET": 0.95
    }
}

# Database Configuration
DATABASE_CONFIG = {
    "INDEXES": {
        "COMPANIES": [
            {"fields": [("ticker", 1)], "unique": True},
            {"fields": [("sector", 1), ("industry", 1)]},
            {"fields": [("market_cap", -1)]},
            {"fields": [("last_validated", -1)]}
        ],
        "ESG_SCORES": [
            {"fields": [("ticker", 1), ("timestamp", -1)]},
            {"fields": [("overall_score", -1)]},
            {"fields": [("expires_at", 1)], "expire_after_seconds": 0}
        ],
        "AI_ANALYSIS": [
            {"fields": [("ticker", 1), ("analysis_timestamp", -1)]},
            {"fields": [("ai_confidence", -1)]},
            {"fields": [("expires_at", 1)], "expire_after_seconds": 0}
        ]
    },
    "COLLECTION_SETTINGS": {
        "WRITE_CONCERN": {"w": 1, "j": True},
        "READ_PREFERENCE": "primaryPreferred",
        "MAX_POOL_SIZE": 10,
        "MIN_POOL_SIZE": 1
    }
}

# Security Configuration
SECURITY_CONFIG = {
    "CORS": {
        "ALLOWED_ORIGINS": [
            "http://localhost:3000",
            "https://esg-research-frontend.com"
        ],
        "ALLOWED_METHODS": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "ALLOWED_HEADERS": ["Content-Type", "Authorization", "X-Requested-With"]
    },
    "API_KEY_VALIDATION": {
        "MIN_LENGTH": 32,
        "REQUIRED_ENTROPY": 5.0
    },
    "REQUEST_VALIDATION": {
        "MAX_REQUEST_SIZE": 10485760,  # 10MB
        "MAX_FIELD_LENGTH": 1000,
        "ALLOWED_CONTENT_TYPES": ["application/json", "text/plain"]
    }
}

# Monitoring and Alerting
MONITORING_CONFIG = {
    "HEALTH_CHECK_INTERVALS": {
        "DATABASE": 60,  # seconds
        "EXTERNAL_APIS": 300,  # seconds
        "SERVICES": 120,  # seconds
        "DISK_SPACE": 600  # seconds
    },
    "ALERT_THRESHOLDS": {
        "ERROR_RATE": 0.05,  # 5% error rate
        "RESPONSE_TIME": 10.0,  # seconds
        "MEMORY_USAGE": 0.85,  # 85% memory usage
        "DISK_USAGE": 0.90,  # 90% disk usage
        "CPU_USAGE": 0.80  # 80% CPU usage
    },
    "NOTIFICATION_CHANNELS": {
        "EMAIL": True,
        "SLACK": False,
        "WEBHOOK": False
    }
}

# AI Analysis Configuration
AI_CONFIG = {
    "MODELS": {
        "PRIMARY": "gpt-4",
        "FALLBACK": "gpt-3.5-turbo",
        "EMBEDDING": "text-embedding-ada-002"
    },
    "PARAMETERS": {
        "TEMPERATURE": 0.3,
        "MAX_TOKENS": 2000,
        "TOP_P": 0.9,
        "FREQUENCY_PENALTY": 0.0,
        "PRESENCE_PENALTY": 0.0
    },
    "CONFIDENCE_THRESHOLDS": {
        "HIGH": 0.8,
        "MEDIUM": 0.6,
        "LOW": 0.4,
        "MINIMUM": 0.2
    }
}

# File and Data Limits
DATA_LIMITS = {
    "MAX_COMPANIES_PER_BULK_REQUEST": 50,
    "MAX_ANALYSIS_HISTORY_DAYS": 365,
    "MAX_NEWS_ARTICLES_PER_COMPANY": 100,
    "MAX_PEER_COMPANIES": 20,
    "MAX_SEARCH_RESULTS": 100,
    "MAX_EXPORT_RECORDS": 1000
}

# Environment-specific Settings
ENVIRONMENT_CONFIG = {
    "DEVELOPMENT": {
        "DEBUG": True,
        "LOG_LEVEL": "DEBUG",
        "ENABLE_PROFILING": True,
        "CACHE_TTL_MULTIPLIER": 0.1
    },
    "STAGING": {
        "DEBUG": False,
        "LOG_LEVEL": "INFO",
        "ENABLE_PROFILING": False,
        "CACHE_TTL_MULTIPLIER": 0.5
    },
    "PRODUCTION": {
        "DEBUG": False,
        "LOG_LEVEL": "WARNING",
        "ENABLE_PROFILING": False,
        "CACHE_TTL_MULTIPLIER": 1.0
    }
}