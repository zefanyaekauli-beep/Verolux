import React, { useState, useEffect } from 'react';

const GateBoxConfig = ({ onConfigChange, initialConfig = null }) => {
  const [config, setConfig] = useState({
    gateArea: {
      x1: 0.3, y1: 0.2,
      x2: 0.7, y2: 0.8
    },
    guardAnchor: {
      x1: 0.1, y1: 0.15,
      x2: 0.25, y2: 0.85
    },
    settings: {
      personMinDwell: 6.0,
      guardMinDwell: 3.0,
      interactionMinOverlap: 1.2,
      proximityScale: 0.35,
      scoreThreshold: 0.9
    }
  });

  const [isVisible, setIsVisible] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  // Load configuration on mount
  useEffect(() => {
    if (initialConfig) {
      setConfig(initialConfig);
    } else {
      loadConfiguration();
    }
  }, [initialConfig]);

  const loadConfiguration = async () => {
    try {
      const response = await fetch('/api/config/gate-rules');
      const data = await response.json();
      
      if (data.gate_area) {
        setConfig(prev => ({
          ...prev,
          gateArea: {
            x1: data.gate_area.x1 || 0.3,
            y1: data.gate_area.y1 || 0.2,
            x2: data.gate_area.x2 || 0.7,
            y2: data.gate_area.y2 || 0.8
          }
        }));
      }
      
      if (data.guard_anchor) {
        setConfig(prev => ({
          ...prev,
          guardAnchor: {
            x1: data.guard_anchor.x1 || 0.1,
            y1: data.guard_anchor.y1 || 0.15,
            x2: data.guard_anchor.x2 || 0.25,
            y2: data.guard_anchor.y2 || 0.85
          }
        }));
      }
    } catch (error) {
      console.error('Failed to load gate configuration:', error);
    }
  };

  const saveConfiguration = async () => {
    try {
      // Save gate area
      await fetch('/api/config/gate-area', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          polygon: [
            [config.gateArea.x1, config.gateArea.y1],
            [config.gateArea.x2, config.gateArea.y1],
            [config.gateArea.x2, config.gateArea.y2],
            [config.gateArea.x1, config.gateArea.y2]
          ]
        })
      });

      // Save guard anchor
      await fetch('/api/config/guard-anchor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          polygon: [
            [config.guardAnchor.x1, config.guardAnchor.y1],
            [config.guardAnchor.x2, config.guardAnchor.y1],
            [config.guardAnchor.x2, config.guardAnchor.y2],
            [config.guardAnchor.x1, config.guardAnchor.y2]
          ]
        })
      });

      // Save settings
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

      if (onConfigChange) {
        onConfigChange(config);
      }
      
      alert('Gate configuration saved successfully!');
    } catch (error) {
      console.error('Failed to save configuration:', error);
      alert('Failed to save configuration');
    }
  };

  const updateConfig = (section, field, value) => {
    setConfig(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: parseFloat(value) || 0
      }
    }));
  };

  if (!isVisible) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          background: 'rgba(0, 0, 0, 0.8)',
          color: 'white',
          border: '1px solid rgba(255, 255, 255, 0.3)',
          borderRadius: '6px',
          padding: '8px 12px',
          cursor: 'pointer',
          fontSize: '12px',
          zIndex: 1000
        }}
      >
        ⚙️ Gate Config
      </button>
    );
  }

  return (
    <div style={{
      position: 'absolute',
      top: '10px',
      right: '10px',
      background: 'rgba(0, 0, 0, 0.9)',
      color: 'white',
      border: '1px solid rgba(255, 255, 255, 0.3)',
      borderRadius: '8px',
      padding: '16px',
      minWidth: '300px',
      zIndex: 1000,
      backdropFilter: 'blur(10px)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ margin: 0, fontSize: '16px' }}>🚪 Gate Configuration</h3>
        <button
          onClick={() => setIsVisible(false)}
          style={{
            background: 'none',
            border: 'none',
            color: 'white',
            cursor: 'pointer',
            fontSize: '18px'
          }}
        >
          ×
        </button>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold' }}>
          Gate Area (Security Check Zone)
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc' }}>X1 (Left)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.gateArea.x1}
              onChange={(e) => updateConfig('gateArea', 'x1', e.target.value)}
              style={{
                width: '100%',
                padding: '4px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '4px',
                color: 'white',
                fontSize: '12px'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc' }}>Y1 (Top)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.gateArea.y1}
              onChange={(e) => updateConfig('gateArea', 'y1', e.target.value)}
              style={{
                width: '100%',
                padding: '4px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '4px',
                color: 'white',
                fontSize: '12px'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc' }}>X2 (Right)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.gateArea.x2}
              onChange={(e) => updateConfig('gateArea', 'x2', e.target.value)}
              style={{
                width: '100%',
                padding: '4px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '4px',
                color: 'white',
                fontSize: '12px'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc' }}>Y2 (Bottom)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.gateArea.y2}
              onChange={(e) => updateConfig('gateArea', 'y2', e.target.value)}
              style={{
                width: '100%',
                padding: '4px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '4px',
                color: 'white',
                fontSize: '12px'
              }}
            />
          </div>
        </div>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold' }}>
          Guard Anchor (Guard Position)
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc' }}>X1 (Left)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.guardAnchor.x1}
              onChange={(e) => updateConfig('guardAnchor', 'x1', e.target.value)}
              style={{
                width: '100%',
                padding: '4px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '4px',
                color: 'white',
                fontSize: '12px'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc' }}>Y1 (Top)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.guardAnchor.y1}
              onChange={(e) => updateConfig('guardAnchor', 'y1', e.target.value)}
              style={{
                width: '100%',
                padding: '4px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '4px',
                color: 'white',
                fontSize: '12px'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc' }}>X2 (Right)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.guardAnchor.x2}
              onChange={(e) => updateConfig('guardAnchor', 'x2', e.target.value)}
              style={{
                width: '100%',
                padding: '4px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '4px',
                color: 'white',
                fontSize: '12px'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc' }}>Y2 (Bottom)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.guardAnchor.y2}
              onChange={(e) => updateConfig('guardAnchor', 'y2', e.target.value)}
              style={{
                width: '100%',
                padding: '4px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '4px',
                color: 'white',
                fontSize: '12px'
              }}
            />
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '8px' }}>
        <button
          onClick={saveConfiguration}
          style={{
            flex: 1,
            background: 'rgba(40, 167, 69, 0.8)',
            border: '1px solid rgba(40, 167, 69, 0.5)',
            borderRadius: '6px',
            padding: '8px 12px',
            color: 'white',
            cursor: 'pointer',
            fontSize: '12px',
            fontWeight: 'bold'
          }}
        >
          💾 Save
        </button>
        <button
          onClick={loadConfiguration}
          style={{
            flex: 1,
            background: 'rgba(23, 162, 184, 0.8)',
            border: '1px solid rgba(23, 162, 184, 0.5)',
            borderRadius: '6px',
            padding: '8px 12px',
            color: 'white',
            cursor: 'pointer',
            fontSize: '12px',
            fontWeight: 'bold'
          }}
        >
          📂 Load
        </button>
      </div>
    </div>
  );
};

export default GateBoxConfig;








