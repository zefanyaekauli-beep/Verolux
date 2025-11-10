import React, { useState } from 'react'
import { motion } from 'framer-motion'
import SimpleInference from './SimpleInference'
import AdvancedBodyChecking from './AdvancedBodyChecking'

export default function Inference(){
  const [mode, setMode] = useState('simple') // 'simple' | 'advanced'

  return (
    <div className="min-h-screen">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-white">Unified Inference</h1>
            <p className="text-gray-300">Live video inference with optional advanced body checking</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={()=>setMode('simple')}
              className={`px-3 py-2 rounded-lg text-sm font-medium ${mode==='simple'?'bg-green-500/20 text-green-400':'bg-gray-500/20 text-gray-300'}`}
            >
              Simple
            </button>
            <button
              onClick={()=>setMode('advanced')}
              className={`px-3 py-2 rounded-lg text-sm font-medium ${mode==='advanced'?'bg-blue-500/20 text-blue-400':'bg-gray-500/20 text-gray-300'}`}
            >
              Advanced
            </button>
          </div>
        </div>
      </div>
      <motion.div initial={{opacity:0}} animate={{opacity:1}}>
        {mode==='simple' ? <SimpleInference/> : <AdvancedBodyChecking/>}
      </motion.div>
    </div>
  )
}


import { motion } from 'framer-motion'
import SimpleInference from './SimpleInference'
import AdvancedBodyChecking from './AdvancedBodyChecking'

export default function Inference(){
  const [mode, setMode] = useState('simple') // 'simple' | 'advanced'

  return (
    <div className="min-h-screen">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-white">Unified Inference</h1>
            <p className="text-gray-300">Live video inference with optional advanced body checking</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={()=>setMode('simple')}
              className={`px-3 py-2 rounded-lg text-sm font-medium ${mode==='simple'?'bg-green-500/20 text-green-400':'bg-gray-500/20 text-gray-300'}`}
            >
              Simple
            </button>
            <button
              onClick={()=>setMode('advanced')}
              className={`px-3 py-2 rounded-lg text-sm font-medium ${mode==='advanced'?'bg-blue-500/20 text-blue-400':'bg-gray-500/20 text-gray-300'}`}
            >
              Advanced
            </button>
          </div>
        </div>
      </div>
      <motion.div initial={{opacity:0}} animate={{opacity:1}}>
        {mode==='simple' ? <SimpleInference/> : <AdvancedBodyChecking/>}
      </motion.div>
    </div>
  )
}






