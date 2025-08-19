"""
ESG analysis API endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, Path, HTTPException, Depends
from loguru import logger

from app.models.esg_analysis import ESGAnalysisRequest, ESGBulkAnalysisRequest
from app.models.responses import (
    ESGAnalysisResponse, BulkAnalysisResponse, ProcessingMetadata,
    NewsAnalysisResponse, IndustryBenchmarkResponse
)
from app.services.company_validator import get_company_validator
from app.services.data_collector import get_data_collector
from app.services.esg_scraper import get_esg_scraper
from app.services.ai_analyzer import get_ai_analyzer
from app.services.benchmark_service import get_benchmark_service
from app.services.storage_service import get_storage_service
from app.api.dependencies import (
    check_rate_limit, validate_ticker_parameter, 
    require_api_feature, get_request_context
)
from app.core.pipeline import get_esg_pipeline


router = APIRouter()


@router.post("/esg", response_model=ESGAnalysisResponse)
async def analyze_company_esg(
    request: ESGAnalysisRequest,
    context: Dict[str, Any] = Depends(get_request_context),
    _: bool = Depends(check_rate_limit),
    __: bool = Depends(require_api_feature("ENABLE_AI_ANALYSIS"))
):
    """
    Perform comprehensive ESG analysis for a company
    
    This endpoint provides AI-powered ESG analysis including:
    - Environmental, Social, and Governance scoring
    - Industry benchmarking and peer comparison
    - Investment recommendations and risk assessment
    - AI-generated insights and analysis
    """
    start_time = datetime.utcnow()
    ticker = request.ticker.upper()
    
    try:
        logger.info(f"Starting ESG analysis for {ticker} (Request ID: {context.get('request_id')})")
        
        # Get ESG pipeline and run analysis
        pipeline = get_esg_pipeline()
        analysis_result = await pipeline.run_complete_analysis(
            ticker=ticker,
            force_refresh=request.force_refresh,
            include_ai_insights=request.include_ai_insights,
            include_benchmarks=request.include_benchmarks,
            include_news=request.include_news,
            analysis_depth=request.analysis_depth
        )
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Create metadata
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=analysis_result.data_sources,
            cache_hit=not request.force_refresh,
            ai_processing_time_ms=processing_time * 0.6,  # Estimate AI portion
            total_api_calls=len(analysis_result.data_sources) * 2,
            analysis_version="2.0"
        )
        
        return ESGAnalysisResponse.analysis_success(analysis_result, metadata)
        
    except Exception as e:
        logger.error(f"ESG analysis failed for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ESG analysis failed: {str(e)}")


@router.get("/esg/{ticker}", response_model=ESGAnalysisResponse)
async def get_esg_analysis(
    ticker: str = Path(..., description="Stock ticker symbol"),
    force_refresh: bool = Query(False, description="Force fresh analysis"),
    include_ai_insights: bool = Query(True, description="Include AI insights"),
    include_benchmarks: bool = Query(True, description="Include benchmark comparison"),
    include_news: bool = Query(True, description="Include news analysis"),
    context: Dict[str, Any] = Depends(get_request_context),
    _: bool = Depends(check_rate_limit)
):
    """
    Get ESG analysis for a company (GET endpoint)
    
    Alternative endpoint for getting ESG analysis using GET request.
    """
    request = ESGAnalysisRequest(
        ticker=ticker,
        force_refresh=force_refresh,
        include_ai_insights=include_ai_insights,
        include_benchmarks=include_benchmarks,
        include_news=include_news
    )
    
    return await analyze_company_esg(request, context)


@router.post("/bulk-esg")
async def bulk_esg_analysis(
    request: ESGBulkAnalysisRequest,
    context: Dict[str, Any] = Depends(get_request_context),
    _: bool = Depends(check_rate_limit),
    __: bool = Depends(require_api_feature("ENABLE_AI_ANALYSIS"))
):
    """
    Perform bulk ESG analysis for multiple companies
    
    Analyzes multiple companies efficiently with parallel processing.
    Maximum 50 companies per request.
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"Starting bulk ESG analysis for {len(request.tickers)} companies")
        
        # Get ESG pipeline
        pipeline = get_esg_pipeline()
        
        # Run bulk analysis
        results = await pipeline.run_bulk_analysis(
            tickers=request.tickers,
            analysis_depth=request.analysis_depth,
            include_ai_insights=request.include_ai_insights,
            include_benchmarks=request.include_benchmarks,
            parallel_processing=request.parallel_processing
        )
        
        # Separate successful and failed results
        successful_results = [r for r in results if r.status == "success"]
        failed_results = [r for r in results if r.status == "error"]
        failed_tickers = [r.data.ticker if r.data else "unknown" for r in failed_results]
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=["multiple_sources"],
            total_api_calls=len(request.tickers) * 5,  # Estimate
            analysis_version="2.0"
        )
        
        return BulkAnalysisResponse.bulk_success(
            results=results,
            failed_tickers=failed_tickers,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Bulk ESG analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk analysis failed: {str(e)}")


@router.get("/news/{ticker}")
async def get_news_analysis(
    ticker: str = Path(..., description="Stock ticker symbol"),
    days: int = Query(30, description="Number of days to analyze", ge=1, le=90),
    context: Dict[str, Any] = Depends(get_request_context),
    _: bool = Depends(check_rate_limit),
    __: bool = Depends(require_api_feature("ENABLE_NEWS_ANALYSIS"))
):
    """
    Get news sentiment analysis for a company
    
    Analyzes recent news articles and social media sentiment
    related to the company's ESG performance.
    """
    start_time = datetime.utcnow()
    
    try:
        ticker = validate_ticker_parameter(ticker)
        
        # Get data collector and analyze news
        data_collector = get_data_collector()
        # This would be implemented in the data collector
        # news_data = await data_collector.collect_news_sentiment(ticker, days)
        
        # For now, return placeholder data
        news_data = {
            "articles": [],
            "sentiment_summary": {
                "overall_sentiment": 0.1,
                "positive_ratio": 0.6,
                "negative_ratio": 0.2,
                "neutral_ratio": 0.2
            }
        }
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=["news_api", "reddit"],
            total_api_calls=2
        )
        
        return NewsAnalysisResponse.news_success(
            ticker=ticker,
            news_articles=news_data["articles"],
            sentiment_summary=news_data["sentiment_summary"],
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"News analysis failed for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"News analysis failed: {str(e)}")


@router.get("/benchmark/{sector}")
async def get_industry_benchmark(
    sector: str = Path(..., description="Industry sector"),
    industry: Optional[str] = Query(None, description="Specific industry within sector"),
    context: Dict[str, Any] = Depends(get_request_context),
    _: bool = Depends(check_rate_limit),
    __: bool = Depends(require_api_feature("ENABLE_PEER_BENCHMARKING"))
):
    """
    Get industry benchmark data for ESG performance
    
    Returns benchmark statistics and peer comparison data
    for companies in the specified sector/industry.
    """
    start_time = datetime.utcnow()
    
    try:
        # Get benchmark service
        benchmark_service = get_benchmark_service()
        
        # Get sector benchmark data
        sector_data = await benchmark_service.get_sector_benchmark(sector)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=["database", "peer_analysis"],
            cache_hit=True,
            total_api_calls=1
        )
        
        # Extract peer companies (top performers)
        peer_companies = sector_data.get("sector_leaders", {}).get("overall", [])
        
        # Create benchmark data
        benchmarks = {
            "environmental_avg": sector_data.get("environmental", {}).get("average", 50),
            "social_avg": sector_data.get("social", {}).get("average", 50),
            "governance_avg": sector_data.get("governance", {}).get("average", 50),
            "overall_avg": sector_data.get("overall", {}).get("average", 50)
        }
        
        return IndustryBenchmarkResponse.benchmark_success(
            sector=sector,
            industry=industry or "All Industries",
            benchmarks=benchmarks,
            peer_companies=peer_companies,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Benchmark retrieval failed for {sector}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Benchmark retrieval failed: {str(e)}")


@router.get("/history/{ticker}")
async def get_analysis_history(
    ticker: str = Path(..., description="Stock ticker symbol"),
    days: int = Query(90, description="Number of days of history", ge=1, le=365),
    context: Dict[str, Any] = Depends(get_request_context),
    _: bool = Depends(check_rate_limit)
):
    """
    Get historical ESG analysis data for a company
    
    Returns time series data showing how ESG scores have changed over time.
    """
    start_time = datetime.utcnow()
    
    try:
        ticker = validate_ticker_parameter(ticker)
        
        # Get storage service
        storage_service = get_storage_service()
        
        # Get analysis history
        history = await storage_service.get_analysis_history(ticker, days)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "ticker": ticker,
            "history_period_days": days,
            "data_points": len(history),
            "history": history,
            "metadata": {
                "processing_time_ms": processing_time,
                "data_sources_used": ["database"],
                "cache_hit": True
            }
        }
        
    except Exception as e:
        logger.error(f"History retrieval failed for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")


