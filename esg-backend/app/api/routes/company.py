# routes company.py
"""
Company validation and information API endpoints
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Query, Path, HTTPException
from loguru import logger

from app.models.company import (
    CompanyValidationRequest, CompanyResponse, CompanySearchResult
)
from app.models.responses import (
    CompanyValidationResponse, CompanySearchResponse, ProcessingMetadata
)
from app.services.company_validator import get_company_validator


router = APIRouter()


@router.post("/validate", response_model=CompanyValidationResponse)
async def validate_company(request: CompanyValidationRequest):
    """
    Validate if a company exists and is publicly traded
    
    This endpoint checks multiple financial data sources to verify
    if a company exists and provides basic company information.
    """
    start_time = datetime.utcnow()
    
    try:
        validator = get_company_validator()
        
        # Perform validation
        validation_result = await validator.validate_company(
            ticker=request.ticker,
            force_refresh=request.force_refresh
        )
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Create metadata
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=validation_result.data_sources_checked,
            cache_hit=not request.force_refresh,
            total_api_calls=len(validation_result.data_sources_checked)
        )
        
        # Return appropriate response
        if validation_result.exists:
            return CompanyValidationResponse.validation_success(validation_result, metadata)
        else:
            return CompanyValidationResponse.company_not_found(
                request.ticker,
                "Please verify the ticker symbol and try again"
            )
            
    except ValueError as e:
        logger.warning(f"Validation request error for {request.ticker}: {str(e)}")
        return CompanyValidationResponse.company_not_found(
            request.ticker,
            str(e)
        )
    except Exception as e:
        logger.error(f"Company validation failed for {request.ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/validate/{ticker}", response_model=CompanyValidationResponse)
async def validate_company_by_ticker(
    ticker: str = Path(..., description="Stock ticker symbol"),
    force_refresh: bool = Query(False, description="Force fresh validation")
):
    """
    Validate company by ticker symbol (GET endpoint)
    
    Alternative endpoint for validating companies using GET request.
    Useful for simple validation checks.
    """
    request = CompanyValidationRequest(ticker=ticker, force_refresh=force_refresh)
    return await validate_company(request)


@router.get("/info/{ticker}", response_model=CompanyValidationResponse)
async def get_company_info(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """
    Get stored company information
    
    Returns cached company information if available.
    Does not perform fresh validation.
    """
    start_time = datetime.utcnow()
    
    try:
        validator = get_company_validator()
        company_info = await validator.get_company_info(ticker)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=["database_cache"],
            cache_hit=True,
            total_api_calls=0
        )
        
        if company_info:
            # Create validation result from stored info
            from app.models.company import CompanyValidationResult, CompanyStatus
            
            validation_result = CompanyValidationResult(
                ticker=company_info.ticker,
                status=CompanyStatus.VALID,
                exists=True,
                message="Company information retrieved from cache",
                company_info=company_info,
                data_sources_checked=["database_cache"],
                confidence_score=0.9
            )
            
            return CompanyValidationResponse.validation_success(validation_result, metadata)
        else:
            return CompanyValidationResponse.company_not_found(
                ticker,
                "Company not found in database. Try validation endpoint first."
            )
            
    except Exception as e:
        logger.error(f"Failed to get company info for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve company info: {str(e)}")


@router.get("/search", response_model=CompanySearchResponse)
async def search_companies(
    query: str = Query(..., description="Search query (company name or ticker)", min_length=1),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    limit: int = Query(20, description="Number of results to return", ge=1, le=100),
    offset: int = Query(0, description="Number of results to skip", ge=0)
):
    """
    Search for companies by name or ticker
    
    Searches through validated companies in the database.
    Supports filtering by sector and pagination.
    """
    start_time = datetime.utcnow()
    
    try:
        validator = get_company_validator()
        
        # Perform search
        companies, total_count = await validator.search_companies(
            query=query,
            sector=sector,
            limit=limit,
            offset=offset
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=["database"],
            cache_hit=True,
            total_api_calls=1
        )
        
        # Convert to response objects
        company_responses = [CompanyResponse(**company.dict()) for company in companies]
        
        # Calculate pagination info
        page = (offset // limit) + 1
        
        return CompanySearchResponse.search_success(
            companies=company_responses,
            total_count=total_count,
            page=page,
            page_size=limit,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Company search failed for query '{query}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/peers/{ticker}")
async def get_industry_peers(
    ticker: str = Path(..., description="Stock ticker symbol"),
    limit: int = Query(10, description="Number of peers to return", ge=1, le=50)
):
    """
    Get industry peer companies
    
    Returns companies in the same industry as the specified ticker.
    Sorted by market capitalization in descending order.
    """
    start_time = datetime.utcnow()
    
    try:
        validator = get_company_validator()
        
        # Get industry peers
        peers = await validator.get_industry_peers(ticker, limit=limit)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=["database"],
            cache_hit=True,
            total_api_calls=1
        )
        
        if not peers:
            # Try to get company info to see if ticker exists
            company_info = await validator.get_company_info(ticker)
            if not company_info:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Company '{ticker}' not found. Validate the company first."
                )
            else:
                return {
                    "ticker": ticker,
                    "industry": company_info.industry,
                    "peers": [],
                    "message": "No industry peers found",
                    "metadata": metadata.dict()
                }
        
        # Convert to response format
        peer_responses = [CompanyResponse(**peer.dict()) for peer in peers]
        
        return {
            "ticker": ticker,
            "industry": peers[0].industry if peers else None,
            "sector": peers[0].sector if peers else None,
            "peers": [peer.dict() for peer in peer_responses],
            "peer_count": len(peer_responses),
            "metadata": metadata.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get industry peers for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get industry peers: {str(e)}")


@router.post("/bulk-validate")
async def bulk_validate_companies(
    request: dict
):
    """
    Validate multiple companies in bulk
    
    Accepts a list of ticker symbols and validates them all.
    Returns results for each ticker with success/failure status.
    """
    start_time = datetime.utcnow()
    
    try:
        tickers = request.get("tickers", [])
        force_refresh = request.get("force_refresh", False)
        
        if not tickers:
            raise HTTPException(status_code=400, detail="No tickers provided")
        
        if len(tickers) > 50:
            raise HTTPException(status_code=400, detail="Too many tickers. Maximum 50 allowed.")
        
        validator = get_company_validator()
        
        # Perform bulk validation
        results = await validator.bulk_validate_companies(tickers, force_refresh)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Count successful and failed validations
        successful_results = [r for r in results if r.exists]
        failed_results = [r for r in results if not r.exists]
        
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=["multiple_financial_apis"],
            cache_hit=not force_refresh,
            total_api_calls=len(tickers) * 3  # Approximate API calls per ticker
        )
        
        return {
            "total_requested": len(tickers),
            "successful_count": len(successful_results),
            "failed_count": len(failed_results),
            "results": [result.dict() for result in results],
            "successful_tickers": [r.ticker for r in successful_results],
            "failed_tickers": [r.ticker for r in failed_results],
            "metadata": metadata.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk validation failed: {str(e)}")


@router.get("/stats")
async def get_validation_stats():
    """
    Get company validation statistics
    
    Returns statistics about validated companies in the system.
    """
    start_time = datetime.utcnow()
    
    try:
        validator = get_company_validator()
        stats = await validator.get_validation_stats()
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=["database"],
            cache_hit=True,
            total_api_calls=1
        )
        
        return {
            "statistics": stats,
            "last_updated": datetime.utcnow().isoformat(),
            "metadata": metadata.dict()
        }
        
    except Exception as e:
        logger.error(f"Failed to get validation stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.get("/sectors")
async def get_available_sectors():
    """
    Get list of available sectors
    
    Returns all sectors that have validated companies in the system.
    """
    try:
        from app.models.company import Sector
        
        return {
            "sectors": [sector.value for sector in Sector],
            "description": "Available sectors for filtering and analysis"
        }
        
    except Exception as e:
        logger.error(f"Failed to get sectors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get sectors: {str(e)}")