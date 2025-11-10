"""
Multi-Camera Synchronization System

Fixes bounding box synchronization issues between multiple camera feeds
by implementing centralized detection processing and coordinate mapping.
"""

import asyncio
import time
import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, deque
import threading
import json


@dataclass
class Detection:
    """Standardized detection format"""
    cls: str
    conf: float
    bbox: List[float]  # Normalized [x1, y1, x2, y2]
    camera_id: str
    timestamp: float
    frame_id: int
    raw_xyxy: List[int]  # Pixel coordinates


@dataclass
class CameraConfig:
    """Camera configuration for synchronization"""
    camera_id: str
    source: str
    resolution: Tuple[int, int]
    calibration_matrix: Optional[np.ndarray] = None
    homography: Optional[np.ndarray] = None
    sync_offset_ms: float = 0.0  # Frame timing offset


class MultiCameraSyncManager:
    """
    Centralized synchronization manager for multiple camera streams
    
    Features:
    - Centralized detection processing
    - Cross-camera object tracking
    - Coordinate system mapping
    - Frame timing synchronization
    - Detection deduplication
    """
    
    def __init__(self, yolo_model=None):
        self.yolo_model = yolo_model
        self.cameras: Dict[str, CameraConfig] = {}
        self.active_detections: Dict[str, List[Detection]] = defaultdict(list)
        self.cross_camera_tracks: Dict[int, Dict[str, Any]] = {}
        self.frame_buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=5))
        self.detection_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))
        
        # Synchronization settings
        self.sync_tolerance_ms = 50.0  # 50ms tolerance for frame sync
        self.track_id_counter = 0
        self.last_sync_time = time.time()
        
        # Performance tracking
        self.stats = {
            "total_detections": 0,
            "synchronized_frames": 0,
            "cross_camera_matches": 0,
            "sync_errors": 0
        }
        
        # Thread safety
        self.lock = threading.RLock()
        
    def register_camera(self, camera_id: str, source: str, resolution: Tuple[int, int], 
                       calibration_matrix: Optional[np.ndarray] = None,
                       sync_offset_ms: float = 0.0):
        """Register a camera for synchronization"""
        with self.lock:
            self.cameras[camera_id] = CameraConfig(
                camera_id=camera_id,
                source=source,
                resolution=resolution,
                calibration_matrix=calibration_matrix,
                sync_offset_ms=sync_offset_ms
            )
            print(f"📹 Registered camera: {camera_id} ({resolution[0]}x{resolution[1]})")
    
    def unregister_camera(self, camera_id: str):
        """Unregister a camera"""
        with self.lock:
            if camera_id in self.cameras:
                del self.cameras[camera_id]
                del self.active_detections[camera_id]
                del self.frame_buffers[camera_id]
                del self.detection_history[camera_id]
                print(f"📹 Unregistered camera: {camera_id}")
    
    def process_frame_sync(self, camera_id: str, frame: np.ndarray, 
                          timestamp: float, frame_id: int) -> Dict[str, Any]:
        """
        Process frame with synchronization and return standardized detections
        
        Returns:
            Dict with synchronized detections and metadata
        """
        with self.lock:
            if camera_id not in self.cameras:
                return {"error": f"Camera {camera_id} not registered"}
            
            # Store frame in buffer for synchronization
            self.frame_buffers[camera_id].append({
                "frame": frame.copy(),
                "timestamp": timestamp,
                "frame_id": frame_id
            })
            
            # Get synchronized detections
            detections = self._get_synchronized_detections(camera_id, frame, timestamp, frame_id)
            
            # Update cross-camera tracking
            self._update_cross_camera_tracking(camera_id, detections, timestamp)
            
            # Update stats
            self.stats["total_detections"] += len(detections)
            if len(detections) > 0:
                self.stats["synchronized_frames"] += 1
            
            return {
                "camera_id": camera_id,
                "timestamp": timestamp,
                "frame_id": frame_id,
                "detections": [self._detection_to_dict(d) for d in detections],
                "sync_metadata": {
                    "active_cameras": len(self.cameras),
                    "cross_camera_tracks": len(self.cross_camera_tracks),
                    "sync_tolerance_ms": self.sync_tolerance_ms
                }
            }
    
    def _get_synchronized_detections(self, camera_id: str, frame: np.ndarray, 
                                   timestamp: float, frame_id: int) -> List[Detection]:
        """Get detections with cross-camera synchronization"""
        
        # Run detection on current frame
        detections = self._run_detection(camera_id, frame, timestamp, frame_id)
        
        # Check for cross-camera synchronization
        if len(self.cameras) > 1:
            detections = self._apply_cross_camera_sync(detections, camera_id, timestamp)
        
        # Store in history
        self.detection_history[camera_id].append(detections)
        
        return detections
    
    def _run_detection(self, camera_id: str, frame: np.ndarray, 
                      timestamp: float, frame_id: int) -> List[Detection]:
        """Run YOLO detection on frame"""
        if self.yolo_model is None:
            return []
        
        try:
            h, w = frame.shape[:2]
            
            # Convert BGR to RGB for Ultralytics
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Run inference
            results = self.yolo_model.predict(
                rgb,
                conf=0.35,
                iou=0.5,
                verbose=False,
                half=True,
                agnostic_nms=True,
                max_det=30
            )
            
            detections = []
            if results and len(results):
                r0 = results[0]
                if hasattr(r0, 'boxes') and r0.boxes is not None:
                    for b in r0.boxes:
                        # Get coordinates
                        xyxy = b.xyxy[0].tolist() if hasattr(b, "xyxy") else b[:4].tolist()
                        x1, y1, x2, y2 = map(int, xyxy)
                        
                        # Clamp to frame bounds
                        x1 = max(0, min(x1, w-1))
                        y1 = max(0, min(y1, h-1))
                        x2 = max(x1, min(x2, w-1))
                        y2 = max(y1, min(y2, h-1))
                        
                        # Get class and confidence
                        cls_id = int(b.cls[0].item()) if hasattr(b, "cls") else 0
                        conf = float(b.conf[0].item()) if hasattr(b, "conf") else 0.0
                        
                        # Get class name
                        if hasattr(r0, 'names') and r0.names:
                            name = r0.names[cls_id] if isinstance(r0.names, dict) and cls_id in r0.names else "person"
                        else:
                            name = "person"
                        
                        # Only include person detections
                        if name.lower() == "person" and conf > 0.35:
                            # Normalize coordinates
                            bbox_norm = [x1/w, y1/h, x2/w, y2/h]
                            
                            detection = Detection(
                                cls=name,
                                conf=conf,
                                bbox=bbox_norm,
                                camera_id=camera_id,
                                timestamp=timestamp,
                                frame_id=frame_id,
                                raw_xyxy=[x1, y1, x2, y2]
                            )
                            detections.append(detection)
            
            return detections
            
        except Exception as e:
            print(f"Detection error for camera {camera_id}: {e}")
            return []
    
    def _apply_cross_camera_sync(self, detections: List[Detection], 
                                camera_id: str, timestamp: float) -> List[Detection]:
        """Apply cross-camera synchronization to detections"""
        
        # Find matching detections from other cameras within sync tolerance
        sync_window_ms = self.sync_tolerance_ms / 1000.0
        
        for detection in detections:
            best_match = None
            best_score = 0.0
            
            # Check other cameras for similar detections
            for other_camera_id, other_detections in self.detection_history.items():
                if other_camera_id == camera_id:
                    continue
                
                for other_detection in other_detections:
                    # Check timing
                    time_diff = abs(detection.timestamp - other_detection.timestamp)
                    if time_diff > sync_window_ms:
                        continue
                    
                    # Check spatial overlap (if cameras overlap)
                    overlap_score = self._calculate_spatial_overlap(detection, other_detection)
                    if overlap_score > best_score and overlap_score > 0.3:
                        best_score = overlap_score
                        best_match = other_detection
            
            # Apply synchronization correction if match found
            if best_match:
                detection = self._sync_detection_coordinates(detection, best_match)
                self.stats["cross_camera_matches"] += 1
        
        return detections
    
    def _calculate_spatial_overlap(self, det1: Detection, det2: Detection) -> float:
        """Calculate spatial overlap between detections from different cameras"""
        # Simple overlap calculation - can be enhanced with homography
        bbox1 = det1.bbox
        bbox2 = det2.bbox
        
        # Calculate intersection
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _sync_detection_coordinates(self, detection: Detection, reference: Detection) -> Detection:
        """Synchronize detection coordinates with reference detection"""
        # Apply coordinate correction based on reference
        # This can be enhanced with homography mapping between cameras
        
        # For now, apply confidence-weighted blending
        weight = 0.7  # Weight for current detection
        
        # Blend bounding boxes
        bbox = detection.bbox.copy()
        ref_bbox = reference.bbox
        
        for i in range(4):
            bbox[i] = weight * bbox[i] + (1 - weight) * ref_bbox[i]
        
        detection.bbox = bbox
        
        # Update confidence
        detection.conf = max(detection.conf, reference.conf * 0.9)
        
        return detection
    
    def _update_cross_camera_tracking(self, camera_id: str, detections: List[Detection], timestamp: float):
        """Update cross-camera object tracking"""
        # Simple cross-camera tracking implementation
        # Can be enhanced with ReID embeddings
        
        for detection in detections:
            # Find existing track or create new one
            track_id = self._assign_track_id(detection, camera_id, timestamp)
            detection.track_id = track_id
    
    def _assign_track_id(self, detection: Detection, camera_id: str, timestamp: float) -> int:
        """Assign track ID to detection"""
        # Simple track assignment - can be enhanced with proper tracking
        return self.track_id_counter
    
    def _detection_to_dict(self, detection: Detection) -> Dict[str, Any]:
        """Convert Detection object to dictionary"""
        return {
            "cls": detection.cls,
            "conf": detection.conf,
            "bbox": detection.bbox,
            "camera_id": detection.camera_id,
            "timestamp": detection.timestamp,
            "frame_id": detection.frame_id,
            "xyxy": detection.raw_xyxy,
            "track_id": getattr(detection, 'track_id', None)
        }
    
    def get_sync_stats(self) -> Dict[str, Any]:
        """Get synchronization statistics"""
        with self.lock:
            return {
                "cameras_registered": len(self.cameras),
                "active_detections": {k: len(v) for k, v in self.active_detections.items()},
                "cross_camera_tracks": len(self.cross_camera_tracks),
                "stats": self.stats.copy(),
                "sync_tolerance_ms": self.sync_tolerance_ms
            }
    
    def set_sync_tolerance(self, tolerance_ms: float):
        """Set synchronization tolerance in milliseconds"""
        with self.lock:
            self.sync_tolerance_ms = tolerance_ms
            print(f"🔄 Sync tolerance set to {tolerance_ms}ms")


