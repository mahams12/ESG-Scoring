"""
API Response models for ESG Investment Research System
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

from .company import CompanyResponse, CompanyValidationResult
from .esg_analysis import ESGAnalysis, ESGResponse


class ResponseStatus(str, Enum):
    """API response status"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PARTIAL_SUCCESS = "partial_success"


class ErrorCode(str, Enum):
    """Error codes for API responses"""
    COMPANY_NOT_FOUND = "COMPANY_NOT_FOUND"
    INVALID_TICKER = "INVALID_TICKER"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    API_LIMIT_EXCEEDED = "API_LIMIT_EXCEEDED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class APIError(BaseModel):
    """API error details"""
    code: ErrorCode
    message: str
    details: Optional[str] = None
    field: Optional[str] = None
    suggestion: Optional[str] = None


class ProcessingMetadata(BaseModel):
    """Processing metadata for API responses"""
    processing_time_ms: float
    data_sources_used: List[str] = []
    cache_hit: bool = False
    ai_processing_time_ms: Optional[float] = None
    total_api_calls: int = 0
    data_freshness_seconds: Optional[int] = None
    analysis_version: str = "2.0"


class BaseAPIResponse(BaseModel):
    """Base API response model"""
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str = "Request processed successfully"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    errors: List[APIError] = []
    warnings: List[str] = []
    metadata: Optional[ProcessingMetadata] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CompanyValidationResponse(BaseAPIResponse):
    """Company validation API response"""
    data: Optional[CompanyValidationResult] = None
    
    @classmethod
    def company_not_found(cls, ticker: str, suggestion: Optional[str] = None):
        """Create response for company not found"""
        return cls(
            status=ResponseStatus.ERROR,
            message=f"Company '{ticker}' does not exist or is not publicly traded",
            errors=[APIError(
                code=ErrorCode.COMPANY_NOT_FOUND,
                message=f"No company found with ticker '{ticker}'",
                suggestion=suggestion or "Please verify the ticker symbol and try again"
            )]
        )
    
    @classmethod
    def validation_success(cls, validation_result: CompanyValidationResult, metadata: ProcessingMetadata):
        """Create successful validation response"""
        return cls(
            status=ResponseStatus.SUCCESS,
            message="Company validation completed successfully",
            data=validation_result,
            metadata=metadata
        )


class ESGAnalysisResponse(BaseAPIResponse):
    """ESG analysis API response"""
    data: Optional[ESGAnalysis] = None
    
    @classmethod
    def analysis_success(cls, analysis: ESGAnalysis, metadata: ProcessingMetadata):
        """Create successful analysis response"""
        return cls(
            status=ResponseStatus.SUCCESS,
            message="ESG analysis completed successfully",
            data=analysis,
            metadata=metadata
        )
    
    @classmethod
    def insufficient_data(cls, ticker: str, available_data: List[str]):
        """Create response for insufficient data"""
        return cls(
            status=ResponseStatus.WARNING,
            message=f"Limited ESG data available for {ticker}",
            warnings=[f"Analysis based on limited data sources: {', '.join(available_data)}"],
            errors=[APIError(
                code=ErrorCode.INSUFFICIENT_DATA,
                message="Some ESG metrics may be incomplete",
                suggestion="Analysis confidence may be lower due to limited data availability"
            )]
        )


class HealthCheckResponse(BaseAPIResponse):
    """Health check API response"""
    data: Dict[str, Any] = {}
    
    @classmethod
    def healthy(cls, services_status: Dict[str, bool]):
        """Create healthy response"""
        return cls(
            status=ResponseStatus.SUCCESS,
            message="All services are healthy",
            data={
                "services": services_status,
                "uptime": "healthy",
                "version": "2.0"
            }
        )
    
    @classmethod
    def unhealthy(cls, failed_services: List[str]):
        """Create unhealthy response"""
        return cls(
            status=ResponseStatus.ERROR,
            message="Some services are unavailable",
            data={
                "failed_services": failed_services,
                "status": "unhealthy"
            },
            errors=[APIError(
                code=ErrorCode.INTERNAL_ERROR,
                message=f"Services unavailable: {', '.join(failed_services)}"
            )]
        )


class BulkAnalysisResponse(BaseAPIResponse):
    """Bulk analysis API response"""
    data: Dict[str, Any] = {}
    
    @classmethod
    def bulk_success(
        cls, 
        results: List[ESGAnalysisResponse], 
        failed_tickers: List[str],
        metadata: ProcessingMetadata
    ):
        """Create bulk analysis response"""
        successful_results = [r for r in results if r.status == ResponseStatus.SUCCESS]
        
        status = ResponseStatus.SUCCESS
        if failed_tickers:
            status = ResponseStatus.PARTIAL_SUCCESS if successful_results else ResponseStatus.ERROR
        
        return cls(
            status=status,
            message=f"Bulk analysis completed: {len(successful_results)} successful, {len(failed_tickers)} failed",
            data={
                "total_requested": len(results) + len(failed_tickers),
                "successful_count": len(successful_results),
                "failed_count": len(failed_tickers),
                "results": [r.dict() for r in results],
                "failed_tickers": failed_tickers
            },
            metadata=metadata
        )


