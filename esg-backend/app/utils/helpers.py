"""
Helper utility functions for ESG Investment Research System
"""

import asyncio
import functools
import re
import time
import uuid
from datetime import datetime
from typing import Optional, Union, Callable, Any, Dict
from loguru import logger


def format_currency(
    amount: Optional[Union[int, float]], 
    currency: str = "USD",
    decimal_places: int = 2
) -> str:
    """
    Format a number as currency
    
    Args:
        amount: Numeric amount to format
        currency: Currency code (default: USD)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    if amount is None:
        return "N/A"
    
    try:
        if currency == "USD":
            if abs(amount) >= 1_000_000_000:
                return f"${amount / 1_000_000_000:.{decimal_places}f}B"
            elif abs(amount) >= 1_000_000:
                return f"${amount / 1_000_000:.{decimal_places}f}M"
            elif abs(amount) >= 1_000:
                return f"${amount / 1_000:.{decimal_places}f}K"
            else:
                return f"${amount:.{decimal_places}f}"
        else:
            return f"{amount:.{decimal_places}f} {currency}"
            
    except (TypeError, ValueError):
        return "N/A"


def format_percentage(
    value: Optional[Union[int, float]], 
    decimal_places: int = 2,
    include_sign: bool = True
) -> str:
    """
    Format a number as percentage
    
    Args:
        value: Numeric value to format (0.15 = 15%)
        decimal_places: Number of decimal places
        include_sign: Whether to include + sign for positive values
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "N/A"
    
    try:
        percentage = value * 100 if abs(value) <= 1 else value
        
        if include_sign and percentage > 0:
            return f"+{percentage:.{decimal_places}f}%"
        else:
            return f"{percentage:.{decimal_places}f}%"
            
    except (TypeError, ValueError):
        return "N/A"


def calculate_percentage_change(
    old_value: Optional[Union[int, float]], 
    new_value: Optional[Union[int, float]]
) -> Optional[float]:
    """
    Calculate percentage change between two values
    
    Args:
        old_value: Original value
        new_value: New value
        
    Returns:
        Percentage change as decimal (0.15 = 15% increase)
    """
    if old_value is None or new_value is None or old_value == 0:
        return None
    
    try:
        return (new_value - old_value) / abs(old_value)
    except (TypeError, ZeroDivisionError):
        return None


def validate_ticker_format(ticker: str) -> bool:
    """
    Validate ticker symbol format
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if valid format, False otherwise
    """
    if not ticker or not isinstance(ticker, str):
        return False
    
    # Basic ticker validation: 1-10 alphanumeric characters, periods, hyphens
    pattern = r'^[A-Z0-9.-]{1,10}$'
    return bool(re.match(pattern, ticker.upper()))