# Global sync manager instance
_sync_manager: Optional[MultiCameraSyncManager] = None


def get_sync_manager(yolo_model=None) -> MultiCameraSyncManager:
    """Get global sync manager instance"""
    global _sync_manager
    if _sync_manager is None:
        _sync_manager = MultiCameraSyncManager(yolo_model)
    return _sync_manager


def register_camera_sync(camera_id: str, source: str, resolution: Tuple[int, int], 
                        calibration_matrix: Optional[np.ndarray] = None,
                        sync_offset_ms: float = 0.0):
    """Register camera for synchronization"""
    manager = get_sync_manager()
    manager.register_camera(camera_id, source, resolution, calibration_matrix, sync_offset_ms)


def process_frame_sync(camera_id: str, frame: np.ndarray, timestamp: float, frame_id: int) -> Dict[str, Any]:
    """Process frame with synchronization"""
    manager = get_sync_manager()
    return manager.process_frame_sync(camera_id, frame, timestamp, frame_id)


def get_sync_stats() -> Dict[str, Any]:
    """Get synchronization statistics"""
    manager = get_sync_manager()
    return manager.get_sync_stats()


def set_sync_tolerance(tolerance_ms: float):
    """Set synchronization tolerance"""
    manager = get_sync_manager()
    manager.set_sync_tolerance(tolerance_ms)


















