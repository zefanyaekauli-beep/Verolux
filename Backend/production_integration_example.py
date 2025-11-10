"""
Production Features Integration Example
Demonstrates how to use all production features together
"""
import asyncio
import time
from typing import Optional
import numpy as np

# Import production features
from video_source_manager import VideoSourceManager, ResilientVideoSource
from event_deduplication import EventDeduplicator, EventType
from alert_rate_limiter import AlertRateLimiter, Alert, AlertChannel, AlertPriority
from model_registry import ModelRegistry, ModelFramework, ModelPrecision, ModelMetrics
from camera_calibration import CalibrationManager


class ProductionGateSystem:
    """
    Example integration of all production features
    Shows best practices for using the complete system
    """
    
    def __init__(self, camera_id: str, rtsp_url: str):
        """
        Initialize production-ready gate system
        
        Args:
            camera_id: Unique camera identifier
            rtsp_url: RTSP stream URL
        """
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        
        # Initialize managers
        self.video_manager = VideoSourceManager()
        self.event_dedup = EventDeduplicator(redis_url="redis://localhost:6379")
        self.alert_limiter = AlertRateLimiter()
        self.model_registry = ModelRegistry()
        self.calibration_mgr = CalibrationManager()
        
        # Get camera-specific calibration
        self.calibration = self.calibration_mgr.get_calibration(camera_id)
        
        # Create resilient video source
        self.video_source: Optional[ResilientVideoSource] = None
        
        print(f"✅ Production gate system initialized for camera {camera_id}")
    
    def setup_camera(self):
        """Set up resilient camera connection"""
        print(f"Setting up camera {self.camera_id}...")
        
        # Add camera to video source manager
        self.video_source = self.video_manager.add_source(
            camera_id=self.camera_id,
            source_url=self.rtsp_url,
            reconnect_enabled=True,
            backoff_base=2.0,
            backoff_max=300.0,
            max_reconnect_attempts=10
        )
        
        # Start async frame grabber for better performance
        self.video_source.start_async_grabber()
        
        print(f"✅ Camera {self.camera_id} connected with auto-reconnect")
    
    def setup_calibration(self):
        """Set up camera calibration"""
        print(f"Setting up calibration for {self.camera_id}...")
        
        # Example: Set calibration points for a typical gate camera
        # These would be configured per-camera in production
        image_points = [
            (100, 100),   # Top-left gate post
            (540, 100),   # Top-right gate post
            (540, 380),   # Bottom-right ground marker
            (100, 380)    # Bottom-left ground marker
        ]
        
        world_points = [
            (0.0, 0.0),   # 0m, 0m
            (3.0, 0.0),   # 3m, 0m (gate width)
            (3.0, 2.5),   # 3m, 2.5m (gate depth)
            (0.0, 2.5)    # 0m, 2.5m
        ]
        
        self.calibration.set_calibration_points(image_points, world_points)
        
        # Enable auto day/night switching
        self.calibration.auto_profile_switching = True
        
        print(f"✅ Camera {self.camera_id} calibrated")
    
    def setup_model_registry(self):
        """Set up model versioning"""
        print("Setting up model registry...")
        
        # Register current model (example)
        try:
            self.model_registry.register_model(
                version="v1.0.0",
                path="./models/weight.pt",
                framework=ModelFramework.PYTORCH,
                precision=ModelPrecision.FP32,
                metrics=ModelMetrics(
                    map_50=0.85,
                    fps=30.0,
                    latency_ms=33.0
                ),
                notes="Production baseline model",
                created_by="system"
            )
            
            # Activate as production model
            self.model_registry.activate_model("v1.0.0")
            
            print("✅ Model registry configured")
        except Exception as e:
            print(f"⚠️ Model registry setup warning: {e}")
    
    async def process_frame(self, frame: np.ndarray, detections: list):
        """
        Process frame with production features
        
        Args:
            frame: Video frame
            detections: YOLO detections
        """
        # 1. Auto-adjust camera profile based on brightness
        self.calibration.auto_adjust_profile(frame)
        
        # 2. Filter detections using calibrated parameters
        filtered_detections = self.calibration.filter_detections(detections)
        
        # 3. Convert detections to world coordinates (if calibrated)
        for det in filtered_detections:
            if self.calibration.is_calibrated:
                world_coords = self.calibration.bbox_to_world(det["bbox"])
                det["world_coordinates"] = world_coords
        
        return filtered_detections
    
    async def emit_security_event(self,
                                 event_type: str,
                                 track_id: int,
                                 event_data: dict):
        """
        Emit security event with deduplication
        
        Args:
            event_type: Type of event
            track_id: Track ID
            event_data: Event payload
        """
        # Emit event with automatic deduplication
        event = self.event_dedup.emit_event(
            camera_id=self.camera_id,
            event_type=event_type,
            event_data=event_data,
            track_id=track_id
        )
        
        if event:
            print(f"✅ Event emitted: {event.event_id} ({event_type})")
            return event
        else:
            print(f"⏭️ Event suppressed (duplicate): {event_type} for track {track_id}")
            return None
    
    async def send_alert(self,
                        channel: AlertChannel,
                        priority: AlertPriority,
                        title: str,
                        message: str,
                        data: dict,
                        snapshot_url: Optional[str] = None):
        """
        Send alert with automatic rate limiting
        
        Args:
            channel: Alert channel (Telegram, Email, etc.)
            priority: Alert priority
            title: Alert title
            message: Alert message
            data: Additional data
            snapshot_url: Optional snapshot URL
        """
        alert = Alert(
            alert_id=f"{self.camera_id}_{int(time.time()*1000)}",
            channel=channel,
            camera_id=self.camera_id,
            priority=priority,
            title=title,
            message=message,
            data=data,
            snapshot_url=snapshot_url
        )
        
        # Send alert (automatically rate limited and batched)
        sent = await self.alert_limiter.send_alert(alert)
        
        if sent:
            print(f"✅ Alert sent immediately: {title}")
        else:
            print(f"⏳ Alert queued for batch: {title}")
        
        return sent
    
    def get_health_status(self) -> dict:
        """Get comprehensive health status"""
        camera_health = self.video_source.get_health_status() if self.video_source else {}
        
        return {
            "camera": camera_health,
            "calibration": self.calibration.get_calibration_status(),
            "deduplication": self.event_dedup.get_stats(),
            "alerts": self.alert_limiter.get_stats(),
            "model": self.model_registry.get_registry_summary()
        }
    
    async def run(self):
        """Main processing loop"""
        print(f"🚀 Starting production gate system for {self.camera_id}...")
        
        frame_count = 0
        
        while True:
            try:
                # Read frame (auto-reconnects on failure)
                ret, frame = self.video_source.read_frame_async()
                
                if not ret or frame is None:
                    await asyncio.sleep(0.1)
                    continue
                
                frame_count += 1
                
                # Example: Emit health event every 100 frames
                if frame_count % 100 == 0:
                    await self.emit_security_event(
                        event_type="heartbeat",
                        track_id=0,
                        event_data={
                            "frame_count": frame_count,
                            "fps": self.video_source.health.current_fps
                        }
                    )
                
                # Process frame with your existing logic here
                # detections = yolo_model(frame)
                # filtered = await self.process_frame(frame, detections)
                # ... your gate checking logic ...
                
                await asyncio.sleep(0.033)  # 30 FPS
                
            except KeyboardInterrupt:
                print("Shutting down...")
                break
            except Exception as e:
                print(f"Error in processing loop: {e}")
                await asyncio.sleep(1)
    
    def cleanup(self):
        """Cleanup resources"""
        if self.video_source:
            self.video_source.close()
        
        print(f"✅ Cleanup complete for {self.camera_id}")


