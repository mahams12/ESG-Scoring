"""
FastAPI dependencies for ESG Investment Research System
"""

import time
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from app.config import get_settings
from app.utils.helpers import generate_request_id


# Security scheme for API authentication (optional for public API)
security_scheme = HTTPBearer(auto_error=False)


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}  # {client_id: [timestamps]}
        
    def is_allowed(
        self, 
        client_id: str, 
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ) -> bool:
        """Check if request is allowed under rate limits"""
        now = time.time()
        
        # Initialize client if not exists
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Clean old requests (older than 1 hour)
        self.requests[client_id] = [
            timestamp for timestamp in self.requests[client_id] 
            if now - timestamp < 3600
        ]
        
        # Check minute limit
        recent_requests = sum(
            1 for timestamp in self.requests[client_id] 
            if now - timestamp < 60
        )
        
        if recent_requests >= requests_per_minute:
            return False
        
        # Check hour limit
        if len(self.requests[client_id]) >= requests_per_hour:
            return False
        
        # Record this request
        self.requests[client_id].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get rate limiter dependency"""
    return rate_limiter


def get_client_id(request: Request) -> str:
    """Extract client identifier for rate limiting"""
    # Use IP address as client identifier
    # In production, you might want to use API keys or user IDs
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    
    return client_ip


def check_rate_limit(
    request: Request,
    limiter: RateLimiter = Depends(get_rate_limiter),
    requests_per_minute: int = 100,
    requests_per_hour: int = 1000
):
    """Check rate limits for incoming requests"""
    client_id = get_client_id(request)
    
    if not limiter.is_allowed(client_id, requests_per_minute, requests_per_hour):
        logger.warning(f"Rate limit exceeded for client {client_id}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"}
        )
    
    return True


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Optional[Dict[str, Any]]:
    """
    Get current user from authentication credentials
    
    Note: This is a placeholder for authentication.
    In production, implement proper JWT/API key validation.
    """
    if not credentials:
        # For public API, no authentication required
        return None
    
    # Placeholder authentication logic
    # In production, validate JWT token or API key here
    try:
        # Example: validate API key or JWT token
        token = credentials.credentials
        
        # For demo purposes, accept any token
        # In production, implement proper validation
        if token:
            return {
                "user_id": "demo_user",
                "api_key": token[:8] + "***",  # Masked for logging
                "permissions": ["read", "analyze"]
            }
        
        return None
        
    except Exception as e:
        logger.warning(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


def validate_request(request: Request) -> Dict[str, Any]:
    """Validate and enrich incoming requests"""
    
    # Generate unique request ID
    request_id = generate_request_id()
    
    # Extract request metadata
    request_metadata = {
        "request_id": request_id,
        "method": request.method,
        "url": str(request.url),
        "client_ip": get_client_id(request),
        "user_agent": request.headers.get("User-Agent", ""),
        "timestamp": time.time()
    }
    
    # Add request ID to headers for response
    request.state.request_id = request_id
    request.state.metadata = request_metadata
    
    return request_metadata


def get_request_metadata(request: Request) -> Dict[str, Any]:
    """Get request metadata from request state"""
    return getattr(request.state, "metadata", {})


def log_request(
    request: Request,
    metadata: Dict[str, Any] = Depends(validate_request)
):
    """Log incoming requests for monitoring"""
    logger.info(
        f"Request {metadata['request_id']}: "
        f"{metadata['method']} {metadata['url']} "
        f"from {metadata['client_ip']}"
    )
    
    return metadata


def validate_ticker_parameter(ticker: str) -> str:
    """Validate ticker parameter"""
    from app.utils.helpers import validate_ticker_format
    
    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticker parameter is required"
        )
    
    ticker = ticker.strip().upper()
    
    if not validate_ticker_format(ticker):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ticker format: {ticker}"
        )
    
    return ticker


def check_feature_flag(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    from app.utils.constants import FEATURE_FLAGS
    
    enabled = FEATURE_FLAGS.get(feature_name, False)
    
    if not enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Feature '{feature_name}' is currently disabled"
        )
    
    return enabled


def validate_pagination(
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100
) -> Dict[str, int]:
    """Validate pagination parameters"""
    
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page number must be greater than 0"
        )
    
    if page_size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be greater than 0"
        )
    
    if page_size > max_page_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Page size cannot exceed {max_page_size}"
        )
    
    return {
        "page": page,
        "page_size": page_size,
        "offset": (page - 1) * page_size
    }


def get_settings_dependency():
    """Get application settings as dependency"""
    return get_settings()


def require_api_feature(feature_name: str):
    """Dependency to require a specific feature to be enabled"""
    def dependency():
        return check_feature_flag(feature_name)
    
    return dependency


def get_request_context(
    request: Request,
    metadata: Dict[str, Any] = Depends(validate_request),
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get complete request context"""
    
    context = {
        "request_id": metadata.get("request_id"),
        "client_ip": metadata.get("client_ip"),
        "user_agent": metadata.get("user_agent"),
        "timestamp": metadata.get("timestamp"),
        "user": user,
        "authenticated": user is not None
    }
    
    return context