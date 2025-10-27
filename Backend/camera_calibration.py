"""
Camera Calibration System
Homography, perspective correction, and per-camera parameter tuning
"""
import numpy as np
import cv2
import json
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class CameraProfile:
    """Camera profile for day/night conditions"""
    name: str
    confidence_threshold: float
    nms_threshold: float
    brightness_multiplier: float
    contrast_multiplier: float
    min_detection_size: int  # Minimum bbox size in pixels
    max_detection_size: int  # Maximum bbox size in pixels
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class CalibrationPoint:
    """Calibration point mapping"""
    image_x: int
    image_y: int
    world_x: float  # meters
    world_y: float  # meters
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


class CameraCalibration:
    """
    Camera calibration and parameter management
    
    Features:
    - Homography (pixel → real-world coordinates)
    - Perspective correction
    - Per-camera detection parameters
    - Day/night profile switching
    - Scene-specific tuning
    """
    
    def __init__(self, camera_id: str, calibration_file: Optional[str] = None):
        """
        Initialize camera calibration
        
        Args:
            camera_id: Unique camera identifier
            calibration_file: Path to calibration JSON file
        """
        self.camera_id = camera_id
        self.calibration_file = calibration_file or f"./config/camera_{camera_id}_calibration.json"
        
        # Homography matrix
        self.homography_matrix: Optional[np.ndarray] = None
        self.is_calibrated = False
        
        # Calibration points
        self.calibration_points: List[CalibrationPoint] = []
        
        # Detection parameters
        self.confidence_threshold = 0.35
        self.nms_threshold = 0.5
        
        # Profiles
        self.profiles: Dict[str, CameraProfile] = {
            "day": CameraProfile(
                name="day",
                confidence_threshold=0.35,
                nms_threshold=0.5,
                brightness_multiplier=1.0,
                contrast_multiplier=1.0,
                min_detection_size=20,
                max_detection_size=10000
            ),
            "night": CameraProfile(
                name="night",
                confidence_threshold=0.45,  # Higher threshold for night
                nms_threshold=0.4,
                brightness_multiplier=1.3,
                contrast_multiplier=1.2,
                min_detection_size=30,  # Larger minimum for night
                max_detection_size=10000
            ),
            "custom": CameraProfile(
                name="custom",
                confidence_threshold=0.35,
                nms_threshold=0.5,
                brightness_multiplier=1.0,
                contrast_multiplier=1.0,
                min_detection_size=20,
                max_detection_size=10000
            )
        }
        
        self.current_profile = "day"
        
        # Auto-switching settings
        self.auto_profile_switching = True
        self.day_brightness_threshold = 120
        self.night_brightness_threshold = 80
        
        # Image statistics
        self._recent_brightness: List[float] = []
        self._brightness_window = 30  # frames
        
        # Load existing calibration
        self._load_calibration()
        
        logger.info(f"Camera {camera_id} calibration initialized")
    
    def set_calibration_points(self,
                              image_points: List[Tuple[int, int]],
                              world_points: List[Tuple[float, float]]):
        """
        Set calibration points and compute homography
        
        Args:
            image_points: [(x1, y1), (x2, y2), ...] in pixels
            world_points: [(x1, y1), (x2, y2), ...] in meters
        """
        if len(image_points) != len(world_points):
            raise ValueError("Image and world points must have same length")
        
        if len(image_points) < 4:
            raise ValueError("Need at least 4 points for homography")
        
        # Store calibration points
        self.calibration_points = [
            CalibrationPoint(ip[0], ip[1], wp[0], wp[1])
            for ip, wp in zip(image_points, world_points)
        ]
        
        # Compute homography
        img_pts = np.float32(image_points)
        world_pts = np.float32(world_points)
        
        self.homography_matrix, status = cv2.findHomography(img_pts, world_pts)
        
        if self.homography_matrix is not None:
            self.is_calibrated = True
            logger.info(
                f"Camera {self.camera_id} calibrated with {len(image_points)} points"
            )
        else:
            logger.error(f"Camera {self.camera_id} homography computation failed")
            self.is_calibrated = False
        
        # Save calibration
        self._save_calibration()
    
    def pixel_to_world(self, x: int, y: int) -> Tuple[float, float]:
        """
        Convert pixel coordinates to real-world meters
        
        Args:
            x: Pixel x coordinate
            y: Pixel y coordinate
            
        Returns:
            (world_x, world_y) in meters
        """
        if not self.is_calibrated or self.homography_matrix is None:
            logger.warning(f"Camera {self.camera_id} not calibrated, returning pixels")
            return (float(x), float(y))
        
        # Apply homography transformation
        point = np.array([[[float(x), float(y)]]], dtype=np.float32)
        transformed = cv2.perspectiveTransform(point, self.homography_matrix)
        
        return tuple(transformed[0][0])
    
    def world_to_pixel(self, x: float, y: float) -> Tuple[int, int]:
        """
        Convert world coordinates to pixel coordinates
        
        Args:
            x: World x coordinate (meters)
            y: World y coordinate (meters)
            
        Returns:
            (pixel_x, pixel_y)
        """
        if not self.is_calibrated or self.homography_matrix is None:
            logger.warning(f"Camera {self.camera_id} not calibrated")
            return (int(x), int(y))
        
        # Apply inverse homography
        point = np.array([[[float(x), float(y)]]], dtype=np.float32)
        inv_matrix = np.linalg.inv(self.homography_matrix)
        transformed = cv2.perspectiveTransform(point, inv_matrix)
        
        return tuple(transformed[0][0].astype(int))
    
    def bbox_to_world(self, bbox: List[int]) -> Dict:
        """
        Convert bounding box to world coordinates
        
        Args:
            bbox: [x1, y1, x2, y2] in pixels
            
        Returns:
            Dictionary with world coordinates and dimensions
        """
        x1, y1, x2, y2 = bbox
        
        # Convert corners
        tl = self.pixel_to_world(x1, y1)
        tr = self.pixel_to_world(x2, y1)
        bl = self.pixel_to_world(x1, y2)
        br = self.pixel_to_world(x2, y2)
        
        # Calculate world dimensions
        width = np.sqrt((br[0] - bl[0])**2 + (br[1] - bl[1])**2)
        height = np.sqrt((tl[0] - bl[0])**2 + (tl[1] - bl[1])**2)
        
        # Calculate center
        center_x = (tl[0] + br[0]) / 2
        center_y = (tl[1] + br[1]) / 2
        
        return {
            "corners": {
                "top_left": tl,
                "top_right": tr,
                "bottom_left": bl,
                "bottom_right": br
            },
            "width_meters": width,
            "height_meters": height,
            "center": (center_x, center_y),
            "area_sqm": width * height
        }
    
    def get_current_profile(self) -> CameraProfile:
        """Get current active profile"""
        return self.profiles[self.current_profile]
    
    def set_profile(self, profile_name: str):
        """Set active profile"""
        if profile_name not in self.profiles:
            raise ValueError(f"Profile {profile_name} not found")
        
        self.current_profile = profile_name
        profile = self.profiles[profile_name]
        
        # Apply profile settings
        self.confidence_threshold = profile.confidence_threshold
        self.nms_threshold = profile.nms_threshold
        
        logger.info(f"Camera {self.camera_id} switched to {profile_name} profile")
    
    def auto_adjust_profile(self, frame: np.ndarray):
        """
        Automatically adjust profile based on frame brightness
        
        Args:
            frame: Input frame (BGR format)
        """
        if not self.auto_profile_switching:
            return
        
        # Calculate frame brightness
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        
        # Update rolling window
        self._recent_brightness.append(brightness)
        if len(self._recent_brightness) > self._brightness_window:
            self._recent_brightness.pop(0)
        
        # Use average brightness for stability
        avg_brightness = np.mean(self._recent_brightness)
        
        # Switch profiles based on brightness
        if avg_brightness < self.night_brightness_threshold:
            if self.current_profile != "night":
                self.set_profile("night")
                logger.info(
                    f"Camera {self.camera_id} auto-switched to NIGHT profile "
                    f"(brightness: {avg_brightness:.1f})"
                )
        
        elif avg_brightness > self.day_brightness_threshold:
            if self.current_profile != "day":
                self.set_profile("day")
                logger.info(
                    f"Camera {self.camera_id} auto-switched to DAY profile "
                    f"(brightness: {avg_brightness:.1f})"
                )
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply profile-based preprocessing to frame
        
        Args:
            frame: Input frame (BGR)
            
        Returns:
            Preprocessed frame
        """
        profile = self.get_current_profile()
        
        # Apply brightness adjustment
        if profile.brightness_multiplier != 1.0:
            frame = cv2.convertScaleAbs(
                frame,
                alpha=profile.brightness_multiplier,
                beta=0
            )
        
        # Apply contrast adjustment
        if profile.contrast_multiplier != 1.0:
            frame = cv2.convertScaleAbs(
                frame,
                alpha=profile.contrast_multiplier,
                beta=0
            )
        
        return frame
    
    def filter_detections(self, detections: List[Dict]) -> List[Dict]:
        """
        Filter detections based on profile settings
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            Filtered detections
        """
        profile = self.get_current_profile()
        filtered = []
        
        for det in detections:
            # Filter by confidence
            if det.get("confidence", 0) < profile.confidence_threshold:
                continue
            
            # Filter by size
            bbox = det.get("bbox", [0, 0, 0, 0])
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            area = width * height
            
            if area < profile.min_detection_size:
                continue
            
            if area > profile.max_detection_size:
                continue
            
            filtered.append(det)
        
        return filtered
    
    def _save_calibration(self):
        """Save calibration to file"""
        try:
            data = {
                "camera_id": self.camera_id,
                "is_calibrated": self.is_calibrated,
                "homography_matrix": self.homography_matrix.tolist() if self.homography_matrix is not None else None,
                "calibration_points": [p.to_dict() for p in self.calibration_points],
                "profiles": {
                    name: profile.to_dict()
                    for name, profile in self.profiles.items()
                },
                "current_profile": self.current_profile,
                "auto_profile_switching": self.auto_profile_switching,
                "day_brightness_threshold": self.day_brightness_threshold,
                "night_brightness_threshold": self.night_brightness_threshold
            }
            
            # Ensure directory exists
            Path(self.calibration_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.calibration_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Camera {self.camera_id} calibration saved")
            
        except Exception as e:
            logger.error(f"Error saving calibration: {e}")
    
    def _load_calibration(self):
        """Load calibration from file"""
        if not Path(self.calibration_file).exists():
            logger.info(f"No calibration file found for camera {self.camera_id}")
            return
        
        try:
            with open(self.calibration_file, 'r') as f:
                data = json.load(f)
            
            # Load homography matrix
            if data.get("homography_matrix"):
                self.homography_matrix = np.array(data["homography_matrix"])
                self.is_calibrated = data.get("is_calibrated", False)
            
            # Load calibration points
            if data.get("calibration_points"):
                self.calibration_points = [
                    CalibrationPoint(**p)
                    for p in data["calibration_points"]
                ]
            
            # Load profiles
            if data.get("profiles"):
                for name, profile_data in data["profiles"].items():
                    self.profiles[name] = CameraProfile(**profile_data)
            
            # Load settings
            self.current_profile = data.get("current_profile", "day")
            self.auto_profile_switching = data.get("auto_profile_switching", True)
            self.day_brightness_threshold = data.get("day_brightness_threshold", 120)
            self.night_brightness_threshold = data.get("night_brightness_threshold", 80)
            
            logger.info(f"Camera {self.camera_id} calibration loaded")
            
        except Exception as e:
            logger.error(f"Error loading calibration: {e}")
    
    def get_calibration_status(self) -> Dict:
        """Get calibration status"""
        return {
            "camera_id": self.camera_id,
            "is_calibrated": self.is_calibrated,
            "calibration_points_count": len(self.calibration_points),
            "current_profile": self.current_profile,
            "auto_profile_switching": self.auto_profile_switching,
            "confidence_threshold": self.confidence_threshold,
            "nms_threshold": self.nms_threshold,
            "profiles": list(self.profiles.keys())
        }


class CalibrationManager:
    """Manage calibrations for multiple cameras"""
    
    def __init__(self):
        self.calibrations: Dict[str, CameraCalibration] = {}
    
    def get_calibration(self, camera_id: str) -> CameraCalibration:
        """Get or create calibration for camera"""
        if camera_id not in self.calibrations:
            self.calibrations[camera_id] = CameraCalibration(camera_id)
        return self.calibrations[camera_id]
    
    def get_all_status(self) -> Dict:
        """Get status of all calibrations"""
        return {
            camera_id: cal.get_calibration_status()
            for camera_id, cal in self.calibrations.items()
        }


# Global instance
calibration_manager = CalibrationManager()













