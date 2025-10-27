import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const BodyCheckingAlert = ({ alert, onClose }) => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    console.log('BodyCheckingAlert useEffect triggered:', alert)
    if (alert && alert.active) {
      console.log('Showing alert:', alert.message)
      setIsVisible(true)
      
      // Auto-hide after 5 seconds
      const timer = setTimeout(() => {
        console.log('Auto-hiding alert')
        setIsVisible(false)
        setTimeout(() => onClose(), 500) // Wait for animation to complete
      }, 5000)
      
      return () => clearTimeout(timer)
    } else {
      console.log('Hiding alert')
      setIsVisible(false)
    }
  }, [alert, onClose])

  if (!alert || !alert.active) return null

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: -50 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: -50 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className="fixed top-4 right-4 z-50 max-w-md"
        >
          <div className="bg-red-600 text-white p-6 rounded-xl shadow-2xl border-2 border-red-400 relative overflow-hidden">
            {/* Animated background */}
            <div className="absolute inset-0 bg-gradient-to-r from-red-600 to-red-700 opacity-90"></div>
            <div className="absolute inset-0 bg-red-500 opacity-20 animate-pulse"></div>
            
            {/* Content */}
            <div className="relative z-10">
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                    <span className="text-red-600 text-xl">🚨</span>
                  </div>
                  <h3 className="text-xl font-bold">SECURITY ALERT</h3>
                </div>
                <button
                  onClick={() => setIsVisible(false)}
                  className="text-white hover:text-red-200 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              {/* Alert Message */}
              <div className="mb-4">
                <p className="text-lg font-semibold mb-2">{alert.message}</p>
                <p className="text-sm opacity-90">
                  Person detected in gate area - Body checking procedure initiated
                </p>
              </div>
              
              {/* Status Indicators */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${alert.person_in_gate ? 'bg-green-400' : 'bg-gray-400'}`}></div>
                  <span className="text-sm">
                    {alert.person_in_gate ? 'Person in Gate Area' : 'No Person Detected'}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${alert.guard_present ? 'bg-green-400' : 'bg-yellow-400'}`}></div>
                  <span className="text-sm">
                    {alert.guard_present ? 'Guard Present' : 'Guard Not Detected'}
                  </span>
                </div>
              </div>
              
              {/* Timestamp */}
              <div className="mt-4 pt-3 border-t border-red-400">
                <p className="text-xs opacity-75">
                  Alert Time: {new Date(alert.timestamp * 1000).toLocaleTimeString()}
                </p>
              </div>
            </div>
            
            {/* Animated border */}
            <div className="absolute inset-0 border-2 border-red-300 rounded-xl animate-ping opacity-20"></div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export default BodyCheckingAlert
