import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Area, AreaChart, ComposedChart,
  RadialBarChart, RadialBar, RadarChart, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, Radar, Scatter, ScatterChart, Treemap
} from 'recharts';
import { 
  Calendar, Download, Filter, TrendingUp, Users, AlertTriangle, 
  Shield, Clock, MapPin, Activity, Eye, BarChart3, PieChart as PieChartIcon,
  FileText, Search, Settings, Zap, Target, AlertCircle, Brain, Database,
  TrendingDown, AlertOctagon, CheckCircle, XCircle, Timer, UserCheck,
  ArrowUpDown, ArrowRight, ArrowLeft, ArrowUp, ArrowDown, 
  Activity as ActivityIcon, Thermometer, Layers, GitBranch,
  RefreshCw, Maximize2, Minimize2, Play, Pause, RotateCcw,
  Grid3X3, BarChart2, LineChart as LineChartIcon, PieChart as PieChartIcon2,
  Table, List, Grid, MoreHorizontal, Edit, Trash2, Copy, Share2,
  Star, ArrowUpRight, ArrowDownRight, Minus, Plus, X, ChevronDown,
  ChevronUp, Info, AlertCircle as AlertCircleIcon, CheckCircle2
} from 'lucide-react';

const Analytics = () => {
  const [activeTab, setActiveTab] = useState('traffic');
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });
  const [selectedCamera, setSelectedCamera] = useState('all');
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState('grid');
  const [chartType, setChartType] = useState('bar');
  const [timeframe, setTimeframe] = useState('7d');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [expandedCards, setExpandedCards] = useState({});
  const [selectedMetrics, setSelectedMetrics] = useState(['traffic', 'utilization', 'behavior']);

  // Comprehensive sample data for analytics
  const sampleData = {
    trafficFlow: {
      hourly: Array.from({ length: 24 }, (_, i) => ({
        hour: `${i}:00`,
        entries: Math.floor(Math.random() * 100) + 20,
        exits: Math.floor(Math.random() * 100) + 15,
        net: Math.floor(Math.random() * 20) - 10,
        efficiency: Math.random() * 30 + 70
      })),
      daily: Array.from({ length: 7 }, (_, i) => ({
        day: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][i],
        traffic: Math.floor(Math.random() * 500) + 200,
        peak: i >= 1 && i <= 5,
        efficiency: Math.random() * 20 + 80
      })),
      zones: [
        { zone: 'Main Entrance', entries: 245, exits: 238, net: 7, efficiency: 92.3 },
        { zone: 'Loading Dock', entries: 89, exits: 92, net: -3, efficiency: 87.6 },
        { zone: 'Parking Lot', entries: 156, exits: 152, net: 4, efficiency: 89.1 },
        { zone: 'Office Area', entries: 78, exits: 81, net: -3, efficiency: 94.2 }
      ]
    },
    utilization: {
      zones: [
        { name: 'Loading Dock', occupancy: 85, capacity: 100, utilization: 85, alerts: 3, efficiency: 92.3 },
        { name: 'Warehouse', occupancy: 60, capacity: 150, utilization: 40, alerts: 1, efficiency: 87.6 },
        { name: 'Office', occupancy: 30, capacity: 50, utilization: 60, alerts: 0, efficiency: 95.1 },
        { name: 'Parking', occupancy: 120, capacity: 200, utilization: 60, alerts: 2, efficiency: 78.9 },
        { name: 'Restricted Area', occupancy: 5, capacity: 10, utilization: 50, alerts: 8, efficiency: 45.2 }
      ],
      trends: Array.from({ length: 30 }, (_, i) => ({
        date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        avgUtilization: Math.random() * 30 + 60,
        peakUtilization: Math.random() * 20 + 80,
        efficiency: Math.random() * 15 + 80
      }))
    },
    behavior: {
      loitering: [
        { location: 'Loading Dock', duration: 15, person: 'Person A', severity: 'medium', timestamp: '2024-01-15 14:30' },
        { location: 'Parking Lot', duration: 8, person: 'Person B', severity: 'low', timestamp: '2024-01-15 16:45' },
        { location: 'Restricted Area', duration: 25, person: 'Person C', severity: 'high', timestamp: '2024-01-15 18:20' }
      ],
      intrusions: [
        { zone: 'Restricted Area', timestamp: '2024-01-15 14:30', person: 'Unknown', severity: 'high' },
        { zone: 'After Hours Office', timestamp: '2024-01-15 22:15', person: 'Employee X', severity: 'medium' },
        { zone: 'Equipment Room', timestamp: '2024-01-15 16:45', person: 'Maintenance', severity: 'low' }
      ],
      patterns: Array.from({ length: 24 }, (_, i) => ({
        hour: `${i}:00`,
        loitering: Math.floor(Math.random() * 10),
        intrusions: Math.floor(Math.random() * 5),
        suspicious: Math.floor(Math.random() * 8)
      }))
    },
    ppeCompliance: {
      categories: [
        { name: 'Helmet', compliant: 95, nonCompliant: 5, violations: 12, trend: '+2%' },
        { name: 'Safety Vest', compliant: 88, nonCompliant: 12, violations: 8, trend: '-1%' },
        { name: 'Safety Glasses', compliant: 92, nonCompliant: 8, violations: 6, trend: '+3%' },
        { name: 'Gloves', compliant: 85, nonCompliant: 15, violations: 15, trend: '+1%' },
        { name: 'Hard Hat', compliant: 98, nonCompliant: 2, violations: 3, trend: '+1%' }
      ],
      trends: Array.from({ length: 7 }, (_, i) => ({
        day: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
        compliance: Math.random() * 10 + 85,
        violations: Math.floor(Math.random() * 20) + 5
      }))
    },
    anomalies: [
      { type: 'Unusual Activity', count: 5, severity: 'high', description: 'Abnormal movement patterns detected', confidence: 0.92 },
      { type: 'Crowd Density', count: 3, severity: 'medium', description: 'Higher than normal occupancy', confidence: 0.87 },
      { type: 'Time Anomaly', count: 2, severity: 'low', description: 'Activity outside normal hours', confidence: 0.78 },
      { type: 'Speed Violation', count: 4, severity: 'high', description: 'Vehicles exceeding speed limits', confidence: 0.95 }
    ],
    systemHealth: {
      cameras: [
        { id: 'CAM-01', name: 'Main Entrance', status: 'online', uptime: 99.8, lastSeen: '2 min ago', quality: 95 },
        { id: 'CAM-02', name: 'Loading Dock', status: 'online', uptime: 99.5, lastSeen: '1 min ago', quality: 92 },
        { id: 'CAM-03', name: 'Parking Lot', status: 'offline', uptime: 0, lastSeen: '2 hours ago', quality: 0 },
        { id: 'CAM-04', name: 'Office Area', status: 'online', uptime: 99.9, lastSeen: '30 sec ago', quality: 98 }
      ],
      performance: {
        cpuUsage: 67.3,
        memoryUsage: 78.9,
        diskUsage: 45.6,
        networkLatency: 12.4,
        totalUptime: 99.7
      }
    },
    efficiency: {
      metrics: [
        { name: 'Resource Utilization', value: 78.5, target: 80, status: 'good' },
        { name: 'Energy Efficiency', value: 85.2, target: 90, status: 'warning' },
        { name: 'Processing Speed', value: 92.1, target: 95, status: 'excellent' },
        { name: 'Storage Optimization', value: 88.7, target: 85, status: 'excellent' }
      ],
      trends: Array.from({ length: 12 }, (_, i) => ({
        month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][i],
        efficiency: Math.random() * 20 + 75,
        cost: Math.random() * 1000 + 5000
      }))
    }
  };

  const tabs = [
    { 
      id: 'traffic', 
      label: 'Traffic Flow', 
      icon: ArrowUpDown, 
      description: 'Movement patterns and directional analytics',
      color: 'blue',
      category: 'movement'
    },
    { 
      id: 'utilization', 
      label: 'Zone Utilization', 
      icon: MapPin, 
      description: 'Occupancy and efficiency metrics',
      color: 'green',
      category: 'space'
    },
    { 
      id: 'behavior', 
      label: 'Behavior Analysis', 
      icon: Brain, 
      description: 'Loitering, intrusion, and safety patterns',
      color: 'purple',
      category: 'behavior'
    },
    { 
      id: 'ppe', 
      label: 'PPE Compliance', 
      icon: Shield, 
      description: 'Safety gear compliance tracking',
      color: 'orange',
      category: 'safety'
    },
    { 
      id: 'anomalies', 
      label: 'Anomaly Detection', 
      icon: AlertTriangle, 
      description: 'Unusual activity identification',
      color: 'red',
      category: 'ai'
    },
    { 
      id: 'system', 
      label: 'System Health', 
      icon: Activity, 
      description: 'Camera and system performance',
      color: 'teal',
      category: 'technical'
    },
    { 
      id: 'efficiency', 
      label: 'Operational Efficiency', 
      icon: TrendingUp, 
      description: 'Resource usage optimization',
      color: 'indigo',
      category: 'performance'
    },
    { 
      id: 'heatmaps', 
      label: 'Heatmaps', 
      icon: Thermometer, 
      description: 'Visual activity intensity maps',
      color: 'pink',
      category: 'visualization'
    }
  ];

  // Helper functions
  const toggleCardExpansion = (cardId) => {
    setExpandedCards(prev => ({
      ...prev,
      [cardId]: !prev[cardId]
    }));
  };

  const getStatusColor = (status) => {
    const colors = {
      online: 'text-green-600 bg-green-50 border-green-200',
      offline: 'text-red-600 bg-red-50 border-red-200',
      warning: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      good: 'text-green-600 bg-green-50 border-green-200',
      excellent: 'text-blue-600 bg-blue-50 border-blue-200'
    };
    return colors[status] || colors.warning;
  };

  const getSeverityColor = (severity) => {
    const colors = {
      high: 'text-red-600 bg-red-50 border-red-200',
      medium: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      low: 'text-green-600 bg-green-50 border-green-200'
    };
    return colors[severity] || colors.medium;
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const generateAnalytics = async (analyticsType) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setAnalytics(sampleData);
    } catch (error) {
      console.error("Error generating analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    generateAnalytics(activeTab);
  }, [activeTab, dateRange, selectedCamera]);

  const renderTrafficFlow = () => (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { title: 'Total Traffic', value: '1,245', change: '+12%', icon: ArrowUpDown, color: 'blue' },
          { title: 'Peak Hour', value: '14:00', change: 'Most Active', icon: Clock, color: 'green' },
          { title: 'Efficiency', value: '87.3%', change: '+3%', icon: TrendingUp, color: 'purple' },
          { title: 'Net Flow', value: '+23', change: 'Positive', icon: ArrowUpRight, color: 'orange' }
        ].map((metric, index) => {
          const Icon = metric.icon;
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white p-6 rounded-xl shadow-lg"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">{metric.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                  <p className="text-xs text-gray-500">{metric.change}</p>
                </div>
                <Icon className="w-8 h-8 text-blue-600" />
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white p-6 rounded-xl shadow-lg"
        >
          <h3 className="text-lg font-semibold mb-4">Hourly Traffic Pattern</h3>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={sampleData.trafficFlow.hourly}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="entries" fill="#3b82f6" name="Entries" />
              <Bar dataKey="exits" fill="#ef4444" name="Exits" />
              <Line type="monotone" dataKey="efficiency" stroke="#10b981" strokeWidth={2} />
            </ComposedChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white p-6 rounded-xl shadow-lg"
        >
          <h3 className="text-lg font-semibold mb-4">Zone Traffic Analysis</h3>
          <div className="space-y-4">
            {sampleData.trafficFlow.zones.map((zone, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <MapPin className="w-5 h-5 text-blue-600" />
                  <div>
                    <span className="font-medium">{zone.zone}</span>
                    <p className="text-sm text-gray-600">Efficiency: {zone.efficiency}%</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">Net: {zone.net > 0 ? '+' : ''}{zone.net}</p>
                  <p className="text-xs text-gray-500">{zone.entries} in, {zone.exits} out</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );

  const renderUtilization = () => (
    <div className="space-y-6">
      {/* Zone Utilization Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sampleData.utilization.zones.map((zone, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <MapPin className="w-5 h-5 text-blue-600" />
                <span className="font-medium">{zone.name}</span>
              </div>
              <span className={`px-2 py-1 text-xs rounded-full border ${getStatusColor(zone.efficiency > 80 ? 'good' : 'warning')}`}>
                {zone.efficiency}% efficient
              </span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Utilization</span>
                <span className="font-semibold">{zone.utilization}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${zone.utilization}%` }}
                ></div>
              </div>
              <div className="flex justify-between items-center text-sm text-gray-600">
                <span>{zone.occupancy}/{zone.capacity}</span>
                {zone.alerts > 0 && (
                  <span className="text-red-600">{zone.alerts} alerts</span>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Utilization Trends */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white p-6 rounded-xl shadow-lg"
      >
        <h3 className="text-lg font-semibold mb-4">Utilization Trends (30 Days)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={sampleData.utilization.trends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="avgUtilization" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
            <Area type="monotone" dataKey="peakUtilization" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.6} />
          </AreaChart>
        </ResponsiveContainer>
      </motion.div>
    </div>
  );

  const renderBehaviorAnalysis = () => (
    <div className="space-y-6">
      {/* Behavior Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { title: 'Loitering Events', value: sampleData.behavior.loitering.length, icon: Timer, color: 'orange' },
          { title: 'Intrusion Alerts', value: sampleData.behavior.intrusions.length, icon: AlertTriangle, color: 'red' },
          { title: 'Suspicious Activity', value: '12', icon: Eye, color: 'purple' }
        ].map((metric, index) => {
          const Icon = metric.icon;
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white p-6 rounded-xl shadow-lg"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">{metric.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                </div>
                <Icon className="w-8 h-8 text-orange-600" />
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Behavior Events */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white p-6 rounded-xl shadow-lg"
        >
          <h3 className="text-lg font-semibold mb-4">Recent Loitering Events</h3>
          <div className="space-y-3">
            {sampleData.behavior.loitering.map((event, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Timer className="w-5 h-5 text-orange-600" />
                  <div>
                    <span className="font-medium">{event.location}</span>
                    <p className="text-sm text-gray-600">{event.person} - {event.duration} min</p>
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${getSeverityColor(event.severity)}`}>
                  {event.severity}
                </span>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white p-6 rounded-xl shadow-lg"
        >
          <h3 className="text-lg font-semibold mb-4">Intrusion Events</h3>
          <div className="space-y-3">
            {sampleData.behavior.intrusions.map((event, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                  <div>
                    <span className="font-medium">{event.zone}</span>
                    <p className="text-sm text-gray-600">{event.person} - {event.timestamp}</p>
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${getSeverityColor(event.severity)}`}>
                  {event.severity}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'traffic': return renderTrafficFlow();
      case 'utilization': return renderUtilization();
      case 'behavior': return renderBehaviorAnalysis();
      case 'ppe': return <div className="text-center py-12"><h3 className="text-xl font-semibold">PPE Compliance Analytics</h3><p className="text-gray-600">Coming soon...</p></div>;
      case 'anomalies': return <div className="text-center py-12"><h3 className="text-xl font-semibold">Anomaly Detection</h3><p className="text-gray-600">Coming soon...</p></div>;
      case 'system': return <div className="text-center py-12"><h3 className="text-xl font-semibold">System Health</h3><p className="text-gray-600">Coming soon...</p></div>;
      case 'efficiency': return <div className="text-center py-12"><h3 className="text-xl font-semibold">Operational Efficiency</h3><p className="text-gray-600">Coming soon...</p></div>;
      case 'heatmaps': return <div className="text-center py-12"><h3 className="text-xl font-semibold">Heatmaps</h3><p className="text-gray-600">Coming soon...</p></div>;
      default: return renderTrafficFlow();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="p-6">
        {/* Enhanced Header */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Advanced Analytics</h1>
              <p className="text-gray-600 text-lg">Comprehensive insights and data-driven analytics for your surveillance system</p>
            </div>
            <div className="flex items-center space-x-3">
              <button 
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  autoRefresh 
                    ? 'bg-green-100 text-green-700 border border-green-200' 
                    : 'bg-gray-100 text-gray-700 border border-gray-200'
                }`}
              >
                {autoRefresh ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                <span className="text-sm font-medium">
                  {autoRefresh ? 'Auto Refresh ON' : 'Auto Refresh OFF'}
                </span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                <Download className="w-4 h-4" />
                <span className="text-sm font-medium">Export Data</span>
              </button>
            </div>
          </div>
        </motion.div>

        {/* Enhanced Filters */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-lg mb-6 p-6"
        >
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-gray-500" />
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <span className="text-gray-500">to</span>
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select 
                value={selectedCamera}
                onChange={(e) => setSelectedCamera(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Cameras</option>
                <option value="cam1">Camera 1</option>
                <option value="cam2">Camera 2</option>
                <option value="cam3">Camera 3</option>
                <option value="cam4">Camera 4</option>
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-gray-500" />
              <select 
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
              </select>
            </div>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => generateAnalytics(activeTab)}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Generating...' : 'Refresh Analytics'}</span>
            </motion.button>
          </div>
        </motion.div>

        {/* Enhanced Analytics Tabs */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl shadow-lg mb-6"
        >
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Analytics Categories</h2>
              <div className="flex items-center space-x-2">
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
          </div>
          
          <div className="flex overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-3 px-6 py-4 border-b-2 transition-all duration-200 ${
                    isActive
                      ? `border-${tab.color}-600 text-${tab.color}-600 bg-${tab.color}-50`
                      : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <div className="text-left">
                    <span className="whitespace-nowrap font-medium">{tab.label}</span>
                    <p className="text-xs text-gray-500">{tab.description}</p>
                  </div>
                  {isActive && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-2 h-2 bg-blue-600 rounded-full"
                    />
                  )}
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* Enhanced Content with Loading State */}
        <motion.div 
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="flex items-center space-x-3">
                <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
                <span className="text-lg font-medium text-gray-600">Generating analytics...</span>
              </div>
            </div>
          ) : (
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                {renderContent()}
              </motion.div>
            </AnimatePresence>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default Analytics;