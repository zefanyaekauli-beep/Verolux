#!/usr/bin/env python3
"""
Event System for Gate Security
Handles micro-events and event logging for audit trails
"""

import time
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import deque
import json


class EventType(Enum):
    """Micro-event types"""
    # Person events
    P_ENTERED_GA = "person_entered_gate_area"
    P_EXITED_GA = "person_exited_gate_area"
    P_DWELL_THRESHOLD = "person_dwell_threshold_met"
    
    # Guard events
    G_ANCHORED = "guard_anchored"
    G_LEFT_ANCHOR = "guard_left_anchor"
    G_DWELL_THRESHOLD = "guard_dwell_threshold_met"
    
    # Interaction events
    P_CONTACT_WITH_G = "person_contact_with_guard"
    CONTACT_STARTED = "contact_started"
    CONTACT_ENDED = "contact_ended"
    
    # Pose events
    POSE_HAND_TO_TORSO = "pose_hand_toward_torso"
    POSE_REACH_GESTURE = "pose_reach_gesture"
    
    # Occlusion events
    OCCLUSION_START = "occlusion_started"
    OCCLUSION_END = "occlusion_ended"
    
    # Session events
    SESSION_STARTED = "session_started"
    SESSION_TIMEOUT = "session_timeout"
    
    # Decision events
    CHECK_COMPLETED = "check_completed"
    CHECK_FAILED = "check_failed"
    
    # State transitions
    STATE_CHANGED = "state_changed"


@dataclass
class Event:
    """Represents a micro-event"""
    event_type: EventType
    timestamp: float
    track_id: int
    related_track_id: Optional[int] = None
    
    # Event-specific data
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Location info
    zone_id: Optional[str] = None
    position: Optional[tuple] = None
    
    # Confidence/strength
    confidence: float = 1.0
    
    def __post_init__(self):
        if isinstance(self.event_type, str):
            self.event_type = EventType(self.event_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'event_type': self.event_type.value,
            'timestamp': self.timestamp,
            'track_id': self.track_id,
            'related_track_id': self.related_track_id,
            'metadata': self.metadata,
            'zone_id': self.zone_id,
            'position': self.position,
            'confidence': self.confidence
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


@dataclass
class ContactEvent:
    """Represents a contact/proximity event"""
    visitor_track_id: int
    guard_track_id: int
    started_at: float
    ended_at: Optional[float] = None
    
    # Contact metrics
    min_center_distance: float = float('inf')
    max_iou: float = 0.0
    avg_center_distance: float = 0.0
    avg_iou: float = 0.0
    
    # Samples for averaging
    _distance_samples: List[float] = field(default_factory=list)
    _iou_samples: List[float] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        """Get contact duration"""
        if self.ended_at is None:
            return time.time() - self.started_at
        return self.ended_at - self.started_at
    
    @property
    def is_active(self) -> bool:
        """Check if contact is still active"""
        return self.ended_at is None
    
    def update(self, center_distance: float, iou: float):
        """Update contact metrics"""
        self.min_center_distance = min(self.min_center_distance, center_distance)
        self.max_iou = max(self.max_iou, iou)
        
        self._distance_samples.append(center_distance)
        self._iou_samples.append(iou)
        
        # Update averages
        self.avg_center_distance = sum(self._distance_samples) / len(self._distance_samples)
        self.avg_iou = sum(self._iou_samples) / len(self._iou_samples)
    
    def end(self):
        """End the contact event"""
        if self.ended_at is None:
            self.ended_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'visitor_track_id': self.visitor_track_id,
            'guard_track_id': self.guard_track_id,
            'started_at': self.started_at,
            'ended_at': self.ended_at,
            'duration': self.duration,
            'min_center_distance': self.min_center_distance,
            'max_iou': self.max_iou,
            'avg_center_distance': self.avg_center_distance,
            'avg_iou': self.avg_iou
        }