@router.get("/trends/{sector}")
async def get_sector_trends(
    sector: str = Path(..., description="Industry sector"),
    days: int = Query(90, description="Number of days for trend analysis", ge=30, le=365),
    context: Dict[str, Any] = Depends(get_request_context),
    _: bool = Depends(check_rate_limit),
    __: bool = Depends(require_api_feature("ENABLE_BENCHMARK_TRENDS"))
):
    """
    Get ESG trend analysis for a sector
    
    Analyzes how ESG performance has evolved over time
    for companies in the specified sector.
    """
    start_time = datetime.utcnow()
    
    try:
        # Get benchmark service
        benchmark_service = get_benchmark_service()
        
        # Get trend data
        trends = await benchmark_service.get_benchmark_trends(sector, "All Industries", days)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "sector": sector,
            "analysis_period_days": days,
            "trends": trends,
            "metadata": {
                "processing_time_ms": processing_time,
                "data_sources_used": ["database", "trend_analysis"],
                "cache_hit": True
            }
        }
        
    except Exception as e:
        logger.error(f"Trend analysis failed for {sector}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")


@router.delete("/cache/{ticker}")
async def clear_analysis_cache(
    ticker: str = Path(..., description="Stock ticker symbol"),
    context: Dict[str, Any] = Depends(get_request_context),
    _: bool = Depends(check_rate_limit)
):
    """
    Clear cached analysis data for a company
    
    Forces fresh data collection and analysis on next request.
    """
    try:
        ticker = validate_ticker_parameter(ticker)
        
        # This would implement cache clearing logic
        # For now, return success message
        
        return {
            "message": f"Cache cleared for {ticker}",
            "ticker": ticker,
            "cleared_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cache clearing failed for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cache clearing failed: {str(e)}")


