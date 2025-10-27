#!/usr/bin/env python3
"""
Verolux Backend Server - Fixed Version
Full production backend with AI model loading
"""
import os
import logging
import time
import json
import cv2
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime
from typing import List, Dict, Optional

# Import performance optimizations
try:
    from performance_optimizer import BatchInferenceEngine, DualStreamCapture, AsyncFrameGrabber
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False
    print("⚠️ Performance optimizer not available, using standard processing")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Verolux Backend", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and connections
model = None
connections = []
batch_engine = None
dual_stream = None

# Gate SOP Configuration
gate_zones = []
gate_sop_rules = {
    "P_ENTERED_GA": {"alert_level": "low", "description": "Person entered gate area"},
    "G_ANCHORED": {"alert_level": "medium", "description": "Gate anchored"},
    "CONTACT_STARTED": {"alert_level": "high", "description": "Contact started"},
    "BODY_CHECK_REQUIRED": {"alert_level": "medium", "description": "Body check required"},
    "UNAUTHORIZED_ACCESS": {"alert_level": "critical", "description": "Unauthorized access detected"}
}

# Session data for reporting
session_data = {
    "session_id": None,
    "start_time": None,
    "total_detections": 0,
    "total_alerts": 0,
    "gate_events": [],
    "detection_history": [],
    "alert_history": []
}

