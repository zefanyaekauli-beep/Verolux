import React, { useState } from 'react'
import { motion } from 'framer-motion'
import SearchTimeline from './SearchTimeline'
import SemanticSearch from './SemanticSearch'

export default function Search(){
  const [tab, setTab] = useState('timeline') // 'timeline' | 'semantic'
  return (
    <div className="min-h-screen verolux-pattern p-6">
      <div className="max-w-7xl mx-auto">
        <div className="verolux-card mb-4 flex items-center justify-between">
          <div>
            <h1 className="verolux-heading-3">Search</h1>
            <p className="verolux-caption">Investigations with timeline filters or natural-language semantic search</p>
          </div>
          <div className="flex gap-2">
            <button onClick={()=>setTab('timeline')} className={`verolux-btn ${tab==='timeline'?'verolux-btn-primary':'verolux-btn-outline'}`}>Timeline</button>
            <button onClick={()=>setTab('semantic')} className={`verolux-btn ${tab==='semantic'?'verolux-btn-primary':'verolux-btn-outline'}`}>Semantic</button>
          </div>
        </div>
        <motion.div initial={{opacity:0,y:10}} animate={{opacity:1,y:0}}>
          {tab==='timeline' ? <SearchTimeline/> : <SemanticSearch/>}
        </motion.div>
      </div>
    </div>
  )
}


import { motion } from 'framer-motion'
import SearchTimeline from './SearchTimeline'
import SemanticSearch from './SemanticSearch'

export default function Search(){
  const [tab, setTab] = useState('timeline') // 'timeline' | 'semantic'
  return (
    <div className="min-h-screen verolux-pattern p-6">
      <div className="max-w-7xl mx-auto">
        <div className="verolux-card mb-4 flex items-center justify-between">
          <div>
            <h1 className="verolux-heading-3">Search</h1>
            <p className="verolux-caption">Investigations with timeline filters or natural-language semantic search</p>
          </div>
          <div className="flex gap-2">
            <button onClick={()=>setTab('timeline')} className={`verolux-btn ${tab==='timeline'?'verolux-btn-primary':'verolux-btn-outline'}`}>Timeline</button>
            <button onClick={()=>setTab('semantic')} className={`verolux-btn ${tab==='semantic'?'verolux-btn-primary':'verolux-btn-outline'}`}>Semantic</button>
          </div>
        </div>
        <motion.div initial={{opacity:0,y:10}} animate={{opacity:1,y:0}}>
          {tab==='timeline' ? <SearchTimeline/> : <SemanticSearch/>}
        </motion.div>
      </div>
    </div>
  )
}








