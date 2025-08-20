# """
# Configuration management for ESG Investment Research System
# """

# import os
# import yaml
# from typing import Dict, List, Optional, Any
# from pydantic_settings import BaseSettings
# from pydantic import Field, field_validator
# from pathlib import Path


# class DatabaseConfig(BaseSettings):
#     """Database configuration"""
#     mongodb_connection_string: str = Field(..., env="MONGODB_CONNECTION_STRING")
#     database_name: str = Field("esg_research", env="MONGODB_DATABASE_NAME")
#     max_pool_size: int = 10
#     min_pool_size: int = 1
#     max_idle_time: int = 30000

#     model_config = {
#         "env_file": ".env",
#         "case_sensitive": False
#     }


# class APIConfig(BaseSettings):
#     """External API configuration"""
#     # Financial Modeling Prep
#     fmp_api_key: str = Field(..., env="FMP_API_KEY")
#     fmp_base_url: str = "https://financialmodelingprep.com/api/v3"
    
#     # OpenAI
#     openai_api_key: str = Field(..., env="OPENAI_API_KEY")
#     openai_model: str = "gpt-4"
#     openai_max_tokens: int = 2000
#     openai_temperature: float = 0.3
    
#     # News API
#     news_api_key: str = Field(..., env="NEWS_API_KEY")
#     news_base_url: str = "https://newsapi.org/v2"
    
#     # Alpha Vantage
#     alphavantage_api_key: str = Field(..., env="ALPHAVANTAGE_API_KEY")
#     alphavantage_base_url: str = "https://www.alphavantage.co"
    
#     # Reddit API
#     reddit_client_id: Optional[str] = Field(None, env="REDDIT_CLIENT_ID")
#     reddit_client_secret: Optional[str] = Field(None, env="REDDIT_CLIENT_SECRET")
#     reddit_user_agent: str = "ESG Research Bot 1.0"

#     model_config = {
#         "env_file": ".env",
#         "case_sensitive": False
#     }


# class RedisConfig(BaseSettings):
#     """Redis configuration"""
#     redis_host: str = Field("localhost", env="REDIS_HOST")
#     redis_port: int = Field(6379, env="REDIS_PORT")
#     redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
#     redis_db: int = 0
#     max_connections: int = 20

#     model_config = {
#         "env_file": ".env",
#         "case_sensitive": False
#     }


# class ScrapingConfig(BaseSettings):
#     """Web scraping configuration"""
#     user_agents: List[str] = Field(default_factory=lambda: [
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
#         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
#         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
#     ])
#     min_delay: int = 1
#     max_delay: int = 3
#     request_timeout: int = 30
#     max_retries: int = 3
#     backoff_factor: int = 2
#     headless: bool = True

#     model_config = {
#         "env_file": ".env",
#         "case_sensitive": False
#     }


# class CachingConfig(BaseSettings):
#     """Caching configuration"""
#     company_validation_ttl: int = 3600  # 1 hour
#     financial_data_ttl: int = 900       # 15 minutes
#     esg_ratings_ttl: int = 1800         # 30 minutes
#     news_data_ttl: int = 600            # 10 minutes
#     analysis_results_ttl: int = 7200    # 2 hours

#     model_config = {
#         "env_file": ".env",
#         "case_sensitive": False
#     }


# class SecurityConfig(BaseSettings):
#     """Security configuration"""
#     cors_origins: List[str] = Field(default_factory=lambda: [
#         "http://localhost:3000",
#         "https://esg-research-frontend.com"
#     ])
#     cors_methods: List[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
#     cors_headers: List[str] = Field(default_factory=lambda: ["Content-Type", "Authorization"])
#     secret_key: Optional[str] = Field(None, env="SECRET_KEY")
#     algorithm: str = Field("HS256", env="ALGORITHM")

#     model_config = {
#         "env_file": ".env",
#         "case_sensitive": False
#     }


# class ESGConfig(BaseSettings):
#     """ESG analysis configuration"""
#     environmental_weight: float = 0.35
#     social_weight: float = 0.30
#     governance_weight: float = 0.35
#     confidence_threshold: float = 0.7
#     max_ai_retries: int = 3

#     model_config = {
#         "env_file": ".env",
#         "case_sensitive": False
#     }


# class Config(BaseSettings):
#     """Main configuration class"""
#     # App settings
#     app_name: str = "ESG Investment Research System"
#     app_version: str = "2.0"
#     debug: bool = Field(False, env="DEBUG")
#     host: str = "0.0.0.0"
#     port: int = 8000
#     workers: int = 4
    
#     # Environment
#     environment: str = Field("development", env="ENVIRONMENT")
    
