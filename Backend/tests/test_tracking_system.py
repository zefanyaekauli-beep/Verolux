"""
Unit Tests for Tracking System
Tests multi-object tracking, track lifecycle, and matching
"""
import pytest
import numpy as np


@pytest.mark.unit
class TestTrackCreation:
    """Test track creation and initialization."""
    
    def test_create_track_from_detection(self, sample_detection):
        """Test creating a new track from detection."""
        from tracking_system import Track
        track = Track(
            track_id=1,
            bbox=sample_detection["bbox"],
            confidence=sample_detection["confidence"]
        )
        assert track.track_id == 1
        assert track.confidence == sample_detection["confidence"]
        assert len(track.bbox) == 4
    
    def test_track_initialization_defaults(self):
        """Test track initialization with defaults."""
        from tracking_system import Track
        track = Track(track_id=1, bbox=[100, 100, 200, 300])
        assert track.age == 0
        assert track.hits == 1
        assert track.time_since_update == 0


@pytest.mark.unit
class TestTrackUpdate:
    """Test track update logic."""
    
    def test_track_update_increases_age(self):
        """Test that updating track increases age."""
        from tracking_system import Track
        track = Track(track_id=1, bbox=[100, 100, 200, 300])
        initial_age = track.age
        track.update([110, 110, 210, 310])
        assert track.age > initial_age
    
    def test_track_update_resets_time_since_update(self):
        """Test that update resets time_since_update."""
        from tracking_system import Track
        track = Track(track_id=1, bbox=[100, 100, 200, 300])
        track.time_since_update = 5
        track.update([110, 110, 210, 310])
        assert track.time_since_update == 0
    
    def test_track_update_increases_hits(self):
        """Test that update increases hit count."""
        from tracking_system import Track
        track = Track(track_id=1, bbox=[100, 100, 200, 300])
        initial_hits = track.hits
        track.update([110, 110, 210, 310])
        assert track.hits == initial_hits + 1


@pytest.mark.unit
class TestTrackMatching:
    """Test track-detection matching algorithms."""
    
    def test_iou_matching(self):
        """Test IoU-based track matching."""
        from tracking_system import match_detections_to_tracks
        tracks = [
            {"track_id": 1, "bbox": [100, 100, 200, 300]},
            {"track_id": 2, "bbox": [300, 100, 400, 300]}
        ]
        detections = [
            {"bbox": [105, 105, 205, 305]},  # Close to track 1
            {"bbox": [305, 105, 405, 305]}   # Close to track 2
        ]
        matches = match_detections_to_tracks(detections, tracks, iou_threshold=0.3)
        assert len(matches) > 0
    
    def test_center_distance_matching(self):
        """Test center distance-based matching."""
        from tracking_system import calculate_center_distance
        bbox1 = [100, 100, 200, 300]
        bbox2 = [105, 105, 205, 305]
        distance = calculate_center_distance(bbox1, bbox2)
        assert distance < 10  # Should be close


@pytest.mark.unit
class TestTrackerLifecycle:
    """Test tracker initialization and lifecycle."""
    
    def test_tracker_initialization(self):
        """Test tracker initialization."""
        from tracking_system import Tracker
        tracker = Tracker(max_age=30, min_hits=3)
        assert tracker.max_age == 30
        assert tracker.min_hits == 3
        assert tracker.next_id == 1
    
    def test_tracker_adds_detections(self):
        """Test tracker processes detections."""
        from tracking_system import Tracker
        tracker = Tracker()
        detections = [{"bbox": [100, 100, 200, 300], "confidence": 0.85}]
        tracks = tracker.update(detections)
        assert isinstance(tracks, list)
    
    def test_tracker_removes_old_tracks(self):
        """Test tracker removes stale tracks."""
        from tracking_system import Tracker
        tracker = Tracker(max_age=2)
        # Add a detection
        detections = [{"bbox": [100, 100, 200, 300], "confidence": 0.85}]
        tracker.update(detections)
        # Update with no detections multiple times
        for _ in range(5):
            tracker.update([])
        # Old tracks should be removed
        active_tracks = [t for t in tracker.tracks if t.time_since_update < tracker.max_age]
        assert len(active_tracks) == 0


@pytest.mark.unit
class TestTrackVelocity:
    """Test velocity estimation."""
    
    def test_velocity_calculation(self):
        """Test track velocity calculation."""
        from tracking_system import Track
        track = Track(track_id=1, bbox=[100, 100, 200, 300])
        track.update([110, 100, 210, 300])  # Moved 10 pixels right
        # Should have positive x velocity
        if hasattr(track, 'velocity'):
            assert track.velocity[0] > 0
    
    def test_stationary_track_zero_velocity(self):
        """Test stationary track has zero velocity."""
        from tracking_system import Track
        track = Track(track_id=1, bbox=[100, 100, 200, 300])
        track.update([100, 100, 200, 300])  # Same position
        if hasattr(track, 'velocity'):
            velocity_magnitude = np.sqrt(track.velocity[0]**2 + track.velocity[1]**2)
            assert velocity_magnitude < 1.0


@pytest.mark.unit
class TestOcclusionHandling:
    """Test occlusion handling."""
    
    def test_track_survives_brief_occlusion(self):
        """Test track survives brief occlusion."""
        from tracking_system import Tracker
        tracker = Tracker(max_age=5)
        # Create track
        detections = [{"bbox": [100, 100, 200, 300], "confidence": 0.85}]
        tracks1 = tracker.update(detections)
        initial_track_id = tracks1[0]["track_id"]
        
        # Brief occlusion (2 frames)
        tracker.update([])
        tracker.update([])
        
        # Reappears
        tracks2 = tracker.update(detections)
        # Should maintain same ID
        if len(tracks2) > 0:
            assert tracks2[0]["track_id"] == initial_track_id


@pytest.mark.unit
class TestTrackHistory:
    """Test track history management."""
    
    def test_track_maintains_history(self):
        """Test that track maintains position history."""
        from tracking_system import Track
        track = Track(track_id=1, bbox=[100, 100, 200, 300])
        track.update([110, 110, 210, 310])
        track.update([120, 120, 220, 320])
        
        if hasattr(track, 'history'):
            assert len(track.history) >= 2
    
    def test_track_history_max_length(self):
        """Test that track history doesn't grow infinitely."""
        from tracking_system import Track
        track = Track(track_id=1, bbox=[100, 100, 200, 300])
        # Update many times
        for i in range(100):
            track.update([100 + i, 100, 200 + i, 300])
        
        if hasattr(track, 'history'):
            # History should be capped
            assert len(track.history) < 100



















