#!/usr/bin/env python3
"""
Indonesian Incident Report Generator
Generates Laporan Kejadian (Incident Reports) in Indonesian format
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import cv2
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from language_templates import MultiLanguageTemplates
import uuid

@dataclass
class IncidentData:
    """Incident report data structure"""
    incident_id: str
    tanggal_waktu: str
    lokasi: str
    jenis_pelanggaran: str
    severity: str
    durasi: str
    jumlah_objek: str
    deskripsi: str
    status: str
    petugas: str
    tindakan: str
    catatan: str
    screenshot_path: Optional[str] = None

class MultiLanguageIncidentReportGenerator:
    """Generates multi-language incident reports (Indonesian, Mandarin, English)"""
    
    def __init__(self, db_path: str = "gate_security.db"):
        self.db_path = db_path
        self.reports_dir = "incident_reports"
        self.language_templates = MultiLanguageTemplates()
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Register fonts for different languages
        self._register_fonts()
    
    def _register_fonts(self):
        """Register fonts for different languages"""
        try:
            # Try to register system fonts for better language support
            # This is optional - ReportLab will fall back to default fonts
            pass
        except Exception as e:
            print(f"Font registration warning: {e}")
    
    def generate_incident_id(self) -> str:
        """Generate unique incident ID"""
        date_str = datetime.now().strftime("%Y%m%d")
        time_str = datetime.now().strftime("%H%M")
        return f"INC-{date_str}-{time_str}"
    
    def create_incident_from_completion(self, completion_data: Dict[str, Any], 
                                     gate_id: str = "Loading Dock - Kamera 2") -> IncidentData:
        """Create incident report from gate security completion data"""
        
        # Calculate duration
        start_time = completion_data.get('window_start', 0)
        end_time = completion_data.get('window_end', 0)
        duration_seconds = int(end_time - start_time) if end_time > start_time else 45
        
        # Determine violation type based on context
        violation_type = "Intrusion"  # Default
        if completion_data.get('score', 0) < 0.9:
            violation_type = "Security Breach"
        elif completion_data.get('interaction_duration', 0) > 10:
            violation_type = "Unauthorized Access"
        
        # Determine severity
        severity = "High"
        if completion_data.get('score', 0) > 0.95:
            severity = "Medium"
        elif completion_data.get('interaction_duration', 0) < 5:
            severity = "Low"
        
        # Generate description
        description = f"Seorang individu memasuki area {gate_id} tanpa otorisasi melalui pintu samping"
        if completion_data.get('guard_track_id'):
            description += " dan berinteraksi dengan petugas keamanan"
        
        # Generate action taken
        action = "Individu dihentikan oleh petugas, identitas diverifikasi, area diamankan."
        if completion_data.get('score', 0) > 0.9:
            action = "Pemeriksaan keamanan berhasil diselesaikan sesuai prosedur."
        
        return IncidentData(
            incident_id=self.generate_incident_id(),
            tanggal_waktu=datetime.now().strftime("%Y-%m-%d %H:%M WIB"),
            lokasi=gate_id,
            jenis_pelanggaran=violation_type,
            severity=severity,
            durasi=f"{duration_seconds} detik",
            jumlah_objek="1 orang",
            deskripsi=description,
            status="Resolved",
            petugas="Andi (Security Shift A)",
            tindakan=action,
            catatan="Tidak ada kerugian material, insiden dilaporkan ke supervisor."
        )
    
    def capture_screenshot(self, frame: np.ndarray, incident_id: str) -> str:
        """Capture screenshot for incident evidence"""
        screenshot_path = os.path.join(self.reports_dir, f"screenshot_{incident_id}.jpg")
        cv2.imwrite(screenshot_path, frame)
        return screenshot_path
    
    def generate_pdf_report(self, incident: IncidentData, language: str = 'id') -> str:
        """Generate PDF report in specified language format"""
        
        # Get language template
        template = self.language_templates.get_template(language)
        
        # Create PDF document with language-specific filename
        lang_suffix = {'id': 'ID', 'zh': 'ZH', 'en': 'EN'}.get(language, 'ID')
        pdf_path = os.path.join(self.reports_dir, f"Incident_Report_{incident.incident_id}_{lang_suffix}.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        field_style = ParagraphStyle(
            'FieldStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20
        )
        
        value_style = ParagraphStyle(
            'ValueStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=100
        )
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph(template.title, title_style))
        story.append(Spacer(1, 20))
        
        # Incident ID
        story.append(Paragraph(f"<b>{template.fields['incident_id']}:</b> {incident.incident_id}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Create table for incident details using template
        incident_data = [
            [f"<b>{template.fields['tanggal_waktu']}:</b>", incident.tanggal_waktu],
            [f"<b>{template.fields['lokasi']}:</b>", incident.lokasi],
            [f"<b>{template.fields['jenis_pelanggaran']}:</b>", incident.jenis_pelanggaran],
            [f"<b>{template.fields['severity']}:</b>", incident.severity],
            [f"<b>{template.fields['durasi']}:</b>", incident.durasi],
            [f"<b>{template.fields['jumlah_objek']}:</b>", incident.jumlah_objek],
            [f"<b>{template.fields['deskripsi']}:</b>", incident.deskripsi],
            [f"<b>{template.fields['status']}:</b>", incident.status],
            [f"<b>{template.fields['petugas']}:</b>", incident.petugas],
            [f"<b>{template.fields['tindakan']}:</b>", incident.tindakan],
            [f"<b>{template.fields['catatan']}:</b>", incident.catatan]
        ]
        
        # Create table
        table = Table(incident_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 30))
        
        # Screenshot evidence section
        story.append(Paragraph(f"<b>{template.fields['screenshot_evidence']}:</b>", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        if incident.screenshot_path and os.path.exists(incident.screenshot_path):
            # Add screenshot to PDF
            img = Image(incident.screenshot_path, width=4*inch, height=3*inch)
            story.append(img)
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"Screenshot {incident.incident_id}", 
                                 ParagraphStyle('Caption', parent=styles['Normal'], 
                                               alignment=TA_CENTER, fontSize=8)))
        else:
            story.append(Paragraph(f"Screenshot {incident.incident_id}", 
                                 ParagraphStyle('Caption', parent=styles['Normal'], 
                                               alignment=TA_CENTER, fontSize=10)))
        
        # Build PDF
        doc.build(story)
        
        return pdf_path
    
    def generate_multi_language_reports(self, incident: IncidentData) -> Dict[str, str]:
        """Generate reports in all three languages"""
        reports = {}
        
        for lang_code in ['id', 'zh', 'en']:
            try:
                # Translate incident data
                translated_data = self.language_templates.translate_incident_data(
                    incident.__dict__, lang_code
                )
                
                # Create translated incident object
                translated_incident = IncidentData(**translated_data)
                
                # Generate PDF
                pdf_path = self.generate_pdf_report(translated_incident, lang_code)
                reports[f'{lang_code}_pdf'] = pdf_path
                
                # Generate JSON
                json_path = self.generate_json_report(translated_incident, lang_code)
                reports[f'{lang_code}_json'] = json_path
                
            except Exception as e:
                print(f"Error generating {lang_code} report: {e}")
                reports[f'{lang_code}_error'] = str(e)
        
        return reports
    
    def generate_json_report(self, incident: IncidentData, language: str = 'id') -> str:
        """Generate JSON report in specified language"""
        lang_suffix = {'id': 'ID', 'zh': 'ZH', 'en': 'EN'}.get(language, 'ID')
        json_path = os.path.join(self.reports_dir, f"Incident_Report_{incident.incident_id}_{lang_suffix}.json")
        
        report_data = {
            "incident_id": incident.incident_id,
            "tanggal_waktu": incident.tanggal_waktu,
            "lokasi": incident.lokasi,
            "jenis_pelanggaran": incident.jenis_pelanggaran,
            "severity": incident.severity,
            "durasi": incident.durasi,
            "jumlah_objek": incident.jumlah_objek,
            "deskripsi": incident.deskripsi,
            "status": incident.status,
            "petugas": incident.petugas,
            "tindakan": incident.tindakan,
            "catatan": incident.catatan,
            "screenshot_path": incident.screenshot_path,
            "generated_at": datetime.now().isoformat()
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return json_path
    
    def log_incident_to_database(self, incident: IncidentData, completion_data: Dict[str, Any]):
        """Log incident to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create incidents table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT UNIQUE NOT NULL,
                tanggal_waktu TEXT NOT NULL,
                lokasi TEXT NOT NULL,
                jenis_pelanggaran TEXT NOT NULL,
                severity TEXT NOT NULL,
                durasi TEXT NOT NULL,
                jumlah_objek TEXT NOT NULL,
                deskripsi TEXT NOT NULL,
                status TEXT NOT NULL,
                petugas TEXT NOT NULL,
                tindakan TEXT NOT NULL,
                catatan TEXT,
                screenshot_path TEXT,
                session_id TEXT,
                visitor_track_id INTEGER,
                guard_track_id INTEGER,
                score REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_incident_id (incident_id),
                INDEX idx_tanggal_waktu (tanggal_waktu),
                INDEX idx_lokasi (lokasi),
                INDEX idx_severity (severity)
            )
        ''')
        
        # Insert incident
        cursor.execute('''
            INSERT INTO incidents 
            (incident_id, tanggal_waktu, lokasi, jenis_pelanggaran, severity, 
             durasi, jumlah_objek, deskripsi, status, petugas, tindakan, 
             catatan, screenshot_path, session_id, visitor_track_id, 
             guard_track_id, score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            incident.incident_id,
            incident.tanggal_waktu,
            incident.lokasi,
            incident.jenis_pelanggaran,
            incident.severity,
            incident.durasi,
            incident.jumlah_objek,
            incident.deskripsi,
            incident.status,
            incident.petugas,
            incident.tindakan,
            incident.catatan,
            incident.screenshot_path,
            completion_data.get('session_id'),
            completion_data.get('visitor_track_id'),
            completion_data.get('guard_track_id'),
            completion_data.get('score')
        ))
        
        conn.commit()
        conn.close()
    
    def get_incidents_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get incidents within date range"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM incidents 
            WHERE tanggal_waktu BETWEEN ? AND ?
            ORDER BY tanggal_waktu DESC
        ''', (start_date, end_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_incident_by_id(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get incident by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM incidents WHERE incident_id = ?', (incident_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row is None:
            return None
        
        return dict(row)
    
    def generate_comprehensive_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate comprehensive incident report"""
        incidents = self.get_incidents_by_date_range(start_date, end_date)
        
        # Statistics
        total_incidents = len(incidents)
        high_severity = len([i for i in incidents if i['severity'] == 'High'])
        medium_severity = len([i for i in incidents if i['severity'] == 'Medium'])
        low_severity = len([i for i in incidents if i['severity'] == 'Low'])
        
        # Group by location
        location_counts = {}
        for incident in incidents:
            location = incident['lokasi']
            location_counts[location] = location_counts.get(location, 0) + 1
        
        # Group by violation type
        violation_counts = {}
        for incident in incidents:
            violation = incident['jenis_pelanggaran']
            violation_counts[violation] = violation_counts.get(violation, 0) + 1
        
        return {
            "report_period": {
                "start_date": start_date,
                "end_date": end_date,
                "generated_at": datetime.now().isoformat()
            },
            "summary": {
                "total_incidents": total_incidents,
                "high_severity": high_severity,
                "medium_severity": medium_severity,
                "low_severity": low_severity
            },
            "by_location": location_counts,
            "by_violation_type": violation_counts,
            "incidents": incidents
        }

# FastAPI integration for incident reports
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(title="Multi-Language Incident Report API")

# Initialize generator
incident_generator = MultiLanguageIncidentReportGenerator()

@app.get("/languages")
async def get_available_languages():
    """Get available languages"""
    return incident_generator.language_templates.get_available_languages()

@app.post("/incidents/generate")
async def generate_incident_report(completion_data: Dict[str, Any], language: str = 'id'):
    """Generate incident report from completion data in specified language"""
    try:
        # Create incident from completion data
        incident = incident_generator.create_incident_from_completion(completion_data)
        
        # Generate PDF and JSON reports in specified language
        pdf_path = incident_generator.generate_pdf_report(incident, language)
        json_path = incident_generator.generate_json_report(incident, language)
        
        # Log to database
        incident_generator.log_incident_to_database(incident, completion_data)
        
        return {
            "incident_id": incident.incident_id,
            "language": language,
            "pdf_path": pdf_path,
            "json_path": json_path,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/incidents/generate-multi")
async def generate_multi_language_reports(completion_data: Dict[str, Any]):
    """Generate incident reports in all three languages"""
    try:
        # Create incident from completion data
        incident = incident_generator.create_incident_from_completion(completion_data)
        
        # Generate reports in all languages
        reports = incident_generator.generate_multi_language_reports(incident)
        
        # Log to database
        incident_generator.log_incident_to_database(incident, completion_data)
        
        return {
            "incident_id": incident.incident_id,
            "reports": reports,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get incident by ID"""
    incident = incident_generator.get_incident_by_id(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@app.get("/incidents")
async def get_incidents(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """Get incidents by date range"""
    incidents = incident_generator.get_incidents_by_date_range(start_date, end_date)
    return {"incidents": incidents, "count": len(incidents)}

@app.get("/incidents/report/comprehensive")
async def get_comprehensive_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """Get comprehensive incident report"""
    return incident_generator.generate_comprehensive_report(start_date, end_date)

@app.get("/incidents/{incident_id}/pdf")
async def download_incident_pdf(incident_id: str):
    """Download incident PDF report"""
    incident = incident_generator.get_incident_by_id(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    pdf_path = os.path.join(incident_generator.reports_dir, f"Laporan_Kejadian_{incident_id}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF report not found")
    
    return FileResponse(pdf_path, filename=f"Laporan_Kejadian_{incident_id}.pdf")

if __name__ == "__main__":
    print("🚀 Starting Indonesian Incident Report Generator")
    print("=" * 60)
    print("📋 Laporan Kejadian (Incident Reports)")
    print("🇮🇩 Indonesian Format")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8004)
