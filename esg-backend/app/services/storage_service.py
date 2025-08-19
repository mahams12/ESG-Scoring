"""
Storage service for managing ESG data persistence and retrieval
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from loguru import logger
import json

from app.config import get_settings
from app.models.esg_analysis import ESGAnalysis
from app.models.company import Company, FinancialMetrics
from app.database import DatabaseRepository, get_database


class StorageService:
    """Service for managing data storage, retrieval, and lifecycle"""
    
    def __init__(self):
        self.settings = get_settings()
        self.company_repo = DatabaseRepository("companies")
        self.esg_repo = DatabaseRepository("esg_scores")
        self.analysis_repo = DatabaseRepository("ai_analysis")
        self.benchmark_repo = DatabaseRepository("benchmarks")
        self.news_repo = DatabaseRepository("news_data")
        
    async def store_esg_analysis(
        self, 
        ticker: str, 
        analysis: ESGAnalysis
    ) -> str:
        """
        Store complete ESG analysis with versioning
        
        Args:
            ticker: Company ticker symbol
            analysis: Complete ESG analysis object
            
        Returns:
            Document ID of stored analysis
        """
        try:
            # Prepare document for storage
            document = {
                "ticker": ticker,
                "type": "complete_esg_analysis",
                "analysis": analysis.dict(),
                "analysis_timestamp": analysis.analysis_timestamp,
                "version": analysis.analysis_version,
                "data_sources": analysis.data_sources,
                "confidence_score": analysis.ai_confidence,
                "expires_at": datetime.utcnow() + timedelta(
                    seconds=self.settings.caching.analysis_results_ttl
                )
            }
            
            # Store with upsert to handle updates
            result_id = await self.esg_repo.upsert(
                {
                    "ticker": ticker, 
                    "type": "complete_esg_analysis"
                },
                document
            )
            
            # Also store in analysis repo for AI tracking
            await self.analysis_repo.upsert(
                {
                    "ticker": ticker, 
                    "type": "ai_esg_analysis"
                },
                {
                    "ticker": ticker,
                    "type": "ai_esg_analysis",
                    "analysis": analysis.dict(),
                    "analysis_timestamp": analysis.analysis_timestamp,
                    "ai_confidence": analysis.ai_confidence
                }
            )
            
            logger.info(f"Stored ESG analysis for {ticker}")
            return str(result_id)
            
        except Exception as e:
            logger.error(f"Failed to store ESG analysis for {ticker}: {str(e)}")
            raise
    
    async def get_latest_esg_analysis(self, ticker: str) -> Optional[ESGAnalysis]:
        """
        Get the most recent ESG analysis for a company
        
        Args:
            ticker: Company ticker symbol
            
        Returns:
            Latest ESG analysis or None if not found
        """
        try:
            # Get latest analysis
            latest_doc = await self.esg_repo.find_one(
                {
                    "ticker": ticker,
                    "type": "complete_esg_analysis"
                },
                sort=[("analysis_timestamp", -1)]
            )
            
            if latest_doc and latest_doc.get("analysis"):
                analysis_data = latest_doc["analysis"]
                return ESGAnalysis(**analysis_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get ESG analysis for {ticker}: {str(e)}")
            return None
    
    async def store_financial_data(
        self, 
        ticker: str, 
        financial_data: Dict[str, Any]
    ) -> str:
        """Store financial data with timestamp"""
        try:
            document = {
                "ticker": ticker,
                "type": "financial_data",
                "data": financial_data,
                "collection_timestamp": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(
                    seconds=self.settings.caching.financial_data_ttl
                )
            }
            
            result_id = await self.esg_repo.upsert(
                {
                    "ticker": ticker, 
                    "type": "financial_data"
                },
                document
            )
            
            return str(result_id)
            
        except Exception as e:
            logger.error(f"Failed to store financial data for {ticker}: {str(e)}")
            raise
    
    async def store_news_data(
        self, 
        ticker: str, 
        news_articles: List[Dict[str, Any]]
    ) -> str:
        """Store news and sentiment data"""
        try:
            document = {
                "ticker": ticker,
                "type": "news_sentiment",
                "articles": news_articles,
                "article_count": len(news_articles),
                "collection_timestamp": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(
                    seconds=self.settings.caching.news_data_ttl
                )
            }
            
            result_id = await self.news_repo.upsert(
                {
                    "ticker": ticker, 
                    "type": "news_sentiment"
                },
                document
            )
            
            return str(result_id)
            
        except Exception as e:
            logger.error(f"Failed to store news data for {ticker}: {str(e)}")
            raise
    
    async def get_cached_data(
        self, 
        ticker: str, 
        data_type: str,
        max_age_hours: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached data if within age limit
        
        Args:
            ticker: Company ticker symbol
            data_type: Type of data to retrieve
            max_age_hours: Maximum age of data in hours
            
        Returns:
            Cached data or None if not found/expired
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            # Determine which repository to use
            repo_map = {
                "financial_data": self.esg_repo,
                "news_sentiment": self.news_repo,
                "esg_analysis": self.esg_repo,
                "benchmark_data": self.benchmark_repo
            }
            
            repo = repo_map.get(data_type, self.esg_repo)
            
            cached_doc = await repo.find_one(
                {
                    "ticker": ticker,
                    "type": data_type,
                    "collection_timestamp": {"$gte": cutoff_time}
                },
                sort=[("collection_timestamp", -1)]
            )
            
            if cached_doc:
                return cached_doc.get("data") or cached_doc.get("analysis")
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get cached data for {ticker}: {str(e)}")
            return None
    
    async def store_company_metrics(
        self, 
        ticker: str, 
        metrics: FinancialMetrics
    ):
        """Store financial metrics in company record"""
        try:
            await self.company_repo.update_one(
                {"ticker": ticker},
                {
                    "financial_metrics": metrics.dict(exclude_none=True),
                    "last_financial_update": datetime.utcnow()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to store company metrics for {ticker}: {str(e)}")
    
    async def get_analysis_history(
        self, 
        ticker: str, 
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get historical ESG analysis data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            history = await self.esg_repo.find_many(
                {
                    "ticker": ticker,
                    "type": "complete_esg_analysis",
                    "analysis_timestamp": {"$gte": cutoff_date}
                },
                sort=[("analysis_timestamp", -1)]
            )
            
            return [
                {
                    "timestamp": doc["analysis_timestamp"],
                    "overall_score": doc.get("analysis", {}).get("overall_score", {}).get("score"),
                    "environmental_score": doc.get("analysis", {}).get("environmental_score", {}).get("score"),
                    "social_score": doc.get("analysis", {}).get("social_score", {}).get("score"),
                    "governance_score": doc.get("analysis", {}).get("governance_score", {}).get("score"),
                    "confidence": doc.get("confidence_score")
                }
                for doc in history
                if doc.get("analysis")
            ]
            
        except Exception as e:
            logger.error(f"Failed to get analysis history for {ticker}: {str(e)}")
            return []
    
    async def cleanup_expired_data(self):
        """Clean up expired cached data"""
        try:
            current_time = datetime.utcnow()
            
            # Clean up each repository
            repositories = [
                self.esg_repo,
                self.news_repo,
                self.analysis_repo,
                self.benchmark_repo
            ]
            
            total_cleaned = 0
            
            for repo in repositories:
                try:
                    # Delete expired documents
                    result = await repo.delete_many(
                        {"expires_at": {"$lt": current_time}}
                    )
                    total_cleaned += result.deleted_count if hasattr(result, 'deleted_count') else 0
                    
                except Exception as e:
                    logger.warning(f"Failed to cleanup repository {repo.collection_name}: {str(e)}")
            
            if total_cleaned > 0:
                logger.info(f"Cleaned up {total_cleaned} expired documents")
            
            return total_cleaned
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {str(e)}")
            return 0
    
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        try:
            db = await get_database()
            db_stats = await db.get_database_stats()
            
            # Get collection-specific stats
            collection_stats = {}
            
            repos = {
                "companies": self.company_repo,
                "esg_scores": self.esg_repo,
                "ai_analysis": self.analysis_repo,
                "benchmarks": self.benchmark_repo,
                "news_data": self.news_repo
            }
            
            for name, repo in repos.items():
                try:
                    total_docs = await repo.count()
                    
                    # Count by type if applicable
                    type_counts = {}
                    if name != "companies":
                        type_pipeline = [
                            {"$group": {"_id": "$type", "count": {"$sum": 1}}},
                            {"$sort": {"count": -1}}
                        ]
                        type_results = await repo.aggregate(type_pipeline)
                        type_counts = {
                            result["_id"]: result["count"] 
                            for result in type_results
                        }
                    
                    collection_stats[name] = {
                        "total_documents": total_docs,
                        "type_breakdown": type_counts
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to get stats for {name}: {str(e)}")
                    collection_stats[name] = {"error": str(e)}
            
            return {
                "database_stats": db_stats,
                "collection_stats": collection_stats,
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage statistics: {str(e)}")
            return {"error": str(e)}
    
    async def export_company_data(
        self, 
        ticker: str, 
        include_history: bool = True
    ) -> Dict[str, Any]:
        """Export all data for a specific company"""
        try:
            exported_data = {
                "ticker": ticker,
                "export_timestamp": datetime.utcnow(),
                "data": {}
            }
            
            # Get company information
            company_doc = await self.company_repo.find_one({"ticker": ticker})
            if company_doc:
                exported_data["data"]["company_info"] = company_doc
            
            # Get latest ESG analysis
            latest_analysis = await self.get_latest_esg_analysis(ticker)
            if latest_analysis:
                exported_data["data"]["latest_esg_analysis"] = latest_analysis.dict()
            
            # Get analysis history if requested
            if include_history:
                history = await self.get_analysis_history(ticker, days=365)
                exported_data["data"]["analysis_history"] = history
            
            # Get latest financial data
            financial_data = await self.get_cached_data(ticker, "financial_data", max_age_hours=24)
            if financial_data:
                exported_data["data"]["financial_data"] = financial_data
            
            # Get recent news data
            news_data = await self.get_cached_data(ticker, "news_sentiment", max_age_hours=24)
            if news_data:
                exported_data["data"]["news_sentiment"] = news_data
            
            return exported_data
            
        except Exception as e:
            logger.error(f"Failed to export data for {ticker}: {str(e)}")
            return {"error": str(e), "ticker": ticker}
    
    async def bulk_update_expires_at(
        self, 
        collection_type: str, 
        new_ttl_seconds: int
    ):
        """Bulk update expiration times for a collection type"""
        try:
            new_expires_at = datetime.utcnow() + timedelta(seconds=new_ttl_seconds)
            
            repo_map = {
                "financial": self.esg_repo,
                "news": self.news_repo,
                "analysis": self.analysis_repo,
                "benchmarks": self.benchmark_repo
            }
            
            repo = repo_map.get(collection_type)
            if not repo:
                raise ValueError(f"Unknown collection type: {collection_type}")
            
            # Update all documents of this type
            filter_query = {"type": {"$regex": collection_type}}
            update_query = {"expires_at": new_expires_at}
            
            result = await repo.update_many(filter_query, update_query)
            
            logger.info(f"Updated {getattr(result, 'modified_count', 0)} documents in {collection_type}")
            
        except Exception as e:
            logger.error(f"Failed to bulk update expires_at: {str(e)}")
    
    async def health_check(self) -> Dict[str, bool]:
        """Check storage service health"""
        try:
            health_status = {}
            
            # Test each repository
            repos = {
                "companies": self.company_repo,
                "esg_scores": self.esg_repo,
                "ai_analysis": self.analysis_repo,
                "benchmarks": self.benchmark_repo,
                "news_data": self.news_repo
            }
            
            for name, repo in repos.items():
                try:
                    # Test basic connectivity by counting documents
                    count = await repo.count({})
                    health_status[name] = True
                except Exception as e:
                    logger.error(f"Health check failed for {name}: {str(e)}")
                    health_status[name] = False
            
            return health_status
            
        except Exception as e:
            logger.error(f"Storage service health check failed: {str(e)}")
            return {"storage_service": False}


# Global service instance
storage_service = StorageService()


def get_storage_service() -> StorageService:
    """Get storage service instance"""
    return storage_service