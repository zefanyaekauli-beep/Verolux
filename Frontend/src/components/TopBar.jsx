import React, { useState } from 'react'
import useUI from '../stores/ui'
import useStatus from '../stores/status'
import useLang from '../stores/lang'
import { ChevronDown, Globe } from 'lucide-react'

export default function TopBar(){
  const page = useUI(s=>s.currentPage)
  const st = useStatus(s=>s.status)
  const { lang, languages, setLang, t } = useLang()
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false)
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'connected': return '#10b981'
      case 'loading': return '#f59e0b'
      case 'error': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const getModelStatus = () => {
    if (st.model_loaded) return { text: 'Model Loaded', color: '#10b981', icon: '✅' }
    return { text: 'Model Not Loaded', color: '#f59e0b', icon: '⚠️' }
  }

  const modelStatus = getModelStatus()

  return (
    <div className="verolux-pattern" style={{
      position: 'fixed',
      left: 280,
      right: 0,
      top: 0,
      height: 64,
      background: 'linear-gradient(135deg, var(--verolux-surface) 0%, rgba(0, 43, 75, 0.9) 100%)',
      borderBottom: '1px solid rgba(76, 212, 176, 0.2)',
      display: 'flex',
      alignItems: 'center',
      padding: '0 24px',
      gap: '16px',
      boxShadow: '0 2px 10px rgba(0, 43, 75, 0.3)',
      backdropFilter: 'blur(10px)',
      zIndex: 999
    }}>
      {/* Page Title */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <div style={{
          width: '32px',
          height: '32px',
          background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '16px'
        }}>
          {page === 'Dashboard' ? '🏠' : 
           page === 'Cameras' ? '📹' :
           page === 'Analytics' ? '📊' :
           page === 'Reports' ? '📋' :
           page === 'Settings' ? '⚙️' : '📄'}
        </div>
        <div>
          <div style={{
            fontWeight: 600,
            fontSize: '18px',
            color: '#ffffff',
            marginBottom: '2px'
          }}>
            {page}
          </div>
          <div style={{
            fontSize: '12px',
            color: '#94a3b8'
          }}>
            {page === 'Dashboard' ? 'Security Monitoring Dashboard' :
             page === 'Cameras' ? 'Camera Management & Live Feeds' :
             page === 'Analytics' ? 'Performance Analytics & Insights' :
             page === 'Reports' ? 'Generate Security Reports' :
             page === 'Settings' ? 'System Configuration' : 'System Management'}
          </div>
        </div>
      </div>

      {/* Status Indicators */}
      <div style={{
        marginLeft: 'auto',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        {/* Framework Status */}
        <div className="verolux-badge verolux-badge-primary" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 12px',
          fontSize: '12px'
        }}>
          <div style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            backgroundColor: st.framework ? '#10b981' : '#f59e0b'
          }} />
          <span style={{ color: '#e2e8f0' }}>
            {st.framework || 'none'}
          </span>
        </div>

        {/* Model Status */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: `rgba(${modelStatus.color === '#10b981' ? '16, 185, 129' : '245, 158, 11'}, 0.1)`,
          border: `1px solid rgba(${modelStatus.color === '#10b981' ? '16, 185, 129' : '245, 158, 11'}, 0.2)`,
          borderRadius: '8px',
          padding: '6px 12px',
          fontSize: '12px'
        }}>
          <span>{modelStatus.icon}</span>
          <span style={{ color: modelStatus.color }}>
            {modelStatus.text}
          </span>
        </div>

        {/* Device Status */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.2)',
          borderRadius: '8px',
          padding: '6px 12px',
          fontSize: '12px'
        }}>
          <div style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            backgroundColor: st.device === 'cuda' ? '#10b981' : '#f59e0b'
          }} />
          <span style={{ color: '#e2e8f0' }}>
            {st.device?.toUpperCase() || 'CPU'}
          </span>
        </div>

        {/* Live Indicator */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.2)',
          borderRadius: '8px',
          padding: '6px 12px',
          fontSize: '12px'
        }}>
          <div style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            backgroundColor: '#10b981',
            animation: 'pulse 2s infinite'
          }} />
          <span style={{ color: '#10b981', fontWeight: '600' }}>
            LIVE
          </span>
        </div>

        {/* Language Selector */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowLanguageDropdown(!showLanguageDropdown)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: 'rgba(76, 212, 176, 0.1)',
              border: '1px solid rgba(76, 212, 176, 0.2)',
              borderRadius: '8px',
              padding: '6px 12px',
              fontSize: '12px',
              color: '#e2e8f0',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.target.style.background = 'rgba(76, 212, 176, 0.2)'
            }}
            onMouseLeave={(e) => {
              e.target.style.background = 'rgba(76, 212, 176, 0.1)'
            }}
          >
            <Globe size={14} />
            <span>{languages[lang]?.flag}</span>
            <span>{languages[lang]?.name}</span>
            <ChevronDown size={12} />
          </button>

          {showLanguageDropdown && (
            <div style={{
              position: 'absolute',
              top: '100%',
              right: 0,
              marginTop: '4px',
              background: 'rgba(0, 43, 75, 0.95)',
              border: '1px solid rgba(76, 212, 176, 0.2)',
              borderRadius: '8px',
              padding: '8px 0',
              minWidth: '200px',
              boxShadow: '0 4px 20px rgba(0, 43, 75, 0.5)',
              backdropFilter: 'blur(10px)',
              zIndex: 1000
            }}>
              {Object.entries(languages).map(([code, language]) => (
                <button
                  key={code}
                  onClick={() => {
                    setLang(code)
                    setShowLanguageDropdown(false)
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    width: '100%',
                    padding: '8px 16px',
                    background: lang === code ? 'rgba(76, 212, 176, 0.1)' : 'transparent',
                    border: 'none',
                    color: '#e2e8f0',
                    cursor: 'pointer',
                    fontSize: '14px',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    if (lang !== code) {
                      e.target.style.background = 'rgba(76, 212, 176, 0.05)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (lang !== code) {
                      e.target.style.background = 'transparent'
                    }
                  }}
                >
                  <span style={{ fontSize: '16px' }}>{language.flag}</span>
                  <span>{language.name}</span>
                  {lang === code && (
                    <span style={{ marginLeft: 'auto', color: '#4cd4b0' }}>✓</span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
