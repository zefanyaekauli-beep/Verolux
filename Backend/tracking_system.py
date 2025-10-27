#!/usr/bin/env python3
"""
Tracking System for Gate Security
Implements ByteTrack-style tracking with Re-ID and track management
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import time
import cv2


@dataclass
class Track:
    """Represents a tracked person"""
    track_id: int
    bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2 (normalized)
    confidence: float
    class_name: str
    
    # Tracking state
    age: int = 0  # Frames since creation
    hits: int = 1  # Number of successful matches
    time_since_update: int = 0  # Frames since last update
    
    # Track history
    bbox_history: deque = field(default_factory=lambda: deque(maxlen=30))
    position_history: deque = field(default_factory=lambda: deque(maxlen=30))
    velocity_history: deque = field(default_factory=lambda: deque(maxlen=10))
    
    # Timestamps
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    
    # Features for Re-ID (optional)
    appearance_feature: Optional[np.ndarray] = None
    
    # State flags
    is_confirmed: bool = False
    is_deleted: bool = False
    
    def __post_init__(self):
        self.bbox_history.append(self.bbox)
        center = self.center
        self.position_history.append(center)
    
    @property
    def center(self) -> Tuple[float, float]:
        """Get bbox center"""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
    
    @property
    def width(self) -> float:
        return self.bbox[2] - self.bbox[0]
    
    @property
    def height(self) -> float:
        return self.bbox[3] - self.bbox[1]
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    @property
    def velocity(self) -> Optional[Tuple[float, float]]:
        """Estimate velocity from position history"""
        if len(self.position_history) < 2:
            return None
        
        # Average velocity over last few frames
        recent = list(self.position_history)[-5:]
        if len(recent) < 2:
            return None
        
        vx = (recent[-1][0] - recent[0][0]) / len(recent)
        vy = (recent[-1][1] - recent[0][1]) / len(recent)
        
        return (vx, vy)
    
    def update(self, bbox: Tuple[float, float, float, float], confidence: float):
        """Update track with new detection"""
        self.bbox = bbox
        self.confidence = confidence
        self.time_since_update = 0
        self.hits += 1
        self.last_seen = time.time()
        
        # Update history
        self.bbox_history.append(bbox)
        center = self.center
        self.position_history.append(center)
        
        # Update velocity
        vel = self.velocity
        if vel is not None:
            self.velocity_history.append(vel)
        
        # Confirm track after sufficient hits
        if self.hits >= 3:
            self.is_confirmed = True
    
    def predict(self) -> Tuple[float, float, float, float]:
        """Predict next bbox position using velocity"""
        if len(self.position_history) < 2:
            return self.bbox
        
        vel = self.velocity
        if vel is None:
            return self.bbox
        
        # Predict center
        cx, cy = self.center
        pred_cx = cx + vel[0]
        pred_cy = cy + vel[1]
        
        # Reconstruct bbox
        w, h = self.width, self.height
        x1 = pred_cx - w / 2.0
        y1 = pred_cy - h / 2.0
        x2 = pred_cx + w / 2.0
        y2 = pred_cy + h / 2.0
        
        return (x1, y1, x2, y2)
    
    def mark_missed(self):
        """Mark track as not matched this frame"""
        self.time_since_update += 1
        self.age += 1
        
        # Mark for deletion if not updated for too long
        if self.time_since_update > 30:  # ~1 second at 30fps
            self.is_deleted = True
    
    def increment_age(self):
        """Increment track age"""
        self.age += 1


class SimpleTracker:
    """
    Simplified ByteTrack-style tracker
    Uses IoU + center distance for matching
    """
    
    def __init__(self, 
                 max_age: int = 30,
                 min_hits: int = 3,
                 iou_threshold: float = 0.3,
                 distance_threshold: float = 0.5):
        """
        Args:
            max_age: Maximum frames to keep track without updates
            min_hits: Minimum hits to confirm track
            iou_threshold: IoU threshold for matching
            distance_threshold: Normalized distance threshold
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.distance_threshold = distance_threshold
        
        self.tracks: List[Track] = []
        self.next_id = 1
        self.frame_count = 0
    
    def update(self, detections: List[Dict[str, Any]]) -> List[Track]:
        """
        Update tracker with new detections
        
        Args:
            detections: List of detection dicts with keys: 'bbox', 'conf', 'cls'
                       bbox should be normalized [x1, y1, x2, y2]
        
        Returns:
            List of active confirmed tracks
        """
        self.frame_count += 1
        
        # Separate high and low confidence detections (ByteTrack approach)
        high_conf_dets = [d for d in detections if d['conf'] >= 0.5]
        low_conf_dets = [d for d in detections if 0.2 <= d['conf'] < 0.5]
        
        # First association: high confidence detections with tracks
        matched, unmatched_tracks, unmatched_dets = self._associate(
            self.tracks, high_conf_dets, self.iou_threshold
        )
        
        # Update matched tracks
        for track_idx, det_idx in matched:
            track = self.tracks[track_idx]
            det = high_conf_dets[det_idx]
            track.update(tuple(det['bbox']), det['conf'])
        
        # Second association: unmatched tracks with low confidence detections
        unmatched_track_objects = [self.tracks[i] for i in unmatched_tracks]
        matched_low, unmatched_tracks_low, _ = self._associate(
            unmatched_track_objects, low_conf_dets, 
            iou_threshold=0.4  # Lower threshold for low conf
        )
        
        # Update tracks matched with low confidence
        for track_idx, det_idx in matched_low:
            track = unmatched_track_objects[track_idx]
            det = low_conf_dets[det_idx]
            track.update(tuple(det['bbox']), det['conf'])
        
        # Mark unmatched tracks as missed
        final_unmatched_track_indices = set(unmatched_tracks)
        for idx in matched_low:
            track_idx, _ = idx
            original_idx = unmatched_tracks[track_idx]
            final_unmatched_track_indices.discard(original_idx)
        
        for idx in final_unmatched_track_indices:
            self.tracks[idx].mark_missed()
        
        # Create new tracks for unmatched high-confidence detections
        for det_idx in unmatched_dets:
            det = high_conf_dets[det_idx]
            new_track = Track(
                track_id=self.next_id,
                bbox=tuple(det['bbox']),
                confidence=det['conf'],
                class_name=det['cls']
            )
            self.tracks.append(new_track)
            self.next_id += 1
        
        # Remove deleted tracks
        self.tracks = [t for t in self.tracks if not t.is_deleted]
        
        # Increment age for all tracks
        for track in self.tracks:
            if track.time_since_update == 0:  # Just updated
                track.increment_age()
        
        # Return confirmed tracks
        return [t for t in self.tracks if t.is_confirmed and not t.is_deleted]
    
    def _associate(self, tracks: List[Track], detections: List[Dict], 
                   iou_threshold: float) -> Tuple[List, List, List]:
        """
        Associate tracks with detections using Hungarian algorithm (greedy version)
        
        Returns:
            matched: List of (track_idx, det_idx) tuples
            unmatched_tracks: List of track indices
            unmatched_dets: List of detection indices
        """
        if len(tracks) == 0:
            return [], [], list(range(len(detections)))
        
        if len(detections) == 0:
            return [], list(range(len(tracks))), []
        
        # Compute cost matrix (1 - IoU)
        cost_matrix = np.zeros((len(tracks), len(detections)))
        
        for t_idx, track in enumerate(tracks):
            # Use predicted position for track
            pred_bbox = track.predict()
            
            for d_idx, det in enumerate(detections):
                det_bbox = det['bbox']
                
                # Compute IoU
                iou = self._compute_iou(pred_bbox, det_bbox)
                
                # Compute center distance
                center_dist = self._compute_center_distance(pred_bbox, det_bbox)
                
                # Combined cost (lower is better)
                # Use IoU primarily, center distance as tie-breaker
                cost = 1.0 - iou + center_dist * 0.1
                
                cost_matrix[t_idx, d_idx] = cost
        
        # Greedy matching (simplified Hungarian)
        matched = []
        matched_tracks = set()
        matched_dets = set()
        
        # Sort by cost
        matches = []
        for t_idx in range(len(tracks)):
            for d_idx in range(len(detections)):
                iou = 1.0 - cost_matrix[t_idx, d_idx] + \
                      self._compute_center_distance(tracks[t_idx].predict(), 
                                                    detections[d_idx]['bbox']) * 0.1
                matches.append((cost_matrix[t_idx, d_idx], t_idx, d_idx, iou))
        
        matches.sort(key=lambda x: x[0])
        
        # Greedy assignment
        for cost, t_idx, d_idx, effective_iou in matches:
            if t_idx in matched_tracks or d_idx in matched_dets:
                continue
            
            # Check if IoU is above threshold
            iou = self._compute_iou(tracks[t_idx].predict(), 
                                   detections[d_idx]['bbox'])
            
            if iou >= iou_threshold:
                matched.append((t_idx, d_idx))
                matched_tracks.add(t_idx)
                matched_dets.add(d_idx)
        
        unmatched_tracks = [i for i in range(len(tracks)) if i not in matched_tracks]
        unmatched_dets = [i for i in range(len(detections)) if i not in matched_dets]
        
        return matched, unmatched_tracks, unmatched_dets
    
    @staticmethod
    def _compute_iou(bbox1: Tuple[float, float, float, float], 
                     bbox2: Tuple[float, float, float, float]) -> float:
        """Compute IoU between two bboxes"""
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        
        inter_w = max(0.0, x2 - x1)
        inter_h = max(0.0, y2 - y1)
        inter_area = inter_w * inter_h
        
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        union_area = area1 + area2 - inter_area
        
        if union_area < 1e-9:
            return 0.0
        
        return inter_area / union_area
    
    @staticmethod
    def _compute_center_distance(bbox1: Tuple[float, float, float, float],
                                bbox2: Tuple[float, float, float, float]) -> float:
        """Compute normalized center distance"""
        c1x = (bbox1[0] + bbox1[2]) / 2.0
        c1y = (bbox1[1] + bbox1[3]) / 2.0
        c2x = (bbox2[0] + bbox2[2]) / 2.0
        c2y = (bbox2[1] + bbox2[3]) / 2.0
        
        dist = np.sqrt((c1x - c2x)**2 + (c1y - c2y)**2)
        
        # Normalize by bbox size
        h1 = bbox1[3] - bbox1[1]
        h2 = bbox2[3] - bbox2[1]
        mean_h = (h1 + h2) / 2.0
        
        if mean_h < 1e-6:
            return float('inf')
        
        return dist / mean_h
    
    def get_track(self, track_id: int) -> Optional[Track]:
        """Get track by ID"""
        for track in self.tracks:
            if track.track_id == track_id:
                return track
        return None
    
    def reset(self):
        """Reset tracker"""
        self.tracks = []
        self.next_id = 1
        self.frame_count = 0