@app.get("/")
def read_root():
    return {"message": "Verolux Backend is running", "status": "ok"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "verolux-backend", 
        "model_loaded": model is not None,
        "model": {
            "loaded": model is not None,
            "device": "cuda" if model is not None else "cpu",
            "framework": "YOLOv8" if model is not None else "none"
        },
        "websocket_endpoints": [
            "/ws/detections",
            "/ws/gate-check", 
            "/ws/alerts"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
def status():
    return {
        "status": "running",
        "version": "1.0.0",
        "service": "verolux-backend",
        "model_loaded": model is not None
    }

@app.get("/stream")
def stream_endpoint(source: str = "webcam:0"):
    """Stream endpoint for video sources"""
    return {
        "message": "Stream endpoint active",
        "source": source,
        "model_loaded": model is not None,
        "status": "ready"
    }

@app.get("/model-status")
def model_status():
    """Get detailed model status for frontend"""
    return {
        "model_loaded": model is not None,
        "model_type": "YOLOv8" if model is not None else None,
        "status": "ready" if model is not None else "not_loaded",
        "message": "AI model loaded and ready" if model is not None else "AI model not loaded"
    }

@app.get("/gate-config")
def get_gate_config():
    """Get current gate SOP configuration"""
    return {
        "zones": gate_zones,
        "rules": gate_sop_rules,
        "status": "configured" if gate_zones else "not_configured"
    }

@app.get("/api/config/gate-area")
def get_gate_area():
    """Get gate area configuration"""
    return {
        "polygon": [
            [0.3, 0.2],
            [0.7, 0.2], 
            [0.7, 0.8],
            [0.3, 0.8]
        ],
        "status": "configured"
    }

@app.post("/api/config/gate-area")
async def update_gate_area(request: Request):
    """Update gate area configuration"""
    try:
        data = await request.json()
        # Store the configuration (in a real app, save to database)
        logger.info(f"Gate area updated: {data}")
        return {"status": "success", "message": "Gate area updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/guard-anchor")
def get_guard_anchor():
    """Get guard anchor configuration"""
    return {
        "polygon": [
            [0.1, 0.15],
            [0.25, 0.15],
            [0.25, 0.85],
            [0.1, 0.85]
        ],
        "status": "configured"
    }

@app.post("/api/config/guard-anchor")
async def update_guard_anchor(request: Request):
    """Update guard anchor configuration"""
    try:
        data = await request.json()
        # Store the configuration (in a real app, save to database)
        logger.info(f"Guard anchor updated: {data}")
        return {"status": "success", "message": "Guard anchor updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/gate-rules")
def get_gate_rules():
    """Get gate rules configuration"""
    return {
        "timers": {
            "person_min_dwell_s": 6.0,
            "guard_min_dwell_s": 3.0,
            "interaction_min_overlap_s": 1.2
        },
        "proximity": {
            "center_dist_scale": 0.35
        },
        "scoring": {
            "threshold": 0.9
        },
        "status": "configured"
    }

@app.post("/api/config/gate-rules")
async def update_gate_rules(request: Request):
    """Update gate rules configuration"""
    try:
        data = await request.json()
        # Store the configuration (in a real app, save to database)
        logger.info(f"Gate rules updated: {data}")
        return {"status": "success", "message": "Gate rules updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gate-config")
def update_gate_config(config: Dict):
    """Update gate SOP configuration"""
    global gate_zones
    if "zones" in config:
        gate_zones = config["zones"]
    return {"status": "updated", "zones": len(gate_zones)}

@app.get("/session-data")
def get_session_data():
    """Get current session data for reporting"""
    return session_data

@app.post("/start-session")
def start_session():
    """Start a new monitoring session"""
    global session_data
    session_data = {
        "session_id": f"session_{int(time.time())}",
        "start_time": datetime.now().isoformat(),
        "total_detections": 0,
        "total_alerts": 0,
        "gate_events": [],
        "detection_history": [],
        "alert_history": []
    }
    return {"status": "started", "session_id": session_data["session_id"]}

@app.post("/generate-report")
def generate_report():
    """Generate a comprehensive report"""
    if not session_data["session_id"]:
        raise HTTPException(status_code=400, detail="No active session")
    
    report = {
        "session_id": session_data["session_id"],
        "start_time": session_data["start_time"],
        "duration": time.time() - time.mktime(datetime.fromisoformat(session_data["start_time"]).timetuple()),
        "total_detections": session_data["total_detections"],
        "total_alerts": session_data["total_alerts"],
        "gate_events": session_data["gate_events"],
        "detection_summary": {
            "total_objects": len(session_data["detection_history"]),
            "unique_classes": list(set([d.get("class", "unknown") for d in session_data["detection_history"]]))
        },
        "alert_summary": {
            "critical": len([a for a in session_data["alert_history"] if a.get("level") == "critical"]),
            "high": len([a for a in session_data["alert_history"] if a.get("level") == "high"]),
            "medium": len([a for a in session_data["alert_history"] if a.get("level") == "medium"]),
            "low": len([a for a in session_data["alert_history"] if a.get("level") == "low"])
        },
        "generated_at": datetime.now().isoformat()
    }
    
    return report

@app.get("/video-files")
def list_video_files():
    """List available video files"""
    video_files = []
    
    # Check Frontend/public directory
    public_dir = "../Frontend/public"
    if os.path.exists(public_dir):
        for file in os.listdir(public_dir):
            if file.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                video_files.append({
                    "name": file,
                    "path": f"file:{file}",
                    "size": os.path.getsize(os.path.join(public_dir, file))
                })
    
    return {"video_files": video_files}

@app.get("/download-report")
def download_report():
    """Download the current session report as JSON"""
    if not session_data["session_id"]:
        raise HTTPException(status_code=400, detail="No active session")
    
    report = {
        "session_id": session_data["session_id"],
        "start_time": session_data["start_time"],
        "duration": time.time() - time.mktime(datetime.fromisoformat(session_data["start_time"]).timetuple()),
        "total_detections": session_data["total_detections"],
        "total_alerts": session_data["total_alerts"],
        "gate_events": session_data["gate_events"],
        "detection_summary": {
            "total_objects": len(session_data["detection_history"]),
            "unique_classes": list(set([d.get("class", "unknown") for d in session_data["detection_history"]]))
        },
        "alert_summary": {
            "critical": len([a for a in session_data["alert_history"] if a.get("level") == "critical"]),
            "high": len([a for a in session_data["alert_history"] if a.get("level") == "high"]),
            "medium": len([a for a in session_data["alert_history"] if a.get("level") == "medium"]),
            "low": len([a for a in session_data["alert_history"] if a.get("level") == "low"])
        },
        "generated_at": datetime.now().isoformat()
    }
    
    # Save report to file
    report_filename = f"report_{session_data['session_id']}.json"
    report_path = f"../Frontend/public/{report_filename}"
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return FileResponse(
        path=report_path,
        filename=report_filename,
        media_type='application/json'
    )

@app.websocket("/ws/detections")
async def websocket_endpoint(websocket: WebSocket, source: str = "webcam:0"):
    await websocket.accept()
    connections.append(websocket)
    
    try:
        # Parse source parameter
        if source.startswith("file:"):
            video_filename = source.replace("file:", "")
            # Check multiple possible locations for video file
            possible_paths = [
                f"../Frontend/public/{video_filename}",  # Frontend public directory
                f"../{video_filename}",                  # Root directory
                f"{video_filename}",                     # Current directory
                f"Frontend/public/{video_filename}"      # Relative from Backend
            ]
            
            video_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    video_path = path
                    logger.info(f"Found video file at: {video_path}")
                    break
            
            if video_path is None:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Video file not found: {video_filename}. Checked paths: {possible_paths}"
                }))
                return
        else:
            # Default to webcam
            video_path = 0
        
        # Start video processing
        import cv2
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            await websocket.send_text(json.dumps({
                "type": "error", 
                "message": f"Could not open video source: {video_path}"
            }))
            return
        
        frame_count = 0
        start_time = time.time()
        
        # Get video properties for proper coordinate scaling
        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps_video = cap.get(cv2.CAP_PROP_FPS)
        
        logger.info(f"Video properties: {video_width}x{video_height}, {total_frames} frames, {fps_video} FPS")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                # Loop the video if it reaches the end
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                frame_count = 0
                start_time = time.time()
                continue
                
            frame_count += 1
            current_time = time.time()
            fps = frame_count / (current_time - start_time) if current_time > start_time else 0
            
            # Process frame with AI model if available (non-blocking)
            detections = []
            processing_time = 0
            
            if model is not None:
                start_process = time.time()
                try:
                    # Use optimized processing for better detection quality
                    results = model(frame, 
                                  imgsz=640,  # Larger input size for better detection
                                  conf=0.3,   # Lower confidence threshold for more detections
                                  iou=0.4,    # Better NMS for multiple objects
                                  max_det=50, # More detections allowed
                                  half=True,   # Use FP16 if available
                                  verbose=False)
                    processing_time = (time.time() - start_process) * 1000  # Convert to ms
                    
                    # Only log every 10th frame to reduce logging overhead
                    if frame_count % 10 == 0:
                        logger.info(f"Processing frame {frame_count}: {video_width}x{video_height}, {len(results)} results")
                    
                    for result in results:
                        if result.boxes is not None:
                            for box in result.boxes:
                                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                                confidence = box.conf[0].cpu().numpy()
                                class_id = int(box.cls[0].cpu().numpy())
                                class_name = model.names[class_id]
                                
                                # Ensure coordinates are within video bounds
                                x1 = max(0, min(x1, video_width))
                                y1 = max(0, min(y1, video_height))
                                x2 = max(0, min(x2, video_width))
                                y2 = max(0, min(y2, video_height))
                                
                                detection = {
                                    "id": len(detections) + 1,
                                    "class": class_name,
                                    "confidence": float(confidence),
                                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                                    "trackId": len(detections) + 1,
                                    "timestamp": current_time,
                                    "video_dimensions": {
                                        "width": video_width,
                                        "height": video_height
                                    }
                                }
                                detections.append(detection)
                                
                                # Only log detections every 10th frame
                                if frame_count % 10 == 0:
                                    logger.info(f"Detection: {class_name} {confidence:.2f} at [{x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}]")
                                
                                # Update session data
                                session_data["total_detections"] += 1
                                session_data["detection_history"].append(detection)
                except Exception as e:
                    logger.error(f"AI processing error: {e}")
                    processing_time = 0
            
            # Check for zone violations if zones are configured
            violations = []
            alerts = []
            if gate_zones and detections:
                violations = check_zone_violations(detections, gate_zones)
                for violation in violations:
                    alert = generate_alert("zone_violation", violation)
                    alerts.append(alert)
                    session_data["total_alerts"] += 1
                    session_data["alert_history"].append(alert)
            
            # Send detection data with alerts (non-blocking)
            try:
                await websocket.send_text(json.dumps({
                    "type": "detection",
                    "detections": detections,
                    "violations": violations,
                    "alerts": alerts,
                    "fps": fps,
                    "processing_time": processing_time,
                    "active_tracks": len(detections),
                    "frame": frame_count,
                    "timestamp": current_time
                }))
            except Exception as e:
                logger.error(f"WebSocket send error: {e}")
                break
            
            # Control frame rate (target 20 FPS for good balance) - use async sleep
            await asyncio.sleep(1/20)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
    except WebSocketDisconnect:
        connections.remove(websocket)
    finally:
        if 'cap' in locals():
            cap.release()

