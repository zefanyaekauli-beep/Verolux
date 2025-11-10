#!/usr/bin/env python3
"""
Generate comprehensive system documentation PDF for Verox System
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_system_documentation_pdf():
    """Generate comprehensive system documentation PDF"""
    
    # Create output directory
    output_dir = "documentation"
    os.makedirs(output_dir, exist_ok=True)
    
    # PDF filename
    pdf_filename = os.path.join(output_dir, f"Verox_System_Documentation_{datetime.now().strftime('%Y%m%d')}.pdf")
    
    # Create PDF document
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=72)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e293b'),
        fontName='Helvetica-Bold'
    )
    
    main_title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        spaceBefore=20,
        textColor=colors.HexColor('#1e40af'),
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=colors.HexColor('#3b82f6'),
        borderPadding=10,
        backColor=colors.HexColor('#dbeafe')
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=12,
        textColor=colors.HexColor('#1e40af'),
        fontName='Helvetica-Bold'
    )
    
    subsection_style = ParagraphStyle(
        'Subsection',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=8,
        textColor=colors.HexColor('#334155'),
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=14
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        leftIndent=20,
        rightIndent=20,
        backColor=colors.HexColor('#f1f5f9'),
        borderColor=colors.HexColor('#cbd5e1'),
        borderWidth=1,
        borderPadding=5
    )
    
    # Build content
    story = []
    
    # Title Page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Verox System", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Comprehensive System Documentation", ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#64748b')
    )))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#64748b')
    )))
    story.append(PageBreak())
    
    # Table of Contents
    story.append(Paragraph("Table of Contents", main_title_style))
    story.append(Spacer(1, 0.2*inch))
    
    toc_items = [
        "1. System Overview",
        "2. High-Level Architecture",
        "3. Frontend Architecture",
        "4. Backend Architecture",
        "5. Data Flow",
        "6. Key Features",
        "7. Database Architecture",
        "8. Configuration System",
        "9. API Endpoints",
        "10. Deployment Architecture",
        "11. Performance Characteristics",
        "12. Security & Privacy",
        "13. Use Cases",
        "14. System Strengths"
    ]
    
    for item in toc_items:
        story.append(Paragraph(item, body_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # 1. System Overview
    story.append(Paragraph("1. System Overview", main_title_style))
    story.append(Paragraph(
        "Verox (Verolux1st) is an AI-powered security checkpoint system designed for real-time video "
        "analysis, body checking, gate security monitoring, and comprehensive analytics. The system "
        "combines advanced computer vision, AI detection, and modern web interfaces to provide a "
        "complete security monitoring solution.",
        body_style
    ))
    story.append(PageBreak())
    
    # 2. High-Level Architecture
    story.append(Paragraph("2. High-Level Architecture", main_title_style))
    story.append(Paragraph("2.1 Three-Tier Architecture", section_style))
    
    architecture_text = """
    The system follows a three-tier architecture:
    
    <b>Frontend Layer:</b> React + Vite + Zustand (State Management) on Port 5173
    <b>Backend Layer:</b> FastAPI + Python + YOLOv8 + Computer Vision on Ports 8002 (Main), 8001 (Reports), 8003 (Semantic)
    <b>Data & Model Layer:</b> SQLite Databases + YOLOv8 Models + Video Sources
    
    The frontend communicates with the backend via HTTP/REST API and WebSocket connections for real-time updates.
    """
    
    story.append(Paragraph(architecture_text, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # 3. Frontend Architecture
    story.append(Paragraph("3. Frontend Architecture", main_title_style))
    story.append(Paragraph("3.1 Technology Stack", section_style))
    
    tech_stack = """
    • React 18.2.0 - Modern UI framework
    • Vite - Fast build tool and dev server
    • Zustand - Lightweight state management
    • Framer Motion - Animation library
    • React Konva - Canvas rendering
    • Recharts - Data visualization
    """
    
    story.append(Paragraph(tech_stack, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("3.2 Main Components & Pages", section_style))
    
    components = """
    <b>Dashboard:</b> System overview, real-time statistics, health monitoring
    
    <b>Simple Inference:</b> Real-time object detection, gate configuration, live video stream with overlay, 
    detection statistics (FPS, object count), adjustable gate areas
    
    <b>Advanced Body Checking:</b> Queue management, group detection, ticket-based system, 
    Batch/Sequential examination modes
    
    <b>Gate Security:</b> 3-layer pipeline monitoring, FSM state visualization, check completion tracking
    
    <b>Analytics:</b> Traffic patterns, behavior analysis, performance metrics
    
    <b>Reports:</b> Incident reports, compliance reports, multi-language support
    
    <b>Semantic Search:</b> Natural language search for events and incidents
    """
    
    story.append(Paragraph(components, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("3.3 State Management (Zustand Stores)", section_style))
    
    stores = """
    • auth.js - JWT authentication, user roles (Admin/Viewer)
    • status.js - System health, model status
    • events.js - Event data management
    • alerts.js - Alert management
    • ui.js - UI state (current page, sidebar)
    • lang.js - Internationalization
    • theme.js - Theme settings
    """
    
    story.append(Paragraph(stores, body_style))
    story.append(PageBreak())
    
    # 4. Backend Architecture
    story.append(Paragraph("4. Backend Architecture", main_title_style))
    story.append(Paragraph("4.1 Main Server Files", section_style))
    
    backend_main = """
    <b>advanced_body_checking.py (Port 8002):</b>
    Main backend server with real-time video processing, gate security features, queue management, 
    and authentication & security.
    
    <b>gate_sop_checker.py:</b>
    3-layer pipeline for gate security:
    • Layer 1: Perception (Object detection, tracking, zone analysis, pose estimation)
    • Layer 2: Events (Micro-events logging, session management)
    • Layer 3: Decisions (FSM per person, explainable scoring, hysteresis logic)
    """
    
    story.append(Paragraph(backend_main, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("4.2 Supporting Backend Modules", section_style))
    
    modules = """
    • tracking_system.py - ByteTrack multi-object tracking
    • zone_utils.py - Polygon operations, point-in-polygon, jitter filtering
    • pose_estimator.py - YOLOv8-pose integration, gesture detection
    • event_system.py - Event logging and session management
    • fsm_decision.py - Finite state machine decision engine
    • gate_database.py - SQLite storage for events, sessions, completions
    • analytics_system.py - Analytics and reporting (Port 8001)
    • reporting_system.py - Report generation with multi-language support
    • semantic_search.py - Semantic search backend (Port 8003)
    • incident_report_generator.py - Multi-language incident reports
    """
    
    story.append(Paragraph(modules, body_style))
    story.append(PageBreak())
    
    # 5. Data Flow
    story.append(Paragraph("5. Data Flow", main_title_style))
    story.append(Paragraph("5.1 Real-Time Detection Flow", section_style))
    
    data_flow = """
    1. Video Source (Webcam/File/RTSP)
    2. Frame Capture (OpenCV)
    3. YOLOv8 Detection → Person/object detection with confidence filtering
    4. Multi-Object Tracking (ByteTrack) → Track assignment, IoU matching, Re-ID
    5. Zone Analysis → Gate area detection, guard anchor detection, proximity calculation
    6. Pose Estimation (Optional) → Hand-to-torso detection, reach gesture detection
    7. Event Generation → Micro-events logged, session management
    8. FSM Decision Engine → State transitions, scoring calculation, check completion
    9. WebSocket Broadcast → Real-time updates to frontend
    10. Database Storage → Events logged, sessions tracked, completions recorded
    """
    
    story.append(Paragraph(data_flow, body_style))
    story.append(PageBreak())
    
    # 6. Key Features
    story.append(Paragraph("6. Key Features", main_title_style))
    
    features = """
    <b>6.1 Real-Time Object Detection:</b>
    • YOLOv8 models (YOLOv8n, YOLOv8n-pose)
    • Multiple classes: person, car, truck, bus, bicycle, motorcycle
    • Confidence threshold: 0.3
    • Max detections: 50 objects
    • FP16 optimization for performance
    
    <b>6.2 Gate Security System:</b>
    • Configurable gate areas (normalized polygons)
    • Guard anchor zones
    • Real-time monitoring
    • Body checking alerts
    • Check completion detection
    
    <b>6.3 Advanced Body Checking:</b>
    • Group detection (spatio-temporal clustering)
    • Ticket-based queue management
    • Batch and Sequential examination modes
    • Guard identification and tracking
    • SLA monitoring (Yellow/Red alerts)
    
    <b>6.4 Analytics & Reporting:</b>
    • Traffic flow analysis
    • Behavior pattern detection
    • PPE compliance monitoring
    • Anomaly detection
    • Multi-language incident reports (EN, ID, ZH)
    
    <b>6.5 Security Features:</b>
    • JWT authentication
    • Role-based access control
    • Rate limiting
    • Security headers (CORS, CSP, XSS protection)
    • Audit logging
    • PII scrubbing
    
    <b>6.6 Multi-Language Support:</b>
    • Incident reports in multiple languages
    • Template-based generation
    • PDF export
    """
    
    story.append(Paragraph(features, body_style))
    story.append(PageBreak())
    
    # 7. Database Architecture
    story.append(Paragraph("7. Database Architecture", main_title_style))
    story.append(Paragraph("7.1 SQLite Databases", section_style))
    
    databases = """
    <b>gate_security.db:</b>
    • Events (micro-events)
    • Sessions (check sessions)
    • Contact events (proximity interactions)
    • Pose events
    • Check completions
    • Snapshots
    • Anomalies
    • Performance metrics
    
    <b>verolux_analytics.db:</b>
    • Analytics data
    • Traffic patterns
    • Behavior metrics
    
    <b>verolux_enterprise.db:</b>
    • Enterprise-level data
    • Reporting data
    
    <b>verolux1st.db:</b>
    • Main application data
    """
    
    story.append(Paragraph(databases, body_style))
    story.append(PageBreak())
    
    # 8. Configuration System
    story.append(Paragraph("8. Configuration System", main_title_style))
    story.append(Paragraph("8.1 Gate Configuration", section_style))
    
    config_text = """
    The system uses JSON-based configuration files for:
    • Zone definitions (polygons)
    • Timer thresholds
    • Proximity settings
    • Scoring parameters
    • Real-time configuration updates
    • Save/Load functionality
    
    Configuration includes:
    • Gate ID and zone definitions
    • Timer settings (dwell times, interaction windows)
    • Proximity detection parameters
    • Pose estimation settings
    • Scoring system parameters
    • Guard anchor logic
    """
    
    story.append(Paragraph(config_text, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Example configuration
    story.append(Paragraph("8.2 Example Configuration Structure", section_style))
    config_example = """
    {
      "gate_id": "A1",
      "zones": {
        "gate_area": "gate_A1_polygon.json",
        "guard_anchor": "guard_anchor_A1_polygon.json"
      },
      "timers": {
        "person_min_dwell_s": 6.0,
        "guard_min_dwell_s": 3.0,
        "interaction_min_overlap_s": 1.2
      },
      "scoring": {
        "base": 0.6,
        "contact_bonus": 0.2,
        "pose_bonus": 0.15,
        "threshold": 0.9
      }
    }
    """
    
    story.append(Paragraph(config_example, code_style))
    story.append(PageBreak())
    
    # 9. API Endpoints
    story.append(Paragraph("9. API Endpoints", main_title_style))
    story.append(Paragraph("9.1 Main Backend (Port 8002)", section_style))
    
    api_main = """
    • GET /health - Health check
    • GET /internal/health - Authenticated health check
    • POST /auth/login - User authentication
    • GET /config/gate - Get gate configuration
    • POST /config/gate - Update gate configuration
    • GET /video/source - Get current video source
    • POST /video/source - Change video source
    • GET /counts - Get object counting statistics
    • POST /counts/reset - Reset counters
    • WebSocket /ws?token=... - Real-time detection stream
    """
    
    story.append(Paragraph(api_main, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("9.2 Gate Security Endpoints", section_style))
    
    api_gate = """
    • GET /gate/completions - List completed checks
    • GET /gate/session/{id} - Session details + timeline
    • GET /gate/stats - Performance statistics
    • GET /gate/config - Current configuration
    • POST /gate/reset - Reset checker state
    • WebSocket /ws/gate-check - Gate check stream
    """
    
    story.append(Paragraph(api_gate, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("9.3 Analytics (Port 8001)", section_style))
    
    api_analytics = """
    • GET /analytics/traffic-flow - Traffic analysis
    • GET /analytics/behavior-patterns - Behavior analysis
    • GET /analytics/ppe-compliance - PPE compliance
    • GET /analytics/anomalies - Anomaly detection
    """
    
    story.append(Paragraph(api_analytics, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("9.4 Reporting (Port 8001)", section_style))
    
    api_reports = """
    • GET /reports/incidents - Incident reports
    • POST /reports/export - Export reports
    • GET /reports/compliance - Compliance reports
    """
    
    story.append(Paragraph(api_reports, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("9.5 Semantic Search (Port 8003)", section_style))
    
    api_search = """
    • POST /search/query - Semantic search
    • GET /search/analytics - Search analytics
    """
    
    story.append(Paragraph(api_search, body_style))
    story.append(PageBreak())
    
    # 10. Deployment Architecture
    story.append(Paragraph("10. Deployment Architecture", main_title_style))
    story.append(Paragraph("10.1 Development Setup", section_style))
    
    deployment = """
    • Backend: Python FastAPI on port 8002
    • Frontend: Vite dev server on port 5173
    • Models: Local YOLOv8 models
    • Databases: Local SQLite files
    """
    
    story.append(Paragraph(deployment, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("10.2 Production Options", section_style))
    
    production = """
    • Docker containers (multiple Dockerfiles available)
    • Kubernetes deployment configs
    • GCP deployment configurations
    • Nginx reverse proxy
    • SSL/TLS support
    • Monitoring with Prometheus/Grafana
    """
    
    story.append(Paragraph(production, body_style))
    story.append(PageBreak())
    
    # 11. Performance Characteristics
    story.append(Paragraph("11. Performance Characteristics", main_title_style))
    
    performance = """
    • Processing Speed: ~5-20 FPS (configurable)
    • Latency: <200ms per frame
    • Memory Usage: ~500MB-2GB (depending on configuration)
    • CPU Usage: 15-30% (without GPU)
    • GPU Usage: 5-10% (with CUDA)
    • Scalability: Up to 10 simultaneous tracks per gate
    """
    
    story.append(Paragraph(performance, body_style))
    story.append(PageBreak())
    
    # 12. Security & Privacy
    story.append(Paragraph("12. Security & Privacy", main_title_style))
    
    security = """
    • Local processing (no cloud dependency)
    • JWT-based authentication
    • Role-based access control
    • Rate limiting
    • Security headers (CSP, XSS protection)
    • Audit trail for compliance
    • Configurable snapshot retention
    • PII scrubbing capabilities
    • Database encryption (optional)
    """
    
    story.append(Paragraph(security, body_style))
    story.append(PageBreak())
    
    # 13. Use Cases
    story.append(Paragraph("13. Use Cases", main_title_style))
    
    use_cases = """
    • Airport security checkpoints
    • Building entrance security
    • Event venue gate monitoring
    • Facility access control
    • Compliance monitoring and reporting
    • Real-time security analytics
    """
    
    story.append(Paragraph(use_cases, body_style))
    story.append(PageBreak())
    
    # 14. System Strengths
    story.append(Paragraph("14. System Strengths", main_title_style))
    
    strengths = """
    <b>1. Modular Architecture:</b>
    Well-organized codebase with clear separation of concerns
    
    <b>2. Real-Time Processing:</b>
    WebSocket streaming for instant updates
    
    <b>3. Explainable AI:</b>
    FSM-based decision making with scoring system
    
    <b>4. Production-Ready:</b>
    Error handling, logging, monitoring, and scalability features
    
    <b>5. Configurable:</b>
    JSON-based configuration without code changes
    
    <b>6. Multi-Language Support:</b>
    Incident reports in multiple languages
    
    <b>7. Scalable:</b>
    Designed for multiple gates/cameras
    
    <b>8. Security-Focused:</b>
    Comprehensive security features and audit trails
    """
    
    story.append(Paragraph(strengths, body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    story.append(Paragraph(
        f"<i>Document generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</i>",
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#64748b')
        )
    ))
    
    # Build PDF
    doc.build(story)
    
    print("PDF documentation generated successfully!")
    print(f"Location: {pdf_filename}")
    print(f"File size: {os.path.getsize(pdf_filename) / 1024:.2f} KB")
    
    return pdf_filename

if __name__ == "__main__":
    try:
        pdf_path = create_system_documentation_pdf()
        print(f"\nSystem documentation PDF created at: {pdf_path}")
    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc()

