"""
Custom exceptions for ESG Investment Research System
"""

from typing import Optional, Dict, Any, List


class ESGSystemError(Exception):
    """Base exception for ESG Investment Research System"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class CompanyValidationError(ESGSystemError):
    """Exception raised during company validation"""
    
    def __init__(
        self, 
        ticker: str,
        message: str = "Company validation failed",
        error_code: str = "VALIDATION_FAILED",
        validation_errors: Optional[List[str]] = None
    ):
        self.ticker = ticker
        self.validation_errors = validation_errors or []
        
        details = {
            "ticker": ticker,
            "validation_errors": self.validation_errors
        }
        
        super().__init__(message, error_code, details)


class CompanyNotFoundError(CompanyValidationError):
    """Exception raised when company is not found"""
    
    def __init__(
        self, 
        ticker: str,
        suggestion: Optional[str] = None
    ):
        message = f"Company '{ticker}' does not exist or is not publicly traded"
        if suggestion:
            message += f". {suggestion}"
        
        details = {
            "ticker": ticker,
            "suggestion": suggestion
        }
        
        super().__init__(
            ticker=ticker,
            message=message,
            error_code="COMPANY_NOT_FOUND",
            validation_errors=[message]
        )


class InvalidTickerError(CompanyValidationError):
    """Exception raised for invalid ticker format"""
    
    def __init__(self, ticker: str):
        message = f"Invalid ticker format: '{ticker}'. Ticker should be 1-10 alphanumeric characters."
        
        super().__init__(
            ticker=ticker,
            message=message,
            error_code="INVALID_TICKER",
            validation_errors=[message]
        )


class DataCollectionError(ESGSystemError):
    """Exception raised during data collection"""
    
    def __init__(
        self, 
        source: str,
        message: str = "Data collection failed",
        error_code: str = "DATA_COLLECTION_FAILED",
        failed_sources: Optional[List[str]] = None
    ):
        self.source = source
        self.failed_sources = failed_sources or [source]
        
        details = {
            "source": source,
            "failed_sources": self.failed_sources
        }
        
        super().__init__(message, error_code, details)


class DataUnavailableError(DataCollectionError):
    """Exception raised when data is unavailable"""
    
    def __init__(
        self, 
        ticker: str,
        data_type: str,
        reason: Optional[str] = None
    ):
        message = f"{data_type} data unavailable for '{ticker}'"
        if reason:
            message += f": {reason}"
        
        details = {
            "ticker": ticker,
            "data_type": data_type,
            "reason": reason
        }
        
        super().__init__(
            source=data_type,
            message=message,
            error_code="DATA_UNAVAILABLE",
            failed_sources=[data_type]
        )


class APIError(ESGSystemError):
    """Exception raised for API-related errors"""
    
    def __init__(
        self, 
        api_name: str,
        status_code: Optional[int] = None,
        message: str = "API request failed",
        error_code: str = "API_ERROR",
        response_data: Optional[Dict[str, Any]] = None
    ):
        self.api_name = api_name
        self.status_code = status_code
        self.response_data = response_data or {}
        
        details = {
            "api_name": api_name,
            "status_code": status_code,
            "response_data": self.response_data
        }
        
        super().__init__(message, error_code, details)


class RateLimitError(APIError):
    """Exception raised when API rate limits are exceeded"""
    
    def __init__(
        self, 
        api_name: str,
        retry_after: Optional[int] = None
    ):
        message = f"Rate limit exceeded for {api_name}"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        
        details = {
            "api_name": api_name,
            "retry_after": retry_after
        }
        
        super().__init__(
            api_name=api_name,
            status_code=429,
            message=message,
            error_code="RATE_LIMIT_EXCEEDED"
        )


class TimeoutError(APIError):
    """Exception raised when API requests timeout"""
    
    def __init__(
        self, 
        api_name: str,
        timeout_duration: Optional[float] = None
    ):
        message = f"Request to {api_name} timed out"
        if timeout_duration:
            message += f" after {timeout_duration} seconds"
        
        details = {
            "api_name": api_name,
            "timeout_duration": timeout_duration
        }
        
        super().__init__(
            api_name=api_name,
            status_code=504,
            message=message,
            error_code="TIMEOUT_ERROR"
        )


class AIAnalysisError(ESGSystemError):
    """Exception raised during AI analysis"""
    
    def __init__(
        self, 
        ticker: str,
        message: str = "AI analysis failed",
        error_code: str = "AI_ANALYSIS_FAILED",
        ai_response: Optional[str] = None
    ):
        self.ticker = ticker
        self.ai_response = ai_response
        
        details = {
            "ticker": ticker,
            "ai_response": ai_response
        }
        
        super().__init__(message, error_code, details)


class InsufficientDataError(AIAnalysisError):
    """Exception raised when insufficient data for AI analysis"""
    
    def __init__(
        self, 
        ticker: str,
        missing_data_types: Optional[List[str]] = None
    ):
        self.missing_data_types = missing_data_types or []
        
        message = f"Insufficient data for ESG analysis of '{ticker}'"
        if self.missing_data_types:
            message += f". Missing: {', '.join(self.missing_data_types)}"
        
        details = {
            "ticker": ticker,
            "missing_data_types": self.missing_data_types
        }
        
        super().__init__(
            ticker=ticker,
            message=message,
            error_code="INSUFFICIENT_DATA"
        )


class ESGAnalysisError(ESGSystemError):
    """Exception raised during ESG analysis process"""
    
    def __init__(
        self, 
        ticker: str,
        analysis_step: str,
        message: str = "ESG analysis failed",
        error_code: str = "ESG_ANALYSIS_ERROR"
    ):
        self.ticker = ticker
        self.analysis_step = analysis_step
        
        details = {
            "ticker": ticker,
            "analysis_step": analysis_step
        }
        
        super().__init__(message, error_code, details)


class BenchmarkError(ESGSystemError):
    """Exception raised during benchmark calculation"""
    
    def __init__(
        self, 
        sector: str,
        industry: Optional[str] = None,
        message: str = "Benchmark calculation failed",
        error_code: str = "BENCHMARK_ERROR"
    ):
        self.sector = sector
        self.industry = industry
        
        details = {
            "sector": sector,
            "industry": industry
        }
        
        super().__init__(message, error_code, details)


class InsufficientPeerDataError(BenchmarkError):
    """Exception raised when insufficient peer data for benchmarking"""
    
    def __init__(
        self, 
        sector: str,
        industry: Optional[str] = None,
        peer_count: int = 0
    ):
        message = f"Insufficient peer data for benchmarking in {sector}"
        if industry:
            message += f" - {industry}"
        message += f" (found {peer_count} peers)"
        
        details = {
            "sector": sector,
            "industry": industry,
            "peer_count": peer_count
        }
        
        super().__init__(
            sector=sector,
            industry=industry,
            message=message,
            error_code="INSUFFICIENT_PEER_DATA"
        )


class StorageError(ESGSystemError):
    """Exception raised during data storage operations"""
    
    def __init__(
        self, 
        operation: str,
        collection: Optional[str] = None,
        message: str = "Storage operation failed",
        error_code: str = "STORAGE_ERROR"
    ):
        self.operation = operation
        self.collection = collection
        
        details = {
            "operation": operation,
            "collection": collection
        }
        
        super().__init__(message, error_code, details)


class DatabaseConnectionError(StorageError):
    """Exception raised when database connection fails"""
    
    def __init__(
        self, 
        database_name: str,
        connection_string: Optional[str] = None
    ):
        message = f"Failed to connect to database: {database_name}"
        
        details = {
            "database_name": database_name,
            "connection_string": "***MASKED***" if connection_string else None
        }
        
        super().__init__(
            operation="connect",
            message=message,
            error_code="DATABASE_CONNECTION_ERROR"
        )


class ConfigurationError(ESGSystemError):
    """Exception raised for configuration issues"""
    
    def __init__(
        self, 
        config_key: str,
        message: str = "Configuration error",
        error_code: str = "CONFIGURATION_ERROR"
    ):
        self.config_key = config_key
        
        details = {
            "config_key": config_key
        }
        
        super().__init__(message, error_code, details)


class MissingAPIKeyError(ConfigurationError):
    """Exception raised when required API keys are missing"""
    
    def __init__(self, api_name: str):
        message = f"Missing API key for {api_name}"
        
        super().__init__(
            config_key=f"{api_name.upper()}_API_KEY",
            message=message,
            error_code="MISSING_API_KEY"
        )


class ValidationError(ESGSystemError):
    """Exception raised for request validation errors"""
    
    def __init__(
        self, 
        field: str,
        value: Any,
        message: str = "Validation failed",
        error_code: str = "VALIDATION_ERROR"
    ):
        self.field = field
        self.value = value
        
        details = {
            "field": field,
            "value": str(value),
            "validation_message": message
        }
        
        super().__init__(message, error_code, details)


class BusinessLogicError(ESGSystemError):
    """Exception raised for business logic violations"""
    
    def __init__(
        self, 
        business_rule: str,
        message: str = "Business rule violation",
        error_code: str = "BUSINESS_LOGIC_ERROR"
    ):
        self.business_rule = business_rule
        
        details = {
            "business_rule": business_rule
        }
        
        super().__init__(message, error_code, details)


# Exception hierarchy for easy catching
API_EXCEPTIONS = (APIError, RateLimitError, TimeoutError)
DATA_EXCEPTIONS = (DataCollectionError, DataUnavailableError, InsufficientDataError)
ANALYSIS_EXCEPTIONS = (AIAnalysisError, ESGAnalysisError, BenchmarkError)
STORAGE_EXCEPTIONS = (StorageError, DatabaseConnectionError)
VALIDATION_EXCEPTIONS = (ValidationError, CompanyValidationError, InvalidTickerError)
CONFIGURATION_EXCEPTIONS = (ConfigurationError, MissingAPIKeyError)

# All custom exceptions
ALL_EXCEPTIONS = (
    ESGSystemError,
    CompanyValidationError,
    CompanyNotFoundError,
    InvalidTickerError,
    DataCollectionError,
    DataUnavailableError,
    APIError,
    RateLimitError,
    TimeoutError,
    AIAnalysisError,
    InsufficientDataError,
    ESGAnalysisError,
    BenchmarkError,
    InsufficientPeerDataError,
    StorageError,
    DatabaseConnectionError,
    ConfigurationError,
    MissingAPIKeyError,
    ValidationError,
    BusinessLogicError
)