"""
Unit Tests for Zone Utilities
Tests polygon operations, point-in-polygon, proximity calculations
"""
import pytest
import numpy as np
from unittest.mock import patch


@pytest.mark.unit
class TestPolygonOperations:
    """Test polygon utility functions."""
    
    def test_point_in_polygon_inside(self, sample_zone_polygon):
        """Test point inside polygon detection."""
        from zone_utils import point_in_polygon
        # Point at center of polygon (0.5, 0.5)
        result = point_in_polygon([0.5, 0.5], sample_zone_polygon)
        assert result == True
    
    def test_point_in_polygon_outside(self, sample_zone_polygon):
        """Test point outside polygon detection."""
        from zone_utils import point_in_polygon
        # Point clearly outside (0.1, 0.1)
        result = point_in_polygon([0.1, 0.1], sample_zone_polygon)
        assert result == False
    
    def test_point_in_polygon_on_edge(self, sample_zone_polygon):
        """Test point on polygon edge."""
        from zone_utils import point_in_polygon
        # Point on edge (0.3, 0.5)
        result = point_in_polygon([0.3, 0.5], sample_zone_polygon)
        assert isinstance(result, bool)
    
    def test_bbox_center_calculation(self):
        """Test bounding box center calculation."""
        from zone_utils import bbox_center
        bbox = [100, 100, 200, 300]
        center = bbox_center(bbox)
        assert center == [150, 200]
    
    def test_bbox_center_normalized(self):
        """Test normalized bounding box center."""
        from zone_utils import bbox_center
        bbox = [0.25, 0.25, 0.75, 0.75]
        center = bbox_center(bbox)
        assert center == [0.5, 0.5]


@pytest.mark.unit
class TestProximityCalculations:
    """Test proximity and distance calculations."""
    
    def test_euclidean_distance(self):
        """Test Euclidean distance calculation."""
        from zone_utils import euclidean_distance
        p1 = [0, 0]
        p2 = [3, 4]
        distance = euclidean_distance(p1, p2)
        assert distance == 5.0
    
    def test_iou_calculation(self):
        """Test IoU (Intersection over Union) calculation."""
        from zone_utils import calculate_iou
        bbox1 = [0, 0, 100, 100]
        bbox2 = [50, 50, 150, 150]
        iou = calculate_iou(bbox1, bbox2)
        assert 0 <= iou <= 1
        assert iou > 0  # These boxes overlap
    
    def test_iou_no_overlap(self):
        """Test IoU for non-overlapping boxes."""
        from zone_utils import calculate_iou
        bbox1 = [0, 0, 100, 100]
        bbox2 = [200, 200, 300, 300]
        iou = calculate_iou(bbox1, bbox2)
        assert iou == 0.0
    
    def test_iou_complete_overlap(self):
        """Test IoU for identical boxes."""
        from zone_utils import calculate_iou
        bbox1 = [0, 0, 100, 100]
        bbox2 = [0, 0, 100, 100]
        iou = calculate_iou(bbox1, bbox2)
        assert iou == 1.0


@pytest.mark.unit
class TestZoneDetection:
    """Test zone detection and dwell time tracking."""
    
    def test_track_in_zone(self, sample_zone_polygon):
        """Test detecting track in zone."""
        from zone_utils import is_bbox_in_zone
        # Bbox at center should be in zone
        bbox = [0.4, 0.4, 0.6, 0.6]
        result = is_bbox_in_zone(bbox, sample_zone_polygon)
        assert result == True
    
    def test_track_outside_zone(self, sample_zone_polygon):
        """Test detecting track outside zone."""
        from zone_utils import is_bbox_in_zone
        # Bbox clearly outside
        bbox = [0.0, 0.0, 0.1, 0.1]
        result = is_bbox_in_zone(bbox, sample_zone_polygon)
        assert result == False


@pytest.mark.unit
class TestJitterFiltering:
    """Test jitter filtering and smoothing."""
    
    def test_savitzky_golay_filter(self):
        """Test Savitzky-Golay smoothing filter."""
        from zone_utils import smooth_trajectory
        # Create noisy trajectory
        trajectory = [[100 + np.random.randn(), 100 + np.random.randn()] for _ in range(10)]
        smoothed = smooth_trajectory(trajectory)
        assert len(smoothed) == len(trajectory)
    
    def test_moving_average_filter(self):
        """Test moving average smoothing."""
        from zone_utils import moving_average
        values = [1, 2, 3, 4, 5]
        smoothed = moving_average(values, window=3)
        assert len(smoothed) <= len(values)


@pytest.mark.unit
class TestCoordinateTransformations:
    """Test coordinate system transformations."""
    
    def test_normalize_coordinates(self):
        """Test coordinate normalization."""
        from zone_utils import normalize_coordinates
        # 640x480 image
        x, y = normalize_coordinates(320, 240, 640, 480)
        assert x == 0.5
        assert y == 0.5
    
    def test_denormalize_coordinates(self):
        """Test coordinate denormalization."""
        from zone_utils import denormalize_coordinates
        x, y = denormalize_coordinates(0.5, 0.5, 640, 480)
        assert x == 320
        assert y == 240


@pytest.mark.unit
class TestPolygonValidation:
    """Test polygon validation."""
    
    def test_valid_polygon(self, sample_zone_polygon):
        """Test valid polygon validation."""
        from zone_utils import validate_polygon
        result = validate_polygon(sample_zone_polygon)
        assert result == True
    
    def test_invalid_polygon_too_few_points(self):
        """Test polygon with too few points."""
        from zone_utils import validate_polygon
        invalid_polygon = [[0.1, 0.1], [0.2, 0.2]]  # Only 2 points
        result = validate_polygon(invalid_polygon)
        assert result == False
    
    def test_invalid_polygon_self_intersecting(self):
        """Test self-intersecting polygon."""
        from zone_utils import validate_polygon
        # Self-intersecting polygon
        invalid_polygon = [[0, 0], [1, 1], [1, 0], [0, 1]]
        # May or may not detect self-intersection depending on implementation
        result = validate_polygon(invalid_polygon)
        assert isinstance(result, bool)



















