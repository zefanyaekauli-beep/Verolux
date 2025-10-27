import React, { useState, useEffect, useRef } from 'react';
import { Stage, Layer, Line, Circle, Rect, Text, Group } from 'react-konva';
import './GateConfigEditor.css';

const GateConfigEditor = () => {
  const stageRef = useRef(null);
  const layerRef = useRef(null);
  
  // Canvas dimensions
  const [canvasSize, setCanvasSize] = useState({ width: 800, height: 600 });
  
  // Configuration state
  const [config, setConfig] = useState({
    gateArea: {
      points: [
        { x: 0.30, y: 0.20 },
        { x: 0.70, y: 0.20 },
        { x: 0.70, y: 0.80 },
        { x: 0.30, y: 0.80 }
      ]
    },
    guardAnchor: {
      points: [
        { x: 0.10, y: 0.15 },
        { x: 0.25, y: 0.15 },
        { x: 0.25, y: 0.85 },
        { x: 0.10, y: 0.85 }
      ]
    },
    settings: {
      personMinDwell: 6.0,
      guardMinDwell: 3.0,
      interactionMinOverlap: 1.2,
      proximityScale: 0.35,
      scoreThreshold: 0.9
    }
  });
  
  // Editor state
  const [selectedZone, setSelectedZone] = useState('gateArea');
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [cameraFeed, setCameraFeed] = useState(null);

  // Convert normalized coordinates to pixel coordinates
  const normalizedToPixel = (point) => ({
    x: point.x * canvasSize.width,
    y: point.y * canvasSize.height
  });

  // Convert pixel coordinates to normalized coordinates
  const pixelToNormalized = (point) => ({
    x: point.x / canvasSize.width,
    y: point.y / canvasSize.height
  });

  // Load configuration from backend
  useEffect(() => {
    loadConfiguration();
  }, []);

  const loadConfiguration = async () => {
    try {
      // Load gate area polygon
      const gateResponse = await fetch('/api/config/gate-area');
      const gateData = await gateResponse.json();
      
      // Load guard anchor polygon
      const guardResponse = await fetch('/api/config/guard-anchor');
      const guardData = await guardResponse.json();
      
      // Load main configuration
      const configResponse = await fetch('/api/config/gate-rules');
      const configData = await configResponse.json();
      
      setConfig({
        gateArea: {
          points: gateData.polygon.map(([x, y]) => ({ x, y }))
        },
        guardAnchor: {
          points: guardData.polygon.map(([x, y]) => ({ x, y }))
        },
        settings: {
          personMinDwell: configData.timers?.person_min_dwell_s || 6.0,
          guardMinDwell: configData.timers?.guard_min_dwell_s || 3.0,
          interactionMinOverlap: configData.timers?.interaction_min_overlap_s || 1.2,
          proximityScale: configData.proximity?.center_dist_scale || 0.35,
          scoreThreshold: configData.scoring?.threshold || 0.9
        }
      });
    } catch (error) {
      console.error('Failed to load configuration:', error);
    }
  };

  // Save configuration to backend
  const saveConfiguration = async () => {
    try {
      // Save gate area polygon
      await fetch('/api/config/gate-area', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          polygon: config.gateArea.points.map(p => [p.x, p.y])
        })
      });
      
      // Save guard anchor polygon
      await fetch('/api/config/guard-anchor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          polygon: config.guardAnchor.points.map(p => [p.x, p.y])
        })
      });
      
      // Save main configuration
      await fetch('/api/config/gate-rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          timers: {
            person_min_dwell_s: config.settings.personMinDwell,
            guard_min_dwell_s: config.settings.guardMinDwell,
            interaction_min_overlap_s: config.settings.interactionMinOverlap
          },
          proximity: {
            center_dist_scale: config.settings.proximityScale
          },
          scoring: {
            threshold: config.settings.scoreThreshold
          }
        })
      });
      
      alert('Configuration saved successfully!');
    } catch (error) {
      console.error('Failed to save configuration:', error);
      alert('Failed to save configuration');
    }
  };

  // Handle stage click for adding points
  const handleStageClick = (e) => {
    if (!isDrawing) return;
    
    const stage = stageRef.current;
    const pointerPosition = stage.getPointerPosition();
    const normalizedPos = pixelToNormalized(pointerPosition);
    
    const newConfig = { ...config };
    newConfig[selectedZone].points.push(normalizedPos);
    setConfig(newConfig);
  };

  // Handle point drag
  const handlePointDrag = (zone, pointIndex, e) => {
    const stage = stageRef.current;
    const pointerPosition = stage.getPointerPosition();
    const normalizedPos = pixelToNormalized(pointerPosition);
    
    const newConfig = { ...config };
    newConfig[zone].points[pointIndex] = normalizedPos;
    setConfig(newConfig);
  };

  // Delete point
  const deletePoint = (zone, pointIndex) => {
    const newConfig = { ...config };
    newConfig[zone].points.splice(pointIndex, 1);
    setConfig(newConfig);
  };

  // Reset to default
  const resetToDefault = () => {
    setConfig({
      gateArea: {
        points: [
          { x: 0.30, y: 0.20 },
          { x: 0.70, y: 0.20 },
          { x: 0.70, y: 0.80 },
          { x: 0.30, y: 0.80 }
        ]
      },
      guardAnchor: {
        points: [
          { x: 0.10, y: 0.15 },
          { x: 0.25, y: 0.15 },
          { x: 0.25, y: 0.85 },
          { x: 0.10, y: 0.85 }
        ]
      },
      settings: {
        personMinDwell: 6.0,
        guardMinDwell: 3.0,
        interactionMinOverlap: 1.2,
        proximityScale: 0.35,
        scoreThreshold: 0.9
      }
    });
  };

  // Render polygon with points
  const renderPolygon = (zone, color, strokeColor) => {
    const points = config[zone].points;
    const pixelPoints = points.flatMap(point => {
      const pixel = normalizedToPixel(point);
      return [pixel.x, pixel.y];
    });

    return (
      <Group key={zone}>
        {/* Polygon outline */}
        <Line
          points={pixelPoints}
          closed
          stroke={strokeColor}
          strokeWidth={3}
          fill={color}
          opacity={0.3}
          dash={[10, 5]}
        />
        
        {/* Corner points */}
        {points.map((point, index) => {
          const pixel = normalizedToPixel(point);
          return (
            <Circle
              key={index}
              x={pixel.x}
              y={pixel.y}
              radius={8}
              fill={strokeColor}
              stroke="white"
              strokeWidth={2}
              draggable
              onDragMove={(e) => handlePointDrag(zone, index, e)}
              onClick={() => setSelectedPoint({ zone, index })}
              onMouseEnter={(e) => {
                e.target.scale({ x: 1.2, y: 1.2 });
                document.body.style.cursor = 'pointer';
              }}
              onMouseLeave={(e) => {
                e.target.scale({ x: 1, y: 1 });
                document.body.style.cursor = 'default';
              }}
            />
          );
        })}
        
        {/* Zone label */}
        <Text
          x={normalizedToPixel(points[0]).x + 10}
          y={normalizedToPixel(points[0]).y - 10}
          text={zone === 'gateArea' ? 'Gate Area' : 'Guard Anchor'}
          fontSize={16}
          fontStyle="bold"
          fill={strokeColor}
        />
      </Group>
    );
  };

  return (
    <div className="gate-config-editor">
      <div className="editor-header">
        <h2>🚪 Gate Security Configuration Editor</h2>
        <div className="controls">
          <button 
            onClick={() => setIsDrawing(!isDrawing)}
            className={isDrawing ? 'btn btn-danger' : 'btn btn-primary'}
          >
            {isDrawing ? 'Stop Drawing' : 'Start Drawing'}
          </button>
          <button onClick={saveConfiguration} className="btn btn-success">
            💾 Save Configuration
          </button>
          <button onClick={loadConfiguration} className="btn btn-info">
            📂 Load Configuration
          </button>
          <button onClick={resetToDefault} className="btn btn-warning">
            🔄 Reset to Default
          </button>
        </div>
      </div>

      <div className="editor-container">
        {/* Zone Selection */}
        <div className="zone-selector">
          <label>
            <input
              type="radio"
              value="gateArea"
              checked={selectedZone === 'gateArea'}
              onChange={(e) => setSelectedZone(e.target.value)}
            />
            Gate Area (Where security check happens)
          </label>
          <label>
            <input
              type="radio"
              value="guardAnchor"
              checked={selectedZone === 'guardAnchor'}
              onChange={(e) => setSelectedZone(e.target.value)}
            />
            Guard Anchor (Where guard must stand)
          </label>
        </div>

        {/* Canvas */}
        <div className="canvas-container">
          <div className="canvas-info">
            <p>📐 Click to add points • Drag to move points • {isDrawing ? 'Drawing Mode ON' : 'Drawing Mode OFF'}</p>
          </div>
          
          <Stage
            ref={stageRef}
            width={canvasSize.width}
            height={canvasSize.height}
            onClick={handleStageClick}
            style={{ border: '2px solid #333', backgroundColor: '#f0f0f0' }}
          >
            <Layer ref={layerRef}>
              {/* Camera feed background (if available) */}
              {cameraFeed && (
                <Rect
                  width={canvasSize.width}
                  height={canvasSize.height}
                  fillPatternImage={cameraFeed}
                />
              )}
              
              {/* Grid */}
              {Array.from({ length: 10 }, (_, i) => (
                <React.Fragment key={i}>
                  <Line
                    points={[i * canvasSize.width / 10, 0, i * canvasSize.width / 10, canvasSize.height]}
                    stroke="#ddd"
                    strokeWidth={1}
                  />
                  <Line
                    points={[0, i * canvasSize.height / 10, canvasSize.width, i * canvasSize.height / 10]}
                    stroke="#ddd"
                    strokeWidth={1}
                  />
                </React.Fragment>
              ))}
              
              {/* Render polygons */}
              {renderPolygon('gateArea', 'rgba(0, 255, 0, 0.3)', '#00aa00')}
              {renderPolygon('guardAnchor', 'rgba(255, 0, 0, 0.3)', '#aa0000')}
            </Layer>
          </Stage>
        </div>

        {/* Settings Panel */}
        <div className="settings-panel">
          <h3>⚙️ Configuration Settings</h3>
          
          <div className="setting-group">
            <h4>⏱️ Timer Settings</h4>
            <div className="setting-item">
              <label>Person Min Dwell (seconds):</label>
              <input
                type="number"
                value={config.settings.personMinDwell}
                onChange={(e) => setConfig({
                  ...config,
                  settings: { ...config.settings, personMinDwell: parseFloat(e.target.value) }
                })}
                step="0.1"
                min="0"
                max="30"
              />
            </div>
            
            <div className="setting-item">
              <label>Guard Min Dwell (seconds):</label>
              <input
                type="number"
                value={config.settings.guardMinDwell}
                onChange={(e) => setConfig({
                  ...config,
                  settings: { ...config.settings, guardMinDwell: parseFloat(e.target.value) }
                })}
                step="0.1"
                min="0"
                max="30"
              />
            </div>
            
            <div className="setting-item">
              <label>Min Interaction Time (seconds):</label>
              <input
                type="number"
                value={config.settings.interactionMinOverlap}
                onChange={(e) => setConfig({
                  ...config,
                  settings: { ...config.settings, interactionMinOverlap: parseFloat(e.target.value) }
                })}
                step="0.1"
                min="0"
                max="10"
              />
            </div>
          </div>
          
          <div className="setting-group">
            <h4>📏 Proximity Settings</h4>
            <div className="setting-item">
              <label>Proximity Scale (0.1-1.0):</label>
              <input
                type="number"
                value={config.settings.proximityScale}
                onChange={(e) => setConfig({
                  ...config,
                  settings: { ...config.settings, proximityScale: parseFloat(e.target.value) }
                })}
                step="0.05"
                min="0.1"
                max="1.0"
              />
            </div>
          </div>
          
          <div className="setting-group">
            <h4>🎯 Scoring Settings</h4>
            <div className="setting-item">
              <label>Score Threshold (0.0-1.0):</label>
              <input
                type="number"
                value={config.settings.scoreThreshold}
                onChange={(e) => setConfig({
                  ...config,
                  settings: { ...config.settings, scoreThreshold: parseFloat(e.target.value) }
                })}
                step="0.05"
                min="0.0"
                max="1.0"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Coordinate Display */}
      <div className="coordinate-display">
        <h4>📊 Current Configuration</h4>
        <div className="coord-section">
          <h5>Gate Area Points:</h5>
          <pre>{JSON.stringify(config.gateArea.points.map(p => [p.x.toFixed(3), p.y.toFixed(3)]), null, 2)}</pre>
        </div>
        <div className="coord-section">
          <h5>Guard Anchor Points:</h5>
          <pre>{JSON.stringify(config.guardAnchor.points.map(p => [p.x.toFixed(3), p.y.toFixed(3)]), null, 2)}</pre>
        </div>
      </div>
    </div>
  );
};

export default GateConfigEditor;
