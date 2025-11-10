#!/usr/bin/env python3
"""
Configuration API for Gate Security System
Handles visual editor configuration updates
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Gate Security Configuration API")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConfigurationManager:
    """Manages gate security configuration files"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
        
        # Configuration file paths
        self.gate_rules_path = os.path.join(config_dir, "gate_rules.demo.json")
        self.gate_area_path = os.path.join(config_dir, "gate_A1_polygon.json")
        self.guard_anchor_path = os.path.join(config_dir, "guard_anchor_A1_polygon.json")
        
    def load_gate_rules(self) -> Dict[str, Any]:
        """Load main gate rules configuration"""
        try:
            with open(self.gate_rules_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_gate_rules()
    
    def save_gate_rules(self, config: Dict[str, Any]) -> bool:
        """Save main gate rules configuration"""
        try:
            # Create backup
            if os.path.exists(self.gate_rules_path):
                backup_path = f"{self.gate_rules_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.gate_rules_path, backup_path)
            
            with open(self.gate_rules_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving gate rules: {e}")
            return False
    
    def load_gate_area(self) -> Dict[str, Any]:
        """Load gate area polygon configuration"""
        try:
            with open(self.gate_area_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_gate_area()
    
    def save_gate_area(self, config: Dict[str, Any]) -> bool:
        """Save gate area polygon configuration"""
        try:
            # Create backup
            if os.path.exists(self.gate_area_path):
                backup_path = f"{self.gate_area_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.gate_area_path, backup_path)
            
            with open(self.gate_area_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving gate area: {e}")
            return False
    
    def load_guard_anchor(self) -> Dict[str, Any]:
        """Load guard anchor polygon configuration"""
        try:
            with open(self.guard_anchor_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_guard_anchor()
    
    def save_guard_anchor(self, config: Dict[str, Any]) -> bool:
        """Save guard anchor polygon configuration"""
        try:
            # Create backup
            if os.path.exists(self.guard_anchor_path):
                backup_path = f"{self.guard_anchor_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.guard_anchor_path, backup_path)
            
            with open(self.guard_anchor_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving guard anchor: {e}")
            return False
    
    def _get_default_gate_rules(self) -> Dict[str, Any]:
        """Get default gate rules configuration"""
        return {
            "gate_id": "A1",
            "zones": {
                "gate_area": "gate_A1_polygon.json",
                "guard_anchor": "guard_anchor_A1_polygon.json"
            },
            "classes": {
                "person": [0],
                "guard_hint_classes": [0]
            },
            "timers": {
                "person_min_dwell_s": 6.0,
                "guard_min_dwell_s": 3.0,
                "interaction_min_overlap_s": 1.2,
                "occlusion_grace_s": 1.0,
                "contact_debounce_s": 0.4,
                "session_timeout_s": 8.0
            },
            "proximity": {
                "center_dist_scale": 0.35,
                "iou_min": 0.03,
                "hands_toward_torso_margin": 0.12
            },
            "pose": {
                "use_pose": True,
                "hand_to_torso_thresh": 0.28,
                "reach_velocity_thresh": 0.6
            },
            "guard_anchor_logic": {
                "mode": "either",
                "anchor_required_fraction": 0.6
            },
            "scoring": {
                "base": 0.6,
                "contact_bonus": 0.2,
                "pose_bonus": 0.15,
                "reid_persistence_bonus": 0.05,
                "threshold": 0.9
            },
            "visualization": {
                "save_snapshots": True,
                "snapshot_dir": "snapshots",
                "draw_zones": True,
                "draw_tracks": True
            },
            "noise_filtering": {
                "min_box_height_px": 40,
                "jitter_smooth_window": 5,
                "multi_frame_consensus": 3,
                "reid_merge_time_s": 0.8,
                "reid_merge_distance_m": 0.5
            }
        }
    
    def _get_default_gate_area(self) -> Dict[str, Any]:
        """Get default gate area configuration"""
        return {
            "zone_id": "gate_A1",
            "zone_type": "gate_area",
            "polygon": [
                [0.30, 0.20],
                [0.70, 0.20],
                [0.70, 0.80],
                [0.30, 0.80]
            ],
            "description": "Main gate area where security check must occur",
            "normalized": True,
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_default_guard_anchor(self) -> Dict[str, Any]:
        """Get default guard anchor configuration"""
        return {
            "zone_id": "guard_anchor_A1",
            "zone_type": "guard_anchor",
            "polygon": [
                [0.10, 0.15],
                [0.25, 0.15],
                [0.25, 0.85],
                [0.10, 0.85]
            ],
            "description": "Guard anchor zone - where guard should stand during check",
            "normalized": True,
            "last_updated": datetime.now().isoformat()
        }

# Initialize configuration manager
config_manager = ConfigurationManager()

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Gate Security Configuration API",
        "version": "1.0.0",
        "endpoints": {
            "gate_rules": "/api/config/gate-rules",
            "gate_area": "/api/config/gate-area",
            "guard_anchor": "/api/config/guard-anchor",
            "validate": "/api/config/validate"
        }
    }

@app.get("/api/config/gate-rules")
async def get_gate_rules():
    """Get main gate rules configuration"""
    try:
        config = config_manager.load_gate_rules()
        return {
            "status": "success",
            "config": config,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config/gate-rules")
async def update_gate_rules(request: Request):
    """Update main gate rules configuration"""
    try:
        data = await request.json()
        
        # Load current config and merge updates
        current_config = config_manager.load_gate_rules()
        
        # Update specific sections
        if "timers" in data:
            current_config["timers"].update(data["timers"])
        if "proximity" in data:
            current_config["proximity"].update(data["proximity"])
        if "scoring" in data:
            current_config["scoring"].update(data["scoring"])
        if "pose" in data:
            current_config["pose"].update(data["pose"])
        
        # Add metadata
        current_config["last_updated"] = datetime.now().isoformat()
        current_config["updated_by"] = "visual_editor"
        
        # Save configuration
        if config_manager.save_gate_rules(current_config):
            return {
                "status": "success",
                "message": "Gate rules configuration updated successfully",
                "config": current_config
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save configuration")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/gate-area")
async def get_gate_area():
    """Get gate area polygon configuration"""
    try:
        config = config_manager.load_gate_area()
        return {
            "status": "success",
            "config": config,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config/gate-area")
async def update_gate_area(request: Request):
    """Update gate area polygon configuration"""
    try:
        data = await request.json()
        
        # Validate polygon data
        if "polygon" not in data:
            raise HTTPException(status_code=400, detail="Polygon data is required")
        
        # Load current config and update
        current_config = config_manager.load_gate_area()
        current_config["polygon"] = data["polygon"]
        current_config["last_updated"] = datetime.now().isoformat()
        current_config["updated_by"] = "visual_editor"
        
        # Save configuration
        if config_manager.save_gate_area(current_config):
            return {
                "status": "success",
                "message": "Gate area configuration updated successfully",
                "config": current_config
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save configuration")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/guard-anchor")
async def get_guard_anchor():
    """Get guard anchor polygon configuration"""
    try:
        config = config_manager.load_guard_anchor()
        return {
            "status": "success",
            "config": config,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config/guard-anchor")
async def update_guard_anchor(request: Request):
    """Update guard anchor polygon configuration"""
    try:
        data = await request.json()
        
        # Validate polygon data
        if "polygon" not in data:
            raise HTTPException(status_code=400, detail="Polygon data is required")
        
        # Load current config and update
        current_config = config_manager.load_guard_anchor()
        current_config["polygon"] = data["polygon"]
        current_config["last_updated"] = datetime.now().isoformat()
        current_config["updated_by"] = "visual_editor"
        
        # Save configuration
        if config_manager.save_guard_anchor(current_config):
            return {
                "status": "success",
                "message": "Guard anchor configuration updated successfully",
                "config": current_config
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save configuration")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config/validate")
async def validate_configuration():
    """Validate current configuration"""
    try:
        gate_rules = config_manager.load_gate_rules()
        gate_area = config_manager.load_gate_area()
        guard_anchor = config_manager.load_guard_anchor()
        
        # Basic validation
        validation_results = {
            "gate_rules": {
                "valid": True,
                "issues": []
            },
            "gate_area": {
                "valid": True,
                "issues": []
            },
            "guard_anchor": {
                "valid": True,
                "issues": []
            }
        }
        
        # Validate gate area polygon
        if len(gate_area.get("polygon", [])) < 3:
            validation_results["gate_area"]["valid"] = False
            validation_results["gate_area"]["issues"].append("Gate area polygon must have at least 3 points")
        
        # Validate guard anchor polygon
        if len(guard_anchor.get("polygon", [])) < 3:
            validation_results["guard_anchor"]["valid"] = False
            validation_results["guard_anchor"]["issues"].append("Guard anchor polygon must have at least 3 points")
        
        # Validate timer values
        timers = gate_rules.get("timers", {})
        if timers.get("person_min_dwell_s", 0) <= 0:
            validation_results["gate_rules"]["valid"] = False
            validation_results["gate_rules"]["issues"].append("Person min dwell time must be greater than 0")
        
        if timers.get("guard_min_dwell_s", 0) <= 0:
            validation_results["gate_rules"]["valid"] = False
            validation_results["gate_rules"]["issues"].append("Guard min dwell time must be greater than 0")
        
        # Validate scoring threshold
        scoring = gate_rules.get("scoring", {})
        threshold = scoring.get("threshold", 0)
        if not (0 <= threshold <= 1):
            validation_results["gate_rules"]["valid"] = False
            validation_results["gate_rules"]["issues"].append("Score threshold must be between 0 and 1")
        
        overall_valid = all(result["valid"] for result in validation_results.values())
        
        return {
            "status": "success",
            "overall_valid": overall_valid,
            "validation_results": validation_results,
            "validated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/backup")
async def create_backup():
    """Create backup of current configuration"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"config_backup_{timestamp}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copy configuration files
        import shutil
        config_files = [
            "gate_rules.demo.json",
            "gate_A1_polygon.json",
            "guard_anchor_A1_polygon.json"
        ]
        
        for file_name in config_files:
            src = os.path.join(config_manager.config_dir, file_name)
            if os.path.exists(src):
                dst = os.path.join(backup_dir, file_name)
                shutil.copy2(src, dst)
        
        return {
            "status": "success",
            "message": f"Backup created successfully",
            "backup_dir": backup_dir,
            "backup_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Gate Security Configuration API")
    print("=" * 60)
    print("⚙️ Configuration Management System")
    print("🎨 Visual Editor Support")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8005)




























