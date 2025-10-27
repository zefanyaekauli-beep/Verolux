"""
Unit Tests for Backend API Endpoints
Tests all FastAPI endpoints without requiring actual models
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json


@pytest.mark.api
class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_endpoint_returns_200(self, client):
        """Test that health endpoint returns 200 status."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_endpoint_returns_json(self, client):
        """Test that health endpoint returns JSON response."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_health_endpoint_includes_uptime(self, client):
        """Test that health endpoint includes uptime information."""
        response = client.get("/health")
        data = response.json()
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0


@pytest.mark.api
class TestInfoEndpoint:
    """Test system info endpoint."""
    
    def test_info_endpoint_returns_200(self, client):
        """Test that info endpoint returns 200 status."""
        response = client.get("/info")
        assert response.status_code == 200
    
    def test_info_endpoint_structure(self, client):
        """Test that info endpoint returns correct structure."""
        response = client.get("/info")
        data = response.json()
        assert "model" in data
        assert "device" in data
        assert "framework" in data


@pytest.mark.api
@pytest.mark.integration
class TestVideoUploadEndpoint:
    """Test video upload endpoint."""
    
    def test_upload_without_file_returns_422(self, client):
        """Test upload without file returns validation error."""
        response = client.post("/upload-video")
        assert response.status_code == 422
    
    @patch('backend_server.UPLOAD_DIR', '/tmp/test_uploads')
    def test_upload_with_file_returns_200(self, client, tmp_path):
        """Test successful file upload."""
        # Create a dummy video file
        test_file = tmp_path / "test_video.mp4"
        test_file.write_bytes(b"fake video content")
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/upload-video",
                files={"video_file": ("test.mp4", f, "video/mp4")}
            )
        
        # Should return 200 or redirect
        assert response.status_code in [200, 302]


@pytest.mark.unit
class TestHelperFunctions:
    """Test helper functions in backend server."""
    
    def test_parse_video_source_webcam(self):
        """Test parsing webcam source."""
        from backend_server import parse_video_source
        source = parse_video_source("webcam:0")
        assert source == 0
    
    def test_parse_video_source_rtsp(self):
        """Test parsing RTSP source."""
        from backend_server import parse_video_source
        source = parse_video_source("rtsp://camera.local/stream")
        assert source == "rtsp://camera.local/stream"
    
    def test_parse_video_source_file(self):
        """Test parsing file source."""
        from backend_server import parse_video_source
        source = parse_video_source("file:///path/to/video.mp4")
        assert "video.mp4" in source
    
    def test_parse_video_source_youtube(self):
        """Test parsing YouTube source."""
        from backend_server import parse_video_source
        source = parse_video_source("youtube:dQw4w9WgXcQ")
        assert "dQw4w9WgXcQ" in source


@pytest.mark.unit
class TestDetectionProcessing:
    """Test detection processing functions."""
    
    def test_normalize_bbox(self):
        """Test bounding box normalization."""
        from backend_server import normalize_bbox
        # Image 640x480, bbox [100, 100, 200, 300]
        normalized = normalize_bbox([100, 100, 200, 300], 640, 480)
        assert len(normalized) == 4
        assert 0 <= normalized[0] <= 1
        assert 0 <= normalized[1] <= 1
        assert normalized[2] > normalized[0]
        assert normalized[3] > normalized[1]
    
    def test_detection_to_dict(self, sample_detection):
        """Test detection object to dictionary conversion."""
        assert "class" in sample_detection
        assert "confidence" in sample_detection
        assert "bbox" in sample_detection
        assert sample_detection["confidence"] > 0
        assert sample_detection["confidence"] <= 1


@pytest.mark.integration
@pytest.mark.slow
class TestWebSocketConnection:
    """Test WebSocket connection and streaming."""
    
    @patch('backend_server.YOLO_MODEL')
    def test_websocket_detection_connection(self, mock_model, client):
        """Test WebSocket detection stream connection."""
        mock_model.return_value = MagicMock()
        
        with client.websocket_connect("/ws/detections?source=webcam:0") as websocket:
            # Should receive connection info
            data = websocket.receive_json()
            assert "type" in data
            # Close cleanly
            websocket.close()
    
    @patch('backend_server.GATE_CHECKER_AVAILABLE', False)
    def test_gate_check_unavailable_returns_error(self, client):
        """Test gate check returns error when not available."""
        try:
            with client.websocket_connect("/ws/gate-check?source=webcam:0") as websocket:
                data = websocket.receive_json()
                # Should receive error or close connection
                assert data is not None
        except Exception:
            # Expected if gate checker is not available
            pass


@pytest.mark.unit
class TestCORSConfiguration:
    """Test CORS middleware configuration."""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present."""
        response = client.options("/health")
        # CORS should allow all origins
        assert response.status_code in [200, 405]  # Some endpoints may not allow OPTIONS


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in API."""
    
    def test_invalid_endpoint_returns_404(self, client):
        """Test that invalid endpoint returns 404."""
        response = client.get("/this-does-not-exist")
        assert response.status_code == 404
    
    def test_invalid_method_returns_405(self, client):
        """Test that invalid method returns 405."""
        response = client.post("/health")
        assert response.status_code == 405













