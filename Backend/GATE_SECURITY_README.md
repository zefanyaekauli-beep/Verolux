# Gate Security Checkpoint System

## Overview

This is a comprehensive, production-ready gate security checkpoint detection system with **high precision** under occlusion, crowding, and jitter conditions. The system provides **deterministic and explainable decisions** with a full audit trail.

## Key Features

✅ **3-Layer Pipeline Architecture**
- **Perception Layer**: Detections → Tracks → Zones → Pose → Proximity
- **Event Layer**: Micro-events (P_ENTERED_GA, G_ANCHORED, CONTACT_STARTED, etc.)
- **Decision Layer**: FSM + Scoring with hysteresis and multi-signal confirmation

✅ **High Precision**
- Multi-frame consensus
- Jitter filtering (Savitzky-Golay)
- Occlusion grace periods
- Re-ID track merging

✅ **Deterministic & Explainable**
- Finite State Machine per person
- Explainable scoring system
- Complete audit trail
- Event timeline for every decision

✅ **Configurable**
- Per-site JSON configuration
- No code changes needed
- Adjustable thresholds and timers

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                          │
├─────────────────────────────────────────────────────────────┤
│ Detections → Tracking (ByteTrack) → Zones → Pose → Proximity│
│                                                               │
│ • Zone detection (gate area, guard anchor)                   │
│ • Dwell time tracking with occlusion handling                │
│ • Contact detection (center distance + IoU)                  │
│ • Hand-to-torso pose detection (optional)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      EVENT LAYER                             │
├─────────────────────────────────────────────────────────────┤
│ Micro-Events with Timestamps                                 │
│                                                               │
│ • P_ENTERED_GA / P_EXITED_GA                                 │
│ • G_ANCHORED / G_LEFT_ANCHOR                                 │
│ • CONTACT_STARTED / CONTACT_ENDED                            │
│ • POSE_HAND_TO_TORSO / POSE_REACH_GESTURE                    │
│ • OCCLUSION_START / OCCLUSION_END                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    DECISION LAYER (FSM)                      │
├─────────────────────────────────────────────────────────────┤
│ States per Person:                                           │
│                                                               │
│ IDLE → PRESENT_IN_GA → GUARD_PRESENT → INTERACTION_WINDOW   │
│                                      → CHECK_COMPLETED        │
│                                                               │
│ Scoring:                                                      │
│   score = base + contact_bonus + pose_bonus + persistence    │
│   require: score ≥ threshold (e.g., 0.9)                     │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Gate Rules Configuration

Location: `Backend/config/gate_rules.demo.json`

```json
{
  "gate_id": "A1",
  "zones": {
    "gate_area": "gate_A1_polygon.json",
    "guard_anchor": "guard_anchor_A1_polygon.json"
  },
  "timers": {
    "person_min_dwell_s": 6.0,
    "guard_min_dwell_s": 3.0,
    "interaction_min_overlap_s": 1.2,
    "occlusion_grace_s": 1.0,
    "contact_debounce_s": 0.4,
    "session_timeout_s": 8.0
  },
  "proximity": {
    "center_dist_scale": 0.35,
    "iou_min": 0.03,
    "hands_toward_torso_margin": 0.12
  },
  "pose": {
    "use_pose": true,
    "hand_to_torso_thresh": 0.28,
    "reach_velocity_thresh": 0.6
  },
  "guard_anchor_logic": {
    "mode": "either",
    "anchor_required_fraction": 0.6
  },
  "scoring": {
    "base": 0.6,
    "contact_bonus": 0.2,
    "pose_bonus": 0.15,
    "reid_persistence_bonus": 0.05,
    "threshold": 0.9
  }
}
```

### Zone Definitions

Zones are defined as normalized polygons (0-1 coordinates):

**Gate Area** (`gate_A1_polygon.json`):
```json
{
  "zone_id": "gate_A1",
  "zone_type": "gate_area",
  "polygon": [
    [0.30, 0.20],
    [0.70, 0.20],
    [0.70, 0.80],
    [0.30, 0.80]
  ]
}
```

**Guard Anchor** (`guard_anchor_A1_polygon.json`):
```json
{
  "zone_id": "guard_anchor_A1",
  "zone_type": "guard_anchor",
  "polygon": [
    [0.10, 0.15],
    [0.25, 0.15],
    [0.25, 0.85],
    [0.10, 0.85]
  ]
}
```

## API Reference

### WebSocket Endpoint

**Connect to Gate Checker:**
```
ws://localhost:8000/ws/gate-check?source=webcam:0
```

**Message Types:**

1. **Connection Info** (received on connect):
```json
{
  "type": "connection_info",
  "gate_checker": true,
  "gate_id": "A1",
  "device": "cuda"
}
```

2. **Gate Check Results** (continuous stream):
```json
{
  "type": "gate_check",
  "ts": 1696723456.789,
  "fps": 5.2,
  "frame_count": 1234,
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
        "dwell_in_ga": 6.5,
        "interaction_time": 1.8
      }
    },
    "guards": {
      "456": {
        "is_qualified": true
      }
    },
    "completions": [
      {
        "session_id": "123_1696723456789",
        "visitor_track_id": 123,
        "guard_track_id": 456,
        "score": 0.95
      }
    ]
  }
}
```

