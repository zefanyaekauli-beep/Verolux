"""
Resilient Video Source Manager
Handles camera reconnection, exponential backoff, and health monitoring
"""
import asyncio
import time
from typing import Optional, Dict, Callable
from dataclasses import dataclass, field
from enum import Enum
import cv2
import numpy as np
import threading
from queue import Queue, Empty
import logging

logger = logging.getLogger(__name__)


class SourceProtocol(Enum):
    """Video source protocols"""
    RTSP_TCP = "rtsp_tcp"
    RTSP_UDP = "rtsp_udp"
    HTTP = "http"
    WEBCAM = "webcam"
    FILE = "file"


@dataclass
class SourceHealth:
    """Health status of a video source"""
    camera_id: str
    last_frame_time: float = field(default_factory=time.time)
    consecutive_failures: int = 0
    is_healthy: bool = False
    reconnect_attempts: int = 0
    total_frames: int = 0
    dropped_frames: int = 0
    current_fps: float = 0.0
    protocol: SourceProtocol = SourceProtocol.RTSP_TCP
    error_message: str = ""
    
    @property
    def frame_age(self) -> float:
        """Seconds since last successful frame"""
        return time.time() - self.last_frame_time
    
    @property
    def status(self) -> str:
        """Human-readable status"""
        if not self.is_healthy:
            return "dead"
        elif self.frame_age > 60:
            return "stale"
        elif self.frame_age > 10:
            return "degraded"
        else:
            return "healthy"
    
    def to_dict(self) -> dict:
        """Export as dictionary"""
        return {
            "camera_id": self.camera_id,
            "is_healthy": self.is_healthy,
            "last_frame_age_seconds": self.frame_age,
            "consecutive_failures": self.consecutive_failures,
            "reconnect_attempts": self.reconnect_attempts,
            "total_frames": self.total_frames,
            "dropped_frames": self.dropped_frames,
            "current_fps": round(self.current_fps, 2),
            "protocol": self.protocol.value,
            "status": self.status,
            "error_message": self.error_message
        }


