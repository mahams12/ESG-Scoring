"""
ESG Analysis data models and schemas
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ESGRatingGrade(str, Enum):
    """ESG rating grades"""
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    CCC = "CCC"


class InvestmentRecommendation(str, Enum):
    """Investment recommendations"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class RiskLevel(str, Enum):
    """ESG risk levels"""
    LOW = "LOW"
    LOW_MEDIUM = "LOW_MEDIUM"
    MEDIUM = "MEDIUM"
    MEDIUM_HIGH = "MEDIUM_HIGH"
    HIGH = "HIGH"


class DataQuality(str, Enum):
    """Data quality indicators"""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"
    INSUFFICIENT = "INSUFFICIENT"


class EnvironmentalMetrics(BaseModel):
    """Environmental performance metrics"""
    carbon_emissions: Optional[float] = Field(None, description="CO2 emissions in metric tons")
    carbon_intensity: Optional[float] = Field(None, description="Carbon intensity per revenue")
    renewable_energy_percentage: Optional[float] = Field(None, ge=0, le=100)
    water_usage: Optional[float] = Field(None, description="Water usage in cubic meters")
    waste_generated: Optional[float] = Field(None, description="Waste generated in metric tons")
    waste_recycled_percentage: Optional[float] = Field(None, ge=0, le=100)
    energy_consumption: Optional[float] = Field(None, description="Energy consumption in MWh")
    environmental_violations: Optional[int] = Field(None, ge=0)
    environmental_fines: Optional[float] = Field(None, ge=0)
    biodiversity_impact_score: Optional[float] = Field(None, ge=0, le=100)
    circular_economy_score: Optional[float] = Field(None, ge=0, le=100)
    climate_change_adaptation: Optional[float] = Field(None, ge=0, le=100)
    
    data_sources: List[str] = []
    last_updated: Optional[datetime] = None


class SocialMetrics(BaseModel):
    """Social performance metrics"""
    employee_satisfaction_score: Optional[float] = Field(None, ge=0, le=100)
    diversity_percentage: Optional[float] = Field(None, ge=0, le=100)
    gender_pay_gap: Optional[float] = Field(None, description="Gender pay gap percentage")
    employee_turnover_rate: Optional[float] = Field(None, ge=0, le=100)
    training_hours_per_employee: Optional[float] = Field(None, ge=0)
    workplace_safety_incidents: Optional[int] = Field(None, ge=0)
    community_investment: Optional[float] = Field(None, ge=0)
    customer_satisfaction_score: Optional[float] = Field(None, ge=0, le=100)
    data_privacy_score: Optional[float] = Field(None, ge=0, le=100)
    product_safety_score: Optional[float] = Field(None, ge=0, le=100)
    supply_chain_labor_score: Optional[float] = Field(None, ge=0, le=100)
    human_rights_score: Optional[float] = Field(None, ge=0, le=100)
    
    data_sources: List[str] = []
    last_updated: Optional[datetime] = None


class GovernanceMetrics(BaseModel):
    """Governance performance metrics"""
    board_independence_percentage: Optional[float] = Field(None, ge=0, le=100)
    board_diversity_percentage: Optional[float] = Field(None, ge=0, le=100)
    executive_compensation_ratio: Optional[float] = Field(None, ge=0)
    audit_quality_score: Optional[float] = Field(None, ge=0, le=100)
    transparency_score: Optional[float] = Field(None, ge=0, le=100)
    ethics_violations: Optional[int] = Field(None, ge=0)
    regulatory_fines: Optional[float] = Field(None, ge=0)
    cybersecurity_score: Optional[float] = Field(None, ge=0, le=100)
    risk_management_score: Optional[float] = Field(None, ge=0, le=100)
    shareholder_rights_score: Optional[float] = Field(None, ge=0, le=100)
    anti_corruption_score: Optional[float] = Field(None, ge=0, le=100)
    tax_transparency_score: Optional[float] = Field(None, ge=0, le=100)
    
    data_sources: List[str] = []
    last_updated: Optional[datetime] = None


