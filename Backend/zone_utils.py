#!/usr/bin/env python3
"""
Zone Utilities for Gate Security System
Handles polygon operations, proximity detection, and spatial analysis
"""

import json
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points
from scipy.signal import savgol_filter
from dataclasses import dataclass
import cv2


@dataclass
class BBox:
    """Bounding box representation"""
    x1: float
    y1: float
    x2: float
    y2: float
    
    @property
    def center(self) -> Tuple[float, float]:
        return ((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)
    
    @property
    def width(self) -> float:
        return self.x2 - self.x1
    
    @property
    def height(self) -> float:
        return self.y2 - self.y1
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    def to_polygon(self) -> Polygon:
        """Convert bbox to Shapely polygon"""
        return Polygon([
            (self.x1, self.y1),
            (self.x2, self.y1),
            (self.x2, self.y2),
            (self.x1, self.y2)
        ])


class ZoneManager:
    """Manages zones and spatial queries"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.zones: Dict[str, Polygon] = {}
        self.zone_metadata: Dict[str, Dict] = {}
        
    def load_zone(self, zone_file: str) -> Polygon:
        """Load zone polygon from JSON file"""
        with open(f"{self.config_dir}/{zone_file}", 'r') as f:
            data = json.load(f)
        
        polygon_coords = data['polygon']
        zone_id = data.get('zone_id', zone_file)
        
        # Convert to Shapely polygon
        poly = Polygon(polygon_coords)
        
        # Store zone and metadata
        self.zones[zone_id] = poly
        self.zone_metadata[zone_id] = data
        
        return poly
    
    def point_in_zone(self, point: Tuple[float, float], zone_id: str) -> bool:
        """Check if point is inside zone"""
        if zone_id not in self.zones:
            return False
        
        pt = Point(point)
        return self.zones[zone_id].contains(pt)
    
    def bbox_in_zone(self, bbox: BBox, zone_id: str, 
                     overlap_thresh: float = 0.2) -> bool:
        """Check if bbox overlaps with zone"""
        if zone_id not in self.zones:
            return False
        
        bbox_poly = bbox.to_polygon()
        zone_poly = self.zones[zone_id]
        
        # Calculate intersection over bbox area
        intersection = bbox_poly.intersection(zone_poly)
        iou = intersection.area / (bbox_poly.area + 1e-9)
        
        return iou >= overlap_thresh
    
    def distance_to_zone(self, point: Tuple[float, float], zone_id: str) -> float:
        """Calculate distance from point to zone boundary"""
        if zone_id not in self.zones:
            return float('inf')
        
        pt = Point(point)
        zone_poly = self.zones[zone_id]
        
        if zone_poly.contains(pt):
            return 0.0
        
        # Find nearest point on zone boundary
        nearest = nearest_points(pt, zone_poly.boundary)[1]
        return pt.distance(nearest)
    
    def denormalize_polygon(self, zone_id: str, width: int, height: int) -> np.ndarray:
        """Convert normalized polygon to pixel coordinates"""
        if zone_id not in self.zones:
            return np.array([])
        
        poly = self.zones[zone_id]
        coords = np.array(poly.exterior.coords[:-1])  # Exclude duplicate last point
        
        # Scale to image dimensions
        coords[:, 0] *= width
        coords[:, 1] *= height
        
        return coords.astype(np.int32)


class ProximityCalculator:
    """Calculates proximity metrics between tracks"""
    
    @staticmethod
    def center_distance_normalized(bbox1: BBox, bbox2: BBox) -> float:
        """
        Normalized center distance based on mean person height
        Returns distance normalized by average height
        """
        c1 = bbox1.center
        c2 = bbox2.center
        
        # Euclidean distance between centers
        dist = np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
        
        # Normalize by mean height
        mean_height = (bbox1.height + bbox2.height) / 2.0
        if mean_height < 1e-6:
            return float('inf')
        
        return dist / mean_height
    
    @staticmethod
    def bbox_iou(bbox1: BBox, bbox2: BBox) -> float:
        """Calculate IoU between two bboxes"""
        # Intersection
        x1 = max(bbox1.x1, bbox2.x1)
        y1 = max(bbox1.y1, bbox2.y1)
        x2 = min(bbox1.x2, bbox2.x2)
        y2 = min(bbox1.y2, bbox2.y2)
        
        inter_w = max(0.0, x2 - x1)
        inter_h = max(0.0, y2 - y1)
        inter_area = inter_w * inter_h
        
        # Union
        union_area = bbox1.area + bbox2.area - inter_area
        
        if union_area < 1e-9:
            return 0.0
        
        return inter_area / union_area
    
    @staticmethod
    def are_in_contact(bbox1: BBox, bbox2: BBox, 
                      center_dist_scale: float = 0.35,
                      iou_min: float = 0.03) -> Tuple[bool, float, float]:
        """
        Determine if two people are in contact
        Returns: (in_contact, center_distance_norm, iou)
        """
        center_dist = ProximityCalculator.center_distance_normalized(bbox1, bbox2)
        iou = ProximityCalculator.bbox_iou(bbox1, bbox2)
        
        # Contact if either condition met
        in_contact = (center_dist <= center_dist_scale) or (iou >= iou_min)
        
        return in_contact, center_dist, iou
    
    @staticmethod
    def estimate_real_world_distance(bbox1: BBox, bbox2: BBox,
                                    pixels_per_meter: float = 100.0) -> float:
        """
        Estimate real-world distance between people
        Assumes approximate calibration
        """
        c1 = bbox1.center
        c2 = bbox2.center
        
        pixel_dist = np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
        return pixel_dist / pixels_per_meter


class JitterFilter:
    """Filters jitter in track positions using Savitzky-Golay filter"""
    
    def __init__(self, window_size: int = 5, poly_order: int = 2):
        self.window_size = window_size
        self.poly_order = poly_order
        self.history: Dict[int, List[Tuple[float, float]]] = {}
        
    def add_position(self, track_id: int, position: Tuple[float, float]):
        """Add new position for track"""
        if track_id not in self.history:
            self.history[track_id] = []
        
        self.history[track_id].append(position)
        
        # Keep only recent history
        if len(self.history[track_id]) > self.window_size * 2:
            self.history[track_id] = self.history[track_id][-self.window_size * 2:]
    
    def get_smoothed_position(self, track_id: int) -> Optional[Tuple[float, float]]:
        """Get smoothed position using Savitzky-Golay filter"""
        if track_id not in self.history:
            return None
        
        positions = self.history[track_id]
        
        if len(positions) < self.window_size:
            # Not enough data, return latest
            return positions[-1] if positions else None
        
        # Apply Savitzky-Golay filter
        x_coords = [p[0] for p in positions[-self.window_size:]]
        y_coords = [p[1] for p in positions[-self.window_size:]]
        
        try:
            x_smooth = savgol_filter(x_coords, self.window_size, self.poly_order)
            y_smooth = savgol_filter(y_coords, self.window_size, self.poly_order)
            
            return (float(x_smooth[-1]), float(y_smooth[-1]))
        except:
            # Fallback to last position if filter fails
            return positions[-1]
    
    def clear_track(self, track_id: int):
        """Remove track history"""
        if track_id in self.history:
            del self.history[track_id]


class KalmanTracker:
    """Simple Kalman filter for position tracking"""
    
    def __init__(self):
        self.trackers: Dict[int, cv2.KalmanFilter] = {}
    
    def update(self, track_id: int, position: Tuple[float, float]) -> Tuple[float, float]:
        """Update Kalman filter and return filtered position"""
        if track_id not in self.trackers:
            # Initialize new Kalman filter
            kf = cv2.KalmanFilter(4, 2)  # 4 state vars (x, y, vx, vy), 2 measurements (x, y)
            kf.measurementMatrix = np.array([[1, 0, 0, 0],
                                            [0, 1, 0, 0]], dtype=np.float32)
            kf.transitionMatrix = np.array([[1, 0, 1, 0],
                                           [0, 1, 0, 1],
                                           [0, 0, 1, 0],
                                           [0, 0, 0, 1]], dtype=np.float32)
            kf.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03
            
            # Initialize state
            kf.statePre = np.array([[position[0]], [position[1]], [0], [0]], dtype=np.float32)
            kf.statePost = np.array([[position[0]], [position[1]], [0], [0]], dtype=np.float32)
            
            self.trackers[track_id] = kf
        
        kf = self.trackers[track_id]
        
        # Predict
        kf.predict()
        
        # Correct with measurement
        measurement = np.array([[position[0]], [position[1]]], dtype=np.float32)
        kf.correct(measurement)
        
        # Return corrected position
        state = kf.statePost
        return (float(state[0][0]), float(state[1][0]))
    
    def predict(self, track_id: int) -> Optional[Tuple[float, float]]:
        """Get predicted position without measurement"""
        if track_id not in self.trackers:
            return None
        
        kf = self.trackers[track_id]
        prediction = kf.predict()
        
        return (float(prediction[0][0]), float(prediction[1][0]))
    
    def remove_tracker(self, track_id: int):
        """Remove tracker"""
        if track_id in self.trackers:
            del self.trackers[track_id]


def visualize_zones(frame: np.ndarray, zone_manager: ZoneManager, 
                   zone_ids: List[str], colors: Dict[str, Tuple[int, int, int]] = None) -> np.ndarray:
    """Draw zones on frame"""
    height, width = frame.shape[:2]
    overlay = frame.copy()
    
    if colors is None:
        colors = {
            'gate_A1': (0, 255, 0),  # Green for gate area
            'guard_anchor_A1': (255, 0, 0)  # Blue for guard anchor
        }
    
    for zone_id in zone_ids:
        if zone_id not in zone_manager.zones:
            continue
        
        # Get denormalized polygon
        poly_coords = zone_manager.denormalize_polygon(zone_id, width, height)
        
        if len(poly_coords) == 0:
            continue
        
        # Draw filled polygon with transparency
        color = colors.get(zone_id, (128, 128, 128))
        cv2.fillPoly(overlay, [poly_coords], color)
        
        # Draw boundary
        cv2.polylines(frame, [poly_coords], True, color, 2)
    
    # Blend overlay with original frame
    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
    
    return frame

