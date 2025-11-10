# Testing & CI/CD Guide - Verolux Backend

## Overview

This document provides comprehensive guidance for testing, code quality, and CI/CD workflows for the Verolux backend system.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Testing Framework](#testing-framework)
3. [Running Tests](#running-tests)
4. [Code Quality](#code-quality)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Pre-commit Hooks](#pre-commit-hooks)
7. [Writing Tests](#writing-tests)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Install Development Dependencies

```bash
cd Backend
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Format Code

```bash
black .
isort .
```

### Run Linters

```bash
flake8 .
pylint **/*.py
```

---

## Testing Framework

### Test Structure

```
Backend/
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── test_backend_api.py      # API endpoint tests
│   ├── test_zone_utils.py       # Zone utility tests
│   ├── test_tracking_system.py  # Tracking tests
│   ├── test_gate_checker.py     # Gate checker tests
│   └── test_api_integration.py  # Integration tests
├── pytest.ini                   # Pytest configuration
└── pyproject.toml              # Tool configurations
```

### Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Fast unit tests (default)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.slow` - Tests taking >1 second
- `@pytest.mark.gpu` - Tests requiring GPU
- `@pytest.mark.webcam` - Tests requiring webcam

### Coverage Goals

- **Target**: 60% minimum code coverage
- **Current**: Run `make test-coverage` to check
- **CI Enforcement**: Tests fail if coverage < 60%

---

## Running Tests

### Using Pytest Directly

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_backend_api.py

# Run specific test
pytest tests/test_backend_api.py::TestHealthEndpoint::test_health_endpoint_returns_200

# Run tests matching pattern
pytest -k "health"
```

### Using Make Commands

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run with coverage
make test-coverage
```

### Test Categories

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests only
pytest -m integration

# API tests only
pytest -m api

# Skip slow tests
pytest -m "not slow"

# GPU tests only
pytest -m gpu
```

---

## Code Quality

### Formatting Tools

#### Black (Code Formatter)

```bash
# Format all files
black .

# Check without formatting
black --check .

# Show diff
black --check --diff .
```

**Configuration:** `pyproject.toml`
- Line length: 120
- Target: Python 3.8+

#### isort (Import Sorter)

```bash
# Sort imports
isort .

# Check without sorting
isort --check-only .

# Show diff
isort --check-only --diff .
```

**Configuration:** `pyproject.toml`
- Profile: black
- Line length: 120

### Linting Tools

#### Flake8

```bash
# Run flake8
flake8 .

# With statistics
flake8 . --count --statistics
```

**Configuration:** `.flake8`
- Max line length: 120
- Max complexity: 15

#### Pylint

```bash
# Run pylint
pylint **/*.py

# Exit with 0 even on warnings
pylint **/*.py --exit-zero

# Check specific file
pylint backend_server.py
```

**Configuration:** `.pylintrc`
- Disabled checks: docstrings, some naming conventions

#### Mypy (Type Checking)

```bash
# Run mypy
mypy .

# Check specific file
mypy backend_server.py
```

**Configuration:** `pyproject.toml`
- Ignore missing imports
- Python 3.8+

### Security Scanning

#### Bandit

```bash
# Run security scan
bandit -r .

# JSON output
bandit -r . -f json -o bandit-report.json

# Skip tests directory
bandit -r . --exclude tests/
```

### All-in-One Commands

```bash
# Format and lint
make ci

# Full quality check
make format lint test
```

---

## CI/CD Pipeline

### GitHub Actions Workflows

#### 1. CI - Tests & Code Quality (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop`
- Pull requests

**Jobs:**
1. **Test** - Run tests on Python 3.8, 3.9, 3.10, 3.11
2. **Code Quality** - Black, isort, flake8, pylint, bandit
3. **Integration Tests** - Full integration test suite
4. **Coverage Report** - Generate and upload coverage

**Environment Variables:**
```yaml
DEVICE: cpu
MODEL_PATH: ./models/weight.pt
```

#### 2. Build Docker Images (`.github/workflows/build-docker.yml`)

**Triggers:**
- Push to `main`
- Tags matching `v*.*.*`
- Manual workflow dispatch

**Jobs:**
- Build backend Docker image
- Build frontend Docker image
- Push to GitHub Container Registry

#### 3. Deploy (`.github/workflows/deploy.yml`)

**Triggers:**
- Manual workflow dispatch
- Release tags

**Jobs:**
- Deploy to GCP Compute Engine
- Deploy to Kubernetes/GKE
- Run health checks

### CI Status Badges

Add to your README:

```markdown
![CI Status](https://github.com/YOUR_USERNAME/Verox/workflows/CI/badge.svg)
![Coverage](https://codecov.io/gh/YOUR_USERNAME/Verox/branch/main/graph/badge.svg)
```

---

## Pre-commit Hooks

### Installation

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Or use make
make pre-commit
```

### Configuration

File: `.pre-commit-config.yaml`

**Hooks:**
1. Trailing whitespace removal
2. End-of-file fixer
3. YAML/JSON validation
4. Large file checker
5. Black formatting
6. isort import sorting
7. Flake8 linting
8. Bandit security checks

### Usage

```bash
# Automatically runs on git commit
git commit -m "Your message"

# Run manually on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Skip hooks (not recommended)
git commit --no-verify
```

---

## Writing Tests

### Test Structure

```python
import pytest

@pytest.mark.unit
class TestYourComponent:
    """Test your component."""
    
    def test_something(self):
        """Test description."""
        # Arrange
        expected = "value"
        
        # Act
        result = your_function()
        
        # Assert
        assert result == expected
```

### Using Fixtures

```python
def test_with_fixture(client, sample_detection):
    """Test using fixtures from conftest.py."""
    response = client.get("/health")
    assert response.status_code == 200
    assert sample_detection["confidence"] > 0
```

### Mocking

```python
from unittest.mock import patch, MagicMock

@patch('backend_server.YOLO_MODEL')
def test_with_mock(mock_yolo):
    """Test with mocked YOLO model."""
    mock_yolo.return_value = MagicMock()
    # Your test code
```

### Testing Async Code

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await your_async_function()
    assert result is not None
```

### Testing WebSocket

```python
def test_websocket(client):
    """Test WebSocket connection."""
    with client.websocket_connect("/ws/detections") as websocket:
        data = websocket.receive_json()
        assert data is not None
```

### Best Practices

1. **One assertion per test** (when possible)
2. **Descriptive test names** - `test_user_login_with_invalid_password`
3. **Use fixtures** for shared setup
4. **Mock external dependencies** (API calls, databases)
5. **Test edge cases** (empty input, None, large values)
6. **Keep tests fast** - unit tests should be <100ms

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Make sure parent directory is in path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 2. Missing Dependencies

```bash
# Reinstall dependencies
pip install -r requirements.txt -r requirements-dev.txt
```

#### 3. Coverage Below Threshold

```bash
# Check which files have low coverage
pytest --cov=. --cov-report=term-missing

# Focus on untested modules
```

#### 4. Slow Tests

```bash
# Run only fast tests
pytest -m "not slow"

# Identify slow tests
pytest --durations=10
```

#### 5. Flake8 Errors

```bash
# Auto-fix with black
black .

# Check specific errors
flake8 --select=E501  # Line too long
```

#### 6. Pre-commit Failures

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Run specific hook
pre-commit run black --all-files
```

### CI Failures

#### Test Failures

1. Run tests locally: `pytest -v`
2. Check logs in GitHub Actions
3. Verify environment variables
4. Check for timing issues

#### Coverage Failures

1. Run locally: `make test-coverage`
2. Check which files need tests
3. Add tests to reach 60%

#### Lint Failures

1. Run locally: `make lint`
2. Auto-fix: `make format`
3. Check `.flake8` and `.pylintrc` config

---

## Performance Testing

### Load Testing

```bash
# Using locust
cd tests/load
locust -f load_test.py
```

### Profiling

```python
# Add to test
def test_with_profiling():
    import cProfile
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code
    
    profiler.disable()
    profiler.print_stats(sort='cumtime')
```

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

## Support

For issues or questions:
1. Check this guide
2. Review test examples in `tests/`
3. Check CI logs in GitHub Actions
4. Consult team documentation

---

**Last Updated:** December 2024
**Coverage Target:** 60% minimum
**CI Status:** ✅ All workflows active




