class ESGScore(BaseModel):
    """Individual ESG dimension score"""
    score: float = Field(..., ge=0, le=100, description="Score from 0-100")
    grade: Optional[ESGRatingGrade] = None
    percentile_rank: Optional[float] = Field(None, ge=0, le=100)
    industry_average: Optional[float] = Field(None, ge=0, le=100)
    year_over_year_change: Optional[float] = None
    confidence_level: float = Field(0.0, ge=0, le=1.0)
    data_quality: DataQuality = DataQuality.FAIR
    
    @field_validator('grade', mode='before')
    @classmethod
    def calculate_grade(cls, v, info):
        """Calculate grade based on score"""
        if v is not None:
            return v
        
        if hasattr(info, 'data') and 'score' in info.data:
            score = info.data['score']
            if score >= 90:
                return ESGRatingGrade.AAA
            elif score >= 80:
                return ESGRatingGrade.AA
            elif score >= 70:
                return ESGRatingGrade.A
            elif score >= 60:
                return ESGRatingGrade.BBB
            elif score >= 50:
                return ESGRatingGrade.BB
            elif score >= 40:
                return ESGRatingGrade.B
            else:
                return ESGRatingGrade.CCC
        return v


class NewsArticle(BaseModel):
    """News article related to ESG"""
    title: str
    content: Optional[str] = None
    url: str
    published_at: datetime
    source: str
    sentiment: Optional[float] = Field(None, ge=-1, le=1, description="Sentiment score -1 to 1")
    esg_relevance_score: Optional[float] = Field(None, ge=0, le=1)
    keywords: List[str] = []
    category: Optional[str] = None


class ESGControversy(BaseModel):
    """ESG-related controversy"""
    title: str
    description: str
    severity: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    category: str  # Environmental, Social, Governance
    date: datetime
    status: str = Field(..., pattern="^(ONGOING|RESOLVED|MONITORING)$")
    financial_impact: Optional[float] = None
    sources: List[str] = []


class BenchmarkComparison(BaseModel):
    """Benchmark comparison data"""
    industry_average: float = Field(..., ge=0, le=100)
    sector_average: float = Field(..., ge=0, le=100)
    market_cap_peer_average: float = Field(..., ge=0, le=100)
    percentile_rank: float = Field(..., ge=0, le=100)
    top_quartile_threshold: float = Field(..., ge=0, le=100)
    bottom_quartile_threshold: float = Field(..., ge=0, le=100)
    peer_companies: List[str] = []
    ranking_position: Optional[int] = None
    total_companies_compared: Optional[int] = None


class AIAnalysisInsight(BaseModel):
    """AI-generated analysis insight"""
    category: str  # e.g., "Environmental Leadership", "Governance Risk"
    insight: str
    confidence: float = Field(..., ge=0, le=1)
    supporting_data: List[str] = []
    recommendation: Optional[str] = None


class ESGAnalysis(BaseModel):
    """Complete ESG analysis results"""
    ticker: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    
    # ESG Scores
    environmental_score: ESGScore
    social_score: ESGScore
    governance_score: ESGScore
    overall_score: ESGScore
    
    # Raw metrics
    environmental_metrics: Optional[EnvironmentalMetrics] = None
    social_metrics: Optional[SocialMetrics] = None
    governance_metrics: Optional[GovernanceMetrics] = None
    
    # Analysis results
    investment_recommendation: InvestmentRecommendation
    risk_level: RiskLevel
    investment_thesis: str
    key_strengths: List[str] = []
    key_weaknesses: List[str] = []
    improvement_areas: List[str] = []
    
    # AI insights
    ai_insights: List[AIAnalysisInsight] = []
    ai_summary: str
    ai_confidence: float = Field(..., ge=0, le=1)
    
    # Benchmark data
    benchmark_comparison: Optional[BenchmarkComparison] = None
    
    # Supporting data
    recent_news: List[NewsArticle] = []
    controversies: List[ESGControversy] = []
    
    # Metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[str] = []
    analysis_version: str = "2.0"
    analyst_notes: Optional[str] = None
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class ESGAnalysisRequest(BaseModel):
    """Request model for ESG analysis"""
    ticker: str = Field(..., description="Stock ticker symbol")
    force_refresh: bool = Field(False, description="Force fresh analysis")
    include_ai_insights: bool = Field(True, description="Include AI-generated insights")
    include_benchmarks: bool = Field(True, description="Include benchmark comparison")
    include_news: bool = Field(True, description="Include recent news analysis")
    analysis_depth: str = Field("comprehensive", pattern="^(basic|standard|comprehensive)$")
    
    @field_validator('ticker')
    @classmethod
    def ticker_must_be_valid(cls, v):
        return v.upper().strip()


