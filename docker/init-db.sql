-- Initialize Verolux Database

-- Create gate security tables
CREATE TABLE IF NOT EXISTS gate_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    gate_id VARCHAR(50),
    visitor_track_id INTEGER,
    guard_track_id INTEGER,
    start_time FLOAT,
    end_time FLOAT,
    score FLOAT,
    visitor_dwell_time FLOAT,
    interaction_duration FLOAT,
    status VARCHAR(50),
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS gate_events (
    event_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES gate_sessions(session_id),
    timestamp FLOAT,
    event_type VARCHAR(100),
    track_id INTEGER,
    data JSONB
);

CREATE TABLE IF NOT EXISTS detections (
    id SERIAL PRIMARY KEY,
    timestamp FLOAT,
    camera_id VARCHAR(100),
    object_class VARCHAR(100),
    confidence FLOAT,
    bbox JSONB,
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    timestamp FLOAT,
    metric_name VARCHAR(100),
    metric_value FLOAT,
    metadata JSONB
);

-- Create indexes
CREATE INDEX idx_gate_sessions_gate_id ON gate_sessions(gate_id);
CREATE INDEX idx_gate_sessions_start_time ON gate_sessions(start_time);
CREATE INDEX idx_gate_events_session_id ON gate_events(session_id);
CREATE INDEX idx_gate_events_timestamp ON gate_events(timestamp);
CREATE INDEX idx_detections_timestamp ON detections(timestamp);
CREATE INDEX idx_detections_camera_id ON detections(camera_id);
CREATE INDEX idx_analytics_timestamp ON analytics(timestamp);

-- Insert sample data
INSERT INTO gate_sessions (session_id, gate_id, status, start_time) 
VALUES ('sample_123', 'A1', 'active', EXTRACT(EPOCH FROM NOW()));






















