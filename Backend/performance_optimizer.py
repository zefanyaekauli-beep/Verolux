#!/usr/bin/env python3
"""
Performance Optimization Utilities for Verolux1st
- AsyncFrameGrabber: Multithreaded frame capture
- BatchInferenceEngine: Batched GPU inference
- DualStreamCapture: Substream for detection
"""

import cv2
import time
import numpy as np
from threading import Thread, Lock
from queue import Queue, Empty
from typing import Optional, Tuple, List, Dict, Any


class AsyncFrameGrabber:
    """
    Asynchronously grab frames in separate thread
    Prevents inference from blocking frame capture
    Target: Reduce latency and ensure no dropped frames
    """
    
    def __init__(self, source: str, buffer_size: int = 1):
        self.source = source
        self.cap = None
        self.grabbed = False
        self.frame = None
        self.running = False
        self.lock = Lock()
        self.fps_actual = 0
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.buffer_size = buffer_size
        
    def _open_capture(self, source: str) -> cv2.VideoCapture:
        """Open video source with optimizations"""
        if source.startswith("webcam:"):
            idx = int(source.split(":", 1)[1])
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        elif source.startswith("file:") or source.startswith("upload:"):
            path = source.split(":", 1)[1]
            cap = cv2.VideoCapture(path)
        else:
            # RTSP or other sources
            cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
        
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open source: {source}")
        
        # Optimize for low latency
        cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
        
        return cap
    
    def start(self):
        """Start frame grabbing thread"""
        self.cap = self._open_capture(self.source)
        self.running = True
        self.thread = Thread(target=self._grab_frames, daemon=True)
        self.thread.start()
        
        # Wait for first frame
        max_wait = 3.0
        start = time.time()
        while self.frame is None and (time.time() - start) < max_wait:
            time.sleep(0.01)
        
        if self.frame is None:
            raise RuntimeError("Failed to capture first frame")
        
        return self
    
    def _grab_frames(self):
        """Worker thread that continuously grabs frames"""
        while self.running:
            grabbed, frame = self.cap.read()
            
            with self.lock:
                self.grabbed = grabbed
                if grabbed and frame is not None:
                    self.frame = frame
                    self.frame_count += 1
                
                # Calculate actual capture FPS
                now = time.time()
                if now - self.last_fps_time >= 1.0:
                    self.fps_actual = self.frame_count
                    self.frame_count = 0
                    self.last_fps_time = now
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Get latest frame (non-blocking)"""
        with self.lock:
            if self.frame is None:
                return False, None
            return self.grabbed, self.frame.copy()
    
    def get_fps(self) -> int:
        """Get actual capture FPS"""
        with self.lock:
            return self.fps_actual
    
    def stop(self):
        """Stop frame grabbing"""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()


class BatchInferenceEngine:
    """
    Process multiple frames in parallel batches
    Target: +20-40% FPS on GPU with batched inference
    """
    
    def __init__(self, model, batch_size: int = 4, timeout: float = 0.015):
        self.model = model
        self.batch_size = batch_size
        self.timeout = timeout
        self.frame_queue = Queue(maxsize=batch_size * 3)
        self.result_dict = {}
        self.running = False
        self.lock = Lock()
        self.worker_thread = None
        
    def start(self):
        """Start batch processing thread"""
        self.running = True
        self.worker_thread = Thread(target=self._process_batches, daemon=True)
        self.worker_thread.start()
        print(f"✅ Batch inference engine started (batch_size={self.batch_size})")
        
    def _process_batches(self):
        """Worker thread that processes frame batches"""
        while self.running:
            batch_frames = []
            batch_ids = []
            batch_originals = []
            
            # Collect batch with timeout
            timeout_start = time.time()
            while len(batch_frames) < self.batch_size:
                try:
                    remaining_time = self.timeout - (time.time() - timeout_start)
                    if remaining_time <= 0:
                        break
                    
                    frame_id, frame_data = self.frame_queue.get(timeout=max(0.001, remaining_time))
                    batch_ids.append(frame_id)
                    batch_frames.append(frame_data['rgb'])
                    batch_originals.append(frame_data['original_size'])
                except Empty:
                    break
            
            if not batch_frames:
                time.sleep(0.001)
                continue
            
            # Batch inference
            try:
                # Single batched inference call (much faster than individual)
                results = self.model.predict(
                    batch_frames,
                    imgsz=416,
                    conf=0.35,
                    iou=0.5,
                    device=self.model.device if hasattr(self.model, 'device') else 'cuda',
                    verbose=False,
                    half=True,
                    batch=len(batch_frames),
                    stream=False,
                    max_det=30
                )
                
                # Store results with lock
                with self.lock:
                    for frame_id, result, orig_size in zip(batch_ids, results, batch_originals):
                        self.result_dict[frame_id] = {
                            'result': result,
                            'original_size': orig_size
                        }
                        
            except Exception as e:
                print(f"Batch inference error: {e}")
                # Mark failed frames
                with self.lock:
                    for frame_id in batch_ids:
                        self.result_dict[frame_id] = None
    
    def infer_async(self, frame_id: int, frame: np.ndarray) -> bool:
        """Submit frame for batched inference"""
        try:
            # Convert to RGB
            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            frame_data = {
                'rgb': rgb,
                'original_size': (h, w)
            }
            
            self.frame_queue.put_nowait((frame_id, frame_data))
            return True
        except:
            return False  # Queue full
    
    def get_result(self, frame_id: int, timeout: float = 0.05) -> Optional[Dict]:
        """Get result for a specific frame"""
        start = time.time()
        while True:
            with self.lock:
                if frame_id in self.result_dict:
                    result = self.result_dict.pop(frame_id)
                    return result
            
            if time.time() - start > timeout:
                return None
            
            time.sleep(0.001)
    
    def stop(self):
        """Stop batch processing"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=1.0)
        print("🛑 Batch inference engine stopped")


