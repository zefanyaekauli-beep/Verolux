#!/usr/bin/env python3
"""
Advanced Body Checking System with Group Detection and Queue Management
- Implements spatio-temporal group detection
- Ticket-based queue management
- Batch and Sequential examination modes
- Comprehensive audit trail
"""

import cv2
import numpy as np
import json
import time
import os
import uuid
import hashlib
from datetime import datetime, timedelta
from ultralytics import YOLO
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import asyncio
import logging
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import jwt
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security Configuration
SECRET_KEY = "your-production-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# User database (in production, use proper database)
USERS_DB = {
    "admin": {
        "password": hashlib.sha256("admin".encode()).hexdigest(),
        "role": "admin"
    },
    "viewer": {
        "password": hashlib.sha256("viewer".encode()).hexdigest(),
        "role": "viewer"
    }
}

# Initialize FastAPI
app = FastAPI(title="Advanced Body Checking System")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware - secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176",
        "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175", "http://127.0.0.1:5176",
        "http://192.168.0.102:5173", "http://192.168.0.102:5174", "http://192.168.0.102:5175", "http://192.168.0.102:5176",
        "http://172.16.0.2:5173", "http://172.16.0.2:5174", "http://172.16.0.2:5175", "http://172.16.0.2:5176",
    ],  # Specific origins for network access
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Include OPTIONS for preflight
    allow_headers=["Authorization", "Content-Type", "Accept"],  # Include Accept header
)

# Security components
security = HTTPBearer()

# Audit logging
audit_logger = logging.getLogger("audit")
audit_handler = logging.FileHandler("audit.log")
audit_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
audit_handler.setFormatter(audit_formatter)
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)

# Enums
class TicketStatus(Enum):
    WAITING = "waiting"
    ASSIGNING = "assigning"
    IN_CHECK = "in_check"
    IN_BATCH = "in_batch"
    CHECKED = "checked"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"
    VERIFY = "verify"

class ExaminationMode(Enum):
    BATCH = "batch"
    SEQUENTIAL = "sequential"

class PersonType(Enum):
    PERSON = "person"
    GUARD = "guard"

# Data Classes
@dataclass
class Person:
    id: str
    bbox: List[float]  # [x1, y1, x2, y2] normalized
    center: Tuple[float, float]
    confidence: float
    type: PersonType
    first_seen: float
    last_seen: float
    in_gate_area: bool
    in_guard_anchor: bool
    appearance_embedding: Optional[List[float]] = None
    # Guard identification fields
    anchor_entry_time: Optional[float] = None
    total_anchor_time: float = 0.0
    location_history: Optional[List[Dict]] = None
    guard_classification_time: Optional[float] = None

@dataclass
class Group:
    id: str
    members: List[str]  # Person IDs
    formed_at: float
    last_updated: float
    center: Tuple[float, float]
    is_stable: bool

@dataclass
class Ticket:
    id: str
    type: str  # "individual" or "group"
    members: List[str]  # Person IDs
    status: TicketStatus
    created_at: float
    ready_at: Optional[float]  # When ready for examination
    assigned_guard: Optional[str]
    examination_mode: ExaminationMode
    proximity_start: Optional[float]
    proximity_duration: float
    examination_start: Optional[float]
    examination_duration: float
    completed_at: Optional[float]
    escalated_reason: Optional[str]
    video_clips: List[str]  # Paths to video clips
    metadata: Dict

@dataclass
class Guard:
    id: str
    person_id: str
    active_since: float
    last_seen: float
    is_active: bool
    current_ticket: Optional[str]

# Configuration Parameters
CONFIG = {
    # Group Detection
    "T_GROUP": 2.0,  # Time window for group formation (seconds)
    "D_MAX": 0.15,   # Max distance for group membership (normalized)
    "T_LOCK": 1.0,   # Minimum time to stabilize group
    "T_BREAK": 2.0,  # Time to break group when separated
    
    # Examination Requirements
    "PRESENCE_TO_CHECK": 6.0,  # Time in gate area before ready
    "GUARD_READY": 3.0,        # Guard must be active for this long
    "PROXIMITY_MIN": 2.0,      # Minimum proximity duration
    "CHECK_MIN_INDIVIDUAL": 3.0,  # Min examination time per person
    "CHECK_MIN_BATCH": 4.0,    # Min total interaction for batch
    
    # Queue Management
    "T_WARN": 30.0,            # Warning threshold
    "T_MAX_WAIT": 45.0,        # Maximum wait time
    "T_VACATE": 2.0,           # Guard vacate threshold
    "T_REJOIN": 10.0,          # Rejoin threshold
    
    # Detection Thresholds
    "PERSON_CONFIDENCE": 0.5,
    "GUARD_CONFIDENCE": 0.5,
    "IOU_THRESHOLD": 0.02,
}

# Global variables
model = None
video_cap = None
current_frame = None
frame_width = 640
frame_height = 360

# State management
state_lock = threading.Lock()
persons: Dict[str, Person] = {}
groups: Dict[str, Group] = {}
tickets: Dict[str, Ticket] = {}
guards: Dict[str, Guard] = {}
queue: List[str] = []  # Ticket IDs in order

# Gate configuration
gate_config_lock = threading.Lock()
gate_config = {
    "gate_area": {"x": 0.3, "y": 0.2, "width": 0.4, "height": 0.6},
    "guard_anchor": {"x": 0.1, "y": 0.15, "width": 0.15, "height": 0.7},
    "enabled": True,
    "examination_mode": "sequential"  # "batch" or "sequential"
}

