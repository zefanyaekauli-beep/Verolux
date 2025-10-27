#!/usr/bin/env python3
"""
Verolux1st - Semantic Search Backend
Advanced AI-powered search that understands context and meaning
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import sqlite3
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Configuration
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "verolux1st.db")
MODEL_NAME = "all-MiniLM-L6-v2"  # Lightweight sentence transformer model

app = FastAPI(title="Verolux1st - Semantic Search API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
semantic_model = None

class SearchQuery(BaseModel):
    query: str
    search_type: str = "all"  # all, detections, reports, analytics, violations
    limit: int = 20
    date_range: Optional[Dict[str, str]] = None

class SearchResult(BaseModel):
    id: str
    title: str
    content: str
    type: str
    relevance_score: float
    timestamp: str
    metadata: Dict[str, Any]

def load_semantic_model():
    """Load the sentence transformer model for semantic search"""
    global semantic_model
    print("🧠 Loading semantic search model...")
    try:
        semantic_model = SentenceTransformer(MODEL_NAME)
        print("✅ Semantic search model loaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error loading semantic model: {e}")
        return False

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_sample_data():
    """Create sample data for demonstration"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            camera_id TEXT,
            object_type TEXT,
            confidence REAL,
            location TEXT,
            description TEXT,
            metadata TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            report_type TEXT,
            created_at TEXT,
            author TEXT,
            status TEXT,
            metadata TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id TEXT PRIMARY KEY,
            violation_type TEXT,
            description TEXT,
            severity TEXT,
            location TEXT,
            timestamp TEXT,
            status TEXT,
            metadata TEXT
        )
    ''')
    
    # Insert sample data
    sample_detections = [
        ("det_001", "2024-01-15 10:30:00", "cam_001", "person", 0.95, "Main Entrance", "Person detected at main entrance with high confidence", '{"bbox": [100, 200, 300, 400], "track_id": "track_001"}'),
        ("det_002", "2024-01-15 10:35:00", "cam_002", "vehicle", 0.88, "Parking Lot", "Vehicle entering parking area", '{"bbox": [50, 150, 250, 350], "license_plate": "ABC123"}'),
        ("det_003", "2024-01-15 11:00:00", "cam_001", "person", 0.92, "Main Entrance", "Person leaving the building", '{"bbox": [120, 180, 280, 420], "track_id": "track_002"}'),
        ("det_004", "2024-01-15 11:15:00", "cam_003", "person", 0.85, "Security Checkpoint", "Person at security checkpoint", '{"bbox": [200, 250, 400, 500], "security_clearance": "pending"}'),
        ("det_005", "2024-01-15 12:00:00", "cam_002", "vehicle", 0.90, "Parking Lot", "Vehicle exiting parking area", '{"bbox": [80, 200, 300, 400], "license_plate": "XYZ789"}'),
    ]
    
    sample_reports = [
        ("rep_001", "Daily Security Summary", "Comprehensive security report covering all camera feeds and detection events from the past 24 hours", "security", "2024-01-15 12:00:00", "Security Team", "completed", '{"total_detections": 45, "alerts": 3, "cameras_covered": 8}'),
        ("rep_002", "Parking Lot Analytics", "Analysis of vehicle traffic patterns and occupancy rates in the main parking facility", "analytics", "2024-01-15 11:30:00", "Analytics Team", "completed", '{"peak_hours": "9-11 AM", "occupancy_rate": 0.75, "total_vehicles": 120}'),
        ("rep_003", "Incident Report - Unauthorized Access", "Detailed report of unauthorized access attempt at the main entrance", "incident", "2024-01-15 10:45:00", "Security Officer", "investigating", '{"severity": "high", "location": "Main Entrance", "time": "10:30 AM"}'),
        ("rep_004", "Weekly Performance Review", "Weekly performance metrics and system health status across all surveillance systems", "performance", "2024-01-15 09:00:00", "System Admin", "completed", '{"uptime": 99.8, "detection_accuracy": 94.2, "system_load": "normal"}'),
    ]
    
    sample_violations = [
        ("vio_001", "Unauthorized Access", "Person attempted to enter restricted area without proper authorization", "high", "Main Entrance", "2024-01-15 10:30:00", "investigating", '{"person_id": "track_001", "attempts": 2, "security_alert": true}'),
        ("vio_002", "Loitering", "Person loitering in restricted area for extended period", "medium", "Security Checkpoint", "2024-01-15 11:15:00", "resolved", '{"duration": "15 minutes", "person_id": "track_002", "security_intervention": true}'),
        ("vio_003", "Vehicle Violation", "Vehicle parked in unauthorized area", "low", "Parking Lot", "2024-01-15 12:00:00", "pending", '{"license_plate": "XYZ789", "violation_type": "no_parking_zone"}'),
    ]
    
    # Insert sample data
    cursor.executemany('''
        INSERT OR REPLACE INTO detections 
        (id, timestamp, camera_id, object_type, confidence, location, description, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_detections)
    
    cursor.executemany('''
        INSERT OR REPLACE INTO reports 
        (id, title, content, report_type, created_at, author, status, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_reports)
    
    cursor.executemany('''
        INSERT OR REPLACE INTO violations 
        (id, violation_type, description, severity, location, timestamp, status, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_violations)
    
    conn.commit()
    conn.close()
    print("✅ Sample data created successfully!")

def preprocess_text(text: str) -> str:
    """Preprocess text for better semantic matching"""
    # Remove special characters and normalize
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def get_semantic_embeddings(texts: List[str]) -> np.ndarray:
    """Get semantic embeddings for a list of texts"""
    if semantic_model is None:
        raise HTTPException(status_code=500, detail="Semantic model not loaded")
    
    # Preprocess texts
    processed_texts = [preprocess_text(text) for text in texts]
    
    # Get embeddings
    embeddings = semantic_model.encode(processed_texts)
    return embeddings

def calculate_relevance_scores(query_embedding: np.ndarray, content_embeddings: np.ndarray) -> List[float]:
    """Calculate relevance scores using cosine similarity"""
    similarities = cosine_similarity([query_embedding], content_embeddings)[0]
    return similarities.tolist()

@app.on_event("startup")
async def startup_event():
    """Initialize the semantic search system"""
    if not load_semantic_model():
        print("❌ Failed to load semantic model. Exiting...")
        os._exit(1)
    
    # Create sample data
    create_sample_data()
    print("✅ Semantic Search Backend ready!")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": "SentenceTransformer",
        "model_name": MODEL_NAME,
        "system": "Semantic Search"
    }

