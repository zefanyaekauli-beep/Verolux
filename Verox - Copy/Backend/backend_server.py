#!/usr/bin/env python3
"""
Verolux1st Backend
- FastAPI + OpenCV + (optional) Ultralytics YOLOv8/YOLOv5
- MJPEG stream, WS detections with normalized boxes, SOP summary, heartbeat
- Upload & YouTube ingest
- Enterprise touches: env-config, graceful errors, health, model auto-detect

ENV (optional):
  MODEL_PATH=./models/yolov8n.pt  (or weights.pt state_dict for custom)
  DEVICE=cuda|cpu
"""
import os, cv2, time, asyncio, uuid, math, subprocess
from typing import List, Dict, Any, Generator
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn

# Optional deps
try:
    import torch
except Exception:
    torch = None

# ---- Config ----
APP_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(APP_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join(APP_DIR, "models", "weight.pt"))
DEVICE = os.environ.get("DEVICE", "cuda" if (torch and torch.cuda.is_available()) else "cpu")

app = FastAPI(title="Verolux1st Backend")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

START = time.time()

# ---- YOLO Loader (Ultralytics) ----
ULTRA = None
YOLO_MODEL = None
CLASS_NAMES = ["person"]  # Focus on person detection only

def load_yolo():
    global ULTRA, YOLO_MODEL, CLASS_NAMES
    info = {"framework":"none","device":"cpu","loaded":False,"warmup":False,"model_path":MODEL_PATH}
    try:
        import ultralytics as UL
        from ultralytics import YOLO
        ULTRA = UL
        info["framework"] = "ultralytics"
        
        # Check if custom weight.pt exists
        if os.path.exists(MODEL_PATH):
            print(f"Loading custom model: {MODEL_PATH}")
            YOLO_MODEL = YOLO(MODEL_PATH)
            info["model_type"] = "custom_weight"
        else:
            print(f"Custom model not found at {MODEL_PATH}, using fallback")
            # Try builtin small model name as fallback
            YOLO_MODEL = YOLO("yolov8n.pt")
            info["model_type"] = "fallback"
        
        # Fuse model for faster inference
        YOLO_MODEL.fuse()
        
        # Get class names from model
        try:
            if hasattr(YOLO_MODEL, "names") and YOLO_MODEL.names:
                CLASS_NAMES = list(YOLO_MODEL.names.values())
                print(f"Model classes: {CLASS_NAMES}")
            else:
                print("Using fallback class names")
        except Exception as e:
            print(f"Could not get class names: {e}")
        
        # Set device
        try:
            YOLO_MODEL.to(DEVICE)
            info["device"] = DEVICE
            print(f"Model loaded on device: {DEVICE}")
        except Exception as e:
            info["device"] = "cpu"
            print(f"Failed to load on {DEVICE}, using CPU: {e}")
        
        # Warmup with dummy inference
        try:
            import torch
            if torch:
                dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
                _ = YOLO_MODEL.predict(dummy_img, verbose=False)
                info["warmup"] = True
                print("Model warmup completed")
        except Exception as e:
            print(f"Warmup failed: {e}")
        
        info["loaded"] = True
        print("✅ Model loaded successfully")
        
    except Exception as e:
        info["error"] = str(e)
        YOLO_MODEL = None
        print(f"❌ Model loading failed: {e}")
    return info

MODEL_INFO = load_yolo()

def infer_boxes(frame):
    """Return detections as list of {cls, conf, xyxy[pixels]}.
       Optimized for real-time person detection using custom weight.pt model.
    """
    h, w = frame.shape[:2]
    if YOLO_MODEL is not None:
        try:
            # Convert BGR to RGB for Ultralytics
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Optimized inference for real-time performance
            results = YOLO_MODEL.predict(
                rgb, 
                imgsz=640,           # Standard input size
                conf=0.3,            # Higher confidence threshold for person detection
                device=DEVICE, 
                verbose=False,
                half=True,           # Use half precision for faster inference
                agnostic_nms=True    # Class-agnostic NMS for better performance
            )
            
            out = []
            if results and len(results):
                r0 = results[0]
                if hasattr(r0, 'boxes') and r0.boxes is not None:
                    boxes = r0.boxes
                    for b in boxes:
                        # Get bounding box coordinates
                        xyxy = b.xyxy[0].tolist() if hasattr(b, "xyxy") else b[:4].tolist()
                        x1, y1, x2, y2 = map(int, xyxy)
                        
                        # Clamp coordinates to frame bounds
                        x1 = max(0, min(x1, w-1))
                        y1 = max(0, min(y1, h-1))
                        x2 = max(x1, min(x2, w-1))
                        y2 = max(y1, min(y2, h-1))
                        
                        # Get class and confidence
                        cls_id = int(b.cls[0].item()) if hasattr(b, "cls") else 0
                        conf = float(b.conf[0].item()) if hasattr(b, "conf") else 0.0
                        
                        # Get class name
                        if hasattr(r0, 'names') and r0.names:
                            if isinstance(r0.names, dict) and cls_id in r0.names:
                                name = r0.names[cls_id]
                            else:
                                name = CLASS_NAMES[cls_id % len(CLASS_NAMES)] if cls_id < len(CLASS_NAMES) else "person"
                        else:
                            name = "person"  # Default to person for custom models
                        
                        # Only include person detections with high confidence
                        if name.lower() == "person" and conf > 0.3:
                            out.append({
                                "cls": name, 
                                "conf": conf, 
                                "xyxy": [x1, y1, x2, y2]
                            })
            
            return out
            
        except Exception as e:
            print(f"Inference error: {e}")
            return []
    
    # Fallback: return empty list if no model
    return []

