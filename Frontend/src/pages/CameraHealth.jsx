import React, { useEffect, useState } from 'react'

export default function CameraHealth(){
  const [health, setHealth] = useState({ status:'unknown' })
  const [cams, setCams] = useState([
    { id:'cam-01', name:'Loading Dock', status:'online' },
    { id:'cam-02', name:'Warehouse A', status:'online' },
    { id:'cam-03', name:'Office Entrance', status:'offline' },
    { id:'cam-04', name:'Parking Lot', status:'online' }
  ])

  useEffect(()=>{
    let stop=false
    const tick = async ()=>{
      try{
        const r = await fetch('http://127.0.0.1:8002/health')
        const j = await r.json()
        setHealth(j)
      }catch{}
      if(!stop) setTimeout(tick, 3000)
    }
    tick()
    return ()=>{ stop=true }
  },[])

  return (
    <div className="min-h-screen verolux-pattern p-6">
      <div className="max-w-5xl mx-auto">
        <h1 className="verolux-heading-3 mb-4">Camera & System Health</h1>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="verolux-card">
            <h2 className="verolux-heading-4 mb-2">Backend Health</h2>
            <div className="verolux-body">Status: <span className="verolux-badge verolux-badge-primary">{health.status}</span></div>
            <div className="verolux-caption">Timestamp: {health.timestamp? new Date(health.timestamp*1000).toLocaleTimeString(): '-'}</div>
          </div>
          <div className="verolux-card">
            <h2 className="verolux-heading-4 mb-2">Cameras</h2>
            <div className="space-y-2">
              {cams.map(c=> (
                <div key={c.id} className="flex items-center justify-between bg-black/30 rounded p-2">
                  <div className="verolux-body">{c.name}</div>
                  <span className={`text-xs px-2 py-0.5 rounded border ${c.status==='online'?'text-emerald-400 border-emerald-600':'text-red-400 border-red-600'}`}>{c.status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}



