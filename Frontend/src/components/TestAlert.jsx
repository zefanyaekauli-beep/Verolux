import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const TestAlert = () => {
  const [showAlert, setShowAlert] = useState(false)

  useEffect(() => {
    // Show alert after 3 seconds for testing
    const timer = setTimeout(() => {
      setShowAlert(true)
    }, 3000)

    return () => clearTimeout(timer)
  }, [])

  const testAlert = {
    active: showAlert,
    message: "🚨 BODY CHECKING IN PROGRESS",
    person_in_gate: true,
    guard_present: true,
    timestamp: Date.now() / 1000
  }

  return (
    <div className="fixed top-4 right-4 z-50">
      <button
        onClick={() => setShowAlert(!showAlert)}
        className="bg-blue-600 text-white px-4 py-2 rounded mb-4"
      >
        {showAlert ? 'Hide Test Alert' : 'Show Test Alert'}
      </button>
      
      <AnimatePresence>
        {showAlert && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: -50 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: -50 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="bg-red-600 text-white p-6 rounded-xl shadow-2xl border-2 border-red-400 relative overflow-hidden max-w-md"
          >
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
                  onClick={() => setShowAlert(false)}
                  className="text-white hover:text-red-200 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              {/* Alert Message */}
              <div className="mb-4">
                <p className="text-lg font-semibold mb-2">{testAlert.message}</p>
                <p className="text-sm opacity-90">
                  Person detected in gate area - Body checking procedure initiated
                </p>
              </div>
              
              {/* Status Indicators */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-green-400"></div>
                  <span className="text-sm">Person in Gate Area</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-green-400"></div>
                  <span className="text-sm">Guard Present</span>
                </div>
              </div>
              
              {/* Timestamp */}
              <div className="mt-4 pt-3 border-t border-red-400">
                <p className="text-xs opacity-75">
                  Alert Time: {new Date(testAlert.timestamp * 1000).toLocaleTimeString()}
                </p>
              </div>
            </div>
            
            {/* Animated border */}
            <div className="absolute inset-0 border-2 border-red-300 rounded-xl animate-ping opacity-20"></div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default TestAlert

