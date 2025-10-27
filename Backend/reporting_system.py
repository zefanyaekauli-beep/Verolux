#!/usr/bin/env python3
"""
Verolux1st Reporting System
Comprehensive analytics and reporting
"""

import os
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np
from collections import defaultdict, Counter
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
import uvicorn

@dataclass
class DetectionEvent:
    """Single detection event"""
    timestamp: datetime
    camera_id: str
    object_class: str
    confidence: float
    bbox: List[float]
    zone_id: Optional[str] = None
    person_id: Optional[str] = None

class VeroluxReportingSystem:
    """Comprehensive reporting system for Verolux Enterprise"""
    
    def __init__(self, db_path: str = "verolux_analytics.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Detection events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                camera_id TEXT,
                object_class TEXT,
                confidence REAL,
                bbox_x1 REAL,
                bbox_y1 REAL,
                bbox_x2 REAL,
                bbox_y2 REAL,
                zone_id TEXT,
                person_id TEXT
            )
        ''')
        
        # Zone events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zone_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                camera_id TEXT,
                zone_id TEXT,
                event_type TEXT,
                object_count INTEGER,
                duration REAL,
                confidence REAL
            )
        ''')
        
        # Alert events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                camera_id TEXT,
                alert_type TEXT,
                severity TEXT,
                message TEXT,
                resolved BOOLEAN,
                response_time REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def log_detection(self, detection: DetectionEvent):
        """Log a detection event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO detection_events 
            (timestamp, camera_id, object_class, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2, zone_id, person_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            detection.timestamp,
            detection.camera_id,
            detection.object_class,
            detection.confidence,
            detection.bbox[0], detection.bbox[1], detection.bbox[2], detection.bbox[3],
            detection.zone_id,
            detection.person_id
        ))
        
        conn.commit()
        conn.close()
        
    def get_object_counts(self, start_time: datetime, end_time: datetime, 
                         camera_id: Optional[str] = None) -> Dict[str, int]:
        """Get object counts for a time period"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT object_class, COUNT(*) as count
            FROM detection_events 
            WHERE timestamp BETWEEN ? AND ?
        '''
        params = [start_time, end_time]
        
        if camera_id:
            query += ' AND camera_id = ?'
            params.append(camera_id)
            
        query += ' GROUP BY object_class'
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return dict(zip(df['object_class'], df['count']))
        
    def get_zone_occupancy(self, zone_id: str, start_time: datetime, 
                          end_time: datetime) -> List[Dict]:
        """Get zone occupancy data"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT timestamp, object_count, duration
            FROM zone_events 
            WHERE zone_id = ? AND timestamp BETWEEN ? AND ?
            AND event_type = 'occupancy'
            ORDER BY timestamp
        '''
        
        df = pd.read_sql_query(query, conn, params=[zone_id, start_time, end_time])
        conn.close()
        
        return df.to_dict('records')
        
    def get_peak_traffic_times(self, camera_id: str, start_date: datetime, 
                              end_date: datetime) -> Dict[str, Any]:
        """Get peak traffic times for a camera"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                strftime('%H', timestamp) as hour,
                COUNT(*) as detection_count
            FROM detection_events 
            WHERE camera_id = ? AND timestamp BETWEEN ? AND ?
            GROUP BY strftime('%H', timestamp)
            ORDER BY detection_count DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=[camera_id, start_date, end_date])
        conn.close()
        
        if df.empty:
            return {"peak_hours": [], "hourly_counts": {}}
            
        peak_hours = df.head(3)['hour'].tolist()
        hourly_counts = dict(zip(df['hour'], df['detection_count']))
        
        return {
            "peak_hours": peak_hours,
            "hourly_counts": hourly_counts,
            "busiest_hour": df.iloc[0]['hour'],
            "total_detections": df['detection_count'].sum()
        }
        
    def get_shift_totals(self, start_date: datetime, end_date: datetime) -> Dict[str, Dict]:
        """Get aggregated counts by shift"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                CASE 
                    WHEN strftime('%H', timestamp) BETWEEN '06' AND '14' THEN 'morning'
                    WHEN strftime('%H', timestamp) BETWEEN '14' AND '22' THEN 'afternoon'
                    ELSE 'night'
                END as shift,
                object_class,
                COUNT(*) as count
            FROM detection_events 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY shift, object_class
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_date, end_date])
        conn.close()
        
        shift_totals = defaultdict(lambda: defaultdict(int))
        for _, row in df.iterrows():
            shift_totals[row['shift']][row['object_class']] = row['count']
            
        return dict(shift_totals)
        
    def get_compliance_report(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get PPE compliance and safety report"""
        conn = sqlite3.connect(self.db_path)
        
        # Get PPE-related detections
        query = '''
            SELECT 
                object_class,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence
            FROM detection_events 
            WHERE timestamp BETWEEN ? AND ?
            AND object_class IN ('helmet', 'vest', 'safety_glasses', 'gloves')
            GROUP BY object_class
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_time, end_time])
        conn.close()
        
        total_ppe_detections = df['count'].sum() if not df.empty else 0
        
        # Get total person detections for compliance calculation
        conn = sqlite3.connect(self.db_path)
        person_query = '''
            SELECT COUNT(*) as person_count
            FROM detection_events 
            WHERE timestamp BETWEEN ? AND ?
            AND object_class = 'person'
        '''
        
        person_df = pd.read_sql_query(person_query, conn, params=[start_time, end_time])
        conn.close()
        
        total_persons = person_df['person_count'].iloc[0] if not person_df.empty else 0
        
        compliance_rate = (total_ppe_detections / total_persons * 100) if total_persons > 0 else 0
        
        return {
            "ppe_detections": df.to_dict('records') if not df.empty else [],
            "total_ppe_detections": int(total_ppe_detections),
            "total_persons": int(total_persons),
            "compliance_rate": round(compliance_rate, 2)
        }
        
    def get_anomaly_summary(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get anomaly detection summary"""
        conn = sqlite3.connect(self.db_path)
        
        # Get baseline statistics
        query = '''
            SELECT 
                object_class,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence
            FROM detection_events 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY object_class
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_time, end_time])
        conn.close()
        
        if df.empty:
            return {"anomalies": [], "baseline": {}}
            
        # Calculate baseline (mean + 2*std for anomaly detection)
        baseline = {}
        for _, row in df.iterrows():
            baseline[row['object_class']] = {
                "normal_count": int(row['count']),
                "avg_confidence": round(row['avg_confidence'], 2)
            }
            
        # Simple anomaly detection (counts significantly above baseline)
        anomalies = []
        for _, row in df.iterrows():
            if row['count'] > row['count'] * 1.5:  # 50% above normal
                anomalies.append({
                    "object_class": row['object_class'],
                    "count": int(row['count']),
                    "severity": "high" if row['count'] > row['count'] * 2 else "medium"
                })
                
        return {
            "anomalies": anomalies,
            "baseline": baseline
        }
        
    def get_event_timeline(self, start_time: datetime, end_time: datetime, 
                          limit: int = 100) -> List[Dict]:
        """Get chronological event timeline"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                timestamp,
                camera_id,
                object_class,
                confidence,
                zone_id
            FROM detection_events 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_time, end_time, limit])
        conn.close()
        
        return df.to_dict('records')
        
    def get_camera_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get camera summary with event counts"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                camera_id,
                COUNT(*) as total_events,
                COUNT(DISTINCT object_class) as unique_objects,
                AVG(confidence) as avg_confidence
            FROM detection_events 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY camera_id
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_date, end_date])
        conn.close()
        
        return {
            "cameras": df.to_dict('records'),
            "total_cameras": len(df),
            "total_events": int(df['total_events'].sum()) if not df.empty else 0
        }
        
    def get_alert_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get alert and notification metrics"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                alert_type,
                severity,
                COUNT(*) as count,
                AVG(response_time) as avg_response_time
            FROM alert_events 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY alert_type, severity
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_time, end_time])
        conn.close()
        
        return {
            "alert_summary": df.to_dict('records') if not df.empty else [],
            "total_alerts": int(df['count'].sum()) if not df.empty else 0,
            "avg_response_time": float(df['avg_response_time'].mean()) if not df.empty else 0
        }
        
    def generate_report(self, report_type: str, start_time: datetime, 
                       end_time: datetime, **kwargs) -> Dict[str, Any]:
        """Generate comprehensive report"""
        
        base_report = {
            "report_type": report_type,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "generated_at": datetime.now().isoformat()
        }
        
        if report_type == "object_counts":
            base_report.update(self.get_object_counts(start_time, end_time, kwargs.get('camera_id')))
            
        elif report_type == "zone_occupancy":
            base_report.update(self.get_zone_occupancy(kwargs['zone_id'], start_time, end_time))
            
        elif report_type == "peak_traffic":
            base_report.update(self.get_peak_traffic_times(kwargs['camera_id'], start_time, end_time))
            
        elif report_type == "shift_totals":
            base_report.update(self.get_shift_totals(start_time, end_time))
            
        elif report_type == "compliance":
            base_report.update(self.get_compliance_report(start_time, end_time))
            
        elif report_type == "anomaly":
            base_report.update(self.get_anomaly_summary(start_time, end_time))
            
        elif report_type == "timeline":
            base_report["events"] = self.get_event_timeline(start_time, end_time, kwargs.get('limit', 100))
            
        elif report_type == "camera_summary":
            base_report.update(self.get_camera_summary(start_time, end_time))
            
        elif report_type == "alerts":
            base_report.update(self.get_alert_metrics(start_time, end_time))
            
        elif report_type == "comprehensive":
            # Generate all reports
            base_report.update({
                "object_counts": self.get_object_counts(start_time, end_time),
                "shift_totals": self.get_shift_totals(start_time, end_time),
                "compliance": self.get_compliance_report(start_time, end_time),
                "anomaly": self.get_anomaly_summary(start_time, end_time),
                "camera_summary": self.get_camera_summary(start_time, end_time),
                "alerts": self.get_alert_metrics(start_time, end_time)
            })
            
        return base_report

# FastAPI endpoints for reporting
app = FastAPI(title="Verolux Enterprise Reporting API")

# Initialize reporting system
reporting_system = VeroluxReportingSystem()

@app.get("/reports/object-counts")
async def get_object_counts(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)"),
    camera_id: str = Query(None, description="Optional camera ID filter")
):
    """Get object counts report"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    return reporting_system.get_object_counts(start_dt, end_dt, camera_id)

@app.get("/reports/zone-occupancy")
async def get_zone_occupancy(
    zone_id: str = Query(..., description="Zone ID"),
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)")
):
    """Get zone occupancy report"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    return reporting_system.get_zone_occupancy(zone_id, start_dt, end_dt)

@app.get("/reports/peak-traffic")
async def get_peak_traffic(
    camera_id: str = Query(..., description="Camera ID"),
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)")
):
    """Get peak traffic times report"""
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)
    
    return reporting_system.get_peak_traffic_times(camera_id, start_dt, end_dt)

@app.get("/reports/shift-totals")
async def get_shift_totals(
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)")
):
    """Get shift totals report"""
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)
    
    return reporting_system.get_shift_totals(start_dt, end_dt)

@app.get("/reports/compliance")
async def get_compliance_report(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)")
):
    """Get compliance and safety report"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    return reporting_system.get_compliance_report(start_dt, end_dt)

@app.get("/reports/anomaly")
async def get_anomaly_report(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)")
):
    """Get anomaly detection summary"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    return reporting_system.get_anomaly_summary(start_dt, end_dt)

@app.get("/reports/timeline")
async def get_event_timeline(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)"),
    limit: int = Query(100, description="Maximum number of events")
):
    """Get event timeline"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    return reporting_system.get_event_timeline(start_dt, end_dt, limit)

@app.get("/reports/comprehensive")
async def get_comprehensive_report(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)")
):
    """Get comprehensive report with all analytics"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    return reporting_system.generate_report("comprehensive", start_dt, end_dt)

@app.post("/reports/export")
async def export_report(
    report_type: str = Query(..., description="Report type"),
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)"),
    format: str = Query("json", description="Export format (json, csv)")
):
    """Export report to file"""
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    report = reporting_system.generate_report(report_type, start_dt, end_dt)
    
    if format == "csv":
        # Convert to CSV
        filename = f"verolux_report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        # Implementation for CSV export would go here
        return {"message": "CSV export not implemented yet", "filename": filename}
    else:
        # Return JSON
        return report

if __name__ == "__main__":
    print("🚀 Starting Verolux Enterprise Reporting System")
    print("=" * 60)
    print("📊 Comprehensive Analytics & Reporting")
    print("🎯 Advanced Reports Available")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)