@app.post("/search", response_model=List[SearchResult])
async def semantic_search(search_query: SearchQuery):
    """Perform semantic search across all data sources"""
    if semantic_model is None:
        raise HTTPException(status_code=500, detail="Semantic model not loaded")
    
    try:
        # Get query embedding
        query_embedding = get_semantic_embeddings([search_query.query])[0]
        
        results = []
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search detections
        if search_query.search_type in ["all", "detections"]:
            cursor.execute("SELECT * FROM detections ORDER BY timestamp DESC LIMIT ?", (search_query.limit,))
            detections = cursor.fetchall()
            
            if detections:
                # Prepare content for embedding
                detection_content = []
                for det in detections:
                    content = f"{det['object_type']} detected at {det['location']} with confidence {det['confidence']}. {det['description']}"
                    detection_content.append(content)
                
                # Get embeddings and calculate relevance
                detection_embeddings = get_semantic_embeddings(detection_content)
                relevance_scores = calculate_relevance_scores(query_embedding, detection_embeddings)
                
                for i, det in enumerate(detections):
                    results.append(SearchResult(
                        id=det['id'],
                        title=f"{det['object_type'].title()} Detection",
                        content=det['description'],
                        type="detection",
                        relevance_score=float(relevance_scores[i]),
                        timestamp=det['timestamp'],
                        metadata=json.loads(det['metadata']) if det['metadata'] else {}
                    ))
        
        # Search reports
        if search_query.search_type in ["all", "reports"]:
            cursor.execute("SELECT * FROM reports ORDER BY created_at DESC LIMIT ?", (search_query.limit,))
            reports = cursor.fetchall()
            
            if reports:
                report_content = [f"{rep['title']}. {rep['content']}" for rep in reports]
                report_embeddings = get_semantic_embeddings(report_content)
                relevance_scores = calculate_relevance_scores(query_embedding, report_embeddings)
                
                for i, rep in enumerate(reports):
                    results.append(SearchResult(
                        id=rep['id'],
                        title=rep['title'],
                        content=rep['content'],
                        type="report",
                        relevance_score=float(relevance_scores[i]),
                        timestamp=rep['created_at'],
                        metadata=json.loads(rep['metadata']) if rep['metadata'] else {}
                    ))
        
        # Search violations
        if search_query.search_type in ["all", "violations"]:
            cursor.execute("SELECT * FROM violations ORDER BY timestamp DESC LIMIT ?", (search_query.limit,))
            violations = cursor.fetchall()
            
            if violations:
                violation_content = [f"{vio['violation_type']} at {vio['location']}. {vio['description']}" for vio in violations]
                violation_embeddings = get_semantic_embeddings(violation_content)
                relevance_scores = calculate_relevance_scores(query_embedding, violation_embeddings)
                
                for i, vio in enumerate(violations):
                    results.append(SearchResult(
                        id=vio['id'],
                        title=f"{vio['violation_type']} Violation",
                        content=vio['description'],
                        type="violation",
                        relevance_score=float(relevance_scores[i]),
                        timestamp=vio['timestamp'],
                        metadata=json.loads(vio['metadata']) if vio['metadata'] else {}
                    ))
        
        conn.close()
        
        # Sort by relevance score and limit results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:search_query.limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/search/suggestions")
async def get_search_suggestions(q: str = Query(..., min_length=2)):
    """Get search suggestions based on partial query"""
    suggestions = [
        "person detected at main entrance",
        "vehicle in parking lot",
        "security incident report",
        "unauthorized access attempt",
        "high confidence detection",
        "parking violation",
        "loitering in restricted area",
        "security checkpoint activity",
        "daily security summary",
        "performance analytics report"
    ]
    
    # Filter suggestions based on query
    filtered_suggestions = [s for s in suggestions if q.lower() in s.lower()]
    return {"suggestions": filtered_suggestions[:5]}

@app.get("/search/analytics")
async def get_search_analytics():
    """Get search analytics and performance metrics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get counts
    cursor.execute("SELECT COUNT(*) FROM detections")
    detection_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM reports")
    report_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM violations")
    violation_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_detections": detection_count,
        "total_reports": report_count,
        "total_violations": violation_count,
        "search_capabilities": [
            "Natural language queries",
            "Context-aware search",
            "Multi-source search",
            "Relevance scoring",
            "Real-time suggestions"
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting Verolux1st Semantic Search Backend...")
    uvicorn.run(app, host="0.0.0.0", port=8003)
