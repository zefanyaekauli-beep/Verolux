#!/usr/bin/env python3
"""
Simple Video Inference System
- Uses weight.pt model for object detection
- Processes videoplayback.mp4
- Includes gate configuration features
- Optimized for performance
"""

import cv2
import numpy as np
import json
import time
import os
from ultralytics import YOLO
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Simple Video Inference System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
model = None
video_cap = None
current_frame = None
import threading
gate_config_lock = threading.Lock()
gate_config = {
    "gate_area": {"x": 0.3, "y": 0.2, "width": 0.4, "height": 0.6},
    "guard_anchor": {"x": 0.1, "y": 0.15, "width": 0.15, "height": 0.7},
    "enabled": True
}

def load_model():
    """Load the weight.pt model"""
    global model
    try:
        model_path = "../weight.pt"
        if not os.path.exists(model_path):
            model_path = "weight.pt"
        
        if os.path.exists(model_path):
            logger.info(f"Loading model from {model_path}")
            model = YOLO(model_path)
            logger.info("Model loaded successfully")
            return True
        else:
            logger.error("weight.pt file not found!")
            return False
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False

def initialize_video():
    """Initialize video capture with robust error handling"""
    global video_cap
    try:
        video_path = "../videoplayback.mp4"
        if not os.path.exists(video_path):
            video_path = "videoplayback.mp4"
        
        if os.path.exists(video_path):
            # Try to open with different backends for better compatibility
            video_cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
            
            # Test if video can be read
            if not video_cap.isOpened():
                logger.warning("Failed to open with FFMPEG, trying default backend")
                video_cap = cv2.VideoCapture(video_path)
            
            if not video_cap.isOpened():
                logger.error("Failed to open video with any backend")
                return False
            
            # Test reading first frame
            ret, frame = video_cap.read()
            if not ret or frame is None:
                logger.error("Failed to read first frame from video")
                video_cap.release()
                return False
            
            # Reset to beginning
            video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            logger.info(f"Video loaded successfully: {video_path}")
            logger.info(f"Video properties: {video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
            return True
        else:
            logger.warning("videoplayback.mp4 not found! Trying test video...")
            # Try test video as fallback
            test_video_path = "test_video.mp4"
            if os.path.exists(test_video_path):
                video_cap = cv2.VideoCapture(test_video_path)
                if video_cap.isOpened():
                    logger.info(f"Using test video: {test_video_path}")
                    return True
                else:
                    video_cap.release()
            
            logger.error("No video files found!")
            return False
    except Exception as e:
        logger.error(f"Error loading video: {e}")
        if video_cap:
            video_cap.release()
        return False

def process_frame(frame):
    """Process frame with YOLO model"""
    if model is None:
        return []
    
    try:
        # Run inference
        results = model(frame, 
                       imgsz=640,
                       conf=0.3,
                       iou=0.4,
                       max_det=50,
                       half=True,
                       verbose=False)
        
        detections = []
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().numpy()
                    cls = int(box.cls[0].cpu().numpy())
                    cls_name = model.names[cls]
                    
                    detections.append({
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "conf": float(conf),
                        "cls": cls_name,
                        "cls_id": int(cls)
                    })
        
        return detections
    except Exception as e:
        logger.error(f"Error processing frame: {e}")
        return []

# Global state tracking
guard_positions_history = []

def check_body_checking_progress(detections, gate_config):
    """Check if body checking is in progress - requires movement from guard anchor to gate"""
    global guard_positions_history
    
    if not gate_config.get("enabled", True):
        return None
    
    gate_area = gate_config.get("gate_area", {})
    guard_anchor = gate_config.get("guard_anchor", {})
    
    # Track people in different areas
    people_in_gate = []
    guards_in_anchor = []
    people_detected = 0
    
    frame_width = 640
    frame_height = 360
    
    # Current frame positions
    current_guard_positions = []
    
    for detection in detections:
        if detection.get("cls_id") == 0 and detection.get("conf", 0) > 0.5:
            people_detected += 1
            
            bbox = detection.get("bbox", [0, 0, 0, 0])
            center_x_px = (bbox[0] + bbox[2]) / 2
            center_y_px = (bbox[1] + bbox[3]) / 2
            
            center_x = center_x_px / frame_width
            center_y = center_y_px / frame_height
            
            # Check if person is in gate area
            gate_x = gate_area.get("x", 0.3)
            gate_y = gate_area.get("y", 0.2)
            gate_w = gate_area.get("width", 0.4)
            gate_h = gate_area.get("height", 0.6)
            
            in_gate = (gate_x <= center_x <= gate_x + gate_w and
                      gate_y <= center_y <= gate_y + gate_h)
            
            if in_gate:
                people_in_gate.append((center_x, center_y))
            
            # Check if guard is in guard anchor area
            guard_x = guard_anchor.get("x", 0.1)
            guard_y = guard_anchor.get("y", 0.15)
            guard_w = guard_anchor.get("width", 0.15)
            guard_h = guard_anchor.get("height", 0.7)
            
            in_anchor = (guard_x <= center_x <= guard_x + guard_w and
                        guard_y <= center_y <= guard_y + guard_h)
            
            if in_anchor:
                guards_in_anchor.append((center_x, center_y))
                current_guard_positions.append((center_x, center_y))
    
    # Update history (keep last 5 frames)
    guard_positions_history.append(current_guard_positions)
    if len(guard_positions_history) > 5:
        guard_positions_history.pop(0)
    
    person_in_gate = len(people_in_gate) > 0
    guard_present = len(guards_in_anchor) > 0
    
    # SIMPLIFIED LOGIC: Body checking is in progress ONLY if:
    # 1. At least 2 people total
    # 2. At least 1 person in gate area  
    # 3. Someone is currently in the guard anchor (guard is present)
    # This means both person in gate AND guard in anchor at the same time
    
    if person_in_gate and people_detected >= 2 and guard_present:
        logger.info(f"Body checking ACTIVE: {people_detected} people, {len(people_in_gate)} in gate, {len(guards_in_anchor)} in anchor")
        return {
            "active": True,
            "message": "🚨 BODY CHECKING IN PROGRESS",
            "person_in_gate": True,
            "guard_present": True,
            "people_count": people_detected,
            "timestamp": time.time()
        }
    
    if people_detected > 0:
        logger.info(f"Body checking NOT active: {people_detected} people, {len(people_in_gate)} in gate, {len(guards_in_anchor)} in anchor")
    
    return {
        "active": False,
        "message": f"Monitoring: {people_detected} people detected",
        "person_in_gate": person_in_gate,
        "guard_present": guard_present,
        "people_count": people_detected,
        "timestamp": time.time()
    }

def get_gate_config_copy():
    """Get a thread-safe copy of gate config"""
    with gate_config_lock:
        return gate_config.copy()

def draw_gate_overlay(frame, detections):
    """Draw gate areas and detections on frame"""
    h, w = frame.shape[:2]
    
    # Get a thread-safe copy of the gate config
    config = get_gate_config_copy()
    
    # Draw gate area (green)
    if config.get("enabled", True):
        gate = config.get("gate_area", {})
        x1 = int(gate.get("x", 0.3) * w)
        y1 = int(gate.get("y", 0.2) * h)
        x2 = int((gate.get("x", 0.3) + gate.get("width", 0.4)) * w)
        y2 = int((gate.get("y", 0.2) + gate.get("height", 0.6)) * h)
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 136), 3)
        cv2.putText(frame, "GATE AREA", (x1, y1-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 136), 2)
        
        # Draw guard anchor (red)
        guard = config.get("guard_anchor", {})
        gx1 = int(guard.get("x", 0.1) * w)
        gy1 = int(guard.get("y", 0.15) * h)
        gx2 = int((guard.get("x", 0.1) + guard.get("width", 0.15)) * w)
        gy2 = int((guard.get("y", 0.15) + guard.get("height", 0.7)) * h)
        
        cv2.rectangle(frame, (gx1, gy1), (gx2, gy2), (255, 107, 107), 3)
        cv2.putText(frame, "GUARD ANCHOR", (gx1, gy1-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 107, 107), 2)
    
    # Draw detections
    colors = {
        'person': (0, 255, 136),
        'car': (255, 107, 107),
        'truck': (76, 205, 196),
        'bus': (69, 183, 209),
        'bicycle': (150, 206, 180),
        'motorcycle': (254, 202, 87)
    }
    
    for detection in detections:
        x1, y1, x2, y2 = detection["bbox"]
        conf = detection["conf"]
        cls = detection["cls"]
        
        # Get color for class
        color = colors.get(cls, (255, 255, 255))
        
        # Draw bounding box
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 3)
        
        # Draw label
        label = f"{cls} {conf:.2f}"
        cv2.putText(frame, label, (int(x1), int(y1)-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    return frame

@app.on_event("startup")
async def startup_event():
    """Initialize the system"""
    logger.info("Starting Simple Video Inference System...")
    
    # Load model
    if not load_model():
        logger.error("Failed to load model!")
        return
    
    # Initialize video
    if not initialize_video():
        logger.error("Failed to load video!")
        return
    
    logger.info("System initialized successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global video_cap
    if video_cap:
        video_cap.release()
    logger.info("System shutdown complete")

@app.get("/")
async def root():
    return {"message": "Simple Video Inference System", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None, "video_loaded": video_cap is not None}

@app.get("/stream")
async def stream_video(request: Request, source: str = "file:videoplayback.mp4"):
    """Stream video with inference and proper headers"""
    global video_cap, current_frame
    
    if video_cap is None:
        return {"error": "Video not loaded"}
    
    def generate_frames():
        """Generate video frames for streaming"""
        frame_count = 0
        
        # Create a local video capture for this stream to avoid conflicts
        local_cap = cv2.VideoCapture("../videoplayback.mp4")
        if not local_cap.isOpened():
            logger.error("Failed to open video for streaming")
            local_cap = video_cap  # Fallback to global video_cap
            
        while True:
            try:
                # Lock mechanism to prevent concurrent access
                ret, frame = local_cap.read()
                if not ret or frame is None:
                    # Reset video to beginning
                    local_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                # Process frame
                detections = process_frame(frame)
                
                # Draw gate overlay and detections
                frame = draw_gate_overlay(frame, detections)
                
                # Encode frame
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if not ret:
                    continue
                
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                frame_count += 1
                
                # Control frame rate
                time.sleep(1/30)  # 30 FPS
                
            except Exception as e:
                logger.error(f"Error reading frame: {e}")
                # Try to reset video
                try:
                    local_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                except:
                    pass
                time.sleep(0.1)  # Brief pause before retrying
                continue
    
    # Add proper headers for MJPEG streaming
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "multipart/x-mixed-replace; boundary=frame"
    }
    
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame", headers=headers)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time data with proper error handling"""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        frame_count = 0
        last_pong = time.time()
        
        # Send initial hello message
        await websocket.send_json({
            "type": "hello",
            "ts": time.time(),
            "message": "WebSocket connected successfully"
        })
        
        while True:
            try:
                # Check if WebSocket is still connected
                if websocket.client_state.name != "CONNECTED":
                    logger.info("WebSocket disconnected, breaking loop")
                    break
                
                if video_cap is None:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Video not loaded"
                    })
                    break
                
                ret, frame = video_cap.read()
                if not ret or frame is None:
                    video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                # Process frame
                detections = process_frame(frame)
                
                # Check for body checking in progress
                body_checking_alert = check_body_checking_progress(detections, gate_config)
                
                # Debug logging
                if body_checking_alert:
                    logger.info(f"Body checking status: active={body_checking_alert.get('active', False)}, people={body_checking_alert.get('people_count', 0)}")
                
                # Send data
                await websocket.send_json({
                    "type": "detection",
                    "detections": detections,
                    "gate_config": gate_config,
                    "body_checking_alert": body_checking_alert,
                    "timestamp": time.time(),
                    "frame_count": frame_count
                })
                
                frame_count += 1
                await asyncio.sleep(1/20)  # 20 FPS
                
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                # Check if it's a close error
                if "close" in str(e).lower() or "disconnect" in str(e).lower():
                    logger.info("WebSocket closed by client")
                    break
                # Send error message to client only if still connected
                try:
                    if websocket.client_state.name == "CONNECTED":
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Processing error: {str(e)}"
                        })
                except:
                    pass
                # Continue the loop instead of breaking
                await asyncio.sleep(1)
                continue
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

