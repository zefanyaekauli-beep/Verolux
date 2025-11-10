"""
Public/Internal Status Page
Shows real-time system health and historical uptime
"""
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

logger = logging.getLogger(__name__)


class ComponentStatus(Enum):
    """Component status levels"""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"
    MAINTENANCE = "maintenance"


@dataclass
class StatusComponent:
    """System component for status page"""
    name: str
    description: str
    status: ComponentStatus
    response_time_ms: Optional[float] = None
    uptime_percent: Optional[float] = None
    last_incident: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "response_time_ms": self.response_time_ms,
            "uptime_percent": self.uptime_percent,
            "last_incident": self.last_incident
        }


@dataclass
class Incident:
    """Status page incident"""
    incident_id: str
    title: str
    description: str
    status: str  # "investigating", "identified", "monitoring", "resolved"
    severity: str  # "critical", "major", "minor"
    started_at: float
    resolved_at: Optional[float] = None
    updates: List[Dict] = field(default_factory=list)
    
    def add_update(self, message: str, status: Optional[str] = None):
        """Add incident update"""
        self.updates.append({
            "timestamp": time.time(),
            "message": message,
            "status": status or self.status
        })
        
        if status:
            self.status = status
    
    def resolve(self):
        """Mark incident as resolved"""
        self.status = "resolved"
        self.resolved_at = time.time()
    
    @property
    def duration_minutes(self) -> float:
        """Incident duration in minutes"""
        end_time = self.resolved_at or time.time()
        return (end_time - self.started_at) / 60
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "severity": self.severity,
            "started_at": self.started_at,
            "resolved_at": self.resolved_at,
            "duration_minutes": round(self.duration_minutes, 2),
            "updates": self.updates
        }


class StatusPage:
    """
    Status page manager
    
    Features:
    - Real-time component status
    - Incident tracking
    - Historical uptime
    - Maintenance schedules
    """
    
    def __init__(self):
        self.components: Dict[str, StatusComponent] = {}
        self.incidents: Dict[str, Incident] = {}
        self._init_components()
    
    def _init_components(self):
        """Initialize system components"""
        components = [
            StatusComponent("api", "Backend API", ComponentStatus.OPERATIONAL),
            StatusComponent("websocket", "WebSocket Streaming", ComponentStatus.OPERATIONAL),
            StatusComponent("cameras", "Camera Connections", ComponentStatus.OPERATIONAL),
            StatusComponent("detection", "AI Detection", ComponentStatus.OPERATIONAL),
            StatusComponent("database", "Database", ComponentStatus.OPERATIONAL),
            StatusComponent("queue", "Message Queue", ComponentStatus.OPERATIONAL),
            StatusComponent("storage", "Object Storage", ComponentStatus.OPERATIONAL)
        ]
        
        for comp in components:
            self.components[comp.name] = comp
    
    def update_component_status(self, 
                               component_name: str,
                               status: ComponentStatus,
                               response_time_ms: Optional[float] = None,
                               uptime_percent: Optional[float] = None):
        """Update component status"""
        if component_name in self.components:
            comp = self.components[component_name]
            comp.status = status
            
            if response_time_ms is not None:
                comp.response_time_ms = response_time_ms
            
            if uptime_percent is not None:
                comp.uptime_percent = uptime_percent
    
    def create_incident(self,
                       title: str,
                       description: str,
                       severity: str = "major") -> Incident:
        """Create new incident"""
        incident_id = f"INC-{int(time.time())}"
        
        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            status="investigating",
            severity=severity,
            started_at=time.time()
        )
        
        self.incidents[incident_id] = incident
        
        logger.info(f"Created incident {incident_id}: {title}")
        
        return incident
    
    def get_overall_status(self) -> ComponentStatus:
        """Get overall system status"""
        statuses = [comp.status for comp in self.components.values()]
        
        if any(s == ComponentStatus.MAJOR_OUTAGE for s in statuses):
            return ComponentStatus.MAJOR_OUTAGE
        elif any(s == ComponentStatus.PARTIAL_OUTAGE for s in statuses):
            return ComponentStatus.PARTIAL_OUTAGE
        elif any(s == ComponentStatus.DEGRADED for s in statuses):
            return ComponentStatus.DEGRADED
        elif any(s == ComponentStatus.MAINTENANCE for s in statuses):
            return ComponentStatus.MAINTENANCE
        else:
            return ComponentStatus.OPERATIONAL
    
    def get_status_summary(self) -> dict:
        """Get status page summary"""
        overall = self.get_overall_status()
        active_incidents = [
            inc for inc in self.incidents.values()
            if inc.status != "resolved"
        ]
        
        return {
            "overall_status": overall.value,
            "components": [comp.to_dict() for comp in self.components.values()],
            "active_incidents": [inc.to_dict() for inc in active_incidents],
            "recent_incidents": [
                inc.to_dict() for inc in sorted(
                    self.incidents.values(),
                    key=lambda x: x.started_at,
                    reverse=True
                )[:10]
            ],
            "timestamp": time.time()
        }


# Global instance
status_page = StatusPage()




