# ===== EXAMPLE USAGE =====

async def example_integration():
    """Complete example of using production features"""
    
    print("="*60)
    print("Production Features Integration Example")
    print("="*60)
    print()
    
    # Initialize system
    system = ProductionGateSystem(
        camera_id="gate_a1",
        rtsp_url="rtsp://192.168.1.100/stream1"
    )
    
    # Setup components
    system.setup_camera()
    system.setup_calibration()
    system.setup_model_registry()
    
    print()
    print("="*60)
    print("System Status")
    print("="*60)
    
    # Check health
    health = system.get_health_status()
    print(f"Camera health: {health['camera']['status']}")
    print(f"Calibration: {'✅ Calibrated' if health['calibration']['is_calibrated'] else '❌ Not calibrated'}")
    print(f"Event deduplication: {health['deduplication']['backend']}")
    print()
    
    # Example: Emit security event
    print("Testing event emission...")
    event1 = await system.emit_security_event(
        event_type=EventType.CHECK_COMPLETED.value,
        track_id=123,
        event_data={"score": 0.95}
    )
    
    # Try to emit duplicate (should be suppressed)
    event2 = await system.emit_security_event(
        event_type=EventType.CHECK_COMPLETED.value,
        track_id=123,
        event_data={"score": 0.95}
    )
    
    print()
    
    # Example: Send alert
    print("Testing alert system...")
    await system.send_alert(
        channel=AlertChannel.TELEGRAM,
        priority=AlertPriority.HIGH,
        title="Security Check Completed",
        message=f"Gate {system.camera_id}: Check completed with score 0.95",
        data={"score": 0.95, "track_id": 123}
    )
    
    print()
    
    # Show statistics
    print("="*60)
    print("Statistics")
    print("="*60)
    dedup_stats = system.event_dedup.get_stats()
    print(f"Events emitted: {dedup_stats['emitted']}")
    print(f"Events suppressed: {dedup_stats['suppressed']}")
    print(f"Suppression rate: {dedup_stats['suppression_rate_percent']}%")
    print()
    
    alert_stats = system.alert_limiter.get_stats()
    print(f"Alerts sent: {alert_stats['sent']}")
    print(f"Alerts batched: {alert_stats['batched']}")
    print()
    
    # Cleanup
    system.cleanup()
    
    print("="*60)
    print("✅ Example complete!")
    print("="*60)


if __name__ == "__main__":
    # Run example
    asyncio.run(example_integration())



















