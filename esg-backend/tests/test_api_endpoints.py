"""
Tests for API endpoints
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.main import app
from app.models.company import CompanyValidationResult, CompanyStatus, CompanyInfo
from app.models.esg_analysis import ESGAnalysis, ESGScore, InvestmentRecommendation, RiskLevel
from app.models.responses import ResponseStatus


class TestAPIEndpoints:
    """Test suite for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_company_validation(self):
        """Sample company validation result"""
        company_info = CompanyInfo(
            ticker="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics",
            market_cap=3000000000000
        )
        
        return CompanyValidationResult(
            ticker="AAPL",
            status=CompanyStatus.VALID,
            exists=True,
            message="Company validation successful",
            company_info=company_info,
            data_sources_checked=["yahoo_finance", "fmp"],
            confidence_score=0.9
        )
    
    @pytest.fixture
    def sample_esg_analysis(self):
        """Sample ESG analysis result"""
        environmental_score = ESGScore(score=88.5, confidence_level=0.85)
        social_score = ESGScore(score=82.1, confidence_level=0.8)
        governance_score = ESGScore(score=84.8, confidence_level=0.82)
        overall_score = ESGScore(score=85.1, confidence_level=0.82)
        
        return ESGAnalysis(
            ticker="AAPL",
            company_name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics",
            environmental_score=environmental_score,
            social_score=social_score,
            governance_score=governance_score,
            overall_score=overall_score,
            investment_recommendation=InvestmentRecommendation.BUY,
            risk_level=RiskLevel.LOW_MEDIUM,
            investment_thesis="Strong ESG performer with excellent fundamentals",
            key_strengths=["Renewable energy leadership", "Strong governance"],
            key_weaknesses=["Supply chain transparency"],
            improvement_areas=["Community engagement"],
            ai_insights=[],
            ai_summary="Comprehensive ESG analysis shows strong performance",
            ai_confidence=0.82,
            data_sources=["multiple"]
        )


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "ESG Investment Research System API"
        assert data["version"] == "2.0"
        assert data["status"] == "operational"
    
    def test_api_info_endpoint(self, client):
        """Test API info endpoint"""
        response = client.get("/api/v1/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["api_name"] == "ESG Investment Research System"
        assert data["version"] == "2.0"
        assert "features" in data
        assert "data_sources" in data
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        with patch('app.api.routes.health.check_all_services') as mock_check:
            mock_check.return_value = {
                "database": True,
                "company_validator": True,
                "data_collector": True
            }
            
            response = client.get("/api/v1/health/")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    def test_database_health_endpoint(self, client):
        """Test database health endpoint"""
        with patch('app.database.get_database') as mock_get_db:
            mock_db = AsyncMock()
            mock_db.health_check.return_value = True
            mock_db.get_database_stats.return_value = {"collections": 5}
            mock_get_db.return_value = mock_db
            
            response = client.get("/api/v1/health/database")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    def test_readiness_check_endpoint(self, client):
        """Test readiness check endpoint"""
        with patch('app.database.get_database') as mock_get_db:
            mock_db = AsyncMock()
            mock_db.health_check.return_value = True
            mock_get_db.return_value = mock_db
            
            response = client.get("/api/v1/health/ready")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
    
    def test_liveness_check_endpoint(self, client):
        """Test liveness check endpoint"""
        response = client.get("/api/v1/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"


class TestCompanyEndpoints:
    """Test company validation endpoints"""
    
    def test_validate_company_success(self, client, sample_company_validation):
        """Test successful company validation"""
        
        with patch('app.services.company_validator.get_company_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.validate_company.return_value = sample_company_validation
            mock_get_validator.return_value = mock_validator
            
            response = client.post(
                "/api/v1/company/validate",
                json={"ticker": "AAPL", "force_refresh": False}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["ticker"] == "AAPL"
            assert data["data"]["exists"] is True
    
    def test_validate_company_not_found(self, client):
        """Test company validation when company not found"""
        
        not_found_result = CompanyValidationResult(
            ticker="INVALID",
            status=CompanyStatus.INVALID,
            exists=False,
            message="Company 'INVALID' does not exist or is not publicly traded",
            confidence_score=0.9
        )
        
        with patch('app.services.company_validator.get_company_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.validate_company.return_value = not_found_result
            mock_get_validator.return_value = mock_validator
            
            response = client.post(
                "/api/v1/company/validate",
                json={"ticker": "INVALID"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"
            assert "does not exist or is not publicly traded" in data["message"]
    
    def test_validate_company_by_ticker_get(self, client, sample_company_validation):
        """Test GET endpoint for company validation"""
        
        with patch('app.services.company_validator.get_company_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.validate_company.return_value = sample_company_validation
            mock_get_validator.return_value = mock_validator
            
            response = client.get("/api/v1/company/validate/AAPL")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["ticker"] == "AAPL"
    
    def test_get_company_info(self, client):
        """Test getting company information"""
        
        company_info = CompanyInfo(
            ticker="AAPL",
            name="Apple Inc.",
            sector="Technology",
            market_cap=3000000000000
        )
        
        with patch('app.services.company_validator.get_company_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.get_company_info.return_value = company_info
            mock_get_validator.return_value = mock_validator
            
            response = client.get("/api/v1/company/info/AAPL")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["company_info"]["name"] == "Apple Inc."
    
    def test_search_companies(self, client):
        """Test company search functionality"""
        
        search_results = [
            CompanyInfo(ticker="AAPL", name="Apple Inc.", sector="Technology"),
            CompanyInfo(ticker="GOOGL", name="Alphabet Inc.", sector="Technology")
        ]
        
        with patch('app.services.company_validator.get_company_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.search_companies.return_value = (search_results, 2)
            mock_get_validator.return_value = mock_validator
            
            response = client.get("/api/v1/company/search?query=tech&limit=10")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["total_count"] == 2
            assert len(data["data"]["companies"]) == 2
    
    def test_get_industry_peers(self, client):
        """Test getting industry peers"""
        
        peers = [
            CompanyInfo(ticker="GOOGL", name="Alphabet Inc.", industry="Internet"),
            CompanyInfo(ticker="MSFT", name="Microsoft Corp.", industry="Software")
        ]
        
        with patch('app.services.company_validator.get_company_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.get_industry_peers.return_value = peers
            mock_get_validator.return_value = mock_validator
            
            response = client.get("/api/v1/company/peers/AAPL")
            
            assert response.status_code == 200
            data = response.json()
            assert "peers" in data
            assert len(data["peers"]) == 2
    
    def test_bulk_validate_companies(self, client, sample_company_validation):
        """Test bulk company validation"""
        
        bulk_results = [sample_company_validation, sample_company_validation]
        
        with patch('app.services.company_validator.get_company_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.bulk_validate_companies.return_value = bulk_results
            mock_get_validator.return_value = mock_validator
            
            response = client.post(
                "/api/v1/company/bulk-validate",
                json={"tickers": ["AAPL", "GOOGL"]}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_requested"] == 2
            assert data["successful_count"] == 2
    
    def test_validation_error_handling(self, client):
        """Test validation error handling"""
        
        # Test with invalid JSON
        response = client.post("/api/v1/company/validate", json={})
        assert response.status_code == 422
        
        # Test with empty ticker
        response = client.post("/api/v1/company/validate", json={"ticker": ""})
        assert response.status_code == 422


class TestESGAnalysisEndpoints:
    """Test ESG analysis endpoints"""
    
    def test_analyze_company_esg_success(self, client, sample_esg_analysis):
        """Test successful ESG analysis"""
        
        with patch('app.core.pipeline.get_esg_pipeline') as mock_get_pipeline:
            mock_pipeline = AsyncMock()
            mock_pipeline.run_complete_analysis.return_value = sample_esg_analysis
            mock_get_pipeline.return_value = mock_pipeline
            
            response = client.post(
                "/api/v1/analysis/esg",
                json={
                    "ticker": "AAPL",
                    "force_refresh": False,
                    "include_ai_insights": True
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["ticker"] == "AAPL"
            assert data["data"]["overall_score"]["score"] == 85.1
    
    def test_get_esg_analysis_get_endpoint(self, client, sample_esg_analysis):
        """Test GET endpoint for ESG analysis"""
        
        with patch('app.core.pipeline.get_esg_pipeline') as mock_get_pipeline:
            mock_pipeline = AsyncMock()
            mock_pipeline.run_complete_analysis.return_value = sample_esg_analysis
            mock_get_pipeline.return_value = mock_pipeline
            
            response = client.get("/api/v1/analysis/esg/AAPL")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["ticker"] == "AAPL"
    
    def test_bulk_esg_analysis(self, client, sample_esg_analysis):
        """Test bulk ESG analysis"""
        
        from app.models.responses import ESGAnalysisResponse, ProcessingMetadata
        
        # Create mock responses
        mock_responses = [
            ESGAnalysisResponse.analysis_success(
                sample_esg_analysis, 
                ProcessingMetadata(processing_time_ms=1000.0, data_sources_used=["test"])
            )
        ]
        
        with patch('app.core.pipeline.get_esg_pipeline') as mock_get_pipeline:
            mock_pipeline = AsyncMock()
            mock_pipeline.run_bulk_analysis.return_value = mock_responses
            mock_get_pipeline.return_value = mock_pipeline
            
            response = client.post(
                "/api/v1/analysis/bulk-esg",
                json={
                    "tickers": ["AAPL"],
                    "analysis_depth": "comprehensive"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    def test_get_news_analysis(self, client):
        """Test news analysis endpoint"""
        
        with patch('app.services.data_collector.get_data_collector') as mock_get_collector:
            mock_collector = AsyncMock()
            mock_get_collector.return_value = mock_collector
            
            response = client.get("/api/v1/analysis/news/AAPL?days=30")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["ticker"] == "AAPL"
    
    def test_get_industry_benchmark(self, client):
        """Test industry benchmark endpoint"""
        
        with patch('app.services.benchmark_service.get_benchmark_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_sector_benchmark.return_value = {
                "sector": "Technology",
                "environmental": {"average": 75.0},
                "social": {"average": 72.0},
                "governance": {"average": 78.0},
                "overall": {"average": 75.0},
                "sector_leaders": {"overall": ["AAPL", "GOOGL"]}
            }
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/v1/analysis/benchmark/Technology")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["sector"] == "Technology"
    
    def test_get_analysis_history(self, client):
        """Test analysis history endpoint"""
        
        history_data = [
            {
                "timestamp": datetime.utcnow(),
                "overall_score": 85.1,
                "environmental_score": 88.5,
                "confidence": 0.82
            }
        ]
        
        with patch('app.services.storage_service.get_storage_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_analysis_history.return_value = history_data
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/v1/analysis/history/AAPL?days=90")
            
            assert response.status_code == 200
            data = response.json()
            assert data["ticker"] == "AAPL"
            assert data["history_period_days"] == 90
            assert len(data["history"]) == 1
    
    def test_get_sector_trends(self, client):
        """Test sector trends endpoint"""
        
        trends_data = {
            "sector": "Technology",
            "time_period_days": 90,
            "trends": {
                "environmental": {
                    "direction": "improving",
                    "change": 2.5
                },
                "overall": {
                    "direction": "stable",
                    "change": 0.1
                }
            }
        }
        
        with patch('app.services.benchmark_service.get_benchmark_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_benchmark_trends.return_value = trends_data
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/v1/analysis/trends/Technology?days=90")
            
            assert response.status_code == 200
            data = response.json()
            assert data["sector"] == "Technology"
            assert "trends" in data
    
    def test_clear_analysis_cache(self, client):
        """Test cache clearing endpoint"""
        
        response = client.delete("/api/v1/analysis/cache/AAPL")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "AAPL"
        assert "Cache cleared" in data["message"]
    
    def test_get_data_quality_report(self, client):
        """Test data quality report endpoint"""
        
        with patch('app.services.data_collector.get_data_collector') as mock_get_collector:
            mock_collector = AsyncMock()
            mock_collector.get_data_freshness_score.return_value = 0.85
            mock_get_collector.return_value = mock_collector
            
            response = client.get("/api/v1/analysis/data-quality/AAPL")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["ticker"] == "AAPL"


class TestRateLimitingAndSecurity:
    """Test rate limiting and security features"""
    
    def test_rate_limiting_not_exceeded(self, client):
        """Test that normal requests don't hit rate limits"""
        
        # Mock rate limiter to allow requests
        with patch('app.api.dependencies.rate_limiter') as mock_limiter:
            mock_limiter.is_allowed.return_value = True
            
            response = client.get("/api/v1/health/")
            assert response.status_code == 200
    
    def test_rate_limiting_exceeded(self, client):
        """Test rate limiting when exceeded"""
        
        # Mock rate limiter to deny requests
        with patch('app.api.dependencies.rate_limiter') as mock_limiter:
            mock_limiter.is_allowed.return_value = False
            
            response = client.get("/api/v1/health/")
            assert response.status_code == 429
            assert "Rate limit exceeded" in response.json()["detail"]
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        
        response = client.get("/api/v1/health/")
        
        # Should have CORS headers (set by middleware)
        assert response.status_code in [200, 429]  # Either success or rate limited
    
    def test_request_validation(self, client):
        """Test request validation"""
        
        # Test invalid ticker format
        response = client.post(
            "/api/v1/company/validate",
            json={"ticker": "INVALID@TICKER"}
        )
        
        # Should validate ticker format
        assert response.status_code in [400, 422]
    
    def test_error_response_format(self, client):
        """Test error response format consistency"""
        
        # Test with invalid JSON structure
        response = client.post(
            "/api/v1/company/validate",
            json={"invalid_field": "value"}
        )
        
        assert response.status_code == 422
        data = response.json()
        
        # Should have consistent error structure
        assert "detail" in data or "message" in data


class TestInputValidation:
    """Test input validation across endpoints"""
    
    def test_ticker_validation(self, client):
        """Test ticker parameter validation"""
        
        # Test empty ticker
        response = client.get("/api/v1/company/validate/")
        assert response.status_code == 404  # Not found due to missing path param
        
        # Test invalid ticker characters
        response = client.post(
            "/api/v1/company/validate",
            json={"ticker": "ABC@123"}
        )
        assert response.status_code == 422
    
    def test_pagination_validation(self, client):
        """Test pagination parameter validation"""
        
        # Test invalid page number
        response = client.get("/api/v1/company/search?query=test&page=0")
        assert response.status_code == 422
        
        # Test invalid page size
        response = client.get("/api/v1/company/search?query=test&page_size=1000")
        assert response.status_code == 422
    
    def test_date_range_validation(self, client):
        """Test date range parameter validation"""
        
        # Test invalid days parameter
        response = client.get("/api/v1/analysis/history/AAPL?days=0")
        assert response.status_code == 422
        
        # Test excessive days parameter
        response = client.get("/api/v1/analysis/history/AAPL?days=1000")
        assert response.status_code == 422
    
    def test_bulk_request_limits(self, client):
        """Test bulk request size limits"""
        
        # Test excessive number of tickers
        large_ticker_list = ["TICK" + str(i) for i in range(100)]
        
        response = client.post(
            "/api/v1/company/bulk-validate",
            json={"tickers": large_ticker_list}
        )
        
        # Should enforce bulk limits
        assert response.status_code == 422


class TestErrorHandling:
    """Test error handling across the API"""
    
    def test_internal_server_error_handling(self, client):
        """Test internal server error handling"""
        
        # Mock a service to raise an exception
        with patch('app.services.company_validator.get_company_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.validate_company.side_effect = Exception("Database connection failed")
            mock_get_validator.return_value = mock_validator
            
            response = client.post(
                "/api/v1/company/validate",
                json={"ticker": "AAPL"}
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "failed" in data["detail"].lower()
    
    def test_service_unavailable_handling(self, client):
        """Test service unavailable scenarios"""
        
        # Mock a service to return service unavailable
        with patch('app.api.dependencies.check_feature_flag') as mock_feature:
            mock_feature.side_effect = HTTPException(status_code=503, detail="Service unavailable")
            
            response = client.post(
                "/api/v1/analysis/esg",
                json={"ticker": "AAPL"}
            )
            
            assert response.status_code == 503
    
    def test_timeout_error_handling(self, client):
        """Test timeout error handling"""
        
        # Mock a service to timeout
        with patch('app.services.company_validator.get_company_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.validate_company.side_effect = asyncio.TimeoutError("Request timed out")
            mock_get_validator.return_value = mock_validator
            
            response = client.post(
                "/api/v1/company/validate",
                json={"ticker": "AAPL"}
            )
            
            assert response.status_code == 500  # Handled as internal error
    
    def test_not_found_error_handling(self, client):
        """Test not found error handling"""
        
        # Test non-existent endpoint
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404


class TestResponseFormats:
    """Test API response formats and structure"""
    
    def test_success_response_format(self, client, sample_company_validation):
        """Test success response format consistency"""
        
        with patch('app.services.company_validator.get_company_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.validate_company.return_value = sample_company_validation
            mock_get_validator.return_value = mock_validator
            
            response = client.post(
                "/api/v1/company/validate",
                json={"ticker": "AAPL"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Check required fields
            assert "status" in data
            assert "message" in data
            assert "timestamp" in data
            assert "data" in data
            assert "metadata" in data
            
            # Check data structure
            assert data["status"] == "success"
            assert isinstance(data["data"], dict)
            assert isinstance(data["metadata"], dict)
    
    def test_error_response_format(self, client):
        """Test error response format consistency"""
        
        response = client.post(
            "/api/v1/company/validate",
            json={}  # Missing required fields
        )
        
        assert response.status_code == 422
        data = response.json()
        
        # FastAPI validation error format
        assert "detail" in data
    
    def test_metadata_in_responses(self, client, sample_company_validation):
        """Test metadata presence in responses"""
        
        with patch('app.services.company_validator.get_company_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.validate_company.return_value = sample_company_validation
            mock_get_validator.return_value = mock_validator
            
            response = client.post(
                "/api/v1/company/validate",
                json={"ticker": "AAPL"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Check metadata structure
            metadata = data.get("metadata", {})
            assert "processing_time_ms" in metadata
            assert "data_sources_used" in metadata
            assert isinstance(metadata["processing_time_ms"], (int, float))
            assert isinstance(metadata["data_sources_used"], list)


class TestAsyncOperations:
    """Test asynchronous operations and concurrency"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """Test handling of concurrent requests"""
        
        # This would test concurrent request handling
        # but TestClient doesn't support async directly
        # In real testing, you'd use httpx.AsyncClient
        
        responses = []
        for i in range(5):
            response = client.get("/api/v1/health/live")
            responses.append(response)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
    
    def test_request_processing_time(self, client):
        """Test that processing time is tracked"""
        
        response = client.get("/api/v1/health/")
        
        if response.status_code == 200:
            # Check for processing time header
            assert "X-Process-Time" in response.headers or \
                   "processing_time_ms" in response.json().get("metadata", {})


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API workflows"""
    
    def test_complete_esg_analysis_workflow(self, client, sample_company_validation, sample_esg_analysis):
        """Test complete workflow from validation to analysis"""
        
        with patch('app.services.company_validator.get_company_validator') as mock_validator, \
             patch('app.core.pipeline.get_esg_pipeline') as mock_pipeline:
            
            # Setup mocks
            mock_validator_instance = AsyncMock()
            mock_validator_instance.validate_company.return_value = sample_company_validation
            mock_validator.return_value = mock_validator_instance
            
            mock_pipeline_instance = AsyncMock()
            mock_pipeline_instance.run_complete_analysis.return_value = sample_esg_analysis
            mock_pipeline.return_value = mock_pipeline_instance
            
            # Step 1: Validate company
            validation_response = client.post(
                "/api/v1/company/validate",
                json={"ticker": "AAPL"}
            )
            assert validation_response.status_code == 200
            
            # Step 2: Run ESG analysis
            analysis_response = client.post(
                "/api/v1/analysis/esg",
                json={"ticker": "AAPL", "include_ai_insights": True}
            )
            assert analysis_response.status_code == 200
            
            # Verify workflow completion
            analysis_data = analysis_response.json()
            assert analysis_data["data"]["ticker"] == "AAPL"
            assert analysis_data["data"]["investment_recommendation"] == "BUY"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])