class CompanySearchResponse(BaseAPIResponse):
    """Company search API response"""
    data: Dict[str, Any] = {}
    
    @classmethod
    def search_success(
        cls, 
        companies: List[CompanyResponse], 
        total_count: int,
        page: int,
        page_size: int,
        metadata: ProcessingMetadata
    ):
        """Create successful search response"""
        return cls(
            status=ResponseStatus.SUCCESS,
            message=f"Found {total_count} companies",
            data={
                "companies": [c.dict() for c in companies],
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "has_next": (page * page_size) < total_count,
                "has_previous": page > 1
            },
            metadata=metadata
        )


class IndustryBenchmarkResponse(BaseAPIResponse):
    """Industry benchmark API response"""
    data: Dict[str, Any] = {}
    
    @classmethod
    def benchmark_success(
        cls,
        sector: str,
        industry: str,
        benchmarks: Dict[str, float],
        peer_companies: List[str],
        metadata: ProcessingMetadata
    ):
        """Create successful benchmark response"""
        return cls(
            status=ResponseStatus.SUCCESS,
            message=f"Benchmark data retrieved for {sector} - {industry}",
            data={
                "sector": sector,
                "industry": industry,
                "benchmarks": benchmarks,
                "peer_companies": peer_companies,
                "peer_count": len(peer_companies)
            },
            metadata=metadata
        )


class NewsAnalysisResponse(BaseAPIResponse):
    """News analysis API response"""
    data: Dict[str, Any] = {}
    
    @classmethod
    def news_success(
        cls,
        ticker: str,
        news_articles: List[Dict],
        sentiment_summary: Dict[str, float],
        metadata: ProcessingMetadata
    ):
        """Create successful news analysis response"""
        return cls(
            status=ResponseStatus.SUCCESS,
            message=f"News analysis completed for {ticker}",
            data={
                "ticker": ticker,
                "articles_count": len(news_articles),
                "articles": news_articles,
                "sentiment_summary": sentiment_summary,
                "analysis_period": "last_30_days"
            },
            metadata=metadata
        )


class DataQualityResponse(BaseAPIResponse):
    """Data quality assessment response"""
    data: Dict[str, Any] = {}
    
    @classmethod
    def quality_assessment(
        cls,
        ticker: str,
        quality_metrics: Dict[str, Any],
        recommendations: List[str],
        metadata: ProcessingMetadata
    ):
        """Create data quality assessment response"""
        return cls(
            status=ResponseStatus.SUCCESS,
            message=f"Data quality assessment completed for {ticker}",
            data={
                "ticker": ticker,
                "quality_metrics": quality_metrics,
                "recommendations": recommendations,
                "assessment_date": datetime.utcnow().isoformat()
            },
            metadata=metadata
        )


class APIErrorResponse(BaseAPIResponse):
    """Generic API error response"""
    
    @classmethod
    def validation_error(cls, field: str, message: str):
        """Create validation error response"""
        return cls(
            status=ResponseStatus.ERROR,
            message="Validation failed",
            errors=[APIError(
                code=ErrorCode.VALIDATION_ERROR,
                message=message,
                field=field
            )]
        )
    
    @classmethod
    def rate_limit_exceeded(cls):
        """Create rate limit error response"""
        return cls(
            status=ResponseStatus.ERROR,
            message="Rate limit exceeded",
            errors=[APIError(
                code=ErrorCode.RATE_LIMIT_EXCEEDED,
                message="Too many requests. Please try again later.",
                suggestion="Reduce request frequency or upgrade your plan"
            )]
        )
    
    @classmethod
    def internal_error(cls, details: Optional[str] = None):
        """Create internal error response"""
        return cls(
            status=ResponseStatus.ERROR,
            message="Internal server error",
            errors=[APIError(
                code=ErrorCode.INTERNAL_ERROR,
                message="An unexpected error occurred",
                details=details,
                suggestion="Please try again later or contact support"
            )]
        )
    
    @classmethod
    def timeout_error(cls, operation: str):
        """Create timeout error response"""
        return cls(
            status=ResponseStatus.ERROR,
            message=f"{operation} timed out",
            errors=[APIError(
                code=ErrorCode.TIMEOUT_ERROR,
                message=f"Operation '{operation}' took too long to complete",
                suggestion="Try again with a simpler request or contact support"
            )]
        )
    
    @classmethod
    def data_unavailable(cls, ticker: str, reason: str):
        """Create data unavailable error response"""
        return cls(
            status=ResponseStatus.ERROR,
            message=f"Data unavailable for {ticker}",
            errors=[APIError(
                code=ErrorCode.DATA_UNAVAILABLE,
                message=reason,
                suggestion="Try again later or check if the company provides ESG data"
            )]
        )


class PaginatedResponse(BaseAPIResponse):
    """Base class for paginated responses"""
    
    def __init__(self, **data):
        super().__init__(**data)
        if 'data' not in data:
            self.data = {}
    
    @property
    def has_next(self) -> bool:
        """Check if there are more pages"""
        if not isinstance(self.data, dict):
            return False
        page = self.data.get('page', 1)
        page_size = self.data.get('page_size', 20)
        total_count = self.data.get('total_count', 0)
        return (page * page_size) < total_count
    
    @property
    def has_previous(self) -> bool:
        """Check if there are previous pages"""
        if not isinstance(self.data, dict):
            return False
        return self.data.get('page', 1) > 1


# Response type unions for API documentation
APIResponseType = Union[
    CompanyValidationResponse,
    ESGAnalysisResponse,
    HealthCheckResponse,
    BulkAnalysisResponse,
    CompanySearchResponse,
    IndustryBenchmarkResponse,
    NewsAnalysisResponse,
    DataQualityResponse,
    APIErrorResponse
]