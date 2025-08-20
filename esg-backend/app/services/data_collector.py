"""
Real-time data collection service for financial and ESG data
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
import yfinance as yf
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.config import get_settings
from app.models.company import FinancialMetrics
from app.models.esg_analysis import EnvironmentalMetrics, SocialMetrics, GovernanceMetrics
from app.database import DatabaseRepository


class RealTimeDataCollector:
    """Service for collecting real-time financial and ESG data from multiple sources"""
    
    def __init__(self):
        self.settings = get_settings()
        self.session = self._create_session()
        self.financial_repo = DatabaseRepository("esg_scores")
        
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
        
        # Set headers
        session.headers.update({
            'User-Agent': 'ESG Research System 2.0',
            'Accept': 'application/json',
        })
        
        return session
    
    async def collect_all_data(self, ticker: str) -> Dict[str, Any]:
        """
        Collect all available data for a company from multiple sources
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing all collected data
        """
        start_time = datetime.utcnow()
        
        try:
            # Run data collection tasks concurrently
            tasks = [
                self._collect_financial_data(ticker),
                self._collect_market_data(ticker),
                self._collect_fundamental_ratios(ticker),
                self._collect_alphavantage_data(ticker)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            financial_data = results[0] if not isinstance(results[0], Exception) else {}
            market_data = results[1] if not isinstance(results[1], Exception) else {}
            ratios_data = results[2] if not isinstance(results[2], Exception) else {}
            alphavantage_data = results[3] if not isinstance(results[3], Exception) else {}
            
            # Combine all data
            combined_data = {
                "ticker": ticker,
                "collection_timestamp": start_time,
                "financial_data": financial_data,
                "market_data": market_data,
                "financial_ratios": ratios_data,
                "alphavantage_data": alphavantage_data,
                "data_sources": self._get_successful_sources(results),
                "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
            }
            
            logger.info(f"Data collection completed for {ticker} in {combined_data['processing_time_ms']:.2f}ms")
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Data collection failed for {ticker}: {str(e)}")
            return {
                "ticker": ticker,
                "collection_timestamp": start_time,
                "error": str(e),
                "data_sources": [],
                "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
            }
    
    async def _collect_financial_data(self, ticker: str) -> Dict[str, Any]:
        """Collect financial data from Financial Modeling Prep"""
        try:
            # Get company profile
            profile_url = f"{self.settings.api.fmp_base_url}/profile/{ticker}"
            profile_params = {"apikey": self.settings.api.fmp_api_key}
            
            # Get income statement (latest year)
            income_url = f"{self.settings.api.fmp_base_url}/income-statement/{ticker}"
            income_params = {"apikey": self.settings.api.fmp_api_key, "limit": 1}
            
            # Get balance sheet (latest year)
            balance_url = f"{self.settings.api.fmp_base_url}/balance-sheet-statement/{ticker}"
            balance_params = {"apikey": self.settings.api.fmp_api_key, "limit": 1}
            
            # Get cash flow (latest year)
            cash_flow_url = f"{self.settings.api.fmp_base_url}/cash-flow-statement/{ticker}"
            cash_flow_params = {"apikey": self.settings.api.fmp_api_key, "limit": 1}
            
            # Make concurrent requests
            async with aiohttp.ClientSession() as session:
                tasks = [
                    session.get(profile_url, params=profile_params),
                    session.get(income_url, params=income_params),
                    session.get(balance_url, params=balance_params),
                    session.get(cash_flow_url, params=cash_flow_params)
                ]
                
                responses = await asyncio.gather(*tasks)
                
                # Parse responses
                profile_data = await responses[0].json() if responses[0].status == 200 else []
                income_data = await responses[1].json() if responses[1].status == 200 else []
                balance_data = await responses[2].json() if responses[2].status == 200 else []
                cash_flow_data = await responses[3].json() if responses[3].status == 200 else []
            
            # Extract financial metrics
            financial_metrics = self._extract_financial_metrics(
                profile_data, income_data, balance_data, cash_flow_data
            )
            
            return {
                "source": "financial_modeling_prep",
                "success": True,
                "metrics": financial_metrics,
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            logger.warning(f"FMP financial data collection failed for {ticker}: {str(e)}")
            return {
                "source": "financial_modeling_prep",
                "success": False,
                "error": str(e)
            }
    
    async def _collect_market_data(self, ticker: str) -> Dict[str, Any]:
        """Collect real-time market data using yfinance"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get current info
            info = stock.info
            
            # Get recent price data
            hist = stock.history(period="5d")
            
            # Calculate some basic metrics
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
            
            price_change = None
            price_change_percent = None
            
            if current_price and previous_close:
                price_change = current_price - previous_close
                price_change_percent = (price_change / previous_close) * 100
            
            # Calculate volatility (5-day)
            volatility = None
            if not hist.empty and len(hist) > 1:
                returns = hist['Close'].pct_change().dropna()
                volatility = returns.std() * (252 ** 0.5)  # Annualized volatility
            
            market_data = {
                "current_price": current_price,
                "previous_close": previous_close,
                "price_change": price_change,
                "price_change_percent": price_change_percent,
                "volume": info.get("volume"),
                "avg_volume": info.get("averageVolume"),
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "shares_outstanding": info.get("sharesOutstanding"),
                "float_shares": info.get("floatShares"),
                "beta": info.get("beta"),
                "volatility_5d": volatility,
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "bid": info.get("bid"),
                "ask": info.get("ask"),
                "bid_size": info.get("bidSize"),
                "ask_size": info.get("askSize")
            }
            
            return {
                "source": "yahoo_finance",
                "success": True,
                "data": market_data,
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            logger.warning(f"Yahoo Finance market data collection failed for {ticker}: {str(e)}")
            return {
                "source": "yahoo_finance",
                "success": False,
                "error": str(e)
            }
    
    async def _collect_fundamental_ratios(self, ticker: str) -> Dict[str, Any]:
        """Collect fundamental ratios from FMP"""
        try:
            # Get key metrics
            metrics_url = f"{self.settings.api.fmp_base_url}/key-metrics/{ticker}"
            params = {"apikey": self.settings.api.fmp_api_key, "limit": 1}
            
            # Get financial ratios
            ratios_url = f"{self.settings.api.fmp_base_url}/ratios/{ticker}"
            ratios_params = {"apikey": self.settings.api.fmp_api_key, "limit": 1}
            
            async with aiohttp.ClientSession() as session:
                tasks = [
                    session.get(metrics_url, params=params),
                    session.get(ratios_url, params=ratios_params)
                ]
                
                responses = await asyncio.gather(*tasks)
                
                metrics_data = await responses[0].json() if responses[0].status == 200 else []
                ratios_data = await responses[1].json() if responses[1].status == 200 else []
            
            # Extract ratios
            fundamental_ratios = {}
            
            if metrics_data and len(metrics_data) > 0:
                metrics = metrics_data[0]
                fundamental_ratios.update({
                    "pe_ratio": metrics.get("peRatio"),
                    "price_to_book": metrics.get("pbRatio"),
                    "price_to_sales": metrics.get("psRatio"),
                    "ev_to_revenue": metrics.get("evToRevenue"),
                    "ev_to_ebitda": metrics.get("evToEbitda"),
                    "debt_to_equity": metrics.get("debtToEquity"),
                    "debt_to_assets": metrics.get("debtToAssets"),
                    "return_on_assets": metrics.get("returnOnAssets"),
                    "return_on_equity": metrics.get("returnOnEquity"),
                    "return_on_invested_capital": metrics.get("returnOnInvestedCapital")
                })
            
            if ratios_data and len(ratios_data) > 0:
                ratios = ratios_data[0]
                fundamental_ratios.update({
                    "current_ratio": ratios.get("currentRatio"),
                    "quick_ratio": ratios.get("quickRatio"),
                    "cash_ratio": ratios.get("cashRatio"),
                    "gross_profit_margin": ratios.get("grossProfitMargin"),
                    "operating_profit_margin": ratios.get("operatingProfitMargin"),
                    "net_profit_margin": ratios.get("netProfitMargin"),
                    "interest_coverage": ratios.get("interestCoverage"),
                    "asset_turnover": ratios.get("assetTurnover"),
                    "inventory_turnover": ratios.get("inventoryTurnover"),
                    "receivables_turnover": ratios.get("receivablesNodeTurnover")
                })
            
            return {
                "source": "financial_modeling_prep_ratios",
                "success": True,
                "ratios": fundamental_ratios,
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            logger.warning(f"FMP ratios collection failed for {ticker}: {str(e)}")
            return {
                "source": "financial_modeling_prep_ratios",
                "success": False,
                "error": str(e)
            }
    
    async def _collect_alphavantage_data(self, ticker: str) -> Dict[str, Any]:
        """Collect additional financial data from Alpha Vantage"""
        try:
            # Get company overview
            overview_url = f"{self.settings.api.alphavantage_base_url}/query"
            overview_params = {
                "function": "OVERVIEW",
                "symbol": ticker,
                "apikey": self.settings.api.alphavantage_api_key
            }
            
            # Get daily adjusted prices for additional metrics
            price_url = f"{self.settings.api.alphavantage_base_url}/query"
            price_params = {
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": ticker,
                "apikey": self.settings.api.alphavantage_api_key,
                "outputsize": "compact"
            }
            
            async with aiohttp.ClientSession() as session:
                tasks = [
                    session.get(overview_url, params=overview_params),
                    session.get(price_url, params=price_params)
                ]
                
                responses = await asyncio.gather(*tasks)
                
                overview_data = await responses[0].json() if responses[0].status == 200 else {}
                price_data = await responses[1].json() if responses[1].status == 200 else {}
            
            # Extract additional financial metrics
            alphavantage_metrics = {}
            
            if overview_data and "Symbol" in overview_data:
                alphavantage_metrics.update({
                    "market_cap": self._safe_float_convert(overview_data.get("MarketCapitalization")),
                    "enterprise_value": self._safe_float_convert(overview_data.get("EnterpriseValue")),
                    "pe_ratio": self._safe_float_convert(overview_data.get("PERatio")),
                    "peg_ratio": self._safe_float_convert(overview_data.get("PEGRatio")),
                    "book_value": self._safe_float_convert(overview_data.get("BookValue")),
                    "dividend_per_share": self._safe_float_convert(overview_data.get("DividendPerShare")),
                    "dividend_yield": self._safe_float_convert(overview_data.get("DividendYield")),
                    "eps": self._safe_float_convert(overview_data.get("EPS")),
                    "revenue_per_share": self._safe_float_convert(overview_data.get("RevenuePerShareTTM")),
                    "profit_margin": self._safe_float_convert(overview_data.get("ProfitMargin")),
                    "operating_margin": self._safe_float_convert(overview_data.get("OperatingMarginTTM")),
                    "return_on_assets": self._safe_float_convert(overview_data.get("ReturnOnAssetsTTM")),
                    "return_on_equity": self._safe_float_convert(overview_data.get("ReturnOnEquityTTM")),
                    "revenue": self._safe_float_convert(overview_data.get("RevenueTTM")),
                    "gross_profit": self._safe_float_convert(overview_data.get("GrossProfitTTM")),
                    "ebitda": self._safe_float_convert(overview_data.get("EBITDA")),
                    "quarter_ending": overview_data.get("LatestQuarter"),
                    "52_week_high": self._safe_float_convert(overview_data.get("52WeekHigh")),
                    "52_week_low": self._safe_float_convert(overview_data.get("52WeekLow")),
                    "50_day_moving_avg": self._safe_float_convert(overview_data.get("50DayMovingAverage")),
                    "200_day_moving_avg": self._safe_float_convert(overview_data.get("200DayMovingAverage")),
                    "shares_outstanding": self._safe_float_convert(overview_data.get("SharesOutstanding")),
                    "beta": self._safe_float_convert(overview_data.get("Beta"))
                })
            
            # Process price data for additional insights
            if price_data and "Time Series (Daily)" in price_data:
                time_series = price_data["Time Series (Daily)"]
                if time_series:
                    # Get recent trading data
                    recent_dates = sorted(time_series.keys(), reverse=True)[:5]
                    recent_volumes = [
                        int(time_series[date]["6. volume"]) 
                        for date in recent_dates
                    ]
                    alphavantage_metrics["avg_volume_5d"] = sum(recent_volumes) / len(recent_volumes)
            
            return {
                "source": "alpha_vantage",
                "success": True,
                "metrics": alphavantage_metrics,
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            logger.warning(f"Alpha Vantage data collection failed for {ticker}: {str(e)}")
            return {
                "source": "alpha_vantage",
                "success": False,
                "error": str(e)
            }
    
    def _safe_float_convert(self, value) -> Optional[float]:
        """Safely convert value to float"""
        if value is None or value == "None" or value == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _extract_financial_metrics(
        self, 
        profile_data: List, 
        income_data: List, 
        balance_data: List, 
        cash_flow_data: List
    ) -> Dict[str, Any]:
        """Extract financial metrics from FMP API responses"""
        
        metrics = {}
        
        try:
            # Profile data
            if profile_data and len(profile_data) > 0:
                profile = profile_data[0]
                metrics.update({
                    "market_cap": profile.get("mktCap"),
                    "enterprise_value": profile.get("volAvg"),
                    "beta": profile.get("beta"),
                    "price": profile.get("price"),
                    "dividend_yield": profile.get("lastDiv")
                })
            
            # Income statement data
            if income_data and len(income_data) > 0:
                income = income_data[0]
                metrics.update({
                    "revenue": income.get("revenue"),
                    "gross_profit": income.get("grossProfit"),
                    "operating_income": income.get("operatingIncome"),
                    "net_income": income.get("netIncome"),
                    "ebitda": income.get("ebitda"),
                    "eps": income.get("eps"),
                    "fiscal_year": income.get("calendarYear")
                })
                
                # Calculate margins
                revenue = income.get("revenue")
                if revenue and revenue > 0:
                    gross_profit = income.get("grossProfit", 0)
                    operating_income = income.get("operatingIncome", 0)
                    net_income = income.get("netIncome", 0)
                    
                    metrics.update({
                        "gross_margin": (gross_profit / revenue) * 100,
                        "operating_margin": (operating_income / revenue) * 100,
                        "profit_margin": (net_income / revenue) * 100
                    })
            
            # Balance sheet data
            if balance_data and len(balance_data) > 0:
                balance = balance_data[0]
                metrics.update({
                    "total_assets": balance.get("totalAssets"),
                    "total_liabilities": balance.get("totalLiabilities"),
                    "total_equity": balance.get("totalEquity"),
                    "total_debt": balance.get("totalDebt"),
                    "cash_and_equivalents": balance.get("cashAndCashEquivalents"),
                    "current_assets": balance.get("totalCurrentAssets"),
                    "current_liabilities": balance.get("totalCurrentLiabilities"),
                    "working_capital": balance.get("totalCurrentAssets", 0) - balance.get("totalCurrentLiabilities", 0)
                })
                
                # Calculate ratios
                total_equity = balance.get("totalEquity")
                total_debt = balance.get("totalDebt")
                current_assets = balance.get("totalCurrentAssets")
                current_liabilities = balance.get("totalCurrentLiabilities")
                
                if total_equity and total_equity > 0:
                    if total_debt:
                        metrics["debt_to_equity"] = total_debt / total_equity
                
                if current_liabilities and current_liabilities > 0:
                    if current_assets:
                        metrics["current_ratio"] = current_assets / current_liabilities
            
            # Cash flow data
            if cash_flow_data and len(cash_flow_data) > 0:
                cash_flow = cash_flow_data[0]
                metrics.update({
                    "operating_cash_flow": cash_flow.get("operatingCashFlow"),
                    "free_cash_flow": cash_flow.get("freeCashFlow"),
                    "capital_expenditure": cash_flow.get("capitalExpenditure"),
                    "dividend_payments": cash_flow.get("dividendsPaid")
                })
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Error extracting financial metrics: {str(e)}")
            return metrics
    
    def _get_successful_sources(self, results: List) -> List[str]:
        """Get list of successful data sources"""
        sources = []
        
        for result in results:
            if not isinstance(result, Exception) and isinstance(result, dict):
                if result.get("success") and result.get("source"):
                    sources.append(result["source"])
        
        return sources
    
    async def get_financial_metrics(self, ticker: str) -> Optional[FinancialMetrics]:
        """Get financial metrics as a structured object"""
        try:
            data = await self.collect_all_data(ticker)
            
            if not data or "financial_data" not in data:
                return None
            
            financial_data = data["financial_data"]
            
            if not financial_data.get("success"):
                return None
            
            metrics_dict = financial_data.get("metrics", {})
            
            # Create FinancialMetrics object
            financial_metrics = FinancialMetrics(
                revenue=metrics_dict.get("revenue"),
                net_income=metrics_dict.get("net_income"),
                total_debt=metrics_dict.get("total_debt"),
                total_equity=metrics_dict.get("total_equity"),
                debt_to_equity=metrics_dict.get("debt_to_equity"),
                current_ratio=metrics_dict.get("current_ratio"),
                return_on_equity=metrics_dict.get("return_on_equity"),
                return_on_assets=metrics_dict.get("return_on_assets"),
                profit_margin=metrics_dict.get("profit_margin"),
                operating_margin=metrics_dict.get("operating_margin"),
                free_cash_flow=metrics_dict.get("free_cash_flow"),
                price_to_earnings=metrics_dict.get("pe_ratio"),
                price_to_book=metrics_dict.get("price_to_book"),
                dividend_yield=metrics_dict.get("dividend_yield"),
                beta=metrics_dict.get("beta"),
                fiscal_year=metrics_dict.get("fiscal_year"),
                data_source="financial_modeling_prep",
                last_updated=datetime.utcnow()
            )
            
            return financial_metrics
            
        except Exception as e:
            logger.error(f"Failed to get financial metrics for {ticker}: {str(e)}")
            return None
    
    async def get_market_performance(self, ticker: str, period: str = "1y") -> Dict[str, Any]:
        """Get market performance data"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get historical data
            hist = stock.history(period=period)
            
            if hist.empty:
                return {"error": "No historical data available"}
            
            # Calculate performance metrics
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            total_return = ((end_price - start_price) / start_price) * 100
            
            # Calculate volatility
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * (252 ** 0.5) * 100  # Annualized
            
            # Calculate max drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            # Calculate Sharpe ratio (assuming 2% risk-free rate)
            risk_free_rate = 0.02
            excess_returns = returns.mean() * 252 - risk_free_rate
            sharpe_ratio = excess_returns / (returns.std() * (252 ** 0.5)) if returns.std() > 0 else 0
            
            performance_data = {
                "period": period,
                "total_return_percent": total_return,
                "annualized_volatility_percent": volatility,
                "max_drawdown_percent": max_drawdown,
                "sharpe_ratio": sharpe_ratio,
                "start_price": start_price,
                "end_price": end_price,
                "start_date": hist.index[0].strftime("%Y-%m-%d"),
                "end_date": hist.index[-1].strftime("%Y-%m-%d"),
                "trading_days": len(hist),
                "average_volume": hist['Volume'].mean(),
                "last_updated": datetime.utcnow()
            }
            
            return {
                "success": True,
                "data": performance_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get market performance for {ticker}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_peer_comparison_data(self, tickers: List[str]) -> Dict[str, Any]:
        """Get comparative data for multiple companies"""
        try:
            # Collect data for all tickers concurrently
            tasks = [self.collect_all_data(ticker) for ticker in tickers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            comparison_data = {}
            
            for i, result in enumerate(results):
                ticker = tickers[i]
                
                if isinstance(result, Exception):
                    comparison_data[ticker] = {"error": str(result)}
                    continue
                
                # Extract key metrics for comparison
                financial_data = result.get("financial_data", {})
                market_data = result.get("market_data", {})
                
                if financial_data.get("success") and market_data.get("success"):
                    metrics = financial_data.get("metrics", {})
                    market = market_data.get("data", {})
                    
                    comparison_data[ticker] = {
                        "market_cap": market.get("market_cap"),
                        "revenue": metrics.get("revenue"),
                        "net_income": metrics.get("net_income"),
                        "profit_margin": metrics.get("profit_margin"),
                        "pe_ratio": metrics.get("pe_ratio"),
                        "debt_to_equity": metrics.get("debt_to_equity"),
                        "current_ratio": metrics.get("current_ratio"),
                        "beta": market.get("beta"),
                        "dividend_yield": metrics.get("dividend_yield")
                    }
                else:
                    comparison_data[ticker] = {"error": "Data collection failed"}
            
            return {
                "success": True,
                "comparison_data": comparison_data,
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to get peer comparison data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cache_collected_data(self, ticker: str, data: Dict[str, Any]):
        """Cache collected data in database"""
        try:
            # Store in database with TTL
            document = {
                "ticker": ticker,
                "data": data,
                "collection_timestamp": data.get("collection_timestamp", datetime.utcnow()),
                "expires_at": datetime.utcnow() + timedelta(minutes=15)  # 15-minute cache
            }
            
            await self.financial_repo.upsert(
                {"ticker": ticker, "type": "raw_financial_data"},
                document
            )
            
        except Exception as e:
            logger.error(f"Failed to cache data for {ticker}: {str(e)}")
    
    async def get_cached_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get cached data if available and fresh"""
        try:
            cached_doc = await self.financial_repo.find_one({
                "ticker": ticker,
                "type": "raw_financial_data",
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if cached_doc:
                return cached_doc.get("data")
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get cached data for {ticker}: {str(e)}")
            return None
    
    async def get_data_freshness_score(self, ticker: str) -> float:
        """Calculate data freshness score (0-1)"""
        try:
            # Check when data was last collected
            cached_doc = await self.financial_repo.find_one({
                "ticker": ticker,
                "type": "raw_financial_data"
            })
            
            if not cached_doc:
                return 0.0  # No data available
            
            collection_time = cached_doc.get("collection_timestamp")
            if not collection_time:
                return 0.0
            
            # Calculate age in hours
            age_hours = (datetime.utcnow() - collection_time).total_seconds() / 3600
            
            # Fresher data gets higher score
            if age_hours < 1:
                return 1.0
            elif age_hours < 6:
                return 0.8
            elif age_hours < 24:
                return 0.6
            elif age_hours < 72:
                return 0.4
            else:
                return 0.2
            
        except Exception as e:
            logger.warning(f"Failed to calculate data freshness for {ticker}: {str(e)}")
            return 0.0
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of data sources"""
        health_status = {}
        
        # Test Yahoo Finance
        try:
            test_stock = yf.Ticker("AAPL")
            info = test_stock.info
            health_status["yahoo_finance"] = bool(info and info.get("regularMarketPrice"))
        except:
            health_status["yahoo_finance"] = False
        
        # Test Financial Modeling Prep
        try:
            test_url = f"{self.settings.api.fmp_base_url}/profile/AAPL"
            response = self.session.get(
                test_url, 
                params={"apikey": self.settings.api.fmp_api_key},
                timeout=10
            )
            health_status["financial_modeling_prep"] = response.status_code == 200
        except:
            health_status["financial_modeling_prep"] = False
        
        # Test Alpha Vantage
        try:
            test_url = f"{self.settings.api.alphavantage_base_url}/query"
            response = self.session.get(
                test_url, 
                params={
                    "function": "GLOBAL_QUOTE",
                    "symbol": "AAPL",
                    "apikey": self.settings.api.alphavantage_api_key
                },
                timeout=10
            )
            health_status["alpha_vantage"] = response.status_code == 200
        except:
            health_status["alpha_vantage"] = False
        
        return health_status


# Global service instance
data_collector = RealTimeDataCollector()


def get_data_collector() -> RealTimeDataCollector:
    """Get data collector service instance"""
    return data_collector