@app.get("/config/gate")
async def get_gate_config():
    """Get gate configuration"""
    return gate_config

@app.post("/config/gate")
async def update_gate_config(config: dict):
    """Update gate configuration"""
    global gate_config
    with gate_config_lock:
        gate_config.update(config)
        updated_config = gate_config.copy()
    logger.info(f"Gate config updated: {updated_config}")
    return {"status": "updated", "config": updated_config}

@app.post("/config/gate/save")
async def save_gate_config():
    """Save gate configuration to file"""
    import json
    global gate_config
    try:
        with gate_config_lock:
            config_to_save = gate_config.copy()
        
        # Save to JSON file
        config_file = "gate_config_saved.json"
        with open(config_file, 'w') as f:
            json.dump(config_to_save, f, indent=2)
        
        logger.info(f"Gate config saved to {config_file}")
        return {
            "status": "saved",
            "message": "Configuration saved successfully",
            "file": config_file,
            "config": config_to_save
        }
    except Exception as e:
        logger.error(f"Error saving gate config: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/config/gate/load")
async def load_gate_config():
    """Load gate configuration from file"""
    import json
    global gate_config
    try:
        config_file = "gate_config_saved.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
            
            with gate_config_lock:
                gate_config.update(loaded_config)
            
            logger.info(f"Gate config loaded from {config_file}")
            return {
                "status": "loaded",
                "message": "Configuration loaded successfully",
                "config": gate_config.copy()
            }
        else:
            return {
                "status": "not_found",
                "message": "No saved configuration found"
            }
    except Exception as e:
        logger.error(f"Error loading gate config: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    logger.info("Starting Simple Video Inference System...")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