# ---- Video utils ----
def open_capture(source: str) -> cv2.VideoCapture:
    if source.startswith("webcam:"):
        idx = int(source.split(":",1)[1]); cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
    elif source.startswith("file:"):
        cap = cv2.VideoCapture(source.split(":",1)[1])
    elif source.startswith("upload:"):
        cap = cv2.VideoCapture(os.path.join(UPLOAD_DIR, source.split(":",1)[1]))
    else:
        cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
    if not cap.isOpened(): raise RuntimeError(f"Cannot open source: {source}")
    return cap

def encode_jpeg(frame) -> bytes:
    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    if not ok: raise RuntimeError("JPEG encode failed")
    return buf.tobytes()

def mjpeg_gen(source: str) -> Generator[bytes, None, None]:
    cap = open_capture(source)
    try:
        while True:
            ok, frame = cap.read()
            if not ok: break
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + encode_jpeg(frame) + b"\r\n"
            time.sleep(0.05)
    finally:
        cap.release()

def norm_xyxy(x1,y1,x2,y2,w,h):
    x1 = max(0.0, min(1.0, x1/max(1,w))); y1 = max(0.0, min(1.0, y1/max(1,h)))
    x2 = max(0.0, min(1.0, x2/max(1,w))); y2 = max(0.0, min(1.0, y2/max(1,h)))
    if x2 < x1: x1,x2 = x2,x1
    if y2 < y1: y1,y2 = y2,y1
    return [x1,y1,x2,y2]

# ---- SOP basic (duration/guard/pause) ----
SOP_CFG = {"check_zone_rect": (200,150,400,300), "guard_anchor_rect": (50,50,140,200), "min_duration_s": 6.0, "min_guard_s": 3.0, "min_pause_s": 2.0}
class SOPState:
    def __init__(self):
        self.zone_since=None; self.guard_since=None; self.last_center=None; self.pause_since=None
SOP_STATE = SOPState()

def rect_iou(a,b):
    ax1,ay1,ax2,ay2=a; bx1,by1,bx2,by2=b
    ix1,iy1=max(ax1,bx1),max(ay1,by1); ix2,iy2=min(ax2,bx2),min(ay2,by2)
    iw,ih=max(0,ix2-ix1),max(0,iy2-iy1); inter=iw*ih
    aarea=max(0,ax2-ax1)*max(0,ay2-ay1); barea=max(0,bx2-bx1)*max(0,by2-by1)
    return inter/(aarea+barea-inter+1e-9)
def center(x1,y1,x2,y2): return ((x1+x2)/2.0,(y1+y2)/2.0)

