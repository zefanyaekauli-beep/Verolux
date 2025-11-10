#!/usr/bin/env python3
"""
Sample Incident Report Generator
Creates a sample Indonesian incident report for demonstration
"""

import os
import sys
import json
from datetime import datetime
from incident_report_generator import IndonesianIncidentReportGenerator, IncidentData

def create_sample_incident():
    """Create a sample incident report"""
    
    # Initialize generator
    generator = IndonesianIncidentReportGenerator()
    
    # Create sample incident data
    incident = IncidentData(
        incident_id="INC-20250929-001",
        tanggal_waktu="2025-09-29 08:15 WIB",
        lokasi="Loading Dock - Kamera 2",
        jenis_pelanggaran="Intrusion",
        severity="High",
        durasi="45 detik",
        jumlah_objek="1 orang",
        deskripsi="Seorang individu memasuki area loading dock tanpa otorisasi melalui pintu samping",
        status="Resolved",
        petugas="Andi (Security Shift A)",
        tindakan="Individu dihentikan oleh petugas, identitas diverifikasi, area diamankan.",
        catatan="Tidak ada kerugian material, insiden dilaporkan ke supervisor."
    )
    
    # Generate reports
    print("📋 Generating sample incident report...")
    
    # Generate PDF
    pdf_path = generator.generate_pdf_report(incident)
    print(f"✅ PDF Report: {pdf_path}")
    
    # Generate JSON
    json_path = generator.generate_json_report(incident)
    print(f"✅ JSON Report: {json_path}")
    
    # Show report content
    print("\n" + "="*60)
    print("LAPORAN KEJADIAN (INCIDENT REPORTS)")
    print("="*60)
    print(f"Incident ID: {incident.incident_id}")
    print()
    print("Tanggal & Waktu (Date & Time):", incident.tanggal_waktu)
    print("Lokasi (Location):", incident.lokasi)
    print("Jenis Pelanggaran (Type of Violation):", incident.jenis_pelanggaran)
    print("Severity:", incident.severity)
    print("Durasi (Duration):", incident.durasi)
    print("Jumlah Objek (Number of Objects):", incident.jumlah_objek)
    print("Deskripsi (Description):", incident.deskripsi)
    print("Status:", incident.status)
    print("Petugas (PIC) (Officer (PIC)):", incident.petugas)
    print("Tindakan (Action):", incident.tindakan)
    print("Catatan (Notes):", incident.catatan)
    print()
    print("Screenshot Evidence:")
    print("Screenshot INC-20250929-001")
    print("="*60)
    
    return pdf_path, json_path

if __name__ == "__main__":
    print("🚀 Sample Incident Report Generator")
    print("=" * 60)
    print("📋 Creating sample Indonesian incident report...")
    print()
    
    try:
        pdf_path, json_path = create_sample_incident()
        print(f"\n✅ Sample reports generated successfully!")
        print(f"📄 PDF: {pdf_path}")
        print(f"📄 JSON: {json_path}")
        
    except Exception as e:
        print(f"❌ Error generating sample report: {e}")
        sys.exit(1)




























