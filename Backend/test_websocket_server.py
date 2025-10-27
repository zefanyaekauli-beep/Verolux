#!/usr/bin/env python3
"""
Simple WebSocket Test Server
This is a minimal server to test WebSocket connections without video dependencies
"""

import cv2
import numpy as np
import json
import time
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Simple WebSocket Test Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
gate_config = {
    "gate_area": {"x": 0.3, "y": 0.2, "width": 0.4, "height": 0.6},
    "guard_anchor": {"x": 0.1, "y": 0.15, "width": 0.15, "height": 0.7},
    "enabled": True
}

@app.get("/")
async def root():
    return {"message": "Simple WebSocket Test Server", "status": "running"}

@app.get("/stream")
async def stream_video():
    """Stream test video with moving objects"""
    
    def generate_frames():
        frame_count = 0
        
        while True:
            try:
                # Create frame
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                
                # Add background gradient
                for y in range(480):
                    color_value = int(50 + (y / 480) * 100)
                    frame[y, :] = [color_value, color_value, color_value]
                
                # Add moving rectangle (simulating a person)
                rect_x = int((frame_count % 300) / 300 * (640 - 100))
                rect_y = int(480 // 2 - 50)
                cv2.rectangle(frame, (rect_x, rect_y), (rect_x + 100, rect_y + 150), (0, 255, 0), -1)
                
                # Add moving circle (simulating another object)
                circle_x = int(640 - ((frame_count % 300) / 300 * (640 - 50)))
                circle_y = int(480 // 3)
                cv2.circle(frame, (circle_x, circle_y), 30, (255, 0, 0), -1)
                
                # Add text
                cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, "Test Video for Inference", (10, 450), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Add gate area overlay
                gate_x = int(640 * 0.3)
                gate_y = int(480 * 0.2)
                gate_w = int(640 * 0.4)
                gate_h = int(480 * 0.6)
                cv2.rectangle(frame, (gate_x, gate_y), (gate_x + gate_w, gate_y + gate_h), (0, 255, 136), 2)
                cv2.putText(frame, "GATE AREA", (gate_x, gate_y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 136), 2)
                
                # Add guard anchor overlay
                guard_x = int(640 * 0.1)
                guard_y = int(480 * 0.15)
                guard_w = int(640 * 0.15)
                guard_h = int(480 * 0.7)
                cv2.rectangle(frame, (guard_x, guard_y), (guard_x + guard_w, guard_y + guard_h), (255, 107, 107), 2)
                cv2.putText(frame, "GUARD", (guard_x, guard_y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 107, 107), 2)
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                # Yield frame in MJPEG format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                frame_count += 1
                time.sleep(1/20)  # 20 FPS
                
            except Exception as e:
                logger.error(f"Error generating frame: {e}")
                break
    
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/health")
async def health():
    return {"status": "healthy", "websocket": "ready"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time data"""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        frame_count = 0
        while True:
            try:
                # Check if WebSocket is still connected
                if websocket.client_state.name != "CONNECTED":
                    logger.info("WebSocket disconnected, breaking loop")
                    break
                
                # Simulate detections
                detections = [
                    {
                        "bbox": [100, 100, 200, 200],
                        "conf": 0.85,
                        "cls": "person",
                        "cls_id": 0
                    }
                ]
                
                # Simulate body checking alert
                body_checking_alert = {
                    "active": True,
                    "message": "🚨 BODY CHECKING IN PROGRESS",
                    "person_in_gate": True,
                    "guard_present": False,
                    "timestamp": time.time()
                } if frame_count % 100 == 0 else None
                
                # Send data only if WebSocket is still connected
                if websocket.client_state.name == "CONNECTED":
                    await websocket.send_text(json.dumps({
                        "type": "detection",
                        "detections": detections,
                        "gate_config": gate_config,
                        "body_checking_alert": body_checking_alert,
                        "timestamp": time.time(),
                        "frame_count": frame_count
                    }))
                
                frame_count += 1
                await asyncio.sleep(1/20)  # 20 FPS
                
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                # Check if it's a close error
                if "close" in str(e).lower():
                    logger.info("WebSocket closed by client")
                    break
                # Send error message to client only if still connected
                try:
                    if websocket.client_state.name == "CONNECTED":
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": f"Processing error: {str(e)}"
                        }))
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
    gate_config.update(config)
    return {"status": "updated", "config": gate_config}

if __name__ == "__main__":
    logger.info("Starting Simple WebSocket Test Server...")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
