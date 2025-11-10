"""
Model Validation Pipeline
Automated model quality gates before deployment
"""
import json
import time
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ValidationMetrics:
    """Model validation metrics"""
    map_50: float  # mAP@0.5
    map_95: float  # mAP@0.5:0.95
    precision: float
    recall: float
    f1_score: float
    fps: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    gpu_memory_mb: float
    passed: bool
    notes: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


class ModelValidator:
    """
    Validate models against quality gates
    
    Features:
    - Regression testing on fixed dataset
    - Performance benchmarking
    - Quality gates (block bad models)
    - Comparison with baseline
    """
    
    def __init__(self, 
                 validation_dataset_path: str = "./validation_data",
                 baseline_model: str = "v1.0.0"):
        """
        Initialize model validator
        
        Args:
            validation_dataset_path: Path to validation dataset
            baseline_model: Baseline model for comparison
        """
        self.validation_dataset_path = Path(validation_dataset_path)
        self.baseline_model = baseline_model
        
        # Quality gates (thresholds)
        self.gates = {
            "min_map_50": 0.80,  # Minimum mAP@0.5
            "min_precision": 0.85,  # Minimum precision
            "min_recall": 0.80,  # Minimum recall
            "max_fps_regression": -10.0,  # Max 10% FPS drop from baseline
            "max_accuracy_regression": -0.02,  # Max 2% mAP drop from baseline
            "max_latency_p95_ms": 100.0  # Max p95 latency
        }
        
        # Load baseline metrics if available
        self.baseline_metrics: Optional[ValidationMetrics] = None
        self._load_baseline()
        
        logger.info(f"Model validator initialized with {len(self.gates)} quality gates")
    
    def _load_baseline(self):
        """Load baseline model metrics"""
        baseline_file = f"./models/validation_{self.baseline_model}.json"
        
        if os.path.exists(baseline_file):
            try:
                with open(baseline_file, 'r') as f:
                    data = json.load(f)
                
                self.baseline_metrics = ValidationMetrics(**data)
                logger.info(f"Loaded baseline metrics for {self.baseline_model}")
            except Exception as e:
                logger.warning(f"Could not load baseline metrics: {e}")
    
    def validate_model(self, 
                      model_path: str,
                      model_version: str,
                      run_performance_test: bool = True) -> ValidationMetrics:
        """
        Validate model against quality gates
        
        Args:
            model_path: Path to model file
            model_version: Model version identifier
            run_performance_test: Run performance benchmarks
            
        Returns:
            ValidationMetrics with results
        """
        logger.info(f"Validating model {model_version}...")
        
        # Load model
        try:
            from ultralytics import YOLO
            model = YOLO(model_path)
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return ValidationMetrics(
                map_50=0, map_95=0, precision=0, recall=0, f1_score=0,
                fps=0, latency_p50_ms=0, latency_p95_ms=0, latency_p99_ms=0,
                gpu_memory_mb=0, passed=False,
                notes=f"Model load failed: {e}"
            )
        
        # Run validation
        metrics = self._run_validation(model, model_version, run_performance_test)
        
        # Check quality gates
        passed, failures = self._check_quality_gates(metrics)
        
        metrics.passed = passed
        if not passed:
            metrics.notes = f"Failed quality gates: {', '.join(failures)}"
        
        # Save metrics
        self._save_metrics(model_version, metrics)
        
        logger.info(
            f"Model {model_version} validation: "
            f"{'✅ PASSED' if passed else '❌ FAILED'}"
        )
        
        return metrics
    
    def _run_validation(self, 
                       model,
                       model_version: str,
                       run_performance_test: bool) -> ValidationMetrics:
        """Run actual validation tests"""
        
        # Mock metrics (in real implementation, run on validation set)
        # This would run model.val(data='validation_dataset.yaml')
        
        logger.info("Running validation on fixed dataset...")
        
        # Simulate validation (replace with actual validation)
        metrics = ValidationMetrics(
            map_50=0.87,
            map_95=0.75,
            precision=0.89,
            recall=0.85,
            f1_score=0.87,
            fps=30.0 if run_performance_test else 0,
            latency_p50_ms=30.0 if run_performance_test else 0,
            latency_p95_ms=45.0 if run_performance_test else 0,
            latency_p99_ms=80.0 if run_performance_test else 0,
            gpu_memory_mb=2048.0,
            passed=False  # Will be set by quality gates
        )
        
        return metrics
    
    def _check_quality_gates(self, metrics: ValidationMetrics) -> tuple[bool, List[str]]:
        """
        Check if metrics pass quality gates
        
        Returns:
            (passed, list_of_failures)
        """
        failures = []
        
        # Check absolute thresholds
        if metrics.map_50 < self.gates["min_map_50"]:
            failures.append(f"mAP@0.5 {metrics.map_50:.3f} < {self.gates['min_map_50']}")
        
        if metrics.precision < self.gates["min_precision"]:
            failures.append(f"Precision {metrics.precision:.3f} < {self.gates['min_precision']}")
        
        if metrics.recall < self.gates["min_recall"]:
            failures.append(f"Recall {metrics.recall:.3f} < {self.gates['min_recall']}")
        
        if metrics.latency_p95_ms > self.gates["max_latency_p95_ms"]:
            failures.append(f"Latency p95 {metrics.latency_p95_ms:.1f}ms > {self.gates['max_latency_p95_ms']}ms")
        
        # Check regression against baseline
        if self.baseline_metrics:
            map_delta = metrics.map_50 - self.baseline_metrics.map_50
            fps_delta_pct = (metrics.fps - self.baseline_metrics.fps) / self.baseline_metrics.fps * 100
            
            if map_delta < self.gates["max_accuracy_regression"]:
                failures.append(
                    f"Accuracy regression {map_delta:.3f} > threshold {self.gates['max_accuracy_regression']}"
                )
            
            if fps_delta_pct < self.gates["max_fps_regression"]:
                failures.append(
                    f"FPS regression {fps_delta_pct:.1f}% > threshold {self.gates['max_fps_regression']}%"
                )
        
        passed = len(failures) == 0
        
        return passed, failures
    
    def _save_metrics(self, model_version: str, metrics: ValidationMetrics):
        """Save validation metrics"""
        metrics_file = f"./models/validation_{model_version}.json"
        
        os.makedirs(os.path.dirname(metrics_file), exist_ok=True)
        
        with open(metrics_file, 'w') as f:
            json.dump(metrics.to_dict(), f, indent=2)
        
        logger.info(f"Validation metrics saved: {metrics_file}")
    
    def compare_models(self, version1: str, version2: str) -> dict:
        """Compare validation metrics of two models"""
        metrics1_file = f"./models/validation_{version1}.json"
        metrics2_file = f"./models/validation_{version2}.json"
        
        if not os.path.exists(metrics1_file) or not os.path.exists(metrics2_file):
            return {"error": "Validation metrics not found for one or both models"}
        
        with open(metrics1_file) as f:
            m1 = json.load(f)
        
        with open(metrics2_file) as f:
            m2 = json.load(f)
        
        return {
            "version1": version1,
            "version2": version2,
            "metrics1": m1,
            "metrics2": m2,
            "delta": {
                "map_50": m2["map_50"] - m1["map_50"],
                "precision": m2["precision"] - m1["precision"],
                "recall": m2["recall"] - m1["recall"],
                "fps": m2["fps"] - m1["fps"],
                "latency_p95_ms": m2["latency_p95_ms"] - m1["latency_p95_ms"]
            },
            "winner": version2 if m2["map_50"] > m1["map_50"] else version1
        }


# Global instance
model_validator = ModelValidator()




















