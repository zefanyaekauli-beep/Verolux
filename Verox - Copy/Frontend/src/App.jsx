import React, { useEffect } from 'react'
import Sidebar from './components/Sidebar'
import TopBar from './components/TopBar'
import useUI from './stores/ui'
import useAuth from './stores/auth'
import useStatus from './stores/status'

import Dashboard from './pages/Dashboard'
import Cameras from './pages/Cameras'
import SemanticSearch from './pages/SemanticSearch'
import Analytics from './pages/Analytics'
import Reports from './pages/Reports'
import Heatmap from './pages/Heatmap'
import Settings from './pages/Settings'

const Router = ({ page }) => {
  switch(page){
    case 'Dashboard': return <Dashboard/>
    case 'Cameras': return <Cameras/>
    case 'SemanticSearch': return <SemanticSearch/>
    case 'Analytics': return <Analytics/>
    case 'Reports': 
    case 'Overview': 
    case 'Object Counts': 
    case 'Zone Analytics': 
    case 'Compliance': 
    case 'Violations': 
    case 'Alerts & Events': 
    case 'Traffic Patterns': 
    case 'Line Crossing': 
    case 'Loitering': 
    case 'Intrusion': 
    case 'Hazards': 
    case 'Anomaly Detection': return <Reports/>
    case 'Heatmap': return <Heatmap/>
    case 'Settings': return <Settings/>
    default: return <Dashboard/>
  }
}

export default function App(){
  const page = useUI(s=>s.currentPage)
  const { user, login } = useAuth()
  const setStatus = useStatus(s=>s.setStatus)

  useEffect(()=>{
    let stop = false
    const tick = async () => {
      try { const r = await fetch('/health'); const j = await r.json(); setStatus({ model_loaded: !!j?.model?.loaded, device: j?.model?.device || 'cpu', framework: j?.model?.framework || 'none' }) } catch {}
      if (!stop) setTimeout(tick, 5000)
    }
    tick()
    return ()=>{ stop = True => False }
  }, [])

  return (
    <div>
      <Sidebar/>
      <TopBar/>
      <div style={{marginLeft:280, marginTop:64, padding:24}}>
        {user ? <Router page={page}/> : (
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: 'calc(100vh - 120px)',
            padding: '20px'
          }}>
            <div className='card' style={{
              maxWidth: 480,
              width: '100%',
              textAlign: 'center',
              background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
              border: '1px solid #334155',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)'
            }}>
              <div style={{
                width: '80px',
                height: '80px',
                background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                borderRadius: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 24px',
                fontSize: '32px'
              }}>
                🛡️
              </div>
              <h2 style={{ margin: '0 0 8px 0', color: '#ffffff', fontSize: '24px' }}>
                Welcome to Verolux1st
              </h2>
              <p style={{ margin: '0 0 24px 0', color: '#94a3b8', fontSize: '16px' }}>
                Security Intelligence Platform
              </p>
              <div style={{
                background: 'rgba(59, 130, 246, 0.1)',
                border: '1px solid rgba(59, 130, 246, 0.2)',
                borderRadius: '12px',
                padding: '20px',
                marginBottom: '24px'
              }}>
                <h3 style={{ margin: '0 0 12px 0', color: '#ffffff' }}>Quick Login</h3>
                <p style={{ margin: '0 0 16px 0', color: '#e2e8f0', fontSize: '14px' }}>
                  Choose your access level:
                </p>
                <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                  <button
                    onClick={() => login('admin', 'admin')}
                    style={{
                      background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                      border: 'none',
                      borderRadius: '8px',
                      padding: '12px 20px',
                      color: '#ffffff',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: '600',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    🔐 Admin Access
                  </button>
                  <button
                    onClick={() => login('viewer', 'viewer')}
                    style={{
                      background: 'linear-gradient(135deg, #10b981, #059669)',
                      border: 'none',
                      borderRadius: '8px',
                      padding: '12px 20px',
                      color: '#ffffff',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: '600',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    👁️ Viewer Access
                  </button>
                </div>
              </div>
              <div style={{
                fontSize: '12px',
                color: '#64748b',
                lineHeight: '1.5'
              }}>
                <p style={{ margin: '0' }}>
                  <strong>Admin:</strong> Full system access and configuration<br/>
                  <strong>Viewer:</strong> Read-only monitoring and reports
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
