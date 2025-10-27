#!/usr/bin/env python3
"""
Database Schema for Gate Security System
Stores events, sessions, and audit trails
"""

import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import os


class GateSecurityDatabase:
    """Database for gate security events and audit trails"""
    
    def __init__(self, db_path: str = "gate_security.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                track_id INTEGER NOT NULL,
                related_track_id INTEGER,
                zone_id TEXT,
                position_x REAL,
                position_y REAL,
                confidence REAL,
                metadata TEXT,
                session_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_track_id (track_id),
                INDEX idx_timestamp (timestamp),
                INDEX idx_event_type (event_type),
                INDEX idx_session_id (session_id)
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                visitor_track_id INTEGER NOT NULL,
                guard_track_id INTEGER,
                gate_id TEXT,
                started_at REAL NOT NULL,
                ended_at REAL,
                duration REAL,
                visitor_dwell_time REAL,
                guard_dwell_time REAL,
                interaction_time REAL,
                final_state TEXT,
                completed BOOLEAN,
                score REAL,
                completion_criteria TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_session_id (session_id),
                INDEX idx_visitor_track_id (visitor_track_id),
                INDEX idx_started_at (started_at),
                INDEX idx_completed (completed)
            )
        ''')
        
        # Contact events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                visitor_track_id INTEGER NOT NULL,
                guard_track_id INTEGER NOT NULL,
                started_at REAL NOT NULL,
                ended_at REAL,
                duration REAL,
                min_center_distance REAL,
                max_iou REAL,
                avg_center_distance REAL,
                avg_iou REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_session_id (session_id),
                INDEX idx_visitor_track_id (visitor_track_id)
            )
        ''')
        
        # Pose events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pose_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                visitor_track_id INTEGER NOT NULL,
                guard_track_id INTEGER NOT NULL,
                timestamp REAL NOT NULL,
                event_type TEXT,
                hand_to_torso_detected BOOLEAN,
                reach_gesture_detected BOOLEAN,
                confidence REAL,
                min_distance REAL,
                velocity REAL,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_session_id (session_id),
                INDEX idx_timestamp (timestamp)
            )
        ''')
        
        # Snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                snapshot_type TEXT,
                timestamp REAL NOT NULL,
                file_path TEXT,
                width INTEGER,
                height INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_session_id (session_id),
                INDEX idx_snapshot_type (snapshot_type)
            )
        ''')
        
        # Check completions table (successful checks)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS check_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                visitor_track_id INTEGER NOT NULL,
                guard_track_id INTEGER NOT NULL,
                gate_id TEXT,
                completed_at REAL NOT NULL,
                window_start REAL NOT NULL,
                window_end REAL NOT NULL,
                visitor_dwell REAL,
                guard_dwell REAL,
                interaction_duration REAL,
                min_center_distance REAL,
                max_iou REAL,
                pose_reach_count INTEGER,
                score REAL NOT NULL,
                threshold REAL NOT NULL,
                criteria_met TEXT,
                snapshot_pre TEXT,
                snapshot_contact TEXT,
                snapshot_post TEXT,
                event_timeline TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_visitor_track_id (visitor_track_id),
                INDEX idx_completed_at (completed_at),
                INDEX idx_gate_id (gate_id)
            )
        ''')
        
        # Anomalies/violations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                visitor_track_id INTEGER NOT NULL,
                timestamp REAL NOT NULL,
                anomaly_type TEXT NOT NULL,
                severity TEXT,
                description TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_visitor_track_id (visitor_track_id),
                INDEX idx_timestamp (timestamp),
                INDEX idx_anomaly_type (anomaly_type)
            )
        ''')
        
        # System performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                gate_id TEXT,
                fps REAL,
                detection_count INTEGER,
                track_count INTEGER,
                active_sessions INTEGER,
                processing_time_ms REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_timestamp (timestamp),
                INDEX idx_gate_id (gate_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"✅ Gate security database initialized: {self.db_path}")
    
    def log_event(self, event: Dict[str, Any], session_id: Optional[str] = None):
        """Log an event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        position = event.get('position')
        pos_x = position[0] if position else None
        pos_y = position[1] if position else None
        
        cursor.execute('''
            INSERT INTO events 
            (event_type, timestamp, track_id, related_track_id, zone_id, 
             position_x, position_y, confidence, metadata, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.get('event_type'),
            event.get('timestamp'),
            event.get('track_id'),
            event.get('related_track_id'),
            event.get('zone_id'),
            pos_x, pos_y,
            event.get('confidence', 1.0),
            json.dumps(event.get('metadata', {})),
            session_id
        ))
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_data: Dict[str, Any]) -> int:
        """Create a new session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions 
            (session_id, visitor_track_id, guard_track_id, gate_id, started_at,
             ended_at, duration, visitor_dwell_time, guard_dwell_time, 
             interaction_time, final_state, completed, score, completion_criteria)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_data.get('session_id'),
            session_data.get('visitor_track_id'),
            session_data.get('guard_track_id'),
            session_data.get('gate_id'),
            session_data.get('started_at'),
            session_data.get('ended_at'),
            session_data.get('duration'),
            session_data.get('visitor_dwell_time'),
            session_data.get('guard_dwell_time'),
            session_data.get('interaction_time'),
            session_data.get('final_state'),
            session_data.get('completed', False),
            session_data.get('score'),
            json.dumps(session_data.get('completion_criteria', {}))
        ))
        
        session_db_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_db_id
    
    def update_session(self, session_id: str, updates: Dict[str, Any]):
        """Update an existing session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build dynamic UPDATE query
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key == 'completion_criteria':
                value = json.dumps(value)
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        values.append(session_id)
        
        query = f"UPDATE sessions SET {', '.join(set_clauses)} WHERE session_id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
    
    def log_contact_event(self, contact_data: Dict[str, Any], session_id: Optional[str] = None):
        """Log a contact event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contact_events 
            (session_id, visitor_track_id, guard_track_id, started_at, ended_at,
             duration, min_center_distance, max_iou, avg_center_distance, avg_iou)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            contact_data.get('visitor_track_id'),
            contact_data.get('guard_track_id'),
            contact_data.get('started_at'),
            contact_data.get('ended_at'),
            contact_data.get('duration'),
            contact_data.get('min_center_distance'),
            contact_data.get('max_iou'),
            contact_data.get('avg_center_distance'),
            contact_data.get('avg_iou')
        ))
        
        conn.commit()
        conn.close()
    
    def log_pose_event(self, pose_data: Dict[str, Any], session_id: Optional[str] = None):
        """Log a pose event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pose_events 
            (session_id, visitor_track_id, guard_track_id, timestamp, event_type,
             hand_to_torso_detected, reach_gesture_detected, confidence, 
             min_distance, velocity, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            pose_data.get('visitor_track_id'),
            pose_data.get('guard_track_id'),
            pose_data.get('timestamp'),
            pose_data.get('event_type'),
            pose_data.get('hand_to_torso_detected', False),
            pose_data.get('reach_gesture_detected', False),
            pose_data.get('confidence'),
            pose_data.get('min_distance'),
            pose_data.get('velocity'),
            json.dumps(pose_data.get('metadata', {}))
        ))
        
        conn.commit()
        conn.close()
    
    def log_check_completion(self, completion_data: Dict[str, Any]):
        """Log a successful check completion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO check_completions 
            (session_id, visitor_track_id, guard_track_id, gate_id, completed_at,
             window_start, window_end, visitor_dwell, guard_dwell, interaction_duration,
             min_center_distance, max_iou, pose_reach_count, score, threshold,
             criteria_met, snapshot_pre, snapshot_contact, snapshot_post, event_timeline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            completion_data.get('session_id'),
            completion_data.get('visitor_track_id'),
            completion_data.get('guard_track_id'),
            completion_data.get('gate_id'),
            completion_data.get('completed_at'),
            completion_data.get('window_start'),
            completion_data.get('window_end'),
            completion_data.get('visitor_dwell'),
            completion_data.get('guard_dwell'),
            completion_data.get('interaction_duration'),
            completion_data.get('min_center_distance'),
            completion_data.get('max_iou'),
            completion_data.get('pose_reach_count'),
            completion_data.get('score'),
            completion_data.get('threshold'),
            json.dumps(completion_data.get('criteria_met', {})),
            completion_data.get('snapshot_pre'),
            completion_data.get('snapshot_contact'),
            completion_data.get('snapshot_post'),
            json.dumps(completion_data.get('event_timeline', []))
        ))
        
        conn.commit()
        conn.close()
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row is None:
            return None
        
        return dict(row)
    
    def get_events_for_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all events for a session"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM events 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
        ''', (session_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_check_completions(self, start_time: Optional[float] = None,
                             end_time: Optional[float] = None,
                             gate_id: Optional[str] = None,
                             limit: int = 100) -> List[Dict[str, Any]]:
        """Get check completions with optional filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM check_completions WHERE 1=1'
        params = []
        
        if start_time is not None:
            query += ' AND completed_at >= ?'
            params.append(start_time)
        
        if end_time is not None:
            query += ' AND completed_at <= ?'
            params.append(end_time)
        
        if gate_id is not None:
            query += ' AND gate_id = ?'
            params.append(gate_id)
        
        query += ' ORDER BY completed_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_performance_stats(self, start_time: float, end_time: float) -> Dict[str, Any]:
        """Get performance statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total checks completed
        cursor.execute('''
            SELECT COUNT(*) FROM check_completions 
            WHERE completed_at BETWEEN ? AND ?
        ''', (start_time, end_time))
        total_checks = cursor.fetchone()[0]
        
        # Average score
        cursor.execute('''
            SELECT AVG(score) FROM check_completions 
            WHERE completed_at BETWEEN ? AND ?
        ''', (start_time, end_time))
        avg_score = cursor.fetchone()[0] or 0.0
        
        # Total events
        cursor.execute('''
            SELECT COUNT(*) FROM events 
            WHERE timestamp BETWEEN ? AND ?
        ''', (start_time, end_time))
        total_events = cursor.fetchone()[0]
        
        # Average processing time
        cursor.execute('''
            SELECT AVG(processing_time_ms) FROM performance_metrics 
            WHERE timestamp BETWEEN ? AND ?
        ''', (start_time, end_time))
        avg_processing_time = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            'total_checks': total_checks,
            'avg_score': round(avg_score, 3),
            'total_events': total_events,
            'avg_processing_time_ms': round(avg_processing_time, 2),
            'time_window': {
                'start': start_time,
                'end': end_time
            }
        }

