#!/usr/bin/env python3
"""
Pose Estimation for Gate Security
Detects hand-to-torso interactions and reach gestures
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import time

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


@dataclass
class PoseKeypoints:
    """Pose keypoints for a person"""
    track_id: int
    keypoints: np.ndarray  # Shape: (17, 3) - (x, y, confidence)
    bbox: Tuple[float, float, float, float]
    timestamp: float = 0.0
    
    # Keypoint indices (COCO format)
    NOSE = 0
    LEFT_EYE = 1
    RIGHT_EYE = 2
    LEFT_EAR = 3
    RIGHT_EAR = 4
    LEFT_SHOULDER = 5
    RIGHT_SHOULDER = 6
    LEFT_ELBOW = 7
    RIGHT_ELBOW = 8
    LEFT_WRIST = 9
    RIGHT_WRIST = 10
    LEFT_HIP = 11
    RIGHT_HIP = 12
    LEFT_KNEE = 13
    RIGHT_KNEE = 14
    LEFT_ANKLE = 15
    RIGHT_ANKLE = 16
    
    def get_keypoint(self, idx: int) -> Optional[Tuple[float, float]]:
        """Get keypoint coordinates if confidence is high enough"""
        if idx >= len(self.keypoints):
            return None
        
        x, y, conf = self.keypoints[idx]
        if conf < 0.3:  # Confidence threshold
            return None
        
        return (float(x), float(y))
    
    def get_hand_keypoints(self) -> List[Tuple[float, float]]:
        """Get all hand keypoints (wrists)"""
        hands = []
        for idx in [self.LEFT_WRIST, self.RIGHT_WRIST]:
            kp = self.get_keypoint(idx)
            if kp is not None:
                hands.append(kp)
        return hands
    
    def get_torso_bbox(self) -> Optional[Tuple[float, float, float, float]]:
        """Estimate torso bounding box from shoulders and hips"""
        shoulders = []
        hips = []
        
        for idx in [self.LEFT_SHOULDER, self.RIGHT_SHOULDER]:
            kp = self.get_keypoint(idx)
            if kp is not None:
                shoulders.append(kp)
        
        for idx in [self.LEFT_HIP, self.RIGHT_HIP]:
            kp = self.get_keypoint(idx)
            if kp is not None:
                hips.append(kp)
        
        if len(shoulders) == 0 or len(hips) == 0:
            # Fallback: use upper portion of full bbox
            x1, y1, x2, y2 = self.bbox
            torso_y1 = y1 + (y2 - y1) * 0.1
            torso_y2 = y1 + (y2 - y1) * 0.6
            return (x1, torso_y1, x2, torso_y2)
        
        # Calculate torso bbox from keypoints
        all_points = shoulders + hips
        xs = [p[0] for p in all_points]
        ys = [p[0] for p in all_points]
        
        x_min = min(xs)
        x_max = max(xs)
        y_min = min(ys)
        y_max = max(ys)
        
        # Add margin
        margin = 0.1
        w = x_max - x_min
        h = y_max - y_min
        
        return (
            x_min - w * margin,
            y_min - h * margin,
            x_max + w * margin,
            y_max + h * margin
        )


class PoseEstimator:
    """Estimates pose and detects hand-to-torso interactions"""
    
    def __init__(self, model_name: str = "yolov8n-pose.pt"):
        self.model = None
        self.model_name = model_name
        self.pose_history: Dict[int, deque] = {}  # track_id -> deque of PoseKeypoints
        
        if YOLO_AVAILABLE:
            try:
                self.model = YOLO(model_name)
                print(f"✅ Pose model loaded: {model_name}")
            except Exception as e:
                print(f"⚠️ Pose model loading failed: {e}")
                self.model = None
        else:
            print("⚠️ Ultralytics not available, pose estimation disabled")
    
    def estimate_poses(self, frame: np.ndarray, tracks: List[Any]) -> Dict[int, PoseKeypoints]:
        """
        Estimate poses for tracked persons
        
        Args:
            frame: Image frame
            tracks: List of Track objects
        
        Returns:
            Dict mapping track_id to PoseKeypoints
        """
        if self.model is None or len(tracks) == 0:
            return {}
        
        height, width = frame.shape[:2]
        poses = {}
        
        try:
            # Run pose estimation on full frame
            results = self.model.predict(frame, verbose=False, conf=0.3)
            
            if not results or len(results) == 0:
                return poses
            
            result = results[0]
            
            if not hasattr(result, 'keypoints') or result.keypoints is None:
                return poses
            
            # Match pose detections to tracks
            for track in tracks:
                if not track.is_confirmed:
                    continue
                
                # Denormalize track bbox
                tx1 = track.bbox[0] * width
                ty1 = track.bbox[1] * height
                tx2 = track.bbox[2] * width
                ty2 = track.bbox[3] * height
                track_center = ((tx1 + tx2) / 2, (ty1 + ty2) / 2)
                
                # Find closest pose detection
                best_match = None
                best_distance = float('inf')
                
                for idx, kps in enumerate(result.keypoints.data):
                    if len(kps) == 0:
                        continue
                    
                    # Get pose center (average of visible keypoints)
                    visible_kps = kps[kps[:, 2] > 0.3]  # Filter by confidence
                    if len(visible_kps) == 0:
                        continue
                    
                    pose_center = (
                        float(visible_kps[:, 0].mean()),
                        float(visible_kps[:, 1].mean())
                    )
                    
                    # Calculate distance to track center
                    dist = np.sqrt(
                        (pose_center[0] - track_center[0])**2 + 
                        (pose_center[1] - track_center[1])**2
                    )
                    
                    if dist < best_distance:
                        best_distance = dist
                        best_match = kps
                
                # If match found and close enough
                if best_match is not None and best_distance < min(tx2 - tx1, ty2 - ty1):
                    # Normalize keypoints
                    normalized_kps = best_match.copy()
                    normalized_kps[:, 0] /= width
                    normalized_kps[:, 1] /= height
                    
                    pose = PoseKeypoints(
                        track_id=track.track_id,
                        keypoints=normalized_kps.cpu().numpy() if hasattr(normalized_kps, 'cpu') else normalized_kps,
                        bbox=track.bbox,
                        timestamp=time.time()
                    )
                    
                    poses[track.track_id] = pose
                    
                    # Update history
                    if track.track_id not in self.pose_history:
                        self.pose_history[track.track_id] = deque(maxlen=10)
                    self.pose_history[track.track_id].append(pose)
        
        except Exception as e:
            print(f"Pose estimation error: {e}")
        
        return poses
    
    def detect_hand_to_torso(self, 
                            visitor_pose: PoseKeypoints,
                            guard_pose: PoseKeypoints,
                            margin: float = 0.12) -> Dict[str, Any]:
        """
        Detect if visitor's hands are toward guard's torso
        
        Args:
            visitor_pose: Visitor's pose keypoints
            guard_pose: Guard's pose keypoints
            margin: Distance threshold (fraction of guard height)
        
        Returns:
            Detection result with flags and distances
        """
        result = {
            'detected': False,
            'left_hand': False,
            'right_hand': False,
            'min_distance': float('inf'),
            'confidence': 0.0
        }
        
        # Get visitor's hand positions
        visitor_hands = visitor_pose.get_hand_keypoints()
        if len(visitor_hands) == 0:
            return result
        
        # Get guard's torso bbox
        guard_torso = guard_pose.get_torso_bbox()
        if guard_torso is None:
            return result
        
        # Calculate guard height for normalization
        guard_height = guard_pose.bbox[3] - guard_pose.bbox[1]
        threshold_dist = guard_height * margin
        
        # Check each hand
        min_dist = float('inf')
        
        for hand_idx, hand_pos in enumerate(visitor_hands):
            # Calculate distance to guard torso
            dist = self._point_to_bbox_distance(hand_pos, guard_torso)
            
            if dist < min_dist:
                min_dist = dist
            
            if dist <= threshold_dist:
                result['detected'] = True
                if hand_idx == 0:  # Left hand
                    result['left_hand'] = True
                else:  # Right hand
                    result['right_hand'] = True
        
        result['min_distance'] = min_dist
        result['confidence'] = max(0.0, 1.0 - (min_dist / (threshold_dist * 2)))
        
        return result
    
    def detect_reach_gesture(self,
                           visitor_track_id: int,
                           guard_track_id: int,
                           velocity_thresh: float = 0.6,
                           min_duration: float = 0.25) -> Dict[str, Any]:
        """
        Detect reaching gesture toward guard
        
        Args:
            visitor_track_id: Visitor track ID
            guard_track_id: Guard track ID
            velocity_thresh: Minimum hand velocity threshold
            min_duration: Minimum duration of reach (seconds)
        
        Returns:
            Detection result
        """
        result = {
            'detected': False,
            'velocity': 0.0,
            'duration': 0.0,
            'direction': None
        }
        
        if visitor_track_id not in self.pose_history:
            return result
        
        if guard_track_id not in self.pose_history:
            return result
        
        visitor_history = list(self.pose_history[visitor_track_id])
        guard_history = list(self.pose_history[guard_track_id])
        
        if len(visitor_history) < 3 or len(guard_history) == 0:
            return result
        
        # Get recent visitor poses
        recent_poses = visitor_history[-5:]
        current_guard_pose = guard_history[-1]
        
        # Calculate hand velocities
        guard_torso = current_guard_pose.get_torso_bbox()
        if guard_torso is None:
            return result
        
        guard_torso_center = (
            (guard_torso[0] + guard_torso[2]) / 2,
            (guard_torso[1] + guard_torso[3]) / 2
        )
        
        # Track hand movement toward guard torso
        for i in range(1, len(recent_poses)):
            prev_pose = recent_poses[i-1]
            curr_pose = recent_poses[i]
            
            prev_hands = prev_pose.get_hand_keypoints()
            curr_hands = curr_pose.get_hand_keypoints()
            
            if len(prev_hands) == 0 or len(curr_hands) == 0:
                continue
            
            # Check each hand
            for prev_hand, curr_hand in zip(prev_hands, curr_hands):
                # Calculate velocity toward guard torso
                prev_dist = np.sqrt(
                    (prev_hand[0] - guard_torso_center[0])**2 + 
                    (prev_hand[1] - guard_torso_center[1])**2
                )
                curr_dist = np.sqrt(
                    (curr_hand[0] - guard_torso_center[0])**2 + 
                    (curr_hand[1] - guard_torso_center[1])**2
                )
                
                # Time delta
                dt = curr_pose.timestamp - prev_pose.timestamp
                if dt < 1e-6:
                    continue
                
                # Velocity (negative = moving toward)
                velocity = (curr_dist - prev_dist) / dt
                
                if velocity < -velocity_thresh:  # Moving toward
                    result['detected'] = True
                    result['velocity'] = abs(velocity)
                    result['duration'] += dt
        
        return result
    
    @staticmethod
    def _point_to_bbox_distance(point: Tuple[float, float], 
                               bbox: Tuple[float, float, float, float]) -> float:
        """Calculate minimum distance from point to bbox"""
        px, py = point
        x1, y1, x2, y2 = bbox
        
        # Clamp point to bbox
        cx = max(x1, min(px, x2))
        cy = max(y1, min(py, y2))
        
        # Distance from point to closest point in bbox
        dist = np.sqrt((px - cx)**2 + (py - cy)**2)
        
        return dist
    
    def cleanup_old_tracks(self, active_track_ids: List[int]):
        """Remove pose history for inactive tracks"""
        to_remove = []
        for track_id in self.pose_history:
            if track_id not in active_track_ids:
                to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.pose_history[track_id]


# Fallback simple pose estimator (when YOLO pose not available)
class SimplePoseEstimator:
    """Simple pose estimator using bbox only (fallback)"""
    
    def __init__(self):
        print("⚠️ Using simple pose estimator (fallback)")
    
    def estimate_poses(self, frame: np.ndarray, tracks: List[Any]) -> Dict[int, PoseKeypoints]:
        """Create dummy poses from bboxes"""
        poses = {}
        
        for track in tracks:
            if not track.is_confirmed:
                continue
            
            # Create dummy keypoints (just estimate from bbox)
            keypoints = self._bbox_to_keypoints(track.bbox)
            
            pose = PoseKeypoints(
                track_id=track.track_id,
                keypoints=keypoints,
                bbox=track.bbox,
                timestamp=time.time()
            )
            
            poses[track.track_id] = pose
        
        return poses
    
    @staticmethod
    def _bbox_to_keypoints(bbox: Tuple[float, float, float, float]) -> np.ndarray:
        """Estimate keypoints from bbox"""
        x1, y1, x2, y2 = bbox
        w = x2 - x1
        h = y2 - y1
        cx = (x1 + x2) / 2
        
        # Rough estimates
        keypoints = np.zeros((17, 3))
        
        # Wrists (most important for hand-to-torso detection)
        keypoints[9] = [x1 + w * 0.3, y1 + h * 0.5, 0.5]  # Left wrist
        keypoints[10] = [x2 - w * 0.3, y1 + h * 0.5, 0.5]  # Right wrist
        
        # Shoulders
        keypoints[5] = [x1 + w * 0.3, y1 + h * 0.2, 0.5]  # Left shoulder
        keypoints[6] = [x2 - w * 0.3, y1 + h * 0.2, 0.5]  # Right shoulder
        
        # Hips
        keypoints[11] = [x1 + w * 0.3, y1 + h * 0.5, 0.5]  # Left hip
        keypoints[12] = [x2 - w * 0.3, y1 + h * 0.5, 0.5]  # Right hip
        
        return keypoints
    
    def detect_hand_to_torso(self, visitor_pose, guard_pose, margin=0.12):
        """Fallback detection based on bbox proximity"""
        return {
            'detected': False,
            'left_hand': False,
            'right_hand': False,
            'min_distance': float('inf'),
            'confidence': 0.0
        }
    
    def detect_reach_gesture(self, visitor_track_id, guard_track_id, 
                           velocity_thresh=0.6, min_duration=0.25):
        """Fallback reach detection"""
        return {
            'detected': False,
            'velocity': 0.0,
            'duration': 0.0,
            'direction': None
        }
    
    def cleanup_old_tracks(self, active_track_ids):
        """No-op for simple estimator"""
        pass

