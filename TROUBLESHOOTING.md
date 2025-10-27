# 🔧 **TROUBLESHOOTING GUIDE**

## 🚨 **Common Issues & Quick Fixes**

---

## ❌ **ISSUE 1: Model Not Loading**

### **Symptoms:**
- Backend shows "Model not loaded"
- Error: "Model file not found"
- Backend won't start

### **Quick Fix:**

**Option A: Auto-download (Easiest)**
```bash
cd Backend
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

This downloads YOLOv8n automatically (~6MB).

**Option B: Use existing model**
```bash
# Check if you have models
dir Backend\models

# If weight.pt exists, backend will use it automatically
```

**Option C: Download manually**
```bash
cd Backend
python download_models_simple.py
```

### **Verification:**
```bash
# Check models exist
dir Backend\models\*.pt

# Should see: weight.pt or yolov8n.pt
```

---

## ❌ **ISSUE 2: CUDA Not Working (GPU)**

### **Symptoms:**
- Backend shows "device: cpu" instead of "device: cuda"
- Slow performance (~5 FPS instead of 30 FPS)
- Warning: "CUDA not available"

### **Check CUDA Status:**
```bash
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

### **If Returns False - Fixes:**

**Fix 1: Install NVIDIA Drivers**
1. Check if you have NVIDIA GPU:
   - Open Device Manager
   - Look under "Display adapters"
   - Should see "NVIDIA GeForce..." or "NVIDIA RTX..."

2. Download drivers: https://www.nvidia.com/Download/index.aspx

**Fix 2: Install CUDA Toolkit**
1. Download CUDA 11.8: https://developer.nvidia.com/cuda-11-8-0-download-archive
2. Install with default settings
3. Reboot PC

**Fix 3: Reinstall PyTorch with CUDA**
```bash
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### **Verification:**
```bash
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

**Expected:** `CUDA: True` and your GPU name

### **Note:**
**System works fine on CPU** - just slower (5-10 FPS instead of 30 FPS). GPU is optional!

---

## ❌ **ISSUE 3: Video Feed Not Connecting**

### **Symptoms:**
- Black screen in UI
- "Cannot read frame" error
- WebSocket connects but no video

### **Diagnose:**

**Test 1: Check webcam**
```bash
python -c "import cv2; cap = cv2.VideoCapture(0); ret, frame = cap.read(); print('Webcam:', 'OK' if ret else 'FAILED'); cap.release()"
```

**Test 2: Check OpenCV**
```bash
python -c "import cv2; print('OpenCV version:', cv2.__version__)"
```

### **Fixes by Source Type:**

#### **Webcam Not Working:**

**Fix 1: Check if webcam is in use**
- Close Zoom, Skype, Teams, OBS
- Close other video apps
- Restart system

**Fix 2: Try different webcam index**
```javascript
// In browser or WebSocket
source=webcam:1  // Try 1, 2, 3...
```

**Fix 3: Check permissions**
- Windows: Settings → Privacy → Camera → Allow apps
- Ensure Python is allowed to use camera

**Fix 4: Use test video instead**
- Download sample: https://www.youtube.com/watch?v=sample
- Use: `source=file:///C:/path/to/video.mp4`

#### **RTSP Camera Not Working:**

**Fix 1: Test RTSP URL**
```bash
# Test with FFmpeg (if installed)
ffplay rtsp://camera-ip/stream

# Or use VLC to test the RTSP URL
```

**Fix 2: Check common RTSP URLs**
```
Hikvision: rtsp://admin:password@camera-ip:554/Streaming/Channels/101
Dahua: rtsp://admin:password@camera-ip:554/cam/realmonitor?channel=1&subtype=0
Generic: rtsp://camera-ip:554/stream1
```

**Fix 3: Check network**
```bash
ping camera-ip
telnet camera-ip 554
```

**Fix 4: Try different transport**
```
# TCP (more reliable)
rtsp://camera-ip/stream?tcp

# UDP (lower latency)
rtsp://camera-ip/stream?udp
```

#### **File Not Working:**

**Fix 1: Use absolute path**
```
# Windows
file:///C:/Users/User/Desktop/video.mp4

# Linux/macOS
file:///home/user/videos/video.mp4
```

**Fix 2: Check file format**
Supported: .mp4, .avi, .mov, .mkv, .flv

---

## ❌ **ISSUE 4: Backend Won't Start**

### **Symptoms:**
- Backend crashes immediately
- Import errors
- Port already in use

### **Fixes:**