def update_sop(dets_px: List[Dict[str,Any]], now: float) -> Dict[str,Any]:
    z=SOP_CFG["check_zone_rect"]; g=SOP_CFG["guard_anchor_rect"]
    in_zone = any(d["cls"]=="person" and rect_iou(d["xyxy"], z)>0.2 for d in dets_px)
    guard   = any(d["cls"]=="person" and rect_iou(d["xyxy"], g)>0.2 for d in dets_px)
    # zone center
    zps = [d for d in dets_px if d["cls"]=="person" and rect_iou(d["xyxy"], z)>0.2]
    c=None
    if zps:
        d=max(zps,key=lambda d:(d["xyxy"][2]-d["xyxy"][0])*(d["xyxy"][3]-d["xyxy"][1]))
        c=center(*d["xyxy"])
    # durations
    if in_zone:
        if SOP_STATE.zone_since is None: SOP_STATE.zone_since = now
    else:
        SOP_STATE.zone_since = None
    if guard:
        if SOP_STATE.guard_since is None: SOP_STATE.guard_since = now
    else:
        SOP_STATE.guard_since = None
    # pause
    paused=False
    if c is not None:
        if SOP_STATE.last_center is None: SOP_STATE.last_center = c
        dist=((c[0]-SOP_STATE.last_center[0])**2 + (c[1]-SOP_STATE.last_center[1])**2)**0.5
        if dist < 5:
            if SOP_STATE.pause_since is None: SOP_STATE.pause_since = now
            elif (now - SOP_STATE.pause_since) >= SOP_CFG["min_pause_s"]:
                paused=True
        else:
            SOP_STATE.pause_since=None
        SOP_STATE.last_center=c
    dur_ok = (SOP_STATE.zone_since is not None) and ((now - SOP_STATE.zone_since) >= SOP_CFG["min_duration_s"])
    guard_ok = (SOP_STATE.guard_since is not None) and ((now - SOP_STATE.guard_since) >= SOP_CFG["min_guard_s"])
    pause_ok = paused
    ok = dur_ok and guard_ok and pause_ok
    return {"ok": ok, "duration_s": round((now - (SOP_STATE.zone_since or now)),2), "guard_s": round((now - (SOP_STATE.guard_since or now)),2), "paused": pause_ok, "failed":[k for k,v in {"duration":dur_ok,"guard":guard_ok,"pause":pause_ok}.items() if not v]}

# ---- Routes ----
@app.get("/health")
def health():
    return JSONResponse({"status":"ok","model":MODEL_INFO,"uptime_s":round(time.time()-START,1)})

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    vid = f"{uuid.uuid4().hex}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, vid)
    with open(path, "wb") as f: f.write(await file.read())
    return {"video_id": vid, "source": f"upload:{vid}"}

def yt_download(url: str) -> str:
    try:
        import yt_dlp
        vid = f"{uuid.uuid4().hex}.mp4"; out = os.path.join(UPLOAD_DIR, vid)
        ydl_opts = {"format": "best[ext=mp4]/best", "outtmpl": out}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
        return vid
    except Exception:
        # fallback to system binary
        vid = f"{uuid.uuid4().hex}.mp4"; out = os.path.join(UPLOAD_DIR, vid)
        subprocess.check_call(["yt-dlp","-f","best[ext=mp4]/best","-o",out,url])
        return vid

@app.post("/ingest-youtube")
async def ingest_youtube(url: str = Form(...)):
    vid = yt_download(url)
    return {"video_id": vid, "source": f"upload:{vid}"}

@app.get("/stream")
def stream(source: str = Query("webcam:0")):
    return StreamingResponse(mjpeg_gen(source), media_type="multipart/x-mixed-replace; boundary=frame")

@app.websocket("/ws/detections")
async def ws_detections(ws: WebSocket, source: str = Query("webcam:0")):
    await ws.accept()
    await ws.send_json({"type":"connection_info","framework":MODEL_INFO.get("framework"),"model_loaded":bool(MODEL_INFO.get("loaded")), "device": MODEL_INFO.get("device","cpu"), "source": source})
    # capture
    try:
        cap = open_capture(source)
    except Exception as e:
        await ws.send_json({"type":"error","message":str(e)}); await ws.close(); return
    last_beat = time.time(); t_prev = time.time()
    try:
        while True:
            ok, frame = cap.read()
            if not ok: break
            t_now = time.time(); dt = max(1e-6, t_now - t_prev); t_prev = t_now; fps = 1.0/dt
            h,w = frame.shape[:2]
            dets_px = infer_boxes(frame)
            sop = update_sop(dets_px, t_now)
            dets = [{"cls": d["cls"], "conf": d["conf"], "bbox": norm_xyxy(*d["xyxy"], w, h)} for d in dets_px]
            await ws.send_json({"type":"detections","ts":t_now,"fps":round(fps,1),"frame_size":[w,h],"detections":dets,"sop":sop})
            if (t_now - last_beat) >= 30.0:
                await ws.send_json({"type":"heartbeat","uptime_s": round(time.time()-START,1)}); last_beat = t_now
            await asyncio.sleep(max(0.0, 0.2 - (time.time()-t_now)))  # target ~5 FPS
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try: await ws.send_json({"type":"error","message":str(e)})
        except Exception: pass
    finally:
        cap.release()

if __name__ == "__main__":
    uvicorn.run("backend_server:app", host="0.0.0.0", port=8000, reload=False)
