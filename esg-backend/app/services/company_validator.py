"""
Company validation service for ESG Investment Research System
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from loguru import logger
import yfinance as yf
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.config import get_settings
from app.models.company import (
    CompanyValidationResult, CompanyInfo, CompanyStatus, 
    FinancialMetrics, classify_market_cap
)
from app.models.responses import ProcessingMetadata
from app.database import DatabaseRepository


class CompanyValidationService:
    """Service for validating company existence and gathering basic information"""
    
    def __init__(self):
        self.settings = get_settings()
        self.company_repo = DatabaseRepository("companies")
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _normalize_ticker(self, ticker: str) -> str:
        """Normalize ticker symbol"""
        if not ticker:
            raise ValueError("Ticker cannot be empty")
        
        # Remove whitespace and convert to uppercase
        normalized = ticker.strip().upper()
        
        # Basic validation
        if not re.match(r'^[A-Z0-9.-]{1,10}$', normalized):
            raise ValueError(f"Invalid ticker format: {ticker}")
        
        return normalized
    
    async def validate_company(
        self, 
        ticker: str, 
        force_refresh: bool = False
    ) -> CompanyValidationResult:
        """
        Validate if a company exists and is publicly traded
        
        Args:
            ticker: Stock ticker symbol
            force_refresh: Force fresh validation ignoring cache
            
        Returns:
            CompanyValidationResult with validation details
        """
        start_time = datetime.utcnow()
        
        try:
            # Normalize ticker
            ticker = self._normalize_ticker(ticker)
            
            # Check cache first (unless force refresh)
            if not force_refresh:
                cached_result = await self._get_cached_validation(ticker)
                if cached_result:
                    logger.info(f"Using cached validation for {ticker}")
                    return cached_result
            
            # Perform validation using multiple sources
            validation_tasks = [
                self._validate_with_yahoo_finance(ticker),
                self._validate_with_fmp(ticker),
                self._validate_with_alphavantage(ticker)
            ]
            
            # Run validations concurrently
            results = await asyncio.gather(*validation_tasks, return_exceptions=True)
            
            # Process results and determine final validation
            final_result = await self._consolidate_validation_results(
                ticker, results, start_time
            )
            
            # Cache the result
            await self._cache_validation_result(final_result)
            
            return final_result
            
        except ValueError as e:
            return CompanyValidationResult(
                ticker=ticker,
                status=CompanyStatus.INVALID,
                exists=False,
                message=str(e),
                data_sources_checked=["validation"],
                confidence_score=1.0
            )
        except Exception as e:
            logger.error(f"Validation error for {ticker}: {str(e)}")
            return CompanyValidationResult(
                ticker=ticker,
                status=CompanyStatus.ERROR,
                exists=False,
                message=f"Validation failed: {str(e)}",
                data_sources_checked=["validation"],
                confidence_score=0.0
            )
    
    async def _get_cached_validation(self, ticker: str) -> Optional[CompanyValidationResult]:
        """Get cached validation result if still valid"""
        try:
            # Look for recent validation (within cache TTL)
            cache_cutoff = datetime.utcnow() - timedelta(
                seconds=self.settings.caching.company_validation_ttl
            )
            
            cached_company = await self.company_repo.find_one({
                "ticker": ticker,
                "last_validated": {"$gte": cache_cutoff}
            })
            
            if cached_company:
                return CompanyValidationResult(
                    ticker=ticker,
                    status=CompanyStatus(cached_company.get("status", "valid")),
                    exists=cached_company.get("exists", True),
                    message="Company validation successful (cached)",
                    company_info=CompanyInfo(**cached_company) if cached_company.get("exists") else None,
                    data_sources_checked=cached_company.get("data_sources", []),
                    confidence_score=cached_company.get("confidence_score", 0.8)
                )
                
        except Exception as e:
            logger.warning(f"Failed to get cached validation for {ticker}: {str(e)}")
        
        return None
    
    async def _validate_with_yahoo_finance(self, ticker: str) -> Dict[str, Any]:
        """Validate company using Yahoo Finance"""
        try:
            # Create yfinance ticker object
            stock = yf.Ticker(ticker)
            
            # Get basic info
            info = stock.info
            
            if not info or 'longName' not in info:
                return {
                    "source": "yahoo_finance",
                    "success": False,
                    "error": "No company data found"
                }
            
            # Extract company information
            company_info = {
                "name": info.get("longName", ""),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
                "employees": info.get("fullTimeEmployees"),
                "website": info.get("website"),
                "description": info.get("longBusinessSummary"),
                "currency": info.get("currency", "USD"),
                "exchange": info.get("exchange"),
                "country": info.get("country"),
                "headquarters": f"{info.get('city', '')}, {info.get('state', '')} {info.get('country', '')}".strip(", ")
            }
            
            # Get recent stock data to verify trading status
            try:
                hist = stock.history(period="5d")
                is_actively_traded = len(hist) > 0 and not hist.empty
            except:
                is_actively_traded = True  # Assume trading if can't verify
            
            return {
                "source": "yahoo_finance",
                "success": True,
                "company_info": company_info,
                "is_actively_traded": is_actively_traded,
                "confidence": 0.9 if is_actively_traded else 0.7
            }
            
        except Exception as e:
            logger.warning(f"Yahoo Finance validation failed for {ticker}: {str(e)}")
            return {
                "source": "yahoo_finance",
                "success": False,
                "error": str(e)
            }
    
    async def _validate_with_fmp(self, ticker: str) -> Dict[str, Any]:
        """Validate company using Financial Modeling Prep API"""
        try:
            url = f"{self.settings.api.fmp_base_url}/profile/{ticker}"
            params = {"apikey": self.settings.api.fmp_api_key}
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or not isinstance(data, list) or len(data) == 0:
                return {
                    "source": "financial_modeling_prep",
                    "success": False,
                    "error": "No company profile found"
                }
            
            profile = data[0]
            
            company_info = {
                "name": profile.get("companyName", ""),
                "sector": profile.get("sector"),
                "industry": profile.get("industry"),
                "market_cap": profile.get("mktCap"),
                "employees": profile.get("fullTimeEmployees"),
                "website": profile.get("website"),
                "description": profile.get("description"),
                "currency": profile.get("currency", "USD"),
                "exchange": profile.get("exchangeShortName"),
                "country": profile.get("country"),
                "headquarters": f"{profile.get('city', '')}, {profile.get('state', '')} {profile.get('country', '')}".strip(", "),
                "founded_year": profile.get("foundedYear")
            }
            
            return {
                "source": "financial_modeling_prep",
                "success": True,
                "company_info": company_info,
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.warning(f"FMP validation failed for {ticker}: {str(e)}")
            return {
                "source": "financial_modeling_prep",
                "success": False,
                "error": str(e)
            }
    
    async def _validate_with_alphavantage(self, ticker: str) -> Dict[str, Any]:
        """Validate company using Alpha Vantage API"""
        try:
            # Company overview endpoint
            url = f"{self.settings.api.alphavantage_base_url}/query"
            params = {
                "function": "OVERVIEW",
                "symbol": ticker,
                "apikey": self.settings.api.alphavantage_api_key
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if we got valid data
            if not data or "Symbol" not in data or data.get("Symbol") != ticker:
                return {
                    "source": "alpha_vantage",
                    "success": False,
                    "error": "No company data found"
                }
            
            # Extract company information
            company_info = {
                "name": data.get("Name", ""),
                "sector": data.get("Sector"),
                "industry": data.get("Industry"),
                "market_cap": self._safe_convert_to_float(data.get("MarketCapitalization")),
                "employees": self._safe_convert_to_int(data.get("FullTimeEmployees")),
                "description": data.get("Description"),
                "exchange": data.get("Exchange"),
                "country": data.get("Country"),
                "currency": data.get("Currency"),
                "headquarters": f"{data.get('Address', '')}, {data.get('Country', '')}".strip(", ")
            }
            
            return {
                "source": "alpha_vantage",
                "success": True,
                "company_info": company_info,
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.warning(f"Alpha Vantage validation failed for {ticker}: {str(e)}")
            return {
                "source": "alpha_vantage",
                "success": False,
                "error": str(e)
            }
    
    def _safe_convert_to_float(self, value: str) -> Optional[float]:
        """Safely convert string to float"""
        if not value or value == "None":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_convert_to_int(self, value: str) -> Optional[int]:
        """Safely convert string to int"""
        if not value or value == "None":
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    async def _consolidate_validation_results(
        self, 
        ticker: str, 
        results: List, 
        start_time: datetime
    ) -> CompanyValidationResult:
        """Consolidate validation results from multiple sources"""
        
        successful_results = []
        data_sources_checked = []
        errors = []
        
        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
                continue
                
            data_sources_checked.append(result.get("source", "unknown"))
            
            if result.get("success"):
                successful_results.append(result)
            else:
                errors.append(f"{result.get('source')}: {result.get('error', 'Unknown error')}")
        
        # Determine if company exists based on successful validations
        if not successful_results:
            return CompanyValidationResult(
                ticker=ticker,
                status=CompanyStatus.INVALID,
                exists=False,
                message=f"Company '{ticker}' does not exist or is not publicly traded. Please check the ticker symbol and try again.",
                data_sources_checked=data_sources_checked,
                confidence_score=0.9  # High confidence in non-existence if all sources fail
            )
        
        # Merge company information from successful sources
        merged_info = self._merge_company_info(successful_results)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(successful_results, len(data_sources_checked))
        
        # Create company info object
        company_info = CompanyInfo(
            ticker=ticker,
            **merged_info
        )
        
        # Set market cap category
        if company_info.market_cap:
            company_info.market_cap_category = classify_market_cap(company_info.market_cap)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return CompanyValidationResult(
            ticker=ticker,
            status=CompanyStatus.VALID,
            exists=True,
            message="Company validation successful",
            company_info=company_info,
            data_sources_checked=data_sources_checked,
            confidence_score=confidence_score
        )
    
    def _merge_company_info(self, successful_results: List[Dict]) -> Dict[str, Any]:
        """Merge company information from multiple sources"""
        merged = {}
        
        # Priority order for data sources (highest to lowest confidence)
        source_priority = {
            "financial_modeling_prep": 3,
            "yahoo_finance": 2,
            "alpha_vantage": 1
        }
        
        # Sort results by priority
        sorted_results = sorted(
            successful_results, 
            key=lambda x: source_priority.get(x.get("source", ""), 0), 
            reverse=True
        )
        
        # Merge data, giving priority to higher-confidence sources
        for result in sorted_results:
            company_data = result.get("company_info", {})
            
            for key, value in company_data.items():
                if value and (key not in merged or not merged[key]):
                    merged[key] = value
        
        # Clean up headquarters field
        if merged.get("headquarters"):
            merged["headquarters"] = re.sub(r',\s*,', ',', merged["headquarters"]).strip(", ")
            if merged["headquarters"] in [",", ", ,", ""]:
                merged["headquarters"] = None
        
        return merged
    
    def _calculate_confidence_score(self, successful_results: List[Dict], total_sources: int) -> float:
        """Calculate confidence score based on validation results"""
        if not successful_results:
            return 0.0
        
        # Base confidence from number of successful validations
        success_ratio = len(successful_results) / max(total_sources, 1)
        base_confidence = success_ratio * 0.6
        
        # Add confidence from individual source confidence scores
        source_confidence = sum(result.get("confidence", 0.5) for result in successful_results) / len(successful_results)
        
        # Combine scores
        final_confidence = base_confidence + (source_confidence * 0.4)
        
        return min(final_confidence, 1.0)
    
    async def _cache_validation_result(self, result: CompanyValidationResult):
        """Cache validation result in database"""
        try:
            document = {
                "ticker": result.ticker,
                "status": result.status.value,
                "exists": result.exists,
                "last_validated": result.validation_timestamp,
                "data_sources": result.data_sources_checked,
                "confidence_score": result.confidence_score
            }
            
            # Add company info if exists
            if result.company_info:
                document.update(result.company_info.dict(exclude_none=True))
            
            # Upsert the document
            await self.company_repo.upsert(
                {"ticker": result.ticker},
                document
            )
            
            logger.debug(f"Cached validation result for {result.ticker}")
            
        except Exception as e:
            logger.error(f"Failed to cache validation result for {result.ticker}: {str(e)}")
    
    async def get_company_info(self, ticker: str) -> Optional[CompanyInfo]:
        """Get stored company information"""
        try:
            ticker = self._normalize_ticker(ticker)
            
            company_doc = await self.company_repo.find_one({"ticker": ticker})
            
            if company_doc and company_doc.get("exists"):
                return CompanyInfo(**company_doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get company info for {ticker}: {str(e)}")
            return None
    
    async def search_companies(
        self, 
        query: str, 
        sector: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[CompanyInfo], int]:
        """Search for companies by name or ticker"""
        try:
            # Build search filter
            search_filter = {
                "exists": True,
                "$or": [
                    {"ticker": {"$regex": query, "$options": "i"}},
                    {"name": {"$regex": query, "$options": "i"}}
                ]
            }
            
            if sector:
                search_filter["sector"] = sector
            
            # Get total count
            total_count = await self.company_repo.count(search_filter)
            
            # Get paginated results
            companies_docs = await self.company_repo.find_many(
                search_filter,
                sort=[("market_cap", -1), ("name", 1)],
                limit=limit
            )
            
            companies = [CompanyInfo(**doc) for doc in companies_docs[offset:offset+limit]]
            
            return companies, total_count
            
        except Exception as e:
            logger.error(f"Failed to search companies: {str(e)}")
            return [], 0
    
    async def get_industry_peers(
        self, 
        ticker: str, 
        limit: int = 10
    ) -> List[CompanyInfo]:
        """Get industry peer companies"""
        try:
            # Get the company's industry information
            company = await self.get_company_info(ticker)
            if not company or not company.industry:
                return []
            
            # Find peers in the same industry
            peers_filter = {
                "exists": True,
                "industry": company.industry,
                "ticker": {"$ne": ticker}
            }
            
            peers_docs = await self.company_repo.find_many(
                peers_filter,
                sort=[("market_cap", -1)],
                limit=limit
            )
            
            return [CompanyInfo(**doc) for doc in peers_docs]
            
        except Exception as e:
            logger.error(f"Failed to get industry peers for {ticker}: {str(e)}")
            return []
    
    async def update_company_financial_metrics(
        self, 
        ticker: str, 
        financial_metrics: FinancialMetrics
    ):
        """Update company financial metrics"""
        try:
            ticker = self._normalize_ticker(ticker)
            
            await self.company_repo.update_one(
                {"ticker": ticker},
                {
                    "financial_metrics": financial_metrics.dict(exclude_none=True),
                    "last_financial_update": datetime.utcnow()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to update financial metrics for {ticker}: {str(e)}")
    
    async def bulk_validate_companies(
        self, 
        tickers: List[str],
        force_refresh: bool = False
    ) -> List[CompanyValidationResult]:
        """Validate multiple companies in bulk"""
        try:
            # Normalize all tickers
            normalized_tickers = [self._normalize_ticker(ticker) for ticker in tickers]
            
            # Create validation tasks
            tasks = [
                self.validate_company(ticker, force_refresh) 
                for ticker in normalized_tickers
            ]
            
            # Run validations concurrently with some limit to avoid overwhelming APIs
            batch_size = 5
            results = []
            
            for i in range(0, len(tasks), batch_size):
                batch = tasks[i:i + batch_size]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        # Create error result for failed validation
                        ticker = normalized_tickers[len(results)]
                        results.append(CompanyValidationResult(
                            ticker=ticker,
                            status=CompanyStatus.ERROR,
                            exists=False,
                            message=f"Validation failed: {str(result)}",
                            confidence_score=0.0
                        ))
                    else:
                        results.append(result)
                
                # Small delay between batches to be respectful to APIs
                if i + batch_size < len(tasks):
                    await asyncio.sleep(1)
            
            return results
            
        except Exception as e:
            logger.error(f"Bulk validation failed: {str(e)}")
            return []
    
    async def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        try:
            # Get total companies
            total_companies = await self.company_repo.count({"exists": True})
            
            # Get companies by status
            valid_companies = await self.company_repo.count({
                "exists": True, 
                "status": CompanyStatus.VALID.value
            })
            
            # Get recent validations (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_validations = await self.company_repo.count({
                "last_validated": {"$gte": yesterday}
            })
            
            # Get companies by sector
            sector_pipeline = [
                {"$match": {"exists": True, "sector": {"$ne": None}}},
                {"$group": {"_id": "$sector", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            sector_stats = await self.company_repo.aggregate(sector_pipeline)
            
            return {
                "total_companies": total_companies,
                "valid_companies": valid_companies,
                "recent_validations_24h": recent_validations,
                "top_sectors": sector_stats,
                "validation_success_rate": valid_companies / max(total_companies, 1)
            }
            
        except Exception as e:
            logger.error(f"Failed to get validation stats: {str(e)}")
            return {}


# Global service instance
company_validator = CompanyValidationService()


def get_company_validator() -> CompanyValidationService:
    """Get company validation service instance"""
    return company_validator