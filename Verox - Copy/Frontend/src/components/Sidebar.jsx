import React, { useState } from 'react'
import useUI from '../stores/ui'
import useAuth from '../stores/auth'
import useLang from '../stores/lang'

const items = [
  { name: 'dashboard', icon: '🏠', page: 'Dashboard' },
  { name: 'cameras', icon: '📹', page: 'Cameras' },
  { name: 'semanticSearch', icon: '🧠', page: 'SemanticSearch' },
  { name: 'analytics', icon: '📊', page: 'Analytics' },
  { 
    name: 'reports', 
    icon: '📋', 
    page: 'Reports',
    hasSubmenu: true,
    submenu: [
      { name: 'overview', icon: '📊', page: 'Overview' },
      { name: 'objectCounts', icon: '👥', page: 'Object Counts' },
      { name: 'zoneAnalytics', icon: '📍', page: 'Zone Analytics' },
      { name: 'compliance', icon: '🛡️', page: 'Compliance' },
      { name: 'violations', icon: '⚠️', page: 'Violations' },
      { name: 'alertsEvents', icon: '🔺', page: 'Alerts & Events' },
      { name: 'trafficPatterns', icon: '📈', page: 'Traffic Patterns' },
      { name: 'lineCrossing', icon: '🎯', page: 'Line Crossing' },
      { name: 'loitering', icon: '🕐', page: 'Loitering' },
      { name: 'intrusion', icon: '🚨', page: 'Intrusion' },
      { name: 'hazards', icon: '⚠️', page: 'Hazards' },
      { name: 'anomalyDetection', icon: '🧠', page: 'Anomaly Detection' }
    ]
  },
  { name: 'heatmap', icon: '🗺️', page: 'Heatmap' },
  { name: 'settings', icon: '⚙️', page: 'Settings' }
]

