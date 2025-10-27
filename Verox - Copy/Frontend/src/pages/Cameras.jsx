import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Camera, Plus, Trash2, Edit, Settings, Play, Pause, 
  RotateCcw, Maximize2, Minimize2, Grid, List, 
  MoreHorizontal, Eye, EyeOff, AlertTriangle, CheckCircle,
  Wifi, WifiOff, Battery, BatteryLow, Clock, MapPin,
  RefreshCw, Download, Upload, Share2, Copy, Star,
  ChevronDown, ChevronUp, X, Search, Filter, SortAsc
} from 'lucide-react'
import VideoFeed from '../components/VideoFeed'

export default function Cameras(){
  const [cams, setCams] = useState([
    { 
      id: 1,
      name: 'Main Entrance', 
      source: 'webcam:0',
      status: 'online',
      quality: 'HD',
      location: 'Building A - Floor 1',
      lastSeen: '2 min ago',
      uptime: 99.8,
      resolution: '1920x1080',
      fps: 30,
      isRecording: true,
      isStreaming: true,
      alerts: 0,
      battery: 85,
      signal: 'strong'
    },
    { 
      id: 2,
      name: 'Parking Lot', 
      source: 'webcam:1',
      status: 'online',
      quality: 'HD',
      location: 'Parking Area - North',
      lastSeen: '1 min ago',
      uptime: 99.5,
      resolution: '1920x1080',
      fps: 25,
      isRecording: true,
      isStreaming: true,
      alerts: 2,
      battery: 92,
      signal: 'strong'
    },
    { 
      id: 3,
      name: 'Loading Dock', 
      source: 'rtsp://192.168.1.100:554/stream',
      status: 'offline',
      quality: '4K',
      location: 'Loading Bay - East',
      lastSeen: '2 hours ago',
      uptime: 0,
      resolution: '3840x2160',
      fps: 0,
      isRecording: false,
      isStreaming: false,
      alerts: 5,
      battery: 0,
      signal: 'none'
    },
    { 
      id: 4,
      name: 'Office Area', 
      source: 'rtsp://192.168.1.101:554/stream',
      status: 'online',
      quality: 'HD',
      location: 'Building B - Floor 2',
      lastSeen: '30 sec ago',
      uptime: 99.9,
      resolution: '1920x1080',
      fps: 30,
      isRecording: true,
      isStreaming: true,
      alerts: 0,
      battery: 78,
      signal: 'medium'
    }
  ])
  const [name, setName] = useState('')
  const [source, setSource] = useState('webcam:0')
  const [location, setLocation] = useState('')
  const [resolution, setResolution] = useState('1920x1080')
  const [showAddForm, setShowAddForm] = useState(false)
  const [viewMode, setViewMode] = useState('grid')
  const [sortBy, setSortBy] = useState('name')
  const [filterStatus, setFilterStatus] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCamera, setSelectedCamera] = useState(null)
  const [showCameraDetails, setShowCameraDetails] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Helper functions
  const getStatusColor = (status) => {
    const colors = {
      online: 'text-green-600 bg-green-50 border-green-200',
      offline: 'text-red-600 bg-red-50 border-red-200',
      warning: 'text-yellow-600 bg-yellow-50 border-yellow-200'
    };
    return colors[status] || colors.offline;
  };

  const getSignalIcon = (signal) => {
    switch (signal) {
      case 'strong': return <Wifi className="w-4 h-4 text-green-600" />;
      case 'medium': return <Wifi className="w-4 h-4 text-yellow-600" />;
      case 'weak': return <Wifi className="w-4 h-4 text-orange-600" />;
      case 'none': return <WifiOff className="w-4 h-4 text-red-600" />;
      default: return <WifiOff className="w-4 h-4 text-gray-600" />;
    }
  };

  const getBatteryIcon = (battery) => {
    if (battery > 80) return <Battery className="w-4 h-4 text-green-600" />;
    if (battery > 20) return <Battery className="w-4 h-4 text-yellow-600" />;
    return <BatteryLow className="w-4 h-4 text-red-600" />;
  };

  const formatUptime = (uptime) => {
    if (uptime === 0) return 'Offline';
    return `${uptime}%`;
  };

  // Camera management functions
  const addCamera = () => {
    if (!name || !source) return
    
    const newCamera = {
      id: Date.now(),
      name,
      source,
      location: location || 'Unknown Location',
      status: 'online',
      quality: resolution === '3840x2160' ? '4K' : 'HD',
      lastSeen: 'Just now',
      uptime: 100,
      resolution,
      fps: 30,
      isRecording: true,
      isStreaming: true,
      alerts: 0,
      battery: 100,
      signal: 'strong'
    };
    
    setCams([...cams, newCamera])
    setName('')
    setSource('webcam:0')
    setLocation('')
    setResolution('1920x1080')
    setShowAddForm(false)
  }

  const removeCamera = (id) => {
    setCams(cams.filter(cam => cam.id !== id))
  }

  const updateCamera = (id, updates) => {
    setCams(cams.map(cam => 
      cam.id === id ? { ...cam, ...updates } : cam
    ))
  }

  const toggleRecording = (id) => {
    updateCamera(id, { isRecording: !cams.find(cam => cam.id === id).isRecording })
  }

  const toggleStreaming = (id) => {
    updateCamera(id, { isStreaming: !cams.find(cam => cam.id === id).isStreaming })
  }

  const refreshCameras = async () => {
    setIsRefreshing(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsRefreshing(false)
  }

  // Filter and sort cameras
  const filteredCameras = cams
    .filter(cam => {
      const matchesSearch = cam.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           cam.location.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = filterStatus === 'all' || cam.status === filterStatus
      return matchesSearch && matchesStatus
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name': return a.name.localeCompare(b.name)
        case 'status': return b.status.localeCompare(a.status)
        case 'uptime': return b.uptime - a.uptime
        case 'alerts': return b.alerts - a.alerts
        default: return 0
      }
    })

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate status updates
      setCams(prevCams => prevCams.map(cam => ({
        ...cam,
        lastSeen: cam.status === 'online' ? 'Just now' : cam.lastSeen
      })))
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Enhanced Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Camera Management</h1>
              <p className="text-gray-600 text-lg">Monitor and manage your security camera network</p>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={refreshCameras}
                disabled={isRefreshing}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                <span className="text-sm font-medium">Refresh</span>
              </button>
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span className="text-sm font-medium">Add Camera</span>
              </button>
            </div>
          </div>
        </motion.div>

        {/* Statistics Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6"
        >
          {[
            { title: 'Total Cameras', value: cams.length, icon: Camera, color: 'blue' },
            { title: 'Online', value: cams.filter(cam => cam.status === 'online').length, icon: CheckCircle, color: 'green' },
            { title: 'Recording', value: cams.filter(cam => cam.isRecording).length, icon: Play, color: 'purple' },
            { title: 'Alerts', value: cams.reduce((sum, cam) => sum + cam.alerts, 0), icon: AlertTriangle, color: 'red' }
          ].map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 + index * 0.1 }}
                className="bg-white p-6 rounded-xl shadow-lg"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">{stat.title}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                  <Icon className="w-8 h-8 text-blue-600" />
                </div>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Enhanced Filters and Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl shadow-lg mb-6 p-6"
        >
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center space-x-2">
              <Search className="w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search cameras..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
              />
            </div>
            
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="online">Online</option>
                <option value="offline">Offline</option>
                <option value="warning">Warning</option>
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <SortAsc className="w-4 h-4 text-gray-500" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="name">Sort by Name</option>
                <option value="status">Sort by Status</option>
                <option value="uptime">Sort by Uptime</option>
                <option value="alerts">Sort by Alerts</option>
              </select>
            </div>

            <div className="flex items-center space-x-2 ml-auto">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:bg-gray-100'}`}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:bg-gray-100'}`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </motion.div>

        {/* Add Camera Form */}
        <AnimatePresence>
          {showAddForm && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-white rounded-xl shadow-lg mb-6 p-6"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">Add New Camera</h3>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Camera Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g., Main Entrance"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Source</label>
                  <select
                    value={source}
                    onChange={(e) => setSource(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="webcam:0">Webcam 0</option>
                    <option value="webcam:1">Webcam 1</option>
                    <option value="rtsp://">RTSP Stream</option>
                    <option value="file://">Video File</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g., Building A - Floor 1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Resolution</label>
                  <select
                    value={resolution}
                    onChange={(e) => setResolution(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="1920x1080">HD (1920x1080)</option>
                    <option value="3840x2160">4K (3840x2160)</option>
                    <option value="1280x720">HD (1280x720)</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowAddForm(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={addCamera}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add Camera
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Camera Grid/List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className={viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
            : 'space-y-4'
          }
        >
          {filteredCameras.map((camera, index) => (
            <motion.div
              key={camera.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className={`bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 ${
                viewMode === 'list' ? 'flex' : ''
              }`}
            >
              {/* Camera Video Feed */}
              <div className={`relative ${viewMode === 'list' ? 'w-1/3' : 'w-full'}`}>
                <VideoFeed 
                  title={camera.name} 
                  source={camera.source}
                  showDetections={true}
                  showStats={true}
                />
                
                {/* Camera Status Overlay */}
                <div className="absolute top-4 left-4 flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs rounded-full border ${getStatusColor(camera.status)}`}>
                    {camera.status}
                  </span>
                  {camera.isRecording && (
                    <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">
                      REC
                    </span>
                  )}
                </div>

                {/* Camera Controls */}
                <div className="absolute top-4 right-4 flex items-center space-x-2">
                  <button
                    onClick={() => toggleRecording(camera.id)}
                    className={`p-2 rounded-lg transition-colors ${
                      camera.isRecording 
                        ? 'bg-red-100 text-red-600 hover:bg-red-200' 
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {camera.isRecording ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  </button>
                  
                  <button
                    onClick={() => {
                      setSelectedCamera(camera)
                      setShowCameraDetails(true)
                    }}
                    className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                  
                  <button
                    onClick={() => removeCamera(camera.id)}
                    className="p-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Camera Details */}
              <div className={`p-6 ${viewMode === 'list' ? 'flex-1' : ''}`}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">{camera.name}</h3>
                  <div className="flex items-center space-x-2">
                    {getSignalIcon(camera.signal)}
                    {getBatteryIcon(camera.battery)}
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Location</span>
                    <span className="text-sm font-medium">{camera.location}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Quality</span>
                    <span className="text-sm font-medium">{camera.quality}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Resolution</span>
                    <span className="text-sm font-medium">{camera.resolution}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">FPS</span>
                    <span className="text-sm font-medium">{camera.fps}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Uptime</span>
                    <span className="text-sm font-medium">{formatUptime(camera.uptime)}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Last Seen</span>
                    <span className="text-sm font-medium">{camera.lastSeen}</span>
                  </div>

                  {camera.alerts > 0 && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Alerts</span>
                      <span className="text-sm font-medium text-red-600">{camera.alerts}</span>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Camera Details Modal */}
        <AnimatePresence>
          {showCameraDetails && selectedCamera && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            >
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              >
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-semibold text-gray-900">Camera Details</h3>
                    <button
                      onClick={() => setShowCameraDetails(false)}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <div className="p-6">
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h4>
                      <div className="space-y-3">
                        <div>
                          <span className="text-sm text-gray-600">Name:</span>
                          <p className="font-medium">{selectedCamera.name}</p>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">Source:</span>
                          <p className="font-medium font-mono text-sm">{selectedCamera.source}</p>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">Location:</span>
                          <p className="font-medium">{selectedCamera.location}</p>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">Status:</span>
                          <span className={`px-2 py-1 text-xs rounded-full border ${getStatusColor(selectedCamera.status)}`}>
                            {selectedCamera.status}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-lg font-medium text-gray-900 mb-4">Technical Details</h4>
                      <div className="space-y-3">
                        <div>
                          <span className="text-sm text-gray-600">Resolution:</span>
                          <p className="font-medium">{selectedCamera.resolution}</p>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">FPS:</span>
                          <p className="font-medium">{selectedCamera.fps}</p>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">Uptime:</span>
                          <p className="font-medium">{formatUptime(selectedCamera.uptime)}</p>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">Battery:</span>
                          <p className="font-medium">{selectedCamera.battery}%</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
