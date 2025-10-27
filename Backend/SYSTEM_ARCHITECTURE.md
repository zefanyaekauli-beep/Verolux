# Gate Security System - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INPUT SOURCES                                │
├─────────────────────────────────────────────────────────────────────┤
│  Webcam  │  IP Camera  │  Video File  │  YouTube  │  RTSP Stream   │
└────┬─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    YOLO DETECTION (backend_server.py)                │
├─────────────────────────────────────────────────────────────────────┤
│  • YOLOv8n person detection                                          │
│  • Confidence filtering (>0.3)                                       │
│  • Bounding box normalization                                        │
└────┬─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────┐
│              GATE CHECKER (gate_sop_checker.py)                      │
│                    3-LAYER PIPELINE                                  │
└─────────────────────────────────────────────────────────────────────┘
     │
     ├─────► LAYER 1: PERCEPTION
     │       ┌──────────────────────────────────────────────────┐
     │       │  tracking_system.py                              │
     │       │  • ByteTrack multi-object tracking               │
     │       │  • IoU + center distance matching                │
     │       │  • Track history & velocity estimation           │
     │       └────┬─────────────────────────────────────────────┘
     │            │
     │       ┌────▼─────────────────────────────────────────────┐
     │       │  zone_utils.py                                   │
     │       │  • Point-in-polygon testing                      │
     │       │  • Gate area & guard anchor detection            │
     │       │  • Proximity calculation (IoU + center distance) │
     │       │  • Jitter filtering (Savitzky-Golay)             │
     │       └────┬─────────────────────────────────────────────┘
     │            │
     │       ┌────▼─────────────────────────────────────────────┐
     │       │  pose_estimator.py                               │
     │       │  • YOLOv8-pose keypoint detection                │
     │       │  • Hand-to-torso detection                       │
     │       │  • Reach gesture detection                       │
     │       └──────────────────────────────────────────────────┘
     │
     ├─────► LAYER 2: EVENTS
     │       ┌──────────────────────────────────────────────────┐
     │       │  event_system.py                                 │
     │       │  • Micro-event logging                           │
     │       │    - P_ENTERED_GA, P_EXITED_GA                   │
     │       │    - G_ANCHORED, G_LEFT_ANCHOR                   │
     │       │    - CONTACT_STARTED, CONTACT_ENDED              │
     │       │    - POSE_HAND_TO_TORSO, POSE_REACH_GESTURE      │
     │       │  • Contact event tracking                        │
     │       │  • Session management                            │
     │       └──────────────────────────────────────────────────┘
     │
     └─────► LAYER 3: DECISIONS
             ┌──────────────────────────────────────────────────┐
             │  fsm_decision.py                                 │
             │  • FSM per person (5 states)                     │
             │    IDLE → PRESENT_IN_GA → GUARD_PRESENT          │
             │         → INTERACTION_WINDOW → CHECK_COMPLETED   │
             │  • Hysteresis logic                              │
             │  • Multi-signal confirmation                     │
             │  • Explainable scoring:                          │
             │    score = base + contact + pose + persistence   │
             │  • Guard qualification logic                     │
             └────┬─────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   STORAGE (gate_database.py)                         │
├─────────────────────────────────────────────────────────────────────┤
│  SQLite Database: gate_security.db                                   │
│  ┌────────────┬────────────────┬──────────────┬─────────────────┐   │
│  │  Events    │  Sessions      │  Contacts    │  Completions    │   │
│  │  Poses     │  Snapshots     │  Anomalies   │  Performance    │   │
│  └────────────┴────────────────┴──────────────┴─────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OUTPUT INTERFACES                                 │
├─────────────────────────────────────────────────────────────────────┤
│  WebSocket: /ws/gate-check                                           │
│    • Real-time stream (5 FPS)                                        │
│    • Decisions, events, stats                                        │
│    • Check completions                                               │
│                                                                       │
│  HTTP API:                                                           │
│    • GET  /gate/completions    - List completed checks               │
│    • GET  /gate/session/{id}   - Session details + timeline          │
│    • GET  /gate/stats          - Performance statistics              │
│    • GET  /gate/config         - Current configuration               │
│    • POST /gate/reset          - Reset checker state                 │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Frame Processing

```
Frame → YOLO → Detections → Tracker → Tracks
                                ↓
                          Zone Analysis
                                ↓
                          Pose Estimation
                                ↓
                        Proximity Calculation
```

### 2. Event Generation

```
Tracks → Zone Events     (P_ENTERED_GA, G_ANCHORED)
      → Contact Events   (CONTACT_STARTED, CONTACT_ENDED)
      → Pose Events      (POSE_HAND_TO_TORSO)
      → State Events     (STATE_CHANGED)
```

### 3. Decision Making

```
Person State: IDLE
    ↓ (enters gate area)
PRESENT_IN_GA
    ↓ (guard qualified)
GUARD_PRESENT
    ↓ (contact/pose detected)
INTERACTION_WINDOW
    ↓ (all criteria met + score ≥ 0.9)
CHECK_COMPLETED ✅
```