#     # Logging
#     log_level: str = "INFO"
#     log_format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    
#     model_config = {
#         "env_file": ".env",
#         "case_sensitive": False,
#         "extra": "ignore"  # This will ignore extra environment variables
#     }

#     @field_validator("environment")
#     @classmethod
#     def validate_environment(cls, v):
#         allowed = ["development", "staging", "production"]
#         if v not in allowed:
#             raise ValueError(f"Environment must be one of {allowed}")
#         return v

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         # Initialize sub-configurations after main config is loaded
#         self._database = None
#         self._api = None
#         self._redis = None
#         self._scraping = None
#         self._caching = None
#         self._security = None
#         self._esg = None
#         # Load YAML config if it exists
#         self._load_yaml_config()

#     @property
#     def database(self) -> DatabaseConfig:
#         """Get database configuration"""
#         if self._database is None:
#             self._database = DatabaseConfig()
#         return self._database

#     @property
#     def api(self) -> APIConfig:
#         """Get API configuration"""
#         if self._api is None:
#             self._api = APIConfig()
#         return self._api

#     @property
#     def redis(self) -> RedisConfig:
#         """Get Redis configuration"""
#         if self._redis is None:
#             self._redis = RedisConfig()
#         return self._redis

#     @property
#     def scraping(self) -> ScrapingConfig:
#         """Get scraping configuration"""
#         if self._scraping is None:
#             self._scraping = ScrapingConfig()
#         return self._scraping

#     @property
#     def caching(self) -> CachingConfig:
#         """Get caching configuration"""
#         if self._caching is None:
#             self._caching = CachingConfig()
#         return self._caching

#     @property
#     def security(self) -> SecurityConfig:
#         """Get security configuration"""
#         if self._security is None:
#             self._security = SecurityConfig()
#         return self._security

#     @property
#     def esg(self) -> ESGConfig:
#         """Get ESG configuration"""
#         if self._esg is None:
#             self._esg = ESGConfig()
#         return self._esg

#     def _load_yaml_config(self):
#         """Load additional configuration from YAML file"""
#         yaml_path = Path("config.yaml")
#         if yaml_path.exists():
#             try:
#                 with open(yaml_path, "r") as file:
#                     yaml_config = yaml.safe_load(file)
#                     self._merge_yaml_config(yaml_config)
#             except Exception as e:
#                 print(f"Warning: Could not load config.yaml: {e}")

#     def _merge_yaml_config(self, yaml_config: Dict[str, Any]):
#         """Merge YAML configuration with existing config"""
#         # Only merge non-sensitive configuration from YAML
#         if "app" in yaml_config:
#             app_config = yaml_config["app"]
#             if "debug" in app_config:
#                 self.debug = app_config["debug"]
#             if "host" in app_config:
#                 self.host = app_config["host"]
#             if "port" in app_config:
#                 self.port = app_config["port"]
#             if "workers" in app_config:
#                 self.workers = app_config["workers"]

#     @property
#     def mongodb_url(self) -> str:
#         """Get MongoDB connection URL"""
#         return self.database.mongodb_connection_string

#     @property
#     def is_production(self) -> bool:
#         """Check if running in production"""
#         return self.environment == "production"

#     @property
#     def is_development(self) -> bool:
#         """Check if running in development"""
#         return self.environment == "development"

#     def get_data_sources(self) -> Dict[str, List[Dict]]:
#         """Get configured data sources"""
#         return {
#             "financial": [
#                 {"name": "Financial Modeling Prep", "priority": 1, "enabled": True},
#                 {"name": "Yahoo Finance", "priority": 2, "enabled": True},
#                 {"name": "Alpha Vantage", "priority": 3, "enabled": True}
#             ],
#             "esg_ratings": [
#                 {
#                     "name": "Sustainalytics",
#                     "url": "https://www.sustainalytics.com",
#                     "priority": 1,
#                     "enabled": True,
#                     "scraping": True
#                 },
#                 {
#                     "name": "CDP",
#                     "url": "https://www.cdp.net",
#                     "priority": 2,
#                     "enabled": True,
#                     "scraping": True
#                 },
#                 {
#                     "name": "MSCI ESG",
#                     "url": "https://www.msci.com/our-solutions/esg-investing",
#                     "priority": 3,
#                     "enabled": True,
#                     "scraping": True
#                 }
#             ],
#             "news_sentiment": [
#                 {"name": "NewsAPI", "enabled": True},
#                 {"name": "Reddit", "enabled": bool(self.api.reddit_client_id)}
#             ]
#         }

#     def get_ai_prompt_template(self) -> str:
#         """Get AI analysis prompt template"""
#         return """
#         Analyze the following ESG data for {company_name} ({ticker}) in the {industry} sector:
        
#         Environmental Data: {environmental_data}
#         Social Data: {social_data}
#         Governance Data: {governance_data}
#         Financial Context: {financial_context}
#         Recent News: {news_sentiment}
        
