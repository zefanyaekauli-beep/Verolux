import React, { useState, useEffect, useRef } from 'react'
import { Stage, Layer, Line, Circle, Rect, Image as KonvaImage } from 'react-konva'
import { Video, Camera, Save, Download, Upload, RotateCcw, Play, Pause, Square } from 'lucide-react'

export default function GateConfigEditorLive() {
  const videoRef = useRef(null)
  const stageRef = useRef(null)
  const layerRef = useRef(null)
  const imgRef = useRef(null)
  const [videoImage, setVideoImage] = useState(null)
  const [canvasSize, setCanvasSize] = useState({ width: 800, height: 600 })
  const [isLive, setIsLive] = useState(false)
  const [videoSource, setVideoSource] = useState('webcam:0')
  
  // Zone configuration
  const [zones, setZones] = useState({
    gateArea: {
      points: [
        { x: 0.30, y: 0.20 },
        { x: 0.70, y: 0.20 },
        { x: 0.70, y: 0.80 },
        { x: 0.30, y: 0.80 }
      ],
      color: 'rgba(0, 255, 136, 0.3)',
      strokeColor: '#00ff88',
      label: 'Gate Area'
    },
    guardAnchor: {
      points: [
        { x: 0.10, y: 0.15 },
        { x: 0.25, y: 0.15 },
        { x: 0.25, y: 0.85 },
        { x: 0.10, y: 0.85 }
      ],
      color: 'rgba(76, 212, 176, 0.3)',
      strokeColor: '#4CD4B0',
      label: 'Guard Anchor'
    }
  })
  
  const [selectedZone, setSelectedZone] = useState('gateArea')
  const [draggingPointIndex, setDraggingPointIndex] = useState(null)
  const [isDrawingMode, setIsDrawingMode] = useState(false)
  
  // Start video feed
  const startVideoFeed = () => {
    if (videoRef.current) {
      const streamUrl = `/stream?source=${encodeURIComponent(videoSource)}`
      videoRef.current.src = streamUrl
      videoRef.current.onloadedmetadata = () => {
        const w = videoRef.current.videoWidth || 640
        const h = videoRef.current.videoHeight || 480
        setCanvasSize({ width: w, height: h })
      }
      setIsLive(true)
    }
  }
  
  // Capture frame from video
  const captureFrame = () => {
    if (videoRef.current) {
      const img = new window.Image()
      const canvas = document.createElement('canvas')
      canvas.width = videoRef.current.videoWidth || videoRef.current.width
      canvas.height = videoRef.current.videoHeight || videoRef.current.height
      const ctx = canvas.getContext('2d')
      ctx.drawImage(videoRef.current, 0, 0)
      
      img.onload = () => {
        setVideoImage(img)
        setCanvasSize({ width: img.width, height: img.height })
      }
      img.src = canvas.toDataURL()
      setIsLive(false)
    }
  }
  
  // Convert normalized to pixel
  const normalizedToPixel = (point) => ({
    x: point.x * canvasSize.width,
    y: point.y * canvasSize.height
  })
  
  // Convert pixel to normalized
  const pixelToNormalized = (point) => ({
    x: point.x / canvasSize.width,
    y: point.y / canvasSize.height
  })
  
  // Handle point drag
  const handlePointDragMove = (e, zoneKey, pointIndex) => {
    const stage = e.target.getStage()
    const point = stage.getPointerPosition()
    
    const newZones = { ...zones }
    newZones[zoneKey].points[pointIndex] = pixelToNormalized(point)
    setZones(newZones)
  }
  
  // Handle stage click (add point in drawing mode)
  const handleStageClick = (e) => {
    if (!isDrawingMode) return
    
    const stage = e.target.getStage()
    const point = stage.getPointerPosition()
    const normalizedPoint = pixelToNormalized(point)
    
    const newZones = { ...zones }
    newZones[selectedZone].points.push(normalizedPoint)
    setZones(newZones)
  }
  
  // Save configuration
  const saveConfiguration = async () => {
    try {
      // Convert to backend format
      const gateAreaConfig = {
        zone_id: 'gate_A1',
        zone_type: 'gate_area',
        polygon: zones.gateArea.points.map(p => [p.x, p.y]),
        description: 'Main gate area where security check must occur',
        normalized: true
      }
      
      const guardAnchorConfig = {
        zone_id: 'guard_anchor_A1',
        zone_type: 'guard_anchor',
        polygon: zones.guardAnchor.points.map(p => [p.x, p.y]),
        description: 'Guard anchor zone - where guard should stand during check',
        normalized: true
      }
      
      // Save to backend
      await fetch('http://localhost:8005/config/gate_A1_polygon.json', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(gateAreaConfig)
      })
      
      await fetch('http://localhost:8005/config/guard_anchor_A1_polygon.json', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(guardAnchorConfig)
      })
      
      alert('✅ Configuration saved successfully!')
    } catch (error) {
      console.error('Failed to save configuration:', error)
      alert('❌ Failed to save configuration')
    }
  }
  
  // Download configuration
  const downloadConfiguration = () => {
    const config = {
      gateArea: {
        polygon: zones.gateArea.points.map(p => [p.x, p.y])
      },
      guardAnchor: {
        polygon: zones.guardAnchor.points.map(p => [p.x, p.y])
      }
    }
    
    const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'gate-zones-config.json'
    a.click()
    URL.revokeObjectURL(url)
  }
  
  // Reset zones
  const resetZones = () => {
    if (confirm('Reset zones to default positions?')) {
      setZones({
        gateArea: {
          ...zones.gateArea,
          points: [
            { x: 0.30, y: 0.20 },
            { x: 0.70, y: 0.20 },
            { x: 0.70, y: 0.80 },
            { x: 0.30, y: 0.80 }
          ]
        },
        guardAnchor: {
          ...zones.guardAnchor,
          points: [
            { x: 0.10, y: 0.15 },
            { x: 0.25, y: 0.15 },
            { x: 0.25, y: 0.85 },
            { x: 0.10, y: 0.85 }
          ]
        }
      })
    }
  }
  
  // Clear last point
  const clearLastPoint = () => {
    const newZones = { ...zones }
    if (newZones[selectedZone].points.length > 3) {
      newZones[selectedZone].points.pop()
      setZones(newZones)
    }
  }
  
  // Render polygon
  const renderPolygon = (zoneKey) => {
    const zone = zones[zoneKey]
    const points = zone.points.map(normalizedToPixel)
    const flatPoints = points.flatMap(p => [p.x, p.y])
    
    return (
      <React.Fragment key={zoneKey}>
        {/* Polygon fill */}
        <Line
          points={flatPoints}
          fill={zone.color}
          stroke={zone.strokeColor}
          strokeWidth={3}
          closed
          opacity={selectedZone === zoneKey ? 0.8 : 0.5}
        />
        
        {/* Control points */}
        {points.map((point, idx) => (
          <Circle
            key={`${zoneKey}-${idx}`}
            x={point.x}
            y={point.y}
            radius={8}
            fill={selectedZone === zoneKey ? zone.strokeColor : '#fff'}
            stroke={zone.strokeColor}
            strokeWidth={2}
            draggable
            onDragMove={(e) => handlePointDragMove(e, zoneKey, idx)}
            onMouseEnter={(e) => {
              const stage = e.target.getStage()
              if (stage?.container) {
                stage.container().style.cursor = 'pointer'
              }
            }}
            onMouseLeave={(e) => {
              const stage = e.target.getStage()
              if (stage?.container) {
                stage.container().style.cursor = 'default'
              }
            }}
          />
        ))}
      </React.Fragment>
    )
  }
  
  return (
    <div style={{ padding: '20px' }}>
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '20px',
        padding: '20px',
        background: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '12px',
        border: '1px solid rgba(76, 212, 176, 0.2)'
      }}>
        <div>
          <h3 style={{ margin: 0, marginBottom: '8px' }}>
            <Video size={24} style={{ verticalAlign: 'middle', marginRight: '12px' }} />
            Live Video Zone Editor
          </h3>
          <p style={{ margin: 0, fontSize: '14px', opacity: 0.7 }}>
            Draw gate security zones directly on your camera feed
          </p>
        </div>
        
        <div style={{ display: 'flex', gap: '12px' }}>
          <input
            type="text"
            value={videoSource}
            onChange={(e) => setVideoSource(e.target.value)}
            placeholder="webcam:0 or file:path"
            style={{
              padding: '8px 12px',
              background: 'rgba(255, 255, 255, 0.1)',
              border: '1px solid rgba(76, 212, 176, 0.3)',
              borderRadius: '6px',
              color: 'white',
              width: '200px'
            }}
          />
          <button
            onClick={startVideoFeed}
            style={{
              padding: '8px 16px',
              background: 'linear-gradient(135deg, var(--verolux-secondary), var(--verolux-accent))',
              border: 'none',
              borderRadius: '6px',
              color: 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <Play size={16} />
            Start Feed
          </button>
          <button
            onClick={captureFrame}
            disabled={!isLive}
            style={{
              padding: '8px 16px',
              background: isLive ? 'rgba(76, 212, 176, 0.2)' : 'rgba(255, 255, 255, 0.1)',
              border: '1px solid rgba(76, 212, 176, 0.3)',
              borderRadius: '6px',
              color: 'white',
              cursor: isLive ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <Camera size={16} />
            Capture Frame
          </button>
        </div>
      </div>
      
      {/* Controls */}
      <div style={{
        display: 'flex',
        gap: '20px',
        marginBottom: '20px',
        padding: '16px',
        background: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '12px',
        border: '1px solid rgba(76, 212, 176, 0.2)'
      }}>
        {/* Zone Selection */}
        <div style={{ flex: 1 }}>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: 600 }}>
            Select Zone
          </label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setSelectedZone('gateArea')}
              style={{
                flex: 1,
                padding: '10px',
                background: selectedZone === 'gateArea' 
                  ? 'linear-gradient(135deg, #00ff88, #00cc6a)'
                  : 'rgba(255, 255, 255, 0.1)',
                border: `2px solid ${selectedZone === 'gateArea' ? '#00ff88' : 'rgba(76, 212, 176, 0.3)'}`,
                borderRadius: '6px',
                color: 'white',
                cursor: 'pointer',
                fontWeight: selectedZone === 'gateArea' ? 600 : 400
              }}
            >
              🚪 Gate Area
            </button>
            <button
              onClick={() => setSelectedZone('guardAnchor')}
              style={{
                flex: 1,
                padding: '10px',
                background: selectedZone === 'guardAnchor' 
                  ? 'linear-gradient(135deg, #4CD4B0, #1ECAD3)'
                  : 'rgba(255, 255, 255, 0.1)',
                border: `2px solid ${selectedZone === 'guardAnchor' ? '#4CD4B0' : 'rgba(76, 212, 176, 0.3)'}`,
                borderRadius: '6px',
                color: 'white',
                cursor: 'pointer',
                fontWeight: selectedZone === 'guardAnchor' ? 600 : 400
              }}
            >
              👮 Guard Anchor
            </button>
          </div>
        </div>
        
        {/* Actions */}
        <div style={{ flex: 1 }}>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: 600 }}>
            Actions
          </label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={saveConfiguration}
              style={{
                flex: 1,
                padding: '10px',
                background: 'linear-gradient(135deg, #22c55e, #16a34a)',
                border: 'none',
                borderRadius: '6px',
                color: 'white',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px'
              }}
            >
              <Save size={16} />
              Save
            </button>
            <button
              onClick={downloadConfiguration}
              style={{
                padding: '10px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(76, 212, 176, 0.3)',
                borderRadius: '6px',
                color: 'white',
                cursor: 'pointer'
              }}
            >
              <Download size={16} />
            </button>
            <button
              onClick={resetZones}
              style={{
                padding: '10px',
                background: 'rgba(239, 68, 68, 0.2)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '6px',
                color: 'white',
                cursor: 'pointer'
              }}
            >
              <RotateCcw size={16} />
            </button>
          </div>
        </div>
      </div>
      
      {/* Canvas with video background */}
      <div style={{ 
        position: 'relative',
        borderRadius: '12px',
        overflow: 'hidden',
        border: '2px solid rgba(76, 212, 176, 0.3)',
        background: '#000'
      }}>
        {/* Video element (hidden) */}
        <video
          ref={videoRef}
          style={{ display: 'none' }}
          autoPlay
          muted
          playsInline
        />
        
        {/* Konva Stage */}
        <Stage
          ref={stageRef}
          width={canvasSize.width}
          height={canvasSize.height}
          onClick={handleStageClick}
          style={{ cursor: isDrawingMode ? 'crosshair' : 'default' }}
        >
          <Layer ref={layerRef}>
            {/* Video background */}
            {videoImage && (
              <KonvaImage
                image={videoImage}
                width={canvasSize.width}
                height={canvasSize.height}
              />
            )}
            
            {/* Render zones */}
            {Object.keys(zones).map(renderPolygon)}
          </Layer>
        </Stage>
        
        {/* Live feed overlay */}
        {isLive && (
          <img
            ref={imgRef}
            src={`/stream?source=${encodeURIComponent(videoSource)}`}
            alt="Live feed"
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              objectFit: 'contain',
              pointerEvents: 'none',
              zIndex: 0
            }}
          />
        )}
      </div>
      
      {/* Instructions */}
      <div style={{
        marginTop: '20px',
        padding: '16px',
        background: 'rgba(76, 212, 176, 0.1)',
        borderRadius: '8px',
        border: '1px solid rgba(76, 212, 176, 0.2)'
      }}>
        <p style={{ margin: 0, fontSize: '14px' }}>
          <strong>💡 How to use:</strong><br/>
          1. Start video feed or capture a frame<br/>
          2. Select a zone (Gate Area or Guard Anchor)<br/>
          3. Drag the corner points to adjust the zone<br/>
          4. Click Save to apply the configuration
        </p>
      </div>
    </div>
  )
}

