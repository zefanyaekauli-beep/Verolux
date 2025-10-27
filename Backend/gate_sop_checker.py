#!/usr/bin/env python3
"""
Gate SOP Checker - Main Orchestration
3-Layer Pipeline: Perception → Event → Decision
High precision with deterministic & explainable decisions
"""

import os
import json
import time
import numpy as np
import cv2
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Import all components
from zone_utils import ZoneManager, BBox, ProximityCalculator, JitterFilter, visualize_zones
from tracking_system import SimpleTracker, Track, visualize_tracks
from pose_estimator import PoseEstimator, SimplePoseEstimator, PoseKeypoints
from event_system import EventLogger, EventType, SessionManager
from fsm_decision import DecisionEngine, CheckState
from gate_database import GateSecurityDatabase
from incident_report_generator import MultiLanguageIncidentReportGenerator


class GateChecker:
    """
    Main gate security checker
    Implements 3-layer pipeline with FSM-based decision making
    """
    
    def __init__(self, config_path: str = "config/gate_rules.demo.json"):
        """Initialize gate checker with configuration"""
        print("🚀 Initializing Gate Security Checker")
        print("=" * 60)
        
        # Load configuration
        self.config = self._load_config(config_path)
        self.gate_id = self.config.get('gate_id', 'unknown')
        
        print(f"Gate ID: {self.gate_id}")
        
        # Initialize components
        config_dir = os.path.dirname(config_path)
        
        # Zone management
        print("📐 Loading zones...")
        self.zone_manager = ZoneManager(config_dir)
        self._load_zones()
        
        # Tracking system
        print("🎯 Initializing tracker...")
        self.tracker = SimpleTracker(
            max_age=30,
            min_hits=3,
            iou_threshold=0.3,
            distance_threshold=0.5
        )
        
        # Pose estimation
        print("🦴 Initializing pose estimator...")
        if self.config.get('pose', {}).get('use_pose', True):
            try:
                self.pose_estimator = PoseEstimator("yolov8n-pose.pt")
            except:
                print("⚠️ Falling back to simple pose estimator")
                self.pose_estimator = SimplePoseEstimator()
        else:
            self.pose_estimator = SimplePoseEstimator()
        
        # Event logging
        print("📝 Initializing event logger...")
        self.event_logger = EventLogger(max_history=2000)
        self.session_manager = SessionManager()
        
        # Decision engine (FSM)
        print("🤖 Initializing decision engine...")
        self.decision_engine = DecisionEngine(self.config)
        
        # Database
        print("💾 Initializing database...")
        db_path = self.config.get('database', {}).get('path', 'gate_security.db')
        self.database = GateSecurityDatabase(db_path)
        
        # Incident report generator
        print("📋 Initializing multi-language incident report generator...")
        self.incident_generator = MultiLanguageIncidentReportGenerator(db_path)
        
        # Jitter filtering
        print("🔧 Initializing filters...")
        jitter_window = self.config.get('noise_filtering', {}).get('jitter_smooth_window', 5)
        self.jitter_filter = JitterFilter(window_size=jitter_window)
        
        # Proximity calculator
        self.proximity_calc = ProximityCalculator()
        
        # Snapshots
        self.snapshots_dir = self.config.get('visualization', {}).get('snapshot_dir', 'snapshots')
        os.makedirs(self.snapshots_dir, exist_ok=True)
        
        # State
        self.frame_count = 0
        self.last_frame_time = time.time()
        
        print("✅ Gate Checker initialized successfully")
        print("=" * 60)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _load_zones(self):
        """Load zone polygons"""
        zones_config = self.config.get('zones', {})
        
        # Load gate area
        if 'gate_area' in zones_config:
            gate_file = zones_config['gate_area']
            self.zone_manager.load_zone(gate_file)
            print(f"  ✓ Loaded gate area: {gate_file}")
        
        # Load guard anchor
        if 'guard_anchor' in zones_config:
            anchor_file = zones_config['guard_anchor']
            self.zone_manager.load_zone(anchor_file)
            print(f"  ✓ Loaded guard anchor: {anchor_file}")
    
    def update(self, frame: np.ndarray, detections: List[Dict[str, Any]], 
               dt: float = None) -> Dict[str, Any]:
        """
        Main update loop - processes one frame
        
        Args:
            frame: BGR image frame
            detections: List of detections with 'bbox' (normalized), 'conf', 'cls'
            dt: Time delta since last frame (auto-calculated if None)
        
        Returns:
            Results dict with decisions, events, and visualizations
        """
        if dt is None:
            current_time = time.time()
            dt = current_time - self.last_frame_time
            self.last_frame_time = current_time
        
        dt = max(0.001, min(dt, 1.0))  # Clamp dt to reasonable range
        
        self.frame_count += 1
        height, width = frame.shape[:2]
        
        # === LAYER 1: PERCEPTION ===
        perception = self._perception_layer(frame, detections, width, height, dt)
        
        # === LAYER 2: EVENTS ===
        events = self._event_layer(perception, dt)
        
        # === LAYER 3: DECISIONS ===
        decisions = self._decision_layer(perception, events, dt)
        
        # Visualize if enabled
        vis_frame = None
        if self.config.get('visualization', {}).get('draw_zones', True):
            vis_frame = self._visualize(frame, perception, decisions)
        
        # Cleanup
        self._cleanup_old_states(perception['tracks'])
        
        return {
            'frame_count': self.frame_count,
            'timestamp': time.time(),
            'perception': perception,
            'events': events,
            'decisions': decisions,
            'visualization': vis_frame,
            'stats': self._get_stats()
        }
    
    def _perception_layer(self, frame: np.ndarray, detections: List[Dict], 
                         width: int, height: int, dt: float) -> Dict[str, Any]:
        """
        Layer 1: Perception
        Processes detections → tracks → zones → pose → proximity
        """
        # Filter detections by class and size
        filtered_dets = self._filter_detections(detections, height)
        
        # Update tracker
        tracks = self.tracker.update(filtered_dets)
        
        # Estimate poses
        poses = self.pose_estimator.estimate_poses(frame, tracks)
        
        # Analyze zones and proximity
        track_analysis = self._analyze_tracks(tracks, poses, width, height, dt)
        
        return {
            'tracks': tracks,
            'poses': poses,
            'track_analysis': track_analysis,
            'frame_shape': (width, height)
        }
    
    def _filter_detections(self, detections: List[Dict], frame_height: int) -> List[Dict]:
        """Filter detections by class and minimum size"""
        min_height_px = self.config.get('noise_filtering', {}).get('min_box_height_px', 40)
        min_height_norm = min_height_px / frame_height
        
        person_classes = self.config.get('classes', {}).get('person', [0])
        
        filtered = []
        for det in detections:
            # Check class
            cls_id = det.get('cls_id', 0)
            if cls_id not in person_classes:
                continue
            
            # Check size
            bbox = det['bbox']
            box_height = bbox[3] - bbox[1]
            if box_height < min_height_norm:
                continue
            
            filtered.append(det)
        
        return filtered
    
    def _analyze_tracks(self, tracks: List[Track], poses: Dict[int, PoseKeypoints],
                       width: int, height: int, dt: float) -> Dict[int, Dict[str, Any]]:
        """Analyze each track for zone presence, proximity, etc."""
        analysis = {}
        
        # Get zone IDs
        gate_area_zone = None
        guard_anchor_zone = None
        
        for zone_id in self.zone_manager.zones.keys():
            if 'gate' in zone_id.lower() and 'anchor' not in zone_id.lower():
                gate_area_zone = zone_id
            elif 'anchor' in zone_id.lower():
                guard_anchor_zone = zone_id
        
        for track in tracks:
            if not track.is_confirmed:
                continue
            
            track_id = track.track_id
            
            # Add to jitter filter
            center = track.center
            self.jitter_filter.add_position(track_id, center)
            smoothed_center = self.jitter_filter.get_smoothed_position(track_id)
            
            # Zone presence
            in_gate_area = False
            in_guard_anchor = False
            
            if gate_area_zone:
                in_gate_area = self.zone_manager.point_in_zone(smoothed_center, gate_area_zone)
            
            if guard_anchor_zone:
                in_guard_anchor = self.zone_manager.point_in_zone(smoothed_center, guard_anchor_zone)
            
            # Store analysis
            analysis[track_id] = {
                'bbox': BBox(*track.bbox),
                'center': smoothed_center,
                'in_gate_area': in_gate_area,
                'in_guard_anchor': in_guard_anchor,
                'has_pose': track_id in poses,
                'pose': poses.get(track_id),
                'velocity': track.velocity
            }
        
        # Calculate proximity between all pairs
        for i, track1 in enumerate(tracks):
            if not track1.is_confirmed or track1.track_id not in analysis:
                continue
            
            for j, track2 in enumerate(tracks):
                if i >= j or not track2.is_confirmed or track2.track_id not in analysis:
                    continue
                
                # Calculate proximity
                bbox1 = analysis[track1.track_id]['bbox']
                bbox2 = analysis[track2.track_id]['bbox']
                
                in_contact, center_dist, iou = ProximityCalculator.are_in_contact(
                    bbox1, bbox2,
                    self.config['proximity']['center_dist_scale'],
                    self.config['proximity']['iou_min']
                )
                
                # Store proximity info
                if 'proximity' not in analysis[track1.track_id]:
                    analysis[track1.track_id]['proximity'] = {}
                
                analysis[track1.track_id]['proximity'][track2.track_id] = {
                    'in_contact': in_contact,
                    'center_distance': center_dist,
                    'iou': iou
                }
        
        return analysis
    
    def _event_layer(self, perception: Dict, dt: float) -> List[Dict]:
        """
        Layer 2: Events
        Generate micro-events from perception
        """
        new_events = []
        
        track_analysis = perception['track_analysis']
        
        for track_id, analysis in track_analysis.items():
            # Zone entry/exit events
            if analysis['in_gate_area']:
                # Check if this is a new entry
                prev_events = self.event_logger.get_events_for_track(
                    track_id, 
                    [EventType.P_ENTERED_GA],
                    since=time.time() - 2.0
                )
                if len(prev_events) == 0:
                    event = self.event_logger.create_event(
                        EventType.P_ENTERED_GA,
                        track_id=track_id,
                        zone_id='gate_area',
                        position=analysis['center']
                    )
                    new_events.append(event)
            
            if analysis['in_guard_anchor']:
                # Check if this is a new anchor
                prev_events = self.event_logger.get_events_for_track(
                    track_id,
                    [EventType.G_ANCHORED],
                    since=time.time() - 2.0
                )
                if len(prev_events) == 0:
                    event = self.event_logger.create_event(
                        EventType.G_ANCHORED,
                        track_id=track_id,
                        zone_id='guard_anchor',
                        position=analysis['center']
                    )
                    new_events.append(event)
            
            # Contact events
            if 'proximity' in analysis:
                for other_id, prox in analysis['proximity'].items():
                    if prox['in_contact']:
                        self.event_logger.update_contact(
                            track_id, other_id,
                            prox['center_distance'],
                            prox['iou']
                        )
        
        return [e.to_dict() for e in new_events]
    
    def _decision_layer(self, perception: Dict, events: List, dt: float) -> Dict[str, Any]:
        """
        Layer 3: Decisions
        FSM-based decision making with scoring
        """
        decisions = {
            'persons': {},
            'guards': {},
            'completions': []
        }
        
        track_analysis = perception['track_analysis']
        
        # Identify guards (in anchor zone)
        guard_tracks = [
            tid for tid, analysis in track_analysis.items()
            if analysis['in_guard_anchor']
        ]
        
        # Update guard states
        for guard_id in guard_tracks:
            analysis = track_analysis[guard_id]
            is_qualified = self.decision_engine.update_guard(
                guard_id,
                analysis['in_guard_anchor'],
                analysis['in_gate_area'],
                dt
            )
            
            decisions['guards'][guard_id] = {
                'is_qualified': is_qualified,
                'in_anchor': analysis['in_guard_anchor'],
                'in_gate': analysis['in_gate_area']
            }
        
        # Update person states (non-guards)
        for track_id, analysis in track_analysis.items():
            if track_id in guard_tracks:
                continue  # Skip guards
            
            # Select nearest guard
            selected_guard = self._select_guard_for_person(
                track_id, guard_tracks, track_analysis
            )
            
            # Check contact with selected guard
            is_in_contact = False
            contact_metrics = {}
            
            if selected_guard and 'proximity' in analysis:
                prox = analysis['proximity'].get(selected_guard, {})
                is_in_contact = prox.get('in_contact', False)
                contact_metrics = {
                    'center_distance': prox.get('center_distance', float('inf')),
                    'iou': prox.get('iou', 0.0)
                }
            
            # Check pose
            pose_detected = False
            if analysis['has_pose'] and selected_guard:
                guard_analysis = track_analysis.get(selected_guard)
                if guard_analysis and guard_analysis['has_pose']:
                    pose_result = self.pose_estimator.detect_hand_to_torso(
                        analysis['pose'],
                        guard_analysis['pose'],
                        self.config['proximity']['hands_toward_torso_margin']
                    )
                    pose_detected = pose_result['detected']
            
            # Update FSM
            decision = self.decision_engine.update_person(
                track_id,
                analysis['in_gate_area'],
                selected_guard,
                is_in_contact,
                contact_metrics,
                pose_detected,
                dt
            )
            
            decisions['persons'][track_id] = decision
            
            # Check for completion
            if decision['completion']['completed']:
                completion = self._handle_completion(
                    track_id, selected_guard, decision, perception
                )
                decisions['completions'].append(completion)
        
        # Check timeouts
        for track_id in list(self.decision_engine.person_states.keys()):
            if self.decision_engine.check_session_timeout(track_id):
                print(f"Session timeout for track {track_id}")
        
        return decisions
    
    def _select_guard_for_person(self, person_id: int, guard_ids: List[int],
                                 track_analysis: Dict) -> Optional[int]:
        """Select nearest qualified guard for person"""
        if len(guard_ids) == 0:
            return None
        
        person_analysis = track_analysis.get(person_id)
        if not person_analysis or not person_analysis['in_gate_area']:
            return None
        
        # Find nearest guard
        min_dist = float('inf')
        best_guard = None
        
        for guard_id in guard_ids:
            # Check if guard is qualified
            guard_state = self.decision_engine.guard_states.get(guard_id)
            if not guard_state or not guard_state.is_qualified:
                continue
            
            # Get proximity
            if 'proximity' in person_analysis and guard_id in person_analysis['proximity']:
                prox = person_analysis['proximity'][guard_id]
                dist = prox['center_distance']
                
                if dist < min_dist:
                    min_dist = dist
                    best_guard = guard_id
        
        return best_guard
    
    def _handle_completion(self, visitor_id: int, guard_id: Optional[int],
                          decision: Dict, perception: Dict) -> Dict[str, Any]:
        """Handle check completion event"""
        print(f"✅ CHECK COMPLETED: Visitor {visitor_id}, Guard {guard_id}")
        
        person_state = self.decision_engine.person_states[visitor_id]
        
        # Create completion record
        completion_data = {
            'session_id': f"{visitor_id}_{int(time.time() * 1000)}",
            'visitor_track_id': visitor_id,
            'guard_track_id': guard_id,
            'gate_id': self.gate_id,
            'completed_at': time.time(),
            'window_start': person_state.session_started_at,
            'window_end': time.time(),
            'visitor_dwell': person_state.dwell_in_ga,
            'guard_dwell': person_state.guard_overlap_time,
            'interaction_duration': person_state.interaction_time,
            'min_center_distance': person_state.min_center_distance,
            'max_iou': person_state.max_iou,
            'pose_reach_count': person_state.pose_reach_count,
            'score': decision['score'],
            'threshold': self.config['scoring']['threshold'],
            'criteria_met': decision['completion']['criteria_met'],
            'event_timeline': self.event_logger.get_event_timeline(visitor_id)
        }
        
        # Log to database
        self.database.log_check_completion(completion_data)
        
        # Generate Indonesian incident report
        try:
            incident = self.incident_generator.create_incident_from_completion(completion_data)
            
            # Capture screenshot if visualization frame is available
            if 'visualization' in perception and perception['visualization'] is not None:
                screenshot_path = self.incident_generator.capture_screenshot(
                    perception['visualization'], incident.incident_id
                )
                incident.screenshot_path = screenshot_path
            
            # Generate multi-language reports
            reports = self.incident_generator.generate_multi_language_reports(incident)
            
            # Log incident to database
            self.incident_generator.log_incident_to_database(incident, completion_data)
            
            print(f"📋 Multi-language incident reports generated: {incident.incident_id}")
            for lang, path in reports.items():
                if not lang.endswith('_error'):
                    print(f"   {lang}: {path}")
            
            # Add report paths to completion data
            completion_data['incident_report'] = {
                'incident_id': incident.incident_id,
                'reports': reports
            }
            
        except Exception as e:
            print(f"⚠️ Failed to generate incident report: {e}")
        
        # Log completion event
        self.event_logger.create_event(
            EventType.CHECK_COMPLETED,
            track_id=visitor_id,
            related_track_id=guard_id,
            metadata=completion_data
        )
        
        return completion_data
    
    def _visualize(self, frame: np.ndarray, perception: Dict, 
                   decisions: Dict) -> np.ndarray:
        """Visualize zones, tracks, and decisions"""
        vis = frame.copy()
        width, height = perception['frame_shape']
        
        # Draw zones
        zone_ids = list(self.zone_manager.zones.keys())
        vis = visualize_zones(vis, self.zone_manager, zone_ids)
        
        # Draw tracks
        vis = visualize_tracks(vis, perception['tracks'], width, height, 
                              show_id=True, show_velocity=False)
        
        # Draw state labels
        for track_id, decision in decisions['persons'].items():
            track = self.tracker.get_track(track_id)
            if track:
                x = int(track.bbox[0] * width)
                y = int(track.bbox[1] * height) - 30
                
                state = decision['state']
                score = decision['score']
                
                label = f"{state[:15]} ({score:.2f})"
                color = (0, 255, 0) if score >= 0.9 else (0, 165, 255)
                
                cv2.putText(vis, label, (x, y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        return vis
    
    def _cleanup_old_states(self, tracks: List[Track]):
        """Cleanup old states for inactive tracks"""
        active_ids = [t.track_id for t in tracks if t.is_confirmed]
        
        self.decision_engine.cleanup_old_states(active_ids)
        self.pose_estimator.cleanup_old_tracks(active_ids)
        
        # Cleanup jitter filter
        for track_id in list(self.jitter_filter.history.keys()):
            if track_id not in active_ids:
                self.jitter_filter.clear_track(track_id)
    
    def _get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            'frame_count': self.frame_count,
            'active_tracks': len([t for t in self.tracker.tracks if t.is_confirmed]),
            'decision_engine': self.decision_engine.get_state_summary(),
            'event_logger': self.event_logger.get_summary()
        }
    
    def reset(self):
        """Reset checker state"""
        self.tracker.reset()
        self.decision_engine.person_states.clear()
        self.decision_engine.guard_states.clear()
        self.frame_count = 0
        print("🔄 Gate checker reset")