**Fix 1: Check port 8000 is free**
```bash
# Windows - check what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

**Fix 2: Reinstall dependencies**
```bash
cd Backend
pip install --upgrade -r requirements.txt
```

**Fix 3: Check Python version**
```bash
python --version
# Need Python 3.8 or higher
```

**Fix 4: Use CPU mode explicitly**
```bash
set DEVICE=cpu
python backend_server.py
```

---

## ❌ **ISSUE 5: Frontend Won't Start**

### **Symptoms:**
- "npm run dev" fails
- Port 5173 in use
- Module not found errors

### **Fixes:**

**Fix 1: Reinstall node modules**
```bash
cd Frontend
rmdir /s node_modules
del package-lock.json
npm install
```

**Fix 2: Check port 5173**
```bash
netstat -ano | findstr :5173
# Kill process if found
```

**Fix 3: Clear cache**
```bash
npm cache clean --force
npm install
```

---

## 🔧 **QUICK DIAGNOSTIC SCRIPT**

Run this to check everything:

```bash
FIX_COMMON_ISSUES.bat
```

This script:
1. ✅ Diagnoses all issues
2. ✅ Downloads missing models
3. ✅ Tests video capture
4. ✅ Verifies dependencies
5. ✅ Provides specific fixes

---

## 📊 **VERIFICATION STEPS**

### **After applying fixes, verify:**

**1. Check Python & packages:**
```bash
python -c "import torch, cv2, ultralytics, fastapi; print('All packages OK')"
```

**2. Check models:**
```bash
dir Backend\models\*.pt
```

**3. Check CUDA (optional):**
```bash
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

**4. Check webcam:**
```bash
python -c "import cv2; cap = cv2.VideoCapture(0); print('Webcam:', cap.isOpened()); cap.release()"
```

**5. Start backend:**
```bash
cd Backend
python backend_server.py
```

**Look for:** `INFO: Uvicorn running on http://0.0.0.0:8000`

---

## 💡 **MOST COMMON ISSUES & SOLUTIONS**

| Issue | Quick Fix |
|-------|-----------|
| **Model not found** | `python Backend/download_models_simple.py` |
| **CUDA not working** | Set `DEVICE=cpu` (system works on CPU) |
| **Webcam in use** | Close other video apps |
| **Port 8000 in use** | `taskkill /F /IM python.exe` |
| **Port 5173 in use** | `taskkill /F /IM node.exe` |
| **Missing packages** | `pip install -r Backend/requirements.txt` |
| **npm errors** | `cd Frontend && npm install` |

---

## 🆘 **STILL NOT WORKING?**

### **Run this complete diagnostic:**

```bash
# 1. Fix all common issues
FIX_COMMON_ISSUES.bat

# 2. Try starting again
START_VEROLUX.bat
```

### **Check logs:**

**Backend log (if it starts):**
- Look at the Backend terminal window
- Check for specific error messages

**Frontend log (if it starts):**
- Look at the Frontend terminal window
- Check for specific error messages

### **Minimal working configuration:**

If nothing works, try absolute minimal:

```bash
# Terminal 1: Backend (CPU mode, no GPU needed)
cd Backend
set DEVICE=cpu
set MODEL_PATH=./models/yolov8n.pt
python backend_server.py

# Terminal 2: Frontend
cd Frontend
npm run dev
```

---

## 📞 **COMMON ERROR MESSAGES & FIXES**

### **"Model file not found"**
```bash
python Backend/download_models_simple.py
```

### **"CUDA out of memory"**
```bash
set DEVICE=cpu
set BATCH_SIZE=1
```

### **"Cannot open video capture device"**
```bash
# Use file instead of webcam
source=file:///C:/path/to/video.mp4
```

### **"Address already in use"**
```bash
# Kill existing processes
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

---

## ✅ **RECOMMENDED: Start with CPU Mode**

If you're having issues, start simple:

```bash
cd Backend

# Set to CPU mode (works on any PC)
set DEVICE=cpu

# Start backend
python backend_server.py

# You should see:
# ✅ Model loaded on CPU
# INFO: Uvicorn running on http://0.0.0.0:8000
```

**System will work fine on CPU** - just slower (5-10 FPS instead of 30 FPS).

You can add GPU later once everything else works!

---

## 🎯 **STEP-BY-STEP FIX**

### **If your system isn't working, do this:**

**Step 1: Run diagnostic**
```bash
FIX_COMMON_ISSUES.bat
```

**Step 2: Check what failed**
Read the output carefully

**Step 3: Apply specific fix**
Based on what failed (see sections above)

**Step 4: Try starting again**
```bash
START_VEROLUX.bat
```

---

**Need more help?** The diagnostic script will tell you exactly what's wrong!

**Run:** `FIX_COMMON_ISSUES.bat` 🔧













