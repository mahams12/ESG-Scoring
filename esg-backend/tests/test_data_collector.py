"""
Tests for real-time data collection service
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.services.data_collector import RealTimeDataCollector
from app.models.company import FinancialMetrics
from app.utils.exceptions import DataCollectionError, APIError


class TestRealTimeDataCollector:
    """Test suite for RealTimeDataCollector"""
    
    @pytest.fixture
    def data_collector(self):
        """Create RealTimeDataCollector instance for testing"""
        return RealTimeDataCollector()
    
    @pytest.mark.asyncio
    async def test_collect_all_data_success(self, data_collector):
        """Test successful data collection from all sources"""
        
        # Mock all collection methods
        with patch.object(data_collector, '_collect_financial_data') as mock_financial, \
             patch.object(data_collector, '_collect_market_data') as mock_market, \
             patch.object(data_collector, '_collect_fundamental_ratios') as mock_ratios, \
             patch.object(data_collector, '_collect_esg_baseline_data') as mock_esg:
            
            # Setup mock responses
            mock_financial.return_value = {
                "source": "financial_modeling_prep",
                "success": True,
                "metrics": {
                    "revenue": 394328000000,
                    "net_income": 99803000000,
                    "market_cap": 3000000000000
                },
                "last_updated": datetime.utcnow()
            }
            
            mock_market.return_value = {
                "source": "yahoo_finance",
                "success": True,
                "data": {
                    "current_price": 175.43,
                    "market_cap": 3000000000000,
                    "volume": 45123456
                },
                "last_updated": datetime.utcnow()
            }
            
            mock_ratios.return_value = {
                "source": "financial_modeling_prep_ratios",
                "success": True,
                "ratios": {
                    "pe_ratio": 28.5,
                    "debt_to_equity": 1.73,
                    "current_ratio": 1.04
                },
                "last_updated": datetime.utcnow()
            }
            
            mock_esg.return_value = {
                "source": "baseline_esg",
                "success": True,
                "data": {
                    "environmental": {"data_availability": "limited"},
                    "social": {"data_availability": "limited"},
                    "governance": {"data_availability": "limited"}
                },
                "last_updated": datetime.utcnow()
            }
            
            # Test data collection
            result = await data_collector.collect_all_data("AAPL")
            
            # Assertions
            assert result["ticker"] == "AAPL"
            assert "collection_timestamp" in result
            assert "financial_data" in result
            assert "market_data" in result
            assert "financial_ratios" in result
            assert "esg_baseline" in result
            assert len(result["data_sources"]) == 4
            assert result["processing_time_ms"] > 0
    
    @pytest.mark.asyncio
    async def test_collect_financial_data_success(self, data_collector):
        """Test successful financial data collection from FMP"""
        
        # Mock aiohttp session
        mock_responses = [
            MagicMock(status=200),  # profile
            MagicMock(status=200),  # income
            MagicMock(status=200),  # balance
            MagicMock(status=200)   # cash flow
        ]
        
        # Mock JSON responses
        profile_data = [{
            "companyName": "Apple Inc.",
            "mktCap": 3000000000000,
            "beta": 1.2,
            "price": 175.43
        }]
        
        income_data = [{
            "revenue": 394328000000,
            "netIncome": 99803000000,
            "grossProfit": 169148000000,
            "calendarYear": 2023
        }]
        
        balance_data = [{
            "totalAssets": 352755000000,
            "totalLiabilities": 290437000000,
            "totalEquity": 62318000000,
            "totalDebt": 123000000000
        }]
        
        cash_flow_data = [{
            "operatingCashFlow": 110543000000,
            "freeCashFlow": 99584000000,
            "capitalExpenditure": -10959000000
        }]
        
        mock_responses[0].json = AsyncMock(return_value=profile_data)
        mock_responses[1].json = AsyncMock(return_value=income_data)
        mock_responses[2].json = AsyncMock(return_value=balance_data)
        mock_responses[3].json = AsyncMock(return_value=cash_flow_data)
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.side_effect = mock_responses
            
            # Test financial data collection
            result = await data_collector._collect_financial_data("AAPL")
            
            # Assertions
            assert result["source"] == "financial_modeling_prep"
            assert result["success"] is True
            assert "metrics" in result
            assert result["metrics"]["revenue"] == 394328000000
            assert result["metrics"]["net_income"] == 99803000000
    
    @pytest.mark.asyncio
    async def test_collect_market_data_success(self, data_collector):
        """Test successful market data collection from Yahoo Finance"""
        
        # Mock yfinance Ticker
        mock_ticker = MagicMock()
        mock_ticker.info = {
            "currentPrice": 175.43,
            "previousClose": 174.21,
            "volume": 45123456,
            "marketCap": 3000000000000,
            "beta": 1.2,
            "fiftyTwoWeekHigh": 198.23,
            "fiftyTwoWeekLow": 124.17
        }
        
        # Mock historical data
        mock_history = MagicMock()
        mock_history.empty = False
        mock_history.__len__ = lambda x: 5
        mock_history['Close'] = MagicMock()
        mock_history['Close'].pct_change.return_value.dropna.return_value.std.return_value = 0.025
        mock_ticker.history.return_value = mock_history
        
        with patch('yfinance.Ticker', return_value=mock_ticker):
            # Test market data collection
            result = await data_collector._collect_market_data("AAPL")
            
            # Assertions
            assert result["source"] == "yahoo_finance"
            assert result["success"] is True
            assert "data" in result
            assert result["data"]["current_price"] == 175.43
            assert result["data"]["market_cap"] == 3000000000000
    
    @pytest.mark.asyncio
    async def test_collect_fundamental_ratios_success(self, data_collector):
        """Test successful fundamental ratios collection"""
        
        # Mock aiohttp responses
        mock_responses = [
            MagicMock(status=200),  # metrics
            MagicMock(status=200)   # ratios
        ]
        
        metrics_data = [{
            "peRatio": 28.5,
            "pbRatio": 5.8,
            "debtToEquity": 1.73,
            "returnOnAssets": 0.283,
            "returnOnEquity": 1.601
        }]
        
        ratios_data = [{
            "currentRatio": 1.04,
            "quickRatio": 0.84,
            "grossProfitMargin": 0.429,
            "netProfitMargin": 0.253,
            "interestCoverage": 35.2
        }]
        
        mock_responses[0].json = AsyncMock(return_value=metrics_data)
        mock_responses[1].json = AsyncMock(return_value=ratios_data)
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.side_effect = mock_responses
            
            # Test ratios collection
            result = await data_collector._collect_fundamental_ratios("AAPL")
            
            # Assertions
            assert result["source"] == "financial_modeling_prep_ratios"
            assert result["success"] is True
            assert "ratios" in result
            assert result["ratios"]["pe_ratio"] == 28.5
            assert result["ratios"]["current_ratio"] == 1.04
    
    @pytest.mark.asyncio
    async def test_get_financial_metrics_success(self, data_collector):
        """Test converting collected data to FinancialMetrics object"""
        
        # Mock collect_all_data
        mock_data = {
            "ticker": "AAPL",
            "financial_data": {
                "success": True,
                "metrics": {
                    "revenue": 394328000000,
                    "net_income": 99803000000,
                    "total_debt": 123000000000,
                    "total_equity": 62318000000,
                    "debt_to_equity": 1.97,
                    "current_ratio": 1.04,
                    "profit_margin": 25.3,
                    "pe_ratio": 28.5,
                    "beta": 1.2,
                    "fiscal_year": 2023
                }
            }
        }
        
        with patch.object(data_collector, 'collect_all_data', return_value=mock_data):
            # Test financial metrics conversion
            metrics = await data_collector.get_financial_metrics("AAPL")
            
            # Assertions
            assert isinstance(metrics, FinancialMetrics)
            assert metrics.revenue == 394328000000
            assert metrics.net_income == 99803000000
            assert metrics.debt_to_equity == 1.97
            assert metrics.data_source == "financial_modeling_prep"
    
    @pytest.mark.asyncio
    async def test_get_market_performance_success(self, data_collector):
        """Test market performance calculation"""
        
        # Mock yfinance data
        mock_ticker = MagicMock()
        
        # Create mock historical data
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range('2023-01-01', periods=252, freq='D')
        prices = np.random.normal(150, 10, 252)
        prices[0] = 140  # Start price
        prices[-1] = 160  # End price
        
        mock_hist = pd.DataFrame({
            'Close': prices,
            'Volume': np.random.randint(20000000, 80000000, 252)
        }, index=dates)
        
        mock_ticker.history.return_value = mock_hist
        
        with patch('yfinance.Ticker', return_value=mock_ticker):
            # Test market performance
            result = await data_collector.get_market_performance("AAPL", "1y")
            
            # Assertions
            assert result["success"] is True
            assert "data" in result
            assert "total_return_percent" in result["data"]
            assert "annualized_volatility_percent" in result["data"]
            assert "sharpe_ratio" in result["data"]
    
    @pytest.mark.asyncio
    async def test_collect_data_with_api_failure(self, data_collector):
        """Test data collection with API failures"""
        
        # Mock failed API responses
        with patch.object(data_collector, '_collect_financial_data') as mock_financial, \
             patch.object(data_collector, '_collect_market_data') as mock_market, \
             patch.object(data_collector, '_collect_fundamental_ratios') as mock_ratios, \
             patch.object(data_collector, '_collect_esg_baseline_data') as mock_esg:
            
            # Setup failed responses
            mock_financial.return_value = {
                "source": "financial_modeling_prep",
                "success": False,
                "error": "API rate limit exceeded"
            }
            
            mock_market.return_value = {
                "source": "yahoo_finance", 
                "success": False,
                "error": "Connection timeout"
            }
            
            mock_ratios.return_value = {
                "source": "financial_modeling_prep_ratios",
                "success": False,
                "error": "Invalid API key"
            }
            
            mock_esg.return_value = {
                "source": "baseline_esg",
                "success": True,
                "data": {}
            }
            
            # Test data collection with failures
            result = await data_collector.collect_all_data("AAPL")
            
            # Assertions
            assert result["ticker"] == "AAPL"
            assert len(result["data_sources"]) == 1  # Only ESG succeeded
    
    @pytest.mark.asyncio
    async def test_cache_collected_data(self, data_collector):
        """Test caching of collected data"""
        
        mock_data = {
            "ticker": "AAPL",
            "collection_timestamp": datetime.utcnow(),
            "financial_data": {"success": True, "metrics": {}}
        }
        
        with patch.object(data_collector.financial_repo, 'upsert') as mock_upsert:
            mock_upsert.return_value = True
            
            # Test caching
            await data_collector.cache_collected_data("AAPL", mock_data)
            
            # Verify cache call
            mock_upsert.assert_called_once()
            call_args = mock_upsert.call_args
            assert call_args[0][0]["ticker"] == "AAPL"
            assert call_args[0][0]["type"] == "raw_financial_data"
    
    @pytest.mark.asyncio
    async def test_get_cached_data(self, data_collector):
        """Test retrieving cached data"""
        
        cached_data = {
            "ticker": "AAPL",
            "data": {
                "financial_data": {"success": True, "metrics": {}},
                "collection_timestamp": datetime.utcnow()
            },
            "expires_at": datetime.utcnow()
        }
        
        with patch.object(data_collector.financial_repo, 'find_one') as mock_find:
            mock_find.return_value = cached_data
            
            # Test cache retrieval
            result = await data_collector.get_cached_data("AAPL")
            
            # Assertions
            assert result is not None
            assert result["financial_data"]["success"] is True
    
    @pytest.mark.asyncio
    async def test_data_freshness_score(self, data_collector):
        """Test data freshness score calculation"""
        
        # Mock recent cached data
        recent_cache = {
            "ticker": "AAPL",
            "collection_timestamp": datetime.utcnow()
        }
        
        with patch.object(data_collector.financial_repo, 'find_one') as mock_find:
            mock_find.return_value = recent_cache
            
            # Test freshness score
            score = await data_collector.get_data_freshness_score("AAPL")
            
            # Should be high for recent data
            assert 0.8 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_peer_comparison_data(self, data_collector):
        """Test peer comparison data collection"""
        
        tickers = ["AAPL", "GOOGL", "MSFT"]
        
        # Mock individual data collection
        with patch.object(data_collector, 'collect_all_data') as mock_collect:
            async def side_effect(ticker):
                return {
                    "ticker": ticker,
                    "financial_data": {
                        "success": True,
                        "metrics": {
                            "revenue": 300000000000,
                            "market_cap": 2000000000000,
                            "profit_margin": 25.0
                        }
                    },
                    "market_data": {
                        "success": True,
                        "data": {"market_cap": 2000000000000}
                    }
                }
            
            mock_collect.side_effect = side_effect
            
            # Test peer comparison
            result = await data_collector.get_peer_comparison_data(tickers)
            
            # Assertions
            assert result["success"] is True
            assert "comparison_data" in result
            assert len(result["comparison_data"]) == 3
            assert "AAPL" in result["comparison_data"]
    
    @pytest.mark.asyncio
    async def test_health_check(self, data_collector):
        """Test data collector health check"""
        
        # Mock successful API responses
        with patch('yfinance.Ticker') as mock_yf, \
             patch.object(data_collector.session, 'get') as mock_get:
            
            # Mock Yahoo Finance
            mock_stock = MagicMock()
            mock_stock.info = {"regularMarketPrice": 175.43}
            mock_yf.return_value = mock_stock
            
            # Mock HTTP responses
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            # Test health check
            health_status = await data_collector.health_check()
            
            # Assertions
            assert isinstance(health_status, dict)
            assert "yahoo_finance" in health_status
            assert "financial_modeling_prep" in health_status
            assert "iex_cloud" in health_status


@pytest.mark.asyncio
async def test_data_collector_integration():
    """Integration test for data collector with mock external APIs"""
    
    collector = RealTimeDataCollector()
    
    # Mock all external dependencies
    with patch('yfinance.Ticker') as mock_yf, \
         patch('aiohttp.ClientSession') as mock_session:
        
        # Setup mocks
        mock_stock = MagicMock()
        mock_stock.info = {
            "longName": "Apple Inc.",
            "currentPrice": 175.43,
            "marketCap": 3000000000000
        }
        mock_yf.return_value = mock_stock
        
        # Mock session responses
        mock_responses = [MagicMock(status=200) for _ in range(6)]
        for response in mock_responses:
            response.json = AsyncMock(return_value=[{}])
        
        mock_session.return_value.__aenter__.return_value.get.side_effect = mock_responses
        
        # Test integration
        result = await collector.collect_all_data("AAPL")
        
        # Verify integration works
        assert result["ticker"] == "AAPL"
        assert "processing_time_ms" in result


if __name__ == "__main__":
    pytest.main([__file__])