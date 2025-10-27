import React, { useState, useEffect, useRef } from 'react';
import './LiveZoneEditor.css';

const LiveZoneEditor = ({ 
  videoRef, 
  canvasRef, 
  isActive = false, 
  onSave, 
  onCancel,
  initialZones = {
    gateArea: { points: [{ x: 0.3, y: 0.2 }, { x: 0.7, y: 0.2 }, { x: 0.7, y: 0.8 }, { x: 0.3, y: 0.8 }] },
    guardAnchor: { points: [{ x: 0.1, y: 0.15 }, { x: 0.25, y: 0.15 }, { x: 0.25, y: 0.85 }, { x: 0.1, y: 0.85 }] }
  }
}) => {
  const [zones, setZones] = useState(initialZones);
  const [selectedZone, setSelectedZone] = useState('gateArea');
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [showInstructions, setShowInstructions] = useState(true);
  const [videoRect, setVideoRect] = useState({ x: 0, y: 0, width: 0, height: 0 });
  
  const overlayRef = useRef(null);
  const isDragging = useRef(false);

  // Update video dimensions when video loads or resizes
  useEffect(() => {
    if (!videoRef?.current || !isActive) return;

    const updateVideoRect = () => {
      const rect = videoRef.current.getBoundingClientRect();
      setVideoRect(rect);
    };

    updateVideoRect();
    window.addEventListener('resize', updateVideoRect);
    
    return () => window.removeEventListener('resize', updateVideoRect);
  }, [videoRef, isActive]);

  // Convert normalized coordinates to screen coordinates
  const normalizedToScreen = (point) => ({
    x: point.x * videoRect.width + videoRect.x,
    y: point.y * videoRect.height + videoRect.y
  });

  // Convert screen coordinates to normalized coordinates
  const screenToNormalized = (point) => ({
    x: (point.x - videoRect.x) / videoRect.width,
    y: (point.y - videoRect.y) / videoRect.height
  });

  // Handle mouse events on the overlay
  const handleMouseDown = (e) => {
    if (!isDrawing) return;

    const rect = overlayRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Convert to normalized coordinates
    const normalizedPoint = screenToNormalized({ x: x + videoRect.x, y: y + videoRect.y });
    
    // Add new point to selected zone
    const newZones = { ...zones };
    newZones[selectedZone].points.push(normalizedPoint);
    setZones(newZones);
  };

  // Handle point dragging
  const handlePointMouseDown = (zoneName, pointIndex, e) => {
    e.stopPropagation();
    setSelectedPoint({ zone: zoneName, index: pointIndex });
    isDragging.current = true;
  };

  const handleMouseMove = (e) => {
    if (!isDragging.current || !selectedPoint) return;

    const rect = overlayRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Convert to normalized coordinates
    const normalizedPoint = screenToNormalized({ x: x + videoRect.x, y: y + videoRect.y });
    
    // Update the point
    const newZones = { ...zones };
    newZones[selectedPoint.zone].points[selectedPoint.index] = normalizedPoint;
    setZones(newZones);
  };

  const handleMouseUp = () => {
    isDragging.current = false;
    setSelectedPoint(null);
  };

  // Render zone polygon
  const renderZone = (zoneName, color, strokeColor) => {
    const points = zones[zoneName].points;
    if (points.length < 2) return null;

    const screenPoints = points.map(point => normalizedToScreen(point));
    
    return (
      <g key={zoneName}>
        {/* Polygon outline */}
        <polygon
          points={screenPoints.map(p => `${p.x - videoRect.x},${p.y - videoRect.y}`).join(' ')}
          fill={color}
          stroke={strokeColor}
          strokeWidth="3"
          fillOpacity="0.3"
          strokeDasharray="10,5"
        />
        
        {/* Corner points */}
        {points.map((point, index) => {
          const screenPoint = normalizedToScreen(point);
          return (
            <circle
              key={index}
              cx={screenPoint.x - videoRect.x}
              cy={screenPoint.y - videoRect.y}
              r="8"
              fill={strokeColor}
              stroke="white"
              strokeWidth="2"
              style={{ cursor: 'pointer' }}
              onMouseDown={(e) => handlePointMouseDown(zoneName, index, e)}
            />
          );
        })}
        
        {/* Zone label */}
        <text
          x={screenPoints[0].x - videoRect.x + 10}
          y={screenPoints[0].y - videoRect.y - 10}
          fill={strokeColor}
          fontSize="16"
          fontWeight="bold"
        >
          {zoneName === 'gateArea' ? 'Gate Area' : 'Guard Anchor'}
        </text>
      </g>
    );
  };

  // Save configuration
  const handleSave = async () => {
    try {
      await fetch('/api/config/gate-area', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          polygon: zones.gateArea.points.map(p => [p.x, p.y])
        })
      });

      await fetch('/api/config/guard-anchor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          polygon: zones.guardAnchor.points.map(p => [p.x, p.y])
        })
      });

      onSave?.(zones);
    } catch (error) {
      console.error('Failed to save zones:', error);
      alert('Failed to save configuration');
    }
  };

  if (!isActive || videoRect.width === 0) return null;

  return (
    <div className="live-zone-editor">
      {/* Overlay Controls */}
      <div className="zone-editor-controls">
        <div className="zone-selector">
          <label>
            <input
              type="radio"
              value="gateArea"
              checked={selectedZone === 'gateArea'}
              onChange={(e) => setSelectedZone(e.target.value)}
            />
            Gate Area
          </label>
          <label>
            <input
              type="radio"
              value="guardAnchor"
              checked={selectedZone === 'guardAnchor'}
              onChange={(e) => setSelectedZone(e.target.value)}
            />
            Guard Anchor
          </label>
        </div>
        
        <div className="editor-buttons">
          <button
            onClick={() => setIsDrawing(!isDrawing)}
            className={`btn ${isDrawing ? 'btn-danger' : 'btn-primary'}`}
          >
            {isDrawing ? 'Stop Drawing' : 'Start Drawing'}
          </button>
          <button onClick={handleSave} className="btn btn-success">
            Save
          </button>
          <button onClick={onCancel} className="btn btn-secondary">
            Cancel
          </button>
        </div>
      </div>

      {/* Overlay SVG */}
      <svg
        ref={overlayRef}
        className="zone-overlay"
        width={videoRect.width}
        height={videoRect.height}
        style={{
          position: 'fixed',
          left: videoRect.x,
          top: videoRect.y,
          pointerEvents: isDrawing ? 'all' : 'none',
          zIndex: 1000,
          backgroundColor: 'transparent'
        }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
        {renderZone('gateArea', 'rgba(0, 255, 0, 0.3)', '#00aa00')}
        {renderZone('guardAnchor', 'rgba(255, 0, 0, 0.3)', '#aa0000')}
      </svg>

      {/* Instructions */}
      {isDrawing && showInstructions && (
        <div className="drawing-instructions">
          <div className="instruction-content">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <h3 style={{ margin: 0 }}>🎯 Zone Editor Active</h3>
              <button 
                onClick={() => setShowInstructions(false)}
                style={{
                  background: 'rgba(255, 255, 255, 0.2)',
                  border: 'none',
                  color: 'white',
                  borderRadius: '50%',
                  width: '30px',
                  height: '30px',
                  cursor: 'pointer',
                  fontSize: '18px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                ×
              </button>
            </div>
            <p>Click to add points to the {selectedZone === 'gateArea' ? 'Gate Area' : 'Guard Anchor'} zone</p>
            <p>Drag existing points to move them</p>
            <p>Click "Stop Drawing" when finished</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LiveZoneEditor;












