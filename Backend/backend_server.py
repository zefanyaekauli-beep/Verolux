"""
Verolux Backend Server - Original Version
This is the original backend server file
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Verolux Backend", version="1.0.0")

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
connections = []

@app.on_event("startup")
async def startup_event():
    """Initialize the backend on startup"""
    global model
    logger.info("Starting Verolux Backend...")
    
    # Try to load model
    try:
        from ultralytics import YOLO
        model_path = "../weight.pt" if os.path.exists("../weight.pt") else "weight.pt"
        if os.path.exists(model_path):
            model = YOLO(model_path)
            logger.info("Model loaded successfully")
        else:
            logger.warning("Model file not found")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
    
    logger.info("Backend startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down backend")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Verolux Backend API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "connections": len(connections)
    }

@app.get("/model-status")
async def model_status():
    """Get model status"""
    return {
        "model_loaded": model is not None,
        "model_type": "YOLOv8" if model else None
    }

@app.websocket("/ws/detections")
async def websocket_detections(websocket: WebSocket):
    """WebSocket endpoint for detections"""
    await websocket.accept()
    connections.append(websocket)
    
    try:
        while True:
            # Send mock detection data
            data = {
                "type": "detection",
                "objects": [
                    {"class": "person", "confidence": 0.95, "bbox": [100, 100, 200, 300]},
                    {"class": "bag", "confidence": 0.87, "bbox": [300, 150, 400, 250]}
                ],
                "timestamp": "2025-01-24T12:00:00Z"
            }
            await websocket.send_json(data)
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in connections:
            connections.remove(websocket)

@app.websocket("/ws/gate-check")
async def websocket_gate_check(websocket: WebSocket):
    """WebSocket endpoint for gate checks"""
    await websocket.accept()
    
    try:
        while True:
            # Send mock gate check data
            data = {
                "type": "gate_check",
                "status": "active",
                "alerts": [],
                "timestamp": "2025-01-24T12:00:00Z"
            }
            await websocket.send_json(data)
            await asyncio.sleep(2)
    except Exception as e:
        logger.error(f"Gate check WebSocket error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