def visualize_tracks(frame: np.ndarray, tracks: List[Track], 
                    width: int, height: int,
                    show_id: bool = True, show_velocity: bool = False) -> np.ndarray:
    """Draw tracks on frame"""
    output = frame.copy()
    
    for track in tracks:
        if not track.is_confirmed:
            continue
        
        # Denormalize bbox
        x1 = int(track.bbox[0] * width)
        y1 = int(track.bbox[1] * height)
        x2 = int(track.bbox[2] * width)
        y2 = int(track.bbox[3] * height)
        
        # Choose color based on track ID
        color = (
            int((track.track_id * 50) % 255),
            int((track.track_id * 100) % 255),
            int((track.track_id * 150) % 255)
        )
        
        # Draw bbox
        cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
        
        # Draw ID
        if show_id:
            label = f"ID:{track.track_id}"
            cv2.putText(output, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw velocity vector
        if show_velocity and track.velocity is not None:
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)
            vx, vy = track.velocity
            
            # Scale velocity for visualization
            end_x = int(cx + vx * width * 10)
            end_y = int(cy + vy * height * 10)
            
            cv2.arrowedLine(output, (cx, cy), (end_x, end_y), 
                          (0, 255, 0), 2, tipLength=0.3)
        
        # Draw track history
        if len(track.position_history) > 1:
            points = []
            for pos in track.position_history:
                px = int(pos[0] * width)
                py = int(pos[1] * height)
                points.append((px, py))
            
            # Draw trail
            for i in range(1, len(points)):
                cv2.line(output, points[i-1], points[i], color, 1)
    
    return output

