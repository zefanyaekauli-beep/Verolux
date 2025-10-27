# 🎯 Simple Video Inference System

A streamlined video inference system using weight.pt model with gate features for videoplayback.mp4.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- weight.pt model file
- videoplayback.mp4 video file

### Installation

1. **Install Python dependencies:**
```bash
pip install ultralytics opencv-python fastapi uvicorn websockets
```

2. **Install Frontend dependencies:**
```bash
cd Frontend
npm install
```

### Running the System

**Option 1: Use the startup script (Recommended)**
```bash
python start_simple_inference.py
```

**Option 2: Manual startup**

1. **Start Backend:**
```bash
cd Backend
python simple_video_inference.py
```

2. **Start Frontend:**
```bash
cd Frontend
npm run dev
```

## 🌐 Access Points

- **Frontend Interface:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Video Stream:** http://localhost:8000/stream
- **WebSocket:** ws://localhost:8000/ws

## 🎯 Features

### Video Inference
- ✅ Real-time object detection using weight.pt model
- ✅ Processes videoplayback.mp4 video file
- ✅ Optimized for 20 FPS performance
- ✅ Multiple object detection (up to 50 objects)
- ✅ Class names and confidence scores displayed

### Gate Configuration
- ✅ Visual gate area overlay (green box)
- ✅ Guard anchor area (red box)
- ✅ Real-time gate configuration
- ✅ Toggle gate visibility
- ✅ Adjustable gate positions

### User Interface
- ✅ Clean, modern interface
- ✅ Real-time detection stats
- ✅ FPS counter
- ✅ Connection status indicator
- ✅ Live detection list with colors

## 🔧 Configuration

### Model Settings
- **Input Size:** 640px (optimized for accuracy)
- **Confidence Threshold:** 0.3 (balanced detection)
- **NMS IoU:** 0.4 (clean multiple detections)
- **Max Detections:** 50 objects
- **FP16:** Enabled for performance

### Gate Settings
- **Gate Area:** 30% left, 20% top, 40% width, 60% height
- **Guard Anchor:** 10% left, 15% top, 15% width, 70% height
- **Colors:** Green for gate area, Red for guard anchor

## 📊 API Endpoints

### HTTP Endpoints
- `GET /` - System status
- `GET /health` - Health check
- `GET /stream` - Video stream with inference
- `GET /config/gate` - Get gate configuration
- `POST /config/gate` - Update gate configuration

### WebSocket
- `ws://localhost:8000/ws` - Real-time detection data

## 🎨 Frontend Features

### Main Interface
- **Video Display:** Large video stream with overlay
- **Detection Stats:** Object count, FPS, status
- **Current Detections:** Live list of detected objects
- **Gate Configuration:** Real-time gate adjustment

### Controls
- **Gate Toggle:** Show/hide gate areas
- **Position Sliders:** Adjust gate positions
- **Enable/Disable:** Toggle gate functionality

## 🔍 Detection Classes

The system detects and displays:
- **Person** (Green) - Human detection
- **Car** (Red) - Vehicle detection  
- **Truck** (Cyan) - Truck detection
- **Bus** (Blue) - Bus detection
- **Bicycle** (Light Green) - Bicycle detection
- **Motorcycle** (Yellow) - Motorcycle detection

## 🛠️ Troubleshooting

### Common Issues

1. **"weight.pt not found"**
   - Ensure weight.pt is in the project root directory
   - Check file permissions

2. **"videoplayback.mp4 not found"**
   - Ensure videoplayback.mp4 is in the project root directory
   - Check file format and permissions

3. **"WebSocket connection failed"**
   - Ensure backend is running on port 8000
   - Check firewall settings

4. **"No video stream"**
   - Check if videoplayback.mp4 exists and is readable
   - Verify OpenCV installation

### Performance Optimization

- **Lower FPS:** Reduce input size to 416px
- **Higher Accuracy:** Increase input size to 640px
- **More Detections:** Lower confidence threshold to 0.2
- **Fewer Detections:** Increase confidence threshold to 0.5

## 📁 File Structure

```
├── Backend/
│   └── simple_video_inference.py    # Main backend server
├── Frontend/
│   ├── src/pages/
│   │   └── SimpleInference.jsx      # Frontend interface
│   └── package.json
├── weight.pt                        # YOLO model file
├── videoplayback.mp4                # Video file
├── start_simple_inference.py        # Startup script
└── SIMPLE_INFERENCE_README.md       # This file
```

## 🎯 Usage

1. **Start the system** using the startup script
2. **Open the frontend** at http://localhost:5173
3. **Navigate to Simple Inference** in the sidebar
4. **View the video stream** with real-time detections
5. **Configure gate areas** using the sidebar controls
6. **Monitor detection stats** in real-time

## 🔧 Customization

### Adding New Detection Classes
Edit the `colors` dictionary in `simple_video_inference.py`:
```python
colors = {
    'person': (0, 255, 136),
    'car': (255, 107, 107),
    'your_class': (R, G, B)  # Add your class
}
```

### Adjusting Performance
Modify model parameters in `process_frame()`:
```python
results = model(frame, 
               imgsz=640,      # Input size
               conf=0.3,       # Confidence threshold
               iou=0.4,        # NMS IoU
               max_det=50,     # Max detections
               half=True)      # FP16 optimization
```

## 📈 Performance Metrics

- **FPS:** 20-30 FPS (depending on hardware)
- **Latency:** <100ms detection delay
- **Memory:** ~2GB RAM usage
- **GPU:** CUDA acceleration supported

## 🎉 Success!

Your Simple Video Inference System is now running with:
- ✅ Real-time object detection
- ✅ Gate configuration features
- ✅ Modern web interface
- ✅ Optimized performance
- ✅ Easy customization

Enjoy your AI-powered video analysis system! 🚀