#         Provide a comprehensive analysis with:
#         1. Environmental score (0-100) with detailed reasoning
#         2. Social score (0-100) with detailed reasoning
#         3. Governance score (0-100) with detailed reasoning
#         4. Overall ESG score and investment recommendation
#         5. Key risks and opportunities
#         6. Industry benchmark comparison
        
#         Format as JSON with scores and detailed explanations.
#         Be objective and data-driven in your analysis.
#         """

#     def get_collection_names(self) -> Dict[str, str]:
#         """Get MongoDB collection names"""
#         return {
#             "companies": "companies",
#             "esg_scores": "esg_scores",
#             "ai_analysis": "ai_analysis",
#             "benchmarks": "benchmarks",
#             "news_data": "news_data"
#         }


# # Global configuration instance
# _settings = None


# def get_settings() -> Config:
#     """Get application settings (singleton pattern)"""
#     global _settings
#     if _settings is None:
#         _settings = Config()
#     return _settings


# def load_config_from_file(file_path: str) -> Config:
#     """Load configuration from specific file"""
#     config = Config()
#     if os.path.exists(file_path):
#         with open(file_path, 'r') as file:
#             yaml_config = yaml.safe_load(file)
#             config._merge_yaml_config(yaml_config)
#     return config




"""
Configuration management for ESG Investment Research System
"""

import os
import yaml
from typing import Dict, List, Optional, Any
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from pathlib import Path


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    mongodb_connection_string: str = Field(..., env="MONGODB_CONNECTION_STRING")
    database_name: str = Field("esg_research", env="MONGODB_DATABASE_NAME")
    max_pool_size: int = 10
    min_pool_size: int = 1
    max_idle_time: int = 30000

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Added to ignore extra environment variables
    }


class APIConfig(BaseSettings):
    """External API configuration"""
    # Financial Modeling Prep
    fmp_api_key: str = Field(..., env="FMP_API_KEY")
    fmp_base_url: str = "https://financialmodelingprep.com/api/v3"
    
    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.3
    
    # News API
    news_api_key: str = Field(..., env="NEWS_API_KEY")
    news_base_url: str = "https://newsapi.org/v2"
    
    # Alpha Vantage
    alphavantage_api_key: str = Field(..., env="ALPHAVANTAGE_API_KEY")
    alphavantage_base_url: str = "https://www.alphavantage.co"
    
    # Reddit API
    reddit_client_id: Optional[str] = Field(None, env="REDDIT_CLIENT_ID")
    reddit_client_secret: Optional[str] = Field(None, env="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = "ESG Research Bot 1.0"

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Added to ignore extra environment variables
    }


class RedisConfig(BaseSettings):
    """Redis configuration"""
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_db: int = 0
    max_connections: int = 20

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Added to ignore extra environment variables
    }


class ScrapingConfig(BaseSettings):
    """Web scraping configuration"""
    user_agents: List[str] = Field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ])
    min_delay: int = 1
    max_delay: int = 3
    request_timeout: int = 30
    max_retries: int = 3
    backoff_factor: int = 2
    headless: bool = True

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Added to ignore extra environment variables
    }


class CachingConfig(BaseSettings):
    """Caching configuration"""
    company_validation_ttl: int = 3600  # 1 hour
    financial_data_ttl: int = 900       # 15 minutes
    esg_ratings_ttl: int = 1800         # 30 minutes
    news_data_ttl: int = 600            # 10 minutes
    analysis_results_ttl: int = 7200    # 2 hours

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Added to ignore extra environment variables
    }


class SecurityConfig(BaseSettings):
    """Security configuration"""
    cors_origins: List[str] = Field(default_factory=lambda: [
        "http://localhost:3000",
        "https://esg-research-frontend.com"
    ])
    cors_methods: List[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    cors_headers: List[str] = Field(default_factory=lambda: ["Content-Type", "Authorization"])
    secret_key: Optional[str] = Field(None, env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Added to ignore extra environment variables
    }


class ESGConfig(BaseSettings):
    """ESG analysis configuration"""
    environmental_weight: float = 0.35
    social_weight: float = 0.30
    governance_weight: float = 0.35
    confidence_threshold: float = 0.7
    max_ai_retries: int = 3

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Added to ignore extra environment variables
    }


