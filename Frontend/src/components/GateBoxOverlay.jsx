import React, { useState, useEffect } from 'react';

const GateBoxOverlay = ({ onConfigChange, isVisible, onToggle }) => {
  const [config, setConfig] = useState({
    gateArea: {
      x1: 0.3, y1: 0.2,
      x2: 0.7, y2: 0.8
    },
    guardAnchor: {
      x1: 0.1, y1: 0.15,
      x2: 0.25, y2: 0.85
    }
  });

  const [isEditing, setIsEditing] = useState(false);

  // Load configuration on mount
  useEffect(() => {
    loadConfiguration();
  }, []);

  const loadConfiguration = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8002/config/gate');
      const data = await response.json();
      
      if (data.gate_area) {
        setConfig(prev => ({
          ...prev,
          gateArea: {
            x1: data.gate_area.x || 0.3,
            y1: data.gate_area.y || 0.2,
            x2: (data.gate_area.x || 0.3) + (data.gate_area.width || 0.4),
            y2: (data.gate_area.y || 0.2) + (data.gate_area.height || 0.6)
          }
        }));
      }
      
      if (data.guard_anchor) {
        setConfig(prev => ({
          ...prev,
          guardAnchor: {
            x1: data.guard_anchor.x || 0.1,
            y1: data.guard_anchor.y || 0.15,
            x2: (data.guard_anchor.x || 0.1) + (data.guard_anchor.width || 0.15),
            y2: (data.guard_anchor.y || 0.15) + (data.guard_anchor.height || 0.7)
          }
        }));
      }
    } catch (error) {
      console.error('Failed to load gate configuration:', error);
    }
  };

  const saveConfiguration = async () => {
    try {
      // Convert x1,y1,x2,y2 format to x,y,width,height format
      const gateAreaConfig = {
        x: config.gateArea.x1,
        y: config.gateArea.y1,
        width: config.gateArea.x2 - config.gateArea.x1,
        height: config.gateArea.y2 - config.gateArea.y1
      };
      
      const guardAnchorConfig = {
        x: config.guardAnchor.x1,
        y: config.guardAnchor.y1,
        width: config.guardAnchor.x2 - config.guardAnchor.x1,
        height: config.guardAnchor.y2 - config.guardAnchor.y1
      };

      await fetch('http://127.0.0.1:8002/config/gate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gate_area: gateAreaConfig,
          guard_anchor: guardAnchorConfig,
          enabled: true
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

  if (!isVisible) {
    return (
      <button
        onClick={onToggle}
        style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          padding: '12px 16px',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: 'bold',
          zIndex: 1000,
          boxShadow: '0 4px 15px rgba(0,0,0,0.3)',
          transition: 'all 0.3s ease'
        }}
        onMouseOver={(e) => {
          e.target.style.transform = 'scale(1.05)';
          e.target.style.boxShadow = '0 6px 20px rgba(0,0,0,0.4)';
        }}
        onMouseOut={(e) => {
          e.target.style.transform = 'scale(1)';
          e.target.style.boxShadow = '0 4px 15px rgba(0,0,0,0.3)';
        }}
      >
        🚪 Gate Configuration
      </button>
    );
  }

  return (
    <div 
      data-gate-config
      style={{
        position: 'absolute',
        top: '10px',
        right: '10px',
        background: 'rgba(0, 0, 0, 0.95)',
        color: 'white',
        border: '2px solid #667eea',
        borderRadius: '12px',
        padding: '20px',
        minWidth: '350px',
        zIndex: 1000,
        backdropFilter: 'blur(15px)',
        boxShadow: '0 10px 30px rgba(0,0,0,0.5)'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 style={{ margin: 0, fontSize: '18px', color: '#667eea', fontWeight: 'bold' }}>
          🚪 Gate Security Configuration
        </h3>
        <button
          onClick={onToggle}
          style={{
            background: 'rgba(255, 255, 255, 0.1)',
            border: 'none',
            color: 'white',
            cursor: 'pointer',
            fontSize: '20px',
            padding: '5px 10px',
            borderRadius: '6px'
          }}
        >
          ×
        </button>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '10px', fontSize: '16px', fontWeight: 'bold', color: '#00ff88' }}>
          🎯 Gate Area (Security Check Zone)
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc', display: 'block', marginBottom: '5px' }}>X1 (Left)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.gateArea.x1}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                gateArea: { ...prev.gateArea, x1: parseFloat(e.target.value) || 0 }
              }))}
              style={{
                width: '100%',
                padding: '8px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(0, 255, 136, 0.3)',
                borderRadius: '6px',
                color: 'white',
                fontSize: '14px'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc', display: 'block', marginBottom: '5px' }}>Y1 (Top)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.gateArea.y1}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                gateArea: { ...prev.gateArea, y1: parseFloat(e.target.value) || 0 }
              }))}
              style={{
                width: '100%',
                padding: '8px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(0, 255, 136, 0.3)',
                borderRadius: '6px',
                color: 'white',
                fontSize: '14px'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc', display: 'block', marginBottom: '5px' }}>X2 (Right)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.gateArea.x2}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                gateArea: { ...prev.gateArea, x2: parseFloat(e.target.value) || 0 }
              }))}
              style={{
                width: '100%',
                padding: '8px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(0, 255, 136, 0.3)',
                borderRadius: '6px',
                color: 'white',
                fontSize: '14px'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc', display: 'block', marginBottom: '5px' }}>Y2 (Bottom)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.gateArea.y2}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                gateArea: { ...prev.gateArea, y2: parseFloat(e.target.value) || 0 }
              }))}
              style={{
                width: '100%',
                padding: '8px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(0, 255, 136, 0.3)',
                borderRadius: '6px',
                color: 'white',
                fontSize: '14px'
              }}
            />
          </div>
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '10px', fontSize: '16px', fontWeight: 'bold', color: '#ff6b6b' }}>
          👮 Guard Anchor (Guard Position)
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc', display: 'block', marginBottom: '5px' }}>X1 (Left)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.guardAnchor.x1}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                guardAnchor: { ...prev.guardAnchor, x1: parseFloat(e.target.value) || 0 }
              }))}
              style={{
                width: '100%',
                padding: '8px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 107, 107, 0.3)',
                borderRadius: '6px',
                color: 'white',
                fontSize: '14px'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc', display: 'block', marginBottom: '5px' }}>Y1 (Top)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.guardAnchor.y1}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                guardAnchor: { ...prev.guardAnchor, y1: parseFloat(e.target.value) || 0 }
              }))}
              style={{
                width: '100%',
                padding: '8px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 107, 107, 0.3)',
                borderRadius: '6px',
                color: 'white',
                fontSize: '14px'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc', display: 'block', marginBottom: '5px' }}>X2 (Right)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.guardAnchor.x2}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                guardAnchor: { ...prev.guardAnchor, x2: parseFloat(e.target.value) || 0 }
              }))}
              style={{
                width: '100%',
                padding: '8px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 107, 107, 0.3)',
                borderRadius: '6px',
                color: 'white',
                fontSize: '14px'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: '#ccc', display: 'block', marginBottom: '5px' }}>Y2 (Bottom)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={config.guardAnchor.y2}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                guardAnchor: { ...prev.guardAnchor, y2: parseFloat(e.target.value) || 0 }
              }))}
              style={{
                width: '100%',
                padding: '8px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 107, 107, 0.3)',
                borderRadius: '6px',
                color: 'white',
                fontSize: '14px'
              }}
            />
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '10px' }}>
        <button
          onClick={saveConfiguration}
          style={{
            flex: 1,
            background: 'linear-gradient(135deg, #00ff88 0%, #00cc6a 100%)',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 16px',
            color: 'white',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 'bold',
            transition: 'all 0.3s ease'
          }}
          onMouseOver={(e) => {
            e.target.style.transform = 'scale(1.05)';
            e.target.style.boxShadow = '0 4px 15px rgba(0, 255, 136, 0.4)';
          }}
          onMouseOut={(e) => {
            e.target.style.transform = 'scale(1)';
            e.target.style.boxShadow = 'none';
          }}
        >
          💾 Save Configuration
        </button>
        <button
          onClick={loadConfiguration}
          style={{
            flex: 1,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 16px',
            color: 'white',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 'bold',
            transition: 'all 0.3s ease'
          }}
          onMouseOver={(e) => {
            e.target.style.transform = 'scale(1.05)';
            e.target.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)';
          }}
          onMouseOut={(e) => {
            e.target.style.transform = 'scale(1)';
            e.target.style.boxShadow = 'none';
          }}
        >
          📂 Load Configuration
        </button>
      </div>
    </div>
  );
};

export default GateBoxOverlay;
