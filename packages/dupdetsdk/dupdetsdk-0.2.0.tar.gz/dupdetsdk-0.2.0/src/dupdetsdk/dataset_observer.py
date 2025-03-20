import time
import asyncio
import threading
import random
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class DatabaseObserver:
    """
    Monitors and maintains a ChromaDB collection by periodically removing expired entries.
    Includes retry logic to handle database locking issues in multi-process environments.
    """
    def __init__(
        self, 
        logger, 
        verbose: bool, 
        db_collection, 
        ttl: int, 
        delta_quantity_trigger: int,
        auto_maintenance_interval: Optional[int] = None,
        max_retries: int = 5
    ):
        self.db_collection = db_collection
        self.logger = logger
        self.ttl = ttl
        self.delta_quantity_trigger = delta_quantity_trigger
        self.verbose = verbose
        self.max_retries = max_retries
        
        # Initialize with a safe count operation that includes retries
        self.previous_count = self._safe_count()
        self.delta_count = 0
        self.lock = threading.Lock()
        self.last_maintenance_time = time.time()
        
        # Statistics
        self.total_cleanups = 0
        self.total_deleted = 0
        self.total_retries = 0
        
        # Auto-maintenance
        self.auto_maintenance_interval = auto_maintenance_interval
        self.running = False
        
        # Start auto-maintenance if interval is specified
        if auto_maintenance_interval:
            self.start_auto_maintenance()

    def _safe_count(self) -> int:
        """Count records with retry logic"""
        for attempt in range(1, self.max_retries + 1):
            try:
                count = self.db_collection.count()
                return count
            except Exception as e:
                if attempt == self.max_retries:
                    if self.logger:
                        self.logger.error(f"<DBObserver> Failed to count records after {attempt} attempts: {e}")
                    return 0
                
                # Add jitter to prevent thundering herd problem
                wait_time = min(2 ** attempt + random.uniform(0, 1), 30)
                if self.logger and self.verbose:
                    self.logger.warning(f"<DBObserver> Database locked, retrying in {wait_time:.2f}s (attempt {attempt}/{self.max_retries})")
                time.sleep(wait_time)
                
                # Track retries for monitoring
                self.total_retries += 1

    async def _count_async(self) -> int:
        """Count records asynchronously with retry logic"""
        return await asyncio.to_thread(self._safe_count)

    async def check_and_maintain_db_async(self) -> bool:
        """Check database size and maintain if necessary"""
        try:
            count = await self._count_async()
            if count is None:  # Error occurred and retries failed
                return False
                
            if self.logger and self.verbose: 
                self.logger.info(f"<DBObserver> DB record count: {count}")
            
            with self.lock:
                delta = count - self.previous_count
                self.delta_count += delta
                
                # Perform maintenance if threshold reached or too much time has passed
                current_time = time.time()
                time_since_last = current_time - self.last_maintenance_time
                
                should_maintain = (
                    self.delta_count >= self.delta_quantity_trigger or 
                    (self.auto_maintenance_interval and time_since_last >= self.auto_maintenance_interval)
                )
                
                if should_maintain:
                    if self.logger:
                        self.logger.info(f"<DBObserver> Starting expiration cleanup (delta: {self.delta_count}, time since last: {time_since_last:.1f}s)")
                    
                    # Execute maintenance with retries
                    deleted_count = await self.rm_expired_entries_async()
                    
                    # Get updated count
                    updated_count = await self._count_async()
                    
                    if self.logger: 
                        self.logger.info(f"<DBObserver> DB record count after cleanup: {updated_count}, records removed: {deleted_count}")
                    
                    # Update stats
                    if deleted_count > 0:
                        self.total_cleanups += 1
                        self.total_deleted += deleted_count
                    
                    # Reset tracking
                    self.delta_count = 0
                    self.last_maintenance_time = current_time
                    count = updated_count if updated_count is not None else count
                
                self.previous_count = count
                return True
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"<DBObserver> Error during maintenance: {e}", exc_info=True)
            return False

    async def rm_expired_entries_async(self) -> int:
        """Remove expired entries with retry logic"""
        for attempt in range(1, self.max_retries + 1):
            try:
                current_time = int(time.time())
                # Get expired items with retries
                expired_items = await self._get_expired_items_async(current_time)
                expired_ids = expired_items.get("ids", [])
                
                if not expired_ids:
                    if self.logger and self.verbose:
                        self.logger.info("<DBObserver> No expired records to delete.")
                    return 0
                
                # Try to delete with exponential backoff
                await asyncio.to_thread(self._safe_delete, expired_ids)
                
                if self.logger:
                    self.logger.info(f"<DBObserver> Deleted {len(expired_ids)} expired records.")
                return len(expired_ids)
                
            except Exception as e:
                if attempt == self.max_retries:
                    if self.logger:
                        self.logger.error(f"<DBObserver> Failed to remove expired entries after {attempt} attempts: {e}")
                    return 0
                
                wait_time = min(2 ** attempt + random.uniform(0, 1), 30)
                if self.logger and self.verbose:
                    self.logger.warning(f"<DBObserver> Database locked during cleanup, retrying in {wait_time:.2f}s (attempt {attempt}/{self.max_retries})")
                await asyncio.sleep(wait_time)
                
                self.total_retries += 1
        
        return 0  # Default return if all attempts fail

    async def _get_expired_items_async(self, current_time: int) -> Dict[str, Any]:
        """Get expired items with retry logic"""
        return await asyncio.to_thread(self._safe_get_expired_items, current_time)

    def _safe_get_expired_items(self, current_time: int) -> Dict[str, Any]:
        """Get expired items with retry logic"""
        for attempt in range(1, self.max_retries + 1):
            try:
                result = self.db_collection.get(
                    where={"timestamp": {"$lt": current_time - self.ttl}},
                    include=["metadatas"]
                )
                return result
            except Exception as e:
                if attempt == self.max_retries:
                    if self.logger:
                        self.logger.error(f"<DBObserver> Failed to get expired items after {attempt} attempts: {e}")
                    return {"ids": []}
                
                wait_time = min(2 ** attempt + random.uniform(0, 1), 30)
                time.sleep(wait_time)
                self.total_retries += 1
                
        return {"ids": []}  # Default if all attempts fail

    def _safe_delete(self, ids):
        """Delete with retry logic"""
        for attempt in range(1, self.max_retries + 1):
            try:
                self.db_collection.delete(ids)
                return True
            except Exception as e:
                if attempt == self.max_retries:
                    if self.logger:
                        self.logger.error(f"<DBObserver> Failed to delete {len(ids)} items after {attempt} attempts: {e}")
                    return False
                
                wait_time = min(2 ** attempt + random.uniform(0, 1), 30)
                time.sleep(wait_time)
                self.total_retries += 1
                
        return False

    def check_and_maintain_db(self) -> bool:
        """Synchronous wrapper for check_and_maintain_db_async"""
        return asyncio.run(self.check_and_maintain_db_async())
        
    async def _periodic_maintenance(self) -> None:
        """Background task for periodic maintenance"""
        while self.running:
            try:
                await self.check_and_maintain_db_async()
                await asyncio.sleep(self.auto_maintenance_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.logger:
                    self.logger.error(f"<DBObserver> Error in background maintenance: {e}", exc_info=True)
                await asyncio.sleep(10)  # If error, wait a bit before retrying
                
    def start_auto_maintenance(self) -> None:
        """Start the background maintenance task"""
        if self.auto_maintenance_interval and not self.running:
            self.running = True
            asyncio.create_task(self._periodic_maintenance())
            if self.logger and self.verbose:
                self.logger.info(f"<DBObserver> Started automatic maintenance every {self.auto_maintenance_interval} seconds")
                
    def stop_auto_maintenance(self) -> None:
        """Stop the background maintenance task"""
        self.running = False
        if self.logger and self.verbose:
            self.logger.info("<DBObserver> Stopped automatic maintenance")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get observer statistics"""
        with self.lock:
            return {
                "current_count": self.previous_count,
                "delta_count": self.delta_count,
                "total_cleanups": self.total_cleanups,
                "total_deleted": self.total_deleted,
                "total_retries": self.total_retries,
                "last_maintenance_time": self.last_maintenance_time
            }