class EventLogger:
    """Logs and manages events"""
    
    def __init__(self, max_history: int = 1000):
        self.events: deque = deque(maxlen=max_history)
        self.active_contacts: Dict[tuple, ContactEvent] = {}  # (visitor_id, guard_id) -> ContactEvent
        
        # Event counters by type
        self.event_counts: Dict[EventType, int] = {}
    
    def log_event(self, event: Event):
        """Log an event"""
        self.events.append(event)
        
        # Update counters
        if event.event_type not in self.event_counts:
            self.event_counts[event.event_type] = 0
        self.event_counts[event.event_type] += 1
    
    def create_event(self, event_type: EventType, track_id: int, **kwargs) -> Event:
        """Create and log an event"""
        event = Event(
            event_type=event_type,
            timestamp=time.time(),
            track_id=track_id,
            **kwargs
        )
        self.log_event(event)
        return event
    
    def start_contact(self, visitor_track_id: int, guard_track_id: int,
                     center_distance: float, iou: float) -> ContactEvent:
        """Start a new contact event"""
        key = (visitor_track_id, guard_track_id)
        
        if key in self.active_contacts:
            # Contact already active, just update
            self.active_contacts[key].update(center_distance, iou)
            return self.active_contacts[key]
        
        # Create new contact event
        contact = ContactEvent(
            visitor_track_id=visitor_track_id,
            guard_track_id=guard_track_id,
            started_at=time.time()
        )
        contact.update(center_distance, iou)
        
        self.active_contacts[key] = contact
        
        # Log micro-event
        self.create_event(
            EventType.CONTACT_STARTED,
            track_id=visitor_track_id,
            related_track_id=guard_track_id,
            metadata={
                'center_distance': center_distance,
                'iou': iou
            }
        )
        
        return contact
    
    def update_contact(self, visitor_track_id: int, guard_track_id: int,
                      center_distance: float, iou: float):
        """Update ongoing contact"""
        key = (visitor_track_id, guard_track_id)
        
        if key not in self.active_contacts:
            # Start new contact
            return self.start_contact(visitor_track_id, guard_track_id, 
                                     center_distance, iou)
        
        self.active_contacts[key].update(center_distance, iou)
    
    def end_contact(self, visitor_track_id: int, guard_track_id: int) -> Optional[ContactEvent]:
        """End a contact event"""
        key = (visitor_track_id, guard_track_id)
        
        if key not in self.active_contacts:
            return None
        
        contact = self.active_contacts[key]
        contact.end()
        
        # Log micro-event
        self.create_event(
            EventType.CONTACT_ENDED,
            track_id=visitor_track_id,
            related_track_id=guard_track_id,
            metadata={
                'duration': contact.duration,
                'min_center_distance': contact.min_center_distance,
                'max_iou': contact.max_iou
            }
        )
        
        # Remove from active
        del self.active_contacts[key]
        
        return contact
    
    def get_contact(self, visitor_track_id: int, guard_track_id: int) -> Optional[ContactEvent]:
        """Get active contact event"""
        key = (visitor_track_id, guard_track_id)
        return self.active_contacts.get(key)
    
    def get_events_for_track(self, track_id: int, 
                           event_types: Optional[List[EventType]] = None,
                           since: Optional[float] = None) -> List[Event]:
        """Get events for a specific track"""
        filtered = []
        
        for event in self.events:
            # Check track ID
            if event.track_id != track_id and event.related_track_id != track_id:
                continue
            
            # Check event type
            if event_types is not None and event.event_type not in event_types:
                continue
            
            # Check timestamp
            if since is not None and event.timestamp < since:
                continue
            
            filtered.append(event)
        
        return filtered
    
    def get_events_in_timewindow(self, start_time: float, end_time: float,
                                event_types: Optional[List[EventType]] = None) -> List[Event]:
        """Get events in time window"""
        filtered = []
        
        for event in self.events:
            if event.timestamp < start_time or event.timestamp > end_time:
                continue
            
            if event_types is not None and event.event_type not in event_types:
                continue
            
            filtered.append(event)
        
        return filtered
    
    def get_event_timeline(self, track_id: int) -> List[Dict[str, Any]]:
        """Get chronological timeline of events for a track"""
        events = self.get_events_for_track(track_id)
        events.sort(key=lambda e: e.timestamp)
        
        return [e.to_dict() for e in events]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        return {
            'total_events': len(self.events),
            'active_contacts': len(self.active_contacts),
            'event_counts': {
                event_type.value: count 
                for event_type, count in self.event_counts.items()
            }
        }
    
    def clear_old_events(self, before_timestamp: float):
        """Clear events older than timestamp"""
        # Note: deque doesn't support efficient removal from middle
        # This is a limitation; in production, use a database
        pass
    
    def export_events(self, filepath: str, 
                     start_time: Optional[float] = None,
                     end_time: Optional[float] = None):
        """Export events to JSON file"""
        if start_time is None:
            start_time = 0.0
        if end_time is None:
            end_time = time.time()
        
        events = self.get_events_in_timewindow(start_time, end_time)
        
        export_data = {
            'start_time': start_time,
            'end_time': end_time,
            'event_count': len(events),
            'events': [e.to_dict() for e in events]
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)


