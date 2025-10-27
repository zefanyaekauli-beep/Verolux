import React, { useEffect, useRef, useState } from 'react'
import useEvents from '../stores/events'
import useAlerts from '../stores/alerts'
import LiveZoneEditor from './LiveZoneEditor'
import GateBoxOverlay from './GateBoxOverlay'

export default function VideoFeed({ 
  title = 'Live Camera Feed', 
  source = 'file:videoplayback.mp4',
  showDetections = true,
  showStats = true,
  className = '',
  enableZoneEditor = false,
  enableGateConfig = false
}) {
  const imgRef = useRef(null)
  const canvasRef = useRef(null)
  const wsRef = useRef(null)
  const [status, setStatus] = useState('connecting')
  const [fps, setFps] = useState(0)
  const [detectionCount, setDetectionCount] = useState(0)
  const [lastDetection, setLastDetection] = useState(null)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isZoneEditorActive, setIsZoneEditorActive] = useState(false)
  const [isGateConfigVisible, setIsGateConfigVisible] = useState(false)
  const [showGateBoxes, setShowGateBoxes] = useState(true)
  
  // Debug gate boxes
  console.log('Gate config enabled:', enableGateConfig, 'Show gate boxes:', showGateBoxes)
  
  const push = useEvents(s => s.push)
  const evalAlerts = useAlerts(s => s.eval)

  useEffect(() => {
    let attempts = 0
    let closed = false
    
    const connect = () => {
      const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
      const url = `${protocol}//127.0.0.1:8002/ws`
      const ws = new WebSocket(url)
      wsRef.current = ws
      
      ws.onopen = () => {
        setStatus('connected')
        attempts = 0
      }
      
      ws.onclose = () => {
        setStatus('disconnected')
        if (!closed) {
          const delay = Math.min(30000, 1000 * Math.pow(2, attempts++))
          setTimeout(connect, delay)
        }
      }
      
      ws.onerror = () => setStatus('error')
      
      ws.onmessage = (ev) => {
        const msg = JSON.parse(ev.data)
        if (msg.type === 'detections') {
          // Handle fps as either a number or object
          const fpsValue = typeof msg.fps === 'number' 
            ? msg.fps 
            : (msg.fps?.inference || msg.fps?.capture || 0)
          setFps(fpsValue)
          setDetectionCount(msg.detections?.length || 0)
          setLastDetection(msg.detections?.[0] || null)
          if (showDetections) {
            drawDetections(msg.detections)
          }
          push(msg)
          evalAlerts(msg)
        }
      }
    }
    
    connect()
    
    return () => {
      closed = true
      try {
        wsRef.current?.close()
      } catch {}
    }
  }, [source, showDetections])

  const drawDetections = (detections) => {
    const img = imgRef.current
    const canvas = canvasRef.current
    if (!img || !canvas) return
    
    // Get actual display dimensions (not natural dimensions)
    const imgRect = img.getBoundingClientRect()
    const w = imgRect.width
    const h = imgRect.height
    if (!w || !h) return
    
    const dpr = window.devicePixelRatio || 1
    canvas.width = Math.round(w * dpr)
    canvas.height = Math.round(h * dpr)
    canvas.style.width = w + 'px'
    canvas.style.height = h + 'px'
    
    const ctx = canvas.getContext('2d')
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    ctx.clearRect(0, 0, w, h)
    
    // Force redraw in fullscreen mode
    if (isFullscreen) {
      canvas.style.position = 'absolute'
      canvas.style.top = '0'
      canvas.style.left = '0'
      canvas.style.zIndex = '10'
    }
    
    for (const detection of detections || []) {
      const [x1, y1, x2, y2] = detection.bbox || []
      if ([x1, y1, x2, y2].some(v => typeof v !== 'number')) continue
      
      const rx1 = x1 * w
      const ry1 = y1 * h
      const rw = (x2 - x1) * w
      const rh = (y2 - y1) * h
      
      // Enhanced bounding box with better styling
      const color = getDetectionColor(detection.cls)
      ctx.lineWidth = 4
      ctx.strokeStyle = color
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      ctx.strokeRect(rx1, ry1, rw, rh)
      
      // Draw corner markers for better visibility
      const cornerSize = 12
      ctx.fillStyle = color
      
      // Top-left corner
      ctx.fillRect(rx1 - 2, ry1 - 2, cornerSize, 4)
      ctx.fillRect(rx1 - 2, ry1 - 2, 4, cornerSize)
      
      // Top-right corner
      ctx.fillRect(rx1 + rw - cornerSize + 2, ry1 - 2, cornerSize, 4)
      ctx.fillRect(rx1 + rw - 2, ry1 - 2, 4, cornerSize)
      
      // Bottom-left corner
      ctx.fillRect(rx1 - 2, ry1 + rh - 2, cornerSize, 4)
      ctx.fillRect(rx1 - 2, ry1 + rh - cornerSize + 2, 4, cornerSize)
      
      // Bottom-right corner
      ctx.fillRect(rx1 + rw - cornerSize + 2, ry1 + rh - 2, cornerSize, 4)
      ctx.fillRect(rx1 + rw - 2, ry1 + rh - cornerSize + 2, 4, cornerSize)
      
      // Enhanced label with class name and confidence
      const label = `${detection.cls || 'object'} ${Math.round((detection.conf || 0) * 100)}%`
      ctx.font = 'bold 16px system-ui'
      const metrics = ctx.measureText(label)
      const tw = metrics.width + 16
      const th = 28
      
      // Label background with rounded corners
      const labelX = rx1
      const labelY = Math.max(0, ry1 - th - 4)
      
      // Draw background
      ctx.fillStyle = color
      ctx.beginPath()
      ctx.roundRect(labelX, labelY, tw, th, 8)
      ctx.fill()
      
      // Draw label text
      ctx.fillStyle = '#ffffff'
      ctx.textAlign = 'left'
      ctx.textBaseline = 'top'
      ctx.fillText(label, labelX + 8, labelY + 6)
      
      // Add subtle glow effect
      ctx.shadowColor = color
      ctx.shadowBlur = 8
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      ctx.strokeRect(rx1, ry1, rw, rh)
      ctx.shadowBlur = 0
    }
  }

  const getDetectionColor = (className) => {
    const colors = {
      'person': '#00ff88',      // Green for person detection
      'car': '#ff6b6b',
      'truck': '#4ecdc4',
      'bus': '#45b7d1',
      'bicycle': '#96ceb4',
      'motorcycle': '#feca57',
      'dog': '#ff9ff3',
      'cat': '#54a0ff'
    }
    return colors[className?.toLowerCase()] || '#00ff88'
  }

  const toggleFullscreen = () => {
    if (!isFullscreen) {
      const element = document.querySelector(`[data-video-feed="${title}"]`)
      if (element.requestFullscreen) {
        element.requestFullscreen()
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen()
      }
    }
    setIsFullscreen(!isFullscreen)
  }

  // Listen for fullscreen changes and window resize
  useEffect(() => {
    const handleFullscreenChange = () => {
      const isCurrentlyFullscreen = !!document.fullscreenElement
      setIsFullscreen(isCurrentlyFullscreen)
      // Redraw detections after fullscreen change
      setTimeout(() => {
        if (lastDetection) {
          drawDetections([lastDetection])
        }
      }, 100)
    }

    const handleResize = () => {
      // Redraw detections on window resize
      setTimeout(() => {
        if (lastDetection) {
          drawDetections([lastDetection])
        }
      }, 100)
    }

    document.addEventListener('fullscreenchange', handleFullscreenChange)
    window.addEventListener('resize', handleResize)
    
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange)
      window.removeEventListener('resize', handleResize)
    }
  }, [lastDetection])

  const getStatusColor = () => {
    switch (status) {
      case 'connected': return '#00ff88'
      case 'connecting': return '#feca57'
      case 'error': return '#ff6b6b'
      default: return '#6c757d'
    }
  }

  return (
    <div 
      className={`video-feed-container ${className}`}
      data-video-feed={title}
      style={{
        background: isFullscreen ? '#000' : 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
        borderRadius: isFullscreen ? '0' : '16px',
        border: isFullscreen ? 'none' : '1px solid #334155',
        overflow: 'hidden',
        boxShadow: isFullscreen ? 'none' : '0 10px 25px rgba(0, 0, 0, 0.3)',
        position: 'relative',
        width: isFullscreen ? '100vw' : 'auto',
        height: isFullscreen ? '100vh' : 'auto'
      }}
    >
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '16px 20px',
        background: 'rgba(0, 0, 0, 0.3)',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: getStatusColor(),
            animation: status === 'connected' ? 'pulse 2s infinite' : 'none'
          }} />
          <h3 style={{ 
            margin: 0, 
            fontSize: '18px', 
            fontWeight: '600',
            color: '#ffffff'
          }}>
            {title}
          </h3>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {showStats && (
            <div style={{ display: 'flex', gap: '8px', fontSize: '12px' }}>
              <span style={{
                background: 'rgba(0, 255, 136, 0.2)',
                color: '#00ff88',
                padding: '4px 8px',
                borderRadius: '6px',
                border: '1px solid rgba(0, 255, 136, 0.3)'
              }}>
                {typeof fps === 'number' ? fps.toFixed(1) : '0.0'} FPS
              </span>
              <span style={{
                background: 'rgba(255, 107, 107, 0.2)',
                color: '#ff6b6b',
                padding: '4px 8px',
                borderRadius: '6px',
                border: '1px solid rgba(255, 107, 107, 0.3)'
              }}>
                {detectionCount} objects
              </span>
            </div>
          )}
          
          {enableZoneEditor && (
            <button
              onClick={() => setIsZoneEditorActive(!isZoneEditorActive)}
              style={{
                background: isZoneEditorActive ? 'rgba(220, 53, 69, 0.8)' : 'rgba(40, 167, 69, 0.8)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                padding: '8px 12px',
                color: '#ffffff',
                cursor: 'pointer',
                fontSize: '12px',
                transition: 'all 0.2s ease',
                marginRight: '8px'
              }}
              onMouseOver={(e) => {
                e.target.style.background = isZoneEditorActive ? 'rgba(220, 53, 69, 1)' : 'rgba(40, 167, 69, 1)'
              }}
              onMouseOut={(e) => {
                e.target.style.background = isZoneEditorActive ? 'rgba(220, 53, 69, 0.8)' : 'rgba(40, 167, 69, 0.8)'
              }}
            >
              {isZoneEditorActive ? 'Stop Config' : 'Configure Zones'}
            </button>
          )}

          {enableGateConfig && (
            <button
              onClick={() => setShowGateBoxes(!showGateBoxes)}
              style={{
                background: showGateBoxes ? 'rgba(0, 255, 136, 0.8)' : 'rgba(100, 100, 100, 0.8)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                padding: '8px 12px',
                color: '#ffffff',
                cursor: 'pointer',
                fontSize: '12px',
                transition: 'all 0.2s ease',
                marginRight: '8px'
              }}
              onMouseOver={(e) => {
                e.target.style.background = showGateBoxes ? 'rgba(0, 255, 136, 1)' : 'rgba(100, 100, 100, 1)'
              }}
              onMouseOut={(e) => {
                e.target.style.background = showGateBoxes ? 'rgba(0, 255, 136, 0.8)' : 'rgba(100, 100, 100, 0.8)'
              }}
            >
              {showGateBoxes ? '🎯 Hide Gates' : '🎯 Show Gates'}
            </button>
          )}
          
          <button
            onClick={toggleFullscreen}
            style={{
              background: 'rgba(255, 255, 255, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '8px',
              padding: '8px 12px',
              color: '#ffffff',
              cursor: 'pointer',
              fontSize: '12px',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.2)'
            }}
            onMouseOut={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.1)'
            }}
          >
            {isFullscreen ? 'Exit' : 'Fullscreen'}
          </button>
        </div>
      </div>

      {/* Video Container */}
      <div 
        className="video-container"
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: '100%',
          background: '#000',
          height: isFullscreen ? 'calc(100vh - 120px)' : 'auto',
          minHeight: isFullscreen ? 'none' : '800px' // Increased minimum height for much larger video
        }}
      >
        <img
          ref={imgRef}
          src={`http://127.0.0.1:8002/stream?source=${encodeURIComponent(source)}`}
          alt={title}
          style={{
            width: '100%',
            height: isFullscreen ? '100%' : 'auto',
            display: 'block',
            maxHeight: isFullscreen ? 'none' : '1000px', // Increased to 1000px for much larger video
            objectFit: isFullscreen ? 'contain' : 'cover'
          }}
          onLoad={() => drawDetections([])}
        />
        
        {showDetections && (
          <canvas
            ref={canvasRef}
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              pointerEvents: 'none',
              width: '100%',
              height: '100%'
            }}
          />
        )}
        
        {/* Overlay Info */}
        {lastDetection && (
          <div style={{
            position: 'absolute',
            top: '16px',
            left: '16px',
            background: 'rgba(0, 0, 0, 0.8)',
            color: '#ffffff',
            padding: '8px 12px',
            borderRadius: '8px',
            fontSize: '12px',
            backdropFilter: 'blur(10px)'
          }}>
            Latest: {lastDetection.cls} ({Math.round(lastDetection.conf * 100)}%)
          </div>
        )}

        {/* Gate Configuration Overlay - Main Feature */}
        {enableGateConfig && (
          <GateBoxOverlay 
            isVisible={isGateConfigVisible}
            onToggle={() => setIsGateConfigVisible(!isGateConfigVisible)}
            onConfigChange={(config) => {
              console.log('Gate configuration updated:', config);
              // You can emit events or update state here
            }}
          />
        )}

        {/* Gate Box Visual Overlay on Video */}
        {enableGateConfig && showGateBoxes && (
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none',
            zIndex: 10
          }}>
            {/* Gate Area Box */}
            <div style={{
              position: 'absolute',
              left: '30%',
              top: '20%',
              width: '40%',
              height: '60%',
              border: '4px solid #00ff88',
              borderRadius: '8px',
              background: 'rgba(0, 255, 136, 0.2)',
              pointerEvents: 'none',
              boxShadow: '0 0 10px rgba(0, 255, 136, 0.5)'
            }}>
              <div style={{
                position: 'absolute',
                top: '-30px',
                left: '0',
                background: 'rgba(0, 255, 136, 0.9)',
                color: 'white',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: 'bold',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
              }}>
                🎯 Gate Area
              </div>
            </div>

            {/* Guard Anchor Box */}
            <div style={{
              position: 'absolute',
              left: '10%',
              top: '15%',
              width: '15%',
              height: '70%',
              border: '4px solid #ff6b6b',
              borderRadius: '8px',
              background: 'rgba(255, 107, 107, 0.2)',
              pointerEvents: 'none',
              boxShadow: '0 0 10px rgba(255, 107, 107, 0.5)'
            }}>
              <div style={{
                position: 'absolute',
                top: '-30px',
                left: '0',
                background: 'rgba(255, 107, 107, 0.9)',
                color: 'white',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: 'bold',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
              }}>
                👮 Guard Anchor
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer Stats */}
      {showStats && (
        <div style={{
          padding: '12px 20px',
          background: 'rgba(0, 0, 0, 0.2)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '12px',
          color: '#94a3b8'
        }}>
          <span>Status: <span style={{ color: getStatusColor() }}>{status}</span></span>
          <span>Source: {source}</span>
        </div>
      )}

      <style jsx="true">{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        
        /* Fullscreen specific styles */
        .video-feed-container:fullscreen {
          background: #000 !important;
          border-radius: 0 !important;
          border: none !important;
          box-shadow: none !important;
          width: 100vw !important;
          height: 100vh !important;
        }
        
        .video-feed-container:fullscreen img {
          object-fit: contain !important;
          max-height: none !important;
          height: calc(100vh - 120px) !important;
        }
        
        .video-feed-container:fullscreen .video-container {
          height: calc(100vh - 120px) !important;
        }
        
        .video-feed-container:fullscreen canvas {
          position: absolute !important;
          top: 0 !important;
          left: 0 !important;
          width: 100% !important;
          height: 100% !important;
          pointer-events: none !important;
          z-index: 5 !important;
        }
        
        .video-feed-container:fullscreen [data-gate-config] {
          z-index: 1000 !important;
          position: absolute !important;
        }
        
        /* Webkit fullscreen support */
        .video-feed-container:-webkit-full-screen {
          background: #000 !important;
          border-radius: 0 !important;
          border: none !important;
          box-shadow: none !important;
          width: 100vw !important;
          height: 100vh !important;
        }
        
        .video-feed-container:-webkit-full-screen img {
          object-fit: contain !important;
          max-height: none !important;
          height: calc(100vh - 120px) !important;
        }
      `}</style>

      {/* Live Zone Editor */}
      {enableZoneEditor && (
        <LiveZoneEditor
          videoRef={imgRef}
          canvasRef={canvasRef}
          isActive={isZoneEditorActive}
          onSave={(zones) => {
            console.log('Zones saved:', zones);
            setIsZoneEditorActive(false);
          }}
          onCancel={() => {
            setIsZoneEditorActive(false);
          }}
        />
      )}
    </div>
  )
}
