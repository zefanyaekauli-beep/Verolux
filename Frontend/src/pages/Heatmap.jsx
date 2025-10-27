import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  MapPin, Navigation, Layers, Filter, Download, 
  RefreshCw, Settings, Eye, EyeOff, Activity,
  TrendingUp, Users, AlertTriangle, Clock
} from 'lucide-react'
import GPSMap from '../components/GPSMap'
import useLang from '../stores/lang'

const Heatmap = () => {
  const { t } = useLang()
  const [heatmapData, setHeatmapData] = useState([])
  const [markers, setMarkers] = useState([])
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h')
  const [selectedDataType, setSelectedDataType] = useState('all')
  const [showHeatmap, setShowHeatmap] = useState(true)
  const [showMarkers, setShowMarkers] = useState(true)
  const [isLoading, setIsLoading] = useState(false)

  // Sample GPS data for demonstration
  const sampleGPSData = {
    detections: [
      { lat: -6.2088, lng: 106.8456, weight: 0.8, type: 'person', timestamp: '2024-01-15 10:30:00' },
      { lat: -6.2095, lng: 106.8460, weight: 0.6, type: 'vehicle', timestamp: '2024-01-15 10:35:00' },
      { lat: -6.2100, lng: 106.8465, weight: 0.9, type: 'person', timestamp: '2024-01-15 11:00:00' },
      { lat: -6.2090, lng: 106.8450, weight: 0.7, type: 'person', timestamp: '2024-01-15 11:15:00' },
      { lat: -6.2085, lng: 106.8445, weight: 0.5, type: 'vehicle', timestamp: '2024-01-15 12:00:00' }
    ],
    violations: [
      { lat: -6.2088, lng: 106.8456, weight: 1.0, type: 'unauthorized_access', severity: 'high' },
      { lat: -6.2095, lng: 106.8460, weight: 0.8, type: 'loitering', severity: 'medium' },
      { lat: -6.2100, lng: 106.8465, weight: 0.6, type: 'parking_violation', severity: 'low' }
    ],
    cameras: [
      { lat: -6.2088, lng: 106.8456, title: 'Main Entrance', status: 'active', type: 'entrance' },
      { lat: -6.2095, lng: 106.8460, title: 'Parking Lot', status: 'active', type: 'parking' },
      { lat: -6.2100, lng: 106.8465, title: 'Security Checkpoint', status: 'active', type: 'security' }
    ]
  }

  useEffect(() => {
    loadHeatmapData()
  }, [selectedTimeRange, selectedDataType])

  const loadHeatmapData = async () => {
    setIsLoading(true)
    
    // Simulate API call
    setTimeout(() => {
      let data = []
      let markerData = []

      if (selectedDataType === 'all' || selectedDataType === 'detections') {
        data = [...data, ...sampleGPSData.detections]
        markerData = [...markerData, ...sampleGPSData.detections.map(d => ({
          lat: d.lat,
          lng: d.lng,
          title: `${d.type} detection`,
          type: 'detection',
          timestamp: d.timestamp
        }))]
      }

      if (selectedDataType === 'all' || selectedDataType === 'violations') {
        data = [...data, ...sampleGPSData.violations]
        markerData = [...markerData, ...sampleGPSData.violations.map(v => ({
          lat: v.lat,
          lng: v.lng,
          title: `${v.type} violation`,
          type: 'violation',
          severity: v.severity
        }))]
      }

      if (selectedDataType === 'all' || selectedDataType === 'cameras') {
        markerData = [...markerData, ...sampleGPSData.cameras.map(c => ({
          lat: c.lat,
          lng: c.lng,
          title: c.title,
          type: 'camera',
          status: c.status
        }))]
      }

      setHeatmapData(data)
      setMarkers(markerData)
      setIsLoading(false)
    }, 1000)
  }

  const handleMarkerClick = (marker) => {
    console.log('Marker clicked:', marker)
    // Handle marker click - could show details, navigate, etc.
  }

  const handleMapClick = (location) => {
    console.log('Map clicked at:', location)
    // Handle map click - could add new markers, show location info, etc.
  }

  const exportHeatmapData = () => {
    const data = {
      heatmapData,
      markers,
      timeRange: selectedTimeRange,
      dataType: selectedDataType,
      timestamp: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `heatmap-data-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const getDataTypeStats = () => {
    const stats = {
      total: heatmapData.length,
      detections: sampleGPSData.detections.length,
      violations: sampleGPSData.violations.length,
      cameras: sampleGPSData.cameras.length
    }
    return stats
  }

  const stats = getDataTypeStats()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center mb-4">
            <MapPin className="w-8 h-8 text-blue-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">GPS Heatmap</h1>
          </div>
          <p className="text-gray-600 text-lg">
            Interactive GPS-based heatmap with real-time location data and analytics
          </p>
        </motion.div>

        {/* Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-lg p-6 mb-6"
        >
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-4">
              {/* Time Range Filter */}
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-gray-500" />
                <select
                  value={selectedTimeRange}
                  onChange={(e) => setSelectedTimeRange(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="1h">Last Hour</option>
                  <option value="24h">Last 24 Hours</option>
                  <option value="7d">Last 7 Days</option>
                  <option value="30d">Last 30 Days</option>
                </select>
              </div>

              {/* Data Type Filter */}
              <div className="flex items-center space-x-2">
                <Filter className="w-4 h-4 text-gray-500" />
                <select
                  value={selectedDataType}
                  onChange={(e) => setSelectedDataType(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Data</option>
                  <option value="detections">Detections Only</option>
                  <option value="violations">Violations Only</option>
                  <option value="cameras">Cameras Only</option>
                </select>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              {/* Toggle Controls */}
              <button
                onClick={() => setShowHeatmap(!showHeatmap)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                  showHeatmap ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                }`}
              >
                {showHeatmap ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                <span>Heatmap</span>
              </button>

              <button
                onClick={() => setShowMarkers(!showMarkers)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                  showMarkers ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'
                }`}
              >
                {showMarkers ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                <span>Markers</span>
              </button>

              {/* Action Buttons */}
              <button
                onClick={loadHeatmapData}
                disabled={isLoading}
                className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>

              <button
                onClick={exportHeatmapData}
                className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
            </div>
          </div>
        </motion.div>

        {/* Stats Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6"
        >
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center">
              <Activity className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
                <p className="text-sm text-gray-600">Total Data Points</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-green-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.detections}</p>
                <p className="text-sm text-gray-600">Detections</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center">
              <AlertTriangle className="w-8 h-8 text-red-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.violations}</p>
                <p className="text-sm text-gray-600">Violations</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center">
              <MapPin className="w-8 h-8 text-purple-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.cameras}</p>
                <p className="text-sm text-gray-600">Cameras</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* GPS Map */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Interactive GPS Map</h2>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Navigation className="w-4 h-4" />
              <span>Jakarta, Indonesia</span>
            </div>
          </div>
          
          <GPSMap
            center={{ lat: -6.2088, lng: 106.8456 }}
            zoom={13}
            markers={showMarkers ? markers : []}
            heatmapData={showHeatmap ? heatmapData : []}
            onMarkerClick={handleMarkerClick}
            onMapClick={handleMapClick}
            height="600px"
            showControls={true}
          />
        </motion.div>
      </div>
    </div>
  )
}

export default Heatmap

