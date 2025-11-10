# Verolux Backend - Test Suite

## Overview

This directory contains the complete test suite for the Verolux backend system.

## Test Files

| File | Tests | Purpose |
|------|-------|---------|
| `conftest.py` | - | Shared fixtures and configuration |
| `test_backend_api.py` | 15+ | API endpoint tests |
| `test_zone_utils.py` | 20+ | Zone utility functions |
| `test_tracking_system.py` | 15+ | Multi-object tracking |
| `test_gate_checker.py` | 18+ | Gate security FSM & scoring |
| `test_api_integration.py` | 12+ | End-to-end integration tests |

**Total: 80+ test cases**

## Quick Start

### Run All Tests

```bash
cd Backend
pytest
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
# Open htmlcov/index.html to view report
```

### Run Specific Test File

```bash
pytest tests/test_backend_api.py -v
```

### Run Specific Test

```bash
pytest tests/test_backend_api.py::TestHealthEndpoint::test_health_endpoint_returns_200
```

## Test Categories

Tests are marked with pytest markers:

### Unit Tests (Fast)
```bash
pytest -m unit
```

### Integration Tests
```bash
pytest -m integration
```

### API Tests
```bash
pytest -m api
```

### Skip Slow Tests
```bash
pytest -m "not slow"
```

## Writing New Tests

### 1. Create Test File

```python
# tests/test_your_feature.py
import pytest

@pytest.mark.unit
class TestYourFeature:
    """Test your feature."""
    
    def test_something(self):
        """Test description."""
        assert True
```

### 2. Use Fixtures

Available fixtures from `conftest.py`:

- `client` - FastAPI test client
- `test_app` - FastAPI app instance
- `mock_yolo_model` - Mock YOLO model
- `sample_video_frame` - Sample video frame (640x480)
- `sample_detection` - Sample detection data
- `sample_gate_config` - Sample gate configuration
- `sample_zone_polygon` - Sample zone polygon
- `temp_upload_dir` - Temporary upload directory
- `mock_database` - Temporary test database

### 3. Example Test

```python
def test_with_fixtures(client, sample_detection):
    """Test using fixtures."""
    # Use the FastAPI test client
    response = client.get("/health")
    assert response.status_code == 200
    
    # Use sample detection data
    assert sample_detection["confidence"] > 0
```

### 4. Mocking

```python
from unittest.mock import patch, MagicMock

@patch('backend_server.YOLO_MODEL')
def test_with_mock(mock_yolo, client):
    """Test with mocked YOLO model."""
    mock_yolo.return_value = MagicMock()
    
    response = client.get("/info")
    assert response.status_code == 200
```

## Test Structure

### Arrange-Act-Assert Pattern

```python
def test_something():
    """Test description."""
    # Arrange - Set up test data
    input_data = "test"
    expected = "TEST"
    
    # Act - Execute the function
    result = your_function(input_data)
    
    # Assert - Verify the result
    assert result == expected
```

### Test Classes

Group related tests:

```python
@pytest.mark.unit
class TestYourComponent:
    """Tests for your component."""
    
    def test_initialization(self):
        """Test component initialization."""
        pass
    
    def test_method_a(self):
        """Test method A."""
        pass
    
    def test_method_b(self):
        """Test method B."""
        pass
```

## Coverage Goals

- **Current Target:** 60% minimum
- **Good:** 75%
- **Excellent:** 85%+

### Check Coverage

```bash
# Generate report
pytest --cov=. --cov-report=html

# View in browser
# Windows: start htmlcov\index.html
# macOS: open htmlcov/index.html
# Linux: xdg-open htmlcov/index.html
```

### Improve Coverage

1. Run coverage report
2. Identify uncovered lines (red/orange in HTML report)
3. Add tests for those lines
4. Focus on:
   - Edge cases
   - Error handling
   - Integration flows
   - Complex logic

## Best Practices

### Do's ✅

- ✅ Write descriptive test names
- ✅ Use fixtures for shared setup
- ✅ Mock external dependencies
- ✅ Keep tests fast (<100ms for unit tests)
- ✅ Test edge cases
- ✅ One assertion per test (when possible)
- ✅ Use appropriate markers
- ✅ Clean up resources (use fixtures)

### Don'ts ❌

- ❌ Don't test third-party libraries
- ❌ Don't hardcode paths
- ❌ Don't depend on external services
- ❌ Don't use sleep() for timing
- ❌ Don't share state between tests
- ❌ Don't skip tests without good reason

## Troubleshooting

### Import Errors

```bash
# Add parent directory to path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Tests Not Found

```bash
# Check test discovery
pytest --collect-only
```

### Slow Tests

```bash
# Find slow tests
pytest --durations=10

# Skip slow tests
pytest -m "not slow"
```

### Mock Issues

```python
# Use MagicMock for flexible mocking
from unittest.mock import MagicMock, patch

@patch('module.function')
def test_something(mock_func):
    mock_func.return_value = "mocked"
    # Your test
```

## Running Tests in CI

Tests automatically run on:
- Every push to `main` or `develop`
- Every pull request
- Manual workflow dispatch

See `.github/workflows/ci.yml` for details.

## Resources

- **Testing Guide:** [../TESTING_GUIDE.md](../TESTING_GUIDE.md)
- **Pytest Docs:** https://docs.pytest.org/
- **Coverage Docs:** https://coverage.readthedocs.io/

## Quick Commands

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run last failed
pytest --lf

# Parallel execution
pytest -n auto

# Generate coverage
pytest --cov=. --cov-report=html

# Specific marker
pytest -m unit

# Pattern matching
pytest -k "health"
```

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure tests pass: `pytest`
3. Check coverage: `pytest --cov=.`
4. Add markers: `@pytest.mark.unit` or `@pytest.mark.integration`
5. Update this README if needed

## Support

For issues:
1. Check [TESTING_GUIDE.md](../TESTING_GUIDE.md)
2. Review test examples in this directory
3. Check CI logs in GitHub Actions



















