#!/usr/bin/env python3
"""
Sample Multi-Language Incident Report Generator
Creates sample reports in Indonesian, Mandarin, and English
"""

import os
import sys
import json
from datetime import datetime
from incident_report_generator import MultiLanguageIncidentReportGenerator, IncidentData

def create_sample_multi_language_reports():
    """Create sample incident reports in all three languages"""
    
    # Initialize generator
    generator = MultiLanguageIncidentReportGenerator()
    
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
    
    print("🌍 Generating multi-language incident reports...")
    print("=" * 60)
    
    # Generate reports in all languages
    reports = generator.generate_multi_language_reports(incident)
    
    print("✅ Multi-language reports generated successfully!")
    print()
    
    # Display report information
    for lang_code in ['id', 'zh', 'en']:
        print(f"📄 {lang_code.upper()} Reports:")
        pdf_key = f'{lang_code}_pdf'
        json_key = f'{lang_code}_json'
        
        if pdf_key in reports:
            print(f"   PDF: {reports[pdf_key]}")
        if json_key in reports:
            print(f"   JSON: {reports[json_key]}")
        
        # Show sample content for each language
        template = generator.language_templates.get_template(lang_code)
        print(f"   Language: {template.language_name}")
        print(f"   Title: {template.title}")
        print()
    
    # Show available languages
    print("🌐 Available Languages:")
    available_langs = generator.language_templates.get_available_languages()
    for code, name in available_langs.items():
        print(f"   {code}: {name}")
    
    print("\n" + "="*60)
    print("📋 SAMPLE REPORT CONTENT")
    print("="*60)
    
    # Show sample content for each language
    for lang_code in ['id', 'zh', 'en']:
        template = generator.language_templates.get_template(lang_code)
        print(f"\n🇮🇩 {template.language_name} ({lang_code.upper()}):")
        print("-" * 40)
        print(f"Title: {template.title}")
        print(f"Incident ID: {incident.incident_id}")
        print(f"Date & Time: {template.fields['tanggal_waktu']} - {incident.tanggal_waktu}")
        print(f"Location: {template.fields['lokasi']} - {incident.lokasi}")
        print(f"Violation Type: {template.fields['jenis_pelanggaran']} - {incident.jenis_pelanggaran}")
        print(f"Severity: {template.fields['severity']} - {incident.severity}")
        print(f"Duration: {template.fields['durasi']} - {incident.durasi}")
        print(f"Objects: {template.fields['jumlah_objek']} - {incident.jumlah_objek}")
        print(f"Description: {template.fields['deskripsi']} - {incident.deskripsi}")
        print(f"Status: {template.fields['status']} - {incident.status}")
        print(f"Officer: {template.fields['petugas']} - {incident.petugas}")
        print(f"Action: {template.fields['tindakan']} - {incident.tindakan}")
        print(f"Notes: {template.fields['catatan']} - {incident.catatan}")
    
    return reports

if __name__ == "__main__":
    print("🚀 Multi-Language Incident Report Generator")
    print("=" * 60)
    print("🌍 Creating sample reports in Indonesian, Mandarin, and English...")
    print()
    
    try:
        reports = create_sample_multi_language_reports()
        print(f"\n✅ Sample multi-language reports generated successfully!")
        print(f"📁 Reports saved in: incident_reports/")
        
    except Exception as e:
        print(f"❌ Error generating multi-language reports: {e}")
        sys.exit(1)





























