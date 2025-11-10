#!/usr/bin/env python3
"""
Create a simple test video for the inference system
This creates a basic video with moving objects for testing
"""

import cv2
import numpy as np
import os

def create_test_video():
    """Create a simple test video with moving objects"""
    
    # Video properties
    width, height = 640, 480
    fps = 30
    duration = 10  # seconds
    total_frames = fps * duration
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('test_video.mp4', fourcc, fps, (width, height))
    
    print(f"Creating test video: {width}x{height}, {fps} FPS, {duration}s")
    
    for frame_num in range(total_frames):
        # Create frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add background gradient
        for y in range(height):
            color_value = int(50 + (y / height) * 100)
            frame[y, :] = [color_value, color_value, color_value]
        
        # Add moving rectangle (simulating a person)
        rect_x = int((frame_num / total_frames) * (width - 100))
        rect_y = int(height // 2 - 50)
        cv2.rectangle(frame, (rect_x, rect_y), (rect_x + 100, rect_y + 150), (0, 255, 0), -1)
        
        # Add moving circle (simulating another object)
        circle_x = int(width - ((frame_num / total_frames) * (width - 50)))
        circle_y = int(height // 3)
        cv2.circle(frame, (circle_x, circle_y), 30, (255, 0, 0), -1)
        
        # Add text
        cv2.putText(frame, f"Frame: {frame_num}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, "Test Video for Inference", (10, height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Write frame
        out.write(frame)
        
        if frame_num % 30 == 0:
            print(f"Progress: {frame_num}/{total_frames} frames")
    
    # Release everything
    out.release()
    print("Test video created: test_video.mp4")
    
    # Verify video
    cap = cv2.VideoCapture('test_video.mp4')
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"Video verified: {frame.shape[1]}x{frame.shape[0]}")
        cap.release()
    else:
        print("Error: Could not verify video")

if __name__ == "__main__":
    create_test_video()








