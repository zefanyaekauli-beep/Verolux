import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Shield, Video, Activity, CheckCircle, XCircle, Clock, Users,
  Settings, Download, Upload, RefreshCw, Save, Eye, AlertTriangle,
  TrendingUp, BarChart3, MapPin, Target, Zap, FileText, Edit3
} from 'lucide-react'
import GateConfigEditor from '../components/GateConfigEditor'
import GateConfigEditorLive from '../components/GateConfigEditorLive'

export default function GateSecurity() {
  const [activeTab, setActiveTab] = useState('overview')
  const [gateStats, setGateStats] = useState(null)
  const [completions, setCompletions] = useState([])
  const [liveStream, setLiveStream] = useState(null)
  const [loading, setLoading] = useState(false)
  const [editorMode, setEditorMode] = useState('live')

  // Fetch gate statistics
  useEffect(() => {
    fetchGateStats()
    fetchCompletions()
    const interval = setInterval(() => {
      fetchGateStats()
      fetchCompletions()
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchGateStats = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8002/gate/stats')
      if (response.ok) {
        const data = await response.json()
        setGateStats(data)
      }
    } catch (error) {
      console.error('Error fetching gate stats:', error)
      setGateStats({}) // Set empty object on error
    }
  }

  const fetchCompletions = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8002/gate/completions?limit=10')
      if (response.ok) {
        const data = await response.json()
        setCompletions(data.completions || [])
      }
    } catch (error) {
      console.error('Error fetching completions:', error)
      setCompletions([]) // Set empty array on error
    }
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Shield },
    { id: 'live', label: 'Live Monitor', icon: Video },
    { id: 'config', label: 'Configuration', icon: Settings },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'completions', label: 'Check History', icon: FileText }
  ]

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ 
        padding: '24px 32px',
        borderBottom: '1px solid rgba(76, 212, 176, 0.2)',
        background: 'linear-gradient(135deg, rgba(76, 212, 176, 0.1), rgba(0, 43, 75, 0.3))'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'linear-gradient(135deg, var(--verolux-secondary), var(--verolux-accent))',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Shield size={24} color="white" />
            </div>
            <div>
              <h2 style={{ margin: 0, fontSize: '28px', fontWeight: 700 }}>Gate Security System</h2>
              <p style={{ margin: '4px 0 0 0', opacity: 0.7, fontSize: '14px' }}>
                AI-Powered Checkpoint Monitoring & Management
              </p>
            </div>
          </div>
          
          {gateStats && (
            <div style={{ display: 'flex', gap: '24px' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--verolux-accent)' }}>
                  {gateStats.total_completions || 0}
                </div>
                <div style={{ fontSize: '12px', opacity: 0.7 }}>Total Checks</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--verolux-secondary)' }}>
                  {gateStats.current_state?.active_tracks || 0}
                </div>
                <div style={{ fontSize: '12px', opacity: 0.7 }}>Active Tracks</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px', fontWeight: 700, color: '#22c55e' }}>
                  {gateStats.current_state?.decision_engine?.total_persons || 0}
                </div>
                <div style={{ fontSize: '12px', opacity: 0.7 }}>Persons</div>
              </div>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: '8px', marginTop: '24px' }}>
          {tabs.map(tab => {
            const Icon = tab.icon
            return (
              <motion.button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: '12px 24px',
                  background: activeTab === tab.id 
                    ? 'linear-gradient(135deg, var(--verolux-secondary), var(--verolux-accent))'
                    : 'rgba(255, 255, 255, 0.05)',
                  border: activeTab === tab.id 
                    ? '1px solid var(--verolux-accent)'
                    : '1px solid rgba(76, 212, 176, 0.2)',
                  borderRadius: '8px',
                  color: 'white',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '14px',
                  fontWeight: activeTab === tab.id ? 600 : 400,
                  transition: 'all 0.3s ease'
                }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Icon size={16} />
                {tab.label}
              </motion.button>
            )
          })}
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '32px' }}>
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <OverviewTab gateStats={gateStats} completions={completions} />
          )}
          {activeTab === 'live' && (
            <LiveMonitorTab />
          )}
          {activeTab === 'config' && (
            <ConfigTab editorMode={editorMode} setEditorMode={setEditorMode} />
          )}
          {activeTab === 'analytics' && (
            <AnalyticsTab gateStats={gateStats} />
          )}
          {activeTab === 'completions' && (
            <CompletionsTab completions={completions} />
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

// Overview Tab Component
function OverviewTab({ gateStats, completions }) {
  const recentCompletions = completions.slice(0, 5)
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', marginBottom: '32px' }}>
        {/* Status Cards */}
        <StatusCard
          title="System Status"
          value="Active"
          icon={CheckCircle}
          color="#22c55e"
          subtitle="All systems operational"
        />
        <StatusCard
          title="Current Activity"
          value={gateStats?.current_state?.active_tracks || 0}
          icon={Activity}
          color="var(--verolux-accent)"
          subtitle="Active tracking sessions"
        />
        <StatusCard
          title="Today's Checks"
          value={gateStats?.today_count || 0}
          icon={Shield}
          color="var(--verolux-secondary)"
          subtitle="Completed security checks"
        />
        <StatusCard
          title="Avg Check Time"
          value={
            gateStats?.avg_duration && typeof gateStats.avg_duration === 'number'
              ? `${gateStats.avg_duration.toFixed(1)}s`
              : 'N/A'
          }
          icon={Clock}
          color="#f59e0b"
          subtitle="Average completion time"
        />
      </div>

      {/* Recent Completions */}
      <div style={{ 
        background: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '12px',
        padding: '24px',
        border: '1px solid rgba(76, 212, 176, 0.2)'
      }}>
        <h3 style={{ marginTop: 0, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <FileText size={20} />
          Recent Security Checks
        </h3>
        {recentCompletions.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {recentCompletions.map((completion, idx) => (
              <CompletionRow key={idx} completion={completion} />
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', opacity: 0.5 }}>
            <Shield size={48} style={{ marginBottom: '16px', opacity: 0.3 }} />
            <p>No security checks completed yet</p>
          </div>
        )}
      </div>
    </motion.div>
  )
}

// Live Monitor Tab Component
function LiveMonitorTab() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <div style={{ 
        background: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '12px',
        padding: '24px',
        border: '1px solid rgba(76, 212, 176, 0.2)',
        textAlign: 'center'
      }}>
        <Video size={64} style={{ margin: '40px auto 20px', opacity: 0.5 }} />
        <h3>Live Camera Feed</h3>
        <p style={{ opacity: 0.7, marginBottom: '24px' }}>
          Connect to webcam stream to see real-time gate monitoring
        </p>
        <button className="btn-primary" style={{
          background: 'linear-gradient(135deg, var(--verolux-secondary), var(--verolux-accent))',
          border: 'none',
          padding: '12px 32px',
          borderRadius: '8px',
          color: 'white',
          cursor: 'pointer',
          fontSize: '16px',
          fontWeight: 600
        }}>
          <Eye size={18} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          Connect to Camera
        </button>
        <div style={{ marginTop: '32px', padding: '20px', background: 'rgba(76, 212, 176, 0.1)', borderRadius: '8px' }}>
          <p style={{ margin: 0, fontSize: '14px' }}>
            <strong>WebSocket Endpoint:</strong> ws://localhost:8000/ws/gate-check?source=webcam:0
          </p>
        </div>
      </div>
    </motion.div>
  )
}

// Config Tab Component
function ConfigTab({ editorMode, setEditorMode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      {/* Editor Mode Toggle */}
      <div style={{ 
        display: 'flex', 
        gap: '12px', 
        marginBottom: '20px',
        padding: '12px',
        background: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '8px',
        border: '1px solid rgba(76, 212, 176, 0.2)'
      }}>
        <button
          onClick={() => setEditorMode('live')}
          style={{
            flex: 1,
            padding: '12px 24px',
            background: editorMode === 'live'
              ? 'linear-gradient(135deg, var(--verolux-secondary), var(--verolux-accent))'
              : 'rgba(255, 255, 255, 0.05)',
            border: editorMode === 'live'
              ? '1px solid var(--verolux-accent)'
              : '1px solid rgba(76, 212, 176, 0.2)',
            borderRadius: '6px',
            color: 'white',
            cursor: 'pointer',
            fontWeight: editorMode === 'live' ? 600 : 400,
            transition: 'all 0.3s ease'
          }}
        >
          📹 Live Video Editor
        </button>
        <button
          onClick={() => setEditorMode('advanced')}
          style={{
            flex: 1,
            padding: '12px 24px',
            background: editorMode === 'advanced'
              ? 'linear-gradient(135deg, var(--verolux-secondary), var(--verolux-accent))'
              : 'rgba(255, 255, 255, 0.05)',
            border: editorMode === 'advanced'
              ? '1px solid var(--verolux-accent)'
              : '1px solid rgba(76, 212, 176, 0.2)',
            borderRadius: '6px',
            color: 'white',
            cursor: 'pointer',
            fontWeight: editorMode === 'advanced' ? 600 : 400,
            transition: 'all 0.3s ease'
          }}
        >
          🎨 Advanced Editor
        </button>
      </div>
      
      {/* Render selected editor */}
      {editorMode === 'live' ? <GateConfigEditorLive /> : <GateConfigEditor />}
    </motion.div>
  )
}

// Analytics Tab Component
function AnalyticsTab({ gateStats }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
        <AnalyticsCard
          title="Total Completions"
          value={gateStats?.total_completions || 0}
          change="+12%"
          trend="up"
        />
        <AnalyticsCard
          title="Success Rate"
          value={
            gateStats?.success_rate && typeof gateStats.success_rate === 'number'
              ? `${(gateStats.success_rate * 100).toFixed(1)}%`
              : 'N/A'
          }
          change="+5%"
          trend="up"
        />
        <AnalyticsCard
          title="Avg Score"
          value={
            gateStats?.avg_score && typeof gateStats.avg_score === 'number'
              ? gateStats.avg_score.toFixed(2)
              : 'N/A'
          }
          change="+0.03"
          trend="up"
        />
      </div>
    </motion.div>
  )
}

// Completions Tab Component
function CompletionsTab({ completions }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <div style={{ 
        background: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '12px',
        padding: '24px',
        border: '1px solid rgba(76, 212, 176, 0.2)'
      }}>
        <h3 style={{ marginTop: 0, marginBottom: '20px' }}>Check History</h3>
        {completions.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {completions.map((completion, idx) => (
              <CompletionRow key={idx} completion={completion} detailed />
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', opacity: 0.5 }}>
            <FileText size={48} style={{ marginBottom: '16px', opacity: 0.3 }} />
            <p>No check history available</p>
          </div>
        )}
      </div>
    </motion.div>
  )
}

// Helper Components
function StatusCard({ title, value, icon: Icon, color, subtitle }) {
  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '12px',
      padding: '24px',
      border: '1px solid rgba(76, 212, 176, 0.2)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <Icon size={32} style={{ color }} />
      </div>
      <div style={{ fontSize: '32px', fontWeight: 700, marginBottom: '8px', color }}>
        {value}
      </div>
      <div style={{ fontSize: '14px', fontWeight: 600, marginBottom: '4px' }}>
        {title}
      </div>
      <div style={{ fontSize: '12px', opacity: 0.7 }}>
        {subtitle}
      </div>
    </div>
  )
}

function CompletionRow({ completion, detailed }) {
  const timestamp = completion.timestamp 
    ? new Date(completion.timestamp * 1000).toLocaleString()
    : 'Unknown time'
  const score = typeof completion.score === 'number' ? completion.score : 0
  const scoreColor = score >= 0.9 ? '#22c55e' : score >= 0.7 ? '#f59e0b' : '#ef4444'
  const dwellTime = typeof completion.visitor_dwell === 'number' ? completion.visitor_dwell : 0

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px',
      background: 'rgba(255, 255, 255, 0.03)',
      borderRadius: '8px',
      border: '1px solid rgba(76, 212, 176, 0.1)'
    }}>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600, marginBottom: '4px' }}>
          Session {completion.session_id?.split('_')[0] || 'Unknown'}
        </div>
        <div style={{ fontSize: '12px', opacity: 0.7 }}>
          {timestamp}
        </div>
      </div>
      <div style={{ textAlign: 'right' }}>
        <div style={{ fontSize: '18px', fontWeight: 700, color: scoreColor }}>
          {score.toFixed(2)}
        </div>
        <div style={{ fontSize: '12px', opacity: 0.7 }}>
          {dwellTime.toFixed(1)}s dwell
        </div>
      </div>
    </div>
  )
}

function AnalyticsCard({ title, value, change, trend }) {
  const trendColor = trend === 'up' ? '#22c55e' : '#ef4444'
  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '12px',
      padding: '24px',
      border: '1px solid rgba(76, 212, 176, 0.2)'
    }}>
      <div style={{ fontSize: '14px', fontWeight: 600, marginBottom: '12px', opacity: 0.7 }}>
        {title}
      </div>
      <div style={{ fontSize: '36px', fontWeight: 700, marginBottom: '8px' }}>
        {value}
      </div>
      <div style={{ fontSize: '14px', color: trendColor }}>
        <TrendingUp size={14} style={{ verticalAlign: 'middle', marginRight: '4px' }} />
        {change}
      </div>
    </div>
  )
}

