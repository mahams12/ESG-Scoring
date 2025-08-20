# pipeline.py
"""
Main ESG analysis pipeline orchestrating all components
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger

from app.config import get_settings
from app.models.esg_analysis import ESGAnalysis
from app.models.responses import ESGAnalysisResponse, ProcessingMetadata
from app.services.company_validator import get_company_validator
from app.services.data_collector import get_data_collector
from app.services.esg_scraper import get_esg_scraper
from app.services.ai_analyzer import get_ai_analyzer
from app.services.benchmark_service import get_benchmark_service
from app.services.storage_service import get_storage_service
from app.utils.exceptions import (
    CompanyNotFoundError, DataCollectionError, ESGAnalysisError
)


class ESGAnalysisPipeline:
    """
    Main pipeline for orchestrating complete ESG analysis
    
    This pipeline coordinates all services to provide comprehensive
    ESG analysis including validation, data collection, AI analysis,
    benchmarking, and storage.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.company_validator = get_company_validator()
        self.data_collector = get_data_collector()
        self.esg_scraper = get_esg_scraper()
        self.ai_analyzer = get_ai_analyzer()
        self.benchmark_service = get_benchmark_service()
        self.storage_service = get_storage_service()
        
    async def run_complete_analysis(
        self,
        ticker: str,
        force_refresh: bool = False,
        include_ai_insights: bool = True,
        include_benchmarks: bool = True,
        include_news: bool = True,
        analysis_depth: str = "comprehensive"
    ) -> ESGAnalysis:
        """
        Run complete ESG analysis pipeline
        
        Args:
            ticker: Stock ticker symbol
            force_refresh: Force fresh data collection
            include_ai_insights: Include AI-generated insights
            include_benchmarks: Include industry benchmarking
            include_news: Include news sentiment analysis
            analysis_depth: Analysis depth (basic, standard, comprehensive)
            
        Returns:
            Complete ESG analysis result
        """
        start_time = datetime.utcnow()
        pipeline_steps = []
        
        try:
            logger.info(f"Starting ESG pipeline for {ticker}")
            
            # Step 1: Company Validation
            logger.info(f"Step 1: Validating company {ticker}")
            pipeline_steps.append("validation")
            
            validation_result = await self.company_validator.validate_company(
                ticker, force_refresh
            )
            
            if not validation_result.exists:
                raise CompanyNotFoundError(
                    ticker, 
                    "Please check the ticker symbol and try again"
                )
            
            company_info = validation_result.company_info
            logger.info(f"Company validated: {company_info.name}")
            
            # Step 2: Check for cached analysis (if not forcing refresh)
            if not force_refresh:
                logger.info("Step 2: Checking for cached analysis")
                pipeline_steps.append("cache_check")
                
                cached_analysis = await self.ai_analyzer.get_cached_analysis(ticker)
                if cached_analysis:
                    logger.info(f"Using cached analysis for {ticker}")
                    return cached_analysis
            
            # Step 3: Data Collection
            logger.info("Step 3: Collecting financial and market data")
            pipeline_steps.append("data_collection")
            
            financial_data = await self.data_collector.collect_all_data(ticker)
            
            if not financial_data or financial_data.get("error"):
                logger.warning(f"Limited financial data available for {ticker}")
            
            # Step 4: ESG Data Scraping
            logger.info("Step 4: Scraping ESG data")
            pipeline_steps.append("esg_scraping")
            
            esg_data = await self.esg_scraper.scrape_all_esg_data(
                ticker, company_info.name
            )
            
            # Step 5: News and Sentiment Analysis (if requested)
            news_data = []
            if include_news:
                logger.info("Step 5: Analyzing news sentiment")
                pipeline_steps.append("news_analysis")
                
                # This would be implemented in the data collector
                # news_data = await self.data_collector.collect_news_sentiment(ticker)
                
            # Step 6: Industry Benchmarking (if requested)
            peer_data = None
            if include_benchmarks and company_info.sector and company_info.industry:
                logger.info("Step 6: Calculating industry benchmarks")
                pipeline_steps.append("benchmarking")
                
                benchmark_comparison = await self.benchmark_service.get_industry_benchmark(
                    ticker=ticker,
                    sector=company_info.sector,
                    industry=company_info.industry,
                    market_cap=company_info.market_cap
                )
                
                peer_data = {
                    "industry_avg_score": benchmark_comparison.industry_average,
                    "peer_tickers": benchmark_comparison.peer_companies,
                    "ranking": benchmark_comparison.ranking_position,
                    "top_quartile": benchmark_comparison.top_quartile_threshold
                }
            
            # Step 7: AI-Powered Analysis
            if include_ai_insights:
                logger.info("Step 7: Running AI analysis")
                pipeline_steps.append("ai_analysis")
                
                esg_analysis = await self.ai_analyzer.analyze_esg_comprehensive(
                    ticker=ticker,
                    company_name=company_info.name,
                    sector=company_info.sector or "Unknown",
                    industry=company_info.industry or "Unknown",
                    financial_data=financial_data,
                    esg_data=esg_data,
                    news_data=news_data,
                    peer_data=peer_data
                )
            else:
                # Create basic analysis without AI
                esg_analysis = await self._create_basic_analysis(
                    ticker, company_info, financial_data, esg_data
                )
            
            # Step 8: Add benchmark comparison if available
            if peer_data and include_benchmarks:
                esg_analysis.benchmark_comparison = benchmark_comparison
            
            # Step 9: Store results
            logger.info("Step 8: Storing analysis results")
            pipeline_steps.append("storage")
            
            await self.storage_service.store_esg_analysis(ticker, esg_analysis)
            
            # Calculate total processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(
                f"ESG pipeline completed for {ticker} in {processing_time:.2f}ms. "
                f"Steps: {' -> '.join(pipeline_steps)}"
            )
            
            return esg_analysis
            
        except CompanyNotFoundError:
            raise
        except Exception as e:
            logger.error(f"ESG pipeline failed for {ticker}: {str(e)}")
            raise ESGAnalysisError(
                ticker=ticker,
                analysis_step=" -> ".join(pipeline_steps),
                message=f"Pipeline failed at step: {pipeline_steps[-1] if pipeline_steps else 'unknown'}"
            )
    
    async def _create_basic_analysis(
        self,
        ticker: str,
        company_info,
        financial_data: Dict[str, Any],
        esg_data: Dict[str, Any]
    ) -> ESGAnalysis:
        """Create basic ESG analysis without AI insights"""
        
        from app.models.esg_analysis import ESGScore, InvestmentRecommendation, RiskLevel
        
        # Create basic scores (would be derived from available data)
        environmental_score = ESGScore(score=50.0, confidence_level=0.5)
        social_score = ESGScore(score=50.0, confidence_level=0.5)
        governance_score = ESGScore(score=50.0, confidence_level=0.5)
        overall_score = ESGScore(score=50.0, confidence_level=0.5)
        
        return ESGAnalysis(
            ticker=ticker,
            company_name=company_info.name,
            sector=company_info.sector,
            industry=company_info.industry,
            environmental_score=environmental_score,
            social_score=social_score,
            governance_score=governance_score,
            overall_score=overall_score,
            investment_recommendation=InvestmentRecommendation.HOLD,
            risk_level=RiskLevel.MEDIUM,
            investment_thesis="Basic analysis based on available data",
            key_strengths=["Data available for analysis"],
            key_weaknesses=["Limited AI insights"],
            improvement_areas=["Enhanced data collection"],
            ai_insights=[],
            ai_summary="Basic ESG assessment completed",
            ai_confidence=0.5,
            data_sources=esg_data.get("data_sources", [])
        )
    
    async def run_bulk_analysis(
        self,
        tickers: List[str],
        analysis_depth: str = "standard",
        include_ai_insights: bool = True,
        include_benchmarks: bool = True,
        parallel_processing: bool = True
    ) -> List[ESGAnalysisResponse]:
        """
        Run bulk ESG analysis for multiple companies
        
        Args:
            tickers: List of ticker symbols
            analysis_depth: Analysis depth for all companies
            include_ai_insights: Include AI insights
            include_benchmarks: Include benchmarking
            parallel_processing: Use parallel processing
            
        Returns:
            List of analysis responses
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting bulk analysis for {len(tickers)} companies")
            
            if parallel_processing:
                # Run analyses in parallel (with some concurrency limit)
                semaphore = asyncio.Semaphore(5)  # Limit concurrent analyses
                
                async def analyze_with_semaphore(ticker):
                    async with semaphore:
                        try:
                            analysis = await self.run_complete_analysis(
                                ticker=ticker,
                                include_ai_insights=include_ai_insights,
                                include_benchmarks=include_benchmarks,
                                analysis_depth=analysis_depth
                            )
                            
                            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                            metadata = ProcessingMetadata(
                                processing_time_ms=processing_time,
                                data_sources_used=analysis.data_sources,
                                analysis_version="2.0"
                            )
                            
                            return ESGAnalysisResponse.analysis_success(analysis, metadata)
                            
                        except Exception as e:
                            logger.error(f"Analysis failed for {ticker}: {str(e)}")
                            return ESGAnalysisResponse(
                                status="error",
                                message=f"Analysis failed for {ticker}: {str(e)}",
                                data=None
                            )
                
                # Execute all analyses in parallel
                tasks = [analyze_with_semaphore(ticker) for ticker in tickers]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Convert exceptions to error responses
                final_results = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        final_results.append(ESGAnalysisResponse(
                            status="error",
                            message=f"Analysis failed for {tickers[i]}: {str(result)}",
                            data=None
                        ))
                    else:
                        final_results.append(result)
                
                return final_results
                
            else:
                # Sequential processing
                results = []
                for ticker in tickers:
                    try:
                        analysis = await self.run_complete_analysis(
                            ticker=ticker,
                            include_ai_insights=include_ai_insights,
                            include_benchmarks=include_benchmarks,
                            analysis_depth=analysis_depth
                        )
                        
                        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                        metadata = ProcessingMetadata(
                            processing_time_ms=processing_time,
                            data_sources_used=analysis.data_sources,
                            analysis_version="2.0"
                        )
                        
                        results.append(ESGAnalysisResponse.analysis_success(analysis, metadata))
                        
                    except Exception as e:
                        logger.error(f"Analysis failed for {ticker}: {str(e)}")
                        results.append(ESGAnalysisResponse(
                            status="error",
                            message=f"Analysis failed for {ticker}: {str(e)}",
                            data=None
                        ))
                
                return results
                
        except Exception as e:
            logger.error(f"Bulk analysis failed: {str(e)}")
            raise
    
    async def refresh_company_data(self, ticker: str) -> bool:
        """
        Refresh all data for a specific company
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if refresh successful
        """
        try:
            logger.info(f"Refreshing data for {ticker}")
            
            # Force fresh validation
            await self.company_validator.validate_company(ticker, force_refresh=True)
            
            # Force fresh data collection
            await self.data_collector.collect_all_data(ticker)
            
            # Force fresh ESG scraping
            company_info = await self.company_validator.get_company_info(ticker)
            if company_info:
                await self.esg_scraper.scrape_all_esg_data(ticker, company_info.name)
            
            logger.info(f"Data refresh completed for {ticker}")
            return True
            
        except Exception as e:
            logger.error(f"Data refresh failed for {ticker}: {str(e)}")
            return False
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all pipeline components"""
        
        try:
            health_status = {}
            
            # Check each service
            services = {
                "company_validator": self.company_validator,
                "data_collector": self.data_collector,
                "esg_scraper": self.esg_scraper,
                "ai_analyzer": self.ai_analyzer,
                "benchmark_service": self.benchmark_service,
                "storage_service": self.storage_service
            }
            
            for name, service in services.items():
                try:
                    if hasattr(service, 'health_check'):
                        result = await service.health_check()
                        if isinstance(result, dict):
                            health_status[name] = all(result.values())
                        else:
                            health_status[name] = bool(result)
                    else:
                        health_status[name] = True
                except Exception as e:
                    logger.error(f"Health check failed for {name}: {str(e)}")
                    health_status[name] = False
            
            return health_status
            
        except Exception as e:
            logger.error(f"Pipeline health check failed: {str(e)}")
            return {"pipeline": False}
    
    async def get_pipeline_statistics(self) -> Dict[str, Any]:
        """Get pipeline performance statistics"""
        
        try:
            # Get storage statistics
            storage_stats = await self.storage_service.get_storage_statistics()
            
            # Get validation statistics
            validation_stats = await self.company_validator.get_validation_stats()
            
            return {
                "storage": storage_stats,
                "validation": validation_stats,
                "pipeline_version": "2.0",
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get pipeline statistics: {str(e)}")
            return {"error": str(e)}
    
    async def cleanup_expired_data(self) -> int:
        """Clean up expired cached data across all services"""
        
        try:
            total_cleaned = 0
            
            # Clean up storage service
            cleaned = await self.storage_service.cleanup_expired_data()
            total_cleaned += cleaned
            
            logger.info(f"Pipeline cleanup completed: {total_cleaned} items cleaned")
            return total_cleaned
            
        except Exception as e:
            logger.error(f"Pipeline cleanup failed: {str(e)}")
            return 0


# Global pipeline instance
esg_pipeline = ESGAnalysisPipeline()


def get_esg_pipeline() -> ESGAnalysisPipeline:
    """Get ESG analysis pipeline instance"""
    return esg_pipeline