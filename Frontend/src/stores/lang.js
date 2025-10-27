import { create } from 'zustand'

const languages = {
  en: { name: 'English', flag: '🇺🇸', code: 'en' },
  id: { name: 'Bahasa Indonesia', flag: '🇮🇩', code: 'id' },
  zh: { name: '中文 (Mandarin)', flag: '🇨🇳', code: 'zh' }
}

const translations = {
  en: {
    dashboard: 'Dashboard',
    cameras: 'Cameras',
    semanticSearch: 'Semantic Search',
    analytics: 'Analytics',
    reports: 'Reports',
    overview: 'Overview',
    objectCounts: 'Object Counts',
    zoneAnalytics: 'Zone Analytics',
    compliance: 'Compliance',
    violations: 'Violations',
    alertsEvents: 'Alerts & Events',
    trafficPatterns: 'Traffic Patterns',
    lineCrossing: 'Line Crossing',
    loitering: 'Loitering',
    intrusion: 'Intrusion',
    hazards: 'Hazards',
    anomalyDetection: 'Anomaly Detection',
    heatmap: 'Heatmap',
    gateConfig: 'Gate Configuration',
    videoplaybackDemo: 'Video Demo',
    settings: 'Settings',
    language: 'Language',
    selectLanguage: 'Select Language'
  },
  id: {
    dashboard: 'Dasbor',
    cameras: 'Kamera',
    semanticSearch: 'Pencarian Semantik',
    analytics: 'Analitik',
    reports: 'Laporan',
    overview: 'Ringkasan',
    objectCounts: 'Jumlah Objek',
    zoneAnalytics: 'Analitik Zona',
    compliance: 'Kepatuhan',
    violations: 'Pelanggaran',
    alertsEvents: 'Peringatan & Acara',
    trafficPatterns: 'Pola Lalu Lintas',
    lineCrossing: 'Penyeberangan Garis',
    loitering: 'Menggantung',
    intrusion: 'Intrusi',
    hazards: 'Bahaya',
    anomalyDetection: 'Deteksi Anomali',
    heatmap: 'Peta Panas',
    gateConfig: 'Konfigurasi Gerbang',
    videoplaybackDemo: 'Demo Video',
    settings: 'Pengaturan',
    language: 'Bahasa',
    selectLanguage: 'Pilih Bahasa'
  },
  zh: {
    dashboard: '仪表板',
    cameras: '摄像头',
    semanticSearch: '语义搜索',
    analytics: '分析',
    reports: '报告',
    overview: '概览',
    objectCounts: '对象计数',
    zoneAnalytics: '区域分析',
    compliance: '合规性',
    violations: '违规行为',
    alertsEvents: '警报和事件',
    trafficPatterns: '交通模式',
    lineCrossing: '越线检测',
    loitering: '徘徊检测',
    intrusion: '入侵检测',
    hazards: '危险事件',
    anomalyDetection: '异常检测',
    heatmap: '热力图',
    gateConfig: '闸机配置',
    videoplaybackDemo: '视频演示',
    settings: '设置',
    language: '语言',
    selectLanguage: '选择语言'
  }
}

export default create((set, get) => ({
  lang: 'en',
  languages,
  translations,
  setLang: (l) => set({ lang: l }),
  t: (key) => {
    const state = get()
    return state.translations[state.lang]?.[key] || key
  }
}))
