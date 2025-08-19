"""
Industry benchmarking service for ESG performance comparison
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
import statistics

from app.config import get_settings
from app.models.esg_analysis import BenchmarkComparison
from app.database import DatabaseRepository


class BenchmarkService:
    """Service for industry ESG benchmarking and peer comparison"""
    
    def __init__(self):
        self.settings = get_settings()
        self.benchmark_repo = DatabaseRepository("benchmarks")
        self.analysis_repo = DatabaseRepository("ai_analysis")
        self.company_repo = DatabaseRepository("companies")
        
    async def get_industry_benchmark(
        self,
        ticker: str,
        sector: str,
        industry: str,
        market_cap: Optional[float] = None
    ) -> BenchmarkComparison:
        """
        Get comprehensive industry benchmark comparison
        
        Args:
            ticker: Target company ticker
            sector: Company sector
            industry: Company industry
            market_cap: Company market capitalization
            
        Returns:
            BenchmarkComparison with industry metrics
        """
        try:
            # Check cache first
            cached_benchmark = await self._get_cached_benchmark(sector, industry)
            if cached_benchmark:
                return await self._calculate_company_position(
                    ticker, cached_benchmark, market_cap
                )
            
            # Get peer companies
            peer_companies = await self._get_peer_companies(sector, industry, market_cap)
            
            if not peer_companies:
                logger.warning(f"No peer companies found for {sector} - {industry}")
                return self._create_default_benchmark(ticker)
            
            # Calculate industry benchmarks
            industry_benchmarks = await self._calculate_industry_benchmarks(
                sector, industry, peer_companies
            )
            
            # Cache the benchmarks
            await self._cache_benchmarks(sector, industry, industry_benchmarks)
            
            # Calculate company position within benchmarks
            return await self._calculate_company_position(
                ticker, industry_benchmarks, market_cap
            )
            
        except Exception as e:
            logger.error(f"Failed to get industry benchmark for {ticker}: {str(e)}")
            return self._create_default_benchmark(ticker)
    
    async def _get_peer_companies(
        self,
        sector: str,
        industry: str,
        market_cap: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Get peer companies in the same sector/industry"""
        try:
            # Build query filter
            filter_query = {
                "sector": sector,
                "industry": industry,
                "exists": True
            }
            
            # Add market cap filter if provided (within 10x range)
            if market_cap:
                filter_query["market_cap"] = {
                    "$gte": market_cap * 0.1,
                    "$lte": market_cap * 10
                }
            
            # Get peer companies
            peer_companies = await self.company_repo.find_many(
                filter_query,
                sort=[("market_cap", -1)],
                limit=50  # Limit to top 50 peers
            )
            
            return peer_companies
            
        except Exception as e:
            logger.error(f"Failed to get peer companies: {str(e)}")
            return []
    
    async def _calculate_industry_benchmarks(
        self,
        sector: str,
        industry: str,
        peer_companies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate industry benchmark metrics"""
        try:
            peer_tickers = [company["ticker"] for company in peer_companies]
            
            # Get ESG scores for all peer companies
            esg_analyses = await self._get_peer_esg_scores(peer_tickers)
            
            if not esg_analyses:
                logger.warning(f"No ESG data found for peers in {sector} - {industry}")
                return self._create_default_benchmark_data(sector, industry)
            
            # Extract scores
            env_scores = []
            social_scores = []
            gov_scores = []
            overall_scores = []
            
            for analysis in esg_analyses:
                if analysis.get("environmental_score"):
                    env_scores.append(analysis["environmental_score"]["score"])
                if analysis.get("social_score"):
                    social_scores.append(analysis["social_score"]["score"])
                if analysis.get("governance_score"):
                    gov_scores.append(analysis["governance_score"]["score"])
                if analysis.get("overall_score"):
                    overall_scores.append(analysis["overall_score"]["score"])
            
            # Calculate statistics
            benchmark_data = {
                "sector": sector,
                "industry": industry,
                "total_companies": len(peer_companies),
                "peer_tickers": peer_tickers,
                "environmental": self._calculate_score_statistics(env_scores),
                "social": self._calculate_score_statistics(social_scores),
                "governance": self._calculate_score_statistics(gov_scores),
                "overall": self._calculate_score_statistics(overall_scores),
                "market_cap_range": {
                    "min": min(c.get("market_cap", 0) for c in peer_companies if c.get("market_cap")),
                    "max": max(c.get("market_cap", 0) for c in peer_companies if c.get("market_cap")),
                    "median": statistics.median([c.get("market_cap", 0) for c in peer_companies if c.get("market_cap")])
                },
                "last_updated": datetime.utcnow()
            }
            
            return benchmark_data
            
        except Exception as e:
            logger.error(f"Failed to calculate industry benchmarks: {str(e)}")
            return self._create_default_benchmark_data(sector, industry)
    
    def _calculate_score_statistics(self, scores: List[float]) -> Dict[str, float]:
        """Calculate statistical metrics for ESG scores"""
        if not scores:
            return {
                "average": 50.0,
                "median": 50.0,
                "std_dev": 0.0,
                "min": 0.0,
                "max": 100.0,
                "q1": 25.0,
                "q3": 75.0,
                "count": 0
            }
        
        try:
            sorted_scores = sorted(scores)
            n = len(sorted_scores)
            
            return {
                "average": statistics.mean(scores),
                "median": statistics.median(scores),
                "std_dev": statistics.stdev(scores) if n > 1 else 0.0,
                "min": min(scores),
                "max": max(scores),
                "q1": sorted_scores[n // 4] if n >= 4 else sorted_scores[0],
                "q3": sorted_scores[3 * n // 4] if n >= 4 else sorted_scores[-1],
                "count": n
            }
            
        except Exception as e:
            logger.warning(f"Failed to calculate score statistics: {str(e)}")
            return {
                "average": 50.0,
                "median": 50.0,
                "std_dev": 0.0,
                "min": 0.0,
                "max": 100.0,
                "q1": 25.0,
                "q3": 75.0,
                "count": 0
            }
    
    async def _get_peer_esg_scores(self, peer_tickers: List[str]) -> List[Dict[str, Any]]:
        """Get ESG scores for peer companies"""
        try:
            # Get recent ESG analyses for peer companies
            cutoff_date = datetime.utcnow() - timedelta(days=30)  # 30-day window
            
            filter_query = {
                "ticker": {"$in": peer_tickers},
                "type": "ai_esg_analysis",
                "analysis_timestamp": {"$gte": cutoff_date}
            }
            
            analyses = await self.analysis_repo.find_many(
                filter_query,
                sort=[("analysis_timestamp", -1)],
                limit=len(peer_tickers)
            )
            
            # Extract analysis data
            esg_scores = []
            for doc in analyses:
                analysis_data = doc.get("analysis", {})
                if analysis_data:
                    esg_scores.append(analysis_data)
            
            return esg_scores
            
        except Exception as e:
            logger.error(f"Failed to get peer ESG scores: {str(e)}")
            return []
    
    async def _calculate_company_position(
        self,
        ticker: str,
        benchmark_data: Dict[str, Any],
        market_cap: Optional[float] = None
    ) -> BenchmarkComparison:
        """Calculate company's position within industry benchmarks"""
        try:
            # Get company's ESG scores
            company_analysis = await self._get_company_esg_analysis(ticker)
            
            if not company_analysis:
                logger.warning(f"No ESG analysis found for {ticker}")
                return self._create_default_benchmark(ticker)
            
            # Extract company scores
            env_score = company_analysis.get("environmental_score", {}).get("score", 50)
            social_score = company_analysis.get("social_score", {}).get("score", 50)
            gov_score = company_analysis.get("governance_score", {}).get("score", 50)
            overall_score = company_analysis.get("overall_score", {}).get("score", 50)
            
            # Calculate percentile rankings
            env_percentile = self._calculate_percentile(
                env_score, 
                benchmark_data.get("environmental", {})
            )
            social_percentile = self._calculate_percentile(
                social_score,
                benchmark_data.get("social", {})
            )
            gov_percentile = self._calculate_percentile(
                gov_score,
                benchmark_data.get("governance", {})
            )
            overall_percentile = self._calculate_percentile(
                overall_score,
                benchmark_data.get("overall", {})
            )
            
            # Determine ranking position
            total_companies = benchmark_data.get("total_companies", 1)
            ranking_position = max(1, int(total_companies * (1 - overall_percentile / 100)))
            
            return BenchmarkComparison(
                industry_average=benchmark_data.get("overall", {}).get("average", 50),
                sector_average=benchmark_data.get("overall", {}).get("average", 50),
                market_cap_peer_average=benchmark_data.get("overall", {}).get("average", 50),
                percentile_rank=overall_percentile,
                top_quartile_threshold=benchmark_data.get("overall", {}).get("q3", 75),
                bottom_quartile_threshold=benchmark_data.get("overall", {}).get("q1", 25),
                peer_companies=benchmark_data.get("peer_tickers", [])[:10],  # Top 10 peers
                ranking_position=ranking_position,
                total_companies_compared=total_companies
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate company position for {ticker}: {str(e)}")
            return self._create_default_benchmark(ticker)
    
    def _calculate_percentile(self, score: float, benchmark_stats: Dict[str, float]) -> float:
        """Calculate percentile ranking for a score"""
        try:
            if not benchmark_stats or "average" not in benchmark_stats:
                return 50.0  # Default to median
            
            average = benchmark_stats.get("average", 50)
            std_dev = benchmark_stats.get("std_dev", 15)
            
            if std_dev == 0:
                return 50.0 if score == average else (75.0 if score > average else 25.0)
            
            # Calculate z-score
            z_score = (score - average) / std_dev
            
            # Convert to percentile (approximate using normal distribution)
            if z_score <= -2:
                percentile = 2.5
            elif z_score <= -1:
                percentile = 16
            elif z_score <= 0:
                percentile = 50
            elif z_score <= 1:
                percentile = 84
            elif z_score <= 2:
                percentile = 97.5
            else:
                percentile = 99
            
            return max(1, min(99, percentile))
            
        except Exception as e:
            logger.warning(f"Failed to calculate percentile: {str(e)}")
            return 50.0
    
    async def _get_company_esg_analysis(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get company's latest ESG analysis"""
        try:
            latest_analysis = await self.analysis_repo.find_one(
                {"ticker": ticker, "type": "ai_esg_analysis"},
                sort=[("analysis_timestamp", -1)]
            )
            
            if latest_analysis:
                return latest_analysis.get("analysis")
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get ESG analysis for {ticker}: {str(e)}")
            return None
    
    async def _get_cached_benchmark(
        self, 
        sector: str, 
        industry: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached benchmark data if available and fresh"""
        try:
            cache_cutoff = datetime.utcnow() - timedelta(hours=24)  # 24-hour cache
            
            cached_doc = await self.benchmark_repo.find_one({
                "sector": sector,
                "industry": industry,
                "type": "industry_benchmark",
                "last_updated": {"$gte": cache_cutoff}
            })
            
            if cached_doc:
                return cached_doc.get("benchmark_data")
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get cached benchmark: {str(e)}")
            return None
    
    async def _cache_benchmarks(
        self, 
        sector: str, 
        industry: str, 
        benchmark_data: Dict[str, Any]
    ):
        """Cache benchmark data"""
        try:
            document = {
                "sector": sector,
                "industry": industry,
                "type": "industry_benchmark",
                "benchmark_data": benchmark_data,
                "last_updated": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=24)
            }
            
            await self.benchmark_repo.upsert(
                {"sector": sector, "industry": industry, "type": "industry_benchmark"},
                document
            )
            
        except Exception as e:
            logger.error(f"Failed to cache benchmark data: {str(e)}")
    
    def _create_default_benchmark(self, ticker: str) -> BenchmarkComparison:
        """Create default benchmark when no data available"""
        return BenchmarkComparison(
            industry_average=50.0,
            sector_average=50.0,
            market_cap_peer_average=50.0,
            percentile_rank=50.0,
            top_quartile_threshold=75.0,
            bottom_quartile_threshold=25.0,
            peer_companies=[],
            ranking_position=None,
            total_companies_compared=1
        )
    
    def _create_default_benchmark_data(self, sector: str, industry: str) -> Dict[str, Any]:
        """Create default benchmark data structure"""
        default_stats = {
            "average": 50.0,
            "median": 50.0,
            "std_dev": 15.0,
            "min": 0.0,
            "max": 100.0,
            "q1": 35.0,
            "q3": 65.0,
            "count": 0
        }
        
        return {
            "sector": sector,
            "industry": industry,
            "total_companies": 0,
            "peer_tickers": [],
            "environmental": default_stats.copy(),
            "social": default_stats.copy(),
            "governance": default_stats.copy(),
            "overall": default_stats.copy(),
            "market_cap_range": {
                "min": 0,
                "max": 0,
                "median": 0
            },
            "last_updated": datetime.utcnow()
        }
    
    async def get_sector_benchmark(self, sector: str) -> Dict[str, Any]:
        """Get sector-wide benchmark statistics"""
        try:
            # Get all companies in sector
            sector_companies = await self.company_repo.find_many(
                {"sector": sector, "exists": True},
                limit=200
            )
            
            if not sector_companies:
                return self._create_sector_default(sector)
            
            # Get ESG analyses for sector companies
            sector_tickers = [company["ticker"] for company in sector_companies]
            sector_analyses = await self._get_peer_esg_scores(sector_tickers)
            
            # Calculate sector statistics
            sector_stats = self._calculate_sector_statistics(sector, sector_analyses)
            
            return sector_stats
            
        except Exception as e:
            logger.error(f"Failed to get sector benchmark for {sector}: {str(e)}")
            return self._create_sector_default(sector)
    
    def _calculate_sector_statistics(
        self, 
        sector: str, 
        analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate sector-wide statistics"""
        try:
            if not analyses:
                return self._create_sector_default(sector)
            
            # Extract all scores
            env_scores = []
            social_scores = []
            gov_scores = []
            overall_scores = []
            
            for analysis in analyses:
                if analysis.get("environmental_score"):
                    env_scores.append(analysis["environmental_score"]["score"])
                if analysis.get("social_score"):
                    social_scores.append(analysis["social_score"]["score"])
                if analysis.get("governance_score"):
                    gov_scores.append(analysis["governance_score"]["score"])
                if analysis.get("overall_score"):
                    overall_scores.append(analysis["overall_score"]["score"])
            
            return {
                "sector": sector,
                "total_companies_analyzed": len(analyses),
                "environmental": self._calculate_score_statistics(env_scores),
                "social": self._calculate_score_statistics(social_scores),
                "governance": self._calculate_score_statistics(gov_scores),
                "overall": self._calculate_score_statistics(overall_scores),
                "sector_leaders": self._identify_sector_leaders(analyses),
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate sector statistics: {str(e)}")
            return self._create_sector_default(sector)
    
    def _identify_sector_leaders(self, analyses: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Identify sector leaders in each ESG category"""
        try:
            # Sort by each category
            env_leaders = sorted(
                analyses,
                key=lambda x: x.get("environmental_score", {}).get("score", 0),
                reverse=True
            )[:5]
            
            social_leaders = sorted(
                analyses,
                key=lambda x: x.get("social_score", {}).get("score", 0),
                reverse=True
            )[:5]
            
            gov_leaders = sorted(
                analyses,
                key=lambda x: x.get("governance_score", {}).get("score", 0),
                reverse=True
            )[:5]
            
            overall_leaders = sorted(
                analyses,
                key=lambda x: x.get("overall_score", {}).get("score", 0),
                reverse=True
            )[:5]
            
            return {
                "environmental": [a.get("ticker", "") for a in env_leaders],
                "social": [a.get("ticker", "") for a in social_leaders],
                "governance": [a.get("ticker", "") for a in gov_leaders],
                "overall": [a.get("ticker", "") for a in overall_leaders]
            }
            
        except Exception as e:
            logger.warning(f"Failed to identify sector leaders: {str(e)}")
            return {
                "environmental": [],
                "social": [],
                "governance": [],
                "overall": []
            }
    
    def _create_sector_default(self, sector: str) -> Dict[str, Any]:
        """Create default sector statistics"""
        default_stats = {
            "average": 50.0,
            "median": 50.0,
            "std_dev": 15.0,
            "min": 0.0,
            "max": 100.0,
            "q1": 35.0,
            "q3": 65.0,
            "count": 0
        }
        
        return {
            "sector": sector,
            "total_companies_analyzed": 0,
            "environmental": default_stats.copy(),
            "social": default_stats.copy(),
            "governance": default_stats.copy(),
            "overall": default_stats.copy(),
            "sector_leaders": {
                "environmental": [],
                "social": [],
                "governance": [],
                "overall": []
            },
            "last_updated": datetime.utcnow()
        }
    
    async def get_benchmark_trends(
        self, 
        sector: str, 
        industry: str, 
        days: int = 90
    ) -> Dict[str, Any]:
        """Get benchmark trends over time"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get historical benchmark data
            historical_benchmarks = await self.benchmark_repo.find_many(
                {
                    "sector": sector,
                    "industry": industry,
                    "type": "industry_benchmark",
                    "last_updated": {"$gte": cutoff_date}
                },
                sort=[("last_updated", 1)]
            )
            
            if not historical_benchmarks:
                return {"message": "No historical data available"}
            
            # Calculate trends
            trends = self._calculate_benchmark_trends(historical_benchmarks)
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get benchmark trends: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_benchmark_trends(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Calculate trend analysis from historical benchmarks"""
        try:
            if len(historical_data) < 2:
                return {"message": "Insufficient data for trend analysis"}
            
            # Extract time series data
            timestamps = []
            env_averages = []
            social_averages = []
            gov_averages = []
            overall_averages = []
            
            for benchmark in historical_data:
                benchmark_data = benchmark.get("benchmark_data", {})
                timestamps.append(benchmark.get("last_updated"))
                
                env_averages.append(benchmark_data.get("environmental", {}).get("average", 50))
                social_averages.append(benchmark_data.get("social", {}).get("average", 50))
                gov_averages.append(benchmark_data.get("governance", {}).get("average", 50))
                overall_averages.append(benchmark_data.get("overall", {}).get("average", 50))
            
            # Calculate trend directions
            def calculate_trend(values):
                if len(values) < 2:
                    return "stable"
                recent = values[-3:] if len(values) >= 3 else values
                if all(recent[i] <= recent[i+1] for i in range(len(recent)-1)):
                    return "improving"
                elif all(recent[i] >= recent[i+1] for i in range(len(recent)-1)):
                    return "declining"
                else:
                    return "volatile"
            
            return {
                "time_period_days": (timestamps[-1] - timestamps[0]).days,
                "data_points": len(historical_data),
                "trends": {
                    "environmental": {
                        "direction": calculate_trend(env_averages),
                        "start_value": env_averages[0],
                        "end_value": env_averages[-1],
                        "change": env_averages[-1] - env_averages[0]
                    },
                    "social": {
                        "direction": calculate_trend(social_averages),
                        "start_value": social_averages[0],
                        "end_value": social_averages[-1],
                        "change": social_averages[-1] - social_averages[0]
                    },
                    "governance": {
                        "direction": calculate_trend(gov_averages),
                        "start_value": gov_averages[0],
                        "end_value": gov_averages[-1],
                        "change": gov_averages[-1] - gov_averages[0]
                    },
                    "overall": {
                        "direction": calculate_trend(overall_averages),
                        "start_value": overall_averages[0],
                        "end_value": overall_averages[-1],
                        "change": overall_averages[-1] - overall_averages[0]
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate benchmark trends: {str(e)}")
            return {"error": str(e)}


# Global service instance
benchmark_service = BenchmarkService()


def get_benchmark_service() -> BenchmarkService:
    """Get benchmark service instance"""
    return benchmark_service