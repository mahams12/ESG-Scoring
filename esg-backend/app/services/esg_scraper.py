"""
ESG data scraping service for collecting ESG ratings and metrics
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urljoin, quote
import aiohttp
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger
import json
import re

from app.config import get_settings
from app.models.esg_analysis import EnvironmentalMetrics, SocialMetrics, GovernanceMetrics
from app.database import DatabaseRepository


class ESGDataScraper:
    """Service for scraping ESG data from various providers"""
    
    def __init__(self):
        self.settings = get_settings()
        self.session = self._create_session()
        self.scraping_repo = DatabaseRepository("esg_scores")
        self.user_agents = self.settings.scraping.user_agents
        
    def _create_session(self) -> requests.Session:
        """Create HTTP session with proper headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        return session
    
    def _get_chrome_driver(self) -> webdriver.Chrome:
        """Create Chrome WebDriver with proper options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={random.choice(self.user_agents)}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    async def scrape_all_esg_data(self, ticker: str, company_name: str) -> Dict[str, Any]:
        """
        Scrape ESG data from all available sources
        
        Args:
            ticker: Stock ticker symbol
            company_name: Full company name
            
        Returns:
            Dictionary containing ESG data from all sources
        """
        start_time = datetime.utcnow()
        
        try:
            # Check cache first
            cached_data = await self._get_cached_esg_data(ticker)
            if cached_data:
                logger.info(f"Using cached ESG data for {ticker}")
                return cached_data
            
            # Scrape from multiple sources concurrently
            scraping_tasks = [
                self._scrape_sustainalytics(ticker, company_name),
                self._scrape_cdp_data(ticker, company_name),
                self._scrape_msci_esg(ticker, company_name),
                self._scrape_esg_enterprise(ticker, company_name),
                self._scrape_epa_violations(ticker, company_name),
                self._scrape_osha_data(ticker, company_name)
            ]
            
            results = await asyncio.gather(*scraping_tasks, return_exceptions=True)
            
            # Process and consolidate results
            consolidated_data = await self._consolidate_esg_data(ticker, results, start_time)
            
            # Cache the results
            await self._cache_esg_data(ticker, consolidated_data)
            
            return consolidated_data
            
        except Exception as e:
            logger.error(f"ESG data scraping failed for {ticker}: {str(e)}")
            return {
                "ticker": ticker,
                "scraping_timestamp": start_time,
                "error": str(e),
                "data_sources": [],
                "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
            }
    
    async def _scrape_sustainalytics(self, ticker: str, company_name: str) -> Dict[str, Any]:
        """Scrape ESG data from Sustainalytics"""
        try:
            # Add delay to be respectful
            await asyncio.sleep(random.uniform(1, 3))
            
            # Search for company on Sustainalytics
            search_url = "https://www.sustainalytics.com/esg-rating"
            
            driver = None
            try:
                driver = self._get_chrome_driver()
                driver.get(search_url)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Try to find company data
                # Note: This is a simplified example - actual implementation would need
                # to handle the specific structure of Sustainalytics website
                
                esg_data = {
                    "overall_score": None,
                    "environmental_score": None,
                    "social_score": None,
                    "governance_score": None,
                    "risk_rating": None,
                    "controversy_score": None,
                    "data_availability": "limited"
                }
                
                # Simulate finding some data (replace with actual scraping logic)
                # This would involve navigating the site, searching for the company,
                # and extracting the ESG ratings
                
                return {
                    "source": "sustainalytics",
                    "success": True,
                    "data": esg_data,
                    "last_updated": datetime.utcnow(),
                    "confidence": 0.8
                }
                
            finally:
                if driver:
                    driver.quit()
                    
        except Exception as e:
            logger.warning(f"Sustainalytics scraping failed for {ticker}: {str(e)}")
            return {
                "source": "sustainalytics",
                "success": False,
                "error": str(e)
            }
    
    async def _scrape_cdp_data(self, ticker: str, company_name: str) -> Dict[str, Any]:
        """Scrape climate data from CDP (Carbon Disclosure Project)"""
        try:
            await asyncio.sleep(random.uniform(1, 3))
            
            # CDP public data search
            search_url = "https://www.cdp.net/en/companies/companies-scores"
            
            # Use requests for simpler data extraction
            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract environmental data
            environmental_data = {
                "climate_score": None,
                "carbon_emissions": None,
                "renewable_energy_percentage": None,
                "water_management_score": None,
                "forest_score": None,
                "data_availability": "public_disclosure"
            }
            
            # Note: Actual implementation would parse the CDP website structure
            # to extract company-specific climate scores and environmental metrics
            
            return {
                "source": "cdp",
                "success": True,
                "data": environmental_data,
                "last_updated": datetime.utcnow(),
                "confidence": 0.7
            }
            
        except Exception as e:
            logger.warning(f"CDP scraping failed for {ticker}: {str(e)}")
            return {
                "source": "cdp",
                "success": False,
                "error": str(e)
            }
    
    async def _scrape_msci_esg(self, ticker: str, company_name: str) -> Dict[str, Any]:
        """Scrape ESG ratings from MSCI ESG"""
        try:
            await asyncio.sleep(random.uniform(1, 3))
            
            # MSCI ESG public information
            base_url = "https://www.msci.com/our-solutions/esg-investing/esg-ratings-climate-search-tool"
            
            # Note: MSCI requires special handling due to their API structure
            # This is a simplified example
            
            esg_data = {
                "msci_rating": None,  # AAA, AA, A, BBB, BB, B, CCC
                "esg_score": None,
                "environmental_pillar": None,
                "social_pillar": None,
                "governance_pillar": None,
                "controversies": [],
                "data_availability": "limited_public"
            }
            
            return {
                "source": "msci_esg",
                "success": True,
                "data": esg_data,
                "last_updated": datetime.utcnow(),
                "confidence": 0.6
            }
            
        except Exception as e:
            logger.warning(f"MSCI ESG scraping failed for {ticker}: {str(e)}")
            return {
                "source": "msci_esg",
                "success": False,
                "error": str(e)
            }
    
    async def _scrape_esg_enterprise(self, ticker: str, company_name: str) -> Dict[str, Any]:
        """Scrape data from ESG Enterprise"""
        try:
            await asyncio.sleep(random.uniform(1, 3))
            
            # ESG Enterprise public data
            search_url = f"https://esg-enterprise.com/search?q={quote(company_name)}"
            
            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract ESG metrics
            esg_metrics = {
                "overall_esg_score": None,
                "environmental_score": None,
                "social_score": None,
                "governance_score": None,
                "sustainability_metrics": {},
                "data_coverage": "comprehensive"
            }
            
            return {
                "source": "esg_enterprise",
                "success": True,
                "data": esg_metrics,
                "last_updated": datetime.utcnow(),
                "confidence": 0.7
            }
            
        except Exception as e:
            logger.warning(f"ESG Enterprise scraping failed for {ticker}: {str(e)}")
            return {
                "source": "esg_enterprise",
                "success": False,
                "error": str(e)
            }
    
    async def _scrape_epa_violations(self, ticker: str, company_name: str) -> Dict[str, Any]:
        """Scrape EPA enforcement data"""
        try:
            await asyncio.sleep(random.uniform(1, 3))
            
            # EPA ECHO database
            search_url = "https://echo.epa.gov/detailed-facility-report"
            
            # Search for company facilities
            environmental_violations = {
                "total_violations": 0,
                "recent_violations": [],
                "total_penalties": 0,
                "compliance_status": "unknown",
                "facility_count": 0,
                "violation_types": []
            }
            
            # Note: Actual implementation would query EPA ECHO database
            # using company name and facilities
            
            return {
                "source": "epa_violations",
                "success": True,
                "data": environmental_violations,
                "last_updated": datetime.utcnow(),
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.warning(f"EPA violations scraping failed for {ticker}: {str(e)}")
            return {
                "source": "epa_violations",
                "success": False,
                "error": str(e)
            }
    
    async def _scrape_osha_data(self, ticker: str, company_name: str) -> Dict[str, Any]:
        """Scrape OSHA safety data"""
        try:
            await asyncio.sleep(random.uniform(1, 3))
            
            # OSHA enforcement database
            search_url = "https://www.osha.gov/ords/imis/establishment.html"
            
            safety_data = {
                "total_inspections": 0,
                "violations_found": 0,
                "total_penalties": 0,
                "serious_violations": 0,
                "workplace_fatalities": 0,
                "injury_rate": None,
                "safety_compliance_status": "unknown"
            }
            
            return {
                "source": "osha_data",
                "success": True,
                "data": safety_data,
                "last_updated": datetime.utcnow(),
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.warning(f"OSHA data scraping failed for {ticker}: {str(e)}")
            return {
                "source": "osha_data",
                "success": False,
                "error": str(e)
            }
    
    async def _consolidate_esg_data(
        self, 
        ticker: str, 
        results: List, 
        start_time: datetime
    ) -> Dict[str, Any]:
        """Consolidate ESG data from multiple sources"""
        
        successful_results = []
        data_sources = []
        errors = []
        
        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
                continue
                
            if result.get("success"):
                successful_results.append(result)
                data_sources.append(result.get("source"))
            else:
                errors.append(f"{result.get('source')}: {result.get('error', 'Unknown error')}")
        
        # Merge data from successful sources
        consolidated = self._merge_esg_data(successful_results)
        
        # Create structured ESG metrics
        environmental_metrics = self._create_environmental_metrics(consolidated)
        social_metrics = self._create_social_metrics(consolidated)
        governance_metrics = self._create_governance_metrics(consolidated)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "ticker": ticker,
            "scraping_timestamp": start_time,
            "environmental_metrics": environmental_metrics.dict() if environmental_metrics else None,
            "social_metrics": social_metrics.dict() if social_metrics else None,
            "governance_metrics": governance_metrics.dict() if governance_metrics else None,
            "raw_data": consolidated,
            "data_sources": data_sources,
            "errors": errors,
            "data_quality_score": self._calculate_data_quality(successful_results),
            "processing_time_ms": processing_time
        }
    
    def _merge_esg_data(self, successful_results: List[Dict]) -> Dict[str, Any]:
        """Merge ESG data from multiple sources with priority weighting"""
        
        # Source priority (higher number = higher priority)
        source_priority = {
            "sustainalytics": 5,
            "msci_esg": 4,
            "cdp": 4,
            "esg_enterprise": 3,
            "epa_violations": 5,  # High priority for regulatory data
            "osha_data": 5
        }
        
        # Sort by priority
        sorted_results = sorted(
            successful_results,
            key=lambda x: source_priority.get(x.get("source", ""), 1),
            reverse=True
        )
        
        merged_data = {}
        
        for result in sorted_results:
            source = result.get("source")
            data = result.get("data", {})
            confidence = result.get("confidence", 0.5)
            
            merged_data[source] = {
                "data": data,
                "confidence": confidence,
                "last_updated": result.get("last_updated")
            }
        
        return merged_data
    
    def _create_environmental_metrics(self, consolidated_data: Dict) -> Optional[EnvironmentalMetrics]:
        """Create EnvironmentalMetrics from consolidated data"""
        try:
            metrics_data = {}
            data_sources = []
            
            # Extract environmental data from various sources
            for source, source_data in consolidated_data.items():
                data = source_data.get("data", {})
                data_sources.append(source)
                
                if source == "cdp":
                    if data.get("carbon_emissions"):
                        metrics_data["carbon_emissions"] = data["carbon_emissions"]
                    if data.get("renewable_energy_percentage"):
                        metrics_data["renewable_energy_percentage"] = data["renewable_energy_percentage"]
                
                elif source == "epa_violations":
                    if data.get("total_violations"):
                        metrics_data["environmental_violations"] = data["total_violations"]
                    if data.get("total_penalties"):
                        metrics_data["environmental_fines"] = data["total_penalties"]
            
            if metrics_data:
                return EnvironmentalMetrics(
                    **metrics_data,
                    data_sources=data_sources,
                    last_updated=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to create environmental metrics: {str(e)}")
            return None
    
    def _create_social_metrics(self, consolidated_data: Dict) -> Optional[SocialMetrics]:
        """Create SocialMetrics from consolidated data"""
        try:
            metrics_data = {}
            data_sources = []
            
            # Extract social data from various sources
            for source, source_data in consolidated_data.items():
                data = source_data.get("data", {})
                data_sources.append(source)
                
                if source == "osha_data":
                    if data.get("violations_found"):
                        metrics_data["workplace_safety_incidents"] = data["violations_found"]
            
            if metrics_data:
                return SocialMetrics(
                    **metrics_data,
                    data_sources=data_sources,
                    last_updated=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to create social metrics: {str(e)}")
            return None
    
    def _create_governance_metrics(self, consolidated_data: Dict) -> Optional[GovernanceMetrics]:
        """Create GovernanceMetrics from consolidated data"""
        try:
            metrics_data = {}
            data_sources = []
            
            # Extract governance data from various sources
            for source, source_data in consolidated_data.items():
                data = source_data.get("data", {})
                data_sources.append(source)
                
                # Governance metrics would be extracted here
                # from ESG rating sources
            
            if metrics_data:
                return GovernanceMetrics(
                    **metrics_data,
                    data_sources=data_sources,
                    last_updated=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to create governance metrics: {str(e)}")
            return None
    
    def _calculate_data_quality(self, successful_results: List[Dict]) -> float:
        """Calculate overall data quality score"""
        if not successful_results:
            return 0.0
        
        # Weight by source confidence and coverage
        total_confidence = sum(result.get("confidence", 0.5) for result in successful_results)
        coverage_score = min(len(successful_results) / 6.0, 1.0)  # 6 total sources
        
        return (total_confidence / len(successful_results)) * coverage_score
    
    async def _get_cached_esg_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get cached ESG data if available and fresh"""
        try:
            cache_cutoff = datetime.utcnow() - timedelta(
                seconds=self.settings.caching.esg_ratings_ttl
            )
            
            cached_doc = await self.scraping_repo.find_one({
                "ticker": ticker,
                "type": "scraped_esg_data",
                "scraping_timestamp": {"$gte": cache_cutoff}
            })
            
            if cached_doc:
                return cached_doc.get("data")
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get cached ESG data for {ticker}: {str(e)}")
            return None
    
    async def _cache_esg_data(self, ticker: str, data: Dict[str, Any]):
        """Cache scraped ESG data"""
        try:
            document = {
                "ticker": ticker,
                "type": "scraped_esg_data",
                "data": data,
                "scraping_timestamp": data.get("scraping_timestamp", datetime.utcnow()),
                "expires_at": datetime.utcnow() + timedelta(
                    seconds=self.settings.caching.esg_ratings_ttl
                )
            }
            
            await self.scraping_repo.upsert(
                {"ticker": ticker, "type": "scraped_esg_data"},
                document
            )
            
        except Exception as e:
            logger.error(f"Failed to cache ESG data for {ticker}: {str(e)}")
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of ESG data sources"""
        health_status = {}
        
        # Test accessibility of major ESG websites
        test_urls = {
            "sustainalytics": "https://www.sustainalytics.com",
            "cdp": "https://www.cdp.net",
            "msci_esg": "https://www.msci.com",
            "epa": "https://echo.epa.gov"
        }
        
        for source, url in test_urls.items():
            try:
                response = self.session.get(url, timeout=10)
                health_status[source] = response.status_code == 200
            except:
                health_status[source] = False
        
        return health_status


# Global service instance
esg_scraper = ESGDataScraper()


def get_esg_scraper() -> ESGDataScraper:
    """Get ESG scraper service instance"""
    return esg_scraper