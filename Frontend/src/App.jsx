import React, { useEffect, Suspense, lazy } from 'react'
import useUI from './stores/ui'
import useAuth from './stores/auth'
import useStatus from './stores/status'

// Lazy load components for better error handling
const Sidebar = lazy(() => import('./components/Sidebar'))
const TopBar = lazy(() => import('./components/TopBar'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Cameras = lazy(() => import('./pages/Cameras'))
const SemanticSearch = lazy(() => import('./pages/SemanticSearch'))
const Analytics = lazy(() => import('./pages/Analytics'))
const Reports = lazy(() => import('./pages/Reports'))
const Heatmap = lazy(() => import('./pages/Heatmap'))
const Settings = lazy(() => import('./pages/Settings'))
const GateConfigEditor = lazy(() => import('./components/GateConfigEditor'))
const GateSecurity = lazy(() => import('./pages/GateSecurity'))
const DiagnosticPage = lazy(() => import('./pages/DiagnosticPage'))
const VideoplaybackDemo = lazy(() => import('./pages/VideoplaybackDemo'))
const SimpleInference = lazy(() => import('./pages/SimpleInference'))

const LoadingSpinner = () => (
  <div style={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '400px',
    color: 'white'
  }}>
    <div style={{textAlign: 'center'}}>
      <div style={{
        border: '4px solid rgba(76, 212, 176, 0.3)',
        borderTop: '4px solid #4CD4B0',
        borderRadius: '50%',
        width: '50px',
        height: '50px',
        animation: 'spin 1s linear infinite',
        margin: '0 auto 20px'
      }}></div>
      <p>Loading...</p>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  </div>
)

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
    case 'GateConfig': return <GateSecurity/>
    case 'GateConfigEditor': return <GateConfigEditor/>
    case 'Diagnostic': return <DiagnosticPage/>
    case 'VideoplaybackDemo': return <VideoplaybackDemo/>
    case 'SimpleInference': return <SimpleInference/>
    default: return <Dashboard/>
  }
}

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '20px',
          background: '#002B4B',
          color: 'white',
          minHeight: '100vh'
        }}>
          <h1>⚠️ Something went wrong</h1>
          <p>Error: {this.state.error?.message}</p>
          <button 
            onClick={() => window.location.reload()}
            style={{
              padding: '10px 20px',
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              marginTop: '10px'
            }}
          >
            Reload Page
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

export default function App(){
  const page = useUI(s=>s.currentPage)
  const { user, login } = useAuth()
  const setStatus = useStatus(s=>s.setStatus)

  useEffect(()=>{
    let stop = false
    const tick = async () => {
      try { 
        const r = await fetch('http://127.0.0.1:8002/health')
        const j = await r.json()
        setStatus({ 
          model_loaded: !!j?.model?.loaded, 
          device: j?.model?.device || 'cpu', 
          framework: j?.model?.framework || 'none' 
        }) 
      } catch (e) {
        // Silently fail health check
      }
      if (!stop) setTimeout(tick, 5000)
    }
    tick()
    return ()=>{ stop = true }
  }, [setStatus])

  return (
    <ErrorBoundary>
      <div>
        <Suspense fallback={<LoadingSpinner/>}>
          <Sidebar/>
          <TopBar/>
        </Suspense>
        <div style={{marginLeft: 280, marginTop: 64, padding: 24}}>
          {user ? (
            <Suspense fallback={<LoadingSpinner/>}>
              <Router page={page}/>
            </Suspense>
          ) : (
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
    </ErrorBoundary>
  )
}