# Video source configuration
video_source_lock = threading.Lock()
video_source = "file:videoplayback.mp4"  # Default: video file (format: "file:path" or "webcam:0")

# Statistics
stats = {
    "total_processed": 0,
    "total_escalated": 0,
    "average_wait_time": 0.0,
    "current_queue_length": 0,
    "active_guards": 0,
    "throughput_per_hour": 0.0
}

# Object Counting Statistics
object_counts = {
    "total_detected": 0,  # Total unique objects ever detected
    "gate_entries": 0,  # Objects entering gate area
    "gate_exits": 0,  # Objects exiting gate area
    "anchor_entries": 0,  # Objects entering guard anchor
    "anchor_exits": 0,  # Objects exiting guard anchor
    "current_in_gate": 0,  # Currently in gate area
    "current_in_anchor": 0,  # Currently in guard anchor
    "total_passed_through": 0  # Objects that fully passed through gate
}

# Track previous state for each person to detect transitions
person_previous_state = {}  # {person_id: {"in_gate": bool, "in_anchor": bool}}

# Authentication functions
def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(required_role: str):
    """Require specific role for access"""
    def role_checker(user: str = Depends(verify_token)):
        user_role = USERS_DB[user]["role"]
        if user_role != required_role and user_role != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker

def log_admin_action(action: str, user: str, details: dict):
    """Log admin actions for audit trail"""
    audit_logger.info(f"ADMIN_ACTION: {action} by {user} - {details}")