### 4. Scoring

```
Base Score:         0.60

+ Contact Quality:  0.20 × confidence
  └─ Based on: normalized center distance, IoU

+ Pose Detection:   0.15 × confidence
  └─ Based on: hand-to-torso count, reach gestures

+ Persistence:      0.05 × factor
  └─ Based on: session duration

────────────────────────
Total Score:        0.60 - 1.00

Threshold:          0.90 (configurable)
```

## Component Dependencies

```
gate_sop_checker.py (Main Orchestrator)
    │
    ├─── zone_utils.py
    │       └─── shapely, scipy
    │
    ├─── tracking_system.py
    │       └─── numpy, cv2
    │
    ├─── pose_estimator.py
    │       └─── ultralytics
    │
    ├─── event_system.py
    │       └─── (no external deps)
    │
    ├─── fsm_decision.py
    │       └─── (no external deps)
    │
    └─── gate_database.py
            └─── sqlite3, pandas
```

## Configuration Flow

```
gate_rules.demo.json
    │
    ├─── zones
    │     ├─── gate_area → gate_A1_polygon.json
    │     └─── guard_anchor → guard_anchor_A1_polygon.json
    │
    ├─── timers
    │     ├─── person_min_dwell_s: 6.0
    │     ├─── guard_min_dwell_s: 3.0
    │     └─── interaction_min_overlap_s: 1.2
    │
    ├─── proximity
    │     ├─── center_dist_scale: 0.35
    │     └─── iou_min: 0.03
    │
    ├─── pose
    │     ├─── use_pose: true
    │     └─── hand_to_torso_thresh: 0.28
    │
    ├─── guard_anchor_logic
    │     ├─── mode: "either"
    │     └─── anchor_required_fraction: 0.6
    │
    └─── scoring
          ├─── base: 0.6
          ├─── contact_bonus: 0.2
          ├─── pose_bonus: 0.15
          └─── threshold: 0.9
```

## State Machine Details

```
PersonState {
    track_id: int
    current_state: CheckState
    
    # Timers
    dwell_in_ga: float           # Time in gate area
    guard_overlap_time: float    # Time with qualified guard
    interaction_time: float      # Time in contact
    
    # Metrics
    min_center_distance: float
    max_iou: float
    pose_reach_count: int
    
    # Hysteresis counters
    consecutive_in_ga: int
    consecutive_contact: int
}

GuardState {
    track_id: int
    
    # Timers
    dwell_in_anchor: float
    dwell_in_ga: float
    
    # Status
    is_qualified: bool
    in_anchor: bool
    in_gate_area: bool
}
```

## Performance Characteristics

- **FPS**: ~5 FPS (configurable)
- **Latency**: < 200ms per frame
- **Memory**: ~500MB (with tracking history)
- **CPU**: 15-30% (without GPU)
- **GPU**: 5-10% (with CUDA)

## Scalability

**Single Gate:**
- ✅ Up to 10 simultaneous tracks
- ✅ Real-time processing
- ✅ Full audit trail

**Future Multi-Gate:**
- Multiple GateChecker instances
- Shared database
- Centralized monitoring

## Error Handling

```
Component Error → Fallback → Continue

Examples:
- Pose model fails → Use SimplePoseEstimator
- Zone file missing → Skip zone checks
- Database error → Log to console
- Track lost → Occlusion grace period
- Session timeout → Auto-reset state
```

## Security & Privacy

- ✅ Local processing (no cloud)
- ✅ Configurable snapshot retention
- ✅ Database encryption (optional)
- ✅ Audit trail for compliance
- ✅ No PII storage (track IDs only)

## Monitoring Points

```
System Health:
├─── FPS (target: 5)
├─── Active tracks
├─── Detection confidence
├─── Processing time
└─── Database size

Decision Quality:
├─── Check completion rate
├─── Average score
├─── Session duration
├─── False positive rate
└─── Missed detection rate
```

## Integration Points

**Frontend:**
- WebSocket client connects to `/ws/gate-check`
- Receives real-time updates
- Displays FSM state, score, events

**Analytics:**
- Query database for historical data
- Generate reports
- Trend analysis

**Alerting:**
- Hook into CHECK_COMPLETED events
- Monitor anomalies
- Performance degradation alerts

## Deployment Architecture

```
┌─────────────────────────────────────┐
│         Frontend (React)            │
│  ┌──────────────────────────────┐   │
│  │  Real-time Display           │   │
│  │  • Live camera feed          │   │
│  │  • Track visualization       │   │
│  │  • FSM state display         │   │
│  │  • Score dashboard           │   │
│  └──────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │ WebSocket
               ▼
┌─────────────────────────────────────┐
│      Backend (FastAPI + Python)     │
│  ┌──────────────────────────────┐   │
│  │  Gate Security Checker       │   │
│  │  • YOLO detection            │   │
│  │  • Tracking                  │   │
│  │  • FSM decisions             │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │  SQLite Database             │   │
│  │  • Events                    │   │
│  │  • Sessions                  │   │
│  │  • Audit trail               │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