class ESGTrendData(BaseModel):
    """ESG trend data over time"""
    ticker: str
    metric: str
    time_series: List[Dict[str, Union[datetime, float]]]
    trend_direction: str = Field(..., pattern="^(IMPROVING|DECLINING|STABLE|VOLATILE)$")
    trend_strength: float = Field(..., ge=0, le=1)
    correlation_with_performance: Optional[float] = Field(None, ge=-1, le=1)


class ESGPortfolioAnalysis(BaseModel):
    """Portfolio-level ESG analysis"""
    portfolio_name: str
    companies: List[str]  # List of tickers
    weighted_esg_score: float = Field(..., ge=0, le=100)
    environmental_score: float = Field(..., ge=0, le=100)
    social_score: float = Field(..., ge=0, le=100)
    governance_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    sector_distribution: Dict[str, float]
    top_performers: List[str]
    bottom_performers: List[str]
    analysis_date: datetime = Field(default_factory=datetime.utcnow)


class ESGAlert(BaseModel):
    """ESG-related alert"""
    ticker: str
    alert_type: str = Field(..., pattern="^(SCORE_DECLINE|CONTROVERSY|REGULATORY|NEWS)$")
    severity: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    title: str
    description: str
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    related_metrics: List[str] = []
    recommended_actions: List[str] = []


class ESGDataQualityReport(BaseModel):
    """Data quality assessment for ESG analysis"""
    ticker: str
    overall_quality: DataQuality
    environmental_data_quality: DataQuality
    social_data_quality: DataQuality
    governance_data_quality: DataQuality
    data_completeness_percentage: float = Field(..., ge=0, le=100)
    data_freshness_score: float = Field(..., ge=0, le=1)
    sources_reliability_score: float = Field(..., ge=0, le=1)
    missing_metrics: List[str] = []
    outdated_metrics: List[str] = []
    quality_issues: List[str] = []
    improvement_suggestions: List[str] = []


class ESGResponse(BaseModel):
    """Standard ESG API response"""
    success: bool = True
    message: str = "Analysis completed successfully"
    data: Optional[ESGAnalysis] = None
    errors: List[str] = []
    warnings: List[str] = []
    metadata: Dict[str, Any] = {}
    processing_time: Optional[float] = None


class ESGBulkAnalysisRequest(BaseModel):
    """Bulk ESG analysis request"""
    tickers: List[str] = Field(..., max_length=50, description="List of ticker symbols")
    analysis_depth: str = Field("standard", pattern="^(basic|standard|comprehensive)$")
    include_ai_insights: bool = True
    include_benchmarks: bool = True
    parallel_processing: bool = True
    
    @field_validator('tickers')
    @classmethod
    def validate_tickers(cls, v):
        if not v:
            raise ValueError('At least one ticker must be provided')
        return [ticker.upper().strip() for ticker in v]


class ESGBulkAnalysisResponse(BaseModel):
    """Bulk ESG analysis response"""
    total_requested: int
    total_completed: int
    total_failed: int
    results: List[ESGResponse]
    failed_tickers: List[str] = []
    processing_time: float
    analysis_summary: Dict[str, Any] = {}


