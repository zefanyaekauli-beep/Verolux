"""
Backpressure Handling System
Manages queue overflow and graceful degradation under load
"""
import time
import asyncio
from typing import Optional, Callable, Any
from collections import deque
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DropPolicy(Enum):
    """Queue overflow policies"""
    DROP_OLDEST = "drop_oldest"  # Drop oldest items (FIFO eviction)
    DROP_LATEST = "drop_latest"  # Drop newest items (reject new)
    DROP_PRIORITY = "drop_priority"  # Drop lowest priority first
    BLOCK = "block"  # Block until space available


class SystemMode(Enum):
    """System operation modes"""
    NORMAL = "normal"
    DEGRADED = "degraded"
    OVERLOAD = "overload"
    EMERGENCY = "emergency"


class BoundedQueue:
    """
    Bounded queue with configurable drop policy
    
    Features:
    - Max size enforcement
    - Multiple drop policies
    - Statistics tracking
    - Backpressure signals
    """
    
    def __init__(self,
                 name: str,
                 maxsize: int,
                 drop_policy: DropPolicy = DropPolicy.DROP_OLDEST):
        """
        Initialize bounded queue
        
        Args:
            name: Queue name
            maxsize: Maximum queue size
            drop_policy: What to do when full
        """
        self.name = name
        self.maxsize = maxsize
        self.drop_policy = drop_policy
        
        self._queue = deque(maxlen=maxsize if drop_policy == DropPolicy.DROP_OLDEST else None)
        self._lock = asyncio.Lock()
        
        # Statistics
        self.stats = {
            "enqueued": 0,
            "dequeued": 0,
            "dropped": 0,
            "rejected": 0
        }
    
    async def put(self, item: Any, priority: int = 0, block: bool = True) -> bool:
        """
        Put item in queue
        
        Args:
            item: Item to enqueue
            priority: Item priority (higher = more important)
            block: Block if queue full (only for BLOCK policy)
            
        Returns:
            True if item was added, False if dropped/rejected
        """
        async with self._lock:
            # Check if queue is full
            if len(self._queue) >= self.maxsize:
                if self.drop_policy == DropPolicy.DROP_OLDEST:
                    # Automatically drops oldest when deque is full
                    self.stats["dropped"] += 1
                    logger.warning(f"Queue {self.name}: Dropping oldest item (queue full)")
                
                elif self.drop_policy == DropPolicy.DROP_LATEST:
                    # Reject new item
                    self.stats["rejected"] += 1
                    logger.warning(f"Queue {self.name}: Rejecting new item (queue full)")
                    return False
                
                elif self.drop_policy == DropPolicy.BLOCK:
                    if block:
                        # Wait for space (with timeout)
                        timeout = 5.0
                        start = time.time()
                        
                        while len(self._queue) >= self.maxsize:
                            if time.time() - start > timeout:
                                self.stats["rejected"] += 1
                                return False
                            
                            await asyncio.sleep(0.1)
                    else:
                        self.stats["rejected"] += 1
                        return False
            
            # Add item to queue
            self._queue.append((priority, item))
            self.stats["enqueued"] += 1
            
            return True
    
    async def get(self, timeout: Optional[float] = None) -> Optional[Any]:
        """
        Get item from queue
        
        Args:
            timeout: Optional timeout in seconds
            
        Returns:
            Item or None if timeout
        """
        start = time.time() if timeout else None
        
        while True:
            async with self._lock:
                if self._queue:
                    priority, item = self._queue.popleft()
                    self.stats["dequeued"] += 1
                    return item
            
            # Check timeout
            if timeout and (time.time() - start) > timeout:
                return None
            
            await asyncio.sleep(0.01)
    
    def size(self) -> int:
        """Get current queue size"""
        return len(self._queue)
    
    def is_full(self) -> bool:
        """Check if queue is full"""
        return len(self._queue) >= self.maxsize
    
    def utilization(self) -> float:
        """Get queue utilization (0-1)"""
        return len(self._queue) / self.maxsize if self.maxsize > 0 else 0
    
    def get_stats(self) -> dict:
        """Get queue statistics"""
        return {
            "name": self.name,
            "size": len(self._queue),
            "maxsize": self.maxsize,
            "utilization_percent": round(self.utilization() * 100, 2),
            "drop_policy": self.drop_policy.value,
            **self.stats
        }