class SessionManager:
    """Manages check sessions"""
    
    @dataclass
    class CheckSession:
        """Represents a check session"""
        session_id: str
        visitor_track_id: int
        guard_track_id: Optional[int]
        started_at: float
        ended_at: Optional[float] = None
        
        # Dwell times
        visitor_dwell_time: float = 0.0
        guard_dwell_time: float = 0.0
        interaction_time: float = 0.0
        
        # State
        state: str = "IDLE"
        
        # Completion status
        completed: bool = False
        score: float = 0.0
        
        # Timeline
        events: List[Event] = field(default_factory=list)
        
        def __post_init__(self):
            if not self.session_id:
                self.session_id = f"{self.visitor_track_id}_{int(self.started_at * 1000)}"
        
        @property
        def duration(self) -> float:
            if self.ended_at is None:
                return time.time() - self.started_at
            return self.ended_at - self.started_at
        
        def end(self):
            if self.ended_at is None:
                self.ended_at = time.time()
        
        def to_dict(self) -> Dict[str, Any]:
            return {
                'session_id': self.session_id,
                'visitor_track_id': self.visitor_track_id,
                'guard_track_id': self.guard_track_id,
                'started_at': self.started_at,
                'ended_at': self.ended_at,
                'duration': self.duration,
                'visitor_dwell_time': self.visitor_dwell_time,
                'guard_dwell_time': self.guard_dwell_time,
                'interaction_time': self.interaction_time,
                'state': self.state,
                'completed': self.completed,
                'score': self.score,
                'event_count': len(self.events)
            }
    
    def __init__(self):
        self.active_sessions: Dict[int, SessionManager.CheckSession] = {}  # visitor_track_id -> Session
        self.completed_sessions: List[SessionManager.CheckSession] = []
    
    def create_session(self, visitor_track_id: int, 
                      guard_track_id: Optional[int] = None) -> CheckSession:
        """Create a new check session"""
        session = self.CheckSession(
            session_id="",
            visitor_track_id=visitor_track_id,
            guard_track_id=guard_track_id,
            started_at=time.time()
        )
        
        self.active_sessions[visitor_track_id] = session
        return session
    
    def get_session(self, visitor_track_id: int) -> Optional[CheckSession]:
        """Get active session for visitor"""
        return self.active_sessions.get(visitor_track_id)
    
    def end_session(self, visitor_track_id: int):
        """End a session"""
        if visitor_track_id not in self.active_sessions:
            return
        
        session = self.active_sessions[visitor_track_id]
        session.end()
        
        # Move to completed
        self.completed_sessions.append(session)
        del self.active_sessions[visitor_track_id]
    
    def get_all_sessions(self) -> List[CheckSession]:
        """Get all sessions (active + completed)"""
        return list(self.active_sessions.values()) + self.completed_sessions