class Config(BaseSettings):
    """Main configuration class"""
    # App settings
    app_name: str = "ESG Investment Research System"
    app_version: str = "2.0"
    debug: bool = Field(False, env="DEBUG")
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # This will ignore extra environment variables
    }

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize sub-configurations after main config is loaded
        self._database = None
        self._api = None
        self._redis = None
        self._scraping = None
        self._caching = None
        self._security = None
        self._esg = None
        # Load YAML config if it exists
        self._load_yaml_config()

    @property
    def database(self) -> DatabaseConfig:
        """Get database configuration"""
        if self._database is None:
            self._database = DatabaseConfig()
        return self._database

    @property
    def api(self) -> APIConfig:
        """Get API configuration"""
        if self._api is None:
            self._api = APIConfig()
        return self._api

    @property
    def redis(self) -> RedisConfig:
        """Get Redis configuration"""
        if self._redis is None:
            self._redis = RedisConfig()
        return self._redis

    @property
    def scraping(self) -> ScrapingConfig:
        """Get scraping configuration"""
        if self._scraping is None:
            self._scraping = ScrapingConfig()
        return self._scraping

    @property
    def caching(self) -> CachingConfig:
        """Get caching configuration"""
        if self._caching is None:
            self._caching = CachingConfig()
        return self._caching

    @property
    def security(self) -> SecurityConfig:
        """Get security configuration"""
        if self._security is None:
            self._security = SecurityConfig()
        return self._security

    @property
    def esg(self) -> ESGConfig:
        """Get ESG configuration"""
        if self._esg is None:
            self._esg = ESGConfig()
        return self._esg

    def _load_yaml_config(self):
        """Load additional configuration from YAML file"""
        yaml_path = Path("config.yaml")
        if yaml_path.exists():
            try:
                with open(yaml_path, "r") as file:
                    yaml_config = yaml.safe_load(file)
                    self._merge_yaml_config(yaml_config)
            except Exception as e:
                print(f"Warning: Could not load config.yaml: {e}")

    def _merge_yaml_config(self, yaml_config: Dict[str, Any]):
        """Merge YAML configuration with existing config"""
        # Only merge non-sensitive configuration from YAML
        if "app" in yaml_config:
            app_config = yaml_config["app"]
            if "debug" in app_config:
                self.debug = app_config["debug"]
            if "host" in app_config:
                self.host = app_config["host"]
            if "port" in app_config:
                self.port = app_config["port"]
            if "workers" in app_config:
                self.workers = app_config["workers"]

    @property
    def mongodb_url(self) -> str:
        """Get MongoDB connection URL"""
        return self.database.mongodb_connection_string

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"

    def get_data_sources(self) -> Dict[str, List[Dict]]:
        """Get configured data sources"""
        return {
            "financial": [
                {"name": "Financial Modeling Prep", "priority": 1, "enabled": True},
                {"name": "Yahoo Finance", "priority": 2, "enabled": True},
                {"name": "Alpha Vantage", "priority": 3, "enabled": True}
            ],
            "esg_ratings": [
                {
                    "name": "Sustainalytics",
                    "url": "https://www.sustainalytics.com",
                    "priority": 1,
                    "enabled": True,
                    "scraping": True
                },
                {
                    "name": "CDP",
                    "url": "https://www.cdp.net",
                    "priority": 2,
                    "enabled": True,
                    "scraping": True
                },
                {
                    "name": "MSCI ESG",
                    "url": "https://www.msci.com/our-solutions/esg-investing",
                    "priority": 3,
                    "enabled": True,
                    "scraping": True
                }
            ],
            "news_sentiment": [
                {"name": "NewsAPI", "enabled": True},
                {"name": "Reddit", "enabled": bool(self.api.reddit_client_id)}
            ]
        }

    def get_ai_prompt_template(self) -> str:
        """Get AI analysis prompt template"""
        return """
        Analyze the following ESG data for {company_name} ({ticker}) in the {industry} sector:
        
        Environmental Data: {environmental_data}
        Social Data: {social_data}
        Governance Data: {governance_data}
        Financial Context: {financial_context}
        Recent News: {news_sentiment}
        
        Provide a comprehensive analysis with:
        1. Environmental score (0-100) with detailed reasoning
        2. Social score (0-100) with detailed reasoning
        3. Governance score (0-100) with detailed reasoning
        4. Overall ESG score and investment recommendation
        5. Key risks and opportunities
        6. Industry benchmark comparison
        
        Format as JSON with scores and detailed explanations.
        Be objective and data-driven in your analysis.
        """

    def get_collection_names(self) -> Dict[str, str]:
        """Get MongoDB collection names"""
        return {
            "companies": "companies",
            "esg_scores": "esg_scores",
            "ai_analysis": "ai_analysis",
            "benchmarks": "benchmarks",
            "news_data": "news_data"
        }


# Global configuration instance
_settings = None


def get_settings() -> Config:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Config()
    return _settings


def load_config_from_file(file_path: str) -> Config:
    """Load configuration from specific file"""
    config = Config()
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            yaml_config = yaml.safe_load(file)
            config._merge_yaml_config(yaml_config)
    return config