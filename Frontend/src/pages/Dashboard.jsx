import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Area, AreaChart
} from 'recharts'
import { 
  Users, Eye, AlertTriangle, Shield, TrendingUp, Activity, 
  Clock, MapPin, Target, Zap, CheckCircle, XCircle
} from 'lucide-react'
import VideoFeed from '../components/VideoFeed'
import AlertsPanel from '../components/AlertsPanel'
import RecentEvents from '../components/RecentEvents'

export default function Dashboard(){
  // Sample data for dashboard analytics
  const sampleData = {
    // Key Metrics
    keyMetrics: [
      { 
        title: 'Total Detections', 
        value: '2,405', 
        change: '+12%', 
        icon: Users, 
        color: 'blue',
        trend: 'up'
      },
      { 
        title: 'Active Cameras', 
        value: '8', 
        change: 'All operational', 
        icon: Eye, 
        color: 'green',
        trend: 'stable'
      },
      { 
        title: 'Alerts Today', 
        value: '12', 
        change: '3 high priority', 
        icon: AlertTriangle, 
        color: 'orange',
        trend: 'down'
      },
      { 
        title: 'Compliance Rate', 
        value: '94%', 
        change: '+2% improvement', 
        icon: Shield, 
        color: 'purple',
        trend: 'up'
      }
    ],

    // Object Detection Data
    objectCounts: [
      { name: 'Person', count: 1250, color: '#22c55e', trend: '+12%' },
      { name: 'Vehicle', count: 890, color: '#3b82f6', trend: '+8%' },
      { name: 'Forklift', count: 45, color: '#f59e0b', trend: '-3%' },
      { name: 'Package', count: 320, color: '#8b5cf6', trend: '+15%' },
      { name: 'Bicycle', count: 120, color: '#06b6d4', trend: '+5%' }
    ],

    // Hourly Traffic Data
    hourlyTraffic: Array.from({ length: 24 }, (_, i) => ({
      hour: `${i}:00`,
      count: Math.floor(Math.random() * 100) + 20,
      trend: i >= 8 && i <= 17 ? 'high' : i >= 18 && i <= 22 ? 'medium' : 'low'
    })),

    // Zone Occupancy Data
    zoneOccupancy: [
      { zone: 'Loading Dock', occupancy: 85, capacity: 100, utilization: 85, alerts: 3 },
      { zone: 'Warehouse', occupancy: 60, capacity: 150, utilization: 40, alerts: 1 },
      { zone: 'Office', occupancy: 30, capacity: 50, utilization: 60, alerts: 0 },
      { zone: 'Parking', occupancy: 120, capacity: 200, utilization: 60, alerts: 2 },
      { zone: 'Restricted Area', occupancy: 5, capacity: 10, utilization: 50, alerts: 8 }
    ],

    // Recent Events
    recentEvents: [
      { id: 1, type: 'Person detected', camera: 'Camera-01', time: '2 min ago', severity: 'low' },
      { id: 2, type: 'Vehicle entered', camera: 'Camera-03', time: '5 min ago', severity: 'medium' },
      { id: 3, type: 'Intrusion alert', camera: 'Camera-07', time: '8 min ago', severity: 'high' },
      { id: 4, type: 'PPE violation', camera: 'Camera-02', time: '12 min ago', severity: 'medium' },
      { id: 5, type: 'Loitering detected', camera: 'Camera-05', time: '15 min ago', severity: 'low' }
    ],

    // Alert Summary
    alertSummary: {
      total: 45,
      high: 8,
      medium: 15,
      low: 22,
      resolved: 42,
      avgResponseTime: 2.3
    }
  }

  return (
    <div className="verolux-pattern" style={{ 
      padding: '24px',
      minHeight: 'calc(100vh - 120px)',
      background: 'var(--verolux-background)'
    }}>
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="verolux-heading-1 mb-2">Security Dashboard</h1>
        <p className="verolux-body-secondary">Real-time surveillance and analytics overview</p>
      </motion.div>

      {/* Key Metrics Cards */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
      >
        {sampleData.keyMetrics.map((metric, index) => {
          const Icon = metric.icon
          const colorClasses = {
            blue: 'from-blue-500 to-blue-600',
            green: 'from-green-500 to-green-600',
            orange: 'from-orange-500 to-orange-600',
            purple: 'from-purple-500 to-purple-600'
          }
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.1 }}
              className={`bg-gradient-to-br ${colorClasses[metric.color]} p-6 rounded-xl text-white shadow-lg`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white/80 text-sm mb-1">{metric.title}</p>
                  <p className="text-3xl font-bold mb-1">{metric.value}</p>
                  <p className="text-white/70 text-xs">{metric.change}</p>
                </div>
                <Icon className="w-8 h-8 text-white/80" />
              </div>
            </motion.div>
          )
        })}
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-8">
        {/* Video Feed - Takes 4 columns for much larger video */}
        <div className="lg:col-span-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="verolux-card mb-6"
          >
            <VideoFeed 
              title="Live Security Feed" 
              source="file:videoplayback.mp4"
              showDetections={true}
              showStats={true}
              enableZoneEditor={true}
              enableGateConfig={true}
            />
          </motion.div>

          {/* Secondary Camera Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            <VideoFeed 
              title="Entrance Camera" 
              source="file:videoplayback.mp4"
              showDetections={true}
              showStats={false}
              className="compact"
            />
            <div className="verolux-card flex flex-col justify-center items-center text-center cursor-pointer hover:shadow-lg transition-all duration-300">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mb-4 shadow-lg">
                <span className="text-2xl">📹</span>
              </div>
              <h4 className="verolux-heading-4 mb-2">Add Camera</h4>
              <p className="verolux-caption">Connect additional cameras</p>
            </div>
          </motion.div>
        </div>

        {/* Analytics Sidebar - Takes 1 column */}
        <div className="space-y-6">
          {/* Object Detection Chart */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="verolux-card"
          >
            <h3 className="verolux-heading-3 mb-4">Object Detection</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={sampleData.objectCounts}
                  cx="50%"
                  cy="50%"
                  outerRadius={60}
                  dataKey="count"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {sampleData.objectCounts.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Zone Occupancy */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="verolux-card"
          >
            <h3 className="verolux-heading-3 mb-4">Zone Occupancy</h3>
            <div className="space-y-3">
              {sampleData.zoneOccupancy.map((zone, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <MapPin className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium">{zone.zone}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${zone.utilization}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-600">{zone.utilization}%</span>
                    {zone.alerts > 0 && (
                      <span className="px-1 py-0.5 bg-red-100 text-red-800 text-xs rounded">
                        {zone.alerts}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Alert Summary */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="verolux-card"
          >
            <h3 className="verolux-heading-3 mb-4">Alert Summary</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Total Alerts</span>
                <span className="font-semibold">{sampleData.alertSummary.total}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-red-600">High Priority</span>
                <span className="font-semibold text-red-600">{sampleData.alertSummary.high}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-yellow-600">Medium Priority</span>
                <span className="font-semibold text-yellow-600">{sampleData.alertSummary.medium}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-green-600">Resolved</span>
                <span className="font-semibold text-green-600">{sampleData.alertSummary.resolved}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Avg Response</span>
                <span className="font-semibold">{sampleData.alertSummary.avgResponseTime}m</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Bottom Analytics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Traffic Pattern Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="verolux-card"
        >
          <h3 className="verolux-heading-3 mb-4">Hourly Traffic Pattern</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={sampleData.hourlyTraffic}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="count" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Recent Events */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="verolux-card"
        >
          <h3 className="verolux-heading-3 mb-4">Recent Events</h3>
          <div className="space-y-3">
            {sampleData.recentEvents.map((event, index) => (
              <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    event.severity === 'high' ? 'bg-red-500' : 
                    event.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                  }`}></div>
                  <div>
                    <p className="text-sm font-medium">{event.type}</p>
                    <p className="text-xs text-gray-600">{event.camera}</p>
                  </div>
                </div>
                <span className="text-xs text-gray-500">{event.time}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
