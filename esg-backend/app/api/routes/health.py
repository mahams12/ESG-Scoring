# routes health.py
"""
Health check API endpoints
"""

import asyncio
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends
from loguru import logger

from app.config import get_settings
from app.database import get_database
from app.models.responses import HealthCheckResponse, ProcessingMetadata
from app.services.company_validator import get_company_validator
from app.services.data_collector import get_data_collector


router = APIRouter()


@router.get("/", response_model=HealthCheckResponse)
async def health_check():
    """
    Comprehensive health check for all system components
    """
    start_time = datetime.utcnow()
    
    try:
        # Check all services
        health_results = await check_all_services()
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Create metadata
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=list(health_results.keys()),
            cache_hit=False,
            total_api_calls=len(health_results)
        )
        
        # Determine overall health
        failed_services = [name for name, status in health_results.items() if not status]
        
        if failed_services:
            return HealthCheckResponse.unhealthy(failed_services)
        else:
            return HealthCheckResponse.healthy(health_results)
            
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheckResponse.unhealthy(["health_check_system"])


@router.get("/database", response_model=HealthCheckResponse)
async def database_health():
    """Check database connectivity and status"""
    start_time = datetime.utcnow()
    
    try:
        db = await get_database()
        is_healthy = await db.health_check()
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=["mongodb"],
            total_api_calls=1
        )
        
        if is_healthy:
            # Get database stats
            db_stats = await db.get_database_stats()
            
            return HealthCheckResponse(
                message="Database is healthy",
                data={
                    "status": "healthy",
                    "connection": "active",
                    "stats": db_stats
                },
                metadata=metadata
            )
        else:
            return HealthCheckResponse.unhealthy(["mongodb"])
            
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return HealthCheckResponse.unhealthy(["mongodb"])


@router.get("/apis", response_model=HealthCheckResponse)
async def apis_health():
    """Check external API connectivity"""
    start_time = datetime.utcnow()
    
    try:
        data_collector = get_data_collector()
        api_health = await data_collector.health_check()
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=list(api_health.keys()),
            total_api_calls=len(api_health)
        )
        
        failed_apis = [name for name, status in api_health.items() if not status]
        
        if failed_apis:
            return HealthCheckResponse(
                message=f"Some APIs are unavailable: {', '.join(failed_apis)}",
                data={
                    "api_status": api_health,
                    "failed_apis": failed_apis,
                    "healthy_apis": [name for name, status in api_health.items() if status]
                },
                metadata=metadata
            )
        else:
            return HealthCheckResponse(
                message="All APIs are healthy",
                data={
                    "api_status": api_health,
                    "all_apis_healthy": True
                },
                metadata=metadata
            )
            
    except Exception as e:
        logger.error(f"API health check failed: {str(e)}")
        return HealthCheckResponse.unhealthy(["external_apis"])


@router.get("/services", response_model=HealthCheckResponse)
async def services_health():
    """Check internal services status"""
    start_time = datetime.utcnow()
    
    try:
        services_status = {}
        
        # Check company validator
        try:
            validator = get_company_validator()
            # Test with a known ticker
            test_result = await validator.validate_company("AAPL", force_refresh=False)
            services_status["company_validator"] = test_result.exists
        except Exception as e:
            logger.warning(f"Company validator check failed: {str(e)}")
            services_status["company_validator"] = False
        
        # Check data collector
        try:
            collector = get_data_collector()
            # Test data collection
            test_data = await collector.get_data_freshness_score("AAPL")
            services_status["data_collector"] = True
        except Exception as e:
            logger.warning(f"Data collector check failed: {str(e)}")
            services_status["data_collector"] = False
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        metadata = ProcessingMetadata(
            processing_time_ms=processing_time,
            data_sources_used=list(services_status.keys()),
            total_api_calls=len(services_status)
        )
        
        failed_services = [name for name, status in services_status.items() if not status]
        
        if failed_services:
            return HealthCheckResponse(
                message=f"Some services are unavailable: {', '.join(failed_services)}",
                data={
                    "services_status": services_status,
                    "failed_services": failed_services
                },
                metadata=metadata
            )
        else:
            return HealthCheckResponse(
                message="All services are healthy",
                data={
                    "services_status": services_status,
                    "all_services_healthy": True
                },
                metadata=metadata
            )
            
    except Exception as e:
        logger.error(f"Services health check failed: {str(e)}")
        return HealthCheckResponse.unhealthy(["internal_services"])


@router.get("/detailed")
async def detailed_health_check():
    """
    Detailed health check with system information
    """
    start_time = datetime.utcnow()
    settings = get_settings()
    
    try:
        # Run all health checks
        db_health_task = database_health()
        api_health_task = apis_health()
        services_health_task = services_health()
        
        # Wait for all checks
        db_result, api_result, services_result = await asyncio.gather(
            db_health_task,
            api_health_task,
            services_health_task,
            return_exceptions=True
        )
        
        # Calculate overall status
        all_healthy = all([
            not isinstance(db_result, Exception) and db_result.data.get("status") == "healthy",
            not isinstance(api_result, Exception) and api_result.data.get("all_apis_healthy", False),
            not isinstance(services_result, Exception) and services_result.data.get("all_services_healthy", False)
        ])
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "overall_status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": processing_time,
            "system_info": {
                "version": settings.app_version,
                "environment": settings.environment,
                "debug_mode": settings.debug
            },
            "components": {
                "database": db_result.dict() if not isinstance(db_result, Exception) else {"error": str(db_result)},
                "external_apis": api_result.dict() if not isinstance(api_result, Exception) else {"error": str(api_result)},
                "internal_services": services_result.dict() if not isinstance(services_result, Exception) else {"error": str(services_result)}
            }
        }
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return {
            "overall_status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes-style readiness check
    Returns 200 if ready to serve traffic, 503 otherwise
    """
    try:
        # Quick checks for critical components
        db = await get_database()
        db_healthy = await db.health_check()
        
        if db_healthy:
            return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Service not ready")
            
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")


@router.get("/live")
async def liveness_check():
    """
    Kubernetes-style liveness check
    Returns 200 if application is alive
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "healthy"
    }


async def check_all_services() -> Dict[str, bool]:
    """Check all system services and return status"""
    services_status = {}
    
    # Database check
    try:
        db = await get_database()
        services_status["database"] = await db.health_check()
    except Exception:
        services_status["database"] = False
    
    # External APIs check
    try:
        data_collector = get_data_collector()
        api_health = await data_collector.health_check()
        services_status.update(api_health)
    except Exception:
        services_status["external_apis"] = False
    
    # Internal services check
    try:
        validator = get_company_validator()
        services_status["company_validator"] = True
    except Exception:
        services_status["company_validator"] = False
    
    return services_status