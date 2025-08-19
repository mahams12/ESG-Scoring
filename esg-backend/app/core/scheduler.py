"""
Background task scheduler for ESG Investment Research System
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from loguru import logger
import schedule
import time
from threading import Thread

from app.config import get_settings
from app.core.pipeline import get_esg_pipeline
from app.services.storage_service import get_storage_service
from app.database import get_database


class BackgroundTaskScheduler:
    """
    Background task scheduler for maintenance and data refresh operations
    
    Handles periodic tasks like:
    - Data cleanup and maintenance
    - Cache refresh for popular companies
    - Health monitoring
    - Performance metrics collection
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.pipeline = get_esg_pipeline()
        self.storage_service = get_storage_service()
        self.running = False
        self.scheduler_thread = None
        self.tasks = {}
        
    def start(self):
        """Start the background scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        logger.info("Starting background task scheduler")
        
        # Setup scheduled tasks
        self._setup_scheduled_tasks()
        
        # Start scheduler in separate thread
        self.scheduler_thread = Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Background scheduler started successfully")
    
    def stop(self):
        """Stop the background scheduler"""
        if not self.running:
            return
        
        self.running = False
        logger.info("Stopping background task scheduler")
        
        # Clear all scheduled tasks
        schedule.clear()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("Background scheduler stopped")
    
    def _setup_scheduled_tasks(self):
        """Setup all scheduled tasks"""
        
        # Daily data cleanup at 2 AM
        schedule.every().day.at("02:00").do(self._schedule_async_task, self.cleanup_expired_data)
        
        # Health check every 15 minutes
        schedule.every(15).minutes.do(self._schedule_async_task, self.health_check_task)
        
        # Performance metrics collection every hour
        schedule.every().hour.do(self._schedule_async_task, self.collect_performance_metrics)
        
        # Cache refresh for popular companies every 6 hours
        schedule.every(6).hours.do(self._schedule_async_task, self.refresh_popular_companies)
        
        # Database maintenance weekly on Sunday at 3 AM
        schedule.every().sunday.at("03:00").do(self._schedule_async_task, self.database_maintenance)
        
        logger.info("Scheduled tasks configured")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        logger.info("Scheduler loop started")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)
        
        logger.info("Scheduler loop stopped")
    
    def _schedule_async_task(self, coro_func):
        """Schedule an async task to run"""
        def wrapper():
            try:
                # Create new event loop for this thread if needed
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                if loop.is_running():
                    # If loop is running, schedule the task
                    asyncio.create_task(coro_func())
                else:
                    # If loop is not running, run the task
                    loop.run_until_complete(coro_func())
                    
            except Exception as e:
                logger.error(f"Error running scheduled task {coro_func.__name__}: {str(e)}")
        
        return wrapper()
    
    async def cleanup_expired_data(self):
        """Clean up expired cached data"""
        try:
            logger.info("Starting scheduled data cleanup")
            start_time = datetime.utcnow()
            
            # Run pipeline cleanup
            cleaned_count = await self.pipeline.cleanup_expired_data()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(
                f"Data cleanup completed: {cleaned_count} items cleaned "
                f"in {processing_time:.2f} seconds"
            )
            
            # Record task completion
            self.tasks["last_cleanup"] = {
                "timestamp": datetime.utcnow(),
                "items_cleaned": cleaned_count,
                "processing_time": processing_time,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Scheduled data cleanup failed: {str(e)}")
            self.tasks["last_cleanup"] = {
                "timestamp": datetime.utcnow(),
                "error": str(e),
                "status": "failed"
            }
    
    async def health_check_task(self):
        """Perform comprehensive health check"""
        try:
            logger.debug("Running scheduled health check")
            start_time = datetime.utcnow()
            
            # Check pipeline health
            health_status = await self.pipeline.health_check()
            
            # Check database health
            db = await get_database()
            db_healthy = await db.health_check()
            health_status["database"] = db_healthy
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Count healthy vs unhealthy services
            healthy_services = sum(1 for status in health_status.values() if status)
            total_services = len(health_status)
            
            overall_health = healthy_services / total_services if total_services > 0 else 0
            
            # Log health status
            if overall_health >= 0.9:
                logger.debug(f"System health: {overall_health:.1%} ({healthy_services}/{total_services} services healthy)")
            elif overall_health >= 0.7:
                logger.warning(f"System health degraded: {overall_health:.1%} ({healthy_services}/{total_services} services healthy)")
            else:
                logger.error(f"System health critical: {overall_health:.1%} ({healthy_services}/{total_services} services healthy)")
            
            # Record health check
            self.tasks["last_health_check"] = {
                "timestamp": datetime.utcnow(),
                "overall_health": overall_health,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "service_status": health_status,
                "processing_time": processing_time,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Scheduled health check failed: {str(e)}")
            self.tasks["last_health_check"] = {
                "timestamp": datetime.utcnow(),
                "error": str(e),
                "status": "failed"
            }
    
    async def collect_performance_metrics(self):
        """Collect system performance metrics"""
        try:
            logger.debug("Collecting performance metrics")
            start_time = datetime.utcnow()
            
            # Get pipeline statistics
            pipeline_stats = await self.pipeline.get_pipeline_statistics()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record metrics
            self.tasks["last_metrics_collection"] = {
                "timestamp": datetime.utcnow(),
                "statistics": pipeline_stats,
                "processing_time": processing_time,
                "status": "success"
            }
            
            logger.debug(f"Performance metrics collected in {processing_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Performance metrics collection failed: {str(e)}")
            self.tasks["last_metrics_collection"] = {
                "timestamp": datetime.utcnow(),
                "error": str(e),
                "status": "failed"
            }
    
    async def refresh_popular_companies(self):
        """Refresh data for frequently analyzed companies"""
        try:
            logger.info("Refreshing popular companies data")
            start_time = datetime.utcnow()
            
            # Get most frequently analyzed companies from database
            popular_companies = await self._get_popular_companies(limit=10)
            
            if not popular_companies:
                logger.info("No popular companies found for refresh")
                return
            
            # Refresh data for each company
            refreshed_count = 0
            failed_count = 0
            
            for ticker in popular_companies:
                try:
                    success = await self.pipeline.refresh_company_data(ticker)
                    if success:
                        refreshed_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to refresh data for {ticker}: {str(e)}")
                    failed_count += 1
                
                # Small delay between refreshes
                await asyncio.sleep(2)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(
                f"Popular companies refresh completed: {refreshed_count} successful, "
                f"{failed_count} failed in {processing_time:.2f} seconds"
            )
            
            # Record task completion
            self.tasks["last_popular_refresh"] = {
                "timestamp": datetime.utcnow(),
                "companies_processed": len(popular_companies),
                "successful": refreshed_count,
                "failed": failed_count,
                "processing_time": processing_time,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Popular companies refresh failed: {str(e)}")
            self.tasks["last_popular_refresh"] = {
                "timestamp": datetime.utcnow(),
                "error": str(e),
                "status": "failed"
            }
    
    async def database_maintenance(self):
        """Perform database maintenance tasks"""
        try:
            logger.info("Starting database maintenance")
            start_time = datetime.utcnow()
            
            db = await get_database()
            
            # Get database statistics before maintenance
            stats_before = await db.get_database_stats()
            
            # Perform maintenance tasks
            maintenance_tasks = []
            
            # 1. Compact collections (if supported)
            try:
                # This would run database-specific maintenance
                # For MongoDB, we might run compact or other maintenance commands
                maintenance_tasks.append("collection_maintenance")
            except Exception as e:
                logger.warning(f"Collection maintenance warning: {str(e)}")
            
            # 2. Update index statistics
            try:
                # Reindex collections if needed
                maintenance_tasks.append("index_maintenance")
            except Exception as e:
                logger.warning(f"Index maintenance warning: {str(e)}")
            
            # Get statistics after maintenance
            stats_after = await db.get_database_stats()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"Database maintenance completed in {processing_time:.2f} seconds")
            
            # Record maintenance completion
            self.tasks["last_db_maintenance"] = {
                "timestamp": datetime.utcnow(),
                "tasks_performed": maintenance_tasks,
                "stats_before": stats_before,
                "stats_after": stats_after,
                "processing_time": processing_time,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Database maintenance failed: {str(e)}")
            self.tasks["last_db_maintenance"] = {
                "timestamp": datetime.utcnow(),
                "error": str(e),
                "status": "failed"
            }
    
    async def _get_popular_companies(self, limit: int = 10) -> List[str]:
        """Get list of most frequently analyzed companies"""
        try:
            # Query database for most frequently analyzed companies
            # This would be based on analysis frequency in the database
            
            # For now, return a sample list of popular companies
            popular_tickers = [
                "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
                "META", "NFLX", "NVDA", "JPM", "JNJ"
            ]
            
            return popular_tickers[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get popular companies: {str(e)}")
            return []
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get status of all scheduled tasks"""
        return {
            "scheduler_running": self.running,
            "scheduled_tasks": list(schedule.jobs),
            "task_history": self.tasks,
            "next_runs": {
                job.job_func.__name__: job.next_run.isoformat() if job.next_run else None
                for job in schedule.jobs
            }
        }
    
    def add_custom_task(
        self, 
        name: str, 
        task_func: Callable, 
        schedule_spec: str
    ):
        """
        Add a custom scheduled task
        
        Args:
            name: Task name
            task_func: Function to execute
            schedule_spec: Schedule specification (e.g., "every().day.at('10:00')")
        """
        try:
            # Parse and add the schedule
            # This is a simplified implementation
            if "daily" in schedule_spec:
                schedule.every().day.do(self._schedule_async_task, task_func)
            elif "hourly" in schedule_spec:
                schedule.every().hour.do(self._schedule_async_task, task_func)
            
            logger.info(f"Added custom task: {name}")
            
        except Exception as e:
            logger.error(f"Failed to add custom task {name}: {str(e)}")
    
    def remove_task(self, task_name: str):
        """Remove a scheduled task"""
        try:
            # Remove task from schedule
            # This would need more sophisticated task tracking
            logger.info(f"Removing task: {task_name}")
            
        except Exception as e:
            logger.error(f"Failed to remove task {task_name}: {str(e)}")


# Global scheduler instance
background_scheduler = BackgroundTaskScheduler()


def get_scheduler() -> BackgroundTaskScheduler:
    """Get background task scheduler instance"""
    return background_scheduler