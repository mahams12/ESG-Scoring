"""
Tests for company validation service
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.company_validator import CompanyValidationService
from app.models.company import CompanyValidationResult, CompanyStatus, CompanyInfo
from app.utils.exceptions import InvalidTickerError, CompanyNotFoundError


class TestCompanyValidationService:
    """Test suite for CompanyValidationService"""
    
    @pytest.fixture
    def validator_service(self):
        """Create CompanyValidationService instance for testing"""
        return CompanyValidationService()
    
    @pytest.mark.asyncio
    async def test_validate_company_success(self, validator_service):
        """Test successful company validation"""
        
        # Mock the validation methods
        with patch.object(validator_service, '_validate_with_yahoo_finance') as mock_yf, \
             patch.object(validator_service, '_validate_with_fmp') as mock_fmp, \
             patch.object(validator_service, '_validate_with_iex') as mock_iex, \
             patch.object(validator_service, '_cache_validation_result') as mock_cache:
            
            # Setup mock responses
            mock_yf.return_value = {
                "source": "yahoo_finance",
                "success": True,
                "company_info": {
                    "name": "Apple Inc.",
                    "sector": "Technology",
                    "market_cap": 3000000000000
                },
                "confidence": 0.9
            }
            
            mock_fmp.return_value = {
                "source": "financial_modeling_prep",
                "success": True,
                "company_info": {
                    "name": "Apple Inc.",
                    "sector": "Technology"
                },
                "confidence": 0.85
            }
            
            mock_iex.return_value = {
                "source": "iex_cloud",
                "success": True,
                "company_info": {
                    "name": "Apple Inc."
                },
                "confidence": 0.8
            }
            
            # Test validation
            result = await validator_service.validate_company("AAPL")
            
            # Assertions
            assert isinstance(result, CompanyValidationResult)
            assert result.ticker == "AAPL"
            assert result.status == CompanyStatus.VALID
            assert result.exists is True
            assert result.company_info is not None
            assert result.company_info.name == "Apple Inc."
            assert result.confidence_score > 0.8
            
            # Verify cache was called
            mock_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_company_not_found(self, validator_service):
        """Test company not found scenario"""
        
        with patch.object(validator_service, '_validate_with_yahoo_finance') as mock_yf, \
             patch.object(validator_service, '_validate_with_fmp') as mock_fmp, \
             patch.object(validator_service, '_validate_with_iex') as mock_iex:
            
            # Setup mock responses for failed validation
            mock_yf.return_value = {
                "source": "yahoo_finance",
                "success": False,
                "error": "No company data found"
            }
            
            mock_fmp.return_value = {
                "source": "financial_modeling_prep",
                "success": False,
                "error": "No company profile found"
            }
            
            mock_iex.return_value = {
                "source": "iex_cloud",
                "success": False,
                "error": "No company data found"
            }
            
            # Test validation
            result = await validator_service.validate_company("INVALID")
            
            # Assertions
            assert result.ticker == "INVALID"
            assert result.status == CompanyStatus.INVALID
            assert result.exists is False
            assert "does not exist or is not publicly traded" in result.message
    
    @pytest.mark.asyncio
    async def test_invalid_ticker_format(self, validator_service):
        """Test invalid ticker format handling"""
        
        # Test empty ticker
        result = await validator_service.validate_company("")
        assert result.status == CompanyStatus.INVALID
        assert result.exists is False
        
        # Test invalid characters
        result = await validator_service.validate_company("ABC@123")
        assert result.status == CompanyStatus.INVALID
        assert result.exists is False
        
        # Test too long ticker
        result = await validator_service.validate_company("VERYLONGTICKER")
        assert result.status == CompanyStatus.INVALID
        assert result.exists is False
    
    @pytest.mark.asyncio
    async def test_cached_validation(self, validator_service):
        """Test cached validation retrieval"""
        
        # Mock cached result
        cached_company = {
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "exists": True,
            "status": "valid",
            "last_validated": "2025-08-19T10:00:00Z",
            "data_sources": ["yahoo_finance"],
            "confidence_score": 0.9
        }
        
        with patch.object(validator_service.company_repo, 'find_one') as mock_find:
            mock_find.return_value = cached_company
            
            # Should not call external APIs if cache is fresh
            with patch.object(validator_service, '_validate_with_yahoo_finance') as mock_yf:
                result = await validator_service.validate_company("AAPL")
                
                # Should use cached result
                assert result.ticker == "AAPL"
                assert result.exists is True
                
                # External API should not be called
                mock_yf.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_bulk_validation(self, validator_service):
        """Test bulk company validation"""
        
        tickers = ["AAPL", "GOOGL", "INVALID"]
        
        # Mock individual validations
        with patch.object(validator_service, 'validate_company') as mock_validate:
            # Setup different responses for each ticker
            async def side_effect(ticker, force_refresh=False):
                if ticker == "AAPL":
                    return CompanyValidationResult(
                        ticker="AAPL",
                        status=CompanyStatus.VALID,
                        exists=True,
                        message="Success",
                        confidence_score=0.9
                    )
                elif ticker == "GOOGL":
                    return CompanyValidationResult(
                        ticker="GOOGL", 
                        status=CompanyStatus.VALID,
                        exists=True,
                        message="Success",
                        confidence_score=0.85
                    )
                else:
                    return CompanyValidationResult(
                        ticker="INVALID",
                        status=CompanyStatus.INVALID,
                        exists=False,
                        message="Not found",
                        confidence_score=0.0
                    )
            
            mock_validate.side_effect = side_effect
            
            # Test bulk validation
            results = await validator_service.bulk_validate_companies(tickers)
            
            # Assertions
            assert len(results) == 3
            assert results[0].exists is True  # AAPL
            assert results[1].exists is True  # GOOGL  
            assert results[2].exists is False  # INVALID
    
    @pytest.mark.asyncio
    async def test_get_company_info(self, validator_service):
        """Test getting stored company information"""
        
        # Mock stored company data
        stored_company = {
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "market_cap": 3000000000000,
            "exists": True
        }
        
        with patch.object(validator_service.company_repo, 'find_one') as mock_find:
            mock_find.return_value = stored_company
            
            # Test getting company info
            info = await validator_service.get_company_info("AAPL")
            
            # Assertions
            assert info is not None
            assert isinstance(info, CompanyInfo)
            assert info.ticker == "AAPL"
            assert info.name == "Apple Inc."
            assert info.sector == "Technology"
    
    @pytest.mark.asyncio
    async def test_search_companies(self, validator_service):
        """Test company search functionality"""
        
        # Mock search results
        search_results = [
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "sector": "Technology",
                "market_cap": 3000000000000
            },
            {
                "ticker": "GOOGL", 
                "name": "Alphabet Inc.",
                "sector": "Technology",
                "market_cap": 1500000000000
            }
        ]
        
        with patch.object(validator_service.company_repo, 'count') as mock_count, \
             patch.object(validator_service.company_repo, 'find_many') as mock_find:
            
            mock_count.return_value = 2
            mock_find.return_value = search_results
            
            # Test search
            companies, total_count = await validator_service.search_companies("Apple")
            
            # Assertions
            assert total_count == 2
            assert len(companies) == 2
            assert companies[0].ticker == "AAPL"
    
    @pytest.mark.asyncio
    async def test_get_industry_peers(self, validator_service):
        """Test getting industry peer companies"""
        
        # Mock company info
        company_info = CompanyInfo(
            ticker="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics"
        )
        
        # Mock peer companies
        peer_companies = [
            {
                "ticker": "SAMSUNG",
                "name": "Samsung Electronics",
                "industry": "Consumer Electronics",
                "market_cap": 400000000000
            },
            {
                "ticker": "SONY",
                "name": "Sony Corporation", 
                "industry": "Consumer Electronics",
                "market_cap": 100000000000
            }
        ]
        
        with patch.object(validator_service, 'get_company_info') as mock_get_info, \
             patch.object(validator_service.company_repo, 'find_many') as mock_find:
            
            mock_get_info.return_value = company_info
            mock_find.return_value = peer_companies
            
            # Test getting peers
            peers = await validator_service.get_industry_peers("AAPL")
            
            # Assertions
            assert len(peers) == 2
            assert all(peer.industry == "Consumer Electronics" for peer in peers)
    
    def test_normalize_ticker(self, validator_service):
        """Test ticker normalization"""
        
        # Test normal case
        assert validator_service._normalize_ticker("aapl") == "AAPL"
        assert validator_service._normalize_ticker(" GOOGL ") == "GOOGL"
        assert validator_service._normalize_ticker("BRK.A") == "BRK.A"
        
        # Test invalid cases
        with pytest.raises(ValueError):
            validator_service._normalize_ticker("")
        
        with pytest.raises(ValueError):
            validator_service._normalize_ticker("INVALID@TICKER")
    
    def test_calculate_confidence_score(self, validator_service):
        """Test confidence score calculation"""
        
        # Test with all sources successful
        successful_results = [
            {"source": "yahoo_finance", "confidence": 0.9},
            {"source": "financial_modeling_prep", "confidence": 0.85},
            {"source": "iex_cloud", "confidence": 0.8}
        ]
        
        confidence = validator_service._calculate_confidence_score(successful_results, 3)
        assert 0.7 <= confidence <= 1.0
        
        # Test with no successful results
        confidence = validator_service._calculate_confidence_score([], 3)
        assert confidence == 0.0
    
    def test_merge_company_info(self, validator_service):
        """Test merging company information from multiple sources"""
        
        successful_results = [
            {
                "source": "yahoo_finance",
                "company_info": {
                    "name": "Apple Inc.",
                    "sector": "Technology",
                    "market_cap": 3000000000000
                }
            },
            {
                "source": "financial_modeling_prep", 
                "company_info": {
                    "name": "Apple Inc.",
                    "industry": "Consumer Electronics",
                    "website": "https://apple.com"
                }
            }
        ]
        
        merged = validator_service._merge_company_info(successful_results)
        
        # Should have data from all sources
        assert merged["name"] == "Apple Inc."
        assert merged["sector"] == "Technology"
        assert merged["industry"] == "Consumer Electronics"
        assert merged["market_cap"] == 3000000000000
        assert merged["website"] == "https://apple.com"


@pytest.mark.asyncio
async def test_validation_service_integration():
    """Integration test for validation service"""
    
    # This would test the actual service with mocked external APIs
    # but real internal logic
    
    service = CompanyValidationService()
    
    # Mock external API calls but test internal logic
    with patch('yfinance.Ticker') as mock_ticker:
        # Setup mock yfinance response
        mock_stock = MagicMock()
        mock_stock.info = {
            'longName': 'Apple Inc.',
            'sector': 'Technology',
            'marketCap': 3000000000000
        }
        mock_ticker.return_value = mock_stock
        
        # Mock other API calls to return empty/failed responses
        with patch.object(service, '_validate_with_fmp') as mock_fmp, \
             patch.object(service, '_validate_with_iex') as mock_iex, \
             patch.object(service, '_cache_validation_result') as mock_cache:
            
            mock_fmp.return_value = {"source": "fmp", "success": False}
            mock_iex.return_value = {"source": "iex", "success": False} 
            mock_cache.return_value = None
            
            # Test with one successful source
            result = await service.validate_company("AAPL")
            
            assert result.exists is True
            assert result.ticker == "AAPL"
            assert result.company_info.name == "Apple Inc."


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__])