### HTTP Endpoints

#### Get Check Completions
```
GET /gate/completions?start_time=1234567890&limit=100
```

Response:
```json
{
  "count": 15,
  "completions": [
    {
      "session_id": "123_1696723456789",
      "visitor_track_id": 123,
      "guard_track_id": 456,
      "completed_at": 1696723456.789,
      "score": 0.95,
      "visitor_dwell": 6.8,
      "guard_dwell": 5.2,
      "interaction_duration": 2.1
    }
  ]
}
```

#### Get Session Details
```
GET /gate/session/{session_id}
```

Response:
```json
{
  "session": {
    "session_id": "123_1696723456789",
    "visitor_track_id": 123,
    "guard_track_id": 456,
    "completed": true,
    "score": 0.95
  },
  "events": [
    {
      "event_type": "person_entered_gate_area",
      "timestamp": 1696723450.0,
      "track_id": 123
    },
    {
      "event_type": "guard_anchored",
      "timestamp": 1696723451.0,
      "track_id": 456
    }
  ]
}
```

#### Get Performance Statistics
```
GET /gate/stats?start_time=1234567890&end_time=1234567900
```

Response:
```json
{
  "total_checks": 156,
  "avg_score": 0.932,
  "total_events": 1248,
  "avg_processing_time_ms": 15.4,
  "current_state": {
    "active_tracks": 3,
    "total_persons": 2
  }
}
```

#### Get Configuration
```
GET /gate/config
```

#### Reset Checker
```
POST /gate/reset
```

## Database Schema

The system stores comprehensive audit trails in SQLite (`gate_security.db`):

### Tables

1. **events** - All micro-events
2. **sessions** - Check sessions
3. **contact_events** - Proximity interactions
4. **pose_events** - Pose detections
5. **check_completions** - Successful checks
6. **snapshots** - Frame snapshots
7. **anomalies** - Violations/anomalies
8. **performance_metrics** - System performance

## Tuning Guide

### Common Scenarios

**Too many missed detections:**
- Reduce `person_min_dwell_s` (default: 6.0 → 5.0)
- Reduce `interaction_min_overlap_s` (default: 1.2 → 1.0)
- Enable pose detection (`use_pose: true`)
- Lower score threshold (0.9 → 0.85)

**Too many false positives:**
- Increase `interaction_min_overlap_s` (1.2 → 1.5)
- Require both proximity AND pose (modify logic)
- Increase `multi_frame_consensus` (3 → 5)
- Increase score threshold (0.9 → 0.95)

**Handling occlusion:**
- Increase `occlusion_grace_s` (1.0 → 2.0)
- Adjust `reid_merge_time_s` (0.8 → 1.5)

**Guard flexibility:**
- Use `mode: "either"` for guards in anchor OR gate area
- Adjust `anchor_required_fraction` (0.6 → 0.5)

## Components

### 1. Zone Utilities (`zone_utils.py`)
- Polygon operations
- Point-in-polygon testing
- Proximity calculations
- Jitter filtering
- Kalman filtering

### 2. Tracking System (`tracking_system.py`)
- ByteTrack-style tracker
- IoU + center distance matching
- Re-ID support
- Track persistence

### 3. Pose Estimator (`pose_estimator.py`)
- YOLOv8-pose integration
- Hand-to-torso detection
- Reach gesture detection
- Fallback simple estimator

### 4. Event System (`event_system.py`)
- Micro-event logging
- Contact event tracking
- Session management
- Event timeline

### 5. FSM Decision Engine (`fsm_decision.py`)
- Per-person state machines
- Hysteresis logic
- Explainable scoring
- Timeout handling

### 6. Database (`gate_database.py`)
- SQLite storage
- Event logging
- Session tracking
- Query API

### 7. Gate Checker (`gate_sop_checker.py`)
- Main orchestrator
- 3-layer pipeline
- Visualization
- Integration

## Installation

```bash
cd Backend
pip install -r requirements.txt
```

Required packages:
- fastapi
- uvicorn
- opencv-python-headless
- ultralytics
- torch
- shapely
- scipy
- pandas
- numpy

## Running

### Start Backend with Gate Checker

```bash
cd Backend
python backend_server.py
```

### Access Endpoints

- WebSocket: `ws://localhost:8000/ws/gate-check?source=webcam:0`
- API: `http://localhost:8000/gate/completions`
- Health: `http://localhost:8000/health`

## Troubleshooting

### Gate checker not available
- Check if config files exist in `Backend/config/`
- Verify all dependencies are installed
- Check console for initialization errors

### Poor detection accuracy
- Adjust zone polygons to match camera view
- Tune thresholds in config
- Ensure proper lighting
- Check YOLO model performance

### Memory issues
- Reduce `max_history` in EventLogger
- Cleanup old database records
- Reduce snapshot retention

## Future Enhancements

- [ ] Multi-gate support
- [ ] Face recognition for guard identification
- [ ] Uniform detection for guard classification
- [ ] Real-time alerting system
- [ ] Advanced analytics dashboard
- [ ] Export to PDF reports
- [ ] Cloud sync for distributed gates
- [ ] ML-based anomaly detection

## License

Part of Verolux1st Security System

