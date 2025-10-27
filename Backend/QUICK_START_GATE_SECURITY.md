# Quick Start - Gate Security System

## ⚡ 5-Minute Setup

### Step 1: Verify Setup

```bash
cd Backend
python test_gate_setup.py
```

This will check:
- ✅ All dependencies installed
- ✅ All components working
- ✅ Configuration files present
- ✅ GateChecker initializes correctly

### Step 2: Start the Backend

**Windows:**
```bash
START_GATE_SECURITY.bat
```

**Linux/Mac:**
```bash
chmod +x START_GATE_SECURITY.sh
./START_GATE_SECURITY.sh
```

**Manual:**
```bash
python backend_server.py
```

### Step 3: Test the WebSocket

Open a browser console or use a WebSocket client:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/gate-check?source=webcam:0');

ws.onopen = () => console.log('Connected to Gate Security');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
  
  if (data.type === 'gate_check') {
    console.log('Decisions:', data.decisions);
    
    // Check for completions
    if (data.decisions.completions.length > 0) {
      console.log('✅ CHECK COMPLETED!', data.decisions.completions);
    }
  }
};
```

### Step 4: View API Endpoints

Visit: http://localhost:8000/docs

Try:
- `GET /gate/completions` - See completed checks
- `GET /gate/stats` - View statistics
- `GET /gate/config` - See current configuration

## 🎯 What to Expect

### Connection Message
```json
{
  "type": "connection_info",
  "gate_checker": true,
  "gate_id": "A1",
  "device": "cuda"
}
```

### Gate Check Stream (5 FPS)
```json
{
  "type": "gate_check",
  "fps": 5.2,
  "stats": {
    "active_tracks": 3,
    "decision_engine": {
      "total_persons": 2,
      "total_guards": 1
    }
  },
  "decisions": {
    "persons": {
      "123": {
        "state": "interaction_window",
        "score": 0.92,
        "dwell_in_ga": 6.5
      }
    },
    "guards": {
      "456": {
        "is_qualified": true
      }
    },
    "completions": []
  }
}
```

### Check Completion
```json
{
  "decisions": {
    "completions": [
      {
        "session_id": "123_1696723456789",
        "visitor_track_id": 123,
        "guard_track_id": 456,
        "score": 0.95,
        "visitor_dwell": 6.8,
        "interaction_duration": 2.1
      }
    ]
  }
}
```

## 🔧 Configuration

Edit `Backend/config/gate_rules.demo.json` to adjust:

### Quick Tuning

**More sensitive (fewer misses):**
```json
{
  "timers": {
    "person_min_dwell_s": 5.0,
    "interaction_min_overlap_s": 1.0
  },
  "scoring": {
    "threshold": 0.85
  }
}
```

**More strict (fewer false positives):**
```json
{
  "timers": {
    "person_min_dwell_s": 7.0,
    "interaction_min_overlap_s": 1.5
  },
  "scoring": {
    "threshold": 0.95
  }
}
```

## 📊 Monitoring

### Real-time Stats
Access via WebSocket or:
```bash
curl http://localhost:8000/gate/stats
```

### Recent Completions
```bash
curl http://localhost:8000/gate/completions?limit=10
```

### Session Details
```bash
curl http://localhost:8000/gate/session/{session_id}
```

## 🎨 Zones

Zones are defined as normalized polygons (0-1 coordinates):

### Gate Area (where check happens)
```json
{
  "polygon": [
    [0.30, 0.20],  // top-left
    [0.70, 0.20],  // top-right
    [0.70, 0.80],  // bottom-right
    [0.30, 0.80]   // bottom-left
  ]
}
```

### Guard Anchor (where guard stands)
```json
{
  "polygon": [
    [0.10, 0.15],
    [0.25, 0.15],
    [0.25, 0.85],
    [0.10, 0.85]
  ]
}
```

To customize:
1. Draw zones on a frame screenshot
2. Convert pixel coords to 0-1 (divide by width/height)
3. Update JSON files in `Backend/config/`

## 🐛 Troubleshooting

### Gate checker not available
```bash
# Check if all dependencies installed
python test_gate_setup.py

# Install missing packages
pip install -r requirements.txt
```

### No detections
- Check camera source: `?source=webcam:0` or `?source=file:path/to/video.mp4`
- Verify YOLO model loaded: Check console output
- Test regular detection first: `ws://localhost:8000/ws/detections`

### No check completions
- Verify zones cover the area (check visualization)
- Lower thresholds in config
- Check console logs for FSM state transitions

### Performance issues
- Reduce FPS in WebSocket loop
- Use smaller YOLO model (yolov8n.pt)
- Disable pose estimation: `"use_pose": false`

## 📚 Resources

- **Full Documentation**: `GATE_SECURITY_README.md`
- **Implementation Summary**: `../GATE_SECURITY_IMPLEMENTATION.md`
- **API Docs**: http://localhost:8000/docs

## 🎉 Success!

You should now see:
- ✅ Real-time tracking
- ✅ FSM state transitions
- ✅ Check completions
- ✅ Database audit trail

The system is monitoring gate security and logging all events to the database!

