"""
Data models for ESG Investment Research System
"""

from .company import (
    Company,
    CompanyInfo,
    CompanyValidationResult,
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    FinancialMetrics,
    CompanyStatus,
    MarketCapCategory,
    Sector
)

from .esg_analysis import (
    ESGAnalysis,
    ESGScore,
    EnvironmentalMetrics,
    SocialMetrics,
    GovernanceMetrics,
    ESGAnalysisRequest,
    InvestmentRecommendation,
    RiskLevel,
    DataQuality,
    BenchmarkComparison,
    AIAnalysisInsight,
    NewsArticle,
    ESGControversy
)

from .responses import (
    BaseAPIResponse,
    CompanyValidationResponse,
    ESGAnalysisResponse,
    HealthCheckResponse,
    BulkAnalysisResponse,
    CompanySearchResponse,
    IndustryBenchmarkResponse,
    NewsAnalysisResponse,
    DataQualityResponse,
    APIErrorResponse,
    ProcessingMetadata,
    ResponseStatus,
    ErrorCode,
    APIError
)

__all__ = [
    # Company models
    "Company",
    "CompanyInfo", 
    "CompanyValidationResult",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "FinancialMetrics",
    "CompanyStatus",
    "MarketCapCategory",
    "Sector",
    
    # ESG Analysis models
    "ESGAnalysis",
    "ESGScore",
    "EnvironmentalMetrics",
    "SocialMetrics", 
    "GovernanceMetrics",
    "ESGAnalysisRequest",
    "InvestmentRecommendation",
    "RiskLevel",
    "DataQuality",
    "BenchmarkComparison",
    "AIAnalysisInsight",
    "NewsArticle",
    "ESGControversy",
    
    # Response models
    "BaseAPIResponse",
    "CompanyValidationResponse",
    "ESGAnalysisResponse",
    "HealthCheckResponse",
    "BulkAnalysisResponse",
    "CompanySearchResponse",
    "IndustryBenchmarkResponse",
    "NewsAnalysisResponse",
    "DataQualityResponse",
    "APIErrorResponse",
    "ProcessingMetadata",
    "ResponseStatus",
    "ErrorCode",
    "APIError"
]