class BackpressureManager:
    """
    Manages system backpressure and graceful degradation
    
    Features:
    - Queue monitoring
    - Automatic mode switching
    - Graceful degradation
    - Load shedding
    """
    
    def __init__(self):
        self.queues: Dict[str, BoundedQueue] = {}
        self.current_mode = SystemMode.NORMAL
        
        # Thresholds for mode switching
        self.thresholds = {
            "degraded_queue_utilization": 0.70,  # 70%
            "overload_queue_utilization": 0.90,  # 90%
            "emergency_queue_utilization": 0.95  # 95%
        }
        
        # Statistics
        self.mode_changes = []
        
        logger.info("Backpressure manager initialized")
    
    def register_queue(self, queue: BoundedQueue):
        """Register a queue for monitoring"""
        self.queues[queue.name] = queue
        logger.info(f"Registered queue: {queue.name}")
    
    async def check_backpressure(self) -> SystemMode:
        """
        Check overall system backpressure
        
        Returns:
            Current system mode
        """
        if not self.queues:
            return SystemMode.NORMAL
        
        # Calculate average queue utilization
        utilizations = [q.utilization() for q in self.queues.values()]
        avg_utilization = sum(utilizations) / len(utilizations)
        
        # Determine mode
        old_mode = self.current_mode
        
        if avg_utilization >= self.thresholds["emergency_queue_utilization"]:
            self.current_mode = SystemMode.EMERGENCY
        elif avg_utilization >= self.thresholds["overload_queue_utilization"]:
            self.current_mode = SystemMode.OVERLOAD
        elif avg_utilization >= self.thresholds["degraded_queue_utilization"]:
            self.current_mode = SystemMode.DEGRADED
        else:
            self.current_mode = SystemMode.NORMAL
        
        # Log mode changes
        if old_mode != self.current_mode:
            self.mode_changes.append({
                "timestamp": time.time(),
                "from": old_mode.value,
                "to": self.current_mode.value,
                "avg_utilization": round(avg_utilization * 100, 2)
            })
            
            logger.warning(
                f"System mode changed: {old_mode.value} → {self.current_mode.value} "
                f"(queue utilization: {avg_utilization*100:.1f}%)"
            )
        
        return self.current_mode
    
    def should_shed_load(self) -> bool:
        """Check if system should shed load"""
        return self.current_mode in [SystemMode.OVERLOAD, SystemMode.EMERGENCY]
    
    def get_degradation_actions(self) -> List[str]:
        """Get recommended degradation actions for current mode"""
        if self.current_mode == SystemMode.EMERGENCY:
            return [
                "Drop all low-priority tasks",
                "Disable preview streams",
                "Reduce inference batch size",
                "Skip non-critical processing"
            ]
        elif self.current_mode == SystemMode.OVERLOAD:
            return [
                "Batch low-priority alerts",
                "Reduce analytics frequency",
                "Skip some frame processing"
            ]
        elif self.current_mode == SystemMode.DEGRADED:
            return [
                "Increase alert batching",
                "Defer non-urgent reports"
            ]
        else:
            return []
    
    def get_backpressure_status(self) -> dict:
        """Get backpressure status summary"""
        return {
            "current_mode": self.current_mode.value,
            "queues": {
                name: queue.get_stats()
                for name, queue in self.queues.items()
            },
            "degradation_actions": self.get_degradation_actions(),
            "recent_mode_changes": self.mode_changes[-10:]
        }


# Global instance
backpressure_manager = BackpressureManager()



















