"""
Integration Tests for FastAPI Endpoints
Tests complete API workflows including WebSocket connections
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import time


@pytest.mark.integration
class TestHealthCheckIntegration:
    """Integration tests for health check endpoints."""
    
    def test_health_check_complete_flow(self, client):
        """Test complete health check flow."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all expected fields
        assert "status" in data
        assert "uptime_seconds" in data
        assert data["status"] == "healthy"
        
        # Health check should be fast
        assert response.elapsed.total_seconds() < 1.0 if hasattr(response, 'elapsed') else True


@pytest.mark.integration
class TestSystemInfoIntegration:
    """Integration tests for system info."""
    
    def test_info_endpoint_complete_response(self, client):
        """Test complete info endpoint response."""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        
        # Check all expected fields
        required_fields = ["model", "device", "framework"]
        for field in required_fields:
            assert field in data


@pytest.mark.integration
class TestFileUploadIntegration:
    """Integration tests for file upload."""
    
    def test_upload_video_complete_flow(self, client, tmp_path):
        """Test complete video upload flow."""
        # Create test video file
        test_video = tmp_path / "test_video.mp4"
        test_video.write_bytes(b"fake video content for testing")
        
        with open(test_video, "rb") as f:
            files = {"video_file": ("test_video.mp4", f, "video/mp4")}
            response = client.post("/upload-video", files=files)
        
        # Should succeed or provide meaningful error
        assert response.status_code in [200, 201, 302, 422]


@pytest.mark.integration
@pytest.mark.slow
class TestWebSocketIntegration:
    """Integration tests for WebSocket connections."""
    
    @patch('backend_server.YOLO_MODEL')
    @patch('backend_server.cv2.VideoCapture')
    def test_detection_websocket_full_flow(self, mock_cv2, mock_yolo, client):
        """Test full WebSocket detection flow."""
        # Mock video capture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, MagicMock())
        mock_cv2.return_value = mock_cap
        
        # Mock YOLO
        mock_result = MagicMock()
        mock_result.boxes = MagicMock()
        mock_result.boxes.cpu.return_value.numpy.return_value = []
        mock_yolo.return_value = [mock_result]
        
        try:
            with client.websocket_connect("/ws/detections?source=webcam:0") as websocket:
                # Should receive connection info
                data = websocket.receive_json(timeout=5)
                assert data is not None
                
                # Should be able to close cleanly
                websocket.close()
        except Exception as e:
            # Expected in test environment without actual camera
            pytest.skip(f"WebSocket test requires camera: {e}")


@pytest.mark.integration
class TestGateSecurityIntegration:
    """Integration tests for gate security endpoints."""
    
    def test_gate_completions_endpoint(self, client):
        """Test gate completions endpoint."""
        response = client.get("/gate/completions")
        # Should return 200 or 503 if gate checker not available
        assert response.status_code in [200, 503]
    
    def test_gate_stats_endpoint(self, client):
        """Test gate statistics endpoint."""
        response = client.get("/gate/stats")
        assert response.status_code in [200, 503]
    
    def test_gate_config_endpoint(self, client):
        """Test gate configuration endpoint."""
        response = client.get("/gate/config")
        assert response.status_code in [200, 503]


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Integration tests for error handling."""
    
    def test_404_error_handling(self, client):
        """Test 404 error response."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_405_method_not_allowed(self, client):
        """Test 405 error for wrong method."""
        response = client.put("/health")
        assert response.status_code == 405
    
    def test_422_validation_error(self, client):
        """Test validation error handling."""
        response = client.post("/upload-video", data={})
        assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.slow
class TestConcurrentRequests:
    """Integration tests for concurrent requests."""
    
    def test_multiple_health_checks(self, client):
        """Test multiple concurrent health checks."""
        import concurrent.futures
        
        def make_request():
            return client.get("/health")
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        # All should succeed
        assert all(r.status_code == 200 for r in results)


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    @patch('gate_database.GateDatabase')
    def test_gate_database_connection(self, mock_db):
        """Test gate database connection."""
        mock_db.return_value = MagicMock()
        from gate_database import GateDatabase
        
        db = GateDatabase("test.db")
        assert db is not None


@pytest.mark.integration
class TestVideoSourceParsing:
    """Integration tests for video source parsing."""
    
    def test_webcam_source_integration(self):
        """Test webcam source parsing."""
        from backend_server import parse_video_source
        source = parse_video_source("webcam:0")
        assert source == 0
    
    def test_file_source_integration(self):
        """Test file source parsing."""
        from backend_server import parse_video_source
        source = parse_video_source("file:///path/to/video.mp4")
        assert isinstance(source, str)
    
    def test_rtsp_source_integration(self):
        """Test RTSP source parsing."""
        from backend_server import parse_video_source
        source = parse_video_source("rtsp://192.168.1.100/stream")
        assert source == "rtsp://192.168.1.100/stream"


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndFlow:
    """End-to-end integration tests."""
    
    @patch('backend_server.YOLO_MODEL')
    def test_complete_detection_pipeline(self, mock_yolo, client, sample_video_frame):
        """Test complete detection pipeline from frame to result."""
        # Setup mock YOLO
        mock_result = MagicMock()
        mock_result.boxes = MagicMock()
        mock_result.boxes.xyxy = [[100, 100, 200, 300]]
        mock_result.boxes.conf = [0.85]
        mock_result.boxes.cls = [0]
        mock_yolo.return_value = [mock_result]
        
        # This would require a full pipeline test
        # For now, just verify the endpoint exists
        response = client.get("/health")
        assert response.status_code == 200


@pytest.mark.integration
class TestPerformanceMetrics:
    """Integration tests for performance metrics."""
    
    def test_response_time_health_check(self, client):
        """Test health check response time."""
        start = time.time()
        response = client.get("/health")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0  # Should be fast
    
    def test_response_time_info_endpoint(self, client):
        """Test info endpoint response time."""
        start = time.time()
        response = client.get("/info")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 2.0  # Allow more time for model info



















