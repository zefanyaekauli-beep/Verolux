import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Settings as SettingsIcon, User, Bell, Shield, Monitor, 
  Globe, Database, Camera, Wifi, Lock, Key, Trash2,
  Save, RotateCcw, Download, Upload, Eye, EyeOff,
  CheckCircle, AlertTriangle, Info, ChevronRight, 
  ChevronDown, Sun, Moon, Palette, Volume2, VolumeX,
  Wifi as WifiIcon, WifiOff, Battery, BatteryLow,
  Clock, MapPin, Zap, Activity, BarChart3, FileText,
  Users, Shield as ShieldIcon, AlertCircle, CheckCircle2,
  X, Plus, Edit, Trash2 as TrashIcon, Copy, Share2
} from 'lucide-react'
import useLang from '../stores/lang'
import useTheme from '../stores/theme'
export default function Settings(){
  const lang = useLang(s=>s.lang), setLang = useLang(s=>s.setLang)
  const theme = useTheme(s=>s.theme), setTheme = useTheme(s=>s.setTheme)
  return <div className='card'>
    <h3>Settings</h3>
    <div className='flex'>
      <div><label>Language </label>
        <select value={lang} onChange={e=>setLang(e.target.value)}><option value='en'>English</option><option value='id'>Bahasa Indonesia</option></select>
      </div>
      <div><label>Theme </label>
        <select value={theme} onChange={e=>setTheme(e.target.value)}><option value='dark'>Dark</option><option value='light'>Light</option></select>
      </div>
    </div>
  </div>
}
