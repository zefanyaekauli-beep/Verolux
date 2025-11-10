"""
Event Deduplication System
Ensures exactly-once event delivery with Redis-backed idempotency
"""
import hashlib
import time
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available, event deduplication will use in-memory fallback")

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event types for deduplication"""
    CHECK_COMPLETED = "check_completed"
    PERSON_ENTERED_GA = "person_entered_ga"
    PERSON_EXITED_GA = "person_exited_ga"
    GUARD_ANCHORED = "guard_anchored"
    GUARD_LEFT_ANCHOR = "guard_left_anchor"
    CONTACT_STARTED = "contact_started"
    CONTACT_ENDED = "contact_ended"
    POSE_DETECTED = "pose_detected"
    ANOMALY_DETECTED = "anomaly_detected"
    CAMERA_OFFLINE = "camera_offline"
    CAMERA_ONLINE = "camera_online"


@dataclass
class EventMetadata:
    """Event metadata for tracking"""
    event_id: str
    event_type: str
    camera_id: str
    track_id: Optional[int]
    timestamp: float
    data: Dict[str, Any]
    idempotency_key: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class EventDeduplicator:
    """
    Ensure exactly-once event delivery
    
    Uses Redis for distributed deduplication across multiple workers
    Falls back to in-memory dict for local-only deployments
    """
    
    def __init__(self, 
                 redis_url: Optional[str] = None,
                 redis_client: Optional[redis.Redis] = None,
                 cooldown_seconds: int = 60,
                 time_bucket_seconds: int = 60):
        """
        Initialize event deduplicator
        
        Args:
            redis_url: Redis connection URL
            redis_client: Existing Redis client
            cooldown_seconds: Event suppression window
            time_bucket_seconds: Time bucketing for idempotency keys
        """
        self.cooldown = cooldown_seconds
        self.time_bucket = time_bucket_seconds
        
        # Initialize Redis or fallback
        if REDIS_AVAILABLE and (redis_url or redis_client):
            if redis_client:
                self.redis = redis_client
            else:
                self.redis = redis.from_url(redis_url)
            self.use_redis = True
            logger.info("Event deduplicator using Redis backend")
        else:
            self.redis = None
            self.use_redis = False
            self._in_memory_cache: Dict[str, float] = {}
            logger.warning("Event deduplicator using in-memory fallback (not distributed)")
        
        # Statistics
        self.stats = {
            "emitted": 0,
            "suppressed": 0,
            "errors": 0
        }
    
    def generate_idempotency_key(self,
                                 camera_id: str,
                                 event_type: str,
                                 track_id: Optional[int] = None,
                                 custom_data: Optional[Dict] = None) -> str:
        """
        Generate idempotent event key
        
        Creates a unique key based on:
        - Camera ID
        - Event type
        - Track ID (if applicable)
        - Time bucket (rounded timestamp)
        - Custom data hash (optional)
        
        Args:
            camera_id: Camera identifier
            event_type: Type of event
            track_id: Optional track ID
            custom_data: Optional additional data for uniqueness
            
        Returns:
            Unique idempotency key
        """
        # Round timestamp to bucket
        timestamp = int(time.time())
        bucket = timestamp - (timestamp % self.time_bucket)
        
        # Build key components
        key_parts = [
            camera_id,
            event_type,
            str(track_id) if track_id is not None else "no_track",
            str(bucket)
        ]
        
        # Add custom data hash if provided
        if custom_data:
            data_str = json.dumps(custom_data, sort_keys=True)
            data_hash = hashlib.md5(data_str.encode()).hexdigest()[:8]
            key_parts.append(data_hash)
        
        # Create hash of all parts
        key_string = ":".join(key_parts)
        event_hash = hashlib.md5(key_string.encode()).hexdigest()[:12]
        
        return f"event:{event_hash}"
    
    def should_emit_event(self,
                         camera_id: str,
                         event_type: str,
                         track_id: Optional[int] = None,
                         custom_data: Optional[Dict] = None) -> tuple[bool, str]:
        """
        Check if event should be emitted (deduplication check)
        
        Args:
            camera_id: Camera identifier
            event_type: Type of event
            track_id: Optional track ID
            custom_data: Optional additional data
            
        Returns:
            (should_emit, idempotency_key) tuple
        """
        idempotency_key = self.generate_idempotency_key(
            camera_id, event_type, track_id, custom_data
        )
        
        try:
            if self.use_redis:
                # Try to set key with NX (only if not exists)
                was_set = self.redis.set(
                    idempotency_key,
                    "1",
                    ex=self.cooldown,  # Expire after cooldown
                    nx=True  # Only set if doesn't exist
                )
                should_emit = bool(was_set)
            else:
                # In-memory fallback
                now = time.time()
                
                # Clean expired keys
                self._clean_expired_keys(now)
                
                # Check if key exists
                if idempotency_key in self._in_memory_cache:
                    should_emit = False
                else:
                    self._in_memory_cache[idempotency_key] = now + self.cooldown
                    should_emit = True
            
            if should_emit:
                self.stats["emitted"] += 1
            else:
                self.stats["suppressed"] += 1
            
            return should_emit, idempotency_key
            
        except Exception as e:
            logger.error(f"Event deduplication error: {e}")
            self.stats["errors"] += 1
            # On error, allow event (fail-open)
            return True, idempotency_key
    
    def _clean_expired_keys(self, now: float):
        """Clean expired keys from in-memory cache"""
        expired_keys = [
            key for key, expiry in self._in_memory_cache.items()
            if expiry < now
        ]
        for key in expired_keys:
            del self._in_memory_cache[key]
    
    def emit_event(self,
                  camera_id: str,
                  event_type: str,
                  event_data: Dict[str, Any],
                  track_id: Optional[int] = None,
                  custom_dedup_data: Optional[Dict] = None) -> Optional[EventMetadata]:
        """
        Emit event with automatic deduplication
        
        Args:
            camera_id: Camera identifier
            event_type: Type of event
            event_data: Event payload
            track_id: Optional track ID
            custom_dedup_data: Optional data for deduplication logic
            
        Returns:
            EventMetadata if event was emitted, None if suppressed
        """
        should_emit, idempotency_key = self.should_emit_event(
            camera_id, event_type, track_id, custom_dedup_data
        )
        
        if not should_emit:
            logger.debug(
                f"Event {event_type} for camera {camera_id} "
                f"track {track_id} suppressed (duplicate)"
            )
            return None
        
        # Generate event ID
        timestamp_ms = int(time.time() * 1000)
        event_id = f"{camera_id}_{track_id or 'notk'}_{timestamp_ms}"
        
        # Create event metadata
        event_metadata = EventMetadata(
            event_id=event_id,
            event_type=event_type,
            camera_id=camera_id,
            track_id=track_id,
            timestamp=time.time(),
            data=event_data,
            idempotency_key=idempotency_key
        )
        
        logger.info(f"Event emitted: {event_id} ({event_type})")
        
        return event_metadata
    
    def force_clear_key(self, idempotency_key: str):
        """Force clear an idempotency key (for testing)"""
        if self.use_redis:
            self.redis.delete(idempotency_key)
        else:
            if idempotency_key in self._in_memory_cache:
                del self._in_memory_cache[idempotency_key]
    
    def get_stats(self) -> dict:
        """Get deduplication statistics"""
        total = self.stats["emitted"] + self.stats["suppressed"]
        suppression_rate = (self.stats["suppressed"] / total * 100) if total > 0 else 0
        
        return {
            "emitted": self.stats["emitted"],
            "suppressed": self.stats["suppressed"],
            "errors": self.stats["errors"],
            "total_events": total,
            "suppression_rate_percent": round(suppression_rate, 2),
            "backend": "redis" if self.use_redis else "in_memory"
        }
    
    def reset_stats(self):
        """Reset statistics (for testing)"""
        self.stats = {
            "emitted": 0,
            "suppressed": 0,
            "errors": 0
        }


class EventBatcher:
    """Batch events to reduce database/queue load"""
    
    def __init__(self, 
                 batch_size: int = 100,
                 batch_timeout: float = 5.0):
        """
        Initialize event batcher
        
        Args:
            batch_size: Max events per batch
            batch_timeout: Max time to wait before flushing (seconds)
        """
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        
        self._batch: list = []
        self._last_flush = time.time()
        self._flush_callbacks: list = []
    
    def add_event(self, event: EventMetadata) -> Optional[list]:
        """
        Add event to batch
        
        Returns:
            List of events if batch is ready to flush, None otherwise
        """
        self._batch.append(event)
        
        # Check if should flush
        if self._should_flush():
            return self.flush()
        
        return None
    
    def _should_flush(self) -> bool:
        """Check if batch should be flushed"""
        if len(self._batch) >= self.batch_size:
            return True
        
        if time.time() - self._last_flush >= self.batch_timeout:
            return True
        
        return False
    
    def flush(self) -> list:
        """
        Flush current batch
        
        Returns:
            List of events in the batch
        """
        if not self._batch:
            return []
        
        events = self._batch.copy()
        self._batch.clear()
        self._last_flush = time.time()
        
        logger.debug(f"Flushed batch of {len(events)} events")
        
        # Call flush callbacks
        for callback in self._flush_callbacks:
            try:
                callback(events)
            except Exception as e:
                logger.error(f"Batch flush callback error: {e}")
        
        return events
    
    def register_flush_callback(self, callback):
        """Register callback to be called on flush"""
        self._flush_callbacks.append(callback)
    
    def get_batch_size(self) -> int:
        """Get current batch size"""
        return len(self._batch)


# Global instance (initialize with your Redis connection)
event_deduplicator = EventDeduplicator()



















