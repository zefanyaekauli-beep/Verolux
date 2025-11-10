import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import BodyCheckingAlert from '../components/BodyCheckingAlert'
import TestAlert from '../components/TestAlert'
import Toast from '../components/Toast'
import useAuth from '../stores/auth'

const AdvancedBodyChecking = () => {
  const { getAuthHeaders } = useAuth()
  
  // Get API base URL dynamically - use network IP if accessed via network, otherwise localhost
  const getApiBase = () => {
    const hostname = window.location.hostname
    // If accessed via IP address (network), use that IP for backend
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `http://${hostname}:8002`
    }
    // Otherwise use localhost
    return 'http://127.0.0.1:8002'
  }
  
  const [status, setStatus] = useState('connecting')
  const [detections, setDetections] = useState([])
  const [gateConfig, setGateConfig] = useState({
    gate_area: { x: 0.3, y: 0.2, width: 0.4, height: 0.6 },
    guard_anchor: { x: 0.1, y: 0.15, width: 0.15, height: 0.7 },
    enabled: true,
    examination_mode: 'sequential'
  })
  const [showGateBoxes, setShowGateBoxes] = useState(true)
  const [fps, setFps] = useState(0)
  const [bodyCheckingAlert, setBodyCheckingAlert] = useState(null)
  const [toast, setToast] = useState(null)
  const [monitoringStatus, setMonitoringStatus] = useState(null)
  
  // Advanced system state
  const [queue, setQueue] = useState([])
  const [tickets, setTickets] = useState({})
  const [guards, setGuards] = useState({})
  const [groups, setGroups] = useState({})
  const [statistics, setStatistics] = useState({})
  const [objectCounts, setObjectCounts] = useState({
    total_detected: 0,
    gate_entries: 0,
    gate_exits: 0,
    anchor_entries: 0,
    anchor_exits: 0,
    current_in_gate: 0,
    current_in_anchor: 0,
    total_passed_through: 0
  })
  const [selectedTicket, setSelectedTicket] = useState(null)
  const [showQueueDetails, setShowQueueDetails] = useState(false)
  const [videoSource, setVideoSource] = useState('file:videoplayback.mp4')
  
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const lastFrameTimeRef = useRef(Date.now())

  const showToast = (message, type = 'success') => {
    setToast({ message, type })
  }

  const connectWebSocket = () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        setStatus('error')
        showToast('Authentication required', 'error')
        return
      }
      
      const wsHost = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1' 
        ? window.location.hostname 
        : '127.0.0.1'
      const ws = new WebSocket(`ws://${wsHost}:8002/ws?token=${token}`)
      
      ws.onopen = () => {
        console.log('WebSocket connected')
        setStatus('connected')
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current)
          reconnectTimeoutRef.current = null
        }
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // Update FPS
          const now = Date.now()
          const timeDiff = now - lastFrameTimeRef.current
          if (timeDiff > 0) {
            setFps(Math.round(1000 / timeDiff))
          }
          lastFrameTimeRef.current = now
          
          // Update detections
          if (data.detections) {
            setDetections(data.detections)
          }
          
          // Update advanced system data
          if (data.queue !== undefined) setQueue(data.queue)
          if (data.tickets) setTickets(data.tickets)
          if (data.guards) setGuards(data.guards)
          if (data.groups) setGroups(data.groups)
          if (data.statistics) setStatistics(data.statistics)
          if (data.object_counts) setObjectCounts(data.object_counts)
          
          // Handle body checking alert
          if (data.body_checking_alert) {
            if (data.body_checking_alert.active) {
              setBodyCheckingAlert(data.body_checking_alert)
            } else {
              setMonitoringStatus(data.body_checking_alert)
            }
          }
          
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setStatus('disconnected')
        
        // Attempt to reconnect after 3 seconds
        if (!reconnectTimeoutRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect...')
            connectWebSocket()
          }, 3000)
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setStatus('error')
      }
      
      wsRef.current = ws
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      setStatus('error')
    }
  }

  useEffect(() => {
    connectWebSocket()
    
    // Load initial gate config
    const loadInitialConfig = async () => {
      try {
        const response = await fetch(`${getApiBase()}/config/gate`, {
          headers: getAuthHeaders()
        })
        const result = await response.json()
        if (result.config) {
          setGateConfig(result.config)
        }
      } catch (error) {
        console.error('Error loading initial gate config:', error)
      }
    }
    
    // Load initial video source
    const loadInitialVideoSource = async () => {
      try {
        const response = await fetch(`${getApiBase()}/video/source`, {
          headers: getAuthHeaders()
        })
        const result = await response.json()
        if (result.source) {
          setVideoSource(result.source)
        }
      } catch (error) {
        console.error('Error loading video source:', error)
      }
    }
    
    loadInitialConfig()
    loadInitialVideoSource()
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [])

  const updateGateConfig = async (newConfig) => {
    try {
      const response = await fetch(`${getApiBase()}/config/gate`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        },
        body: JSON.stringify(newConfig)
      })
      const result = await response.json()
      if (result.status === 'updated') {
        setGateConfig(result.config)
      }
    } catch (error) {
      console.error('Error updating gate config:', error)
    }
  }

  const getDetectionColor = (cls) => {
    const colors = {
      0: '#ff6b6b', // person
      1: '#4ecdc4', // bicycle
      2: '#45b7d1', // car
      3: '#96ceb4', // motorcycle
      4: '#feca57', // airplane
      5: '#ff9ff3', // bus
      6: '#54a0ff', // train
      7: '#5f27cd', // truck
      8: '#00d2d3', // boat
    }
    return colors[cls] || '#ffffff'
  }

  const getTicketStatusColor = (status) => {
    const colors = {
      'waiting': 'bg-yellow-500/20 text-yellow-400',
      'assigning': 'bg-blue-500/20 text-blue-400',
      'in_check': 'bg-purple-500/20 text-purple-400',
      'in_batch': 'bg-purple-500/20 text-purple-400',
      'checked': 'bg-green-500/20 text-green-400',
      'escalated': 'bg-red-500/20 text-red-400',
      'cancelled': 'bg-gray-500/20 text-gray-400',
      'verify': 'bg-orange-500/20 text-orange-400'
    }
    return colors[status] || 'bg-gray-500/20 text-gray-400'
  }

  const getTicketStatusIcon = (status) => {
    const icons = {
      'waiting': '⏳',
      'assigning': '👮',
      'in_check': '🔍',
      'in_batch': '👥',
      'checked': '✅',
      'escalated': '⚠️',
      'cancelled': '❌',
      'verify': '❓'
    }
    return icons[status] || '❓'
  }

  const formatDuration = (seconds) => {
    if (seconds < 60) return `${Math.round(seconds)}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.round(seconds % 60)
    return `${minutes}m ${remainingSeconds}s`
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleTimeString()
  }

  const cancelTicket = async (ticketId, reason = 'Manual cancellation') => {
    try {
      const response = await fetch(`${getApiBase()}/ticket/${ticketId}/cancel`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        },
        body: JSON.stringify({ reason })
      })
      const result = await response.json()
      if (result.status === 'cancelled') {
        showToast(`Ticket ${ticketId} cancelled`, 'success')
      } else {
        showToast(`Failed to cancel ticket: ${result.message}`, 'error')
      }
    } catch (error) {
      console.error('Error cancelling ticket:', error)
      showToast('Error cancelling ticket', 'error')
    }
  }

  const switchVideoSource = async (newSource) => {
    try {
      const response = await fetch(`${getApiBase()}/video/source`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        },
        body: JSON.stringify({ source: newSource })
      })
      const result = await response.json()
      if (result.status === 'updated') {
        setVideoSource(newSource)
        const sourceName = newSource.replace(':', ': ').replace('file', 'File').replace('webcam', 'Webcam')
        showToast(`Video source changed to ${sourceName}`, 'success')
        // Force video reload by updating key
        setTimeout(() => {
          const img = document.querySelector('img[alt="Live Video Stream"]')
          if (img) {
            img.src = `${getApiBase()}/stream?source=${encodeURIComponent(newSource)}&token=${encodeURIComponent(localStorage.getItem('token') || '')}`
          }
        }, 500)
      } else {
        showToast(`Failed to switch source: ${result.message}`, 'error')
      }
    } catch (error) {
      console.error('Error switching video source:', error)
      showToast('Error switching video source', 'error')
    }
  }

  const getQueuePriority = (ticket) => {
    const waitTime = Date.now() / 1000 - (ticket.ready_at || ticket.created_at)
    if (waitTime > 45) return 'critical'
    if (waitTime > 30) return 'warning'
    return 'normal'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      {/* Body Checking Alert Popup */}
      <BodyCheckingAlert 
        alert={bodyCheckingAlert} 
        onClose={() => setBodyCheckingAlert(null)} 
      />
      
      {/* Test Alert for Testing */}
      <TestAlert />
      
      {/* Toast Notifications */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          duration={3000}
          onClose={() => setToast(null)}
        />
      )}

      {/* Header */}
      <div className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">
                🎯 Advanced Body Checking System
              </h1>
              <p className="text-gray-300">Group detection, queue management & audit trail</p>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Status Indicator */}
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                status === 'connected' ? 'bg-green-500/20 text-green-400' :
                status === 'connecting' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-red-500/20 text-red-400'
              }`}>
                {status === 'connected' ? '🟢 Connected' :
                 status === 'connecting' ? '🟡 Connecting' :
                 '🔴 Disconnected'}
              </div>
              
              {/* FPS Counter */}
              <div className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm font-medium">
                📊 {fps} FPS
              </div>
              
              {/* Queue Status */}
              <div className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-sm font-medium">
                🎫 {queue.length} in queue
              </div>
              
              {/* Active Guards */}
              <div className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-medium">
                👮 {Object.values(guards).filter(g => g.is_active).length} active guards
              </div>
              
              {/* Gate Toggle */}
              <button
                onClick={() => setShowGateBoxes(!showGateBoxes)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  showGateBoxes 
                    ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30' 
                    : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30'
                }`}
              >
                {showGateBoxes ? '🎯 Hide Gates' : '🎯 Show Gates'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Video Stream */}
          <div className="lg:col-span-3">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-black rounded-xl overflow-hidden shadow-2xl"
            >
              {/* Video Feed Header */}
              <div className="bg-black/50 backdrop-blur-sm border-b border-white/10 px-4 py-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${status === 'connected' ? 'bg-green-500 animate-pulse' : status === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'}`} />
                    <h2 className="text-lg font-semibold text-white">📹 Live Camera Feed</h2>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-gray-300">
                    <span className="bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                      {fps} FPS
                    </span>
                    <span className="bg-purple-500/20 text-purple-400 px-2 py-1 rounded">
                      {detections.length} detections
                    </span>
                  </div>
                </div>
                {/* Video Source Switcher */}
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-xs text-gray-400">Source:</span>
                  <button
                    onClick={() => switchVideoSource('webcam:0')}
                    className={`px-2 py-1 rounded text-xs font-medium transition-all ${
                      videoSource === 'webcam:0' 
                        ? 'bg-blue-500/30 text-blue-400 border border-blue-500/50' 
                        : 'bg-gray-700/30 text-gray-400 hover:bg-gray-700/50 border border-gray-600/30'
                    }`}
                  >
                    📹 Webcam
                  </button>
                  <button
                    onClick={() => switchVideoSource('file:videoplayback.mp4')}
                    className={`px-2 py-1 rounded text-xs font-medium transition-all ${
                      videoSource === 'file:videoplayback.mp4' 
                        ? 'bg-blue-500/30 text-blue-400 border border-blue-500/50' 
                        : 'bg-gray-700/30 text-gray-400 hover:bg-gray-700/50 border border-gray-600/30'
                    }`}
                  >
                    🎬 Video File
                  </button>
                </div>
              </div>
              
              <div className="relative">
                <img
                  key={videoSource} // Force reload when source changes
                  src={`${getApiBase()}/stream?source=${encodeURIComponent(videoSource)}&token=${encodeURIComponent(localStorage.getItem('token') || '')}`}
                  alt="Live Video Stream"
                  className="w-full h-auto max-h-[800px] object-contain bg-gray-900"
                  style={{ minHeight: '600px' }}
                  onError={(e) => {
                    console.error('Video stream error:', videoSource)
                    e.target.style.display = 'none'
                  }}
                  onLoad={() => {
                    console.log('Video stream loaded successfully:', videoSource)
                  }}
                />
                
                {/* Loading overlay */}
                {status !== 'connected' && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                    <div className="text-center">
                      <div className="w-12 h-12 border-4 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4" />
                      <p className="text-white font-medium">
                        {status === 'connecting' ? 'Connecting to camera feed...' : 'Camera feed unavailable'}
                      </p>
                    </div>
                  </div>
                )}
              
                {/* Gate Overlay */}
                {showGateBoxes && gateConfig.enabled && (
                  <div className="absolute inset-0 pointer-events-none">
                    {/* Gate Area */}
                    <div
                      className="absolute border-4 border-green-400 rounded-lg"
                      style={{
                        left: `${gateConfig.gate_area.x * 100}%`,
                        top: `${gateConfig.gate_area.y * 100}%`,
                        width: `${gateConfig.gate_area.width * 100}%`,
                        height: `${gateConfig.gate_area.height * 100}%`,
                        boxShadow: '0 0 20px rgba(0, 255, 136, 0.5)'
                      }}
                    >
                      <div className="absolute -top-8 left-0 bg-green-400 text-white px-2 py-1 rounded text-sm font-bold">
                        🎯 GATE AREA
                      </div>
                    </div>
                    
                    {/* Guard Anchor */}
                    <div
                      className="absolute border-4 border-red-400 rounded-lg"
                      style={{
                        left: `${gateConfig.guard_anchor.x * 100}%`,
                        top: `${gateConfig.guard_anchor.y * 100}%`,
                        width: `${gateConfig.guard_anchor.width * 100}%`,
                        height: `${gateConfig.guard_anchor.height * 100}%`,
                        boxShadow: '0 0 20px rgba(255, 107, 107, 0.5)'
                      }}
                    >
                      <div className="absolute -top-8 left-0 bg-red-400 text-white px-2 py-1 rounded text-sm font-bold">
                        👮 GUARD ANCHOR
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Object Counting Statistics */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.05 }}
              className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">🔢 Object Counting</h3>
                <button
                  onClick={async () => {
                    try {
                      const response = await fetch(`${getApiBase()}/counts/reset`, {
                        method: 'POST',
                        headers: {
                          'Content-Type': 'application/json',
                          ...getAuthHeaders()
                        }
                      })
                      const result = await response.json()
                      if (result.status === 'reset') {
                        setObjectCounts(result.counts)
                        showToast('Object counts reset successfully', 'success')
                      } else {
                        showToast('Failed to reset counts', 'error')
                      }
                    } catch (error) {
                      console.error('Error resetting counts:', error)
                      showToast('Error resetting counts', 'error')
                    }
                  }}
                  className="px-2 py-1 bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded text-xs"
                  title="Reset counters (Admin only)"
                >
                  🔄 Reset
                </button>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-300">Total Detected:</span>
                  <span className="text-white font-bold">{objectCounts.total_detected || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Passed Through:</span>
                  <span className="text-green-400 font-bold">{objectCounts.total_passed_through || 0}</span>
                </div>
                <div className="border-t border-white/10 pt-2 mt-2">
                  <div className="text-xs text-gray-400 mb-2">Gate Area</div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Entries:</span>
                      <span className="text-green-400 font-bold">{objectCounts.gate_entries || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Exits:</span>
                      <span className="text-red-400 font-bold">{objectCounts.gate_exits || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Current:</span>
                      <span className="text-blue-400 font-bold">{objectCounts.current_in_gate || 0}</span>
                    </div>
                  </div>
                </div>
                <div className="border-t border-white/10 pt-2 mt-2">
                  <div className="text-xs text-gray-400 mb-2">Guard Anchor</div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Entries:</span>
                      <span className="text-green-400 font-bold">{objectCounts.anchor_entries || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Exits:</span>
                      <span className="text-red-400 font-bold">{objectCounts.anchor_exits || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Current:</span>
                      <span className="text-blue-400 font-bold">{objectCounts.current_in_anchor || 0}</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* System Statistics */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20"
            >
              <h3 className="text-lg font-bold text-white mb-4">📊 System Statistics</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-300">Queue Length:</span>
                  <span className="text-white font-bold">{statistics.current_queue_length || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Active Guards:</span>
                  <span className="text-green-400 font-bold">{statistics.active_guards || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Processed:</span>
                  <span className="text-blue-400 font-bold">{statistics.total_processed || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Escalated:</span>
                  <span className="text-red-400 font-bold">{statistics.total_escalated || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Avg Wait:</span>
                  <span className="text-yellow-400 font-bold">{formatDuration(statistics.average_wait_time || 0)}</span>
                </div>
              </div>
            </motion.div>

            {/* Queue Management */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">🎫 Queue Management</h3>
                <button
                  onClick={() => setShowQueueDetails(!showQueueDetails)}
                  className="text-blue-400 hover:text-blue-300 text-sm"
                >
                  {showQueueDetails ? 'Hide Details' : 'Show Details'}
                </button>
              </div>
              
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {queue.length === 0 ? (
                  <p className="text-gray-400 text-sm">No tickets in queue</p>
                ) : (
                  queue.slice(0, showQueueDetails ? queue.length : 3).map((ticketId, index) => {
                    const ticket = tickets[ticketId]
                    if (!ticket) return null
                    
                    const priority = getQueuePriority(ticket)
                    const waitTime = Date.now() / 1000 - (ticket.ready_at || ticket.created_at)
                    
                    return (
                      <div
                        key={ticketId}
                        className={`p-3 rounded-lg border ${
                          priority === 'critical' ? 'border-red-500/50 bg-red-500/10' :
                          priority === 'warning' ? 'border-yellow-500/50 bg-yellow-500/10' :
                          'border-white/10 bg-white/5'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <span className="text-lg">{getTicketStatusIcon(ticket.status)}</span>
                            <span className="text-white font-medium text-sm">
                              #{ticketId.slice(-6)}
                            </span>
                          </div>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getTicketStatusColor(ticket.status)}`}>
                            {ticket.status}
                          </span>
                        </div>
                        
                        <div className="text-xs text-gray-300 space-y-1">
                          <div>Type: {ticket.type}</div>
                          <div>Members: {ticket.members.length}</div>
                          <div>Wait: {formatDuration(waitTime)}</div>
                          {ticket.assigned_guard && (
                            <div>Guard: #{ticket.assigned_guard.slice(-6)}</div>
                          )}
                        </div>
                        
                        {showQueueDetails && (
                          <div className="mt-2 flex space-x-1">
                            <button
                              onClick={() => cancelTicket(ticketId)}
                              className="px-2 py-1 bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded text-xs"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={() => setSelectedTicket(ticket)}
                              className="px-2 py-1 bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 rounded text-xs"
                            >
                              Details
                            </button>
                          </div>
                        )}
                      </div>
                    )
                  })
                )}
              </div>
            </motion.div>

            {/* Active Guards */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20"
            >
              <h3 className="text-lg font-bold text-white mb-4">👮 Active Guards</h3>
              <div className="space-y-2">
                {Object.values(guards).filter(g => g.is_active).length === 0 ? (
                  <p className="text-gray-400 text-sm">No active guards</p>
                ) : (
                  Object.values(guards).filter(g => g.is_active).map(guard => (
                    <div key={guard.id} className="p-3 bg-white/5 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-white font-medium text-sm">
                          Guard #{guard.id.slice(-6)}
                        </span>
                        <span className="text-green-400 text-xs">
                          Active {formatDuration(Date.now() / 1000 - guard.active_since)}
                        </span>
                      </div>
                      {guard.current_ticket && (
                        <div className="text-xs text-gray-300 mt-1">
                          Processing: #{guard.current_ticket.slice(-6)}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </motion.div>

            {/* Gate Configuration */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20"
            >
              <h3 className="text-lg font-bold text-white mb-4">⚙️ Configuration</h3>
              <div className="space-y-4">
                {/* Examination Mode */}
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">Examination Mode:</label>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => updateGateConfig({ ...gateConfig, examination_mode: 'sequential' })}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        gateConfig.examination_mode === 'sequential'
                          ? 'bg-blue-500/20 text-blue-400' 
                          : 'bg-gray-500/20 text-gray-400'
                      }`}
                    >
                      Sequential
                    </button>
                    <button
                      onClick={() => updateGateConfig({ ...gateConfig, examination_mode: 'batch' })}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        gateConfig.examination_mode === 'batch'
                          ? 'bg-blue-500/20 text-blue-400' 
                          : 'bg-gray-500/20 text-gray-400'
                      }`}
                    >
                      Batch
                    </button>
                  </div>
                </div>
                
                {/* Gate Area Configuration */}
                <div className="border-b border-white/10 pb-4">
                  <h4 className="text-sm font-semibold text-green-400 mb-2">🎯 Gate Area</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs text-gray-300 mb-1">X Position:</label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={gateConfig.gate_area.x}
                        onChange={(e) => updateGateConfig({
                          ...gateConfig,
                          gate_area: { ...gateConfig.gate_area, x: parseFloat(e.target.value) }
                        })}
                        className="w-full"
                      />
                      <span className="text-xs text-gray-400">{gateConfig.gate_area.x.toFixed(2)}</span>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-300 mb-1">Y Position:</label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={gateConfig.gate_area.y}
                        onChange={(e) => updateGateConfig({
                          ...gateConfig,
                          gate_area: { ...gateConfig.gate_area, y: parseFloat(e.target.value) }
                        })}
                        className="w-full"
                      />
                      <span className="text-xs text-gray-400">{gateConfig.gate_area.y.toFixed(2)}</span>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-300 mb-1">Width:</label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={gateConfig.gate_area.width}
                        onChange={(e) => updateGateConfig({
                          ...gateConfig,
                          gate_area: { ...gateConfig.gate_area, width: parseFloat(e.target.value) }
                        })}
                        className="w-full"
                      />
                      <span className="text-xs text-gray-400">{gateConfig.gate_area.width.toFixed(2)}</span>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-300 mb-1">Height:</label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={gateConfig.gate_area.height}
                        onChange={(e) => updateGateConfig({
                          ...gateConfig,
                          gate_area: { ...gateConfig.gate_area, height: parseFloat(e.target.value) }
                        })}
                        className="w-full"
                      />
                      <span className="text-xs text-gray-400">{gateConfig.gate_area.height.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
                
                {/* Guard Anchor Configuration */}
                <div className="border-b border-white/10 pb-4">
                  <h4 className="text-sm font-semibold text-red-400 mb-2">👮 Guard Anchor</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs text-gray-300 mb-1">X Position:</label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={gateConfig.guard_anchor.x}
                        onChange={(e) => updateGateConfig({
                          ...gateConfig,
                          guard_anchor: { ...gateConfig.guard_anchor, x: parseFloat(e.target.value) }
                        })}
                        className="w-full"
                      />
                      <span className="text-xs text-gray-400">{gateConfig.guard_anchor.x.toFixed(2)}</span>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-300 mb-1">Y Position:</label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={gateConfig.guard_anchor.y}
                        onChange={(e) => updateGateConfig({
                          ...gateConfig,
                          guard_anchor: { ...gateConfig.guard_anchor, y: parseFloat(e.target.value) }
                        })}
                        className="w-full"
                      />
                      <span className="text-xs text-gray-400">{gateConfig.guard_anchor.y.toFixed(2)}</span>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-300 mb-1">Width:</label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={gateConfig.guard_anchor.width}
                        onChange={(e) => updateGateConfig({
                          ...gateConfig,
                          guard_anchor: { ...gateConfig.guard_anchor, width: parseFloat(e.target.value) }
                        })}
                        className="w-full"
                      />
                      <span className="text-xs text-gray-400">{gateConfig.guard_anchor.width.toFixed(2)}</span>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-300 mb-1">Height:</label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={gateConfig.guard_anchor.height}
                        onChange={(e) => updateGateConfig({
                          ...gateConfig,
                          guard_anchor: { ...gateConfig.guard_anchor, height: parseFloat(e.target.value) }
                        })}
                        className="w-full"
                      />
                      <span className="text-xs text-gray-400">{gateConfig.guard_anchor.height.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
                
                <button
                  onClick={() => updateGateConfig({ ...gateConfig, enabled: !gateConfig.enabled })}
                  className={`w-full py-2 px-4 rounded-lg font-medium transition-all ${
                    gateConfig.enabled 
                      ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30' 
                      : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30'
                  }`}
                >
                  {gateConfig.enabled ? '✅ Gates Enabled' : '❌ Gates Disabled'}
                </button>
                
                {/* Save/Load Configuration Buttons */}
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={async () => {
                      try {
                        const response = await fetch(`${getApiBase()}/config/gate/save`, {
                          method: 'POST',
                          headers: { 
                            'Content-Type': 'application/json',
                            ...getAuthHeaders()
                          }
                        })
                        const result = await response.json()
                        if (result.status === 'saved') {
                          showToast('Configuration saved successfully!', 'success')
                        } else {
                          showToast('Failed to save: ' + result.message, 'error')
                        }
                      } catch (error) {
                        console.error('Error saving config:', error)
                        showToast('Error saving configuration', 'error')
                      }
                    }}
                    className="flex-1 py-2 px-4 bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 rounded-lg font-medium transition-all"
                  >
                    💾 Save Config
                  </button>
                  <button
                    onClick={async () => {
                      try {
                        const response = await fetch(`${getApiBase()}/config/gate/load`, {
                          headers: getAuthHeaders()
                        })
                        const result = await response.json()
                        if (result.status === 'loaded') {
                          setGateConfig(result.config)
                          showToast('Configuration loaded successfully!', 'success')
                        } else if (result.status === 'not_found') {
                          showToast('No saved configuration found', 'info')
                        } else {
                          showToast('Failed to load: ' + result.message, 'error')
                        }
                      } catch (error) {
                        console.error('Error loading config:', error)
                        showToast('Error loading configuration', 'error')
                      }
                    }}
                    className="flex-1 py-2 px-4 bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 rounded-lg font-medium transition-all"
                  >
                    📂 Load Config
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Ticket Details Modal */}
      <AnimatePresence>
        {selectedTicket && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
            onClick={() => setSelectedTicket(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-gray-800 rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white">Ticket Details</h3>
                <button
                  onClick={() => setSelectedTicket(null)}
                  className="text-gray-400 hover:text-white text-2xl"
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-gray-300">Ticket ID:</label>
                    <p className="text-white font-mono">{selectedTicket.id}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-300">Status:</label>
                    <p className={`px-2 py-1 rounded text-sm font-medium ${getTicketStatusColor(selectedTicket.status)}`}>
                      {getTicketStatusIcon(selectedTicket.status)} {selectedTicket.status}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-300">Type:</label>
                    <p className="text-white">{selectedTicket.type}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-300">Examination Mode:</label>
                    <p className="text-white">{selectedTicket.examination_mode}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-300">Created:</label>
                    <p className="text-white">{formatTime(selectedTicket.created_at)}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-300">Ready:</label>
                    <p className="text-white">{selectedTicket.ready_at ? formatTime(selectedTicket.ready_at) : 'N/A'}</p>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm text-gray-300">Members ({selectedTicket.members.length}):</label>
                  <div className="mt-2 space-y-1">
                    {selectedTicket.members.map((memberId, index) => (
                      <div key={memberId} className="text-white font-mono text-sm bg-white/5 p-2 rounded">
                        #{memberId.slice(-8)}
                      </div>
                    ))}
                  </div>
                </div>
                
                {selectedTicket.assigned_guard && (
                  <div>
                    <label className="text-sm text-gray-300">Assigned Guard:</label>
                    <p className="text-white font-mono">#{selectedTicket.assigned_guard.slice(-8)}</p>
                  </div>
                )}
                
                {selectedTicket.escalated_reason && (
                  <div>
                    <label className="text-sm text-gray-300">Escalation Reason:</label>
                    <p className="text-red-400">{selectedTicket.escalated_reason}</p>
                  </div>
                )}
                
                <div className="flex space-x-2 pt-4">
                  <button
                    onClick={() => cancelTicket(selectedTicket.id)}
                    className="px-4 py-2 bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded-lg font-medium"
                  >
                    Cancel Ticket
                  </button>
                  <button
                    onClick={() => setSelectedTicket(null)}
                    className="px-4 py-2 bg-gray-500/20 text-gray-400 hover:bg-gray-500/30 rounded-lg font-medium"
                  >
                    Close
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default AdvancedBodyChecking
