# Makefile for Verolux Backend Development

.PHONY: help install test lint format clean run docker-build docker-up

help:
	@echo "Verolux Backend - Development Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  install         Install all dependencies"
	@echo "  install-dev     Install development dependencies"
	@echo "  test            Run all tests"
	@echo "  test-unit       Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-coverage   Run tests with coverage report"
	@echo "  lint            Run all linters"
	@echo "  format          Format code with black and isort"
	@echo "  format-check    Check code formatting without changes"
	@echo "  security        Run security checks"
	@echo "  clean           Clean temporary files"
	@echo "  run             Run backend server"
	@echo "  docker-build    Build Docker image"
	@echo "  docker-up       Start services with docker-compose"
	@echo "  pre-commit      Install pre-commit hooks"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest -v --cov=. --cov-report=html --cov-report=term-missing

test-unit:
	pytest -v -m unit

test-integration:
	pytest -v -m integration

test-coverage:
	pytest --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	@echo "Running flake8..."
	flake8 . --count --statistics
	@echo "Running pylint..."
	pylint **/*.py --exit-zero
	@echo "Running mypy..."
	mypy . --ignore-missing-imports

format:
	@echo "Formatting code with black..."
	black .
	@echo "Sorting imports with isort..."
	isort .

format-check:
	black --check --diff .
	isort --check-only --diff .

security:
	@echo "Running bandit security checks..."
	bandit -r . -f screen

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	@echo "Clean complete!"

run:
	python backend_server.py

run-dev:
	uvicorn backend_server:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t verolux-backend:latest -f ../docker/Dockerfile.backend .

docker-up:
	cd .. && docker-compose up -d

docker-down:
	cd .. && docker-compose down

pre-commit:
	pre-commit install
	@echo "Pre-commit hooks installed!"

pre-commit-run:
	pre-commit run --all-files

ci: format-check lint test
	@echo "CI checks complete!"

all: install-dev format lint test
	@echo "All tasks complete!"



















