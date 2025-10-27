import React, { useEffect, useRef, useState } from 'react'
import useEvents from '../stores/events'
import useAlerts from '../stores/alerts'

export default function VideoFeed({ 
  title = 'Live Camera Feed', 
  source = 'webcam:0',
  showDetections = true,
  showStats = true,
  className = ''
}) {
  const imgRef = useRef(null)
  const canvasRef = useRef(null)
  const wsRef = useRef(null)
  const [status, setStatus] = useState('connecting')
  const [fps, setFps] = useState(0)
  const [detectionCount, setDetectionCount] = useState(0)
  const [lastDetection, setLastDetection] = useState(null)
  const [isFullscreen, setIsFullscreen] = useState(false)
  
  const push = useEvents(s => s.push)
  const evalAlerts = useAlerts(s => s.eval)

  useEffect(() => {
    let attempts = 0
    let closed = false
    
    const connect = () => {
      const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
      const url = `${protocol}//${location.host}/ws/detections?source=${encodeURIComponent(source)}`
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
          setFps(msg.fps || 0)
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
    
    const w = img.naturalWidth || img.width
    const h = img.naturalHeight || img.height
    if (!w || !h) return
    
    const dpr = window.devicePixelRatio || 1
    canvas.width = Math.round(w * dpr)
    canvas.height = Math.round(h * dpr)
    canvas.style.width = w + 'px'
    canvas.style.height = h + 'px'
    
    const ctx = canvas.getContext('2d')
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    ctx.clearRect(0, 0, w, h)
    
    for (const detection of detections || []) {
      const [x1, y1, x2, y2] = detection.bbox || []
      if ([x1, y1, x2, y2].some(v => typeof v !== 'number')) continue
      
      const rx1 = x1 * w
      const ry1 = y1 * h
      const rw = (x2 - x1) * w
      const rh = (y2 - y1) * h
      
      // Draw bounding box
      ctx.lineWidth = 3
      ctx.strokeStyle = getDetectionColor(detection.cls)
      ctx.strokeRect(rx1, ry1, rw, rh)
      
      // Draw label background
      const label = `${detection.cls || 'object'} ${Math.round((detection.conf || 0) * 100)}%`
      const metrics = ctx.measureText(label)
      const tw = metrics.width + 12
      const th = 20
      
      ctx.fillStyle = 'rgba(0, 0, 0, 0.8)'
      ctx.fillRect(rx1, Math.max(0, ry1 - th), tw, th)
      
      // Draw label text
      ctx.fillStyle = '#ffffff'
      ctx.font = 'bold 12px system-ui'
      ctx.fillText(label, rx1 + 6, Math.max(12, ry1 - 6))
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
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
        borderRadius: '16px',
        border: '1px solid #334155',
        overflow: 'hidden',
        boxShadow: '0 10px 25px rgba(0, 0, 0, 0.3)',
        position: 'relative'
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
                {fps.toFixed(1)} FPS
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
      <div style={{
        position: 'relative',
        width: '100%',
        maxWidth: '100%',
        background: '#000'
      }}>
        <img
          ref={imgRef}
          src={`/stream?source=${encodeURIComponent(source)}`}
          alt={title}
          style={{
            width: '100%',
            height: 'auto',
            display: 'block',
            maxHeight: '600px',
            objectFit: 'cover'
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
      `}</style>
    </div>
  )
}
