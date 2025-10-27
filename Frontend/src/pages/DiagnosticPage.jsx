import React, { useState, useEffect } from 'react'

export default function DiagnosticPage() {
  const [backendStatus, setBackendStatus] = useState('checking...')
  const [streamStatus, setStreamStatus] = useState('checking...')
  const [healthData, setHealthData] = useState(null)

  useEffect(() => {
    // Check backend health
    fetch('/health')
      .then(res => res.json())
      .then(data => {
        setBackendStatus('✅ Connected')
        setHealthData(data)
      })
      .catch(err => {
        setBackendStatus('❌ Not connected: ' + err.message)
      })

    // Check stream endpoint
    fetch('/stream?source=webcam:0')
      .then(res => {
        if (res.ok) {
          setStreamStatus('✅ Stream endpoint accessible')
        } else {
          setStreamStatus('❌ Stream endpoint error: ' + res.status)
        }
      })
      .catch(err => {
        setStreamStatus('❌ Stream not accessible: ' + err.message)
      })
  }, [])

  return (
    <div style={{
      padding: '20px',
      color: 'white',
      minHeight: '100vh'
    }}>
      <h1>🔧 System Diagnostics</h1>
      
      <div style={{
        background: 'rgba(76, 212, 176, 0.1)',
        padding: '20px',
        borderRadius: '10px',
        marginTop: '20px',
        border: '1px solid rgba(76, 212, 176, 0.3)'
      }}>
        <h2>Backend Status</h2>
        <p><strong>Connection:</strong> {backendStatus}</p>
        {healthData && (
          <div>
            <p><strong>Model Loaded:</strong> {healthData.model?.loaded ? '✅ Yes' : '❌ No'}</p>
            <p><strong>Device:</strong> {healthData.model?.device || 'Unknown'}</p>
            <p><strong>Framework:</strong> {healthData.model?.framework || 'None'}</p>
          </div>
        )}
      </div>

      <div style={{
        background: 'rgba(76, 212, 176, 0.1)',
        padding: '20px',
        borderRadius: '10px',
        marginTop: '20px',
        border: '1px solid rgba(76, 212, 176, 0.3)'
      }}>
        <h2>Stream Status</h2>
        <p><strong>Stream Endpoint:</strong> {streamStatus}</p>
        <p><strong>Stream URL:</strong> http://127.0.0.1:8002/stream?source=webcam:0</p>
        
        <div style={{ marginTop: '20px' }}>
          <h3>Test Stream Display:</h3>
          <img 
            src="/stream?source=webcam:0" 
            alt="Video Stream"
            style={{
              maxWidth: '100%',
              border: '2px solid #4CD4B0',
              borderRadius: '8px',
              marginTop: '10px'
            }}
            onError={(e) => {
              e.target.style.display = 'none'
              e.target.nextSibling.style.display = 'block'
            }}
          />
          <div style={{ 
            display: 'none', 
            padding: '20px', 
            background: 'rgba(239, 68, 68, 0.2)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            marginTop: '10px'
          }}>
            ❌ Stream failed to load. Possible issues:
            <ul>
              <li>Webcam not connected or in use</li>
              <li>Backend server not running</li>
              <li>Permissions denied for camera access</li>
            </ul>
          </div>
        </div>
      </div>

      <div style={{
        background: 'rgba(76, 212, 176, 0.1)',
        padding: '20px',
        borderRadius: '10px',
        marginTop: '20px',
        border: '1px solid rgba(76, 212, 176, 0.3)'
      }}>
        <h2>Troubleshooting Steps</h2>
        <ol>
          <li>Check if webcam is connected and not in use by another application</li>
          <li>Restart the backend server (close the Backend window and run QUICK_START.bat again)</li>
          <li>Try accessing the stream directly: <a href="http://127.0.0.1:8002/stream?source=webcam:0" target="_blank" style={{color: '#4CD4B0'}}>http://127.0.0.1:8002/stream?source=webcam:0</a></li>
          <li>Check backend console for error messages</li>
        </ol>
      </div>

      <div style={{ marginTop: '20px' }}>
        <button
          onClick={() => window.location.reload()}
          style={{
            padding: '12px 24px',
            background: 'linear-gradient(135deg, #4CD4B0, #3BC4A0)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: 'bold'
          }}
        >
          🔄 Refresh Diagnostics
        </button>
      </div>
    </div>
  )
}






















