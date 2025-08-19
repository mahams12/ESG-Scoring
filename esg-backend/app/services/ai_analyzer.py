"""
AI-powered ESG analysis engine using OpenAI GPT-4
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
import openai
from openai import AsyncOpenAI

from app.config import get_settings
from app.models.esg_analysis import (
    ESGAnalysis, ESGScore, InvestmentRecommendation, RiskLevel,
    AIAnalysisInsight, calculate_overall_esg_score, 
    determine_risk_level, generate_investment_recommendation
)
from app.models.company import FinancialMetrics
from app.database import DatabaseRepository


class AIAnalysisEngine:
    """AI-powered ESG analysis using OpenAI GPT-4"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.api.openai_api_key)
        self.analysis_repo = DatabaseRepository("ai_analysis")
        
    async def analyze_esg_comprehensive(
        self,
        ticker: str,
        company_name: str,
        sector: str,
        industry: str,
        financial_data: Dict[str, Any],
        esg_data: Dict[str, Any],
        news_data: List[Dict[str, Any]] = None,
        peer_data: Dict[str, Any] = None
    ) -> ESGAnalysis:
        """
        Perform comprehensive AI-powered ESG analysis
        
        Args:
            ticker: Stock ticker symbol
            company_name: Full company name
            sector: Company sector
            industry: Company industry
            financial_data: Financial metrics and ratios
            esg_data: ESG metrics from multiple sources
            news_data: Recent news articles and sentiment
            peer_data: Industry peer comparison data
            
        Returns:
            Complete ESG analysis with AI insights
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting AI ESG analysis for {ticker}")
            
            # Prepare data for AI analysis
            analysis_context = self._prepare_analysis_context(
                ticker, company_name, sector, industry,
                financial_data, esg_data, news_data, peer_data
            )
            
            # Generate AI analysis
            ai_response = await self._generate_ai_analysis(analysis_context)
            
            # Parse AI response
            parsed_analysis = self._parse_ai_response(ai_response)
            
            # Create ESG scores
            environmental_score = ESGScore(
                score=parsed_analysis.get("environmental_score", 50),
                confidence_level=parsed_analysis.get("environmental_confidence", 0.7),
                industry_average=peer_data.get("environmental_avg", 50) if peer_data else None
            )
            
            social_score = ESGScore(
                score=parsed_analysis.get("social_score", 50),
                confidence_level=parsed_analysis.get("social_confidence", 0.7),
                industry_average=peer_data.get("social_avg", 50) if peer_data else None
            )
            
            governance_score = ESGScore(
                score=parsed_analysis.get("governance_score", 50),
                confidence_level=parsed_analysis.get("governance_confidence", 0.7),
                industry_average=peer_data.get("governance_avg", 50) if peer_data else None
            )
            
            # Calculate overall score
            overall_score_value = calculate_overall_esg_score(
                environmental_score.score,
                social_score.score,
                governance_score.score
            )
            
            overall_score = ESGScore(
                score=overall_score_value,
                confidence_level=min([
                    environmental_score.confidence_level,
                    social_score.confidence_level,
                    governance_score.confidence_level
                ]),
                industry_average=peer_data.get("overall_avg", 50) if peer_data else None
            )
            
            # Determine risk level and investment recommendation
            risk_level = determine_risk_level(overall_score_value, [])
            investment_recommendation = generate_investment_recommendation(
                overall_score_value, 
                risk_level,
                financial_data.get("financial_health_score")
            )
            
            # Create AI insights
            ai_insights = self._create_ai_insights(parsed_analysis)
            
            # Create complete ESG analysis
            esg_analysis = ESGAnalysis(
                ticker=ticker,
                company_name=company_name,
                sector=sector,
                industry=industry,
                environmental_score=environmental_score,
                social_score=social_score,
                governance_score=governance_score,
                overall_score=overall_score,
                investment_recommendation=investment_recommendation,
                risk_level=risk_level,
                investment_thesis=parsed_analysis.get("investment_thesis", ""),
                key_strengths=parsed_analysis.get("key_strengths", []),
                key_weaknesses=parsed_analysis.get("key_weaknesses", []),
                improvement_areas=parsed_analysis.get("improvement_areas", []),
                ai_insights=ai_insights,
                ai_summary=parsed_analysis.get("executive_summary", ""),
                ai_confidence=parsed_analysis.get("overall_confidence", 0.7),
                data_sources=esg_data.get("data_sources", [])
            )
            
            # Cache the analysis
            await self._cache_analysis(ticker, esg_analysis)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info(f"AI ESG analysis completed for {ticker} in {processing_time:.2f}ms")
            
            return esg_analysis
            
        except Exception as e:
            logger.error(f"AI ESG analysis failed for {ticker}: {str(e)}")
            raise
    
    def _prepare_analysis_context(
        self,
        ticker: str,
        company_name: str,
        sector: str,
        industry: str,
        financial_data: Dict[str, Any],
        esg_data: Dict[str, Any],
        news_data: Optional[List[Dict[str, Any]]],
        peer_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare context data for AI analysis"""
        
        # Format financial context
        financial_context = {}
        if financial_data:
            financial_context = {
                "revenue": financial_data.get("revenue"),
                "market_cap": financial_data.get("market_cap"),
                "profit_margin": financial_data.get("profit_margin"),
                "debt_to_equity": financial_data.get("debt_to_equity"),
                "return_on_equity": financial_data.get("return_on_equity"),
                "financial_health_score": financial_data.get("financial_health_score")
            }
        
        # Format ESG context
        esg_context = {}
        if esg_data:
            environmental_metrics = esg_data.get("environmental_metrics", {})
            social_metrics = esg_data.get("social_metrics", {})
            governance_metrics = esg_data.get("governance_metrics", {})
            
            esg_context = {
                "environmental": {
                    "carbon_emissions": environmental_metrics.get("carbon_emissions"),
                    "renewable_energy": environmental_metrics.get("renewable_energy_percentage"),
                    "environmental_violations": environmental_metrics.get("environmental_violations"),
                    "environmental_fines": environmental_metrics.get("environmental_fines")
                },
                "social": {
                    "workplace_safety_incidents": social_metrics.get("workplace_safety_incidents"),
                    "employee_satisfaction": social_metrics.get("employee_satisfaction_score"),
                    "diversity_percentage": social_metrics.get("diversity_percentage")
                },
                "governance": {
                    "board_independence": governance_metrics.get("board_independence_percentage"),
                    "executive_compensation": governance_metrics.get("executive_compensation_ratio"),
                    "ethics_violations": governance_metrics.get("ethics_violations"),
                    "transparency_score": governance_metrics.get("transparency_score")
                }
            }
        
        # Format news sentiment
        news_context = {}
        if news_data:
            total_articles = len(news_data)
            positive_sentiment = sum(1 for article in news_data if article.get("sentiment", 0) > 0.1)
            negative_sentiment = sum(1 for article in news_data if article.get("sentiment", 0) < -0.1)
            
            news_context = {
                "total_articles": total_articles,
                "positive_sentiment_ratio": positive_sentiment / total_articles if total_articles > 0 else 0,
                "negative_sentiment_ratio": negative_sentiment / total_articles if total_articles > 0 else 0,
                "recent_headlines": [article.get("title", "") for article in news_data[:5]]
            }
        
        # Format peer comparison
        peer_context = {}
        if peer_data:
            peer_context = {
                "industry_esg_average": peer_data.get("industry_avg_score"),
                "peer_companies": peer_data.get("peer_tickers", []),
                "industry_ranking": peer_data.get("ranking"),
                "top_quartile_threshold": peer_data.get("top_quartile")
            }
        
        return {
            "company": {
                "ticker": ticker,
                "name": company_name,
                "sector": sector,
                "industry": industry
            },
            "financial_data": financial_context,
            "esg_data": esg_context,
            "news_sentiment": news_context,
            "peer_comparison": peer_context
        }
    
    async def _generate_ai_analysis(self, context: Dict[str, Any]) -> str:
        """Generate AI analysis using OpenAI GPT-4"""
        
        # Create comprehensive prompt
        prompt = self._build_analysis_prompt(context)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.api.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert ESG (Environmental, Social, Governance) analyst with deep knowledge of sustainable investing, corporate responsibility, and financial analysis. Provide comprehensive, objective, and data-driven ESG analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.settings.api.openai_max_tokens,
                temperature=self.settings.api.openai_temperature,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            # Retry once after delay
            await asyncio.sleep(2)
            try:
                response = await self.client.chat.completions.create(
                    model=self.settings.api.openai_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an ESG analyst. Provide objective ESG analysis."
                        },
                        {
                            "role": "user",
                            "content": self._build_simplified_prompt(context)
                        }
                    ],
                    max_tokens=1000,
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                return response.choices[0].message.content
            except Exception as retry_error:
                logger.error(f"OpenAI retry failed: {str(retry_error)}")
                raise
    
    def _build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build comprehensive analysis prompt for AI"""
        
        company = context["company"]
        financial_data = context["financial_data"]
        esg_data = context["esg_data"]
        news_sentiment = context["news_sentiment"]
        peer_comparison = context["peer_comparison"]
        
        prompt = f"""
        Analyze the ESG performance of {company["name"]} ({company["ticker"]}) in the {company["sector"]} sector.
        
        COMPANY INFORMATION:
        - Sector: {company["sector"]}
        - Industry: {company["industry"]}
        
        FINANCIAL CONTEXT:
        - Market Cap: {financial_data.get("market_cap")}
        - Revenue: {financial_data.get("revenue")}
        - Profit Margin: {financial_data.get("profit_margin")}%
        - Debt-to-Equity: {financial_data.get("debt_to_equity")}
        - ROE: {financial_data.get("return_on_equity")}%
        - Financial Health Score: {financial_data.get("financial_health_score")}/100
        
        ENVIRONMENTAL DATA:
        - Carbon Emissions: {esg_data["environmental"].get("carbon_emissions")}
        - Renewable Energy %: {esg_data["environmental"].get("renewable_energy")}%
        - Environmental Violations: {esg_data["environmental"].get("environmental_violations")}
        - Environmental Fines: ${esg_data["environmental"].get("environmental_fines")}
        
        SOCIAL DATA:
        - Workplace Safety Incidents: {esg_data["social"].get("workplace_safety_incidents")}
        - Employee Satisfaction: {esg_data["social"].get("employee_satisfaction")}/100
        - Diversity Percentage: {esg_data["social"].get("diversity_percentage")}%
        
        GOVERNANCE DATA:
        - Board Independence: {esg_data["governance"].get("board_independence")}%
        - Executive Compensation Ratio: {esg_data["governance"].get("executive_compensation")}
        - Ethics Violations: {esg_data["governance"].get("ethics_violations")}
        - Transparency Score: {esg_data["governance"].get("transparency_score")}/100
        
        NEWS SENTIMENT ANALYSIS:
        - Total Recent Articles: {news_sentiment.get("total_articles")}
        - Positive Sentiment Ratio: {news_sentiment.get("positive_sentiment_ratio", 0):.2f}
        - Negative Sentiment Ratio: {news_sentiment.get("negative_sentiment_ratio", 0):.2f}
        
        PEER COMPARISON:
        - Industry ESG Average: {peer_comparison.get("industry_esg_average")}/100
        - Industry Ranking: {peer_comparison.get("industry_ranking")}
        - Top Quartile Threshold: {peer_comparison.get("top_quartile")}
        
        ANALYSIS REQUIREMENTS:
        
        Provide a comprehensive ESG analysis in JSON format with the following structure:
        
        {{
            "environmental_score": <0-100>,
            "environmental_confidence": <0-1>,
            "environmental_reasoning": "<detailed explanation>",
            "social_score": <0-100>,
            "social_confidence": <0-1>,
            "social_reasoning": "<detailed explanation>",
            "governance_score": <0-100>,
            "governance_confidence": <0-1>,
            "governance_reasoning": "<detailed explanation>",
            "overall_confidence": <0-1>,
            "investment_thesis": "<comprehensive investment thesis>",
            "key_strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
            "key_weaknesses": ["<weakness 1>", "<weakness 2>", "<weakness 3>"],
            "improvement_areas": ["<area 1>", "<area 2>", "<area 3>"],
            "risk_factors": ["<risk 1>", "<risk 2>", "<risk 3>"],
            "opportunities": ["<opportunity 1>", "<opportunity 2>", "<opportunity 3>"],
            "industry_positioning": "<analysis of position vs peers>",
            "future_outlook": "<forward-looking assessment>",
            "executive_summary": "<concise summary of overall ESG assessment>",
            "ai_insights": [
                {{
                    "category": "<insight category>",
                    "insight": "<detailed insight>",
                    "confidence": <0-1>,
                    "supporting_data": ["<data point 1>", "<data point 2>"]
                }}
            ]
        }}
        
        SCORING GUIDELINES:
        - Environmental (0-100): Consider carbon footprint, renewable energy usage, environmental compliance, waste management
        - Social (0-100): Evaluate employee relations, community impact, product safety, supply chain practices
        - Governance (0-100): Assess board structure, executive compensation, transparency, ethics
        - Be objective and data-driven
        - Consider industry context and peer comparison
        - Factor in recent news sentiment and controversies
        - Provide confidence scores based on data availability and quality
        """
        
        return prompt
    
    def _build_simplified_prompt(self, context: Dict[str, Any]) -> str:
        """Build simplified prompt for fallback analysis"""
        
        company = context["company"]
        
        return f"""
        Provide ESG analysis for {company["name"]} ({company["ticker"]}) in JSON format:
        {{
            "environmental_score": <0-100>,
            "social_score": <0-100>,
            "governance_score": <0-100>,
            "environmental_confidence": 0.5,
            "social_confidence": 0.5,
            "governance_confidence": 0.5,
            "overall_confidence": 0.5,
            "investment_thesis": "Limited data available for comprehensive analysis",
            "key_strengths": ["To be determined with more data"],
            "key_weaknesses": ["Data availability limitations"],
            "improvement_areas": ["Enhanced ESG reporting"],
            "executive_summary": "ESG assessment based on limited available data",
            "ai_insights": []
        }}
        """
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response JSON"""
        try:
            parsed = json.loads(ai_response)
            
            # Validate and sanitize scores
            for score_field in ["environmental_score", "social_score", "governance_score"]:
                if score_field in parsed:
                    parsed[score_field] = max(0, min(100, float(parsed[score_field])))
            
            # Validate confidence scores
            for conf_field in ["environmental_confidence", "social_confidence", "governance_confidence", "overall_confidence"]:
                if conf_field in parsed:
                    parsed[conf_field] = max(0, min(1, float(parsed[conf_field])))
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            # Return default response
            return {
                "environmental_score": 50,
                "social_score": 50,
                "governance_score": 50,
                "environmental_confidence": 0.3,
                "social_confidence": 0.3,
                "governance_confidence": 0.3,
                "overall_confidence": 0.3,
                "investment_thesis": "Analysis failed - using default scores",
                "key_strengths": [],
                "key_weaknesses": ["AI analysis unavailable"],
                "improvement_areas": [],
                "executive_summary": "ESG analysis could not be completed",
                "ai_insights": []
            }
    
    def _create_ai_insights(self, parsed_analysis: Dict[str, Any]) -> List[AIAnalysisInsight]:
        """Create AI insights from parsed analysis"""
        insights = []
        
        try:
            ai_insights_data = parsed_analysis.get("ai_insights", [])
            
            for insight_data in ai_insights_data:
                if isinstance(insight_data, dict):
                    insight = AIAnalysisInsight(
                        category=insight_data.get("category", "General"),
                        insight=insight_data.get("insight", ""),
                        confidence=insight_data.get("confidence", 0.5),
                        supporting_data=insight_data.get("supporting_data", [])
                    )
                    insights.append(insight)
            
            # Add default insights if none provided
            if not insights:
                insights = [
                    AIAnalysisInsight(
                        category="Analysis Quality",
                        insight="ESG analysis completed with available data sources",
                        confidence=0.7,
                        supporting_data=["Multi-source data collection", "AI-powered analysis"]
                    )
                ]
            
        except Exception as e:
            logger.warning(f"Failed to create AI insights: {str(e)}")
        
        return insights
    
    async def _cache_analysis(self, ticker: str, analysis: ESGAnalysis):
        """Cache AI analysis results"""
        try:
            document = {
                "ticker": ticker,
                "type": "ai_esg_analysis",
                "analysis": analysis.dict(),
                "analysis_timestamp": analysis.analysis_timestamp,
                "expires_at": datetime.utcnow() + timedelta(hours=2)  # 2-hour cache
            }
            
            await self.analysis_repo.upsert(
                {"ticker": ticker, "type": "ai_esg_analysis"},
                document
            )
            
        except Exception as e:
            logger.error(f"Failed to cache AI analysis for {ticker}: {str(e)}")
    
    async def get_cached_analysis(self, ticker: str) -> Optional[ESGAnalysis]:
        """Get cached AI analysis if available"""
        try:
            cached_doc = await self.analysis_repo.find_one({
                "ticker": ticker,
                "type": "ai_esg_analysis",
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if cached_doc:
                analysis_data = cached_doc.get("analysis")
                return ESGAnalysis(**analysis_data)
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get cached analysis for {ticker}: {str(e)}")
            return None
    
    async def health_check(self) -> bool:
        """Check AI service health"""
        try:
            # Test OpenAI API connectivity
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Health check"}],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"AI service health check failed: {str(e)}")
            return False


# Global service instance
ai_analyzer = AIAnalysisEngine()


def get_ai_analyzer() -> AIAnalysisEngine:
    """Get AI analyzer service instance"""
    return ai_analyzer