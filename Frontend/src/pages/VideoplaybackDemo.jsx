import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Play, Pause, Square, RotateCcw, Settings, AlertTriangle, 
  Shield, Users, Eye, Activity, Zap, CheckCircle, XCircle,
  Camera, Video, Download, Upload, Maximize2, Minimize2,
  Target, MapPin, UserCheck, Hand, SquareCheck, FileText
} from 'lucide-react'

export default function VideoplaybackDemo() {
  // State management
  const [isPlaying, setIsPlaying] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  
  // System states
  const [detections, setDetections] = useState([])
  const [gateEvents, setGateEvents] = useState([])
  const [alerts, setAlerts] = useState([])
  const [systemStats, setSystemStats] = useState({
    fps: 0,
    processingTime: 0,
    activeTracks: 0,
    totalDetections: 0
  })
  
  // Gate configuration states
  const [gateConfig, setGateConfig] = useState({
    gateId: 'A1',
    zones: {
      checkZone: { x: 100, y: 100, width: 200, height: 150, active: true },
      guardZone: { x: 300, y: 200, width: 150, height: 100, active: true }
    },
    thresholds: {
      confidence: 0.7,
      dwellTime: 3.0,
      guardTime: 2.0,
      interactionTime: 1.0
    },
    bodyCheck: {
      enabled: true,
      handToTorso: true,
      reachGesture: true,
      proximityCheck: true
    }
  })
  
  // Body check states
  const [bodyCheckStatus, setBodyCheckStatus] = useState({
    completed: false,
    handToTorsoDetected: false,
    reachGestureDetected: false,
    proximityMet: false,
    score: 0
  })
  
  // WebSocket connections
  const [wsDetections, setWsDetections] = useState(null)
  const [wsGateCheck, setWsGateCheck] = useState(null)
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  
  // Refs
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const alertContainerRef = useRef(null)
  
  // No sample data - only use real AI detections from WebSocket

  // Report generation states
  const [reportData, setReportData] = useState({
    sessionId: `VIDEO_${Date.now()}`,
    startTime: new Date(),
    endTime: null,
    totalDetections: 0,
    totalAlerts: 0,
    gateEvents: [],
    systemStats: {},
    isGenerating: false
  })

  // Initialize with empty detections - let WebSocket populate
  useEffect(() => {
    // Don't set sample data initially - let WebSocket handle it
    setDetections([])
  }, [])
  
  // No sample data - only use real data from WebSocket

  // Initialize WebSocket connections
  useEffect(() => {
    const connectWebSockets = () => {
      try {
        // Detection WebSocket - try multiple video sources
        const videoSources = [
          'file:videoplayback.mp4',
          'file:../videoplayback.mp4', 
          'file:Frontend/public/videoplayback.mp4'
        ]
        
        let currentSourceIndex = 0
        const tryConnect = () => {
        if (currentSourceIndex >= videoSources.length) {
          console.log('All video sources failed - no fallback data')
          setConnectionStatus('error')
          // No fallback data - wait for real connection
          return
        }
          
          const source = videoSources[currentSourceIndex]
          console.log(`Trying video source: ${source}`)
          
          const detectionsWs = new WebSocket(`ws://127.0.0.1:8002/ws/detections?source=${source}`)
          detectionsWs.onopen = () => {
            console.log(`Detections WebSocket connected with source: ${source}`)
            setConnectionStatus('connected')
          }
          detectionsWs.onmessage = (event) => {
            const data = JSON.parse(event.data)
            console.log('WebSocket received:', data.type, 'detections:', data.detections?.length || 0)
            if (data.type === 'detection') {
              // Only use real detections from WebSocket
              setDetections(data.detections || [])
              setSystemStats(prev => ({
                ...prev,
                fps: data.fps || 0,
                processingTime: data.processing_time || 0,
                activeTracks: data.active_tracks || 0,
                totalDetections: prev.totalDetections + (data.detections?.length || 0)
              }))
            } else if (data.type === 'error') {
              console.error('WebSocket error:', data.message)
              setConnectionStatus('error')
            }
          }
        detectionsWs.onerror = (error) => {
          console.log(`Detections WebSocket failed for source: ${source}`, error)
          setConnectionStatus('error')
          currentSourceIndex++
          setTimeout(tryConnect, 1000) // Try next source after 1 second
        }
          detectionsWs.onclose = () => {
            console.log('Detections WebSocket closed')
            setConnectionStatus('disconnected')
          }
          setWsDetections(detectionsWs)
        }
        
        tryConnect() // Start trying connections

        // Gate Check WebSocket - use the same source as detections
        const gateSource = videoSources[0] || 'file:videoplayback.mp4'
        const gateWs = new WebSocket(`ws://127.0.0.1:8002/ws/gate-check?source=${gateSource}`)
        gateWs.onopen = () => {
          console.log(`Gate Check WebSocket connected with source: ${gateSource}`)
        }
        gateWs.onmessage = (event) => {
          const data = JSON.parse(event.data)
          if (data.type === 'gate_check') {
            setGateEvents(data.events || [])
            if (data.alerts && data.alerts.length > 0) {
              setAlerts(prev => [...data.alerts, ...prev])
            }
            
            // Update body check status from gate data
            if (data.bodyCheck) {
              setBodyCheckStatus(prev => ({
                ...prev,
                handToTorsoDetected: data.bodyCheck.handToTorsoDetected || false,
                reachGestureDetected: data.bodyCheck.reachGestureDetected || false,
                proximityMet: data.bodyCheck.proximityMet || false,
                score: data.bodyCheck.score || 0,
                completed: data.bodyCheck.completed || false
              }))
            }
          }
        }
        gateWs.onerror = () => {
          console.log('Gate Check WebSocket connection failed - no fallback data')
          // No fallback data - wait for real connection
          
          // Simulate body check status updates
          const simulateBodyCheck = () => {
            setBodyCheckStatus(prev => {
              const newStatus = { ...prev }
              
              // Randomly update status based on time
              const now = Date.now()
              const cycle = Math.floor(now / 5000) % 4 // 4 different states
              
              switch (cycle) {
                case 0:
                  newStatus.handToTorsoDetected = false
                  newStatus.reachGestureDetected = false
                  newStatus.proximityMet = false
                  newStatus.score = 0
                  newStatus.completed = false
                  break
                case 1:
                  newStatus.handToTorsoDetected = true
                  newStatus.reachGestureDetected = false
                  newStatus.proximityMet = false
                  newStatus.score = 25
                  newStatus.completed = false
                  break
                case 2:
                  newStatus.handToTorsoDetected = true
                  newStatus.reachGestureDetected = true
                  newStatus.proximityMet = true
                  newStatus.score = 75
                  newStatus.completed = false
                  break
                case 3:
                  newStatus.handToTorsoDetected = true
                  newStatus.reachGestureDetected = true
                  newStatus.proximityMet = true
                  newStatus.score = 100
                  newStatus.completed = true
                  break
              }
              
              return newStatus
            })
          }
          
          // Start simulation
          simulateBodyCheck()
          const interval = setInterval(simulateBodyCheck, 5000)
          
          // Cleanup interval when component unmounts
          return () => clearInterval(interval)
        }
        setWsGateCheck(gateWs)
      } catch (error) {
        console.log('WebSocket connection failed - no fallback data')
        setConnectionStatus('error')
        // No fallback data - wait for real connection
      }
    }

    connectWebSockets()

    return () => {
      if (wsDetections) wsDetections.close()
      if (wsGateCheck) wsGateCheck.close()
    }
  }, [])

  // Video controls
  const togglePlayPause = () => {
    if (isPaused) {
      videoRef.current?.play()
      setIsPaused(false)
    } else {
      videoRef.current?.pause()
      setIsPaused(true)
    }
    setIsPlaying(!isPaused)
  }

  const handleSeek = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const pos = (e.clientX - rect.left) / rect.width
    const newTime = pos * duration
    setCurrentTime(newTime)
    if (videoRef.current) {
      videoRef.current.currentTime = newTime
    }
  }

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      videoRef.current?.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  // Sync canvas size with video
  const syncCanvasSize = () => {
    const canvas = canvasRef.current
    const video = videoRef.current
    if (canvas && video) {
      const rect = video.getBoundingClientRect()
      canvas.width = rect.width
      canvas.height = rect.height
      
      // Force canvas redraw after size change
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      console.log('Canvas synced:', rect.width, 'x', rect.height)
    }
  }

  // Add resize observer for canvas sync
  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const resizeObserver = new ResizeObserver(() => {
      syncCanvasSize()
      // Force redraw after resize
      setTimeout(() => {
        const canvas = canvasRef.current
        if (canvas) {
          const ctx = canvas.getContext('2d')
          ctx.clearRect(0, 0, canvas.width, canvas.height)
          // Trigger redraw by updating detections
          setDetections(prev => [...prev])
        }
      }, 100)
    })

    resizeObserver.observe(video)

    // Also listen to window resize
    const handleResize = () => {
      syncCanvasSize()
      // Force redraw after resize
      setTimeout(() => {
        const canvas = canvasRef.current
        if (canvas) {
          const ctx = canvas.getContext('2d')
          ctx.clearRect(0, 0, canvas.width, canvas.height)
          // Trigger redraw by updating detections
          setDetections(prev => [...prev])
        }
      }, 100)
    }
    
    window.addEventListener('resize', handleResize)

    return () => {
      resizeObserver.disconnect()
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  // Draw detection boxes with proper letterboxing handling
  useEffect(() => {
    const canvas = canvasRef.current
    const video = videoRef.current
    if (!canvas || !video) return

    // Only draw if we have detections and video is loaded
    if (detections.length === 0 || !video.videoWidth) return

    // CSS size of the VIDEO element on screen
    const cssW = video.clientWidth
    const cssH = video.clientHeight

    // Intrinsic (source) size from the stream/decoder
    const srcW = video.videoWidth || 1920
    const srcH = video.videoHeight || 1080

    // Get actual video dimensions from detection data if available
    let actualVideoWidth = srcW
    let actualVideoHeight = srcH
    if (detections.length > 0 && detections[0].video_dimensions) {
      actualVideoWidth = detections[0].video_dimensions.width
      actualVideoHeight = detections[0].video_dimensions.height
    }

    // Compute aspect-fit (object-fit: contain) letterbox
    const r = Math.min(cssW / actualVideoWidth, cssH / actualVideoHeight)
    const drawW = actualVideoWidth * r
    const drawH = actualVideoHeight * r
    const offsetX = (cssW - drawW) / 2 // left black bar
    const offsetY = (cssH - drawH) / 2 // top black bar

    // Handle HiDPI (crisp lines)
    const dpr = window.devicePixelRatio || 1
    canvas.style.width = `${cssW}px`
    canvas.style.height = `${cssH}px`
    canvas.width = Math.round(cssW * dpr)
    canvas.height = Math.round(cssH * dpr)

    const ctx = canvas.getContext('2d')
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    ctx.clearRect(0, 0, cssW, cssH)

    console.log('Drawing detections:', detections.length)
    console.log('CSS size:', cssW, 'x', cssH)
    console.log('Source size:', actualVideoWidth, 'x', actualVideoHeight)
    console.log('Draw size:', drawW.toFixed(1), 'x', drawH.toFixed(1))
    console.log('Offset:', offsetX.toFixed(1), 'x', offsetY.toFixed(1))

    // Draw boxes mapped from MODEL coords (relative to actualVideoWidth x actualVideoHeight)
    detections.forEach((detection, index) => {
      const [x1, y1, x2, y2] = detection.bbox
      const width = x2 - x1
      const height = y2 - y1

      // Map from source coordinates to display coordinates with letterboxing
      const x = offsetX + x1 * (drawW / actualVideoWidth)
      const y = offsetY + y1 * (drawH / actualVideoHeight)
      const w = width * (drawW / actualVideoWidth)
      const h = height * (drawH / actualVideoHeight)

      console.log(`Detection ${index}: [${x1}, ${y1}, ${x2}, ${y2}] -> [${x.toFixed(1)}, ${y.toFixed(1)}, ${w.toFixed(1)}, ${h.toFixed(1)}]`)

      // Color based on class
      let color = '#3b82f6'
      if (detection.class === 'person') {
        color = '#22c55e'
      } else if (detection.class === 'vehicle') {
        color = '#f59e0b'
      }

      // Draw bounding box
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      ctx.strokeRect(x, y, w, h)

      // Draw label
      const tag = `${detection.class} ${(detection.confidence * 100).toFixed(0)}%`
      const labelWidth = ctx.measureText(tag).width + 8
      const labelHeight = 18
      
      ctx.fillStyle = 'rgba(0,0,0,0.6)'
      ctx.fillRect(x, y - labelHeight, labelWidth, labelHeight)
      ctx.fillStyle = '#fff'
      ctx.font = '12px sans-serif'
      ctx.fillText(tag, x + 4, y - 5)
    })

  }, [detections])

  // Report generation functions
  const generateReport = async () => {
    setReportData(prev => ({ ...prev, isGenerating: true }))
    
    const report = {
      sessionId: reportData.sessionId,
      startTime: reportData.startTime,
      endTime: new Date(),
      duration: Math.floor((new Date() - reportData.startTime) / 1000),
      totalDetections: systemStats.totalDetections,
      totalAlerts: alerts.length,
      gateEventsCount: gateEvents.length,
      systemStats: {
        avgFps: systemStats.fps,
        avgProcessingTime: systemStats.processingTime,
        activeTracks: systemStats.activeTracks
      },
      detections: detections,
      alerts: alerts,
      gateEvents: gateEvents,
      bodyCheckStatus: bodyCheckStatus,
      gateConfig: gateConfig
    }
    
    // Simulate report generation
    setTimeout(() => {
      setReportData(prev => ({ ...prev, isGenerating: false, endTime: new Date() }))
      
      // Show success alert
      setAlerts(prev => [{
        id: Date.now(),
        type: 'success',
        message: `Report generated successfully! Session: ${report.sessionId}`,
        timestamp: Date.now()
      }, ...prev])
      
      // Download report as JSON
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `verolux_report_${report.sessionId}.json`
      a.click()
      URL.revokeObjectURL(url)
    }, 2000)
  }

  // Alert animations
  const AlertComponent = ({ alert, onClose }) => (
    <motion.div
      initial={{ opacity: 0, x: 300, scale: 0.8 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 300, scale: 0.8 }}
      className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm ${
        alert.type === 'high' ? 'bg-red-500' : 
        alert.type === 'medium' ? 'bg-yellow-500' : 
        alert.type === 'success' ? 'bg-green-500' : 'bg-blue-500'
      }`}
    >
      <div className="flex items-start space-x-3">
        <AlertTriangle className="w-5 h-5 text-white" />
        <div className="flex-1">
          <p className="text-white font-medium">{alert.message}</p>
          <p className="text-white/80 text-sm">
            {new Date(alert.timestamp).toLocaleTimeString()}
          </p>
        </div>
        <button
          onClick={onClose}
          className="text-white/80 hover:text-white"
        >
          <XCircle className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  )

  return (
    <div className="verolux-pattern min-h-screen p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="verolux-heading-1 mb-2">Videoplayback System Demo</h1>
          <p className="verolux-body-secondary">
            Real-time object detection, gate SOP system, and live alerting
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            connectionStatus === 'connected' ? 'bg-green-500/20 text-green-400' :
            connectionStatus === 'demo' ? 'bg-yellow-500/20 text-yellow-400' :
            'bg-red-500/20 text-red-400'
          }`}>
            {connectionStatus === 'connected' ? 'Live' : 
             connectionStatus === 'demo' ? 'Demo Mode' : 'Disconnected'}
          </div>
          <button
            onClick={() => {
              // Force WebSocket reconnection instead of using sample data
              window.location.reload()
            }}
            className="verolux-btn verolux-btn-primary"
          >
            <Target className="w-4 h-4" />
            Test Overlay
          </button>
          <button
            onClick={generateReport}
            disabled={reportData.isGenerating}
            className="verolux-btn verolux-btn-primary"
          >
            {reportData.isGenerating ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Generating...
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                Generate Report
              </>
            )}
          </button>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="verolux-btn verolux-btn-outline"
          >
            <Settings className="w-4 h-4" />
            Settings
          </button>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Video Player - Takes 3 columns */}
        <div className="lg:col-span-3">
          <div className="verolux-card relative">
            <div className="relative w-full">
              <video
                ref={videoRef}
                className="block w-full rounded-lg"
                src="/videoplayback.mp4"
                controls
                autoPlay
                muted
                loop
                playsInline
                style={{ maxWidth: '100%', height: 'auto', objectFit: 'contain' }}
                onTimeUpdate={(e) => setCurrentTime(e.target.currentTime)}
                onLoadedMetadata={(e) => {
                  setDuration(e.target.duration)
                  // Trigger detection overlay redraw
                  setTimeout(() => {
                    const canvas = canvasRef.current
                    const video = videoRef.current
                    if (canvas && video) {
                      // Force redraw of detection overlay
                      const event = new Event('resize')
                      window.dispatchEvent(event)
                    }
                  }, 500)
                }}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
                onError={(e) => {
                  console.error('Video error:', e)
                  console.log('Video src:', e.target.src)
                }}
              />
              
              {/* Detection Overlay Canvas */}
              <canvas
                ref={canvasRef}
                className="absolute top-0 left-0 pointer-events-none"
                style={{ 
                  imageRendering: 'pixelated',
                  zIndex: 10,
                  width: '100%',
                  height: '100%',
                  objectFit: 'contain',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  pointerEvents: 'none',
                  transform: 'translateZ(0)' // Force hardware acceleration
                }}
              />
              
              {/* Video Controls Overlay */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={togglePlayPause}
                    className="text-white hover:text-blue-400 transition-colors"
                  >
                    {isPaused ? <Play className="w-6 h-6" /> : <Pause className="w-6 h-6" />}
                  </button>
                  
                  <div className="flex-1">
                    <div
                      className="w-full h-2 bg-white/30 rounded-full cursor-pointer"
                      onClick={handleSeek}
                    >
                      <div
                        className="h-full bg-blue-500 rounded-full"
                        style={{ width: `${(currentTime / duration) * 100}%` }}
                      />
                    </div>
                  </div>
                  
                  <span className="text-white text-sm">
                    {Math.floor(currentTime / 60)}:{(currentTime % 60).toFixed(0).padStart(2, '0')} / 
                    {Math.floor(duration / 60)}:{(duration % 60).toFixed(0).padStart(2, '0')}
                  </span>
                  
                  <button
                    onClick={toggleFullscreen}
                    className="text-white hover:text-blue-400 transition-colors"
                  >
                    {isFullscreen ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* System Status Panel - Takes 1 column */}
        <div className="space-y-6">
          {/* System Stats */}
          <div className="verolux-card">
            <h3 className="verolux-heading-3 mb-4">System Status</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm">FPS</span>
                <span className="font-semibold text-green-400">{systemStats.fps.toFixed(1)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Processing Time</span>
                <span className="font-semibold text-blue-400">{systemStats.processingTime}ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Active Tracks</span>
                <span className="font-semibold text-purple-400">{systemStats.activeTracks}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Total Detections</span>
                <span className="font-semibold text-yellow-400">{systemStats.totalDetections}</span>
              </div>
            </div>
          </div>

          {/* Gate Configuration */}
          <div className="verolux-card">
            <h3 className="verolux-heading-3 mb-4 flex items-center">
              <Target className="w-5 h-5 mr-2" />
              Gate Configuration
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Gate ID</label>
                <input
                  type="text"
                  value={gateConfig.gateId}
                  onChange={(e) => setGateConfig(prev => ({ ...prev, gateId: e.target.value }))}
                  className="verolux-input w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Confidence Threshold</label>
                <input
                  type="range"
                  min="0.1"
                  max="1"
                  step="0.1"
                  value={gateConfig.thresholds.confidence}
                  onChange={(e) => setGateConfig(prev => ({
                    ...prev,
                    thresholds: { ...prev.thresholds, confidence: parseFloat(e.target.value) }
                  }))}
                  className="w-full"
                />
                <span className="text-xs text-gray-400">{gateConfig.thresholds.confidence}</span>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Dwell Time (s)</label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  step="0.5"
                  value={gateConfig.thresholds.dwellTime}
                  onChange={(e) => setGateConfig(prev => ({
                    ...prev,
                    thresholds: { ...prev.thresholds, dwellTime: parseFloat(e.target.value) }
                  }))}
                  className="verolux-input w-full"
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="checkZone"
                  checked={gateConfig.zones.checkZone.active}
                  onChange={(e) => setGateConfig(prev => ({
                    ...prev,
                    zones: {
                      ...prev.zones,
                      checkZone: { ...prev.zones.checkZone, active: e.target.checked }
                    }
                  }))}
                  className="rounded"
                />
                <label htmlFor="checkZone" className="text-sm">Check Zone</label>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="guardZone"
                  checked={gateConfig.zones.guardZone.active}
                  onChange={(e) => setGateConfig(prev => ({
                    ...prev,
                    zones: {
                      ...prev.zones,
                      guardZone: { ...prev.zones.guardZone, active: e.target.checked }
                    }
                  }))}
                  className="rounded"
                />
                <label htmlFor="guardZone" className="text-sm">Guard Zone</label>
              </div>
            </div>
          </div>

          {/* Body Check Configuration */}
          <div className="verolux-card">
            <h3 className="verolux-heading-3 mb-4 flex items-center">
              <UserCheck className="w-5 h-5 mr-2" />
              Body Check
            </h3>
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="bodyCheckEnabled"
                  checked={gateConfig.bodyCheck.enabled}
                  onChange={(e) => setGateConfig(prev => ({
                    ...prev,
                    bodyCheck: { ...prev.bodyCheck, enabled: e.target.checked }
                  }))}
                  className="rounded"
                />
                <label htmlFor="bodyCheckEnabled" className="text-sm font-medium">Enable Body Check</label>
              </div>
              
              {gateConfig.bodyCheck.enabled && (
                <>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="handToTorso"
                      checked={gateConfig.bodyCheck.handToTorso}
                      onChange={(e) => setGateConfig(prev => ({
                        ...prev,
                        bodyCheck: { ...prev.bodyCheck, handToTorso: e.target.checked }
                      }))}
                      className="rounded"
                    />
                    <label htmlFor="handToTorso" className="text-sm">Hand to Torso Detection</label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="reachGesture"
                      checked={gateConfig.bodyCheck.reachGesture}
                      onChange={(e) => setGateConfig(prev => ({
                        ...prev,
                        bodyCheck: { ...prev.bodyCheck, reachGesture: e.target.checked }
                      }))}
                      className="rounded"
                    />
                    <label htmlFor="reachGesture" className="text-sm">Reach Gesture Detection</label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="proximityCheck"
                      checked={gateConfig.bodyCheck.proximityCheck}
                      onChange={(e) => setGateConfig(prev => ({
                        ...prev,
                        bodyCheck: { ...prev.bodyCheck, proximityCheck: e.target.checked }
                      }))}
                      className="rounded"
                    />
                    <label htmlFor="proximityCheck" className="text-sm">Proximity Check</label>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Body Check Status */}
          {gateConfig.bodyCheck.enabled && (
            <div className="verolux-card">
              <h3 className="verolux-heading-3 mb-4 flex items-center">
                <SquareCheck className="w-5 h-5 mr-2" />
                Body Check Status
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Hand to Torso</span>
                  <div className={`w-3 h-3 rounded-full ${bodyCheckStatus.handToTorsoDetected ? 'bg-green-500' : 'bg-gray-500'}`} />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Reach Gesture</span>
                  <div className={`w-3 h-3 rounded-full ${bodyCheckStatus.reachGestureDetected ? 'bg-green-500' : 'bg-gray-500'}`} />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Proximity</span>
                  <div className={`w-3 h-3 rounded-full ${bodyCheckStatus.proximityMet ? 'bg-green-500' : 'bg-gray-500'}`} />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Score</span>
                  <span className="font-semibold text-blue-400">{bodyCheckStatus.score.toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Status</span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    bodyCheckStatus.completed ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {bodyCheckStatus.completed ? 'COMPLETED' : 'IN PROGRESS'}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Current Detections */}
          <div className="verolux-card">
            <h3 className="verolux-heading-3 mb-4">Live Detections</h3>
            <div className="space-y-2">
              {detections.map(detection => (
                <div key={detection.id} className="flex items-center justify-between p-2 bg-gray-800 rounded">
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${
                      detection.class === 'person' ? 'bg-green-500' : 'bg-blue-500'
                    }`} />
                    <span className="text-sm">{detection.class}</span>
                  </div>
                  <span className="text-xs text-gray-400">
                    {(detection.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Gate Events */}
          <div className="verolux-card">
            <h3 className="verolux-heading-3 mb-4">Gate Events</h3>
            <div className="space-y-2">
              {gateEvents.map(event => (
                <div key={event.id} className="flex items-center justify-between p-2 bg-gray-800 rounded">
                  <div className="flex items-center space-x-2">
                    <Shield className="w-4 h-4 text-blue-400" />
                    <span className="text-sm">{event.type}</span>
                  </div>
                  <span className="text-xs text-gray-400">
                    {(event.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Report Status */}
          <div className="verolux-card">
            <h3 className="verolux-heading-3 mb-4 flex items-center">
              <FileText className="w-5 h-5 mr-2" />
              Report Status
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm">Session ID</span>
                <span className="font-mono text-xs text-blue-400">{reportData.sessionId}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Duration</span>
                <span className="font-semibold text-green-400">
                  {Math.floor((new Date() - reportData.startTime) / 1000)}s
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Total Detections</span>
                <span className="font-semibold text-yellow-400">{systemStats.totalDetections}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Total Alerts</span>
                <span className="font-semibold text-red-400">{alerts.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Gate Events</span>
                <span className="font-semibold text-purple-400">{gateEvents.length}</span>
              </div>
              <button
                onClick={generateReport}
                disabled={reportData.isGenerating}
                className="w-full verolux-btn verolux-btn-primary mt-4"
              >
                {reportData.isGenerating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Generating Report...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Generate Report
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Live Alerts */}
      <AnimatePresence>
        {alerts.map(alert => (
          <AlertComponent
            key={alert.id}
            alert={alert}
            onClose={() => setAlerts(prev => prev.filter(a => a.id !== alert.id))}
          />
        ))}
      </AnimatePresence>

      {/* Settings Modal */}
      {showSettings && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setShowSettings(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="verolux-card max-w-md w-full mx-4"
            onClick={e => e.stopPropagation()}
          >
            <h3 className="verolux-heading-3 mb-4">System Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Detection Confidence</label>
                <input
                  type="range"
                  min="0.1"
                  max="1"
                  step="0.1"
                  defaultValue="0.5"
                  className="w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Alert Sensitivity</label>
                <select className="verolux-input w-full">
                  <option>Low</option>
                  <option>Medium</option>
                  <option>High</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Video Source</label>
                <select className="verolux-input w-full" defaultValue="videoplayback.mp4">
                  <option value="file:videoplayback.mp4">videoplayback.mp4</option>
                  <option value="webcam:0">Webcam 0</option>
                  <option value="webcam:1">Webcam 1</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowSettings(false)}
                className="verolux-btn verolux-btn-outline"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowSettings(false)}
                className="verolux-btn verolux-btn-primary"
              >
                Save
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  )
}
