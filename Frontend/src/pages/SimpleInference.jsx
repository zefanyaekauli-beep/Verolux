import React, { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import BodyCheckingAlert from '../components/BodyCheckingAlert'
import TestAlert from '../components/TestAlert'
import Toast from '../components/Toast'

const SimpleInference = () => {
  const [status, setStatus] = useState('connecting')
  const [detections, setDetections] = useState([])
  const [gateConfig, setGateConfig] = useState({
    gate_area: { x: 0.3, y: 0.2, width: 0.4, height: 0.6 },
    guard_anchor: { x: 0.1, y: 0.15, width: 0.15, height: 0.7 },
    enabled: true
  })
  const [showGateBoxes, setShowGateBoxes] = useState(true)
  const [fps, setFps] = useState(0)
  const [bodyCheckingAlert, setBodyCheckingAlert] = useState(null)
  const [toast, setToast] = useState(null)
  const [monitoringStatus, setMonitoringStatus] = useState(null)
  
  const wsRef = useRef(null)
  const fpsRef = useRef(0)
  const lastTimeRef = useRef(Date.now())

  useEffect(() => {
    let closed = false
    
    const connectWebSocket = () => {
      try {
        // Use 127.0.0.1 instead of localhost for better compatibility
        const ws = new WebSocket('ws://127.0.0.1:8002/ws')
        wsRef.current = ws
        
        ws.onopen = () => {
          console.log('WebSocket connected')
          setStatus('connected')
        }
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            console.log('WebSocket message received:', data.type)
            
            if (data.type === 'hello') {
              console.log('WebSocket hello received:', data.message)
              return
            }
            
            if (data.type === 'detection') {
              setDetections(data.detections || [])
              setGateConfig(data.gate_config || gateConfig)
              
              // Handle body checking alert
              if (data.body_checking_alert) {
                console.log('Body checking alert received:', data.body_checking_alert)
                console.log('Alert active:', data.body_checking_alert.active, 'People count:', data.body_checking_alert.people_count)
                if (data.body_checking_alert.active) {
                  setBodyCheckingAlert(data.body_checking_alert)
                  setMonitoringStatus(null)
                } else {
                  // Show monitoring status
                  setMonitoringStatus(data.body_checking_alert)
                  setBodyCheckingAlert(null)
                }
              } else {
                setBodyCheckingAlert(null)
                setMonitoringStatus(null)
              }
              
              // Calculate FPS
              const now = Date.now()
              const delta = now - lastTimeRef.current
              if (delta > 0) {
                fpsRef.current = 1000 / delta
                setFps(Math.round(fpsRef.current))
              }
              lastTimeRef.current = now
            }
          } catch (e) {
            console.error('Error parsing WebSocket message:', e)
            console.error('Raw message:', event.data)
          }
        }
        
        ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          setStatus('disconnected')
          if (!closed) {
            console.log('Attempting to reconnect in 3 seconds...')
            setTimeout(connectWebSocket, 3000)
          }
        }
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          setStatus('error')
        }
      } catch (error) {
        console.error('WebSocket connection error:', error)
        setStatus('error')
      }
    }
    
    connectWebSocket()
    
    return () => {
      closed = true
      if (wsRef.current) {
        console.log('Closing WebSocket connection...')
        wsRef.current.close(1000, 'Component unmounting')
        wsRef.current = null
      }
    }
  }, [])

  const updateGateConfig = async (newConfig) => {
    try {
      const response = await fetch('http://127.0.0.1:8002/config/gate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newConfig)
      })
      
      if (response.ok) {
        setGateConfig(newConfig)
      }
    } catch (error) {
      console.error('Error updating gate config:', error)
    }
  }

  const showToast = (message, type = 'success') => {
    setToast({ message, type })
  }

  const getDetectionColor = (className) => {
    const colors = {
      'person': '#00ff88',
      'car': '#ff6b6b',
      'truck': '#4ecdc4',
      'bus': '#45b7d1',
      'bicycle': '#96ceb4',
      'motorcycle': '#feca57'
    }
    return colors[className] || '#ffffff'
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
                🎯 Simple Video Inference System
              </h1>
              <p className="text-gray-300">Real-time object detection with gate features</p>
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
              
              {/* Monitoring Status */}
              {monitoringStatus && (
                <div className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-sm font-medium">
                  👁️ {monitoringStatus.people_count} people • {monitoringStatus.person_in_gate ? 'Person in gate' : 'No person'} • {monitoringStatus.guard_present ? 'Guard present' : 'No guard'}
                </div>
              )}
              
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
                 <div className="relative">
                   <img
                     src="http://127.0.0.1:8002/stream?source=file%3Avideoplayback.mp4"
                     alt="Video Stream"
                     className="w-full h-auto max-h-[800px] object-contain"
                     style={{ minHeight: '600px' }}
                   />
                
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
            {/* Detection Stats */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20"
            >
              <h3 className="text-lg font-bold text-white mb-4">📊 Detection Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-300">Total Objects:</span>
                  <span className="text-white font-bold">{detections.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">FPS:</span>
                  <span className="text-blue-400 font-bold">{fps}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Status:</span>
                  <span className={`font-bold ${
                    status === 'connected' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {status}
                  </span>
                </div>
              </div>
            </motion.div>

            {/* Current Detections */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20"
            >
              <h3 className="text-lg font-bold text-white mb-4">🎯 Current Detections</h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {detections.length === 0 ? (
                  <p className="text-gray-400 text-sm">No objects detected</p>
                ) : (
                  detections.map((detection, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-white/5 rounded-lg"
                    >
                      <div className="flex items-center space-x-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: getDetectionColor(detection.cls) }}
                        />
                        <span className="text-white font-medium">{detection.cls}</span>
                      </div>
                      <span className="text-gray-400 text-sm">
                        {Math.round(detection.conf * 100)}%
                      </span>
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
              <h3 className="text-lg font-bold text-white mb-4">⚙️ Gate Configuration</h3>
              <div className="space-y-4">
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
                        const response = await fetch('http://127.0.0.1:8002/config/gate/save', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' }
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
                        const response = await fetch('http://127.0.0.1:8002/config/gate/load')
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
    </div>
  )
}

export default SimpleInference