def calculate_overall_esg_score(
    environmental: float, 
    social: float, 
    governance: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """Calculate overall ESG score from individual dimensions"""
    if weights is None:
        weights = {"environmental": 0.35, "social": 0.30, "governance": 0.35}
    
    total_weight = sum(weights.values())
    if abs(total_weight - 1.0) > 0.01:
        # Normalize weights if they don't sum to 1
        weights = {k: v / total_weight for k, v in weights.items()}
    
    overall_score = (
        environmental * weights["environmental"] +
        social * weights["social"] +
        governance * weights["governance"]
    )
    
    return round(overall_score, 2)


def determine_risk_level(esg_score: float, controversies: List[ESGControversy]) -> RiskLevel:
    """Determine risk level based on ESG score and controversies"""
    # Base risk from score
    if esg_score >= 80:
        base_risk = RiskLevel.LOW
    elif esg_score >= 70:
        base_risk = RiskLevel.LOW_MEDIUM
    elif esg_score >= 60:
        base_risk = RiskLevel.MEDIUM
    elif esg_score >= 50:
        base_risk = RiskLevel.MEDIUM_HIGH
    else:
        base_risk = RiskLevel.HIGH
    
    # Adjust for controversies
    high_severity_controversies = [
        c for c in controversies 
        if c.severity in ["HIGH", "CRITICAL"] and c.status == "ONGOING"
    ]
    
    if high_severity_controversies:
        if base_risk == RiskLevel.LOW:
            return RiskLevel.LOW_MEDIUM
        elif base_risk == RiskLevel.LOW_MEDIUM:
            return RiskLevel.MEDIUM
        elif base_risk == RiskLevel.MEDIUM:
            return RiskLevel.MEDIUM_HIGH
        else:
            return RiskLevel.HIGH
    
    return base_risk


def generate_investment_recommendation(
    esg_score: float, 
    risk_level: RiskLevel,
    financial_health_score: Optional[float] = None
) -> InvestmentRecommendation:
    """Generate investment recommendation based on ESG and financial factors"""
    # Base recommendation from ESG score
    if esg_score >= 85:
        base_rec = InvestmentRecommendation.STRONG_BUY
    elif esg_score >= 75:
        base_rec = InvestmentRecommendation.BUY
    elif esg_score >= 60:
        base_rec = InvestmentRecommendation.HOLD
    elif esg_score >= 45:
        base_rec = InvestmentRecommendation.SELL
    else:
        base_rec = InvestmentRecommendation.STRONG_SELL
    
    # Adjust for risk level
    if risk_level == RiskLevel.HIGH:
        if base_rec == InvestmentRecommendation.STRONG_BUY:
            return InvestmentRecommendation.BUY
        elif base_rec == InvestmentRecommendation.BUY:
            return InvestmentRecommendation.HOLD
        elif base_rec == InvestmentRecommendation.HOLD:
            return InvestmentRecommendation.SELL
    
    # Adjust for financial health if available
    if financial_health_score is not None:
        if financial_health_score < 40:  # Poor financial health
            if base_rec == InvestmentRecommendation.STRONG_BUY:
                return InvestmentRecommendation.BUY
            elif base_rec == InvestmentRecommendation.BUY:
                return InvestmentRecommendation.HOLD
    
    return base_rec


def calculate_data_quality_score(
    environmental_metrics: Optional[EnvironmentalMetrics],
    social_metrics: Optional[SocialMetrics],
    governance_metrics: Optional[GovernanceMetrics]
) -> DataQuality:
    """Calculate overall data quality based on available metrics"""
    total_possible_metrics = 36  # Total metrics across all dimensions
    available_metrics = 0
    
    if environmental_metrics:
        env_fields = [f for f in environmental_metrics.model_fields 
                     if f not in ['data_sources', 'last_updated']]
        available_metrics += sum(1 for field in env_fields 
                               if getattr(environmental_metrics, field) is not None)
    
    if social_metrics:
        social_fields = [f for f in social_metrics.model_fields 
                        if f not in ['data_sources', 'last_updated']]
        available_metrics += sum(1 for field in social_fields 
                               if getattr(social_metrics, field) is not None)
    
    if governance_metrics:
        gov_fields = [f for f in governance_metrics.model_fields 
                     if f not in ['data_sources', 'last_updated']]
        available_metrics += sum(1 for field in gov_fields 
                               if getattr(governance_metrics, field) is not None)
    
    completeness_ratio = available_metrics / total_possible_metrics
    
    if completeness_ratio >= 0.8:
        return DataQuality.EXCELLENT
    elif completeness_ratio >= 0.6:
        return DataQuality.GOOD
    elif completeness_ratio >= 0.4:
        return DataQuality.FAIR
    elif completeness_ratio >= 0.2:
        return DataQuality.POOR
    else:
        return DataQuality.INSUFFICIENT