export default function Sidebar(){
  const page = useUI(s=>s.currentPage)
  const setPage = useUI(s=>s.setPage)
  const { user, login, logout } = useAuth()
  const { t } = useLang()
  const [openDropdowns, setOpenDropdowns] = useState({})
  
  const toggleDropdown = (itemName) => {
    setOpenDropdowns(prev => ({
      ...prev,
      [itemName]: !prev[itemName]
    }))
  }
  
  const isDropdownOpen = (itemName) => openDropdowns[itemName] || false
  
  const isPageActive = (itemPage) => page === itemPage
  const isSubmenuPageActive = (submenu) => submenu.some(subItem => page === subItem.page)
  
  return (
    <>
      <style jsx="true">{`
        .sidebar-scroll::-webkit-scrollbar {
          width: 6px;
        }
        .sidebar-scroll::-webkit-scrollbar-track {
          background: transparent;
        }
        .sidebar-scroll::-webkit-scrollbar-thumb {
          background: rgba(76, 212, 176, 0.3);
          border-radius: 3px;
        }
        .sidebar-scroll::-webkit-scrollbar-thumb:hover {
          background: rgba(76, 212, 176, 0.5);
        }
      `}</style>
      <div className="verolux-pattern" style={{
      width: 280,
      background: 'linear-gradient(180deg, var(--verolux-surface) 0%, rgba(0, 43, 75, 0.9) 100%)',
      height: '100vh',
      position: 'fixed',
      left: 0,
      top: 0,
      borderRight: '1px solid rgba(76, 212, 176, 0.2)',
      boxShadow: '4px 0 20px rgba(0, 43, 75, 0.3)',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header Section - Fixed */}
      <div style={{ padding: '24px 20px 0 20px' }}>
        {/* Verolux1st Logo and Brand */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          marginBottom: '32px',
          paddingBottom: '20px',
          borderBottom: '1px solid rgba(76, 212, 176, 0.2)'
        }}>
        <div style={{
          width: '48px',
          height: '48px',
          background: 'linear-gradient(135deg, var(--verolux-secondary), var(--verolux-accent))',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginRight: '12px',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: '0 4px 15px rgba(76, 212, 176, 0.3)'
        }}>
          {/* Verolux1st Logo Icon */}
          <div style={{
            width: '28px',
            height: '28px',
            position: 'relative'
          }}>
            {/* V shape - left part (gold) */}
            <div style={{
              position: 'absolute',
              left: '2px',
              top: '6px',
              width: '10px',
              height: '16px',
              background: 'var(--verolux-accent)',
              borderRadius: '5px 0 0 5px',
              transform: 'skewY(-15deg)'
            }} />
            {/* V shape - right part (turquoise) */}
            <div style={{
              position: 'absolute',
              right: '2px',
              top: '6px',
              width: '10px',
              height: '16px',
              background: 'var(--verolux-secondary)',
              borderRadius: '0 5px 5px 0',
              transform: 'skewY(15deg)'
            }} />
          </div>
        </div>
        <div>
          <div className="verolux-heading-3" style={{ margin: '0 0 2px 0' }}>
            Verolux1st
          </div>
          <div className="verolux-caption">
            Security Intelligence
          </div>
        </div>
      </div>

      {/* User Info */}
      <div className="verolux-card" style={{
        padding: '16px',
        marginBottom: '24px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          marginBottom: '8px'
        }}>
          <div style={{
            width: '32px',
            height: '32px',
            background: 'linear-gradient(135deg, #10b981, #059669)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginRight: '12px',
            fontSize: '14px'
          }}>
            👤
          </div>
          <div>
            <div className="verolux-body" style={{ fontWeight: '600' }}>
              {user ? user.username : 'Guest'}
            </div>
            <div className="verolux-caption">
              {user ? user.role : 'Not signed in'}
            </div>
          </div>
        </div>
      </div>
      </div>

      {/* Scrollable Navigation Area */}
      <div className="sidebar-scroll" style={{ 
        flex: 1, 
        overflowY: 'auto', 
        padding: '0 20px 20px 20px',
        scrollbarWidth: 'thin',
        scrollbarColor: 'rgba(76, 212, 176, 0.3) transparent'
      }}>
        {/* Navigation */}
        <nav style={{ marginBottom: '24px' }}>
        {items.map(item => (
          <div key={item.page} style={{ marginBottom: '8px' }}>
            {/* Main Menu Item */}
            <button
              onClick={() => {
                if (item.hasSubmenu) {
                  toggleDropdown(item.name)
                } else {
                  setPage(item.page)
                }
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                width: '100%',
                textAlign: 'left',
                padding: '12px 16px',
                borderRadius: '12px',
                border: 'none',
                background: (isPageActive(item.page) || (item.hasSubmenu && isSubmenuPageActive(item.submenu)))
                  ? 'linear-gradient(135deg, var(--verolux-secondary), var(--verolux-accent))' 
                  : 'transparent',
                color: (isPageActive(item.page) || (item.hasSubmenu && isSubmenuPageActive(item.submenu)))
                  ? 'var(--verolux-white)' 
                  : 'var(--verolux-text-primary)',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                fontSize: '14px',
                fontWeight: '500'
              }}
              onMouseOver={(e) => {
                if (!isPageActive(item.page) && !(item.hasSubmenu && isSubmenuPageActive(item.submenu))) {
                  e.target.style.background = 'rgba(76, 212, 176, 0.1)'
                  e.target.style.color = 'var(--verolux-white)'
                }
              }}
              onMouseOut={(e) => {
                if (!isPageActive(item.page) && !(item.hasSubmenu && isSubmenuPageActive(item.submenu))) {
                  e.target.style.background = 'transparent'
                  e.target.style.color = 'var(--verolux-text-primary)'
                }
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <span style={{ marginRight: '12px', fontSize: '16px' }}>
                  {item.icon}
                </span>
                {t(item.name)}
              </div>
              {item.hasSubmenu && (
                <span style={{ 
                  fontSize: '12px', 
                  transform: isDropdownOpen(item.name) ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.2s ease'
                }}>
                  ▼
                </span>
              )}
            </button>
            
            {/* Submenu */}
            {item.hasSubmenu && isDropdownOpen(item.name) && (
              <div style={{ 
                marginLeft: '20px', 
                marginTop: '4px',
                borderLeft: '2px solid rgba(76, 212, 176, 0.3)',
                paddingLeft: '12px',
                backgroundColor: 'rgba(76, 212, 176, 0.1)',
                borderRadius: '8px',
                padding: '8px',
                margin: '4px 0 4px 20px'
              }}>
                {item.submenu.map(subItem => (
                  <button
                    key={subItem.page}
                    onClick={() => setPage(subItem.page)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      width: '100%',
                      textAlign: 'left',
                      padding: '8px 12px',
                      marginBottom: '4px',
                      borderRadius: '8px',
                      border: 'none',
                      background: isPageActive(subItem.page)
                        ? 'rgba(76, 212, 176, 0.2)'
                        : 'transparent',
                      color: isPageActive(subItem.page)
                        ? 'var(--verolux-white)'
                        : 'var(--verolux-text-secondary)',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      fontSize: '13px',
                      fontWeight: '400'
                    }}
                    onMouseOver={(e) => {
                      if (!isPageActive(subItem.page)) {
                        e.target.style.background = 'rgba(76, 212, 176, 0.1)'
                        e.target.style.color = 'var(--verolux-white)'
                      }
                    }}
                    onMouseOut={(e) => {
                      if (!isPageActive(subItem.page)) {
                        e.target.style.background = 'transparent'
                        e.target.style.color = 'var(--verolux-text-secondary)'
                      }
                    }}
                  >
                    <span style={{ marginRight: '8px', fontSize: '14px' }}>
                      {subItem.icon}
                    </span>
                    {t(subItem.name)}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
        </nav>
      </div>

      {/* Fixed Footer - Auth Section */}
      <div style={{
        padding: '20px',
        borderTop: '1px solid #334155',
        background: 'rgba(0, 43, 75, 0.9)'
      }}>
        {user ? (
          <button
            onClick={logout}
            className="verolux-btn verolux-btn-secondary"
            style={{
              width: '100%',
              background: 'linear-gradient(135deg, var(--verolux-error), #dc2626)',
              border: 'none',
              borderRadius: '12px',
              padding: '12px 16px',
              color: 'var(--verolux-white)',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => {
              e.target.style.transform = 'translateY(-1px)'
              e.target.style.boxShadow = '0 4px 12px rgba(239, 68, 68, 0.3)'
            }}
            onMouseOut={(e) => {
              e.target.style.transform = 'translateY(0)'
              e.target.style.boxShadow = 'none'
            }}
          >
            🚪 Logout
          </button>
        ) : (
          <button
            onClick={() => login('admin', 'admin')}
            className="verolux-btn verolux-btn-primary"
            style={{
              width: '100%',
              background: 'linear-gradient(135deg, var(--verolux-secondary), var(--verolux-accent))',
              border: 'none',
              borderRadius: '12px',
              padding: '12px 16px',
              color: 'var(--verolux-white)',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => {
              e.target.style.transform = 'translateY(-1px)'
              e.target.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.3)'
            }}
            onMouseOut={(e) => {
              e.target.style.transform = 'translateY(0)'
              e.target.style.boxShadow = 'none'
            }}
          >
            🔐 Login as Admin
          </button>
        )}
      </div>
      </div>
    </>
  )
}