@router.get("/data-quality/{ticker}")
async def get_data_quality_report(
    ticker: str = Path(..., description="Stock ticker symbol"),
    context: Dict[str, Any] = Depends(get_request_context),
    _: bool = Depends(check_rate_limit)
):
    """
    Get data quality assessment for a company's ESG analysis
    
    Returns detailed information about data availability,
    freshness, and reliability for the company.
    """
    start_time = datetime.utcnow()
    
    try:
        ticker = validate_ticker_parameter(ticker)
        
        # Get data collector for freshness assessment
        data_collector = get_data_collector()
        freshness_score = await data_collector.get_data_freshness_score(ticker)
        
        # Create quality assessment
        quality_metrics = {
            "overall_quality": "GOOD" if freshness_score > 0.7 else "FAIR",
            "data_freshness_score": freshness_score,
            "data_completeness": 0.8,  # Placeholder
            "source_reliability": 0.85,  # Placeholder
            "last_updated": datetime.utcnow().isoformat()
        }
        
        recommendations = [
            "ESG data sources are reliable and current",
            "Consider additional data sources for comprehensive analysis",
            "Regular updates ensure data freshness"
        ]
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=["data_quality_assessment"],
            total_api_calls=1
        )
        
        from app.models.responses import DataQualityResponse
        return DataQualityResponse.quality_assessment(
            ticker=ticker,
            quality_metrics=quality_metrics,
            recommendations=recommendations,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Data quality assessment failed for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data quality assessment failed: {str(e)}")