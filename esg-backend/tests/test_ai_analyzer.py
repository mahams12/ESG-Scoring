"""
Tests for AI-powered ESG analysis engine
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.services.ai_analyzer import AIAnalysisEngine
from app.models.esg_analysis import (
    ESGAnalysis, ESGScore, InvestmentRecommendation, 
    RiskLevel, AIAnalysisInsight
)
from app.utils.exceptions import AIAnalysisError


class TestAIAnalysisEngine:
    """Test suite for AIAnalysisEngine"""
    
    @pytest.fixture
    def ai_analyzer(self):
        """Create AIAnalysisEngine instance for testing"""
        return AIAnalysisEngine()
    
    @pytest.fixture
    def sample_analysis_context(self):
        """Sample context data for AI analysis"""
        return {
            "company": {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics"
            },
            "financial_data": {
                "revenue": 394328000000,
                "market_cap": 3000000000000,
                "profit_margin": 25.3,
                "debt_to_equity": 1.97,
                "return_on_equity": 160.1,
                "financial_health_score": 85.2
            },
            "esg_data": {
                "environmental": {
                    "carbon_emissions": 22600000,
                    "renewable_energy": 100,
                    "environmental_violations": 0,
                    "environmental_fines": 0
                },
                "social": {
                    "workplace_safety_incidents": 2,
                    "employee_satisfaction": 82,
                    "diversity_percentage": 45
                },
                "governance": {
                    "board_independence": 67,
                    "executive_compensation": 1000,
                    "ethics_violations": 0,
                    "transparency_score": 88
                }
            },
            "news_sentiment": {
                "total_articles": 15,
                "positive_sentiment_ratio": 0.6,
                "negative_sentiment_ratio": 0.2,
                "recent_headlines": [
                    "Apple Reports Strong Quarterly Results",
                    "Apple Announces New Sustainability Initiative"
                ]
            },
            "peer_comparison": {
                "industry_esg_average": 72.5,
                "peer_tickers": ["GOOGL", "MSFT", "META"],
                "ranking": 2,
                "top_quartile": 80.0
            }
        }
    
    @pytest.fixture
    def sample_ai_response(self):
        """Sample AI response JSON"""
        return {
            "environmental_score": 88.5,
            "environmental_confidence": 0.85,
            "environmental_reasoning": "Strong renewable energy commitment and carbon neutrality goals",
            "social_score": 82.1,
            "social_confidence": 0.8,
            "social_reasoning": "Good employee practices with some supply chain concerns",
            "governance_score": 84.8,
            "governance_confidence": 0.82,
            "governance_reasoning": "Strong board independence and transparency practices",
            "overall_confidence": 0.82,
            "investment_thesis": "Apple demonstrates strong ESG leadership with comprehensive sustainability initiatives",
            "key_strengths": [
                "100% renewable energy in operations",
                "Strong financial performance",
                "Good governance practices"
            ],
            "key_weaknesses": [
                "Supply chain labor concerns",
                "High executive compensation",
                "Limited community engagement disclosure"
            ],
            "improvement_areas": [
                "Enhanced supply chain transparency",
                "Expanded social impact programs",
                "Better stakeholder engagement"
            ],
            "risk_factors": [
                "Regulatory changes in key markets",
                "Supply chain disruptions",
                "Competitive pressure"
            ],
            "opportunities": [
                "Circular economy initiatives",
                "Emerging market expansion",
                "AI for sustainability"
            ],
            "industry_positioning": "Apple ranks in the top quartile for ESG performance in the technology sector",
            "future_outlook": "Positive trajectory with continued focus on sustainability and innovation",
            "executive_summary": "Apple demonstrates exceptional ESG performance with strong environmental leadership and governance practices",
            "ai_insights": [
                {
                    "category": "Environmental Leadership",
                    "insight": "Apple's commitment to carbon neutrality sets industry standards",
                    "confidence": 0.9,
                    "supporting_data": ["100% renewable energy", "Carbon neutral supply chain goal"]
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_analyze_esg_comprehensive_success(self, ai_analyzer, sample_analysis_context, sample_ai_response):
        """Test successful comprehensive ESG analysis"""
        
        # Mock OpenAI API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(sample_ai_response)
        
        with patch.object(ai_analyzer.client.chat.completions, 'create', return_value=mock_response) as mock_create, \
             patch.object(ai_analyzer, '_cache_analysis') as mock_cache:
            
            # Test comprehensive analysis
            result = await ai_analyzer.analyze_esg_comprehensive(
                ticker="AAPL",
                company_name="Apple Inc.",
                sector="Technology",
                industry="Consumer Electronics",
                financial_data=sample_analysis_context["financial_data"],
                esg_data=sample_analysis_context["esg_data"],
                news_data=[],
                peer_data=sample_analysis_context["peer_comparison"]
            )
            
            # Assertions
            assert isinstance(result, ESGAnalysis)
            assert result.ticker == "AAPL"
            assert result.company_name == "Apple Inc."
            assert result.environmental_score.score == 88.5
            assert result.social_score.score == 82.1
            assert result.governance_score.score == 84.8
            assert result.ai_confidence == 0.82
            assert len(result.key_strengths) == 3
            assert len(result.ai_insights) > 0
            
            # Verify OpenAI was called
            mock_create.assert_called_once()
            
            # Verify caching
            mock_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_prepare_analysis_context(self, ai_analyzer):
        """Test preparation of analysis context"""
        
        financial_data = {
            "revenue": 394328000000,
            "market_cap": 3000000000000,
            "profit_margin": 25.3
        }
        
        esg_data = {
            "environmental_metrics": {
                "carbon_emissions": 22600000,
                "renewable_energy_percentage": 100
            },
            "social_metrics": {
                "workplace_safety_incidents": 2,
                "employee_satisfaction_score": 82
            },
            "governance_metrics": {
                "board_independence_percentage": 67,
                "transparency_score": 88
            }
        }
        
        news_data = [
            {
                "title": "Apple Reports Strong Results",
                "sentiment": 0.8
            }
        ]
        
        peer_data = {
            "industry_avg_score": 72.5,
            "peer_tickers": ["GOOGL", "MSFT"]
        }
        
        # Test context preparation
        context = ai_analyzer._prepare_analysis_context(
            ticker="AAPL",
            company_name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics",
            financial_data=financial_data,
            esg_data=esg_data,
            news_data=news_data,
            peer_data=peer_data
        )
        
        # Assertions
        assert context["company"]["ticker"] == "AAPL"
        assert context["company"]["name"] == "Apple Inc."
        assert context["financial_data"]["revenue"] == 394328000000
        assert context["esg_data"]["environmental"]["carbon_emissions"] == 22600000
        assert context["news_sentiment"]["total_articles"] == 1
        assert context["peer_comparison"]["industry_esg_average"] == 72.5
    
    @pytest.mark.asyncio
    async def test_generate_ai_analysis_success(self, ai_analyzer, sample_analysis_context, sample_ai_response):
        """Test successful AI analysis generation"""
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(sample_ai_response)
        
        with patch.object(ai_analyzer.client.chat.completions, 'create', return_value=mock_response):
            
            # Test AI analysis generation
            result = await ai_analyzer._generate_ai_analysis(sample_analysis_context)
            
            # Assertions
            assert isinstance(result, str)
            parsed_result = json.loads(result)
            assert parsed_result["environmental_score"] == 88.5
            assert parsed_result["overall_confidence"] == 0.82
    
    @pytest.mark.asyncio
    async def test_generate_ai_analysis_with_retry(self, ai_analyzer, sample_analysis_context, sample_ai_response):
        """Test AI analysis generation with retry mechanism"""
        
        # Mock first call failure, second call success
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(sample_ai_response)
        
        with patch.object(ai_analyzer.client.chat.completions, 'create') as mock_create:
            # First call raises exception, second succeeds
            mock_create.side_effect = [Exception("API Error"), mock_response]
            
            # Test with retry
            result = await ai_analyzer._generate_ai_analysis(sample_analysis_context)
            
            # Should succeed after retry
            assert isinstance(result, str)
            assert mock_create.call_count == 2
    
    def test_parse_ai_response_success(self, ai_analyzer, sample_ai_response):
        """Test successful AI response parsing"""
        
        ai_response_json = json.dumps(sample_ai_response)
        
        # Test parsing
        parsed = ai_analyzer._parse_ai_response(ai_response_json)
        
        # Assertions
        assert parsed["environmental_score"] == 88.5
        assert parsed["social_score"] == 82.1
        assert parsed["governance_score"] == 84.8
        assert 0 <= parsed["environmental_confidence"] <= 1
        assert len(parsed["key_strengths"]) == 3
    
    def test_parse_ai_response_invalid_json(self, ai_analyzer):
        """Test AI response parsing with invalid JSON"""
        
        invalid_json = "This is not valid JSON"
        
        # Test parsing invalid JSON
        parsed = ai_analyzer._parse_ai_response(invalid_json)
        
        # Should return default response
        assert parsed["environmental_score"] == 50
        assert parsed["social_score"] == 50
        assert parsed["governance_score"] == 50
        assert "AI analysis unavailable" in parsed["executive_summary"]
    
    def test_parse_ai_response_score_validation(self, ai_analyzer):
        """Test AI response parsing with score validation"""
        
        # Test with out-of-range scores
        invalid_response = {
            "environmental_score": 150,  # Too high
            "social_score": -10,  # Too low
            "governance_score": 75,  # Valid
            "environmental_confidence": 1.5,  # Too high
            "social_confidence": -0.1,  # Too low
            "governance_confidence": 0.8,  # Valid
            "overall_confidence": 0.7,
            "investment_thesis": "Test thesis",
            "key_strengths": [],
            "key_weaknesses": [],
            "improvement_areas": [],
            "executive_summary": "Test summary",
            "ai_insights": []
        }
        
        ai_response_json = json.dumps(invalid_response)
        
        # Test parsing with validation
        parsed = ai_analyzer._parse_ai_response(ai_response_json)
        
        # Scores should be clamped to valid ranges
        assert 0 <= parsed["environmental_score"] <= 100
        assert 0 <= parsed["social_score"] <= 100
        assert parsed["governance_score"] == 75  # Should remain unchanged
        
        # Confidence scores should be clamped to 0-1
        assert 0 <= parsed["environmental_confidence"] <= 1
        assert 0 <= parsed["social_confidence"] <= 1
        assert parsed["governance_confidence"] == 0.8  # Should remain unchanged
    
    def test_create_ai_insights_success(self, ai_analyzer):
        """Test creation of AI insights from parsed analysis"""
        
        parsed_analysis = {
            "ai_insights": [
                {
                    "category": "Environmental Leadership",
                    "insight": "Strong renewable energy commitment",
                    "confidence": 0.9,
                    "supporting_data": ["100% renewable energy", "Carbon neutral goals"]
                },
                {
                    "category": "Governance Risk",
                    "insight": "Executive compensation concerns",
                    "confidence": 0.7,
                    "supporting_data": ["High CEO pay ratio"]
                }
            ]
        }
        
        # Test insights creation
        insights = ai_analyzer._create_ai_insights(parsed_analysis)
        
        # Assertions
        assert len(insights) == 2
        assert all(isinstance(insight, AIAnalysisInsight) for insight in insights)
        assert insights[0].category == "Environmental Leadership"
        assert insights[0].confidence == 0.9
        assert len(insights[0].supporting_data) == 2
    
    def test_create_ai_insights_empty(self, ai_analyzer):
        """Test creation of AI insights with empty data"""
        
        parsed_analysis = {"ai_insights": []}
        
        # Test insights creation with empty data
        insights = ai_analyzer._create_ai_insights(parsed_analysis)
        
        # Should create default insight
        assert len(insights) == 1
        assert insights[0].category == "Analysis Quality"
        assert "ESG analysis completed" in insights[0].insight
    
    def test_build_analysis_prompt(self, ai_analyzer, sample_analysis_context):
        """Test building of comprehensive analysis prompt"""
        
        # Test prompt building
        prompt = ai_analyzer._build_analysis_prompt(sample_analysis_context)
        
        # Assertions
        assert "Apple Inc." in prompt
        assert "AAPL" in prompt
        assert "Technology" in prompt
        assert "394328000000" in prompt  # Revenue
        assert "renewable_energy" in prompt
        assert "board_independence" in prompt
        assert "JSON" in prompt  # Should request JSON format
    
    def test_build_simplified_prompt(self, ai_analyzer, sample_analysis_context):
        """Test building of simplified fallback prompt"""
        
        # Test simplified prompt
        prompt = ai_analyzer._build_simplified_prompt(sample_analysis_context)
        
        # Assertions
        assert "Apple Inc." in prompt
        assert "AAPL" in prompt
        assert "JSON" in prompt
        assert len(prompt) < 500  # Should be shorter than comprehensive prompt
    
    @pytest.mark.asyncio
    async def test_cache_analysis(self, ai_analyzer):
        """Test caching of AI analysis results"""
        
        # Create sample ESG analysis
        environmental_score = ESGScore(score=88.5, confidence_level=0.85)
        social_score = ESGScore(score=82.1, confidence_level=0.8)
        governance_score = ESGScore(score=84.8, confidence_level=0.82)
        overall_score = ESGScore(score=85.1, confidence_level=0.82)
        
        analysis = ESGAnalysis(
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
            investment_thesis="Strong ESG performer",
            key_strengths=["Renewable energy", "Good governance"],
            key_weaknesses=["Supply chain concerns"],
            improvement_areas=["Social impact"],
            ai_insights=[],
            ai_summary="Comprehensive ESG analysis",
            ai_confidence=0.82,
            data_sources=["multiple"]
        )
        
        with patch.object(ai_analyzer.analysis_repo, 'upsert') as mock_upsert:
            mock_upsert.return_value = True
            
            # Test caching
            await ai_analyzer._cache_analysis("AAPL", analysis)
            
            # Verify cache call
            mock_upsert.assert_called_once()
            call_args = mock_upsert.call_args
            assert call_args[0][0]["ticker"] == "AAPL"
            assert call_args[0][0]["type"] == "ai_esg_analysis"
    
    @pytest.mark.asyncio
    async def test_get_cached_analysis(self, ai_analyzer):
        """Test retrieving cached AI analysis"""
        
        # Mock cached analysis data
        cached_data = {
            "ticker": "AAPL",
            "analysis": {
                "ticker": "AAPL",
                "company_name": "Apple Inc.",
                "environmental_score": {"score": 88.5, "confidence_level": 0.85},
                "social_score": {"score": 82.1, "confidence_level": 0.8},
                "governance_score": {"score": 84.8, "confidence_level": 0.82},
                "overall_score": {"score": 85.1, "confidence_level": 0.82},
                "investment_recommendation": "BUY",
                "risk_level": "LOW_MEDIUM",
                "investment_thesis": "Strong ESG performer",
                "key_strengths": ["Renewable energy"],
                "key_weaknesses": ["Supply chain"],
                "improvement_areas": ["Social impact"],
                "ai_insights": [],
                "ai_summary": "Test summary",
                "ai_confidence": 0.82,
                "data_sources": ["test"],
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "analysis_version": "2.0"
            }
        }
        
        with patch.object(ai_analyzer.analysis_repo, 'find_one') as mock_find:
            mock_find.return_value = cached_data
            
            # Test cache retrieval
            result = await ai_analyzer.get_cached_analysis("AAPL")
            
            # Assertions
            assert isinstance(result, ESGAnalysis)
            assert result.ticker == "AAPL"
            assert result.environmental_score.score == 88.5
    
    @pytest.mark.asyncio
    async def test_get_cached_analysis_not_found(self, ai_analyzer):
        """Test retrieving cached analysis when not found"""
        
        with patch.object(ai_analyzer.analysis_repo, 'find_one') as mock_find:
            mock_find.return_value = None
            
            # Test cache retrieval with no data
            result = await ai_analyzer.get_cached_analysis("AAPL")
            
            # Should return None
            assert result is None
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, ai_analyzer):
        """Test AI service health check success"""
        
        # Mock successful OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Health check response"
        
        with patch.object(ai_analyzer.client.chat.completions, 'create', return_value=mock_response):
            
            # Test health check
            is_healthy = await ai_analyzer.health_check()
            
            # Should be healthy
            assert is_healthy is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, ai_analyzer):
        """Test AI service health check failure"""
        
        with patch.object(ai_analyzer.client.chat.completions, 'create') as mock_create:
            mock_create.side_effect = Exception("API Error")
            
            # Test health check with failure
            is_healthy = await ai_analyzer.health_check()
            
            # Should be unhealthy
            assert is_healthy is False
    
    @pytest.mark.asyncio
    async def test_analyze_esg_with_minimal_data(self, ai_analyzer):
        """Test ESG analysis with minimal input data"""
        
        # Minimal context
        minimal_context = {
            "company": {
                "ticker": "TEST",
                "name": "Test Company",
                "sector": "Unknown",
                "industry": "Unknown"
            },
            "financial_data": {},
            "esg_data": {},
            "news_sentiment": {},
            "peer_comparison": {}
        }
        
        # Mock AI response for minimal data
        minimal_ai_response = {
            "environmental_score": 50,
            "social_score": 50,
            "governance_score": 50,
            "environmental_confidence": 0.3,
            "social_confidence": 0.3,
            "governance_confidence": 0.3,
            "overall_confidence": 0.3,
            "investment_thesis": "Limited data available",
            "key_strengths": [],
            "key_weaknesses": ["Limited data"],
            "improvement_areas": ["Enhanced reporting"],
            "executive_summary": "Analysis based on limited data",
            "ai_insights": []
        }
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(minimal_ai_response)
        
        with patch.object(ai_analyzer.client.chat.completions, 'create', return_value=mock_response), \
             patch.object(ai_analyzer, '_cache_analysis'):
            
            # Test analysis with minimal data
            result = await ai_analyzer.analyze_esg_comprehensive(
                ticker="TEST",
                company_name="Test Company",
                sector="Unknown",
                industry="Unknown",
                financial_data={},
                esg_data={}
            )
            
            # Should still produce valid analysis
            assert isinstance(result, ESGAnalysis)
            assert result.ticker == "TEST"
            assert result.ai_confidence == 0.3  # Lower confidence for minimal data


@pytest.mark.asyncio
async def test_ai_analyzer_integration():
    """Integration test for AI analyzer with mocked OpenAI API"""
    
    analyzer = AIAnalysisEngine()
    
    # Complete mock AI response
    ai_response = {
        "environmental_score": 85.0,
        "social_score": 78.0,
        "governance_score": 82.0,
        "environmental_confidence": 0.8,
        "social_confidence": 0.75,
        "governance_confidence": 0.85,
        "overall_confidence": 0.8,
        "investment_thesis": "Strong ESG performer with good fundamentals",
        "key_strengths": ["Environmental leadership", "Strong governance"],
        "key_weaknesses": ["Social impact disclosure"],
        "improvement_areas": ["Community engagement"],
        "executive_summary": "Comprehensive ESG analysis shows strong performance",
        "ai_insights": [
            {
                "category": "Environmental",
                "insight": "Leading in renewable energy",
                "confidence": 0.9,
                "supporting_data": ["100% renewable energy"]
            }
        ]
    }
    
    # Mock OpenAI API
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(ai_response)
    
    with patch.object(analyzer.client.chat.completions, 'create', return_value=mock_response), \
         patch.object(analyzer, '_cache_analysis'):
        
        # Test full integration
        result = await analyzer.analyze_esg_comprehensive(
            ticker="AAPL",
            company_name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics",
            financial_data={"revenue": 394328000000},
            esg_data={"environmental_metrics": {"renewable_energy_percentage": 100}}
        )
        
        # Verify complete analysis
        assert isinstance(result, ESGAnalysis)
        assert result.environmental_score.score == 85.0
        assert result.investment_recommendation in [
            InvestmentRecommendation.BUY, 
            InvestmentRecommendation.STRONG_BUY,
            InvestmentRecommendation.HOLD
        ]


if __name__ == "__main__":
    pytest.main([__file__])