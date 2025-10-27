#!/usr/bin/env python3
"""
Verolux1st Analytics System
Comprehensive advanced analytics and reporting
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
import uvicorn
import asyncio
import threading
import time

@dataclass
class TrafficFlow:
    """Traffic flow data point"""
    timestamp: datetime
    camera_id: str
    zone_id: str
    direction: str  # 'inbound' or 'outbound'
    object_type: str
    confidence: float

@dataclass
class BehaviorEvent:
    """Behavior analysis event"""
    timestamp: datetime
    camera_id: str
    zone_id: str
    event_type: str  # 'loitering', 'intrusion', 'ppe_violation', 'hazard'
    duration: float
    severity: str
    object_count: int

class VeroluxAnalyticsSystem:
    """Comprehensive analytics system for Verolux Enterprise"""
    
    def __init__(self, db_path: str = "verolux_analytics.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize comprehensive analytics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Traffic flow analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traffic_flow (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                camera_id TEXT,
                zone_id TEXT,
                direction TEXT,
                object_type TEXT,
                confidence REAL,
                flow_path TEXT
            )
        ''')
        
        # Behavior analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavior_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                camera_id TEXT,
                zone_id TEXT,
                event_type TEXT,
                duration REAL,
                severity TEXT,
                object_count INTEGER,
                details TEXT
            )
        ''')
        
        # Zone utilization
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zone_utilization (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                zone_id TEXT,
                occupancy_count INTEGER,
                utilization_percent REAL,
                peak_hour BOOLEAN
            )
        ''')
        
        # PPE compliance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ppe_compliance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                camera_id TEXT,
                zone_id TEXT,
                ppe_type TEXT,
                compliant BOOLEAN,
                confidence REAL
            )
        ''')
        
        # Anomaly detection
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                camera_id TEXT,
                anomaly_type TEXT,
                severity TEXT,
                baseline_deviation REAL,
                details TEXT
            )
        ''')
        
        # System health
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                camera_id TEXT,
                uptime_percent REAL,
                stream_errors INTEGER,
                last_event DATETIME
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def log_traffic_flow(self, flow: TrafficFlow):
        """Log traffic flow data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO traffic_flow 
            (timestamp, camera_id, zone_id, direction, object_type, confidence, flow_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            flow.timestamp, flow.camera_id, flow.zone_id, 
            flow.direction, flow.object_type, flow.confidence, ""
        ))
        
        conn.commit()
        conn.close()
        
    def log_behavior_event(self, event: BehaviorEvent):
        """Log behavior analysis event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO behavior_events 
            (timestamp, camera_id, zone_id, event_type, duration, severity, object_count, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.timestamp, event.camera_id, event.zone_id,
            event.event_type, event.duration, event.severity,
            event.object_count, ""
        ))
        
        conn.commit()
        conn.close()
        
    def get_traffic_flow_analytics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get comprehensive traffic flow analytics"""
        conn = sqlite3.connect(self.db_path)
        
        # Directional counts
        query = '''
            SELECT direction, object_type, COUNT(*) as count
            FROM traffic_flow 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY direction, object_type
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_time, end_time])
        
        # Flow patterns by hour
        hourly_query = '''
            SELECT 
                strftime('%H', timestamp) as hour,
                direction,
                COUNT(*) as count
            FROM traffic_flow 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY hour, direction
            ORDER BY hour
        '''
        
        hourly_df = pd.read_sql_query(hourly_query, conn, params=[start_time, end_time])
        
        conn.close()
        
        return {
            "directional_counts": df.to_dict('records') if not df.empty else [],
            "hourly_patterns": hourly_df.to_dict('records') if not hourly_df.empty else [],
            "total_flow": int(df['count'].sum()) if not df.empty else 0
        }
        
    def get_zone_utilization_analytics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get zone utilization analytics"""
        conn = sqlite3.connect(self.db_path)
        
        # Zone occupancy over time
        query = '''
            SELECT 
                zone_id,
                AVG(occupancy_count) as avg_occupancy,
                MAX(occupancy_count) as peak_occupancy,
                AVG(utilization_percent) as avg_utilization
            FROM zone_utilization 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY zone_id
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_time, end_time])
        
        # Peak hours analysis
        peak_query = '''
            SELECT 
                strftime('%H', timestamp) as hour,
                AVG(utilization_percent) as avg_utilization
            FROM zone_utilization 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY hour
            ORDER BY avg_utilization DESC
        '''
        
        peak_df = pd.read_sql_query(peak_query, conn, params=[start_time, end_time])
        
        conn.close()
        
        return {
            "zone_metrics": df.to_dict('records') if not df.empty else [],
            "peak_hours": peak_df.to_dict('records') if not peak_df.empty else [],
            "total_zones": len(df) if not df.empty else 0
        }
        
    def get_behavior_analytics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get behavior and safety analytics"""
        conn = sqlite3.connect(self.db_path)
        
        # Loitering analysis
        loitering_query = '''
            SELECT 
                zone_id,
                AVG(duration) as avg_duration,
                COUNT(*) as loitering_count,
                MAX(duration) as max_duration
            FROM behavior_events 
            WHERE timestamp BETWEEN ? AND ? AND event_type = 'loitering'
            GROUP BY zone_id
        '''
        
        loitering_df = pd.read_sql_query(loitering_query, conn, params=[start_time, end_time])
        
        # Intrusion trends
        intrusion_query = '''
            SELECT 
                zone_id,
                COUNT(*) as intrusion_count,
                AVG(duration) as avg_duration
            FROM behavior_events 
            WHERE timestamp BETWEEN ? AND ? AND event_type = 'intrusion'
            GROUP BY zone_id
        '''
        
        intrusion_df = pd.read_sql_query(intrusion_query, conn, params=[start_time, end_time])
        
        # Hazard incidents
        hazard_query = '''
            SELECT 
                zone_id,
                COUNT(*) as hazard_count,
                severity
            FROM behavior_events 
            WHERE timestamp BETWEEN ? AND ? AND event_type = 'hazard'
            GROUP BY zone_id, severity
        '''
        
        hazard_df = pd.read_sql_query(hazard_query, conn, params=[start_time, end_time])
        
        conn.close()
        
        return {
            "loitering_analysis": loitering_df.to_dict('records') if not loitering_df.empty else [],
            "intrusion_trends": intrusion_df.to_dict('records') if not intrusion_df.empty else [],
            "hazard_incidents": hazard_df.to_dict('records') if not hazard_df.empty else []
        }
        
    def get_ppe_compliance_analytics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get PPE compliance analytics"""
        conn = sqlite3.connect(self.db_path)
        
        # Compliance by type
        query = '''
            SELECT 
                ppe_type,
                AVG(CASE WHEN compliant THEN 1.0 ELSE 0.0 END) as compliance_rate,
                COUNT(*) as total_checks,
                SUM(CASE WHEN compliant THEN 1 ELSE 0 END) as compliant_count
            FROM ppe_compliance 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY ppe_type
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_time, end_time])
        
        # Compliance trends over time
        trend_query = '''
            SELECT 
                strftime('%H', timestamp) as hour,
                ppe_type,
                AVG(CASE WHEN compliant THEN 1.0 ELSE 0.0 END) as compliance_rate
            FROM ppe_compliance 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY hour, ppe_type
            ORDER BY hour
        '''
        
        trend_df = pd.read_sql_query(trend_query, conn, params=[start_time, end_time])
        
        conn.close()
        
        return {
            "compliance_by_type": df.to_dict('records') if not df.empty else [],
            "compliance_trends": trend_df.to_dict('records') if not trend_df.empty else [],
            "overall_compliance": float(df['compliance_rate'].mean()) if not df.empty else 0.0
        }
        
    def get_anomaly_analytics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get anomaly detection analytics"""
        conn = sqlite3.connect(self.db_path)
        
        # Anomaly types and severity
        query = '''
            SELECT 
                anomaly_type,
                severity,
                COUNT(*) as count,
                AVG(baseline_deviation) as avg_deviation
            FROM anomalies 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY anomaly_type, severity
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_time, end_time])
        
        # Anomaly timeline
        timeline_query = '''
            SELECT 
                timestamp,
                anomaly_type,
                severity,
                baseline_deviation
            FROM anomalies 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
            LIMIT 100
        '''
        
        timeline_df = pd.read_sql_query(timeline_query, conn, params=[start_time, end_time])
        
        conn.close()
        
        return {
            "anomaly_summary": df.to_dict('records') if not df.empty else [],
            "anomaly_timeline": timeline_df.to_dict('records') if not timeline_df.empty else [],
            "total_anomalies": int(df['count'].sum()) if not df.empty else 0
        }
        
    def get_system_health_analytics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get system health analytics"""
        conn = sqlite3.connect(self.db_path)
        
        # Camera health metrics
        query = '''
            SELECT 
                camera_id,
                AVG(uptime_percent) as avg_uptime,
                SUM(stream_errors) as total_errors,
                MAX(last_event) as last_activity
            FROM system_health 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY camera_id
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_time, end_time])
        
        # System performance over time
        performance_query = '''
            SELECT 
                strftime('%H', timestamp) as hour,
                AVG(uptime_percent) as avg_uptime,
                SUM(stream_errors) as total_errors
            FROM system_health 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY hour
            ORDER BY hour
        '''
        
        performance_df = pd.read_sql_query(performance_query, conn, params=[start_time, end_time])
        
        conn.close()
        
        return {
            "camera_health": df.to_dict('records') if not df.empty else [],
            "performance_trends": performance_df.to_dict('records') if not performance_df.empty else [],
            "overall_uptime": float(df['avg_uptime'].mean()) if not df.empty else 0.0
        }
        
    def generate_heatmap_data(self, start_time: datetime, end_time: datetime, 
                             heatmap_type: str = "movement") -> List[Dict]:
        """Generate heatmap data for visualization"""
        conn = sqlite3.connect(self.db_path)
        
        if heatmap_type == "movement":
            query = '''
                SELECT 
                    zone_id,
                    strftime('%H', timestamp) as hour,
                    COUNT(*) as activity_level
                FROM traffic_flow 
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY zone_id, hour
            '''
        elif heatmap_type == "anomalies":
            query = '''
                SELECT 
                    camera_id,
                    strftime('%H', timestamp) as hour,
                    COUNT(*) as anomaly_count
                FROM anomalies 
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY camera_id, hour
            '''
        else:  # utilization
            query = '''
                SELECT 
                    zone_id,
                    strftime('%H', timestamp) as hour,
                    AVG(utilization_percent) as utilization
                FROM zone_utilization 
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY zone_id, hour
            '''
        
        df = pd.read_sql_query(query, conn, params=[start_time, end_time])
        conn.close()
        
        return df.to_dict('records') if not df.empty else []
        
    def get_operational_efficiency(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get operational efficiency analytics"""
        conn = sqlite3.connect(self.db_path)
        
        # Loading dock usage
        dock_query = '''
            SELECT 
                zone_id,
                COUNT(*) as usage_count,
                AVG(occupancy_count) as avg_occupancy
            FROM zone_utilization 
            WHERE timestamp BETWEEN ? AND ? AND zone_id LIKE '%dock%'
            GROUP BY zone_id
        '''
        
        dock_df = pd.read_sql_query(dock_query, conn, params=[start_time, end_time])
        
        # Idle time analysis
        idle_query = '''
            SELECT 
                zone_id,
                COUNT(CASE WHEN utilization_percent < 10 THEN 1 END) as idle_periods,
                AVG(utilization_percent) as avg_utilization
            FROM zone_utilization 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY zone_id
        '''
        
        idle_df = pd.read_sql_query(idle_query, conn, params=[start_time, end_time])
        
        # Shift comparisons
        shift_query = '''
            SELECT 
                CASE 
                    WHEN strftime('%H', timestamp) BETWEEN '06' AND '14' THEN 'morning'
                    WHEN strftime('%H', timestamp) BETWEEN '14' AND '22' THEN 'afternoon'
                    ELSE 'night'
                END as shift,
                AVG(utilization_percent) as avg_utilization,
                COUNT(*) as activity_count
            FROM zone_utilization 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY shift
        '''
        
        shift_df = pd.read_sql_query(shift_query, conn, params=[start_time, end_time])
        
        conn.close()
        
        return {
            "dock_usage": dock_df.to_dict('records') if not dock_df.empty else [],
            "idle_analysis": idle_df.to_dict('records') if not idle_df.empty else [],
            "shift_comparisons": shift_df.to_dict('records') if not shift_df.empty else []
        }