def verify_websocket_token(token: str):
    """Verify token for WebSocket connections"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
        return username
    except jwt.PyJWTError:
        return None

def get_gate_config_copy():
    """Thread-safe copy of gate configuration"""
    with gate_config_lock:
        return gate_config.copy()

def update_gate_config(new_config):
    """Thread-safe update of gate configuration"""
    with gate_config_lock:
        gate_config.update(new_config)

def get_video_source():
    """Get current video source"""
    with video_source_lock:
        return video_source

def set_video_source(new_source: str):
    """Update video source and reopen capture"""
    global video_cap, frame_width, frame_height, video_source
    
    with video_source_lock:
        video_source = new_source
        
        # Close existing capture
        if video_cap:
            video_cap.release()
        
        # Open new source
        try:
            if new_source.startswith("webcam:"):
                # Extract camera index: webcam:0, webcam:1, etc.
                cam_index = int(new_source.split(":")[1]) if ":" in new_source else 0
                video_cap = cv2.VideoCapture(cam_index)
                logger.info(f"Opening webcam {cam_index}")
            elif new_source.startswith("file:"):
                # Extract file path: file:videoplayback.mp4
                file_path = new_source.split(":", 1)[1]
                if not os.path.isabs(file_path):
                    file_path = os.path.join("..", file_path)
                video_cap = cv2.VideoCapture(file_path)
                logger.info(f"Opening video file: {file_path}")
            else:
                # Default: try as direct path or camera index
                if os.path.exists(new_source):
                    video_cap = cv2.VideoCapture(new_source)
                    logger.info(f"Opening video file: {new_source}")
                else:
                    # Try as camera index
                    try:
                        cam_idx = int(new_source)
                        video_cap = cv2.VideoCapture(cam_idx)
                        logger.info(f"Opening webcam {cam_idx}")
                    except ValueError:
                        logger.error(f"Invalid source format: {new_source}")
                        return False
            
            if video_cap.isOpened():
                frame_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                logger.info(f"Video source changed to: {new_source} ({frame_width}x{frame_height})")
                return True
            else:
                logger.error(f"Failed to open source: {new_source}")
                return False
        except Exception as e:
            logger.error(f"Error opening video source {new_source}: {e}")
            return False

def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points"""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calculate_iou(box1: List[float], box2: List[float]) -> float:
    """Calculate Intersection over Union of two bounding boxes"""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    if x2 <= x1 or y2 <= y1:
        return 0.0
    
    intersection = (x2 - x1) * (y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0.0

def is_in_area(center: Tuple[float, float], area: Dict) -> bool:
    """Check if a point is within a defined area"""
    x, y = center
    return (area["x"] <= x <= area["x"] + area["width"] and
            area["y"] <= y <= area["y"] + area["height"])

def detect_groups(current_persons: Dict[str, Person], current_time: float) -> Dict[str, Group]:
    """Detect groups based on spatio-temporal criteria"""
    new_groups = {}
    
    # Find persons in gate area
    gate_persons = {pid: p for pid, p in current_persons.items() 
                   if p.in_gate_area and p.type == PersonType.PERSON}
    
    if len(gate_persons) < 2:
        return new_groups
    
    # Group detection algorithm
    person_ids = list(gate_persons.keys())
    
    for i, pid1 in enumerate(person_ids):
        person1 = gate_persons[pid1]
        
        # Check if person1 is already in a group
        already_grouped = any(pid1 in group.members for group in groups.values())
        if already_grouped:
            continue
            
        group_members = [pid1]
        group_center = person1.center
        
        for j, pid2 in enumerate(person_ids[i+1:], i+1):
            person2 = gate_persons[pid2]
            
            # Check if person2 is already in a group
            if any(pid2 in group.members for group in groups.values()):
                continue
            
            # Check spatial proximity
            distance = calculate_distance(person1.center, person2.center)
            iou = calculate_iou(person1.bbox, person2.bbox)
            
            if distance <= CONFIG["D_MAX"] or iou >= CONFIG["IOU_THRESHOLD"]:
                # Check temporal proximity
                time_diff = abs(person1.first_seen - person2.first_seen)
                if time_diff <= CONFIG["T_GROUP"]:
                    group_members.append(pid2)
                    # Update group center
                    group_center = (
                        (group_center[0] * (len(group_members) - 1) + person2.center[0]) / len(group_members),
                        (group_center[1] * (len(group_members) - 1) + person2.center[1]) / len(group_members)
                    )
        
        # Create group if we have multiple members
        if len(group_members) > 1:
            group_id = str(uuid.uuid4())
            new_groups[group_id] = Group(
                id=group_id,
                members=group_members,
                formed_at=current_time,
                last_updated=current_time,
                center=group_center,
                is_stable=True
            )
    
    return new_groups

def update_existing_groups(current_persons: Dict[str, Person], current_time: float):
    """Update existing groups and handle splitting"""
    groups_to_remove = []
    groups_to_split = []
    
    for group_id, group in groups.items():
        # Check if all members are still present
        active_members = [pid for pid in group.members if pid in current_persons]
        
        if len(active_members) == 0:
            groups_to_remove.append(group_id)
            continue
        
        if len(active_members) < len(group.members):
            # Some members left
            group.members = active_members
            group.last_updated = current_time
        
        # Check for group splitting due to separation
        if len(active_members) > 1:
            # Calculate distances between all pairs
            max_distance = 0
            for i, pid1 in enumerate(active_members):
                for pid2 in active_members[i+1:]:
                    distance = calculate_distance(
                        current_persons[pid1].center,
                        current_persons[pid2].center
                    )
                    max_distance = max(max_distance, distance)
            
            # If group is too spread out, consider splitting
            if max_distance > CONFIG["D_MAX"] * 1.5:
                # Check if separation has been sustained
                if current_time - group.last_updated > CONFIG["T_BREAK"]:
                    groups_to_split.append(group_id)
    
    # Remove empty groups
    for group_id in groups_to_remove:
        del groups[group_id]
    
    # Split groups that are too separated
    for group_id in groups_to_split:
        group = groups[group_id]
        if len(group.members) > 1:
            # Split into individual tickets
            split_group(group_id, current_time)
        del groups[group_id]

def split_group(group_id: str, current_time: float):
    """Split a group into individual tickets"""
    group = groups[group_id]
    
    # Find the group's ticket
    group_ticket = None
    for ticket in tickets.values():
        if ticket.type == "group" and set(ticket.members) == set(group.members):
            group_ticket = ticket
            break
    
    if group_ticket:
        # Create individual tickets for each member
        for member_id in group.members:
            individual_ticket = Ticket(
                id=str(uuid.uuid4()),
                type="individual",
                members=[member_id],
                status=TicketStatus.WAITING,
                created_at=current_time,
                ready_at=group_ticket.ready_at,
                assigned_guard=None,
                examination_mode=ExaminationMode.SEQUENTIAL,
                proximity_start=None,
                proximity_duration=0.0,
                examination_start=None,
                examination_duration=0.0,
                completed_at=None,
                escalated_reason=None,
                video_clips=[],
                metadata={"split_from_group": group_id}
            )
            tickets[individual_ticket.id] = individual_ticket
            queue.append(individual_ticket.id)
        
        # Cancel the original group ticket
        group_ticket.status = TicketStatus.CANCELLED
        group_ticket.escalated_reason = "Group split due to separation"

def create_tickets_for_individuals(current_persons: Dict[str, Person], current_time: float):
    """Create tickets for individuals not in groups"""
    gate_persons = {pid: p for pid, p in current_persons.items() 
                   if p.in_gate_area and p.type == PersonType.PERSON}
    
    # Find persons not in any group
    grouped_person_ids = set()
    for group in groups.values():
        grouped_person_ids.update(group.members)
    
    ungrouped_persons = {pid: p for pid, p in gate_persons.items() 
                        if pid not in grouped_person_ids}
    
    # Create tickets for ungrouped persons who have been in gate area long enough
    for pid, person in ungrouped_persons.items():
        time_in_gate = current_time - person.first_seen
        
        if time_in_gate >= CONFIG["PRESENCE_TO_CHECK"]:
            # Check if ticket already exists
            existing_ticket = None
            for ticket in tickets.values():
                if ticket.type == "individual" and pid in ticket.members and ticket.status in [TicketStatus.WAITING, TicketStatus.ASSIGNING, TicketStatus.IN_CHECK]:
                    existing_ticket = ticket
                    break
            
            if not existing_ticket:
                ticket = Ticket(
                    id=str(uuid.uuid4()),
                    type="individual",
                    members=[pid],
                    status=TicketStatus.WAITING,
                    created_at=current_time,
                    ready_at=current_time,
                    assigned_guard=None,
                    examination_mode=ExaminationMode.SEQUENTIAL,
                    proximity_start=None,
                    proximity_duration=0.0,
                    examination_start=None,
                    examination_duration=0.0,
                    completed_at=None,
                    escalated_reason=None,
                    video_clips=[],
                    metadata={}
                )
                tickets[ticket.id] = ticket
                queue.append(ticket.id)

def create_tickets_for_groups(current_time: float):
    """Create tickets for stable groups"""
    for group_id, group in groups.items():
        # Check if group is stable (existed for T_LOCK time)
        if current_time - group.formed_at >= CONFIG["T_LOCK"]:
            # Check if ticket already exists
            existing_ticket = None
            for ticket in tickets.values():
                if ticket.type == "group" and set(ticket.members) == set(group.members) and ticket.status in [TicketStatus.WAITING, TicketStatus.ASSIGNING, TicketStatus.IN_BATCH]:
                    existing_ticket = ticket
                    break
            
            if not existing_ticket:
                # Determine examination mode based on configuration
                mode = ExaminationMode.BATCH if gate_config.get("examination_mode") == "batch" else ExaminationMode.SEQUENTIAL
                
                ticket = Ticket(
                    id=str(uuid.uuid4()),
                    type="group",
                    members=group.members.copy(),
                    status=TicketStatus.WAITING,
                    created_at=current_time,
                    ready_at=current_time,
                    assigned_guard=None,
                    examination_mode=mode,
                    proximity_start=None,
                    proximity_duration=0.0,
                    examination_start=None,
                    examination_duration=0.0,
                    completed_at=None,
                    escalated_reason=None,
                    video_clips=[],
                    metadata={"group_id": group_id}
                )
                tickets[ticket.id] = ticket
                queue.append(ticket.id)

def update_guard_status(current_persons: Dict[str, Person], current_time: float):
    """Update guard status and track active guards"""
    guard_persons = {pid: p for pid, p in current_persons.items() 
                    if p.in_guard_anchor and p.type == PersonType.GUARD}
    
    # Update existing guards
    for guard_id, guard in guards.items():
        if guard.person_id in guard_persons:
            guard.last_seen = current_time
            # Check if guard has been active long enough
            if current_time - guard.active_since >= CONFIG["GUARD_READY"]:
                guard.is_active = True
            else:
                guard.is_active = False
        else:
            # Guard left the anchor area
            if current_time - guard.last_seen > CONFIG["T_VACATE"]:
                guard.is_active = False
                # Handle current ticket if any
                if guard.current_ticket:
                    handle_guard_vacation(guard.current_ticket, current_time)
    
    # Add new guards
    for pid, person in guard_persons.items():
        if not any(g.person_id == pid for g in guards.values()):
            guard = Guard(
                id=str(uuid.uuid4()),
                person_id=pid,
                active_since=current_time,
                last_seen=current_time,
                is_active=False,
                current_ticket=None
            )
            guards[guard.id] = guard

def handle_guard_vacation(ticket_id: str, current_time: float):
    """Handle when a guard leaves during examination"""
    if ticket_id in tickets:
        ticket = tickets[ticket_id]
        ticket.status = TicketStatus.ESCALATED
        ticket.escalated_reason = "Guard left during examination"
        ticket.completed_at = current_time
        
        # Remove from queue if still there
        if ticket_id in queue:
            queue.remove(ticket_id)

def assign_tickets_to_guards(current_time: float):
    """Assign waiting tickets to available guards"""
    available_guards = [g for g in guards.values() if g.is_active and g.current_ticket is None]
    
    if not available_guards:
        return
    
    # Process queue in FIFO order
    for ticket_id in queue[:]:
        if ticket_id not in tickets:
            queue.remove(ticket_id)
            continue
            
        ticket = tickets[ticket_id]
        
        if ticket.status != TicketStatus.WAITING:
            continue
        
        # Assign to first available guard
        if available_guards:
            guard = available_guards.pop(0)
            ticket.assigned_guard = guard.id
            ticket.status = TicketStatus.ASSIGNING
            guard.current_ticket = ticket_id
            
            logger.info(f"Assigned ticket {ticket_id} to guard {guard.id}")

def update_ticket_status(current_persons: Dict[str, Person], current_time: float):
    """Update ticket status based on current state"""
    for ticket_id, ticket in tickets.items():
        if ticket.status in [TicketStatus.ASSIGNING, TicketStatus.IN_CHECK, TicketStatus.IN_BATCH]:
            guard_id = ticket.assigned_guard
            if guard_id and guard_id in guards:
                guard = guards[guard_id]
                
                # Check if guard is still active
                if not guard.is_active:
                    handle_guard_vacation(ticket_id, current_time)
                    continue
                
                # Check proximity between guard and ticket members
                guard_person = current_persons.get(guard.person_id)
                if not guard_person:
                    continue
                
                proximity_detected = False
                for member_id in ticket.members:
                    member = current_persons.get(member_id)
                    if member and member.in_gate_area:
                        distance = calculate_distance(guard_person.center, member.center)
                        if distance <= CONFIG["D_MAX"]:
                            proximity_detected = True
                            break
                
                if proximity_detected:
                    if ticket.proximity_start is None:
                        ticket.proximity_start = current_time
                    else:
                        ticket.proximity_duration = current_time - ticket.proximity_start
                    
                    # Check if proximity duration meets requirements
                    if ticket.proximity_duration >= CONFIG["PROXIMITY_MIN"]:
                        if ticket.status == TicketStatus.ASSIGNING:
                            if ticket.type == "individual":
                                ticket.status = TicketStatus.IN_CHECK
                            else:
                                ticket.status = TicketStatus.IN_BATCH
                            ticket.examination_start = current_time
                        
                        # Check examination duration
                        if ticket.examination_start:
                            ticket.examination_duration = current_time - ticket.examination_start
                            
                            min_duration = CONFIG["CHECK_MIN_INDIVIDUAL"] if ticket.type == "individual" else CONFIG["CHECK_MIN_BATCH"]
                            
                            if ticket.examination_duration >= min_duration:
                                # Check if all members are still in gate area
                                all_in_gate = all(
                                    current_persons.get(mid, Person("", [], (0,0), 0, PersonType.PERSON, 0, 0, False, False)).in_gate_area
                                    for mid in ticket.members
                                )
                                
                                if all_in_gate:
                                    ticket.status = TicketStatus.CHECKED
                                    ticket.completed_at = current_time
                                    
                                    # Release guard
                                    if guard_id in guards:
                                        guards[guard_id].current_ticket = None
                                    
                                    # Remove from queue
                                    if ticket_id in queue:
                                        queue.remove(ticket_id)
                                    
                                    logger.info(f"Ticket {ticket_id} completed successfully")
                                else:
                                    ticket.status = TicketStatus.ESCALATED
                                    ticket.escalated_reason = "Member left gate area during examination"
                                    ticket.completed_at = current_time
                else:
                    # Reset proximity if not detected
                    ticket.proximity_start = None
                    ticket.proximity_duration = 0.0

def check_escalation_conditions(current_time: float):
    """Check for tickets that need escalation"""
    for ticket_id, ticket in tickets.items():
        if ticket.status == TicketStatus.WAITING:
            wait_time = current_time - ticket.ready_at if ticket.ready_at else current_time - ticket.created_at
            
            if wait_time > CONFIG["T_MAX_WAIT"]:
                ticket.status = TicketStatus.ESCALATED
                ticket.escalated_reason = "Maximum wait time exceeded"
                ticket.completed_at = current_time
                
                # Remove from queue
                if ticket_id in queue:
                    queue.remove(ticket_id)
                
                logger.warning(f"Ticket {ticket_id} escalated due to wait time")

def update_statistics():
    """Update system statistics"""
    with state_lock:
        stats["current_queue_length"] = len(queue)
        stats["active_guards"] = len([g for g in guards.values() if g.is_active])
        
        # Calculate average wait time
        completed_tickets = [t for t in tickets.values() if t.completed_at]
        if completed_tickets:
            wait_times = []
            for ticket in completed_tickets:
                wait_time = (ticket.examination_start or ticket.completed_at) - (ticket.ready_at or ticket.created_at)
                wait_times.append(wait_time)
            stats["average_wait_time"] = sum(wait_times) / len(wait_times)
        
        stats["total_processed"] = len([t for t in tickets.values() if t.status == TicketStatus.CHECKED])
        stats["total_escalated"] = len([t for t in tickets.values() if t.status == TicketStatus.ESCALATED])

def identify_guards_by_location():
    """Identify guards based on location and duration in guard anchor area"""
    current_time = time.time()
    
    for person_id, person in persons.items():
        # Initialize location history if needed
        if person.location_history is None:
            person.location_history = []
        
        # Record current location
        person.location_history.append({
            'time': current_time,
            'in_anchor': person.in_guard_anchor,
            'in_gate': person.in_gate_area
        })
        
        # Keep only last 10 seconds of history
        person.location_history = [
            h for h in person.location_history 
            if current_time - h['time'] < 10.0
        ]
        
        # Track time in guard anchor
        if person.in_guard_anchor:
            if person.anchor_entry_time is None:
                person.anchor_entry_time = current_time
            
            # Calculate time spent in anchor
            time_in_anchor = current_time - person.anchor_entry_time
            person.total_anchor_time = time_in_anchor
            
            # If person has been in guard anchor for GUARD_READY duration, classify as guard
            if time_in_anchor >= CONFIG["GUARD_READY"]:
                if person.type != PersonType.GUARD:
                    person.type = PersonType.GUARD
                    person.guard_classification_time = current_time
                    logger.info(f"Person {person_id} identified as GUARD based on location (spent {time_in_anchor:.2f}s in anchor)")
            
            # Check for guard movement patterns: guards move between anchor and gate
            if len(person.location_history) >= 3:
                anchor_visits = sum(1 for h in person.location_history if h['in_anchor'])
                gate_visits = sum(1 for h in person.location_history if h['in_gate'])
                
                # Guard pattern: spends time in anchor, then moves to gate for examination
                if anchor_visits >= 2 and gate_visits >= 1:
                    if person.type != PersonType.GUARD:
                        person.type = PersonType.GUARD
                        person.guard_classification_time = current_time
                        logger.info(f"Person {person_id} identified as GUARD based on movement pattern")
        else:
            # Person not currently in anchor
            if person.anchor_entry_time is not None:
                # Check if they left recently
                time_since_exit = current_time - person.anchor_entry_time
                
                # If they left more than T_VACATE ago, reset anchor tracking
                if time_since_exit > CONFIG["T_VACATE"]:
                    # Check if they should still be classified as guard
                    # Keep guard status if they were recently classified as guard
                    if person.guard_classification_time and person.type == PersonType.GUARD:
                        time_as_guard = current_time - person.guard_classification_time
                        if time_as_guard > 30.0:  # Been a guard for at least 30 seconds
                            # Downgrade to person if they're not returning to anchor
                            total_recent_anchor_time = sum(
                                h['time'] for h in person.location_history 
                                if h['in_anchor'] and current_time - h['time'] < 10.0
                            )
                            if total_recent_anchor_time < 1.0:
                                person.type = PersonType.PERSON
                                logger.info(f"Person {person_id} downgraded from GUARD to PERSON")
                    
                    person.anchor_entry_time = None
                    person.total_anchor_time = 0.0

def process_detections(detections, gate_config):
    """Main processing function for detections"""
    current_time = time.time()
    
    with state_lock:
        # Update persons from detections
        current_persons = {}
        for detection in detections:
            if detection.get("cls_id") == 0 and detection.get("conf", 0) > CONFIG["PERSON_CONFIDENCE"]:
                bbox = detection.get("bbox", [0, 0, 0, 0])
                center_x = (bbox[0] + bbox[2]) / 2 / frame_width
                center_y = (bbox[1] + bbox[3]) / 2 / frame_height
                
                person_id = str(uuid.uuid4())  # In real implementation, use stable ID tracking
                
                person = Person(
                    id=person_id,
                    bbox=[bbox[0]/frame_width, bbox[1]/frame_height, bbox[2]/frame_width, bbox[3]/frame_height],
                    center=(center_x, center_y),
                    confidence=detection.get("conf", 0),
                    type=PersonType.PERSON,  # Will be updated by guard identification
                    first_seen=current_time,
                    last_seen=current_time,
                    in_gate_area=is_in_area((center_x, center_y), gate_config["gate_area"]),
                    in_guard_anchor=is_in_area((center_x, center_y), gate_config["guard_anchor"]),
                    anchor_entry_time=None,
                    total_anchor_time=0.0,
                    location_history=None,
                    guard_classification_time=None
                )
                
                current_persons[person_id] = person
        
        # Calculate persons to remove BEFORE updating
        persons_to_remove = [pid for pid in persons.keys() if pid not in current_persons]
        
        # Preserve guard identification data from existing persons
        for pid, existing_person in persons.items():
            if pid in current_persons:
                new_person = current_persons[pid]
                # Copy guard identification fields
                new_person.anchor_entry_time = existing_person.anchor_entry_time
                new_person.total_anchor_time = existing_person.total_anchor_time
                new_person.location_history = existing_person.location_history
                new_person.guard_classification_time = existing_person.guard_classification_time
                new_person.type = existing_person.type  # Preserve guard classification
        
        # Count objects before updating persons dict
        # Since person IDs are unstable (new UUID each frame), we track zone occupancy changes
        prev_gate_count = sum(1 for p in persons.values() if p.in_gate_area)
        prev_anchor_count = sum(1 for p in persons.values() if p.in_guard_anchor)
        
        # Track object counting - count zone occupancy changes
        current_gate_count = sum(1 for p in current_persons.values() if p.in_gate_area)
        current_anchor_count = sum(1 for p in current_persons.values() if p.in_guard_anchor)
        
        # Detect gate area transitions based on occupancy changes
        if current_gate_count > prev_gate_count:
            # Objects entered gate area
            entries = current_gate_count - prev_gate_count
            object_counts["gate_entries"] += entries
            object_counts["total_detected"] += entries  # Count new detections
            logger.debug(f"{entries} objects entered gate area")
        elif current_gate_count < prev_gate_count:
            # Objects exited gate area
            exits = prev_gate_count - current_gate_count
            object_counts["gate_exits"] += exits
            object_counts["total_passed_through"] += exits  # Count as passed through
            logger.debug(f"{exits} objects exited gate area (passed through)")
        
        # Detect guard anchor transitions based on occupancy changes
        if current_anchor_count > prev_anchor_count:
            # Objects entered guard anchor
            entries = current_anchor_count - prev_anchor_count
            object_counts["anchor_entries"] += entries
            logger.debug(f"{entries} objects entered guard anchor")
        elif current_anchor_count < prev_anchor_count:
            # Objects exited guard anchor
            exits = prev_anchor_count - current_anchor_count
            object_counts["anchor_exits"] += exits
            logger.debug(f"{exits} objects exited guard anchor")
        
        # Track individual persons for stable counting (preserve existing persons)
        for person_id, person in current_persons.items():
            # Get previous state if person exists (preserved from previous frame)
            prev_state = person_previous_state.get(person_id, {"in_gate": False, "in_anchor": False})
            current_in_gate = person.in_gate_area
            current_in_anchor = person.in_guard_anchor
            
            # Update previous state for tracking
            person_previous_state[person_id] = {
                "in_gate": current_in_gate,
                "in_anchor": current_in_anchor
            }
        
        # Remove previous states for persons that are no longer detected
        for pid in persons_to_remove:
            if pid in person_previous_state:
                del person_previous_state[pid]
        
        # Update existing persons and remove old ones
        persons.update(current_persons)
        for pid in persons_to_remove:
            del persons[pid]
        
        # Update current counts
        object_counts["current_in_gate"] = current_gate_count
        object_counts["current_in_anchor"] = current_anchor_count
        
        # Apply guard identification based on location
        identify_guards_by_location()
        
        # Detect groups
        new_groups = detect_groups(persons, current_time)
        groups.update(new_groups)
        
        # Update existing groups
        update_existing_groups(persons, current_time)
        
        # Create tickets
        create_tickets_for_individuals(persons, current_time)
        create_tickets_for_groups(current_time)
        
        # Update guard status
        update_guard_status(persons, current_time)
        
        # Assign tickets to guards
        assign_tickets_to_guards(current_time)
        
        # Update ticket status
        update_ticket_status(persons, current_time)
        
        # Check escalation conditions
        check_escalation_conditions(current_time)
        
        # Update statistics
        update_statistics()
    
    # Return status for WebSocket
    return {
        "active": len(queue) > 0,
        "message": f"Queue: {len(queue)} tickets, {len([g for g in guards.values() if g.is_active])} active guards",
        "queue_length": len(queue),
        "active_guards": len([g for g in guards.values() if g.is_active]),
        "tickets": [asdict(ticket) for ticket in tickets.values()],
        "groups": [asdict(group) for group in groups.values()],
        "guards": [asdict(guard) for guard in guards.values()],
        "statistics": stats,
        "object_counts": object_counts.copy(),  # Include object counting statistics
        "timestamp": current_time
    }

# Rest of the FastAPI endpoints remain the same...
# (continuing with the existing endpoints)

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    global model, video_cap, frame_width, frame_height
    
    logger.info("Starting Advanced Body Checking System...")
    
    # Load model
    model_path = "../weight.pt"
    if os.path.exists(model_path):
        logger.info(f"Loading model from {model_path}")
        model = YOLO(model_path)
        logger.info("Model loaded successfully")
    else:
        logger.error(f"Model file not found: {model_path}")
        return
    
    # Load video source (configurable via environment variable or default to file)
    default_source = os.getenv("VIDEO_SOURCE", "file:videoplayback.mp4")
    logger.info(f"Loading video source: {default_source}")
    
    if not set_video_source(default_source):
        logger.error(f"Failed to initialize video source: {default_source}")
        return
    
    logger.info("System initialized successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global video_cap
    if video_cap:
        video_cap.release()
    logger.info("System shutdown complete")

@app.get("/health")
async def health_check():
    """Public health check endpoint - minimal info only"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/internal/health")
@limiter.limit("30/minute")
async def internal_health_check(request: Request, user: str = Depends(verify_token)):
    """Detailed health check for authenticated users"""
    return {
        "status": "healthy", 
        "timestamp": time.time(),
        "queue_length": len(queue),
        "active_guards": len([g for g in guards.values() if g.is_active]),
        "system_load": "normal"
    }

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, body: LoginRequest):
    """Authentication endpoint"""
    user = USERS_DB.get(body.username)
    if not user or user["password"] != hashlib.sha256(body.password.encode()).hexdigest():
        audit_logger.warning(f"FAILED_LOGIN: {body.username} from {request.client.host}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": body.username})
    audit_logger.info(f"SUCCESSFUL_LOGIN: {body.username} from {request.client.host}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication with authentication"""
    await websocket.accept()
    
    # Get token from query params
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return
    
    # Verify token
    username = verify_websocket_token(token)
    if not username:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    logger.info(f"WebSocket connection established for user: {username}")
    
    try:
        while True:
            # Read frame from configured source
            with video_source_lock:
                current_source = video_source
                cap = video_cap
            
            if not cap or not cap.isOpened():
                logger.warning("Video capture not available, waiting...")
                await asyncio.sleep(1)
                continue
            
            ret, frame = cap.read()
            if not ret:
                # Check if it's a file (can restart) or webcam (wait)
                if current_source.startswith("file:"):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    # Webcam - wait and retry
                    await asyncio.sleep(0.1)
                    continue
            
            # Run inference
            results = model(frame, verbose=False)
            
            # Process detections
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        detection = {
                            "cls_id": int(box.cls[0]),
                            "conf": float(box.conf[0]),
                            "bbox": box.xyxy[0].tolist()
                        }
                        detections.append(detection)
            
            # Process with advanced system
            gate_config_copy = get_gate_config_copy()
            status = process_detections(detections, gate_config_copy)
            
            # Send status
            await websocket.send_json(status)
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.1)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket closed by client: {username}")
    except Exception as e:
        logger.error(f"Error in WebSocket loop for {username}: {e}")

@app.get("/stream")
@limiter.limit("30/minute")
async def stream_video(request: Request, source: str = None, user: Optional[str] = Depends(lambda: None)):
    """Video streaming endpoint with authentication via Bearer header or token query param"""
    # Allow either Authorization header or token query param for <img> tags
    if not user:
        token = request.query_params.get("token")
        username = verify_websocket_token(token) if token else None
        if not username:
            raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Use provided source or default to configured source
    if not source:
        source = get_video_source()
    
    def generate_frames():
        local_cap = None
        is_webcam = False
        
        try:
            # Parse source parameter
            if source.startswith("webcam:"):
                # Extract camera index: webcam:0, webcam:1, etc.
                cam_index = int(source.split(":")[1]) if ":" in source else 0
                local_cap = cv2.VideoCapture(cam_index)
                is_webcam = True
                logger.debug(f"Stream: Opening webcam {cam_index}")
            elif source.startswith("file:"):
                # Extract file path: file:videoplayback.mp4
                file_path = source.split(":", 1)[1]
                if not os.path.isabs(file_path):
                    file_path = os.path.join("..", file_path)
                local_cap = cv2.VideoCapture(file_path)
                is_webcam = False
                logger.debug(f"Stream: Opening video file: {file_path}")
            else:
                # Default: try as file path
                if os.path.exists(source):
                    local_cap = cv2.VideoCapture(source)
                    is_webcam = False
                else:
                    # Try as camera index
                    try:
                        cam_idx = int(source)
                        local_cap = cv2.VideoCapture(cam_idx)
                        is_webcam = True
                    except ValueError:
                        logger.error(f"Invalid source format: {source}")
                        return
            
            if not local_cap or not local_cap.isOpened():
                logger.error(f"Failed to open source: {source}")
                return
            
            while True:
                ret, frame = local_cap.read()
                if not ret:
                    if is_webcam:
                        # For webcam, wait a bit and try again
                        time.sleep(0.1)
                        continue
                    else:
                        # For video file, restart from beginning
                        local_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                
                # Draw gate overlays
                gate_config_copy = get_gate_config_copy()
                if gate_config_copy.get("enabled", True):
                    frame = draw_gate_overlay(frame, gate_config_copy)
                
                # Encode frame
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        finally:
            # Don't close - keep stream alive
            # local_cap will be released when generator exits
            pass
    
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

def draw_gate_overlay(frame, gate_config):
    """Draw gate area and guard anchor overlays"""
    height, width = frame.shape[:2]
    
    # Gate Area
    gate_area = gate_config.get("gate_area", {})
    x1 = int(gate_area.get("x", 0.3) * width)
    y1 = int(gate_area.get("y", 0.2) * height)
    x2 = int((gate_area.get("x", 0.3) + gate_area.get("width", 0.4)) * width)
    y2 = int((gate_area.get("y", 0.2) + gate_area.get("height", 0.6)) * height)
    
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
    cv2.putText(frame, "GATE AREA", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Guard Anchor
    guard_anchor = gate_config.get("guard_anchor", {})
    x1 = int(guard_anchor.get("x", 0.1) * width)
    y1 = int(guard_anchor.get("y", 0.15) * height)
    x2 = int((guard_anchor.get("x", 0.1) + guard_anchor.get("width", 0.15)) * width)
    y2 = int((guard_anchor.get("y", 0.15) + guard_anchor.get("height", 0.7)) * height)
    
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
    cv2.putText(frame, "GUARD ANCHOR", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    return frame

@app.post("/config/gate")
@limiter.limit("30/minute")
async def update_gate_config_endpoint(request: Request, user: str = Depends(require_role("admin"))):
    """Update gate configuration - admin only"""
    try:
        config = await request.json()
        update_gate_config(config)
        log_admin_action("CONFIG_UPDATE", user, {"config": config})
        return {"status": "updated", "config": get_gate_config_copy()}
    except Exception as e:
        logger.error(f"Error updating gate config: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/config/gate")
async def get_gate_config_endpoint(user: str = Depends(verify_token)):
    """Get current gate configuration"""
    return {"config": get_gate_config_copy()}

@app.post("/config/gate/save")
@limiter.limit("30/minute")
async def save_gate_config(request: Request, user: str = Depends(require_role("admin"))):
    """Save current gate configuration to file - admin only"""
    try:
        config = get_gate_config_copy()
        with open("gate_config_saved.json", "w") as f:
            json.dump(config, f, indent=2)
        log_admin_action("CONFIG_SAVE", user, {"config": config})
        return {"status": "saved", "config": config}
    except Exception as e:
        logger.error(f"Error saving gate config: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/config/gate/load")
@limiter.limit("30/minute")
async def load_gate_config(request: Request, user: str = Depends(require_role("admin"))):
    """Load gate configuration from file - admin only"""
    try:
        if os.path.exists("gate_config_saved.json"):
            with open("gate_config_saved.json", "r") as f:
                config = json.load(f)
            update_gate_config(config)
            log_admin_action("CONFIG_LOAD", user, {"config": config})
            return {"status": "loaded", "config": config}
        else:
            return {"status": "not_found"}
    except Exception as e:
        logger.error(f"Error loading gate config: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/video/source")
@limiter.limit("30/minute")
async def get_video_source_endpoint(request: Request, user: str = Depends(verify_token)):
    """Get current video source"""
    return {"source": get_video_source()}

@app.post("/video/source")
@limiter.limit("10/minute")
async def set_video_source_endpoint(request: Request, user: str = Depends(require_role("admin"))):
    """Change video source - admin only"""
    try:
        data = await request.json()
        new_source = data.get("source")
        if not new_source:
            return {"status": "error", "message": "Source parameter required"}
        
        success = set_video_source(new_source)
        if success:
            log_admin_action("VIDEO_SOURCE_CHANGE", user, {"source": new_source})
            return {"status": "updated", "source": new_source}
        else:
            return {"status": "error", "message": f"Failed to open source: {new_source}"}
    except Exception as e:
        logger.error(f"Error changing video source: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/counts")
@limiter.limit("60/minute")
async def get_object_counts(request: Request, user: str = Depends(verify_token)):
    """Get object counting statistics"""
    with state_lock:
        return {"counts": object_counts.copy()}

@app.post("/counts/reset")
@limiter.limit("10/minute")
async def reset_object_counts(request: Request, user: str = Depends(require_role("admin"))):
    """Reset object counting statistics - admin only"""
    global object_counts, person_previous_state
    with state_lock:
        object_counts = {
            "total_detected": 0,
            "gate_entries": 0,
            "gate_exits": 0,
            "anchor_entries": 0,
            "anchor_exits": 0,
            "current_in_gate": 0,
            "current_in_anchor": 0,
            "total_passed_through": 0
        }
        person_previous_state = {}
        log_admin_action("COUNTS_RESET", user, {})
        return {"status": "reset", "counts": object_counts.copy()}

@app.get("/queue")
async def get_queue_status(user: str = Depends(verify_token)):
    """Get current queue status"""
    with state_lock:
        return {
            "queue": queue,
            "tickets": [asdict(ticket) for ticket in tickets.values()],
            "guards": [asdict(guard) for guard in guards.values()],
            "statistics": stats
        }

@app.post("/ticket/{ticket_id}/cancel")
@limiter.limit("30/minute")
async def cancel_ticket(request: Request, ticket_id: str, user: str = Depends(require_role("admin"))):
    """Cancel a specific ticket - admin only"""
    try:
        data = await request.json()
        reason = data.get("reason", "Manual cancellation")
        
        with state_lock:
            if ticket_id in tickets:
                ticket = tickets[ticket_id]
                ticket.status = TicketStatus.CANCELLED
                ticket.escalated_reason = reason
                ticket.completed_at = time.time()
                
                # Remove from queue
                if ticket_id in queue:
                    queue.remove(ticket_id)
                
                # Release guard if assigned
                if ticket.assigned_guard and ticket.assigned_guard in guards:
                    guards[ticket.assigned_guard].current_ticket = None
                
                log_admin_action("TICKET_CANCEL", user, {"ticket_id": ticket_id, "reason": reason})
                return {"status": "cancelled", "ticket_id": ticket_id}
            else:
                return {"status": "not_found", "ticket_id": ticket_id}
    except Exception as e:
        logger.error(f"Error cancelling ticket: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
