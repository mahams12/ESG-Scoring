"""
ESG Investment Research System - Main FastAPI Application
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
import uvicorn

from app.config import get_settings
from app.database import get_database, close_database
from app.api.routes import analysis, company, health

# Global variables for application state
app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting ESG Investment Research System...")
    
    try:
        # Initialize database
        db = await get_database()
        app_state["database"] = db
        logger.info("Database connection established")
        
        # Check database health
        is_healthy = await db.health_check()
        if not is_healthy:
            logger.warning("Database health check failed")
        
        # Initialize services
        try:
            from app.services.company_validator import get_company_validator
            from app.services.data_collector import get_data_collector
            
            app_state["company_validator"] = get_company_validator()
            app_state["data_collector"] = get_data_collector()
            logger.info("Services initialized successfully")
        except ImportError as e:
            logger.warning(f"Some services not available: {e}")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        # Don't raise - allow app to start even if some components fail
        yield
    
    finally:
        # Shutdown
        logger.info("Shutting down ESG Investment Research System...")
        
        try:
            await close_database()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")


# Create FastAPI application
def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    settings = get_settings()
    
    app = FastAPI(
        title="ESG Investment Research System",
        description="Real-time ESG analysis and investment research platform with AI-powered insights",
        version="2.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Add middleware
    setup_middleware(app, settings)
    
    # Add exception handlers
    setup_exception_handlers(app)
    
    # Include routers
    setup_routes(app)
    
    return app


def setup_middleware(app: FastAPI, settings):
    """Setup application middleware"""
    
    # CORS middleware - UPDATED for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000", 
            "http://localhost:3001",
            "http://127.0.0.1:3001",
            "http://localhost:5173",  # Vite default
            "http://127.0.0.1:5173"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware (for production)
    if getattr(settings, 'is_production', False):
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["esg-research-api.com", "*.esg-research-api.com"]
        )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = datetime.utcnow()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.info(f"Response: {response.status_code} - {process_time:.2f}ms")
        
        # Add processing time header
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        return response


def setup_exception_handlers(app: FastAPI):
    """Setup custom exception handlers"""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors"""
        logger.warning(f"Validation error: {exc}")
        
        # Extract first error for cleaner response
        first_error = exc.errors()[0] if exc.errors() else {}
        field = ".".join(str(loc) for loc in first_error.get("loc", []))
        message = first_error.get("msg", "Validation failed")
        
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "message": f"Validation error in {field}: {message}",
                "errors": exc.errors()
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions"""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error",
                "details": str(exc) if get_settings().debug else None
            }
        )


def setup_routes(app: FastAPI):
    """Setup application routes"""
    
    # Include API routers
    app.include_router(
        health.router,
        prefix="/api/v1/health",
        tags=["Health Check"]
    )
    
    app.include_router(
        company.router,
        prefix="/api/v1/company",
        tags=["Company Validation"]
    )
    
    app.include_router(
        analysis.router,
        prefix="/api/v1/analysis",
        tags=["ESG Analysis"]
    )
    
    # Root endpoint
    @app.get("/", include_in_schema=False)
    async def root():
        """Root endpoint"""
        return {
            "message": "ESG Investment Research System API",
            "version": "2.0",
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "docs_url": "/docs",
            "health_check": "/api/v1/health"
        }
    
    # API info endpoint
    @app.get("/api/v1/info")
    async def api_info():
        """Get API information"""
        settings = get_settings()
        
        return {
            "api_name": getattr(settings, 'app_name', 'ESG Investment Research System'),
            "version": getattr(settings, 'app_version', '2.0'),
            "environment": getattr(settings, 'environment', 'development'),
            "features": {
                "real_time_data": True,
                "ai_analysis": True,
                "company_validation": True,
                "esg_scoring": True,
                "benchmark_comparison": True,
                "news_analysis": True,
                "bulk_analysis": True,
                "report_download": True
            },
            "data_sources": {
                "financial": ["Financial Modeling Prep", "Yahoo Finance", "Alpha Vantage"],
                "esg": ["Sustainalytics", "CDP", "MSCI ESG", "ESG Enterprise"],
                "news": ["NewsAPI", "Reddit"],
                "regulatory": ["EPA", "OSHA"]
            },
            "rate_limits": {
                "requests_per_minute": 100,
                "requests_per_hour": 1000
            },
            "support": {
                "documentation": "/docs",
                "health_check": "/api/v1/health",
                "contact": "support@esg-research.com"
            }
        }


# Create the application instance
app = create_application()


# Development server runner
def run_development_server():
    """Run development server"""
    settings = get_settings()
    
    # Log server details
    host = getattr(settings, 'host', '127.0.0.1')
    port = getattr(settings, 'port', 8000)
    debug = getattr(settings, 'debug', True)
    
    logger.info(f"🚀 Starting server on http://{host}:{port}")
    logger.info(f"📚 API Documentation: http://localhost:{port}/docs")
    logger.info(f"🔍 Alternative Docs: http://localhost:{port}/redoc")
    logger.info(f"❤️  Health Check: http://localhost:{port}/api/v1/health")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning",
        access_log=debug
    )


if __name__ == "__main__":
    # Configure logging
    logger.add(
        "logs/esg_system_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        compression="gz",
        level="INFO"
    )
    
    logger.info("Starting ESG Investment Research System in development mode")
    run_development_server()