# FastAPI endpoints for analytics
app = FastAPI(title="Verolux Enterprise Analytics API")

# Initialize analytics system
analytics_system = VeroluxAnalyticsSystem()

@app.get("/analytics/traffic-flow")
async def get_traffic_flow_analytics(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)")
):
    """Get traffic flow analytics"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    return analytics_system.get_traffic_flow_analytics(start_dt, end_dt)

@app.get("/analytics/zone-utilization")
async def get_zone_utilization_analytics(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)")
):
    """Get zone utilization analytics"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    return analytics_system.get_zone_utilization_analytics(start_dt, end_dt)

@app.get("/analytics/behavior")
async def get_behavior_analytics(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)")
):
    """Get behavior and safety analytics"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    return analytics_system.get_behavior_analytics(start_dt, end_dt)

@app.get("/analytics/ppe-compliance")
async def get_ppe_compliance_analytics(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)")
):
    """Get PPE compliance analytics"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    return analytics_system.get_ppe_compliance_analytics(start_dt, end_dt)

@app.get("/analytics/anomalies")
async def get_anomaly_analytics(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)")
):
    """Get anomaly detection analytics"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    return analytics_system.get_anomaly_analytics(start_dt, end_dt)

@app.get("/analytics/system-health")
async def get_system_health_analytics(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)")
):
    """Get system health analytics"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    return analytics_system.get_system_health_analytics(start_dt, end_dt)

@app.get("/analytics/heatmap")
async def get_heatmap_data(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)"),
    heatmap_type: str = Query("movement", description="Type: movement, anomalies, utilization")
):
    """Get heatmap data for visualization"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    return analytics_system.generate_heatmap_data(start_dt, end_dt, heatmap_type)

@app.get("/analytics/operational-efficiency")
async def get_operational_efficiency(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)")
):
    """Get operational efficiency analytics"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    return analytics_system.get_operational_efficiency(start_dt, end_dt)

if __name__ == "__main__":
    print("🚀 Starting Verolux Enterprise Analytics System")
    print("=" * 60)
    print("📊 Comprehensive Advanced Analytics")
    print("🎯 Traffic Flow, Behavior, PPE, Anomaly Detection")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