def clean_company_name(name: str) -> str:
    """
    Clean and standardize company name
    
    Args:
        name: Raw company name
        
    Returns:
        Cleaned company name
    """
    if not name or not isinstance(name, str):
        return ""
    
    # Remove common suffixes and clean up
    cleaned = name.strip()
    
    # Remove common corporate suffixes (case-insensitive)
    suffixes = [
        r'\s+Inc\.?$',
        r'\s+Corporation$',
        r'\s+Corp\.?$',
        r'\s+Company$',
        r'\s+Co\.?$',
        r'\s+Ltd\.?$',
        r'\s+Limited$',
        r'\s+LLC$',
        r'\s+L\.L\.C\.?$',
        r'\s+PLC$',
        r'\s+S\.A\.?$',
        r'\s+N\.V\.?$'
    ]
    
    for suffix in suffixes:
        cleaned = re.sub(suffix, '', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


def parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Parse various date string formats
    
    Args:
        date_str: Date string to parse
        
    Returns:
        Parsed datetime object or None if parsing fails
    """
    if not date_str:
        return None
    
    # Common date formats to try
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%Y/%m/%d",
        "%d-%m-%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse date string: {date_str}")
    return None


def generate_request_id() -> str:
    """
    Generate unique request ID for tracking
    
    Returns:
        Unique request identifier
    """
    return str(uuid.uuid4())


def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for backoff delay
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                        
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise e
                    
                    delay = backoff_factor * (2 ** attempt)
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}), retrying in {delay}s: {str(e)}")
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                        
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise e
                    
                    delay = backoff_factor * (2 ** attempt)
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}), retrying in {delay}s: {str(e)}")
                    time.sleep(delay)
            
            raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


def rate_limit_decorator(
    calls_per_minute: int = 60,
    calls_per_hour: int = 1000
):
    """
    Decorator for rate limiting function calls
    
    Args:
        calls_per_minute: Maximum calls per minute
        calls_per_hour: Maximum calls per hour
    """
    call_times = []
    
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            now = time.time()
            
            # Clean old entries
            call_times[:] = [t for t in call_times if now - t < 3600]  # Keep last hour
            
            # Check rate limits
            recent_calls = sum(1 for t in call_times if now - t < 60)  # Last minute
            
            if recent_calls >= calls_per_minute:
                raise Exception(f"Rate limit exceeded: {calls_per_minute} calls per minute")
            
            if len(call_times) >= calls_per_hour:
                raise Exception(f"Rate limit exceeded: {calls_per_hour} calls per hour")
            
            # Record this call
            call_times.append(now)
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            now = time.time()
            
            # Clean old entries
            call_times[:] = [t for t in call_times if now - t < 3600]  # Keep last hour
            
            # Check rate limits
            recent_calls = sum(1 for t in call_times if now - t < 60)  # Last minute
            
            if recent_calls >= calls_per_minute:
                raise Exception(f"Rate limit exceeded: {calls_per_minute} calls per minute")
            
            if len(call_times) >= calls_per_hour:
                raise Exception(f"Rate limit exceeded: {calls_per_hour} calls per hour")
            
            # Record this call
            call_times.append(now)
            
            # Execute function
            return func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


def sanitize_input(input_str: str, max_length: int = 100) -> str:
    """
    Sanitize user input for security
    
    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not input_str:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';(){}]', '', str(input_str))
    
    # Limit length
    sanitized = sanitized[:max_length]
    
    # Strip whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def is_business_hours() -> bool:
    """
    Check if current time is within business hours (9 AM - 5 PM UTC)
    
    Returns:
        True if within business hours
    """
    now = datetime.utcnow()
    return 9 <= now.hour < 17


def calculate_confidence_score(
    data_sources: list,
    data_completeness: float,
    data_freshness: float
) -> float:
    """
    Calculate overall confidence score for analysis
    
    Args:
        data_sources: List of data sources used
        data_completeness: Completeness ratio (0-1)
        data_freshness: Freshness score (0-1)
        
    Returns:
        Confidence score (0-1)
    """
    try:
        # Source diversity score (more sources = higher confidence)
        source_score = min(len(data_sources) / 5.0, 1.0)  # Max at 5 sources
        
        # Weighted average
        confidence = (
            source_score * 0.3 +
            data_completeness * 0.4 +
            data_freshness * 0.3
        )
        
        return max(0.0, min(1.0, confidence))
        
    except (TypeError, ValueError):
        return 0.5  # Default moderate confidence


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask sensitive data in dictionaries for logging
    
    Args:
        data: Dictionary that may contain sensitive data
        
    Returns:
        Dictionary with sensitive values masked
    """
    if not isinstance(data, dict):
        return data
    
    sensitive_keys = {
        'api_key', 'password', 'token', 'secret', 'auth',
        'private_key', 'client_secret', 'access_token'
    }
    
    masked_data = {}
    
    for key, value in data.items():
        key_lower = key.lower()
        
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            masked_data[key] = "***MASKED***"
        elif isinstance(value, dict):
            masked_data[key] = mask_sensitive_data(value)
        elif isinstance(value, list):
            masked_data[key] = [
                mask_sensitive_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            masked_data[key] = value
    
    return masked_data


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix