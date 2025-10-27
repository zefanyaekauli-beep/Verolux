"""
Model Registry and Versioning System
Manages model versions, A/B testing, and safe rollbacks
"""
import os
import json
import time
import shutil
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, List
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ModelFramework(Enum):
    """Supported model frameworks"""
    PYTORCH = "pytorch"
    TENSORRT = "tensorrt"
    ONNX = "onnx"
    OPENVINO = "openvino"


class ModelPrecision(Enum):
    """Model precision types"""
    FP32 = "fp32"
    FP16 = "fp16"
    INT8 = "int8"
    MIXED = "mixed"


class ModelStatus(Enum):
    """Model deployment status"""
    REGISTERED = "registered"      # Registered but not tested
    VALIDATED = "validated"         # Passed validation
    CANARY = "canary"              # In A/B test (partial traffic)
    ACTIVE = "active"              # Fully deployed
    DEPRECATED = "deprecated"       # Marked for removal
    FAILED = "failed"              # Failed validation


@dataclass
class ModelMetrics:
    """Model performance metrics"""
    map_50: float = 0.0          # mAP@0.5
    map_95: float = 0.0          # mAP@0.5:0.95
    precision: float = 0.0
    recall: float = 0.0
    fps: float = 0.0
    latency_ms: float = 0.0
    gpu_memory_mb: float = 0.0
    validation_accuracy: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ModelVersion:
    """Model version metadata"""
    version: str
    framework: ModelFramework
    precision: ModelPrecision
    path: str
    status: ModelStatus
    created_at: float = field(default_factory=time.time)
    activated_at: Optional[float] = None
    deprecated_at: Optional[float] = None
    metrics: ModelMetrics = field(default_factory=ModelMetrics)
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    created_by: str = ""
    parent_version: Optional[str] = None
    
    @property
    def age_days(self) -> float:
        """Age of model in days"""
        return (time.time() - self.created_at) / 86400
    
    @property
    def is_active(self) -> bool:
        """Check if model is active"""
        return self.status == ModelStatus.ACTIVE
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "version": self.version,
            "framework": self.framework.value,
            "precision": self.precision.value,
            "path": self.path,
            "status": self.status.value,
            "created_at": self.created_at,
            "activated_at": self.activated_at,
            "deprecated_at": self.deprecated_at,
            "metrics": self.metrics.to_dict(),
            "tags": self.tags,
            "notes": self.notes,
            "created_by": self.created_by,
            "parent_version": self.parent_version,
            "age_days": round(self.age_days, 2)
        }


class ModelRegistry:
    """
    Model versioning and lifecycle management
    
    Features:
    - Version tracking
    - A/B testing (canary deployments)
    - Safe rollbacks
    - Performance comparison
    - Automatic backups
    """
    
    def __init__(self, 
                 registry_path: str = "./models/registry.json",
                 models_dir: str = "./models"):
        """
        Initialize model registry
        
        Args:
            registry_path: Path to registry JSON file
            models_dir: Directory containing model files
        """
        self.registry_path = registry_path
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.models: Dict[str, ModelVersion] = {}
        self._load_registry()
        
        logger.info(f"Model registry initialized with {len(self.models)} models")
    
    def _load_registry(self):
        """Load registry from disk"""
        if not os.path.exists(self.registry_path):
            logger.info("No existing registry found, creating new one")
            self._save_registry()
            return
        
        try:
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
            
            # Deserialize models
            for version, model_data in data.items():
                self.models[version] = self._deserialize_model(model_data)
            
            logger.info(f"Loaded {len(self.models)} models from registry")
            
        except Exception as e:
            logger.error(f"Error loading registry: {e}")
            # Backup corrupted registry
            if os.path.exists(self.registry_path):
                backup_path = f"{self.registry_path}.backup_{int(time.time())}"
                shutil.copy(self.registry_path, backup_path)
                logger.info(f"Backed up corrupted registry to {backup_path}")
    
    def _save_registry(self):
        """Save registry to disk"""
        try:
            # Serialize models
            data = {
                version: model.to_dict()
                for version, model in self.models.items()
            }
            
            # Create backup before saving
            if os.path.exists(self.registry_path):
                backup_path = f"{self.registry_path}.backup"
                shutil.copy(self.registry_path, backup_path)
            
            # Save
            with open(self.registry_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Registry saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving registry: {e}")
    
    def _deserialize_model(self, data: dict) -> ModelVersion:
        """Deserialize model from dictionary"""
        return ModelVersion(
            version=data["version"],
            framework=ModelFramework(data["framework"]),
            precision=ModelPrecision(data["precision"]),
            path=data["path"],
            status=ModelStatus(data["status"]),
            created_at=data.get("created_at", time.time()),
            activated_at=data.get("activated_at"),
            deprecated_at=data.get("deprecated_at"),
            metrics=ModelMetrics(**data.get("metrics", {})),
            tags=data.get("tags", []),
            notes=data.get("notes", ""),
            created_by=data.get("created_by", ""),
            parent_version=data.get("parent_version")
        )
    
    def register_model(self,
                      version: str,
                      path: str,
                      framework: ModelFramework,
                      precision: ModelPrecision,
                      metrics: Optional[ModelMetrics] = None,
                      tags: Optional[List[str]] = None,
                      notes: str = "",
                      created_by: str = "",
                      parent_version: Optional[str] = None) -> ModelVersion:
        """
        Register a new model version
        
        Args:
            version: Version identifier (e.g., "v1.2.3")
            path: Path to model file
            framework: Model framework
            precision: Model precision
            metrics: Performance metrics
            tags: Optional tags
            notes: Release notes
            created_by: Creator name
            parent_version: Parent model version
            
        Returns:
            ModelVersion object
        """
        if version in self.models:
            logger.warning(f"Model {version} already registered, will overwrite")
        
        # Verify path exists
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        # Create model version
        model = ModelVersion(
            version=version,
            framework=framework,
            precision=precision,
            path=path,
            status=ModelStatus.REGISTERED,
            metrics=metrics or ModelMetrics(),
            tags=tags or [],
            notes=notes,
            created_by=created_by,
            parent_version=parent_version
        )
        
        self.models[version] = model
        self._save_registry()
        
        logger.info(f"Registered model {version} ({framework.value}/{precision.value})")
        
        return model
    
    def update_metrics(self, version: str, metrics: ModelMetrics):
        """Update model metrics"""
        if version not in self.models:
            raise ValueError(f"Model {version} not found")
        
        self.models[version].metrics = metrics
        self._save_registry()
        
        logger.info(f"Updated metrics for model {version}")
    
    def validate_model(self, version: str):
        """Mark model as validated"""
        if version not in self.models:
            raise ValueError(f"Model {version} not found")
        
        self.models[version].status = ModelStatus.VALIDATED
        self._save_registry()
        
        logger.info(f"Model {version} marked as validated")
    
    def activate_model(self, version: str, canary: bool = False):
        """
        Activate a model version
        
        Args:
            version: Version to activate
            canary: If True, deploy as canary (A/B test)
        """
        if version not in self.models:
            raise ValueError(f"Model {version} not found")
        
        model = self.models[version]
        
        # Validate model is in good state
        if model.status not in [ModelStatus.VALIDATED, ModelStatus.CANARY]:
            logger.warning(
                f"Model {version} has status {model.status.value}, "
                f"activating anyway"
            )
        
        if canary:
            # Canary deployment
            model.status = ModelStatus.CANARY
            logger.info(f"Model {version} deployed as CANARY")
        else:
            # Full deployment - deactivate current active models
            for v in self.models.values():
                if v.status == ModelStatus.ACTIVE:
                    v.status = ModelStatus.DEPRECATED
                    v.deprecated_at = time.time()
                    logger.info(f"Model {v.version} deprecated")
            
            # Activate new model
            model.status = ModelStatus.ACTIVE
            model.activated_at = time.time()
            logger.info(f"✅ Model {version} ACTIVATED")
        
        self._save_registry()
    
    def rollback_model(self) -> Optional[ModelVersion]:
        """
        Rollback to previous active model
        
        Returns:
            Previous model version, or None if no previous version
        """
        # Find current active model
        current_active = self.get_active_model()
        
        if not current_active:
            logger.warning("No active model to rollback from")
            return None
        
        # Find most recent validated/deprecated model
        candidates = [
            model for model in self.models.values()
            if model.version != current_active.version
            and model.status in [ModelStatus.VALIDATED, ModelStatus.DEPRECATED]
        ]
        
        if not candidates:
            logger.error("No previous model version available for rollback")
            return None
        
        # Sort by activation time (most recent first)
        candidates.sort(
            key=lambda m: m.activated_at or m.created_at,
            reverse=True
        )
        
        previous = candidates[0]
        
        # Perform rollback
        logger.warning(f"⏪ ROLLBACK: {current_active.version} → {previous.version}")
        
        current_active.status = ModelStatus.FAILED
        self.activate_model(previous.version)
        
        return previous
    
    def get_active_model(self) -> Optional[ModelVersion]:
        """Get currently active model"""
        for model in self.models.values():
            if model.status == ModelStatus.ACTIVE:
                return model
        return None
    
    def get_canary_model(self) -> Optional[ModelVersion]:
        """Get canary model (if any)"""
        for model in self.models.values():
            if model.status == ModelStatus.CANARY:
                return model
        return None
    
    def get_model(self, version: str) -> Optional[ModelVersion]:
        """Get model by version"""
        return self.models.get(version)
    
    def list_models(self, 
                   status: Optional[ModelStatus] = None,
                   framework: Optional[ModelFramework] = None) -> List[ModelVersion]:
        """
        List models with optional filtering
        
        Args:
            status: Filter by status
            framework: Filter by framework
            
        Returns:
            List of matching models
        """
        models = list(self.models.values())
        
        if status:
            models = [m for m in models if m.status == status]
        
        if framework:
            models = [m for m in models if m.framework == framework]
        
        # Sort by creation time (newest first)
        models.sort(key=lambda m: m.created_at, reverse=True)
        
        return models
    
    def compare_models(self, version1: str, version2: str) -> dict:
        """
        Compare two model versions
        
        Returns:
            Comparison metrics
        """
        m1 = self.get_model(version1)
        m2 = self.get_model(version2)
        
        if not m1 or not m2:
            raise ValueError("One or both models not found")
        
        return {
            "version1": version1,
            "version2": version2,
            "metrics_diff": {
                "map_50": m2.metrics.map_50 - m1.metrics.map_50,
                "map_95": m2.metrics.map_95 - m1.metrics.map_95,
                "fps": m2.metrics.fps - m1.metrics.fps,
                "latency_ms": m2.metrics.latency_ms - m1.metrics.latency_ms,
                "gpu_memory_mb": m2.metrics.gpu_memory_mb - m1.metrics.gpu_memory_mb
            },
            "improvements": {
                "accuracy": m2.metrics.map_50 > m1.metrics.map_50,
                "speed": m2.metrics.fps > m1.metrics.fps,
                "memory": m2.metrics.gpu_memory_mb < m1.metrics.gpu_memory_mb
            },
            "model1": m1.to_dict(),
            "model2": m2.to_dict()
        }
    
    def get_registry_summary(self) -> dict:
        """Get registry summary statistics"""
        status_counts = {}
        for status in ModelStatus:
            count = len([m for m in self.models.values() if m.status == status])
            if count > 0:
                status_counts[status.value] = count
        
        framework_counts = {}
        for framework in ModelFramework:
            count = len([m for m in self.models.values() if m.framework == framework])
            if count > 0:
                framework_counts[framework.value] = count
        
        active_model = self.get_active_model()
        canary_model = self.get_canary_model()
        
        return {
            "total_models": len(self.models),
            "status_distribution": status_counts,
            "framework_distribution": framework_counts,
            "active_model": active_model.version if active_model else None,
            "canary_model": canary_model.version if canary_model else None,
            "registry_path": self.registry_path,
            "models_dir": str(self.models_dir)
        }
    
    def cleanup_old_models(self, keep_count: int = 5):
        """
        Cleanup old deprecated models
        
        Args:
            keep_count: Number of recent models to keep per framework
        """
        # Group by framework
        by_framework = {}
        for model in self.models.values():
            if model.framework not in by_framework:
                by_framework[model.framework] = []
            by_framework[model.framework].append(model)
        
        deleted = 0
        
        for framework, models in by_framework.items():
            # Sort by creation time
            models.sort(key=lambda m: m.created_at, reverse=True)
            
            # Keep active/canary models
            protected = [
                m for m in models
                if m.status in [ModelStatus.ACTIVE, ModelStatus.CANARY]
            ]
            
            # Keep N most recent deprecated models
            deprecated = [
                m for m in models
                if m.status == ModelStatus.DEPRECATED
            ]
            
            to_delete = deprecated[keep_count:]
            
            for model in to_delete:
                # Delete model file
                if os.path.exists(model.path):
                    os.remove(model.path)
                    logger.info(f"Deleted model file: {model.path}")
                
                # Remove from registry
                del self.models[model.version]
                deleted += 1
        
        if deleted > 0:
            self._save_registry()
            logger.info(f"Cleaned up {deleted} old models")
        
        return deleted


# Global instance
model_registry = ModelRegistry()













