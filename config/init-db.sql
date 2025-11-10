-- Initialize Verolux Production Database

-- Create databases
CREATE DATABASE IF NOT EXISTS verolux;
CREATE DATABASE IF NOT EXISTS keycloak;

-- Connect to verolux database
\c verolux;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create gate security tables
CREATE TABLE IF NOT EXISTS gate_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    gate_id VARCHAR(50) NOT NULL,
    visitor_track_id INTEGER,
    guard_track_id INTEGER,
    start_time DOUBLE PRECISION NOT NULL,
    end_time DOUBLE PRECISION,
    score DOUBLE PRECISION,
    visitor_dwell_time DOUBLE PRECISION,
    interaction_duration DOUBLE PRECISION,
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gate_events (
    event_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES gate_sessions(session_id) ON DELETE CASCADE,
    timestamp DOUBLE PRECISION NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    track_id INTEGER,
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS detections (
    id SERIAL PRIMARY KEY,
    timestamp DOUBLE PRECISION NOT NULL,
    camera_id VARCHAR(100),
    object_class VARCHAR(100),
    confidence DOUBLE PRECISION,
    bbox JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics_metrics (
    id SERIAL PRIMARY KEY,
    timestamp DOUBLE PRECISION NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION,
    metric_type VARCHAR(50),
    tags JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS incident_reports (
    report_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES gate_sessions(session_id),
    report_type VARCHAR(100),
    severity VARCHAR(50),
    language VARCHAR(10) DEFAULT 'en',
    title VARCHAR(500),
    description TEXT,
    file_path VARCHAR(500),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS camera_sources (
    camera_id VARCHAR(100) PRIMARY KEY,
    camera_name VARCHAR(255),
    source_url VARCHAR(500),
    location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_gate_sessions_gate_id ON gate_sessions(gate_id);
CREATE INDEX idx_gate_sessions_start_time ON gate_sessions(start_time);
CREATE INDEX idx_gate_sessions_status ON gate_sessions(status);
CREATE INDEX idx_gate_events_session_id ON gate_events(session_id);
CREATE INDEX idx_gate_events_timestamp ON gate_events(timestamp);
CREATE INDEX idx_gate_events_event_type ON gate_events(event_type);
CREATE INDEX idx_detections_timestamp ON detections(timestamp);
CREATE INDEX idx_detections_camera_id ON detections(camera_id);
CREATE INDEX idx_detections_object_class ON detections(object_class);
CREATE INDEX idx_analytics_timestamp ON analytics_metrics(timestamp);
CREATE INDEX idx_analytics_metric_name ON analytics_metrics(metric_name);

-- Create views for common queries
CREATE OR REPLACE VIEW v_gate_completions AS
SELECT 
    s.session_id,
    s.gate_id,
    s.visitor_track_id,
    s.guard_track_id,
    s.start_time,
    s.end_time,
    s.score,
    s.visitor_dwell_time,
    s.interaction_duration,
    COUNT(e.event_id) as event_count
FROM gate_sessions s
LEFT JOIN gate_events e ON s.session_id = e.session_id
WHERE s.status = 'completed'
GROUP BY s.session_id
ORDER BY s.end_time DESC;

CREATE OR REPLACE VIEW v_daily_stats AS
SELECT 
    DATE(to_timestamp(start_time)) as date,
    gate_id,
    COUNT(*) as total_checks,
    AVG(score) as avg_score,
    AVG(visitor_dwell_time) as avg_dwell_time,
    AVG(interaction_duration) as avg_interaction_time
FROM gate_sessions
WHERE status = 'completed'
GROUP BY DATE(to_timestamp(start_time)), gate_id
ORDER BY date DESC;

-- Insert sample configuration
INSERT INTO camera_sources (camera_id, camera_name, source_url, location, status) VALUES
('gate_a1_main', 'Gate A1 Main Camera', 'rtsp://mediamtx:8554/gate_a1', 'Gate A1', 'active'),
('gate_a1_backup', 'Gate A1 Backup Camera', 'rtsp://mediamtx:8554/gate_a1_backup', 'Gate A1', 'active'),
('webcam_0', 'Development Webcam', 'webcam:0', 'Development', 'active')
ON CONFLICT (camera_id) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO verolux;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO verolux;

-- Vacuum and analyze
VACUUM ANALYZE;






