@app.websocket("/ws/gate-check")
async def gate_check_websocket(websocket: WebSocket, source: str = "webcam:0"):
    await websocket.accept()
    connections.append(websocket)
    
    try:
        # Simulate gate check events for demonstration
        event_id = 1
        while True:
            # Simulate gate events based on time
            current_time = time.time()
            cycle = int(current_time) % 20  # 20-second cycle
            
            events = []
            alerts = []
            
            if cycle == 5:
                event = {
                    "id": event_id,
                    "type": "P_ENTERED_GA",
                    "timestamp": current_time * 1000,
                    "confidence": 0.95
                }
                events.append(event)
                session_data["gate_events"].append(event)
                event_id += 1
                
            elif cycle == 10:
                event = {
                    "id": event_id,
                    "type": "G_ANCHORED",
                    "timestamp": current_time * 1000,
                    "confidence": 0.88
                }
                events.append(event)
                session_data["gate_events"].append(event)
                event_id += 1
                
            elif cycle == 15:
                event = {
                    "id": event_id,
                    "type": "CONTACT_STARTED",
                    "timestamp": current_time * 1000,
                    "confidence": 0.92
                }
                events.append(event)
                session_data["gate_events"].append(event)
                event_id += 1
                
                # Generate alert for contact
                alert = {
                    "id": event_id,
                    "type": "high",
                    "level": "high",
                    "message": "Contact detected in gate area",
                    "timestamp": current_time * 1000
                }
                alerts.append(alert)
                session_data["total_alerts"] += 1
                session_data["alert_history"].append(alert)
                event_id += 1
            
            # Simulate body check status
            body_check_score = min(100, (cycle * 5) % 100)
            body_check = {
                "handToTorsoDetected": body_check_score > 25,
                "reachGestureDetected": body_check_score > 50,
                "proximityMet": body_check_score > 75,
                "score": body_check_score,
                "completed": body_check_score >= 100
            }
            
            # Send gate check data
            await websocket.send_text(json.dumps({
                "type": "gate_check",
                "events": events,
                "alerts": alerts,
                "bodyCheck": body_check,
                "timestamp": current_time
            }))
            
            # Wait 1 second before next update
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Gate check WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
    except WebSocketDisconnect:
        connections.remove(websocket)

