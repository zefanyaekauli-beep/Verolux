# Verolux Startup Guide

## 🚀 Quick Start

### Main Startup Scripts (Use These Only)

#### 1. **START_VEROLUX.bat** (Recommended)
- **Complete system startup** with all checks
- **AI model detection** and setup
- **Video file verification** and copying
- **Backend and frontend** startup
- **System health checks**
- **Automatic dashboard opening**

#### 2. **START_VEROLUX_SIMPLE.bat** (Quick Start)
- **Simple startup** without extensive checks
- **Fast startup** for development
- **Basic backend and frontend** startup
- **Automatic dashboard opening**

#### 3. **STOP_VEROLUX.bat** (Shutdown)
- **Clean shutdown** of all processes
- **Port verification** and cleanup
- **Safe system shutdown**

## 📋 System Requirements

### Before First Run:
1. **Backend Setup:**
   ```bash
   cd Backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Frontend Setup:**
   ```bash
   cd Frontend
   npm install
   ```

3. **AI Model:**
   - Place your `weight.pt` file in the root directory
   - Or in `Backend\models\weight.pt`

4. **Video File:**
   - Place `videoplayback.mp4` in the root directory
   - Or in `Frontend\public\videoplayback.mp4`

## 🎯 Usage

### Normal Startup:
```bash
START_VEROLUX.bat
```

### Quick Startup:
```bash
START_VEROLUX_SIMPLE.bat
```

### Shutdown:
```bash
STOP_VEROLUX.bat
```

## 🌐 Access Points

- **Dashboard:** http://localhost:5173
- **Video Demo:** http://localhost:5173 (Navigate to VideoplaybackDemo)
- **Backend API:** http://localhost:8000
- **Health Check:** http://localhost:8000/health

## 🔧 Features

- ✅ **Real-time AI object detection**
- ✅ **Video processing with detection overlay**
- ✅ **Gate SOP monitoring**
- ✅ **Alert system**
- ✅ **Session reporting**
- ✅ **WebSocket real-time communication**

## 🚨 Troubleshooting

### If Backend Won't Start:
1. Check if `Backend\venv\Scripts\activate.bat` exists
2. Run: `cd Backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt`

### If Frontend Won't Start:
1. Check if `Frontend\node_modules` exists
2. Run: `cd Frontend && npm install`

### If AI Model Not Loading:
1. Ensure `weight.pt` is in root directory or `Backend\models\`
2. Check backend logs for model loading errors

### If Video Not Playing:
1. Ensure `videoplayback.mp4` is in `Frontend\public\`
2. Check browser console for video loading errors

## 📁 File Structure

```
Verox/
├── START_VEROLUX.bat          # Main startup script
├── START_VEROLUX_SIMPLE.bat  # Simple startup script
├── STOP_VEROLUX.bat          # Shutdown script
├── weight.pt                 # AI model file
├── videoplayback.mp4         # Video demo file
├── Backend/
│   ├── backend_server_fixed.py
│   ├── models/
│   └── venv/
└── Frontend/
    ├── public/
    └── node_modules/
```

## 🎉 Success Indicators

- **Two windows opened:** Backend and Frontend
- **Dashboard accessible:** http://localhost:5173
- **Video demo working:** Detection overlay appears
- **AI model loaded:** Backend health shows model_loaded: true
- **Real-time detections:** Detection boxes appear on video

---

**That's it! Just use these 3 scripts for a clean, reliable Verolux system.**


