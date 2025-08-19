"""
Company data models and schemas
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class CompanyStatus(str, Enum):
    """Company validation status"""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    ERROR = "error"


class MarketCapCategory(str, Enum):
    """Market capitalization categories"""
    MEGA_CAP = "mega_cap"      # > $200B
    LARGE_CAP = "large_cap"    # $10B - $200B
    MID_CAP = "mid_cap"        # $2B - $10B
    SMALL_CAP = "small_cap"    # $300M - $2B
    MICRO_CAP = "micro_cap"    # $50M - $300M
    NANO_CAP = "nano_cap"      # < $50M


class Sector(str, Enum):
    """Industry sectors"""
    TECHNOLOGY = "Technology"
    HEALTHCARE = "Healthcare"
    FINANCIALS = "Financials"
    CONSUMER_DISCRETIONARY = "Consumer Discretionary"
    CONSUMER_STAPLES = "Consumer Staples"
    INDUSTRIALS = "Industrials"
    ENERGY = "Energy"
    UTILITIES = "Utilities"
    MATERIALS = "Materials"
    REAL_ESTATE = "Real Estate"
    COMMUNICATION_SERVICES = "Communication Services"


class CompanyBase(BaseModel):
    """Base company model"""
    ticker: str = Field(..., description="Stock ticker symbol", min_length=1, max_length=10)
    name: str = Field(..., description="Company name", min_length=1, max_length=200)
    
    @validator('ticker')
    def ticker_must_be_uppercase(cls, v):
        return v.upper().strip()
    
    @validator('name')
    def name_must_be_clean(cls, v):
        return v.strip()


class CompanyInfo(CompanyBase):
    """Extended company information"""
    sector: Optional[Sector] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    market_cap_category: Optional[MarketCapCategory] = None
    employees: Optional[int] = None
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    currency: Optional[str] = "USD"
    exchange: Optional[str] = None
    country: Optional[str] = None
    
    @validator('market_cap')
    def validate_market_cap(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Market cap must be positive')
        return v
    
    @validator('founded_year')
    def validate_founded_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1800 or v > current_year:
                raise ValueError(f'Founded year must be between 1800 and {current_year}')
        return v


class FinancialMetrics(BaseModel):
    """Company financial metrics"""
    revenue: Optional[float] = None
    revenue_growth: Optional[float] = None
    net_income: Optional[float] = None
    total_debt: Optional[float] = None
    total_equity: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    return_on_equity: Optional[float] = None
    return_on_assets: Optional[float] = None
    profit_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    free_cash_flow: Optional[float] = None
    price_to_earnings: Optional[float] = None
    price_to_book: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None
    
    fiscal_year: Optional[int] = None
    reporting_currency: str = "USD"
    data_source: Optional[str] = None
    last_updated: Optional[datetime] = None


class CompanyValidationResult(BaseModel):
    """Company validation result"""
    ticker: str
    status: CompanyStatus
    exists: bool
    message: str
    company_info: Optional[CompanyInfo] = None
    validation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    data_sources_checked: List[str] = []
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)


class CompanyCreate(CompanyBase):
    """Company creation model"""
    pass


class CompanyUpdate(BaseModel):
    """Company update model"""
    name: Optional[str] = None
    sector: Optional[Sector] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    employees: Optional[int] = None
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    
    @validator('name')
    def name_must_be_clean(cls, v):
        if v is not None:
            return v.strip()
        return v


class Company(CompanyInfo):
    """Complete company model with database fields"""
    id: Optional[str] = Field(None, alias="_id")
    status: CompanyStatus = CompanyStatus.PENDING
    last_validated: Optional[datetime] = None
    validation_count: int = 0
    financial_metrics: Optional[FinancialMetrics] = None
    data_sources: List[str] = []
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CompanyResponse(Company):
    """Company response model for API"""
    pass


class CompanySearchResult(BaseModel):
    """Company search result"""
    companies: List[CompanyResponse]
    total_count: int
    page: int = 1
    page_size: int = 20
    has_next: bool = False
    has_previous: bool = False


class CompanyAnalysisStatus(BaseModel):
    """Company analysis status"""
    ticker: str
    has_esg_analysis: bool = False
    last_esg_analysis: Optional[datetime] = None
    has_financial_data: bool = False
    last_financial_update: Optional[datetime] = None
    data_freshness_score: float = Field(0.0, ge=0.0, le=1.0)
    analysis_ready: bool = False


class IndustryPeers(BaseModel):
    """Industry peer companies"""
    sector: str
    industry: str
    peer_companies: List[CompanyResponse]
    market_cap_range: Dict[str, float]
    total_peers: int


class CompanyValidationRequest(BaseModel):
    """Request model for company validation"""
    ticker: str = Field(..., description="Stock ticker symbol")
    force_refresh: bool = Field(False, description="Force fresh validation")
    
    @validator('ticker')
    def ticker_must_be_valid(cls, v):
        v = v.upper().strip()
        if not v:
            raise ValueError('Ticker cannot be empty')
        if len(v) > 10:
            raise ValueError('Ticker too long')
        # Basic ticker format validation
        if not v.replace('.', '').replace('-', '').isalnum():
            raise ValueError('Invalid ticker format')
        return v


class CompanyMetrics(BaseModel):
    """Company metrics summary"""
    ticker: str
    name: str
    sector: Optional[str]
    market_cap: Optional[float]
    market_cap_category: Optional[MarketCapCategory]
    financial_health_score: Optional[float] = None
    esg_score: Optional[float] = None
    last_analysis: Optional[datetime] = None
    data_quality_score: float = Field(0.0, ge=0.0, le=1.0)


def classify_market_cap(market_cap: Optional[float]) -> Optional[MarketCapCategory]:
    """Classify company by market capitalization"""
    if market_cap is None:
        return None
    
    if market_cap >= 200_000_000_000:  # $200B+
        return MarketCapCategory.MEGA_CAP
    elif market_cap >= 10_000_000_000:  # $10B+
        return MarketCapCategory.LARGE_CAP
    elif market_cap >= 2_000_000_000:   # $2B+
        return MarketCapCategory.MID_CAP
    elif market_cap >= 300_000_000:     # $300M+
        return MarketCapCategory.SMALL_CAP
    elif market_cap >= 50_000_000:      # $50M+
        return MarketCapCategory.MICRO_CAP
    else:
        return MarketCapCategory.NANO_CAP


def calculate_financial_health_score(metrics: FinancialMetrics) -> float:
    """Calculate financial health score from metrics"""
    score = 0.0
    factors = 0
    
    # Profitability factors
    if metrics.profit_margin is not None:
        if metrics.profit_margin > 0.15:
            score += 20
        elif metrics.profit_margin > 0.05:
            score += 10
        factors += 1
    
    if metrics.return_on_equity is not None:
        if metrics.return_on_equity > 0.15:
            score += 20
        elif metrics.return_on_equity > 0.05:
            score += 10
        factors += 1
    
    # Liquidity factors
    if metrics.current_ratio is not None:
        if metrics.current_ratio >= 1.5:
            score += 15
        elif metrics.current_ratio >= 1.0:
            score += 10
        factors += 1
    
    # Leverage factors
    if metrics.debt_to_equity is not None:
        if metrics.debt_to_equity < 0.3:
            score += 15
        elif metrics.debt_to_equity < 0.6:
            score += 10
        elif metrics.debt_to_equity < 1.0:
            score += 5
        factors += 1
    
    # Growth factors
    if metrics.revenue_growth is not None:
        if metrics.revenue_growth > 0.1:
            score += 15
        elif metrics.revenue_growth > 0.05:
            score += 10
        elif metrics.revenue_growth > 0:
            score += 5
        factors += 1
    
    # Cash flow factors
    if metrics.free_cash_flow is not None and metrics.revenue is not None:
        if metrics.revenue > 0:
            fcf_margin = metrics.free_cash_flow / metrics.revenue
            if fcf_margin > 0.1:
                score += 15
            elif fcf_margin > 0.05:
                score += 10
            elif fcf_margin > 0:
                score += 5
        factors += 1
    
    return (score / factors) if factors > 0 else 0.0