class ResilientVideoSource:
    """Production-grade video source with automatic reconnection"""
    
    def __init__(self, 
                 source_url: str,
                 camera_id: str,
                 reconnect_enabled: bool = True,
                 backoff_base: float = 2.0,
                 backoff_max: float = 300.0,
                 max_reconnect_attempts: int = 10,
                 buffer_size: int = 3,
                 timeout_seconds: float = 10.0):
        """
        Initialize resilient video source
        
        Args:
            source_url: RTSP URL, webcam index, or file path
            camera_id: Unique camera identifier
            reconnect_enabled: Enable automatic reconnection
            backoff_base: Base for exponential backoff (seconds)
            backoff_max: Maximum backoff delay (seconds)
            max_reconnect_attempts: Max attempts before marking dead
            buffer_size: OpenCV buffer size (lower = less latency)
            timeout_seconds: Connection timeout
        """
        self.source_url = source_url
        self.camera_id = camera_id
        self.reconnect_enabled = reconnect_enabled
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.max_reconnect_attempts = max_reconnect_attempts
        self.buffer_size = buffer_size
        self.timeout_seconds = timeout_seconds
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.health = SourceHealth(camera_id=camera_id)
        
        # Protocol detection
        self._detect_protocol()
        
        # Frame timing for FPS calculation
        self._frame_times: list = []
        self._fps_window = 30  # Calculate FPS over last 30 frames
        
        # Thread-safe frame queue for async grabbing
        self._frame_queue: Queue = Queue(maxsize=2)
        self._grabber_thread: Optional[threading.Thread] = None
        self._grabber_running = False
        
        logger.info(f"Initialized video source {camera_id} with protocol {self.health.protocol.value}")
    
    def _detect_protocol(self):
        """Detect source protocol from URL"""
        url_lower = str(self.source_url).lower()
        
        if url_lower.startswith("rtsp://"):
            self.health.protocol = SourceProtocol.RTSP_TCP
        elif url_lower.startswith("http://") or url_lower.startswith("https://"):
            self.health.protocol = SourceProtocol.HTTP
        elif url_lower.startswith("file://") or url_lower.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            self.health.protocol = SourceProtocol.FILE
        elif str(self.source_url).isdigit() or url_lower.startswith("webcam:"):
            self.health.protocol = SourceProtocol.WEBCAM
    
    def connect(self) -> bool:
        """
        Connect to video source with fallback protocols
        
        Returns:
            True if connection successful
        """
        try:
            # Try primary protocol
            if self.health.protocol == SourceProtocol.RTSP_TCP:
                success = self._connect_rtsp_tcp()
                
                # Fallback to UDP if TCP fails
                if not success:
                    logger.warning(f"Camera {self.camera_id}: TCP failed, trying UDP...")
                    self.health.protocol = SourceProtocol.RTSP_UDP
                    success = self._connect_rtsp_udp()
                
                return success
            
            elif self.health.protocol == SourceProtocol.RTSP_UDP:
                return self._connect_rtsp_udp()
            
            elif self.health.protocol == SourceProtocol.WEBCAM:
                return self._connect_webcam()
            
            elif self.health.protocol == SourceProtocol.FILE:
                return self._connect_file()
            
            elif self.health.protocol == SourceProtocol.HTTP:
                return self._connect_http()
            
            else:
                logger.error(f"Camera {self.camera_id}: Unknown protocol")
                return False
                
        except Exception as e:
            logger.error(f"Camera {self.camera_id} connection error: {e}")
            self.health.error_message = str(e)
            return False
    
    def _connect_rtsp_tcp(self) -> bool:
        """Connect via RTSP over TCP"""
        try:
            # Force TCP transport
            rtsp_tcp = self.source_url + "?tcp"
            
            self.cap = cv2.VideoCapture(rtsp_tcp, cv2.CAP_FFMPEG)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
            self.cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, int(self.timeout_seconds * 1000))
            
            if self.cap.isOpened():
                self.health.is_healthy = True
                self.health.reconnect_attempts = 0
                self.health.consecutive_failures = 0
                self.health.error_message = ""
                logger.info(f"Camera {self.camera_id} connected via RTSP/TCP")
                return True
                
        except Exception as e:
            logger.error(f"Camera {self.camera_id} RTSP/TCP error: {e}")
            self.health.error_message = str(e)
        
        return False
    
    def _connect_rtsp_udp(self) -> bool:
        """Connect via RTSP over UDP"""
        try:
            # Force UDP transport
            rtsp_udp = self.source_url.replace("rtsp://", "rtspu://")
            
            self.cap = cv2.VideoCapture(rtsp_udp, cv2.CAP_FFMPEG)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
            
            if self.cap.isOpened():
                self.health.is_healthy = True
                self.health.reconnect_attempts = 0
                self.health.consecutive_failures = 0
                self.health.error_message = ""
                logger.info(f"Camera {self.camera_id} connected via RTSP/UDP")
                return True
                
        except Exception as e:
            logger.error(f"Camera {self.camera_id} RTSP/UDP error: {e}")
            self.health.error_message = str(e)
        
        return False
    
    def _connect_webcam(self) -> bool:
        """Connect to webcam"""
        try:
            index = int(str(self.source_url).replace("webcam:", ""))
            self.cap = cv2.VideoCapture(index)
            
            if self.cap.isOpened():
                self.health.is_healthy = True
                self.health.reconnect_attempts = 0
                self.health.consecutive_failures = 0
                logger.info(f"Camera {self.camera_id} connected to webcam {index}")
                return True
                
        except Exception as e:
            logger.error(f"Camera {self.camera_id} webcam error: {e}")
            self.health.error_message = str(e)
        
        return False
    
    def _connect_file(self) -> bool:
        """Connect to video file"""
        try:
            file_path = str(self.source_url).replace("file://", "")
            self.cap = cv2.VideoCapture(file_path)
            
            if self.cap.isOpened():
                self.health.is_healthy = True
                self.health.reconnect_attempts = 0
                self.health.consecutive_failures = 0
                logger.info(f"Camera {self.camera_id} opened file {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"Camera {self.camera_id} file error: {e}")
            self.health.error_message = str(e)
        
        return False
    
    def _connect_http(self) -> bool:
        """Connect to HTTP stream"""
        try:
            self.cap = cv2.VideoCapture(self.source_url)
            
            if self.cap.isOpened():
                self.health.is_healthy = True
                self.health.reconnect_attempts = 0
                self.health.consecutive_failures = 0
                logger.info(f"Camera {self.camera_id} connected via HTTP")
                return True
                
        except Exception as e:
            logger.error(f"Camera {self.camera_id} HTTP error: {e}")
            self.health.error_message = str(e)
        
        return False
    
    def read_frame(self) -> tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame with automatic reconnection
        
        Returns:
            (success, frame) tuple
        """
        # Check if connected
        if not self.cap or not self.cap.isOpened():
            if self.reconnect_enabled:
                if not self._attempt_reconnect():
                    return False, None
            else:
                return False, None
        
        try:
            ret, frame = self.cap.read()
            
            if not ret or frame is None:
                self.health.consecutive_failures += 1
                self.health.dropped_frames += 1
                
                # Reconnect after 3 consecutive failures
                if self.health.consecutive_failures >= 3:
                    logger.warning(
                        f"Camera {self.camera_id}: {self.health.consecutive_failures} "
                        f"consecutive failures, reconnecting..."
                    )
                    if self.reconnect_enabled:
                        self._attempt_reconnect()
                
                return False, None
            
            # Success - update metrics
            self.health.consecutive_failures = 0
            self.health.last_frame_time = time.time()
            self.health.is_healthy = True
            self.health.total_frames += 1
            
            # Update FPS calculation
            self._update_fps()
            
            return True, frame
            
        except Exception as e:
            logger.error(f"Camera {self.camera_id} read error: {e}")
            self.health.error_message = str(e)
            if self.reconnect_enabled:
                self._attempt_reconnect()
            return False, None
    
    def _attempt_reconnect(self) -> bool:
        """
        Attempt to reconnect with exponential backoff
        
        Returns:
            True if reconnection successful
        """
        self.health.reconnect_attempts += 1
        
        # Check if exceeded max attempts
        if self.health.reconnect_attempts > self.max_reconnect_attempts:
            logger.error(
                f"Camera {self.camera_id} DEAD after "
                f"{self.max_reconnect_attempts} reconnect attempts"
            )
            self.health.is_healthy = False
            self.health.error_message = "Max reconnect attempts exceeded"
            return False
        
        # Calculate exponential backoff delay
        backoff_delay = min(
            self.backoff_base ** self.health.reconnect_attempts,
            self.backoff_max
        )
        
        logger.info(
            f"Camera {self.camera_id} reconnecting in {backoff_delay:.1f}s "
            f"(attempt {self.health.reconnect_attempts}/{self.max_reconnect_attempts})"
        )
        
        time.sleep(backoff_delay)
        
        # Close existing connection
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Attempt reconnection
        return self.connect()
    
    def _update_fps(self):
        """Update FPS calculation"""
        now = time.time()
        self._frame_times.append(now)
        
        # Keep only recent frames
        if len(self._frame_times) > self._fps_window:
            self._frame_times.pop(0)
        
        # Calculate FPS
        if len(self._frame_times) >= 2:
            time_span = self._frame_times[-1] - self._frame_times[0]
            if time_span > 0:
                self.health.current_fps = (len(self._frame_times) - 1) / time_span
    
    def start_async_grabber(self):
        """Start background thread for frame grabbing"""
        if self._grabber_running:
            return
        
        self._grabber_running = True
        self._grabber_thread = threading.Thread(target=self._frame_grabber_loop, daemon=True)
        self._grabber_thread.start()
        logger.info(f"Camera {self.camera_id}: Started async frame grabber")
    
    def _frame_grabber_loop(self):
        """Background thread that continuously grabs frames"""
        while self._grabber_running:
            ret, frame = self.read_frame()
            
            if ret and frame is not None:
                # Try to put frame in queue (non-blocking)
                try:
                    # Remove old frame if queue is full
                    if self._frame_queue.full():
                        try:
                            self._frame_queue.get_nowait()
                            self.health.dropped_frames += 1
                        except Empty:
                            pass
                    
                    self._frame_queue.put((ret, frame), block=False)
                except Exception as e:
                    logger.error(f"Camera {self.camera_id} queue error: {e}")
            
            # Small delay to prevent CPU spin
            time.sleep(0.001)
    
    def read_frame_async(self) -> tuple[bool, Optional[np.ndarray]]:
        """
        Read frame from async grabber queue
        
        Returns:
            (success, frame) tuple
        """
        try:
            return self._frame_queue.get(timeout=1.0)
        except Empty:
            return False, None
    
    def get_health_status(self) -> dict:
        """Get detailed health status"""
        return self.health.to_dict()
    
    def reset_health(self):
        """Reset health metrics (useful for testing)"""
        self.health.reconnect_attempts = 0
        self.health.consecutive_failures = 0
        self.health.dropped_frames = 0
        self.health.error_message = ""
        logger.info(f"Camera {self.camera_id}: Health metrics reset")
    
    def close(self):
        """Cleanup and close connection"""
        # Stop async grabber
        if self._grabber_running:
            self._grabber_running = False
            if self._grabber_thread:
                self._grabber_thread.join(timeout=2.0)
        
        # Release capture
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.health.is_healthy = False
        logger.info(f"Camera {self.camera_id}: Connection closed")
    
    def __del__(self):
        """Ensure cleanup on deletion"""
        self.close()


class VideoSourceManager:
    """Manage multiple video sources with health monitoring"""
    
    def __init__(self):
        self.sources: Dict[str, ResilientVideoSource] = {}
        self._health_check_interval = 30  # seconds
        self._health_check_task: Optional[asyncio.Task] = None
    
    def add_source(self, camera_id: str, source_url: str, **kwargs) -> ResilientVideoSource:
        """Add a new video source"""
        source = ResilientVideoSource(source_url, camera_id, **kwargs)
        source.connect()
        self.sources[camera_id] = source
        logger.info(f"Added camera {camera_id} to source manager")
        return source
    
    def remove_source(self, camera_id: str):
        """Remove and cleanup a video source"""
        if camera_id in self.sources:
            self.sources[camera_id].close()
            del self.sources[camera_id]
            logger.info(f"Removed camera {camera_id} from source manager")
    
    def get_source(self, camera_id: str) -> Optional[ResilientVideoSource]:
        """Get video source by camera ID"""
        return self.sources.get(camera_id)
    
    def get_all_health_status(self) -> dict:
        """Get health status of all cameras"""
        return {
            camera_id: source.get_health_status()
            for camera_id, source in self.sources.items()
        }
    
    def get_healthy_cameras(self) -> list:
        """Get list of healthy camera IDs"""
        return [
            camera_id
            for camera_id, source in self.sources.items()
            if source.health.is_healthy
        ]
    
    def get_unhealthy_cameras(self) -> list:
        """Get list of unhealthy camera IDs"""
        return [
            camera_id
            for camera_id, source in self.sources.items()
            if not source.health.is_healthy
        ]
    
    async def start_health_monitoring(self):
        """Start background health monitoring"""
        while True:
            await asyncio.sleep(self._health_check_interval)
            await self._periodic_health_check()
    
    async def _periodic_health_check(self):
        """Periodic health check for all cameras"""
        unhealthy = self.get_unhealthy_cameras()
        
        if unhealthy:
            logger.warning(f"Unhealthy cameras: {unhealthy}")
        
        # Log aggregate statistics
        total = len(self.sources)
        healthy = len(self.get_healthy_cameras())
        
        logger.info(f"Camera health: {healthy}/{total} healthy")
    
    def close_all(self):
        """Close all video sources"""
        for source in self.sources.values():
            source.close()
        self.sources.clear()
        logger.info("All video sources closed")


# Global instance
video_source_manager = VideoSourceManager()




















