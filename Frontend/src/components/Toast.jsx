import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const Toast = ({ message, type = 'success', duration = 3000, onClose }) => {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false)
        setTimeout(() => onClose?.(), 300) // Wait for animation
      }, duration)

      return () => clearTimeout(timer)
    }
  }, [duration, onClose])

  const styles = {
    success: {
      bg: 'bg-green-600',
      border: 'border-green-400',
      text: 'text-white',
      icon: '✅'
    },
    error: {
      bg: 'bg-red-600',
      border: 'border-red-400',
      text: 'text-white',
      icon: '❌'
    },
    info: {
      bg: 'bg-blue-600',
      border: 'border-blue-400',
      text: 'text-white',
      icon: 'ℹ️'
    }
  }

  const style = styles[type] || styles.success

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8, x: 100 }}
          animate={{ opacity: 1, scale: 1, x: 0 }}
          exit={{ opacity: 0, scale: 0.8, x: 100 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className="fixed bottom-4 right-4 z-50 min-w-[300px]"
        >
          <div className={`${style.bg} ${style.text} p-4 rounded-xl shadow-2xl border-2 ${style.border} relative overflow-hidden`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{style.icon}</span>
                <p className="font-semibold">{message}</p>
              </div>
              <button
                onClick={() => {
                  setIsVisible(false)
                  setTimeout(() => onClose?.(), 300)
                }}
                className={`${style.text} hover:opacity-70 transition-opacity ml-4`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export default Toast

