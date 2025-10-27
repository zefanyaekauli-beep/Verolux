"""
Model Drift Monitoring System
Detects input drift, label drift, and performance drift
"""
import time
import numpy as np
from typing import Dict, List, Optional, Deque
from collections import deque
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class DriftMetrics:
    """Drift detection metrics"""
    timestamp: float
    mean_brightness: float
    mean_contrast: float
    detection_count_avg: float
    confidence_avg: float
    fps: float
    latency_ms: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp,
            "mean_brightness": self.mean_brightness,
            "mean_contrast": self.mean_contrast,
            "detection_count_avg": self.detection_count_avg,
            "confidence_avg": self.confidence_avg,
            "fps": self.fps,
            "latency_ms": self.latency_ms
        }


class DriftDetector:
    """
    Detect drift in model inputs and outputs
    
    Monitors:
    - Input drift (brightness, scene changes)
    - Label drift (detection patterns)
    - Performance drift (FPS, latency degradation)
    """
    
    def __init__(self,
                 window_size: int = 1000,
                 baseline_window: int = 100):
        """
        Initialize drift detector
        
        Args:
            window_size: Number of frames to track
            baseline_window: Initial frames to establish baseline
        """
        self.window_size = window_size
        self.baseline_window = baseline_window
        
        # Rolling windows for metrics
        self.brightness_history: Deque[float] = deque(maxlen=window_size)
        self.contrast_history: Deque[float] = deque(maxlen=window_size)
        self.detection_count_history: Deque[int] = deque(maxlen=window_size)
        self.confidence_history: Deque[float] = deque(maxlen=window_size)
        self.fps_history: Deque[float] = deque(maxlen=window_size)
        self.latency_history: Deque[float] = deque(maxlen=window_size)
        
        # Baseline statistics
        self.baseline: Optional[DriftMetrics] = None
        self.baseline_established = False
        
        # Drift detection thresholds
        self.thresholds = {
            "brightness_change_pct": 20.0,  # 20% change
            "contrast_change_pct": 25.0,
            "detection_count_change_pct": 30.0,
            "confidence_drop": 0.10,  # 10% absolute drop
            "fps_drop_pct": 15.0,
            "latency_increase_pct": 50.0
        }
        
        # Drift alerts
        self.drift_alerts: List[Dict] = []
        
        logger.info("Drift detector initialized")
    
    def update(self,
              frame: np.ndarray,
              detections: List[Dict],
              fps: float,
              latency_ms: float):
        """
        Update drift metrics with new frame data
        
        Args:
            frame: Input frame (BGR)
            detections: Detection results
            fps: Current FPS
            latency_ms: Processing latency
        """
        # Calculate frame statistics
        gray = frame if len(frame.shape) == 2 else frame.mean(axis=2)
        brightness = float(gray.mean())
        contrast = float(gray.std())
        
        # Detection statistics
        detection_count = len(detections)
        confidence_avg = (
            float(np.mean([d.get("confidence", 0) for d in detections]))
            if detections else 0.0
        )
        
        # Update histories
        self.brightness_history.append(brightness)
        self.contrast_history.append(contrast)
        self.detection_count_history.append(detection_count)
        self.confidence_history.append(confidence_avg)
        self.fps_history.append(fps)
        self.latency_history.append(latency_ms)
        
        # Establish baseline if not done
        if not self.baseline_established and len(self.brightness_history) >= self.baseline_window:
            self._establish_baseline()
        
        # Check for drift if baseline established
        if self.baseline_established:
            self._check_drift()
    
    def _establish_baseline(self):
        """Establish baseline statistics"""
        logger.info("Establishing baseline statistics...")
        
        self.baseline = DriftMetrics(
            timestamp=time.time(),
            mean_brightness=float(np.mean(list(self.brightness_history)[:self.baseline_window])),
            mean_contrast=float(np.mean(list(self.contrast_history)[:self.baseline_window])),
            detection_count_avg=float(np.mean(list(self.detection_count_history)[:self.baseline_window])),
            confidence_avg=float(np.mean(list(self.confidence_history)[:self.baseline_window])),
            fps=float(np.mean(list(self.fps_history)[:self.baseline_window])),
            latency_ms=float(np.mean(list(self.latency_history)[:self.baseline_window]))
        )
        
        self.baseline_established = True
        
        logger.info(
            f"Baseline established: brightness={self.baseline.mean_brightness:.1f}, "
            f"detections={self.baseline.detection_count_avg:.1f}/frame, "
            f"fps={self.baseline.fps:.1f}"
        )
    
    def _check_drift(self):
        """Check for drift in recent data"""
        if not self.baseline:
            return
        
        # Calculate current statistics (recent window)
        recent_window = min(100, len(self.brightness_history))
        
        current_brightness = float(np.mean(list(self.brightness_history)[-recent_window:]))
        current_contrast = float(np.mean(list(self.contrast_history)[-recent_window:]))
        current_detection_count = float(np.mean(list(self.detection_count_history)[-recent_window:]))
        current_confidence = float(np.mean(list(self.confidence_history)[-recent_window:]))
        current_fps = float(np.mean(list(self.fps_history)[-recent_window:]))
        current_latency = float(np.mean(list(self.latency_history)[-recent_window:]))
        
        # Check for drift
        drift_detected = False
        
        # Input drift (brightness/contrast changes)
        brightness_change_pct = abs(current_brightness - self.baseline.mean_brightness) / self.baseline.mean_brightness * 100
        if brightness_change_pct > self.thresholds["brightness_change_pct"]:
            self._alert_drift(
                "input",
                f"Brightness drift: {brightness_change_pct:.1f}% change "
                f"(baseline: {self.baseline.mean_brightness:.1f}, current: {current_brightness:.1f})"
            )
            drift_detected = True
        
        # Label drift (detection patterns)
        detection_change_pct = abs(current_detection_count - self.baseline.detection_count_avg) / max(self.baseline.detection_count_avg, 1) * 100
        if detection_change_pct > self.thresholds["detection_count_change_pct"]:
            self._alert_drift(
                "label",
                f"Detection pattern drift: {detection_change_pct:.1f}% change "
                f"(baseline: {self.baseline.detection_count_avg:.1f}, current: {current_detection_count:.1f})"
            )
            drift_detected = True
        
        # Confidence drift
        confidence_drop = self.baseline.confidence_avg - current_confidence
        if confidence_drop > self.thresholds["confidence_drop"]:
            self._alert_drift(
                "confidence",
                f"Confidence drift: {confidence_drop:.3f} drop "
                f"(baseline: {self.baseline.confidence_avg:.3f}, current: {current_confidence:.3f})"
            )
            drift_detected = True
        
        # Performance drift (FPS/latency)
        fps_change_pct = (current_fps - self.baseline.fps) / self.baseline.fps * 100
        if fps_change_pct < -self.thresholds["fps_drop_pct"]:
            self._alert_drift(
                "performance",
                f"FPS drift: {fps_change_pct:.1f}% drop "
                f"(baseline: {self.baseline.fps:.1f}, current: {current_fps:.1f})"
            )
            drift_detected = True
        
        return drift_detected
    
    def _alert_drift(self, drift_type: str, message: str):
        """Log drift alert"""
        alert = {
            "timestamp": time.time(),
            "type": drift_type,
            "message": message
        }
        
        self.drift_alerts.append(alert)
        
        # Keep only recent alerts
        if len(self.drift_alerts) > 100:
            self.drift_alerts.pop(0)
        
        logger.warning(f"Drift detected ({drift_type}): {message}")
    
    def _save_metrics(self, model_version: str, metrics: ValidationMetrics):
        """Save validation metrics to file"""
        metrics_file = f"./models/validation_{model_version}.json"
        
        os.makedirs(os.path.dirname(metrics_file), exist_ok=True)
        
        with open(metrics_file, 'w') as f:
            json.dump(metrics.to_dict(), f, indent=2)
    
    def get_drift_status(self) -> dict:
        """Get current drift status"""
        return {
            "baseline_established": self.baseline_established,
            "baseline": self.baseline.to_dict() if self.baseline else None,
            "recent_alerts": self.drift_alerts[-10:],
            "total_alerts": len(self.drift_alerts),
            "samples_collected": len(self.brightness_history)
        }
    
    def reset_baseline(self):
        """Reset baseline (e.g., after camera move or lighting change)"""
        self.baseline_established = False
        self.baseline = None
        self.drift_alerts.clear()
        
        logger.info("Drift baseline reset")


# Global instance
drift_monitor = DriftDetector()