@app.websocket("/ws/alerts")
async def alerts_websocket(websocket: WebSocket):
    """WebSocket for real-time alerts and notifications"""
    await websocket.accept()
    connections.append(websocket)
    
    try:
        while True:
            # Check for new alerts in session data
            if session_data["alert_history"]:
                latest_alerts = session_data["alert_history"][-5:]  # Get last 5 alerts
                await websocket.send_text(json.dumps({
                    "type": "alerts",
                    "alerts": latest_alerts,
                    "total_alerts": session_data["total_alerts"],
                    "timestamp": time.time()
                }))
            
            time.sleep(2)  # Check every 2 seconds
            
    except Exception as e:
        logger.error(f"Alerts WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
    except WebSocketDisconnect:
        connections.remove(websocket)

def check_zone_violations(detections, zones):
    """Check if detections violate any configured zones"""
    violations = []
    
    for detection in detections:
        bbox = detection["bbox"]
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2
        
        for zone in zones:
            if zone.get("type") == "restricted":
                # Check if detection center is within restricted zone
                if (zone["x1"] <= center_x <= zone["x2"] and 
                    zone["y1"] <= center_y <= zone["y2"]):
                    violations.append({
                        "detection_id": detection["id"],
                        "zone_id": zone["id"],
                        "class": detection["class"],
                        "confidence": detection["confidence"],
                        "timestamp": detection["timestamp"]
                    })
    
    return violations

def generate_alert(violation_type, data):
    """Generate alert based on violation type"""
    alert_levels = {
        "zone_violation": "high",
        "unauthorized_access": "critical",
        "contact_detected": "medium",
        "body_check_required": "low"
    }
    
    return {
        "id": len(session_data["alert_history"]) + 1,
        "type": violation_type,
        "level": alert_levels.get(violation_type, "low"),
        "message": f"{violation_type.replace('_', ' ').title()} detected",
        "data": data,
        "timestamp": time.time() * 1000
    }

def load_model():
    """Load the AI model"""
    global model
    try:
        # Try to import and load YOLOv8 model
        from ultralytics import YOLO
        
        # Check for model file - use weight.pt from root directory
        model_path = "../weight.pt"
        if not os.path.exists(model_path):
            model_path = "weight.pt"
        
        if os.path.exists(model_path):
            logger.info(f"Loading model from {model_path}")
            model = YOLO(model_path)
            logger.info("Model loaded successfully")
            return True
        else:
            logger.warning("Model file not found, running without AI model")
            return False
    except ImportError:
        logger.warning("Ultralytics not available, running without AI model")
        return False
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize the backend on startup"""
    global batch_engine, dual_stream
    logger.info("Starting Verolux Backend...")
    
    # Load AI model
    model_loaded = load_model()
    
    if model_loaded:
        logger.info("AI model loaded successfully")
        
        # Initialize performance optimizations if available
        if PERFORMANCE_AVAILABLE:
            try:
                # Initialize batch inference engine for higher FPS
                batch_engine = BatchInferenceEngine(model, batch_size=4, timeout=0.015)
                batch_engine.start()
                logger.info("✅ Batch inference engine started (batch_size=4)")
                
                # Initialize dual stream capture for reduced GPU load
                dual_stream = DualStreamCapture("webcam:0", detection_scale=0.6)
                logger.info("✅ Dual stream capture initialized (scale=0.6)")
                
            except Exception as e:
                logger.warning(f"Performance optimizations failed: {e}")
                batch_engine = None
                dual_stream = None
    else:
        logger.warning("Running without AI model")
    
    # Initialize session
    session_data["session_id"] = f"session_{int(time.time())}"
    session_data["start_time"] = datetime.now().isoformat()
    
    logger.info("Backend startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global batch_engine, dual_stream
    logger.info("Shutting down backend...")
    
    # Stop performance optimizations
    if batch_engine:
        batch_engine.stop()
        logger.info("🛑 Batch inference engine stopped")
    
    if dual_stream:
        dual_stream.release()
        logger.info("🛑 Dual stream capture stopped")
    
    # Close all WebSocket connections
    for connection in connections:
        try:
            await connection.close()
        except:
            pass
    connections.clear()
    logger.info("Backend shutdown complete")

if __name__ == "__main__":
    print("Starting Verolux Backend with AI Model...")
    print("Backend will be available at: http://localhost:8000")
    print("Health check: http://localhost:8000/health")
    print("API docs: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

