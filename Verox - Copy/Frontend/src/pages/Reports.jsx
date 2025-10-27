import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Area, AreaChart, Scatter, ScatterChart,
  ComposedChart, RadialBarChart, RadialBar, RadarChart, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, Radar, FunnelChart, Funnel, LabelList, Treemap
} from 'recharts';
import { 
  Calendar, Download, Filter, TrendingUp, Users, AlertTriangle, 
  Shield, Clock, MapPin, Activity, Eye, BarChart3, PieChart as PieChartIcon,
  FileText, Search, Settings, Zap, Target, AlertCircle, Brain, Database,
  TrendingDown, AlertOctagon, CheckCircle, XCircle, Timer, UserCheck,
  RefreshCw, Maximize2, Minimize2, ChevronDown, ChevronUp, Star,
  ArrowUpRight, ArrowDownRight, Minus, Play, Pause, RotateCcw,
  Layers, Grid3X3, BarChart2, LineChart as LineChartIcon, PieChart as PieChartIcon2,
  Table, List, Grid, MoreHorizontal, Edit, Trash2, Copy, Share2
} from 'lucide-react';

const Reports = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });
  const [selectedCamera, setSelectedCamera] = useState('all');
  const [reports, setReports] = useState({});
  const [loading, setLoading] = useState(false);
  const [violationTimeframe, setViolationTimeframe] = useState('7d');
  const [violationType, setViolationType] = useState('all');
  const [viewMode, setViewMode] = useState('grid'); // grid, list, table
  const [expandedCards, setExpandedCards] = useState({});
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [selectedMetrics, setSelectedMetrics] = useState(['detections', 'alerts', 'compliance']);
  const [chartType, setChartType] = useState('bar'); // bar, line, pie, area
  const [timeframe, setTimeframe] = useState('24h'); // 24h, 7d, 30d, 90d
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('timestamp');
  const [sortOrder, setSortOrder] = useState('desc');

  // Comprehensive sample data for all advanced reports
  const sampleData = {
    // Enhanced Object & Activity Reports
    objectCounts: [
      { name: 'Person', count: 1250, color: '#22c55e', trend: '+12%', confidence: 94.2, avgSize: 'Medium' },
      { name: 'Vehicle', count: 890, color: '#3b82f6', trend: '+8%', confidence: 97.8, avgSize: 'Large' },
      { name: 'Forklift', count: 45, color: '#f59e0b', trend: '-3%', confidence: 99.1, avgSize: 'Large' },
      { name: 'Package', count: 320, color: '#8b5cf6', trend: '+15%', confidence: 89.5, avgSize: 'Small' },
      { name: 'Bicycle', count: 120, color: '#06b6d4', trend: '+5%', confidence: 92.3, avgSize: 'Medium' },
      { name: 'Motorcycle', count: 35, color: '#ef4444', trend: '+22%', confidence: 95.7, avgSize: 'Medium' },
      { name: 'Truck', count: 78, color: '#f97316', trend: '-8%', confidence: 98.9, avgSize: 'XLarge' },
      { name: 'Cart', count: 156, color: '#84cc16', trend: '+18%', confidence: 87.2, avgSize: 'Small' }
    ],

    // Enhanced Detection Analytics
    detectionAnalytics: {
      totalDetections: 2848,
      accuracy: 94.7,
      falsePositives: 2.3,
      falseNegatives: 1.8,
      avgProcessingTime: 45.2,
      peakHour: '14:00-15:00',
      lowActivityHour: '02:00-04:00'
    },

    // Real-time Performance Metrics
    performanceMetrics: {
      systemUptime: 99.8,
      avgLatency: 45.2,
      throughput: 1250,
      errorRate: 0.2,
      cpuUsage: 67.3,
      memoryUsage: 78.9,
      diskUsage: 45.6,
      networkLatency: 12.4
    },
    
    // Enhanced Zone Analytics
    zoneOccupancy: [
      { 
        zone: 'Loading Dock', 
        occupancy: 85, 
        capacity: 100, 
        utilization: 85, 
        alerts: 3, 
        temperature: 22.5, 
        humidity: 45, 
        lastActivity: '2 min ago',
        status: 'active',
        efficiency: 92.3
      },
      { 
        zone: 'Warehouse', 
        occupancy: 60, 
        capacity: 150, 
        utilization: 40, 
        alerts: 1, 
        temperature: 20.1, 
        humidity: 38, 
        lastActivity: '5 min ago',
        status: 'normal',
        efficiency: 87.6
      },
      { 
        zone: 'Office', 
        occupancy: 30, 
        capacity: 50, 
        utilization: 60, 
        alerts: 0, 
        temperature: 23.2, 
        humidity: 42, 
        lastActivity: '1 min ago',
        status: 'active',
        efficiency: 95.1
      },
      { 
        zone: 'Parking', 
        occupancy: 120, 
        capacity: 200, 
        utilization: 60, 
        alerts: 2, 
        temperature: 18.7, 
        humidity: 55, 
        lastActivity: '30 sec ago',
        status: 'active',
        efficiency: 78.9
      },
      { 
        zone: 'Restricted Area', 
        occupancy: 5, 
        capacity: 10, 
        utilization: 50, 
        alerts: 8, 
        temperature: 21.3, 
        humidity: 41, 
        lastActivity: '15 min ago',
        status: 'warning',
        efficiency: 45.2
      },
      { 
        zone: 'Production Floor', 
        occupancy: 45, 
        capacity: 80, 
        utilization: 56, 
        alerts: 0, 
        temperature: 24.8, 
        humidity: 48, 
        lastActivity: '3 min ago',
        status: 'active',
        efficiency: 89.7
      }
    ],

    // Enhanced Traffic Patterns with more detailed data
    trafficPatterns: {
      hourly: Array.from({ length: 24 }, (_, i) => ({
        hour: `${i}:00`,
        count: Math.floor(Math.random() * 100) + 20,
        trend: i >= 8 && i <= 17 ? 'high' : i >= 18 && i <= 22 ? 'medium' : 'low',
        efficiency: Math.random() * 30 + 70,
        peak: i >= 14 && i <= 16
      })),
      daily: Array.from({ length: 7 }, (_, i) => ({
        day: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][i],
        count: Math.floor(Math.random() * 500) + 200,
        efficiency: Math.random() * 20 + 80,
        peak: i >= 1 && i <= 5
      })),
      weekly: Array.from({ length: 4 }, (_, i) => ({
        week: `Week ${i + 1}`,
        count: Math.floor(Math.random() * 2000) + 1000,
        efficiency: Math.random() * 15 + 85,
        trend: Math.random() > 0.5 ? 'up' : 'down'
      }))
    },
    
    // Traffic Patterns
    hourlyTraffic: Array.from({ length: 24 }, (_, i) => ({
      hour: `${i}:00`,
      count: Math.floor(Math.random() * 100) + 20,
      trend: i >= 8 && i <= 17 ? 'high' : i >= 18 && i <= 22 ? 'medium' : 'low'
    })),
    
    // Compliance & Safety
    complianceData: [
      { category: 'Helmet', compliant: 95, nonCompliant: 5, violations: 12 },
      { category: 'Safety Vest', compliant: 88, nonCompliant: 12, violations: 8 },
      { category: 'Safety Glasses', compliant: 92, nonCompliant: 8, violations: 6 },
      { category: 'Gloves', compliant: 85, nonCompliant: 15, violations: 15 },
      { category: 'Hard Hat', compliant: 98, nonCompliant: 2, violations: 3 }
    ],
    
    // Shift Analytics
    shiftTotals: {
      morning: { person: 450, vehicle: 320, forklift: 20, package: 150 },
      afternoon: { person: 380, vehicle: 280, forklift: 15, package: 120 },
      night: { person: 120, vehicle: 80, forklift: 5, package: 30 }
    },
    
    // Alert & Event Analytics
    alertMetrics: {
      totalAlerts: 45,
      avgResponseTime: 2.3,
      resolutionRate: 98,
      alertTypes: [
        { type: 'Intrusion', count: 15, severity: 'high', responseTime: 1.2 },
        { type: 'Loitering', count: 12, severity: 'medium', responseTime: 3.1 },
        { type: 'PPE Violation', count: 8, severity: 'low', responseTime: 4.5 },
        { type: 'Line Crossing', count: 10, severity: 'medium', responseTime: 2.8 }
      ]
    },
    
    // Heatmap Data
    heatmapData: Array.from({ length: 7 }, (_, day) => 
      Array.from({ length: 24 }, (_, hour) => ({
        day: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][day],
        hour: hour,
        activity: Math.floor(Math.random() * 100)
      }))
    ).flat(),
    
    // Event Timeline
    eventTimeline: Array.from({ length: 20 }, (_, i) => ({
      id: i + 1,
      timestamp: new Date(Date.now() - i * 3600000).toISOString(),
      camera: `Camera ${Math.floor(Math.random() * 8) + 1}`,
      event: ['Person detected', 'Vehicle entered', 'Intrusion alert', 'PPE violation'][Math.floor(Math.random() * 4)],
      severity: ['high', 'medium', 'low'][Math.floor(Math.random() * 3)],
      confidence: Math.random() * 0.4 + 0.6
    })),
    
    // Utilization Reports
    utilizationData: [
      { date: '2024-01-01', dock: 85, warehouse: 60, office: 30, parking: 120 },
      { date: '2024-01-02', dock: 90, warehouse: 65, office: 35, parking: 110 },
      { date: '2024-01-03', dock: 80, warehouse: 55, office: 25, parking: 130 },
      { date: '2024-01-04', dock: 95, warehouse: 70, office: 40, parking: 140 },
      { date: '2024-01-05', dock: 75, warehouse: 50, office: 20, parking: 100 }
    ],
    
    // Anomaly Detection
    anomalies: [
      { type: 'Unusual Activity', count: 5, severity: 'high', description: 'Abnormal movement patterns detected' },
      { type: 'Crowd Density', count: 3, severity: 'medium', description: 'Higher than normal occupancy' },
      { type: 'Time Anomaly', count: 2, severity: 'low', description: 'Activity outside normal hours' }
    ],
    
    // Line Crossing Analytics
    lineCrossingData: [
      { line: 'Main Entrance', entries: 245, exits: 238, net: 7 },
      { line: 'Loading Dock', entries: 89, exits: 92, net: -3 },
      { line: 'Emergency Exit', entries: 12, exits: 8, net: 4 },
      { line: 'Restricted Zone', entries: 3, exits: 2, net: 1 }
    ],
    
    // Loitering Events
    loiteringEvents: [
      { location: 'Loading Dock', duration: 15, person: 'Person A', severity: 'medium' },
      { location: 'Parking Lot', duration: 8, person: 'Person B', severity: 'low' },
      { location: 'Restricted Area', duration: 25, person: 'Person C', severity: 'high' }
    ],
    
    // Intrusion Events
    intrusionEvents: [
      { zone: 'Restricted Area', timestamp: '2024-01-15 14:30', person: 'Unknown', severity: 'high' },
      { zone: 'After Hours Office', timestamp: '2024-01-15 22:15', person: 'Employee X', severity: 'medium' },
      { zone: 'Equipment Room', timestamp: '2024-01-15 16:45', person: 'Maintenance', severity: 'low' }
    ],
    
    // Fall/Hazard Events
    hazardEvents: [
      { type: 'Slip', location: 'Loading Dock', severity: 'high', timestamp: '2024-01-15 10:30' },
      { type: 'Trip', location: 'Warehouse', severity: 'medium', timestamp: '2024-01-15 15:20' },
      { type: 'PPE Violation', location: 'Construction Zone', severity: 'high', timestamp: '2024-01-15 09:15' }
    ],

    // Violation Reports Data
    violations: [
      {
        id: 'V001',
        type: 'Unauthorized Access',
        severity: 'High',
        timestamp: '2024-01-15 14:32:15',
        location: 'Restricted Area - Loading Dock',
        camera: 'Camera-03',
        description: 'Person detected in restricted zone without proper authorization',
        image: '/api/violations/v001.jpg',
        status: 'Resolved',
        resolvedBy: 'Security Team Alpha',
        resolvedAt: '2024-01-15 14:45:22'
      },
      {
        id: 'V002',
        type: 'PPE Violation',
        severity: 'Medium',
        timestamp: '2024-01-15 13:28:45',
        location: 'Warehouse Floor - Section A',
        camera: 'Camera-07',
        description: 'Worker not wearing required safety helmet in designated area',
        image: '/api/violations/v002.jpg',
        status: 'Under Investigation',
        resolvedBy: null,
        resolvedAt: null
      },
      {
        id: 'V003',
        type: 'Loitering',
        severity: 'Low',
        timestamp: '2024-01-15 12:15:30',
        location: 'Parking Area - Zone B',
        camera: 'Camera-12',
        description: 'Person loitering in parking area for extended period',
        image: '/api/violations/v003.jpg',
        status: 'Resolved',
        resolvedBy: 'Patrol Officer',
        resolvedAt: '2024-01-15 12:25:15'
      },
      {
        id: 'V004',
        type: 'Safety Protocol Breach',
        severity: 'High',
        timestamp: '2024-01-15 11:45:12',
        location: 'Production Floor - Line 3',
        camera: 'Camera-05',
        description: 'Worker bypassing safety barriers during equipment operation',
        image: '/api/violations/v004.jpg',
        status: 'Escalated',
        resolvedBy: null,
        resolvedAt: null
      },
      {
        id: 'V005',
        type: 'After Hours Access',
        severity: 'Medium',
        timestamp: '2024-01-14 22:30:45',
        location: 'Office Building - Floor 2',
        camera: 'Camera-09',
        description: 'Unauthorized access to office building after business hours',
        image: '/api/violations/v005.jpg',
        status: 'Resolved',
        resolvedBy: 'Night Security',
        resolvedAt: '2024-01-14 22:45:30'
      },
      {
        id: 'V006',
        type: 'Vehicle Violation',
        severity: 'Medium',
        timestamp: '2024-01-14 16:20:15',
        location: 'Loading Dock - Gate 2',
        camera: 'Camera-02',
        description: 'Vehicle exceeding speed limit in restricted area',
        image: '/api/violations/v006.jpg',
        status: 'Under Investigation',
        resolvedBy: null,
        resolvedAt: null
      },
      {
        id: 'V007',
        type: 'Equipment Misuse',
        severity: 'High',
        timestamp: '2024-01-14 15:10:30',
        location: 'Warehouse - Equipment Zone',
        camera: 'Camera-08',
        description: 'Improper use of forklift without proper certification',
        image: '/api/violations/v007.jpg',
        status: 'Resolved',
        resolvedBy: 'Safety Supervisor',
        resolvedAt: '2024-01-14 15:25:45'
      },
      {
        id: 'V008',
        type: 'Crowd Density',
        severity: 'Low',
        timestamp: '2024-01-14 14:05:20',
        location: 'Main Entrance',
        camera: 'Camera-01',
        description: 'Crowd density exceeding safety limits during peak hours',
        image: '/api/violations/v008.jpg',
        status: 'Resolved',
        resolvedBy: 'Crowd Control Team',
        resolvedAt: '2024-01-14 14:15:10'
      }
    ]
  };

  // Enhanced tabs with categories and better organization
  const tabs = [
    { 
      id: 'overview', 
      label: 'Overview', 
      icon: BarChart3, 
      description: 'Key metrics and KPIs',
      category: 'dashboard',
      color: 'blue'
    },
    { 
      id: 'objects', 
      label: 'Object Counts', 
      icon: Users, 
      description: 'Detection analytics',
      category: 'analytics',
      color: 'green'
    },
    { 
      id: 'zones', 
      label: 'Zone Analytics', 
      icon: MapPin, 
      description: 'Occupancy and utilization',
      category: 'analytics',
      color: 'purple'
    },
    { 
      id: 'compliance', 
      label: 'Compliance', 
      icon: Shield, 
      description: 'Safety and PPE reports',
      category: 'safety',
      color: 'orange'
    },
    { 
      id: 'violations', 
      label: 'Violations', 
      icon: AlertOctagon, 
      description: 'Security violations and incidents',
      category: 'security',
      color: 'red'
    },
    { 
      id: 'alerts', 
      label: 'Alerts & Events', 
      icon: AlertTriangle, 
      description: 'Incident management',
      category: 'security',
      color: 'yellow'
    },
    { 
      id: 'traffic', 
      label: 'Traffic Patterns', 
      icon: TrendingUp, 
      description: 'Movement analytics',
      category: 'analytics',
      color: 'blue'
    },
    { 
      id: 'linecrossing', 
      label: 'Line Crossing', 
      icon: Target, 
      description: 'Entry/exit analytics',
      category: 'analytics',
      color: 'indigo'
    },
    { 
      id: 'loitering', 
      label: 'Loitering', 
      icon: Timer, 
      description: 'Duration tracking',
      category: 'security',
      color: 'amber'
    },
    { 
      id: 'intrusion', 
      label: 'Intrusion', 
      icon: AlertOctagon, 
      description: 'Unauthorized access',
      category: 'security',
      color: 'red'
    },
    { 
      id: 'hazards', 
      label: 'Hazards', 
      icon: AlertCircle, 
      description: 'Safety incidents',
      category: 'safety',
      color: 'orange'
    },
    { 
      id: 'anomaly', 
      label: 'Anomaly Detection', 
      icon: Brain, 
      description: 'Unusual activity',
      category: 'ai',
      color: 'purple'
    },
    { 
      id: 'utilization', 
      label: 'Utilization', 
      icon: Database, 
      description: 'Resource usage',
      category: 'performance',
      color: 'teal'
    },
    { 
      id: 'export', 
      label: 'Export Data', 
      icon: Download, 
      description: 'Data export tools',
      category: 'tools',
      color: 'gray'
    }
  ];

  // Helper functions for enhanced UI
  const toggleCardExpansion = (cardId) => {
    setExpandedCards(prev => ({
      ...prev,
      [cardId]: !prev[cardId]
    }));
  };

  const getStatusColor = (status) => {
    const colors = {
      active: 'text-green-600 bg-green-50 border-green-200',
      normal: 'text-blue-600 bg-blue-50 border-blue-200',
      warning: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      error: 'text-red-600 bg-red-50 border-red-200',
      offline: 'text-gray-600 bg-gray-50 border-gray-200'
    };
    return colors[status] || colors.normal;
  };

  const getTrendIcon = (trend) => {
    if (trend.startsWith('+')) return <ArrowUpRight className="w-4 h-4 text-green-600" />;
    if (trend.startsWith('-')) return <ArrowDownRight className="w-4 h-4 text-red-600" />;
    return <Minus className="w-4 h-4 text-gray-600" />;
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const getChartTypeIcon = (type) => {
    const icons = {
      bar: BarChart2,
      line: LineChartIcon,
      pie: PieChartIcon2,
      area: AreaChart
    };
    return icons[type] || BarChart2;
  };

  const generateReport = async (reportType) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setReports(prev => ({ ...prev, [reportType]: sampleData }));
    } catch (error) {
      console.error('Error generating report:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    generateReport('overview');
  }, [dateRange, selectedCamera]);

      const renderOverview = () => (
        <div className="space-y-6">
          {/* Enhanced Key Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { 
                title: 'Total Detections', 
                value: formatNumber(sampleData.detectionAnalytics.totalDetections), 
                change: '+12%', 
                icon: Users, 
                color: 'blue',
                trend: 'up',
                subtitle: `${sampleData.detectionAnalytics.accuracy}% accuracy`
              },
              { 
                title: 'Active Cameras', 
                value: '8', 
                change: 'All operational', 
                icon: Eye, 
                color: 'green',
                trend: 'stable',
                subtitle: `${sampleData.performanceMetrics.systemUptime}% uptime`
              },
              { 
                title: 'Alerts Today', 
                value: '12', 
                change: '3 high priority', 
                icon: AlertTriangle, 
                color: 'orange',
                trend: 'down',
                subtitle: 'Avg response: 2.3m'
              },
              { 
                title: 'Compliance Rate', 
                value: '94%', 
                change: '+2% improvement', 
                icon: Shield, 
                color: 'purple',
                trend: 'up',
                subtitle: 'Safety score: 92.3'
              }
            ].map((metric, index) => {
              const Icon = metric.icon;
              const colorClasses = {
                blue: 'from-blue-500 to-blue-600',
                green: 'from-green-500 to-green-600',
                orange: 'from-orange-500 to-orange-600',
                purple: 'from-purple-500 to-purple-600'
              };
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`bg-gradient-to-br ${colorClasses[metric.color]} p-6 rounded-xl text-white shadow-lg hover:shadow-xl transition-all duration-300`}
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-2">
                      <Icon className="w-6 h-6 text-white/80" />
                      <span className="text-white/80 text-sm font-medium">{metric.title}</span>
                    </div>
                    {getTrendIcon(metric.change)}
                  </div>
                  <div className="space-y-2">
                    <p className="text-3xl font-bold">{metric.value}</p>
                    <p className="text-white/70 text-sm">{metric.change}</p>
                    <p className="text-white/60 text-xs">{metric.subtitle}</p>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Performance Metrics Row */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-4"
          >
            <div className="bg-white p-6 rounded-xl shadow-lg">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Activity className="w-5 h-5 text-blue-600 mr-2" />
                System Performance
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">CPU Usage</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${sampleData.performanceMetrics.cpuUsage}%` }}></div>
                    </div>
                    <span className="text-sm font-medium">{sampleData.performanceMetrics.cpuUsage}%</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Memory Usage</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{ width: `${sampleData.performanceMetrics.memoryUsage}%` }}></div>
                    </div>
                    <span className="text-sm font-medium">{sampleData.performanceMetrics.memoryUsage}%</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Network Latency</span>
                  <span className="text-sm font-medium">{sampleData.performanceMetrics.networkLatency}ms</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-lg">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Zap className="w-5 h-5 text-yellow-600 mr-2" />
                Detection Analytics
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Accuracy</span>
                  <span className="text-sm font-medium text-green-600">{sampleData.detectionAnalytics.accuracy}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">False Positives</span>
                  <span className="text-sm font-medium text-orange-600">{sampleData.detectionAnalytics.falsePositives}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Processing Time</span>
                  <span className="text-sm font-medium">{sampleData.detectionAnalytics.avgProcessingTime}ms</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-lg">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Clock className="w-5 h-5 text-purple-600 mr-2" />
                Peak Activity
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Peak Hour</span>
                  <span className="text-sm font-medium">{sampleData.detectionAnalytics.peakHour}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Low Activity</span>
                  <span className="text-sm font-medium">{sampleData.detectionAnalytics.lowActivityHour}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Throughput</span>
                  <span className="text-sm font-medium">{sampleData.performanceMetrics.throughput}/min</span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Enhanced Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-white p-6 rounded-xl shadow-lg"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Hourly Traffic Pattern</h3>
                <div className="flex items-center space-x-2">
                  <button className="p-2 hover:bg-gray-100 rounded-lg">
                    <RefreshCw className="w-4 h-4" />
                  </button>
                  <button className="p-2 hover:bg-gray-100 rounded-lg">
                    <Maximize2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={sampleData.trafficPatterns.hourly}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="count" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="bg-white p-6 rounded-xl shadow-lg"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Object Distribution</h3>
                <div className="flex items-center space-x-2">
                  <button className="p-2 hover:bg-gray-100 rounded-lg">
                    <RefreshCw className="w-4 h-4" />
                  </button>
                  <button className="p-2 hover:bg-gray-100 rounded-lg">
                    <Maximize2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={sampleData.objectCounts}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
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
          </div>

          {/* Zone Status Overview */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="bg-white p-6 rounded-xl shadow-lg"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Zone Status Overview</h3>
              <div className="flex items-center space-x-2">
                <button className="px-3 py-1 text-sm bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200">
                  View All
                </button>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sampleData.zoneOccupancy.map((zone, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 border rounded-lg hover:shadow-md transition-all duration-300"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <MapPin className="w-4 h-4 text-blue-600" />
                      <span className="font-medium text-sm">{zone.zone}</span>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full border ${getStatusColor(zone.status)}`}>
                      {zone.status}
                    </span>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-600">Utilization</span>
                      <span className="text-sm font-medium">{zone.utilization}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${zone.utilization}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between items-center text-xs text-gray-600">
                      <span>{zone.occupancy}/{zone.capacity}</span>
                      <span>{zone.temperature}°C</span>
                    </div>
                    {zone.alerts > 0 && (
                      <div className="flex items-center space-x-1">
                        <AlertTriangle className="w-3 h-3 text-red-500" />
                        <span className="text-xs text-red-600">{zone.alerts} alerts</span>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      );

  const renderObjectCounts = () => (
    <div className="space-y-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-4 rounded-lg shadow-lg"
      >
        <h3 className="text-lg font-semibold mb-3">Object Detection Counts</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={sampleData.objectCounts}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </motion.div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white p-4 rounded-lg shadow-lg"
      >
        <h3 className="text-lg font-semibold mb-3">Detection Trends</h3>
        <div className="space-y-2">
          {sampleData.objectCounts.map((item, index) => (
            <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                <span className="font-medium text-sm">{item.name}</span>
              </div>
              <div className="text-right">
                <p className="font-semibold text-sm">{item.count}</p>
                <p className={`text-xs ${item.trend.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                  {item.trend}
                </p>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white p-4 rounded-lg shadow-lg"
      >
        <h3 className="text-lg font-semibold mb-3">Shift Comparison</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
            <span className="font-medium text-sm">Morning</span>
            <div className="flex space-x-3 text-xs">
              <span className="text-blue-600">👥 450</span>
              <span className="text-green-600">🚗 320</span>
              <span className="text-orange-600">🚛 20</span>
            </div>
          </div>
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
            <span className="font-medium text-sm">Afternoon</span>
            <div className="flex space-x-3 text-xs">
              <span className="text-blue-600">👥 380</span>
              <span className="text-green-600">🚗 280</span>
              <span className="text-orange-600">🚛 15</span>
            </div>
          </div>
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
            <span className="font-medium text-sm">Night</span>
            <div className="flex space-x-3 text-xs">
              <span className="text-blue-600">👥 120</span>
              <span className="text-green-600">🚗 80</span>
              <span className="text-orange-600">🚛 5</span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );

  const renderZoneAnalytics = () => (
    <div className="space-y-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-4 rounded-lg shadow-lg"
      >
        <h3 className="text-lg font-semibold mb-3">Zone Occupancy & Utilization</h3>
        <div className="space-y-2">
          {sampleData.zoneOccupancy.map((zone, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div className="flex items-center space-x-2">
                <MapPin className="w-4 h-4 text-blue-600" />
                <div>
                  <span className="font-medium text-sm">{zone.zone}</span>
                  <p className="text-xs text-gray-600">Util: {zone.utilization}%</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="text-right">
                  <p className="text-xs text-gray-600">Occupancy</p>
                  <p className="font-semibold text-sm">{zone.occupancy}/{zone.capacity}</p>
                </div>
                <div className="w-16 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${zone.utilization}%` }}
                  ></div>
                </div>
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
    </div>
  );

  const renderCompliance = () => (
    <div className="space-y-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-4 rounded-lg shadow-lg"
      >
        <h3 className="text-lg font-semibold mb-3">PPE Compliance Report</h3>
        <div className="space-y-3">
          {sampleData.complianceData.map((item, index) => (
            <div key={index} className="p-3 border rounded">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm">{item.category}</span>
                <span className="text-xs text-gray-600">{item.compliant}% compliant</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                <div 
                  className="bg-green-600 h-2 rounded-full" 
                  style={{ width: `${item.compliant}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-gray-600">
                <span>Compliant: {item.compliant}%</span>
                <span>Violations: {item.violations}</span>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );

  const renderAlerts = () => (
    <div className="space-y-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-4 rounded-lg shadow-lg"
      >
        <h3 className="text-lg font-semibold mb-3">Alert Summary</h3>
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="text-center p-3 bg-red-50 rounded">
            <p className="text-xl font-bold text-red-600">{sampleData.alertMetrics.totalAlerts}</p>
            <p className="text-xs text-gray-600">Total Alerts</p>
          </div>
          <div className="text-center p-3 bg-blue-50 rounded">
            <p className="text-xl font-bold text-blue-600">{sampleData.alertMetrics.avgResponseTime}m</p>
            <p className="text-xs text-gray-600">Avg Response</p>
          </div>
          <div className="text-center p-3 bg-green-50 rounded">
            <p className="text-xl font-bold text-green-600">{sampleData.alertMetrics.resolutionRate}%</p>
            <p className="text-xs text-gray-600">Resolution</p>
          </div>
        </div>

        <div className="space-y-2">
          {sampleData.alertMetrics.alertTypes.map((alert, index) => (
            <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  alert.severity === 'high' ? 'bg-red-500' : 
                  alert.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                }`}></div>
                <span className="font-medium text-sm">{alert.type}</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-xs text-gray-600">{alert.count} events</span>
                <span className="text-xs text-gray-600">{alert.responseTime}m</span>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );

  const renderTrafficPatterns = () => (
    <div className="space-y-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-4 rounded-lg shadow-lg"
      >
        <h3 className="text-lg font-semibold mb-3">Peak Traffic Analysis</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={sampleData.hourlyTraffic}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </motion.div>
    </div>
  );

  const renderExport = () => (
    <div className="space-y-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-4 rounded-lg shadow-lg"
      >
        <h3 className="text-lg font-semibold mb-3">Export Reports</h3>
        <div className="grid grid-cols-2 gap-3">
          {[
            { name: 'Object Counts', format: 'CSV', size: '2.3 MB', icon: BarChart3 },
            { name: 'Zone Analytics', format: 'Excel', size: '1.8 MB', icon: MapPin },
            { name: 'Compliance Report', format: 'PDF', size: '3.1 MB', icon: Shield },
            { name: 'Alert Timeline', format: 'JSON', size: '1.2 MB', icon: AlertTriangle },
            { name: 'Traffic Patterns', format: 'CSV', size: '2.7 MB', icon: TrendingUp },
            { name: 'Comprehensive', format: 'ZIP', size: '8.5 MB', icon: FileText }
          ].map((report, index) => {
            const Icon = report.icon;
            return (
              <motion.div 
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-3 border rounded hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center space-x-2">
                    <Icon className="w-4 h-4 text-blue-600" />
                    <h4 className="font-medium text-sm">{report.name}</h4>
                  </div>
                  <Download className="w-4 h-4 text-gray-400" />
                </div>
                <div className="flex items-center justify-between text-xs text-gray-600">
                  <span>{report.format}</span>
                  <span>{report.size}</span>
                </div>
              </motion.div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );

  const renderLineCrossing = () => (
    <div className="space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-6 rounded-xl shadow-lg"
      >
        <h3 className="text-xl font-semibold mb-4">Line Crossing Analytics</h3>
        <div className="space-y-4">
          {sampleData.lineCrossingData.map((line, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <Target className="w-5 h-5 text-blue-600" />
                <div>
                  <span className="font-medium">{line.line}</span>
                  <p className="text-sm text-gray-600">Net: {line.net > 0 ? '+' : ''}{line.net}</p>
                </div>
              </div>
              <div className="flex items-center space-x-6">
                <div className="text-center">
                  <p className="text-sm text-gray-600">Entries</p>
                  <p className="font-semibold text-green-600">{line.entries}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Exits</p>
                  <p className="font-semibold text-red-600">{line.exits}</p>
                </div>
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${line.net > 0 ? 'bg-green-600' : 'bg-red-600'}`}
                    style={{ width: `${Math.abs(line.net) * 2}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );

  const renderLoitering = () => (
    <div className="space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-6 rounded-xl shadow-lg"
      >
        <h3 className="text-xl font-semibold mb-4">Loitering Events</h3>
        <div className="space-y-4">
          {sampleData.loiteringEvents.map((event, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <Timer className="w-5 h-5 text-orange-600" />
                <div>
                  <span className="font-medium">{event.location}</span>
                  <p className="text-sm text-gray-600">{event.person} - {event.duration} minutes</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  event.severity === 'high' ? 'bg-red-100 text-red-800' :
                  event.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {event.severity}
                </span>
                <span className="text-sm text-gray-600">{event.duration} min</span>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );

  const renderIntrusion = () => (
    <div className="space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-6 rounded-xl shadow-lg"
      >
        <h3 className="text-xl font-semibold mb-4">Intrusion Events</h3>
        <div className="space-y-4">
          {sampleData.intrusionEvents.map((event, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <AlertOctagon className="w-5 h-5 text-red-600" />
                <div>
                  <span className="font-medium">{event.zone}</span>
                  <p className="text-sm text-gray-600">{event.person} - {event.timestamp}</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  event.severity === 'high' ? 'bg-red-100 text-red-800' :
                  event.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {event.severity}
                </span>
                <span className="text-sm text-gray-600">{event.timestamp.split(' ')[1]}</span>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );

  const renderHazards = () => (
    <div className="space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-6 rounded-xl shadow-lg"
      >
        <h3 className="text-xl font-semibold mb-4">Hazard & Safety Events</h3>
        <div className="space-y-4">
          {sampleData.hazardEvents.map((event, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <div>
                  <span className="font-medium">{event.type}</span>
                  <p className="text-sm text-gray-600">{event.location} - {event.timestamp}</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  event.severity === 'high' ? 'bg-red-100 text-red-800' :
                  event.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {event.severity}
                </span>
                <span className="text-sm text-gray-600">{event.timestamp.split(' ')[1]}</span>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );

  const renderAnomaly = () => (
    <div className="space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-6 rounded-xl shadow-lg"
      >
        <h3 className="text-xl font-semibold mb-4">Anomaly Detection Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 bg-red-50 rounded-lg">
            <p className="text-2xl font-bold text-red-600">{sampleData.anomalies.filter(a => a.severity === 'high').length}</p>
            <p className="text-sm text-gray-600">High Severity</p>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <p className="text-2xl font-bold text-yellow-600">{sampleData.anomalies.filter(a => a.severity === 'medium').length}</p>
            <p className="text-sm text-gray-600">Medium Severity</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">{sampleData.anomalies.filter(a => a.severity === 'low').length}</p>
            <p className="text-sm text-gray-600">Low Severity</p>
          </div>
        </div>

        <div className="space-y-3">
          {sampleData.anomalies.map((anomaly, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <Brain className="w-5 h-5 text-purple-600" />
                <div>
                  <span className="font-medium">{anomaly.type}</span>
                  <p className="text-sm text-gray-600">{anomaly.description}</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  anomaly.severity === 'high' ? 'bg-red-100 text-red-800' :
                  anomaly.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {anomaly.severity}
                </span>
                <span className="text-sm text-gray-600">{anomaly.count} events</span>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );

  const renderUtilization = () => (
    <div className="space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-6 rounded-xl shadow-lg"
      >
        <h3 className="text-xl font-semibold mb-4">Resource Utilization Trends</h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={sampleData.utilizationData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="dock" stroke="#3b82f6" name="Loading Dock" />
            <Line type="monotone" dataKey="warehouse" stroke="#22c55e" name="Warehouse" />
            <Line type="monotone" dataKey="office" stroke="#f59e0b" name="Office" />
            <Line type="monotone" dataKey="parking" stroke="#8b5cf6" name="Parking" />
          </LineChart>
        </ResponsiveContainer>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white p-6 rounded-xl shadow-lg"
        >
          <h3 className="text-lg font-semibold mb-4">Peak Utilization Times</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Loading Dock</span>
              <span className="text-sm text-gray-600">Peak: 14:00-16:00</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Warehouse</span>
              <span className="text-sm text-gray-600">Peak: 09:00-11:00</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Office</span>
              <span className="text-sm text-gray-600">Peak: 10:00-12:00</span>
            </div>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white p-6 rounded-xl shadow-lg"
        >
          <h3 className="text-lg font-semibold mb-4">Idle Time Analysis</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Loading Dock</span>
              <span className="text-sm text-gray-600">2.5 hours idle</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Warehouse</span>
              <span className="text-sm text-gray-600">1.8 hours idle</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Office</span>
              <span className="text-sm text-gray-600">4.2 hours idle</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );

  const renderViolations = () => {
    const getSeverityColor = (severity) => {
      switch (severity) {
        case 'High': return 'text-red-600 bg-red-50 border-red-200';
        case 'Medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
        case 'Low': return 'text-green-600 bg-green-50 border-green-200';
        default: return 'text-gray-600 bg-gray-50 border-gray-200';
      }
    };

    const getStatusColor = (status) => {
      switch (status) {
        case 'Resolved': return 'text-green-600 bg-green-50 border-green-200';
        case 'Under Investigation': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
        case 'Escalated': return 'text-red-600 bg-red-50 border-red-200';
        default: return 'text-gray-600 bg-gray-50 border-gray-200';
      }
    };

    const filteredViolations = sampleData.violations.filter(violation => {
      if (violationType !== 'all' && violation.type !== violationType) return false;
      return true;
    });

    return (
      <div className="space-y-6">
        {/* Violation Filters */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="verolux-card"
        >
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-gray-500" />
              <select 
                value={violationTimeframe}
                onChange={(e) => setViolationTimeframe(e.target.value)}
                className="verolux-input"
              >
                <option value="1d">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
                <option value="custom">Custom Range</option>
              </select>
            </div>
            
            <div className="flex items-center space-x-2">
              <AlertOctagon className="w-4 h-4 text-gray-500" />
              <select 
                value={violationType}
                onChange={(e) => setViolationType(e.target.value)}
                className="verolux-input"
              >
                <option value="all">All Violations</option>
                <option value="Unauthorized Access">Unauthorized Access</option>
                <option value="PPE Violation">PPE Violation</option>
                <option value="Loitering">Loitering</option>
                <option value="Safety Protocol Breach">Safety Protocol Breach</option>
                <option value="After Hours Access">After Hours Access</option>
                <option value="Vehicle Violation">Vehicle Violation</option>
                <option value="Equipment Misuse">Equipment Misuse</option>
                <option value="Crowd Density">Crowd Density</option>
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <Search className="w-4 h-4 text-gray-500" />
              <input 
                type="text" 
                placeholder="Search violations..." 
                className="verolux-input"
              />
            </div>

            <button className="verolux-btn verolux-btn-primary">
              <Download className="w-4 h-4" />
              Export Report
            </button>
          </div>
        </motion.div>

        {/* Violation Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="verolux-card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="verolux-caption">Total Violations</p>
                <p className="verolux-heading-3">{filteredViolations.length}</p>
              </div>
              <AlertOctagon className="w-8 h-8 text-red-500" />
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="verolux-card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="verolux-caption">High Severity</p>
                <p className="verolux-heading-3">{filteredViolations.filter(v => v.severity === 'High').length}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="verolux-card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="verolux-caption">Resolved</p>
                <p className="verolux-heading-3">{filteredViolations.filter(v => v.status === 'Resolved').length}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="verolux-card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="verolux-caption">Under Investigation</p>
                <p className="verolux-heading-3">{filteredViolations.filter(v => v.status === 'Under Investigation').length}</p>
              </div>
              <Timer className="w-8 h-8 text-yellow-500" />
            </div>
          </motion.div>
        </div>

        {/* Violations Table */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="verolux-card"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="verolux-heading-3">Violation Reports</h3>
            <div className="flex items-center space-x-2">
              <button className="verolux-btn verolux-btn-outline">
                <Settings className="w-4 h-4" />
                Configure
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredViolations.map((violation, index) => (
              <motion.div 
                key={violation.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="verolux-card hover:shadow-lg transition-all duration-300"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center space-x-3">
                    <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">
                      {violation.id}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(violation.severity)}`}>
                      {violation.severity}
                    </span>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(violation.status)}`}>
                    {violation.status}
                  </span>
                </div>

                <div className="space-y-3">
                  <div>
                    <h4 className="verolux-heading-4 mb-1">{violation.type}</h4>
                    <p className="verolux-body-secondary">{violation.description}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="verolux-caption text-gray-500">Location</p>
                      <p className="verolux-body">{violation.location}</p>
                    </div>
                    <div>
                      <p className="verolux-caption text-gray-500">Camera</p>
                      <p className="verolux-body font-mono">{violation.camera}</p>
                    </div>
                  </div>

                  <div>
                    <p className="verolux-caption text-gray-500">Timestamp</p>
                    <div className="flex items-center space-x-2">
                      <Clock className="w-4 h-4 text-gray-400" />
                      <div>
                        <p className="verolux-body">{violation.timestamp.split(' ')[0]}</p>
                        <p className="verolux-caption">{violation.timestamp.split(' ')[1]}</p>
                      </div>
                    </div>
                  </div>

                  {violation.resolvedBy && (
                    <div>
                      <p className="verolux-caption text-gray-500">Resolved By</p>
                      <p className="verolux-body">{violation.resolvedBy}</p>
                      {violation.resolvedAt && (
                        <p className="verolux-caption">at {violation.resolvedAt}</p>
                      )}
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                    <button className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-gray-200 transition-colors">
                      <Eye className="w-4 h-4 text-gray-600" />
                    </button>
                    
                    <div className="flex items-center space-x-2">
                      <button className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="View Details">
                        <FileText className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors" title="Resolve">
                        <CheckCircle className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="Escalate">
                        <XCircle className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {filteredViolations.length === 0 && (
            <div className="text-center py-12">
              <AlertOctagon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="verolux-heading-4 text-gray-500 mb-2">No Violations Found</h3>
              <p className="verolux-body-secondary">No violations match your current filters.</p>
            </div>
          )}
        </motion.div>
      </div>
    );
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'objects': return renderObjectCounts();
      case 'zones': return renderZoneAnalytics();
      case 'compliance': return renderCompliance();
      case 'violations': return renderViolations();
      case 'alerts': return renderAlerts();
      case 'traffic': return renderTrafficPatterns();
      case 'linecrossing': return renderLineCrossing();
      case 'loitering': return renderLoitering();
      case 'intrusion': return renderIntrusion();
      case 'hazards': return renderHazards();
      case 'anomaly': return renderAnomaly();
      case 'utilization': return renderUtilization();
      case 'export': return renderExport();
      default: return renderOverview();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="p-6">
        {/* Enhanced Header with Advanced Actions */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Analytics & Reports</h1>
              <p className="text-gray-600 text-lg">Comprehensive insights and analytics for your surveillance system</p>
            </div>
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 px-4 py-2 bg-white rounded-lg shadow-sm border">
                <Clock className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-600">Last updated: {new Date().toLocaleTimeString()}</span>
              </div>
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
                <span className="text-sm font-medium">Export Report</span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                <Share2 className="w-4 h-4" />
                <span className="text-sm font-medium">Share</span>
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
                onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <span className="text-gray-500">to</span>
              <input 
                type="date" 
                value={dateRange.end}
                onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
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
                <option value="cam5">Camera 5</option>
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

            <div className="flex items-center space-x-2">
              <Search className="w-4 h-4 text-gray-500" />
              <input 
                type="text" 
                placeholder="Search reports..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-48"
              />
            </div>

            <div className="flex items-center space-x-2">
              <button 
                onClick={() => generateReport(activeTab)}
                disabled={loading}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span className="text-sm font-medium">
                  {loading ? 'Generating...' : 'Refresh Data'}
                </span>
              </button>
            </div>
          </div>
        </motion.div>

        {/* Enhanced Tabs with Categories */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl shadow-lg mb-6"
        >
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Report Categories</h2>
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
                <button 
                  onClick={() => setViewMode('table')}
                  className={`p-2 rounded-lg ${viewMode === 'table' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:bg-gray-100'}`}
                >
                  <Table className="w-4 h-4" />
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

        {/* Enhanced Content with Loading State and Progress */}
        <motion.div 
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="flex items-center space-x-3 mb-4">
                <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
                <span className="text-lg font-medium text-gray-600">Generating report...</span>
              </div>
              <div className="w-64 bg-gray-200 rounded-full h-2">
                <motion.div 
                  className="bg-blue-600 h-2 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: "100%" }}
                  transition={{ duration: 2, ease: "easeInOut" }}
                />
              </div>
              <p className="text-sm text-gray-500 mt-2">Processing data and generating visualizations...</p>
            </div>
          ) : (
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                {/* Report Header with Quick Actions */}
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 capitalize">{activeTab.replace(/([A-Z])/g, ' $1').trim()}</h2>
                      <p className="text-gray-600 mt-1">Detailed analytics and insights for {activeTab} reporting</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button className="flex items-center space-x-2 px-3 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                        <Eye className="w-4 h-4" />
                        <span className="text-sm">Preview</span>
                      </button>
                      <button className="flex items-center space-x-2 px-3 py-2 text-blue-600 bg-blue-100 rounded-lg hover:bg-blue-200 transition-colors">
                        <Download className="w-4 h-4" />
                        <span className="text-sm">Export</span>
                      </button>
                      <button className="flex items-center space-x-2 px-3 py-2 text-purple-600 bg-purple-100 rounded-lg hover:bg-purple-200 transition-colors">
                        <Share2 className="w-4 h-4" />
                        <span className="text-sm">Share</span>
                      </button>
                    </div>
                  </div>
                </div>
                
                {renderContent()}
              </motion.div>
            </AnimatePresence>
          )}
        </motion.div>

        {/* Floating Action Button */}
        <motion.div
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5 }}
          className="fixed bottom-6 right-6 z-50"
        >
          <div className="flex flex-col items-end space-y-3">
            {/* Quick Actions Menu */}
            <AnimatePresence>
              {expandedCards.quickActions && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  className="bg-white rounded-xl shadow-lg p-4 mb-3"
                >
                  <div className="space-y-2">
                    <button className="flex items-center space-x-2 w-full px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
                      <Download className="w-4 h-4" />
                      <span className="text-sm">Export All</span>
                    </button>
                    <button className="flex items-center space-x-2 w-full px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
                      <Share2 className="w-4 h-4" />
                      <span className="text-sm">Share Report</span>
                    </button>
                    <button className="flex items-center space-x-2 w-full px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
                      <Settings className="w-4 h-4" />
                      <span className="text-sm">Settings</span>
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Main FAB */}
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setExpandedCards(prev => ({ ...prev, quickActions: !prev.quickActions }))}
              className="w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center"
            >
              <motion.div
                animate={{ rotate: expandedCards.quickActions ? 45 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <Plus className="w-6 h-6" />
              </motion.div>
            </motion.button>
          </div>
        </motion.div>

        {/* Report Summary Footer */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-8 bg-white rounded-xl shadow-lg p-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-600">Report generated at {new Date().toLocaleTimeString()}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Database className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-600">Data source: Live surveillance feeds</span>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Report ID: RPT-{Date.now().toString().slice(-6)}</span>
              <button className="p-1 hover:bg-gray-100 rounded">
                <Copy className="w-4 h-4 text-gray-500" />
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Reports;