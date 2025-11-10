"""
Pytest Configuration and Fixtures
Provides shared test fixtures for all tests
"""
import os
import sys
import pytest
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_app():
    """Create a test FastAPI application instance."""
    # Import here to avoid loading heavy dependencies during collection
    from backend_server import app
    return app


@pytest.fixture(scope="function")
def client(test_app) -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application."""
    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def mock_yolo_model():
    """Mock YOLO model for testing without loading actual model."""
    class MockYOLOModel:
        def __init__(self):
            self.device = "cpu"
            
        def __call__(self, frame, **kwargs):
            """Return mock detections."""
            class MockResult:
                def __init__(self):
                    self.boxes = MockBoxes()
                    
            class MockBoxes:
                def __init__(self):
                    import numpy as np
                    # Mock detection: one person at center
                    self.xyxy = np.array([[100, 100, 200, 300]])
                    self.conf = np.array([0.85])
                    self.cls = np.array([0])
                    
                def cpu(self):
                    return self
                    
                def numpy(self):
                    return self.xyxy
            
            return [MockResult()]
    
    return MockYOLOModel()


@pytest.fixture(scope="function")
def sample_video_frame():
    """Generate a sample video frame for testing."""
    import numpy as np
    # Create a blank 640x480 BGR image
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    return frame


@pytest.fixture(scope="function")
def sample_detection():
    """Sample detection data."""
    return {
        "class": "person",
        "confidence": 0.85,
        "bbox": [100, 100, 200, 300],
        "normalized_bbox": [0.15625, 0.20833, 0.3125, 0.625]
    }


@pytest.fixture(scope="function")
def sample_gate_config():
    """Sample gate configuration."""
    return {
        "gate_id": "TEST_GATE_A1",
        "zones": {
            "gate_area": "test_gate_polygon.json",
            "guard_anchor": "test_guard_polygon.json"
        },
        "timers": {
            "person_min_dwell_s": 3.0,
            "guard_min_dwell_s": 2.0,
            "interaction_min_overlap_s": 1.0
        },
        "scoring": {
            "base": 0.6,
            "threshold": 0.9
        }
    }


@pytest.fixture(scope="function")
def temp_upload_dir(tmp_path):
    """Create a temporary upload directory."""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    return str(upload_dir)


@pytest.fixture(scope="function")
def sample_zone_polygon():
    """Sample zone polygon coordinates."""
    return [
        [0.3, 0.2],
        [0.7, 0.2],
        [0.7, 0.8],
        [0.3, 0.8]
    ]


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(scope="function")
def mock_database(tmp_path):
    """Create a temporary test database."""
    db_path = tmp_path / "test_gate_security.db"
    return str(db_path)


# Mark all tests as unit by default
def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their location."""
    for item in items:
        if "integration" not in item.keywords:
            item.add_marker(pytest.mark.unit)




