class DualStreamCapture:
    """
    Dual-stream processing: main stream for display, substream for detection
    Target: 40% GPU load reduction
    """
    
    def __init__(self, source: str, detection_scale: float = 0.6):
        self.source = source
        self.detection_scale = detection_scale
        self.grabber = AsyncFrameGrabber(source)
        self.grabber.start()
        
    def read(self) -> Tuple[bool, Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Read both streams
        Returns: (ok, main_frame, detection_frame)
        """
        ok, frame_main = self.grabber.read()
        if not ok or frame_main is None:
            return False, None, None
        
        # Create downscaled version for detection
        h, w = frame_main.shape[:2]
        new_w = int(w * self.detection_scale)
        new_h = int(h * self.detection_scale)
        
        # Fast resize for detection
        frame_detection = cv2.resize(
            frame_main, 
            (new_w, new_h), 
            interpolation=cv2.INTER_LINEAR
        )
        
        return True, frame_main, frame_detection
    
    def get_fps(self) -> int:
        """Get capture FPS"""
        return self.grabber.get_fps()
    
    def release(self):
        """Release resources"""
        self.grabber.stop()


def scale_detections(detections: List[Dict[str, Any]], 
                     from_size: Tuple[int, int], 
                     to_size: Tuple[int, int]) -> List[Dict[str, Any]]:
    """
    Scale detection coordinates from one frame size to another
    Used when detecting on substream but need main stream coordinates
    """
    h_from, w_from = from_size
    h_to, w_to = to_size
    
    scale_x = w_to / w_from
    scale_y = h_to / h_from
    
    scaled = []
    for det in detections:
        scaled_det = det.copy()
        x1, y1, x2, y2 = det['xyxy']
        scaled_det['xyxy'] = [
            int(x1 * scale_x),
            int(y1 * scale_y),
            int(x2 * scale_x),
            int(y2 * scale_y)
        ]
        scaled.append(scaled_det)
    
    return scaled


























